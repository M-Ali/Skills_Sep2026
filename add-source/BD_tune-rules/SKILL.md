---
name: tune-rules
description: Change how bdleads labels and scores leads - add or remove keywords for agencies (ad, media, digital, PR, analytics), sectors and signals, adjust scoring weights or PSX filing rules - by previewing the effect on everything already collected, testing on real items, applying it with reclassify, and reporting exactly which leads were added, dropped or relabelled. Use whenever the user says leads are missing, wrong, noisy or mislabelled ("we're missing documentary tenders", "too many director resignations", "survey equipment showing as research", "this should be media not ad"), wants a new category or sector, wants to weight something higher or lower, asks why something was or wasn't picked up, or is doing Phase 2 categorisation with the BD team - even if they don't mention rules.toml.
---

# Tune the classification and scoring rules

Every label in bdleads comes from a keyword rule, and every score point from a scoring
rule, both stored with the lead so anyone can see why. That traceability is what lets
BD trust the list, so rule changes go through these files, not through judgement calls
on individual leads. The job here is to make a change that does what the user meant,
and show its exact effect before it lands.

## The files

| What | Where |
|---|---|
| Domain/service keywords (domain = ad, media, digital, pr, analytics) | `src/bdleads/config/rules.toml` → `[services.<domain>]` (one list per service) |
| Service display names and best-fit BU | `rules.toml` → `[service_labels]`, `[service_bu]` (every service needs both) |
| Sector and news/company signal keywords, signal names | `rules.toml` → `[sectors]`, `[signals]`, `[signal_labels]` |
| How long company signals stay visible in the dashboard | `rules.toml` → `[display] signal_max_age_days` (30) |
| Scoring weights | `rules.toml` → `[scoring]`, `[scoring.base_by_kind]`, `[scoring.signal_weights]`, `[scoring.sector_weights]` |
| PSX filing rules (which filing titles count, and routine ones to ignore) | `src/bdleads/config/sources.toml` → `[psx.title_signals]`, `[psx.exclude]` |
| Screening of news/alert leads (not about Pakistan, public-body notice, AI-summary page, same-story merge) | `rules.toml` → `[screen]`; code in `src/bdleads/screen.py`; held-back items: `uv run bdleads screened` |
| Known companies and brands (Pakistan check, sector from a company name) | `src/bdleads/config/companies.csv` (Excel); `uv run bdleads companies validate` / `find "<headline>"`; built by `scripts/import_companies.py` |
| How patterns match | `src/bdleads/classify.py`: case-insensitive regex, word boundaries added automatically |

Edit these files with targeted edits (the Edit tool), never by rewriting them with a
script. A scripted rewrite once truncated `sources.toml` and broke the daily run.

## Workflow

### 1. Turn the request into a concrete rule change
Restate it as "add pattern X to group Y" or "change weight Z from a to b". If the user
gave an example lead or tender, find it first (`uv run bdleads list --text "..."
--include-expired`, or `uv run bdleads raw search "..."` for items that aren't leads) and
look at its exact text and `matched` labels (`uv run bdleads show <id>`). The real
text tells you which words to match.

### 2. Get a clean baseline
```bash
uv run bdleads reclassify      # make the database reflect the rules as they are now
```

### 3. Try candidate patterns on the real data before editing
Search the raw store for the words you plan to match, and read what comes back:
```bash
uv run bdleads raw search "documentar" --limit 30
```
This is where false positives show up. "advertisement" appears in almost every PPRA
notice ("as per advertisement"), and "survey" catches dry-docking surveys and survey
equipment. Prefer phrases ("documentary production", "media buying") over single
common words, and add a second, narrower pattern rather than a broad one.

### 4. Edit, then preview the effect
```bash
uv run python .claude/skills/tune-rules/scripts/rules_diff.py            # all sources
uv run python .claude/skills/tune-rules/scripts/rules_diff.py --source ppra --show 30
```
It lists NEW leads, DROPPED leads (with their team status), CHANGED labels or
scores, and SCREENED news items (made by the rules but held back by `[screen]`), each
with the matching keyword or reason and source link. Read every NEW title. If any
aren't communications work, tighten the pattern and preview again. Don't apply a
change whose preview you haven't read.

### 5. Lock it in with a test
Add a case to `tests/test_sources.py` using a **real** title from a fixture or from the
raw store (quote it exactly; never invent an example). Cover both sides when you can:
one real item the rule should catch, one real false positive it must not. Then:
```bash
uv run pytest -q
```

### 6. Apply and report
```bash
uv run bdleads reclassify      # applies to everything collected; team statuses kept
uv run bdleads rescore         # only if you changed scoring weights (also covers manual leads)
uv run bdleads audit
```
Leads that no longer match are never deleted. `reclassify` hides those nobody has
worked on (status `new`) and keeps the others visible, because someone may already be
working them. Show the user the kept-visible ones and ask whether to mark any as
`dropped` (`uv run bdleads status <id> dropped --note "rule change: ..."`). Don't change
statuses on your own.

If the dashboard is running, restart it. If the project commits its work, commit the
rule change together with its test, and say in the message what changed and the effect.

## Report back

```
Change: <group>: added/removed <pattern(s)> | weight <name> a -> b
Why: <user's request, in one line>
Effect on stored data: +<new> new leads, -<dropped> no longer matching, ~<changed> relabelled/rescored
  e.g. + "<real title>" (<source link>)
  e.g. - "<real title>" [status: <status>]
Rejected patterns: "<pattern>" (caught "<real false-positive title>")
Tests: <n> passing (added: <test name>)
Waiting on you: <dropped leads to confirm, if any>
```

## Things not to do

- Don't label or score individual leads by hand. If one lead is wrong, the rule is
  wrong; fix the rule so every similar item is handled the same way.
- Don't loosen a test to make it pass after a rule change. If a test about real data
  fails, the change probably broke something real.
- Don't delete leads or raw items to "clean up" after a change.
