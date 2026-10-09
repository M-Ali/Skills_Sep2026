"""Preview the effect of the current rule files on everything in the raw store.

Usage:
    uv run python .claude/skills/tune-rules/scripts/rules_diff.py [--source ppra] [--show 15] [--json]

Builds leads from every stored raw item using the rules as they are *now* on disk
(rules.toml, sources.toml), compares them with the leads currently in the database,
and reports:
  NEW      items that would become leads but aren't leads now
  DROPPED  current leads whose raw item would no longer produce a lead
  CHANGED  leads whose agencies / sectors / signals / score would change
  SCREENED news/alert leads the rules make but rules.toml [screen] holds back (with
           the reason). Same-story merges are not simulated; reclassify does them.
Read-only: nothing is written. Apply with `uv run bdleads reclassify`.

Typical use: run `uv run bdleads reclassify` first (so the database reflects the old
rules), edit the rules, then run this script to see the difference before applying it.
"""

from __future__ import annotations

import argparse
import json
import sys

from bdleads import pipeline
from bdleads import screen as screening
from bdleads.store import Store


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="only this collector (ppra, worldbank, psx, rss, email)")
    ap.add_argument("--show", type=int, default=15, help="examples to print per section")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    store = Store()
    items = store.raw_items(args.source)
    proposed: dict[tuple[str, str], dict] = {}
    screened: list[dict] = []
    for it in items:
        for lead in pipeline.item_to_leads(it):
            if hit := screening.screen(lead, it.data):
                screened.append({"title": lead.title, "rule": hit[0], "reason": hit[1],
                                 "url": lead.evidence[0].source_url})
                continue
            c = lead.classification
            proposed[(lead.kind, lead.source_key)] = {
                "source": it.source, "title": lead.title, "url": lead.evidence[0].source_url,
                "agencies": sorted(c.agencies), "services": sorted(c.services), "sectors": sorted(c.sectors),
                "signals": sorted(c.signals), "score": lead.score, "matched": c.matched,
                "deadline": lead.deadline.isoformat() if lead.deadline else None,
            }

    raw_keys = {it.key for it in items}
    current: dict[tuple[str, str], dict] = {}
    for r in store.query(include_expired=True):
        if r["kind"] == "manual" or r["source_key"] not in raw_keys:
            continue  # manual leads and other sources are outside this comparison
        current[(r["kind"], r["source_key"])] = {
            "id": r["id"], "title": r["title"], "status": r["status"],
            "agencies": sorted(r["agencies"]), "services": sorted(r.get("services") or []), "sectors": sorted(r["sectors"]),
            "signals": sorted(r["signals"]), "score": r["score"], "matched": r["matched"],
        }

    new = [proposed[k] for k in proposed.keys() - current.keys()]
    dropped = [current[k] for k in current.keys() - proposed.keys()]
    changed = []
    for k in proposed.keys() & current.keys():
        p, c = proposed[k], current[k]
        diffs = {f: (c[f], p[f]) for f in ("agencies", "services", "sectors", "signals", "score") if c[f] != p[f]}
        if diffs:
            changed.append({"title": p["title"], "id": c["id"], "status": c["status"], "changes": diffs,
                            "url": p["url"]})

    if args.json:
        print(json.dumps({"raw_items": len(items), "current_leads": len(current),
                          "proposed_leads": len(proposed), "new": new, "dropped": dropped,
                          "changed": changed, "screened": screened}, indent=2, ensure_ascii=False, default=str))
        return 0

    print(f"Raw items checked: {len(items)}" + (f" (source {args.source})" if args.source else ""))
    print(f"Leads now: {len(current)}  ->  with current rule files: {len(proposed)}")
    print(f"NEW {len(new)}   DROPPED {len(dropped)}   CHANGED {len(changed)}   SCREENED {len(screened)}")
    if new:
        print("\nNEW (would become leads):")
        for x in sorted(new, key=lambda x: -x["score"])[: args.show]:
            print(f"  + [{x['source']}] {x['title'][:100]}")
            print(f"      {'; '.join(m for m in x['matched'] if not m.startswith('sector:'))}  score {x['score']}")
            print(f"      {x['url']}")
    if dropped:
        print("\nDROPPED (no longer match; reclassify keeps them and lists them):")
        for x in dropped[: args.show]:
            print(f"  - {x['id']} [{x['status']}] {x['title'][:100]}")
            print(f"      was: {'; '.join(x['matched'])}")
    if changed:
        print("\nCHANGED:")
        for x in changed[: args.show]:
            parts = [f"{f}: {old} -> {new_}" for f, (old, new_) in x["changes"].items()]
            print(f"  ~ {x['id']} [{x['status']}] {x['title'][:90]}")
            print(f"      {' | '.join(parts)}")
    if screened:
        print("\nSCREENED (made by the rules, held back by [screen]):")
        for x in screened[: args.show]:
            print(f"  x [{x['rule']}] {x['title'][:95]}")
            print(f"      {x['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
