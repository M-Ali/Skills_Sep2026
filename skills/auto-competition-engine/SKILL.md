---
name: auto-competition-engine
description: "Competition Engine of autopulse (Automotive Growth Intelligence for Pakistan's auto clients such as Suzuki and Hyundai): answers 'what are competitors doing' - their advertising and social output, message themes, share of voice against share of market, launches and promotions, list-price changes, and used-car prices and on money on PakWheels/OLX - and writes each change as a signal. Use whenever the user asks what Toyota, Honda, Haval, Kia, Changan, MG, BYD or any rival auto brand is posting, advertising, offering or charging in Pakistan, wants share of voice vs share of market for cars, a competitor price-change log, resale value or on-money tracking, or a competitive section for an auto client - even if they only say 'what's the competition up to'. Uses category-creative-scan and competitor-comms-audit for the creative work."
---

# Competition Engine

**Question it answers:** what are competitors doing?
**Data:** public only. Any client may see the output.
**Project:** `D:/personal/BHT_Sep26` (uv app `autopulse`).

## Status

| Part | Status |
|---|---|
| Social and ad creative scan, coded | use `category-creative-scan` / `competitor-comms-audit` |
| Share of voice vs share of market | **not built**: method below; share of market comes from the Market Engine's signals |
| Share of conversation (YouTube comments by brand) | available now from the Consumer Engine's database |
| List-price log | **not built** |
| Used-car prices and on money | **not built**: check PakWheels and OLX terms of service before any scraping |

## What is code and what is judgement

- **Judgement:** coding a post or ad (theme, product, offer, audience), and
  deciding whether a competitor move is a real shift or routine.
- **Code:** counts, share of voice, price change %, the SOV–SOM gap, and
  signals. Prices are recorded with the date and URL they were seen on, never
  from memory.

## Method

1. **Define the set.** Brands a client actually competes with, by segment.
   Include non-PAMA brands (Kia, Changan, MG, BYD and other importers or
   assemblers): they are invisible in PAMA data but not to buyers. The comment
   database already shows how much this matters - Changan Deepal, Kia Sportage,
   MG HS and Changan Alsvin together carry more coded comments than the Suzuki
   Alto, while PAMA reports none of them. Their aliases are in
   `data/public/model_aliases.csv`, so `consumer themes --model Sportage` works
   today even though no sales series exists for them.
2. **Creative and social.** Run `category-creative-scan` for posts and
   artwork, or `competitor-comms-audit` for ads (Meta Ad Library). Keep its
   coded file as this engine's input.
3. **Share of voice vs share of market.** SOV = a brand's share of coded
   posts/ads (or spend if known) in the segment for the period. SOM = its
   share of PAMA sales from Market Engine signals for the same segment and
   period. Report the gap in points. Brands without PAMA sales get SOV only,
   flagged "no SOM (non-PAMA)".
4. **Prices.** Log list-price announcements with effective date, variant,
   old and new price, and source URL. For used prices and on money, sample the
   same model/year/variant each month so the numbers are comparable, and
   record sample size.
5. **Write signals** and a short "what changed this month" list.

## Reading it

- SOV well above SOM is a brand investing to grow (or defending a launch);
  SOV well below SOM is a brand coasting on distribution. Both are hypotheses
  until the Growth Engine sees them next to demand and consumer signals.
- A promotion (free registration, discounted financing, cash discount) is a
  price move even when the list price stays put. Log it as one.

## Signals this engine writes

`engine=competition`, `scope=public`.

| metric | comparisons | change_unit |
|---|---|---|
| `sov_pct` | level, mom | pts |
| `sov_minus_som_pts` | level | |
| `list_price_pkr` (by variant in `model`) | level, mom | pct |
| `used_price_pkr`, `on_money_pkr` | level, mom | pct |
| `promo_active` (1/0, description in `source`) | level | |

Signal format (master copy: `src/autopulse/signals.py`): `id, engine, scope,
period, geography, brand, model, segment, metric, value, baseline, change,
change_unit, comparison, source`.

## Limits

- Paid media spend isn't public; SOV here is share of visible output, not of
  money. Say so.
- Scraping marketplaces may breach their terms and get blocked. Don't build a
  client-facing tracker on it until the terms are checked.

## Changelog

- 2026-09-18: the Consumer Engine's comment database gives a share of
  conversation for non-PAMA brands (Deepal, Sportage, MG HS, Alsvin) that no
  sales source covers. Aliases added so those brands match.
- 2026-09-17: created. Creative work via existing skills; SOV-SOM, price log
  and used-price tracker not built.
