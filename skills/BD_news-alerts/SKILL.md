---
name: news-alerts
description: Manage the Google Alerts and news RSS feeds that feed bdleads - connect new Google Alert RSS links the user pasted into docs/Google_Alerts_List.xlsx (verify each feed, add it to sources.toml, run it), run the weekly review of which alerts produce leads and suggest which to keep, reword or drop, help word new alert queries, and explain why the user (not Claude) has to create the alerts in Google. Use whenever the user mentions Google Alerts, alert links, RSS feeds, "I've added more links to the sheet", "connect these alerts", "which alerts are working", "are the alerts giving anything", "drop the useless alerts", "add an alert for X", LinkedIn posts via Google, or news feeds in the app - even if they only say "the sheet" or "the feeds".
---

# News alerts (Google Alerts and RSS feeds)

Google Alerts are how bdleads picks up agency searches, RFPs, EOIs, launches and public
LinkedIn posts that no single site publishes. The user creates each alert in their own
Google account with "Deliver to: RSS feed", pastes the feed link into
`docs/Google_Alerts_List.xlsx`, and the app reads the feeds on every run through the news
collector (`src/bdleads/sources/rss.py`, feeds with `google_alert = true` in
`src/bdleads/config/sources.toml` `[rss]`).

## The boundary (read this first)

google.com/robots.txt disallows `/alerts/`. On 2026-10-08 the user approved one narrow
exception: the app may read **the alert feeds they created**, once per run, like a
feed reader (recorded in AGENTS.md and `source_registry.csv`). Everything else is still
off-limits, because the exception is the user's decision about their own feeds, not a
general permission:

- Fetch only `https://www.google.com/alerts/feeds/...` links that came from the user.
- Never fetch Google search results, `google.com/alerts` creation pages, or "preview" a
  query by searching Google. To see what a query would return, the user can type it on
  google.com/alerts, which shows a preview.
- Never create, edit or delete alerts. That needs the user's Google sign-in, and
  robots.txt disallows it. If asked, explain this in one or two sentences and hand the
  user the exact query and settings so it takes them a minute.

## A. Connect new alert links

1. Compare the sheet with what's connected, and verify the new feeds:
   ```bash
   uv run python .claude/skills/news-alerts/scripts/alerts_sync.py --check
   ```
   Each row comes back as `connected`, `NEW` (with a ready TOML line), `NOT A LINK`
   (something else was pasted, often the query text) or no link. `--check` fetches each NEW
   feed once and confirms its title matches the row's query, which catches a link pasted
   into the wrong row.
2. For each NEW feed that checked OK, insert its TOML line **with the Edit tool** at the
   end of the Google Alerts block in `[rss] feeds` in `sources.toml`. Shorten the name if
   it's long (it shows in the dashboard's Source column) and keep names unique. Don't
   rewrite the file with a script: a scripted rewrite once truncated `sources.toml` and
   broke the daily run.
3. Don't connect a link that failed the check or whose title doesn't match. Tell the user
   which row and what you saw.
4. Verify:
   ```bash
   uv run pytest -q
   uv run bdleads collect rss      # news + all alerts; reads only these feeds
   uv run bdleads audit
   ```
   An empty new alert is normal: Google only lists results found after the alert was
   created. A `problem:` line for an alert is not normal; report it.
5. Update the record: in `source_registry.csv`, the `google_alerts` row's name ("Google
   Alerts (RSS, N alerts)") and evidence; one line in `SOFAR.md` §14. Commit if the
   project commits its work. The dashboard doesn't need a restart for a config change.

You don't edit the user's Excel file (they may have it open). Tell them which rows are
now connected so they can mark "Created? = Y" themselves.

## B. Weekly review: which alerts are working

```bash
uv run python .claude/skills/news-alerts/scripts/alerts_review.py --samples 3
```

Per alert: days connected, results stored, leads made, samples of both, and a suggested
action. Also run `alerts_sync.py` (without `--check`, so nothing is fetched): if the sheet
has links that aren't connected, mention them and offer to connect them (section A), but
don't connect them unasked. A review is a report. Don't run a fresh collection for it
either; the daily run already read the feeds. Read the samples before agreeing with the
suggestion:

The script re-applies the current rules to every stored result, so its lead counts are
what the rules make today. It also shows **team dropped** (leads the BD team marked
`dropped`, which is the real noise signal), **stale** leads (in the database from an older rule,
listed not deleted), and whether any alert lead links to google.com instead of the real
page (a collector bug if so).

| Suggested | Means | What to do |
|---|---|---|
| too early | connected < 7 days | No verdict. Say when a fair review is possible |
| noisy | 4+ leads, half or more marked dropped by the team | Read the dropped samples. If they share a cause, fix it there (see "How noise gets in" below); otherwise suggest rewording the alert |
| keep | at least one lead | Keep. Mention the best lead with its link |
| tune | results, but no leads | If the samples are off-topic, reword the alert. If they are relevant but the rules missed them, that's a rule gap: use **tune-rules** |
| reword/drop | no results after 7+ days | Suggest a broader wording, or dropping it |

Rewording tips for the user (they edit the alert in Google): fewer quoted phrases, `OR`
in capitals between alternatives, drop `site:linkedin.com` if LinkedIn alone gives
nothing, add a minus word to cut noise (`-jobs`, `-cricket`).

To drop an alert from the app, remove its line from `sources.toml` with the Edit tool,
then run the tests. Its stored results and leads stay; nothing is deleted. Tell the user
to delete it in Google too, or the feed keeps existing unread. Don't drop anything
without the user's OK.

### How noise gets in (and what's already handled)

Learned on 2026-10-09, when the first read of all 33 alerts gave 33 leads and about
half were noise ("Turkey will not fight Yemen war" as a launch):

- **Snippet boilerplate.** Google's snippet is cut from the page and often contains its
  menus and other headlines ("... Launch KissanPay ... Telecom News ..."). So for alert
  entries, `rss.py` takes signals and services from the **headline only** and uses the
  snippet just for the sector. Don't undo this to "catch more": the evidence would
  then be a word in a menu. Tests: `tests/test_google_alerts.py`, on a real saved feed.
- **Broad signals on broad alerts.** Sector-watch alerts (rows 24–30) return general
  news, so a launch, merger or other broad signal also needs a commercial sector.
  Agency intent (`agency_search`, `agency_review`) or a domain/service match is enough
  on its own.
- **Off-topic but correctly labelled** (a BMW launch abroad, an IsDB plan for
  Indonesia): the rules are working; the alert's query is too broad. Suggest a
  narrower query (add `Pakistan` in quotes, a minus word) rather than a rule hack.
- **A missing keyword** surfaced by the noise fix (e.g. "changes name to" wasn't a
  rebrand until 2026-10-09): use **tune-rules** with a real headline as the test.

- **Not about Pakistan, public-body notices, AI-summary pages, duplicates** (added
  2026-10-09): `src/bdleads/screen.py` with the patterns in `rules.toml` `[screen]`. A lead
  that fails is not shown to BD; it's listed with its rule and reason in `bdleads
  screened` and the dashboard's Sources → "news and alerts screened out". The Pakistan check
  reads the headline without the outlet name plus the snippet's **first fragment only**
  (Google joins fragments with "..." and menus often say "Pakistan"). A story already shown
  from another outlet is merged into that lead as a second source.
- **Known companies** come from `config/companies.csv` (MediaMonitors TV advertisers 2025
  + PSX watchlist, ~1,000 rows, each sourced). Check a headline with
  `uv run bdleads companies find "<headline>"`. Only `match_names` count.
- **Known gap:** a real Pakistani launch whose headline and opening fragment name neither
  Pakistan nor a `match_names` entry (e.g. "Suzuki e SKY EV Confirmed for November
  Launch": the sheet only has "Suzuki Every") is screened out. The fix is a reviewed row
  or name in `companies.csv` (with its source), not loosening the Pakistan check.

The review's job is to catch mistakes in both directions: real leads in the screened
list (screen too strict: extend `[screen].companies` or adjust a pattern, with a real
headline as a test in `tests/test_screen.py`), and noise still shown (screen too loose).
Preview any change with tune-rules' `rules_diff.py`, which shows a SCREENED section.

When noise appears: check whether the matched keyword (`uv run bdleads show <id>`,
`matched`) is in the headline or only in the snippet, and whether the lead has a
sector. That tells you which of the above it is. Fix rules for the whole class, never
single leads. After a rule change, `bdleads reclassify` keeps the old leads and lists
them as stale. Offer to mark them `dropped` with a note, and do it only on the user's OK.

## C. Suggest new alert queries

Base suggestions on gaps you can show: a domain or sector with few leads
(`uv run bdleads list --json`), or a signal the BD team asked for. Give each as a row the
user can paste into the sheet: query, signal, domain, and the settings (At most once a
day, Automatic, English, Any region, All results, Deliver to RSS feed). Remember the
evidence for a lead will be whatever page the alert finds, so prefer queries that land on
primary pages (company announcements, newspapers, tender notices) over aggregators.

## Things to keep true

- Every alert lead must cite the real page, not a `google.com/url?...` redirect. rss.py
  unwraps the redirect. If you see a lead whose source URL is a Google link, that's a bug
  to fix in the collector, with a test.
- Labels on alert leads come from the keyword rules like everything else. Don't relabel
  or rescore individual leads.
- A feed link works like a password for that alert. Keep the links out of chat
  summaries, emails and documents shared outside the team.

## Report back

```
Alerts: <n> connected (<new> added today: rows ...)
Not connected: row <r> — <reason: not a link / failed check / title mismatch>
Review: keep <n> · noisy <n> · tune <n> · reword/drop <n> · too early <n>  (stale leads: <n>; Google links: none)
  e.g. keep "<alert>": <leads> leads, best: "<title>" (<real url>)
  e.g. reword "<alert>": 0 results in <d> days — try: <new query>
Run: <items read>, <new leads>; tests <n> passing; audit 0 failures
Your side: <rows to mark in the sheet / alerts to edit or delete in Google>
```
