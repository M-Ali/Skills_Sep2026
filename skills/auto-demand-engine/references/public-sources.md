# Public sources for the Demand Engine

What is already in `D:/personal/BHT_Sep26/data/`, checked 17 Sep 2026.

## Pakistan Economic Survey 2025-26, chapter 13 (`13_Transport_and_Communications.pdf`)

26 pages; the vehicle tables are text (extract with pdfplumber; no OCR needed).

| table | page | what | grain | trap |
|---|---|---|---|---|
| 13.3 Number of motor vehicles registered | 21 | motorcycles (2 and 3 wheels), cars/jeeps/station wagons, cabs/taxis, buses, trucks, others, total | calendar year 2011–2025, national | cumulative registrations, includes scrapped vehicles; source PBS |
| 13.4 Motor vehicles on road (LCV, HCV) | 22–23 | '000 by type | fiscal year 2010-11 to 2025-26 (Jul–Mar) | **base year changed in 2018-19**: motor cars 7,470.8k (2018-19) then 3,960.2k (2019-20). Never compute growth across the break; source NTRC |
| 13.5 Motor vehicles production | 24 | motorcycles/rickshaws, cars & jeeps, LCVs, buses, trucks, tractors | fiscal year; 2025-26 Jul–Mar provisional | PBS numbers, not PAMA; they differ from PAMA totals, so don't mix the two in one series; 2023-24 row is missing |
| 13.6 Motor vehicles imports | 25 | units by HS-style category (motorcycles, cars, pickups, SUVs, electric vehicles…) | fiscal year | columns are misaligned in the extracted text and some values look implausible for units (e.g. "Passengers Cars" 874,386 in 2011-12); verify against the PBS original before use |

The chapter has no provincial or city split.

## PAMA historical PDF (`Historical-Data-1995-2026.pdf`)

4 pages, annual production (P) and sales (S) by model, FY1995-96 to
2025-26, `~` = not reported. Mainly for the Market Engine; here for long-run
sales against drivers.

## Loaded since

- **Census 2023** (`data/public/census/Population_tables_2023.xlsx`): households,
  population 2023 and 2017, average household size and growth by province,
  division and district; 130 places in the `population` table. Use **households**
  as the denominator for car ownership, not people: household size runs from
  about 5.2 in Hyderabad division to 6.5 in Bahawalpur. Known gap, reported by
  the import check: the four provincial sheets sum to 37.93m households against
  the national 38.34m, because Islamabad and AJK/GB are not in them.
- **Google Trends**: `search_interest` table, 17 terms over 25 months plus a
  19-year brand series. Relative index only; see the skill for the anchor method.

## To add
- Monthly drivers not yet in `data/`: SBP policy rate and auto financing
  outstanding, PKR/USD, petrol prices, CPI. Record the publication and
  release date for each.
