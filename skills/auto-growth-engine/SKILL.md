---
name: auto-growth-engine
description: "Growth Engine of autopulse (Automotive Growth Intelligence for one Pakistan auto client at a time, e.g. Suzuki or Hyundai): answers 'what action could convert this opportunity into sales' by joining signals from the Market, Consumer, Competition, Dealer and Demand engines on brand, model, geography and period, and turning the combinations into ranked, evidence-cited recommended investigations (media, offer, financing message, dealer follow-up, stock, creative, CRM). Use whenever the user asks what a client should do next, where the growth opportunity is, to connect the market, consumer, competitor and dealer findings, for an insight-to-action brief, a monthly recommendations page, or 'so what' for an auto client - even if they only say 'what should Hyundai do about Tucson'. Reads signals only; never a raw data file."
---

# Growth Engine

**Question it answers:** what action could convert the opportunity into sales?
**Data:** signals only. For client X: public signals plus X's own, nothing
else.
**Project:** `D:/personal/BHT_Sep26` (uv app `autopulse`).

## Status

**Built** for the public engines:

```bash
uv run autopulse growth run --period 2026-06 --category "PASSENGER CARS"
uv run autopulse growth run --period 2026-06 --client suzuki      # adds that client's own signals
```

It collects the period's signals from every engine that has them, writes them to
`workspace/out/signals/growth_<period>/collected.csv`, reads them back **through
the audience check**, joins them, and writes a versioned recommendations page to
`workspace/out/` plus one signal per recommendation.

Three engines write signals today:

| Engine | Signals available |
|---|---|
| Market | `units`, `share_of_local_market_pct`, `production_units`, `production_minus_sales`, `launch_month_units`, `launch_vs_benchmark_pct` |
| Consumer | `coded_comments`, `theme_share_pct:<theme>` for 12 barriers |
| Demand | `search_index`, `share_of_search_pct` |

All three are `scope=public`, so a run works for either client with no private
data. Dealer signals (the private half) still need a pilot client, so the two
patterns that need dealer conversion never fire yet.

### What the code decides

| Rule | Why |
|---|---|
| a candidate needs **two or more engines** | one engine is a finding; it belongs in that engine's read-out, and the page lists those separately |
| shares are recomputed over the **same set of models** | a PAMA share is of everything PAMA reports, motorcycles included, while a search share is of the tracked terms; comparing them directly is meaningless |
| evidence more than 3 months apart is dropped, and the span is printed | signals months apart are not one story |
| confidence: high = 3+ engines within a month; medium = 2+ within three months; otherwise low | stated, not felt |
| ranked by units at stake x engines agreeing | the size of the prize, not how good the story is |

### The engines don't share a calendar

PAMA closes its fiscal year in June while comments and search run to today, so
signals are collected in a window around the period (2 months back, 3 forward),
each keeps its own period, and every candidate prints the span. A run says which
period each engine's signals came from.

## Why signals only

Every other engine has already decided what its data means and recorded the
source. If this engine re-read raw files it would re-interpret them, and two
engines could disagree about the same number. Reading signals also makes the
client wall checkable: load them with
`autopulse signals check <files> --client <name>` (or
`load_signals(files, client=...)`), which refuses any other client's rows.

## What is code and what is judgement

- **Code:** loading and checking signals, joining them on brand, model,
  geography and period, applying the rules below to produce candidate
  combinations with the signal ids attached.
- **Judgement:** choosing which combinations are worth a client's attention,
  and wording the investigation. The model adds no number that isn't in a
  cited signal.

## Method

1. **Load** all signal files for the client and period through the check.
2. **Join** on brand + model, then geography, then period (allow the demand
   signal to lead sales by 1–3 months).
3. **Find combinations.** A candidate needs signals from **at least two
   engines** pointing the same way. Patterns worth looking for:

| pattern | signals |
|---|---|
| Demand without conversion | demand `search_index` up + dealer conversion down or market share flat |
| Barrier with a competitor opening | consumer barrier share up (price, financing) + competition promo or price cut on a rival |
| Share loss in a growing segment | market segment units up + brand share down |
| Voice below share | competition `sov_minus_som_pts` strongly negative + market share falling |
| Launch not converting | market launch production ≫ sales + consumer delivery or price complaints |
| Stock or delivery friction | dealer booking-to-delivery days up + consumer `delivery` theme up |

4. **Rank** by size of opportunity (units or share points at stake, from the
   market signals) × number of engines agreeing. Don't rank by how
   interesting the story is.
5. **Write each recommendation** in this form:

```
<Model> — <place>, <period>
What the signals show: <one sentence per signal, with its number>
Signals: <signal ids>
Recommended investigation: <action to test, e.g. evaluate financing
communication + dealer follow-up + local media in this catchment>
What would confirm it: <data to check, e.g. lead-to-test-drive rate by
source for Dealer X over 3 months>
Confidence: <low/medium/high> because <engines agreeing, sample sizes>
```

Example of the right register: "Search interest for Tucson in Sindh rose
while Dealer X's enquiry-to-test-drive rate fell and financing complaints
rose. Recommended investigation: evaluate financing communication and dealer
follow-up in this area." Wrong register: "Tucson sales are falling because of
financing." The signals show things moving together, not why.

## Signals this engine writes

`engine=growth`, `scope=client:<name>`, `metric=recommendation`,
`comparison=level`, `value` = rank, `source` = the ids of the signals behind
it joined with `;`.

## Limits

- One engine alone is a finding, not a recommendation: send it back as that
  engine's output.
- If the signals behind a candidate come from different periods by more than
  3 months, drop it or say so.

## Changelog

- 2026-09-18 (later): built. `engines/growth/` with `collect.py` (regenerate a
  period's signals), `patterns.py` (six patterns) and the renderer. Shares are
  recomputed over a common set of models, because a raw PAMA share and a search
  share are not comparable. 11 tests.
- 2026-09-18: unblocked. Market, Consumer and Demand all emit public signals.
  Two of the six patterns now have real inputs (search interest against
  share, consumer barrier share against a competitor move); the two that need
  dealer conversion still don't. Note that search interest is **not** a leading
  indicator here, so a "demand rising" pattern must rest on the level gap or on
  consumer evidence, not on a search trend alone.
- 2026-09-17: created. Patterns v1 (6). No code; only Market signals exist.
