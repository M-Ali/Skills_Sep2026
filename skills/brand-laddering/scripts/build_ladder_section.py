"""Build the five-slide Brand Meaning Ladder section from a JSON spec.

    uv run --with python-pptx --with pandas python build_ladder_section.py spec.json \
        --levels ladder_levels.csv [--base deck.pptx --insert-at N]

- Without --base: writes a new 16:9 deck holding only the section.
- With --base: copies the deck and inserts the section before slide N+1 (0-based index N).
- Never overwrites: writes the first free name among out.pptx, out-v2.pptx, out-v3.pptx ...

The numbers are not typed into the spec. Slide 2 prints each brand's mean from --levels, and
slide 5's "Says" counts come from the client's row in --levels. The build refuses to run if a
brand in the table is missing from slide 2 (and not listed in `omitted`), or sits on a rung
other than its modal level. Spec shape: ../assets/example_spec.json. Layout:
../references/slide-specs.md.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

NAVY = RGBColor(0x10, 0x2A, 0x43)
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x6B, 0x74, 0x80)
ACCENT = RGBColor(0xC8, 0x10, 0x2E)
PALE = RGBColor(0xF2, 0xF5, 0xF8)
FAINT = RGBColor(0xFA, 0xFB, 0xFC)
SKY = RGBColor(0x9F, 0xB4, 0xC7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Segoe UI"

VOICE = {1: '"I am here"', 2: '"Reason to buy me"', 3: '"Here is what I can do for you"',
         4: '"I am like you; you are like me"', 5: '"I think like you do"',
         6: '"I change things you would like to"'}
QUESTION = {1: '"Who are you?"', 2: '"What do you have?"', 3: '"What does it do for me?"',
            4: '"What does choosing you say about me?"', 5: '"What do you believe?"',
            6: '"What change do you want to create?"'}
NAME = {1: "Product identification", 2: "Product attributes", 3: "Product benefits",
        4: "Psychological associations", 5: "Human values / way of life", 6: "Purpose / philosophy"}

ROW_TOP, ROW_H, ROW_GAP = 1.82, 0.74, 0.04  # six rows end at 6.50, above the band at 6.55


# ---------- primitives ----------

def rect(slide, x, y, w, h, fill):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def text(slide, x, y, w, h, paras, size=9, bold=False, color=INK, space=2):
    """paras: str, or list of str / (label, body) tuples. A label renders as a bold run-in."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, para in enumerate(paras if isinstance(paras, list) else [paras]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space)
        p.alignment = PP_ALIGN.LEFT
        label, body = para if isinstance(para, tuple) else (None, para)
        if label:
            r = p.add_run()
            r.text = label + "  "
            _font(r, size, True, color)
        r = p.add_run()
        r.text = body
        _font(r, size, bold, color)
    return tb


def _font(run, size, bold, color):
    run.font.name, run.font.size, run.font.bold = FONT, Pt(size), bold
    run.font.color.rgb = color


def level_cell(slide, x, y, w, level, label, sub):
    tb = text(slide, x, y + 0.07, w, ROW_H, [label, sub], 10, True, NAVY)
    f = tb.text_frame.paragraphs[1].runs[0].font
    f.bold, f.size, f.color.rgb = False, Pt(8.5), MUTED


def frame(prs, headline, standfirst, heads, conclusion, footnote):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, prs.slide_width / 914400, 1.0, NAVY)
    text(s, 0.6, 0.3, 12.1, 0.5, headline, 20 if len(headline) > 60 else 24, True, WHITE)
    text(s, 0.6, 1.1, 12.1, 0.35, standfirst, 10.5, True, NAVY)
    for x, w, h in heads:
        text(s, x, 1.55, w, 0.25, h.upper(), 9, True, MUTED)
    rect(s, 0.6, 6.55, 12.1, 0.62, NAVY)
    text(s, 0.85, 6.64, 11.6, 0.5, conclusion, 11, True, WHITE)
    if footnote:
        text(s, 0.6, 7.2, 12.1, 0.28, footnote, 8, False, MUTED)
    return s


def rows_top_down(rows):
    by_level = {r["level"]: r for r in rows}
    if sorted(by_level) != [1, 2, 3, 4, 5, 6]:
        raise SystemExit(f"each slide needs exactly levels 1-6, got {sorted(by_level)}")
    for i, lv in enumerate([6, 5, 4, 3, 2, 1]):
        yield ROW_TOP + i * (ROW_H + ROW_GAP), by_level[lv]


# ---------- validation ----------

def validate(spec, table):
    errors = []
    placed = {}
    for r in spec["placement"]["rows"]:
        for b in r.get("brands", []):
            placed[b] = r["level"]
    omitted = spec["placement"].get("omitted", {})
    for _, t in table.iterrows():
        if t.brand in omitted:
            continue
        if t.brand not in placed:
            errors.append(f"{t.brand} is in the levels table but not on slide 2 (add it, or list it in "
                          f"placement.omitted with a reason)")
        elif placed[t.brand] != t["mode"]:
            errors.append(f"{t.brand} is placed on L{placed[t.brand]} but its modal level is L{t['mode']} "
                          f"(mean {t['mean']})")
    for b in placed:
        if b not in set(table.brand):
            errors.append(f"{b} is on slide 2 but has no computed levels")
    client = spec["client"]
    if client not in set(table.brand):
        errors.append(f"client {client} has no computed levels")
    targets = [r for r in spec["client_ladder"]["rows"] if r.get("target")]
    if len(targets) != 1:
        errors.append(f"slide 5 needs exactly one target row, found {len(targets)}")
    if errors:
        raise SystemExit("Refusing to build:\n  - " + "\n  - ".join(errors))


# ---------- slides ----------

def divider(prs, d):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, prs.slide_width / 914400, prs.slide_height / 914400, NAVY)
    rect(s, 0.9, 2.3, 1.6, 0.06, ACCENT)
    text(s, 0.9, 2.6, 11.4, 0.7, d.get("title", "The Brand Meaning Ladder"), 40, True, WHITE)
    text(s, 0.9, 3.55, 11.4, 1.4, [d["subtitle"], "", d["direction"]], 18, False, SKY, space=0)


def placement(prs, p, table):
    means = dict(zip(table.brand, table["mean"]))
    splits = set(table.brand[table.split])
    s = frame(prs, p["headline"], p["standfirst"],
              [(0.72, 2.9, "Level"), (3.9, 5.2, "Brands at this level (mean level)"), (9.3, 3.3, "")],
              p["conclusion"], p.get("footnote"))
    for y, r in rows_top_down(p["rows"]):
        marked = bool(r.get("marker"))
        rect(s, 0.6, y, 12.1, ROW_H, PALE if marked else FAINT)
        if marked:
            rect(s, 0.6, y, 0.06, ROW_H, ACCENT)
        level_cell(s, 0.72, y, 2.9, r["level"], f'{r["level"]}. {r.get("name", NAME[r["level"]])}',
                   VOICE[r["level"]])
        names = ", ".join(f"{b} ({means[b]:.1f}{', split' if b in splits else ''})" for b in r.get("brands", []))
        body = f"{names} - {r['note']}" if names else r["note"]
        text(s, 3.9, y + 0.1, 5.2, ROW_H, body, 10, False, INK)
        if marked:
            text(s, 9.3, y + 0.1, 3.3, ROW_H, r["marker"].upper(), 10, True, ACCENT)


def factor_list(prs, f):
    s = frame(prs, f["headline"], f["standfirst"],
              [(0.72, 1.9, "Level"), (2.6, 3.45, "Current"), (6.2, 4.6, "Potential"), (10.95, 1.65, "Unsupported")],
              f["conclusion"], f.get("footnote"))
    for y, r in rows_top_down(f["rows"]):
        rect(s, 0.6, y, 12.1, ROW_H, FAINT)
        rect(s, 2.5, y, 3.55, ROW_H, PALE)
        level_cell(s, 0.72, y, 1.8, r["level"], f'{r["level"]}. {r.get("name", NAME[r["level"]])}',
                   QUESTION[r["level"]])
        text(s, 2.6, y + 0.07, 3.35, ROW_H, "  ·  ".join(r["current"]), 9, True, NAVY)
        text(s, 6.2, y + 0.07, 4.6, ROW_H, "  ·  ".join(r["potential"]), 8.5, False, INK)
        text(s, 10.95, y + 0.07, 1.65, ROW_H, "  ·  ".join(r["unsupported"]) or "-", 8.5, False, MUTED)


def category_evidence(prs, c):
    s = frame(prs, c["headline"], c["standfirst"],
              [(0.72, 1.6, "Level"), (2.4, 4.5, "What brands claim"), (7.0, 2.75, "What customers judge on"),
               (9.95, 2.6, "Open - nobody claims")],
              c["conclusion"], c.get("footnote"))
    for y, r in rows_top_down(c["rows"]):
        rect(s, 0.6, y, 12.1, ROW_H, FAINT)
        rect(s, 9.85, y, 2.85, ROW_H, PALE)
        level_cell(s, 0.72, y, 1.6, r["level"], f'{r["level"]}. {r.get("name", NAME[r["level"]])}',
                   QUESTION[r["level"]])
        text(s, 2.4, y + 0.07, 4.5, ROW_H, r["brands_claim"], 8.5, False, INK)
        text(s, 7.0, y + 0.07, 2.75, ROW_H, r["customers_judge"], 8.5, False, INK)
        text(s, 9.95, y + 0.07, 2.65, ROW_H, r["open"], 8.5, True, NAVY)


def client_ladder(prs, c, client, crow):
    standfirst = c["standfirst"].format(client=client, n=int(crow.n), mode=int(crow["mode"]),
                                        mean=float(crow["mean"]))
    s = frame(prs, c["headline"].format(client=client), standfirst,
              [(0.72, 1.85, "Level"), (2.55, 5.05, "Factors in the category"),
               (7.75, 3.05, f"{client} today"), (10.95, 1.75, "Placement")],
              c["conclusion"], c.get("footnote"))
    for y, r in rows_top_down(c["rows"]):
        tgt = bool(r.get("target"))
        rect(s, 0.6, y, 12.1, ROW_H, PALE if tgt else FAINT)
        if tgt:
            rect(s, 0.6, y, 0.06, ROW_H, ACCENT)
        level_cell(s, 0.72, y, 1.73, r["level"], f'{r["level"]}. {r.get("name", NAME[r["level"]])}',
                   QUESTION[r["level"]])
        text(s, 2.55, y + 0.07, 5.05, ROW_H, [("In use:", r["in_use"]), ("Open:", r["open"])], 8.5)
        count = int(crow[f"L{r['level']}"])
        says = f"{count} post{'s' if count != 1 else ''}" + (f" - {r['says']}" if r.get("says") else ".")
        text(s, 7.75, y + 0.07, 3.05, ROW_H, [("Says:", says), ("Heard:", r["heard"])], 8.5)
        verb = f"PLACE {client.upper()} HERE" if tgt else r["placement"].upper()
        tb = text(s, 10.95, y + 0.1, 1.65, ROW_H, [verb, r["placement_sub"]], 10 if tgt else 9.5, True,
                  ACCENT if tgt else NAVY)
        f = tb.text_frame.paragraphs[1].runs[0].font
        f.bold, f.size, f.color.rgb = False, Pt(8.5), INK


# ---------- deck handling ----------

def free_path(out: Path) -> Path:
    if not out.exists():
        return out
    n = 2
    while (p := out.with_name(f"{out.stem}-v{n}{out.suffix}")).exists():
        n += 1
    return p


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path)
    ap.add_argument("--levels", type=Path, required=True, help="output of compute_levels.py")
    ap.add_argument("--base", type=Path, help="existing deck to insert the section into (copied, never edited)")
    ap.add_argument("--insert-at", type=int, help="0-based slide index for the divider (default: end)")
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    table = pd.read_csv(args.levels)
    validate(spec, table)
    crow = table[table.brand == spec["client"]].iloc[0]

    if args.base:
        prs = Presentation(str(args.base))
    else:
        prs = Presentation()
        prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
    before = len(prs.slides)

    divider(prs, spec["divider"])
    placement(prs, spec["placement"], table)
    factor_list(prs, spec["factor_list"])
    category_evidence(prs, spec["category_evidence"])
    client_ladder(prs, spec["client_ladder"], spec["client"], crow)

    if args.insert_at is not None:
        ids = prs.slides._sldIdLst
        new = list(ids)[before:]
        for el in new:
            ids.remove(el)
        for i, el in enumerate(new):
            ids.insert(args.insert_at + i, el)

    out = free_path(Path(spec["out"]) if Path(spec["out"]).is_absolute() else args.spec.parent / spec["out"])
    prs.save(out)
    print(f"{out}  ({len(prs.slides)} slides; section = 5 slides; client {spec['client']} "
          f"mode L{int(crow['mode'])}, mean {float(crow['mean']):.2f})")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
