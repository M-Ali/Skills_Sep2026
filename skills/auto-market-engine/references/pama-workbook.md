# PAMA production and sales workbook

What was found in `data/five-years-12.xlsx` (downloaded from the PAMA website,
file dated 17 Sep 2026). Read this before building or fixing the importer.

## Shape

- 19 sheets, one per fiscal year: `2007-08` … `2025-26` (July to June).
- Each sheet stacks sections: PASSENGER CARS (by engine size: 1300cc and
  above, 1000cc, below 1000cc, electric car), LCVS VANS & JEEPS / JEEPS &
  PICKUPS, TRUCKS, BUSES, FARM TRACTORS, MOTORCYCLES & THREE-WHEELERS.
- A month header row per section: model-label column, then 12 month columns,
  then `Cumulative`. Month labels drift: `Jul'07`, `Oct' 07`, `July'15`,
  `Sept'15`, `July'2020`, `July'25`, `June'26`. Parse by column position under
  the header, not by label text.
- Each model is two rows: the name row with `Prod.` or `Prod` in the next
  column, then a row with `Sale` (the name cell is blank). Brand and
  assembler are often in one cell with padding, e.g.
  `HAVAL / TANK            SAZGAR`, `Honda Cars   (Civic & City)`.
- `Sub-Total`, `TOTAL CARS`, `TOTAL JEEPS & PICK-UPs`, `TOTAL TRUCKS & BUSES`
  etc. are totals: exclude them from rows, but use them to **check** the
  import (sum of models = subtotal for every month).
- Some rows are short: in 2024-25 and 2025-26, Road Prince rows hold 5–6
  values for 12 months. Their position under the month headers decides which
  months they are; don't left-align them.
- Up to 2020-21 most rows say `Prod.` (with a dot); from 2021-22 mostly
  `Prod`. Match both. Verify each fiscal year separately against its totals.

## Brand and segment mapping

Keep a hand-maintained mapping file (label → brand, model, segment) rather
than parsing names with rules, because groupings change across years:
Honda Civic and City separate until 2014-15, then combined; Toyota Corolla
alone in 2020-21, then "Corolla, Yaris & Corolla Cross". Record the grouping
in the model name so a comparison across a change is visible.

## Checks the importer must pass

1. Every month's model sum equals the sheet's subtotal and total rows.
2. Cumulative column equals the sum of 12 months (or of the months present).
3. No month appears in two sheets.
4. `source` on every row, e.g. `PAMA five-years-12.xlsx 2025-26`.

## Related public file

`data/Historical-Data-1995-2026.pdf`: PAMA annual production (P) and sales
(S) by model, FY1995-96 to 2025-26. `~` = not reported. Useful to extend
history before 2007-08 at annual grain, and to cross-check fiscal-year totals
from the workbook (e.g. Honda Civic & City 2025-26 sales 24,416 appears in both).
