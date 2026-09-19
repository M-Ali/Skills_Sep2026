# Slide specs - Brand Meaning Ladder section

Measured from the PTCL deck (`pakistan_fixed_broadband_category_creati_2026-09-11-v14_S.pptx`,
slides 23-27). The slides are 16:9 (13.333 x 7.5 in), blank layout, all text Segoe UI, and all
boxes are python-pptx rectangles with no outline and no shadow. The builder script implements
exactly this. The spec is here so a slide can be checked, or rebuilt in another tool.

## Palette

| Token | Hex | Use |
|---|---|---|
| NAVY | 102A43 | title bar, divider background, conclusion band, level names |
| INK | 1A1A1A | body text |
| MUTED | 6B7480 | column heads, consumer questions, footnotes, unsupported factors |
| ACCENT | C8102E | divider rule, markers, target-row bar |
| PALE | F2F5F8 | highlighted rows, current-factor column |
| FAINT | FAFBFC | ordinary rows |
| SKY | 9FB4C7 | divider subtitle |
| WHITE | FFFFFF | text on navy |

## Shared frame (slides 2-5)

- Title bar: rectangle 0,0 full width x 1.00 in, NAVY. Title at x0.60 y0.30 w12.1, 20-24 pt
  bold white. Use 20 pt when the title runs past ~60 characters.
- Standfirst: x0.60 y1.10 w12.1 h0.35, 10.5 pt bold NAVY. One or two sentences defining the
  columns or the method.
- Column heads: y1.55, 9 pt bold MUTED, upper case.
- Rows: six rows, Level 6 at the top, starting y1.82, height 0.74, gap 0.04 (so the last
  row ends at 6.50). Row fill FAINT; target or marked rows PALE with a 0.06 in ACCENT bar
  on the left edge.
- Level cell: x0.72, level name 10 pt bold NAVY, then the consumer question 8.5 pt MUTED on
  a second paragraph.
- Conclusion band: rectangle x0.60 y6.55 w12.1 h0.62 NAVY; text x0.85 y6.64 w11.6, 11 pt
  bold white. One sentence, two lines at most.
- Footnote: x0.60 y7.20 w12.1 h0.28, 8 pt MUTED. Framework name, sources, method caveat.

**Fit rule:** six rows must end above the band at 6.55. When text does not fit, shrink the
type (8.5 pt is the floor for factor lists), never the row count or the band.

## Slide 1 - divider

- Full-bleed NAVY rectangle.
- ACCENT rule x0.90 y2.30 w1.60 h0.06.
- Title x0.90 y2.60 w11.4, 40 pt bold white: "The Brand Meaning Ladder".
- Subtitle x0.90 y3.55 w11.4, about 18 pt SKY, two paragraphs with a blank one between:
  what the ladder is, then "From functional benefits -> to emotions -> to values and purpose."

## Slide 2 - placement

Columns: level x0.72 w2.9 | brands x3.90 w5.2 | marker x9.30 w3.3.

- Level cell uses the consumer *voice* of each level rather than the question:
  1 "I am here", 2 "Reason to buy me", 3 "Here is what I can do for you",
  4 "I am like you; you are like me", 5 "I think like you do", 6 "I change things you would like to".
- Brands cell: `Brand (mean)` for each brand whose modal level is this row, then " - " and a
  short description of what they do. Brands 10.5 pt INK.
- Marker cell: 10.5 pt bold ACCENT, upper case. Only on rows that carry the argument.
  Marked rows get PALE fill and the ACCENT bar.
- Empty rungs say so plainly ("Nobody in this category.").

## Slide 3 - factor list

Columns: level x0.72 w1.9 | current x2.60 w3.45 | potential x6.20 w4.6 | unsupported x10.95 w1.65.

- The current column sits on a PALE panel (x2.50 w3.55) so it reads as "what is taken".
- Factors are joined with "  ·  ". Current 9 pt bold NAVY; potential 8.5 pt INK; unsupported
  8.5 pt MUTED.
- † marks category additions. The standfirst defines Current, Potential, Unsupported and †.

## Slide 4 - category evidence

Columns: level x0.72 w1.8 | brands claim x2.40 w4.5 | customers judge x7.00 w2.75 |
open x9.85 w2.75.

- The open column sits on a PALE panel and is bold NAVY: it is the column the eye should land on.
- Others 8.5 pt INK. Counts in brackets with the leading brands:
  "value for money (31: Zong 9, Optix 7)".

## Slide 5 - client ladder

Columns: level x0.72 w1.85 | factors in category x2.55 w5.05 | client today x7.75 w3.05 |
placement x10.95 w1.75.

- Factors cell: two paragraphs with bold run-in labels, "In use:" and "Open:", 8.5 pt.
- Client cell: "Says:" (post count at this level, from the computed table) and "Heard:"
  (consumer evidence with a strength word), 8.5 pt.
- Placement cell: verb 9.5 pt bold NAVY (HOLD, PROVE, NEXT, LATER, NOT NOW), with a sub-line
  8.5 pt INK stating the condition. The target row's verb is "PLACE [CLIENT] HERE", 10 pt
  bold ACCENT, and the row gets PALE fill and the ACCENT bar.
- The standfirst states the client's n, mode and mean: "PTCL says = its 24 coded posts,
  classified by level (mode L1, mean 2.4)."
