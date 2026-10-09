---
name: lead-search
description: Find new-business leads for the group's agencies (Ad/Creative, Media, Digital, PR, Analytics) in the bdleads database and from its live sources - government tenders (PPRA), World Bank-financed project tenders, stock-exchange filings of FMCG, banking, telecom and auto companies (PSX), news signals and LinkedIn alert emails - and return them with the source link for every lead. Use whenever the user asks for leads, tenders, RFPs, EOIs, pitches, prospects or opportunities, asks "who is hiring an agency", "any media buying tenders", "which banks changed CEO", "what's new for the ad agency", "find opportunities in FMCG", or wants to refresh or search the lead list - even if they don't say "lead" or name the tool.
---

# Lead search

Find leads in the **bdleads** app (this repository) and present them with their sources.
The app's rule applies to you too: **every lead you mention carries its source link, and
you never add a fact the source doesn't contain.** BD people forward these lists to
directors and clients, so one invented detail undermines the whole list.

## 1. Decide: search what's stored, or fetch fresh?

Use `uv run bdleads collect --quick` for a routine refresh (about 2 minutes). Use a full
`uv run bdleads collect` (about 5 minutes) when the user asks about deadline changes or
corrigenda, or when the last full run is more than a week old.

Check when sources last ran:

```bash
uv run bdleads audit
```

The run lines show each source's last fetch time. Collect again if the relevant
source is more than a day old or the user asks for "latest" or "today":

```bash
uv run bdleads collect ppra        # ~3-4 min: all federal tenders, keeps comms-related ones
uv run bdleads collect worldbank   # ~10 s: World Bank-financed project notices in Pakistan
uv run bdleads collect psx         # ~1-2 min: watchlist company filings
uv run bdleads collect rss         # seconds: news feeds
uv run bdleads collect email       # LinkedIn alerts, only if IMAP env vars are set
```

Read the `problem:` lines in the output and pass them on (e.g. "IMAP isn't configured,
so LinkedIn alerts aren't included"). Don't silently skip a source the user asked about.

## 2. Translate the request into filters

| User says | Filter |
|---|---|
| ad / creative / TVC / branding | `--agency ad` |
| media / media buying / airtime / placement | `--agency media` |
| social / digital / website | `--agency digital` |
| PR / events / launch event | `--agency pr` |
| research / survey / analytics | `--agency analytics` |
| a specific service (production, performance marketing, lead generation, influencer, events/EMC, BTL, business plans…) | `--service <domain>.<service>`, ids in `rules.toml` `[service_labels]`, e.g. `digital.performance_marketing`, `ad.production`, `pr.events_exhibitions`, `analytics.business_plans_feasibility` |
| for a group company (Synergy Dentsu, Synchronize Media, Synite Digital, Syntax, Synergy Marketing) | the services mapped to it in `rules.toml` `[service_bu]` |
| tenders / RFP / EOI | `--kind tender` |
| donor / World Bank / development | `--source "World Bank"` |
| government tenders only | `--source PPRA` |
| CEO / CMO / leadership changes, listed companies | `--kind corporate_announcement --signal leadership_change` |
| FMCG / food / consumer goods | `--sector fmcg` |
| banks / insurance / fintech / finance | `--sector banking_finance` |
| telecom, auto, pharma | `--sector telecom` / `auto` / `pharma_health` |
| a company or topic name | `--text "<name>"` |
| hot / priority | `--min-score 50` |

Use `--json` when you need the evidence to write your answer:

```bash
uv run bdleads list --agency media --kind tender --json --limit 30
```

Past-deadline tenders are hidden by default. Add `--include-expired` only if the user
asks about closed tenders, e.g. to see who has been running agency roster EOIs.

If a filter returns nothing, say so, then try one broader query (drop the sector, or
switch `--text` to a shorter stem such as `advertis`). Don't pad the answer with
loosely related leads presented as matches.

## 3. Present the results

Use this format. Keep each lead to two or three lines:

```
**<Title as stored>** — <organisation if stated> · score <n>
For: <domain> (<service>) · best fit <BU> · <kind> · closes <deadline> / published <date>
Source: [<source_name>](<source_url>) (fetched <date>)
```

Rules for the write-up:
- Copy titles, organisations, dates and deadlines from the stored fields only.
  If the organisation is empty, leave it out. Never fill it from the headline or from
  your own knowledge.
- Show the deadline for tenders and the publish date for everything else.
- If you add context from your own knowledge (e.g. "SIFC is the Special Investment
  Facilitation Council"), label it as context and keep it separate from the sourced lines.
- End with one line on coverage: which sources were searched and when they were last
  fetched, plus any source that failed or isn't configured.

## 4. Things the user can add themselves

If the user mentions a lead from somewhere the app doesn't collect (a LinkedIn post, a
newspaper EOI, a WhatsApp forward), offer to add it. It needs a URL and the text the
source actually says:

```bash
uv run bdleads add --title "..." --url "https://..." --excerpt "<verbatim text>" --added-by "<name>"
```

Don't create the excerpt yourself from memory. Ask the user to paste the source text if
they haven't.

## Related skills

- To dig into one lead (read the tender PDF, write a brief): use **lead-analysis**.
- To prioritise, group by domain, update statuses or build a digest: use **lead-triage**.
