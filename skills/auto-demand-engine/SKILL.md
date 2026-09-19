---
name: auto-demand-engine
description: "Demand Engine of autopulse (Automotive Growth Intelligence for Pakistan's auto clients such as Suzuki and Hyundai): answers 'where is future demand emerging' - the economic drivers of car demand (policy rate and bank auto financing, rupee, fuel prices, inflation, taxes), the vehicle parc and motorisation from registered-vehicle and population data, search interest by province and city, and a demand outlook - written as signals. Use whenever the user asks why car sales rose or fell, what's driving auto demand, the effect of interest rates, auto loans, petrol prices or the budget on car sales, vehicles per 1,000 people, registered vehicles or vehicles on road, population-based market potential, Google Trends for car models, or a sales forecast for Pakistan autos - even if they only say 'is the market going to pick up'."
---

# Demand Engine

**Question it answers:** where is future demand emerging?
**Data:** public, except when a client's GA4 or lead geography is used for
catchment-level demand (then `scope=client:<name>`).
**Project:** `D:/personal/BHT_Sep26` (uv app `autopulse`).

## Status

| Part | Status | Command |
|---|---|---|
| Google Trends search interest, anchored groups | built | `demand trends` |
| Share of search by brand or model | built | part of `demand trends` |
| Registered vehicles, vehicles on road, census households | built (Market Engine imports them) | `db import-survey`, `db import-population` |
| Economic drivers: policy rate, auto financing, PKR, fuel, CPI | **not built** | no series loaded yet |
| Keyword volumes (what people actually type) | **not built** | needs a Google Ads developer token with Basic access |

```bash
uv run autopulse demand trends --timeframe "2024-09-01 2026-09-18" --geo PK
uv run autopulse google check          # which credentials are in .env
```

### Trends is an index, never a count

Trends scales each request of at most five terms to 100, so two terms from
different requests can't be compared. One **anchor** term rides in every request
and the groups are rescaled through it; a group whose anchor is too small to
rescale against is left on its own scale and excluded from any share. The code
enforces this - only rows on the shared scale enter a share of search.

### Tested here, and it did not hold

Share of search does **not** predict sales in Pakistan. Brand level, 19 years,
228 months: correlations of +0.27 to +0.36 on levels (best at a 2-3 month lead)
and about +0.1 on year-on-year changes. Two years of model-level data gives
noise. Don't sell it as a leading indicator. Likely reasons: a supply-constrained
market where monthly sales follow allocation, nameplate searches catching used
and imported interest, and a rounded index.

**What it is good for, and what to use it for:**

1. **The desire-versus-purchase gap.** Over 19 years Honda takes 41.4% of brand
   search against 13.5% of sales (+27.9 pts); Suzuki 25.1% against 53.8%
   (-28.7). Stable enough to report as a brand fact.
2. **Where attention sits.** Honda's search share is 49.0% in Punjab against
   38.4% in Sindh; Suzuki 29.5% in Sindh against 22.5% in Punjab. A
   media-weighting input, not a sales claim.
3. Launch attention as context in the Market Engine's launch tracker - shown
   beside the sales curve, never as a forecast, because pre-launch buzz doesn't
   predict launch size either (+0.82 with Toyota Yaris in the sample, +0.25
   without it).

## What is code and what is judgement

- **Code:** loading each series with its source and period, aligning
  frequencies (monthly, fiscal year, calendar year), per-capita ratios,
  correlations and any model, and signals.
- **Judgement:** which drivers plausibly matter this period, and how strongly
  to word a relationship. With ~20 years of data and many drivers moving
  together, a regression shows association, not cause. Say "moved with", not
  "caused".

## Method

1. **Assemble series** with source and period on every row. See
   `references/public-sources.md` for what exists and its traps (fiscal vs
   calendar year, the 2018-19 base-year break in vehicles on road).
2. **Market potential.** Registered vehicles (calendar year) and vehicles on
   road (fiscal year) ÷ population → vehicles per 1,000 people, by vehicle
   type. National only in the Economic Survey tables; provincial needs the
   PBS or provincial excise source. Growth in parc minus new PAMA sales
   roughly indicates imports and re-registrations: label as indicative.
3. **Drivers.** Monthly PAMA car sales (Market Engine) against policy rate,
   auto financing outstanding, PKR/USD, petrol price, CPI. Lag each driver
   1–6 months and report which lags hold across more than one period, not the
   single best fit.
4. **Search interest.** Google Trends by model, province and city: an index
   within each query, so compare shapes and timing, not levels across models.
5. **Outlook.** A range for the next 3–6 months with the assumptions stated
   (e.g. "if the policy rate holds"), never a single number.
6. **Write signals.**

## Signals this engine writes

`engine=demand`.

| metric | geography | comparisons |
|---|---|---|
| `vehicles_registered` (by type in `segment`) | Pakistan | level, yoy |
| `vehicles_per_1000_people` | Pakistan / province | level, yoy |
| `policy_rate_pct`, `auto_financing_pkr_bn`, `pkr_usd`, `petrol_pkr_litre`, `cpi_yoy_pct` | Pakistan | level, mom, yoy |
| `search_index` (by model) | Pakistan / province / city | level, mom, yoy |
| `sales_outlook_low`, `sales_outlook_high` | Pakistan | level |

Signal format (master copy: `src/autopulse/signals.py`): `id, engine, scope,
period, geography, brand, model, segment, metric, value, baseline, change,
change_unit, comparison, source`. Annual series use the fiscal or calendar
year's last month as `period` and say which in `source`.

## Limits

- Google Trends gives province and city, not catchment. Catchment demand
  needs the client's GA4 or lead locations.
- Registered-vehicle counts are cumulative registrations and include scrapped
  vehicles; they overstate the parc in use.

## Changelog

- 2026-09-18: Google Trends built with the anchor method; `search_interest`
  table keeps the query group so levels are never compared across scales. Share
  of search tested against 19 years of PAMA and recorded as not predictive;
  kept for the desire-versus-purchase gap and provincial attention. Census
  population loaded (households are the denominator for car ownership).
- 2026-09-17: created. Sources noted: Pakistan Economic Survey 2025-26
  chapter 13 tables; population to be added.
