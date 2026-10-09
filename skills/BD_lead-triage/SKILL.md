---
name: lead-triage
description: Sort, de-duplicate, prioritise and group bdleads leads by domain and service, update their pipeline status (new, qualified, contacted, pitching, won, lost, dropped), and produce the weekly BD digest per agency with source links. Use whenever the user asks to prioritise or rank leads, "what should we chase first", clean up or merge duplicate leads, group leads by agency, domain or service, mark a lead as contacted, won or lost, review the pipeline, or prepare the Monday/weekly digest or BD meeting list - even if they just say "sort these out" or "who's handling what".
---

# Lead triage

Keep the lead list workable: the right leads at the top, grouped by domain and service, duplicates
grouped, statuses current, and a digest each domain's team can read in two minutes.
Triage changes *status and notes*, never the sourced fields, so the evidence
trail stays intact.

## 1. Get the current picture

```bash
uv run bdleads list --json --limit 300
```

Count by status, domain and service with a short `uv run python` snippet. Don't count by eye.

## 2. Sort

The app's score is the default order, and every point is explained in `score_reasons`.
Adjust the order only for reasons you can state from the data, and say what you did:

1. **Deadline first for tenders.** A tender closing in under 7 days moves to the top
   with a "decide today" flag, whatever its score. A tender already past its deadline
   is never "priority".
2. **Then score.**
3. **Ties:** a lead in a priority sector (fmcg, banking_finance) comes before one in
   any other sector.

If the user wants a different weighting for good, change the weights in
`src/bdleads/config/rules.toml` and run `uv run bdleads rescore` rather than re-sorting by
hand each week. Show them the diff.

## 3. Group duplicates (don't delete)

The same event often appears more than once. NBP, for example, filed both an
"Appointment of President/CEO" and an "NBP | ... Appointment of President". Two leads
are duplicates only if the **stored text** shows the same organisation **and** the same
event within a few days. Same organisation alone is not enough.

For each duplicate group, keep the highest-scoring lead as the primary and mark the
others:

```bash
uv run bdleads status <dup_id> dropped --by "<user>" --note "duplicate of <primary_id>"
```

Ask before dropping more than a handful at once.

## 4. Group by domain and service

BD Leads is a central system: leads are not assigned to named owners. Each lead
carries its **domain** (`agencies`: ad, media, digital, pr, analytics) and its
**services** (e.g. `digital.performance_marketing`, `pr.events_exhibitions`,
`ad.production`). Each label records the keyword that produced it. Group and
present leads by domain, then service, using the labels in `rules.toml`
`[service_labels]`:

```bash
uv run bdleads list --agency pr --json            # one domain
uv run bdleads list --service ad.production       # one service
```

Company signals (PSX filings, news) usually have **no** domain or service, because a
CEO change isn't a request for a particular service. List them in their own
"company signals" group and say so; don't assign them a domain by judgement.

To record that a lead has been looked at, change its status with a note:

```bash
uv run bdleads status <id> qualified --by "<user>" --note "<why>"
```

## 5. Status hygiene

- `new` → `qualified`: someone has looked at it and it is relevant.
- `qualified` → `contacted` → `pitching` → `won` / `lost`.
- `dropped`: not relevant, a duplicate, or the deadline passed with no action.
  Always add a note saying which.
- Tenders past their deadline that are still `new` or `qualified`: list them and
  propose `dropped` with the note "deadline passed". Apply only after the user agrees.

## 6. Weekly digest

```bash
uv run bdleads digest --agency media --limit 15 --out exports/digest_media_<YYYY-MM-DD>.md
uv run bdleads digest --agency ad    --limit 15 --out exports/digest_ad_<YYYY-MM-DD>.md
uv run bdleads digest --limit 20     --out exports/digest_all_<YYYY-MM-DD>.md
uv run bdleads export exports/bd_leads_<YYYY-MM-DD>.xlsx
```

The generated digest already cites a source for each lead. If you add a "This week"
summary on top, use only counts and facts from the listed leads. Then give the user the
file paths.

## Report back

End with a short changelog: how many leads were reviewed, re-prioritised, grouped by
domain and service, grouped as duplicates and dropped, plus anything waiting on the user
(approval to drop).

## Related skills

- **lead-search** to find leads, **lead-analysis** to read a tender or filing in depth.
