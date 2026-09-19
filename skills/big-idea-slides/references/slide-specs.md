# Slide specs - Big Idea section

Measured from the PTCL deck (`pakistan_fixed_broadband_category_creati_2026-09-11-v14_S.pptx`,
slides 31-37). 16:9 (13.333 x 7.5 in), blank layout, Segoe UI throughout, every box a
python-pptx rectangle with no outline and no shadow. `scripts/build_big_idea_section.py`
implements this; the spec is here so a slide can be checked or rebuilt elsewhere.

## Palette

| Token | Hex | Use |
|---|---|---|
| NAVY | 102A43 | header bar, idea band, insight lines, conclusion band |
| INK | 1A1A1A | body text |
| MUTED | 6B7480 | section labels, sources, the removal test |
| ACCENT | C8102E | rules, arrow, comms platform, PROVISIONAL tag |
| PALE | F2F5F8 | interpretation panel, alternatives panel, platform box |
| DIM | 9FB4C7 | kicker on navy, divider subtitle |
| WHITE | FFFFFF | text on navy |

## Header (slides 2-7)

- Navy bar 0,0 full width x 1.00 in.
- Kicker x0.60 y0.14 w12.0, 10 pt bold DIM, upper case, separated by "  ·  ":
  step number, what the insight is, where it comes from.
- Title x0.60 y0.42 w12.1, 22 pt bold WHITE.

## Slide 1 - divider

Full-bleed NAVY; ACCENT rule x0.90 y2.30 w1.60 h0.06; "The Big Idea" x0.90 y2.60, 40 pt bold
WHITE; two DIM lines at y3.55, 16 pt: "Consumer insight  +  Category insight  +  Brand
insight" and "Three single lines, combined into one organising thought."

## Slides 2-4 - the three insights

- ACCENT rule x0.60 y1.35 w0.08 h1.75 (vertical), with the line at x0.95 y1.35 w11.7,
  23 pt bold NAVY, wrapped in curly quotes.
- Optional tag: ACCENT box x10.90 y1.05 w1.80 h0.26 with 9 pt bold WHITE centred text
  ("PROVISIONAL").
- "EVIDENCE" label x0.60 y3.40, 10 pt bold MUTED; bullets x0.60 y3.72 w6.90 h3.10, 11 pt INK,
  each prefixed "·  ", 7 pt space after. Four to five bullets fit; five is the ceiling.
- Interpretation panel: PALE rectangle x7.90 y3.40 w4.80 h3.40; label x8.15 y3.55, 10 pt bold
  MUTED; body x8.15 y3.90 w4.35 h2.85, 10.5 pt NAVY, three short paragraphs.
- Source x0.60 y7.05 w12.1, 8.5 pt MUTED: corpus or document, size, and the limit.

## Slide 5 - convergence

- Three columns at x0.60, 4.70, 8.80, each w3.90: ACCENT rule h0.05 at y1.35; label y1.55,
  10 pt bold MUTED ("CONSUMER INSIGHT  ·  Relevant"); short line y1.90 h1.40, 14 pt bold NAVY.
- Arrow "▼" x0.60 y3.30 w12.1 centred, 22 pt bold ACCENT.
- Idea band: NAVY rectangle x0.60 y3.85 w12.1 h1.55; "THE BIG IDEA" x0.90 y3.98, 10 pt bold
  DIM; the idea x0.90 y4.30 w11.5, 32 pt bold WHITE (28 pt if it runs past ~60 characters).
- Meaning sentence x0.60 y5.65 w12.1 h0.90, 14 pt INK.
- Removal test x0.60 y6.60 w12.1, 10.5 pt MUTED, run-in bold label "Test:".

## Slide 6 - strategy and platform

Left column w7.20 from x0.60:
- "STRATEGY" label y1.35; statement y1.65 h1.90, 16 pt bold NAVY.
- Platform box: PALE rectangle y3.70 h1.30; "COMMS PLATFORM" label x0.85 y3.82; platform
  x0.85 y4.12 w6.80, 19 pt bold ACCENT with a run-in "Position [brand] as".
- "WHY IT HOLDS" label y5.25; three run-in lines y5.55 h1.60, 11 pt INK
  ("Relevant:", "Distinctive:", "Ownable:").

Right panel: PALE rectangle x8.20 y1.35 w4.50 h5.80; "ALTERNATIVES CONSIDERED" label x8.45
y1.50; entries x8.45 y1.85 w4.05 h5.20, 10.5 pt NAVY, run-in bold title then the trade-off,
9 pt space between. Four entries fit (three alternatives plus the swap test).

## Slide 7 - the price of the idea

- Left: label x0.60 y1.35 w6.0; then commitment rows from y1.75, step 0.88: ACCENT bar
  x0.60 w0.05 h0.72, title x0.80 13 pt bold NAVY ("1  Price notice"), body x0.80 +0.35,
  11 pt INK. Five rows fit above the band.
- Right: "MEDIA PRINCIPLES" label x7.00 y1.35 w5.70; channel-insight quote y1.70 h0.90,
  13 pt bold italic NAVY; five run-in principles y2.65 h3.60, 11.5 pt INK, 9 pt space.
- Conclusion band: NAVY x0.60 y6.35 w12.1 h0.80; text x0.85 y6.47 w11.6, 12.5 pt bold WHITE -
  what to do if the client will not commit.

**Fit rules.** Five evidence bullets, five commitments, five media principles, four
alternatives entries. Past that, cut content rather than shrinking type below the sizes above -
these slides carry the argument and must stay readable from the back of a room.
