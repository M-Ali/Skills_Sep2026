---
name: auto-consumer-engine
description: "Consumer Engine of autopulse (Automotive Growth Intelligence for Pakistan's auto clients such as Suzuki and Hyundai): answers 'what are people thinking' about cars, brands and models from a database of YouTube comments on PakWheels, Zawar Motors, Car Mate PK, Zain Ul Abideen and Pak Automobile - purchase barriers (price, financing, delivery, on money, resale, fuel economy, safety, features, after-sales, dealer experience, tax, brand trust), what buyers want, and how talk changes from launch to ownership, as signals by model and month. Use whenever the user mentions YouTube comments, consumer voice, what buyers are saying, complaints about a car, why people are not buying a model, sentiment on Tucson/Fronx/Alto/Haval, fetching or updating the comment database, PakWheels conversation, owner reviews, launch versus ownership sentiment, or wants the consumer side of an auto category - even if they only say 'here are the SUV comments, what's in them'. Hands the reading of a one-off comment file to comment-analysis."
---

# Consumer Engine

**Question:** what are people thinking?
**Data:** public YouTube comments in `data/public/db/autopulse.db`. A corpus from a
client's own pages or CRM is that client's data (`scope=client:<name>`), never pooled.
**Project:** `D:/personal/BHT_Sep26` (uv app `autopulse`). Read its `AGENTS.md` first.

## Status

| Part | Status | Command |
|---|---|---|
| YouTube video and comment database, 5 channels | built | `consumer fetch` |
| Title-to-model matching (comparison videos keep every model) | built | part of `consumer fetch` |
| What's held: channels, videos, models, comments | built | `consumer status` |
| Barrier coding to the 12 themes, with stance and stage | built | `consumer code` |
| Theme table, sourced quotes and signals | built | `consumer themes --model Alto` |
| Re-match titles after editing the map or aliases | built | `consumer rematch` |
| Reading the `unclear` stance (most of them) | **not built** | this is where a model pass belongs |
| Launch-versus-ownership split | **not built** | months-from-first-sale comes from PAMA |

## Fetching

```bash
uv run autopulse consumer fetch --since 2024-09-01 --videos-only     # list uploads, match titles
uv run autopulse consumer fetch --comments-only --max-videos 500     # busiest videos first
uv run autopulse consumer status
```

The key lives in `.env` as `YOUTUBE_API_KEY` (git-ignored, see `config.py`); the
official API is used, not scraping, because these numbers reach client work.
Free quota is 10,000 units a day: listing costs about 1 unit per 50 videos, a
page of 100 comments 1 unit. A run stops cleanly when quota runs out and
re-running continues where it left off, so the sweep can span days.

Rules the code already applies:

- **Comments off is not the same as no comments.** `comments_state` records
  `fetched`, `disabled`, `error` or `pending`.
- **A comparison video matches every model it names**, and those comments are
  ambiguous: never rest a single-model claim on them alone.
- **Authors are hashed.** The analysis is about opinions, not people. Don't put
  a commenter's name in a deliverable.
- **Busiest videos first**, because one long PakWheels review says more than
  twenty Shorts.

## Coding

```bash
uv run autopulse consumer code                       # code new comments
uv run autopulse consumer code --recode              # start again after editing the lexicon
uv run autopulse consumer themes --model Alto        # themes, quotes and (with --month) signals
```

`data/public/theme_lexicon.csv` holds the terms, in English, Roman Urdu and Urdu
script, and is the only place a person decides anything. It carries the local
meanings that matter: **"average" is mileage**, **"own" is the premium paid for
early delivery**, **"qist" is an instalment**.

What the code decides, so nobody has to:

| Rule | Why |
|---|---|
| spam dropped (numbers, links, "help me") | it is not consumer voice |
| chatter about the video or host dropped | "please do an expert review" is not a barrier |
| stance set only on clear wording, else `unclear` | "expensive" is a barrier, "worth the price" is not, "price?" is neither |
| a comment naming another model is excluded | under a Fronx review, "Corolla is better" is a Corolla opinion |
| quotes come from single-model videos | a comparison video's comments are ambiguous |
| themes under 10 comments are quoted, never turned into a percentage | with 7 comments, "43% mention price" is three people |

On a hand check of 28 coded comments, the theme was right in about 26. Stance is
deliberately conservative: most comments come back `unclear`, and reading those
is the model's job, not a rule's.

## What is code and what is judgement

- **Code:** which video is about which model, spam and chatter, theme matching,
  counts, shares, stance where the wording is unambiguous, and signals.
- **Judgement (the model, at the end):** reading the `unclear` stances, deciding
  which barriers matter for this client this month, and writing it up. A keyword
  count only ranks what to read.

## Barrier taxonomy

| theme | what counts |
|---|---|
| price | sticker price, price rises, "out of reach" |
| financing | bank loans, markup, lease, down payment |
| delivery | booking wait, delivery delays |
| on_money | premium paid over list for early delivery |
| resale | resale value, demand in the used market |
| fuel_economy | mileage, running cost, hybrid vs petrol |
| safety_quality | airbags, build quality, reliability |
| features | equipment, variant spec, CKD vs CBU spec |
| after_sales | service, parts, warranty, dealer network |
| dealer_experience | showroom treatment, follow-up |
| tax_registration | registration, token tax, withholding tax, provincial rebates |
| brand_trust | brand longevity, Chinese vs Japanese, "will they stay" |

Add a theme only when 10+ comments fit nothing, and log it in the Changelog so
month-on-month counts stay comparable.

## Method

1. **Check what's held** with `consumer status`: videos, matched models,
   comments per model. State the corpus size for any model you report on.
2. **Read before counting.** Pull the comments for a model, read a sample, then
   code them. Roman Urdu is common: keep it verbatim, translate in brackets.
3. **Watch for off-topic praise.** Much of any review's comments are about the
   reviewer ("amazing review"), not the car. Those are not consumer signal.
4. **Split launch from ownership** using the model's first PAMA sale month:
   comments in months 1-3 are anticipation, after month 12 they are ownership.
   The same model's complaints change as the cars age, which is what a brand
   tracker charges a fortune to measure.
5. **Write signals**, then the read-up: barriers that matter, with counts,
   shares and quotes.

## Signals this engine writes

`engine=consumer`, `geography=Pakistan` unless the source is local.

| metric | value | comparisons |
|---|---|---|
| `theme_share_pct:<theme>` | % of a model's on-topic comments coded to that theme as a barrier | level, mom |
| `onthread_comments` | on-topic comments behind those shares | level |

Format: `src/autopulse/signals.py`. Themes with under ~10 coded comments are
quoted, never turned into a percentage.

## Limits

- Commenters are not buyers, and a video's audience is not the market.
- No demographics and no location: never claim "Karachi buyers say".
- A video's framing colours its comments. Check a theme across several channels
  before calling it category-wide.

## Sourcing

Every quote and every number carries its video title, channel, date and URL
(`https://www.youtube.com/watch?v=<video_id>`), plus the comment count behind
it. "YouTube says" is not a source.

## Changelog

- 2026-09-18 (later): coding built. Lexicon of 154 terms across the 12 themes in
  three languages; spam, chatter, stance, stage and other-model attribution as
  rules; theme table, sourced quotes and signals. On 112,020 comments: 24%
  coded, 56% no theme, 11% chatter, 0.7% spam. Non-PAMA nameplates (Kia,
  Changan, MG, BYD) added to the aliases so comparison videos are recognised.
- 2026-09-18: comment database built. Five channels, uploads from 2024-09-01,
  ~7,700 videos in window, ~3,500 matched to a model; comments fetched busiest
  first. Coding and theme signals still to build.
- 2026-09-17: created. Barrier taxonomy v1 (12 themes).
