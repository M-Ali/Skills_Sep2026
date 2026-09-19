---
name: auto-market-engine
description: "Market Engine of autopulse (Automotive Growth Intelligence for Pakistan's auto clients such as Suzuki and Hyundai): answers 'what is happening in the market' from the autopulse database of PAMA monthly production and sales (FY2007-08 onward), plus annual registered vehicles, vehicles on road and population - share and growth by brand, segment and model, production against sales, launch curves, and the local-versus-imported split - written as signals the Growth Engine can join. Use whenever the user mentions PAMA data, car or bike sales numbers, auto market share, segment share, production figures, which brand or model is growing or losing, monthly or fiscal-year auto sales, importing this month's PAMA file, updating the database, a new model's first months (Fronx, Jetour, Haval), the market monitor, imported used cars versus local assembly, or asks 'how is Suzuki/Hyundai/Toyota/Honda doing' in Pakistan - even if they only drop a PAMA file and say 'what's the picture this month'."
---

# Market Engine

**Question:** what is happening in the market?
**Data:** public only, in `data/public/db/autopulse.db`. Any client may see the output.
**Project:** `D:/personal/BHT_Sep26` (uv app `autopulse`). Read its `AGENTS.md` before changing code.

Run from the project folder, or anywhere with `uv run --project D:/personal/BHT_Sep26 autopulse ...`.

## Status

| Part | Status | Command |
|---|---|---|
| Database of PAMA monthly production + sales, FY2007-08 to date | built | `db import-pama <xlsx>` |
| Annual registered vehicles, vehicles on road, PBS production | built | `db import-survey <pdf>` |
| Population and households by district | built | `db import-population <xlsx>` |
| Monitor: sales, production, share, growth, flags, signals | built | `market monitor [--category C] [--month YYYY-MM]` |
| What is loaded, coverage, failed checks, unmapped labels | built | `db status` |
| Imports (used and new CBU) as a series | **not built** | table 13.6 needs checking against the PBS original |
| Launch tracker against the median of earlier launches | built | `market launch --model Fronx` |
| Annual PAMA history from the 1995-2026 PDF | **not built** | |

Don't invent a command that isn't here. If something is not built, say so and offer to build it.

## The monthly update

```bash
uv run autopulse db import-pama data/public/pama/five-years-12.xlsx --label "PAMA five-years-12.xlsx (downloaded <date>)"
uv run autopulse db status          # coverage, failed checks, labels needing a mapping
uv run autopulse market monitor --category "PASSENGER CARS" --month 2026-06
```

The importer checks every model row against PAMA's own Sub-Total and TOTAL rows
before writing, so a parsing slip shows up as a failed check rather than a wrong
share in a client deck. Re-importing the same file changes nothing; a revised
file is layered on top, newest wins, and the earlier figures stay.

A new model line (a launch, a rename) has to be added to
`data/public/model_map.csv` with its brand, model and segment. Until it is, the
monitor refuses to compute shares, because a missing mapping would silently drop
a brand. `db status` and `db map` name what's missing.

## What is code and what is judgement

**Code does every number and every call that can be made by rule:**

| Flag on each row | Rule | What it means for the write-up |
|---|---|---|
| `small_base` | base month under `--small-base` (default 100 units) | report units, not a growth % |
| `new_entry` | no sales in the comparison month | growth is blank; a share change from zero is real |
| `stock_building` | production above sales | units went to dealers, not necessarily to buyers |

Growth on a small base is also withheld from the signals, so the Growth Engine
can't rank a 400% jump on 5 units as an opportunity.

**Judgement is what to say:** which of the computed movements matter to this
client this month, and what to warn about. Never retype a number: read it from
the monitor's xlsx or the signals CSV.

## The three market universes: never say "market share" unqualified

1. **Locally assembled** — what PAMA reports, monthly. This is where the client
   competes on equal terms, and it is what `share_of_local_market_pct` means.
2. **Imported** — used and new CBU. No monthly public source; annual estimate only.
3. **Total** = 1 + 2, annual and approximate.

So: "Suzuki holds 63.9% of the locally assembled market in June 2026". Not
"63.9% of the market". Imports press hardest on the small-car and used-hybrid
segments, so a Cultus or Alto share means less without that caveat than a
Fortuner share does.

## Reading the numbers

- **Sales for demand, production for stock.** Both are in the database.
  `production_minus_sales` over two or three months is the closest public
  signal for stock building; PAMA publishes no inventory.
- **Share in points, growth in percent.** Don't mix the units.
- **Seasonality:** the fiscal year starts in July. Put the same month last year
  beside any month-on-month move, and check for Ramzan and Eid timing, the June
  budget, price rises and plant shutdowns before calling a move a trend.
- **Coverage:** PAMA covers members only. Kia passenger cars, Changan, MG and
  BYD are not in the 2025-26 sheets, nor is any import.
- **Grouping changes:** PAMA merges and splits lines (Honda Civic and City
  combined from 2015-16; Toyota Corolla alone, later with Yaris and Corolla
  Cross; Haval combined with Tank). `model_map.csv` records these in its note
  column and the model name says "(combined)". A year-on-year comparison across
  such a change is not like for like.

## Launch tracker

```bash
uv run autopulse market launch --list                 # launches, newest first
uv run autopulse market launch --model Fronx          # track one against its peers
```

Each launch is indexed to its own launch month, then compared with the **median
of earlier launches at the same age**, computed from the data every run. What
the code decides, so nobody has to:

- **A PAMA relabel is not a launch.** When PAMA merges or renames a reporting
  line ("Haval H6 & Tank (combined)"), the new label starts at full volume and
  would flatten the benchmark. Those rows are marked `relabel` from the model
  name and `model_map`'s note, and excluded from the benchmark.
- **A tiny launch month is flagged**, not silently indexed: under 50 units in
  month one makes every later percentage meaningless, so read the units.
- **Production ahead of sales** every month is flagged as stock reaching
  dealers faster than buyers.
- Fewer than three comparable launches means the benchmark is called indicative.

Attention (search interest, YouTube comments) is printed beside the curve as
**context, never a forecast**: pre-launch buzz was tested across eight launches
and does not predict launch size (+0.82 with Toyota Yaris in, +0.25 without).

Signals: `launch_month_units` and `launch_vs_benchmark_pct` (100 = the median
launch at that age).

## Signals this engine writes

`engine=market`, `scope=public`, `geography=Pakistan`, for brand, segment and model rows:

| metric | comparisons | change_unit |
|---|---|---|
| `units` | level, mom, yoy | pct |
| `share_of_local_market_pct` | level; brands also mom, yoy | pts |
| `production_units` | level, mom | pct |
| `production_minus_sales` | level | |

Format (master copy `src/autopulse/signals.py`): `id, engine, scope, period,
geography, brand, model, segment, metric, value, baseline, change, change_unit,
comparison, source`. Check any file with `autopulse signals check`.

## Limits

- National only: PAMA has no province or city split. Geography comes from the
  Demand and Dealer engines.
- No prices, no discounts, no used-car values here: those are the Competition Engine.

## Output

Lead with 3-5 decided findings, each citing its signal ids, then the monitor
tables, then the caveats that apply (universe, coverage, grouping changes,
flagged small bases). Give the paths of the xlsx and signals CSV, and say which
PAMA file and download date the figures came from: reports must cite their source.

## Changelog

- 2026-09-18 (later): launch tracker built, with the relabel, small-base and
  stock flags. Benchmark from 10 comparable launches since 2018 runs roughly
  flat (100, 100, 88, 76, 90, 92, 113), not the steep ramp an earlier
  hand-picked subset suggested.
- 2026-09-18: rebuilt on the database. PAMA production and sales both imported
  (228 months, FY2007-08 to FY2025-26), annual Survey tables and census
  population added, `share_of_market_pct` renamed `share_of_local_market_pct`,
  `small_base` / `new_entry` / `stock_building` computed instead of left to
  judgement, small-base growth withheld from signals.
- 2026-09-17: created. Monitor and signals built on a sales CSV.
