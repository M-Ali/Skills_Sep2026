---
name: add-source
description: Check a candidate website, portal, API or feed and, if it is allowed and worth it, add it to the bdleads app as a new collector - from finding the official URL, robots.txt/terms and access checks, a live probe and a relevance test, to fixture, collector code, tests, a live run and the source-registry update. Use whenever the user wants to add, onboard, plug in, scrape, monitor or "start collecting from" a new source (a procurement portal, tender page, donor or development-bank site, ministry or authority website, contract-awards list, RSS feed, aggregator), asks "can we get data from X", "is X worth adding", "check AJK/GB/ADB/IsDB/NADRA", or picks the next item from the source registry or SOFAR.md - even if they only name the organisation.
---

# Add a source to bdleads

Sources are where the app's credibility starts. A collector that scrapes something it
shouldn't, invents fields, or silently returns nothing does more harm than having no
collector. So this is a gated workflow: each gate can end with **"don't build it"**, and
that is a good outcome as long as the reason is recorded.

Work in the project root (`D:\Personal\BusDevp_Oct2026` or wherever the repo is). Read
`AGENTS.md` first if you haven't this session; its rules apply throughout.

## Gate 1: Is this the official source?

1. Look the candidate up in `src/bdleads/config/source_registry.csv`
   (`uv run bdleads sources show`). If it is already Blocked / Not worth it, read the
   recorded reason before spending time on it. Re-check only if something has changed.
2. Find the **official URL** from an official page, e.g. the federal PPRA home page
   links to every provincial PPRA. Never guess a domain. Note where the URL came from.
3. If the user means an aggregator (TenderPK and the like), treat it as discovery
   only: leads must cite the original publisher, so the collector belongs at the source.

## Gate 2: Are we allowed to read it automatically?

Run the probe (it uses the app's identifying User-Agent and saves the body for you):

```bash
uv run python .claude/skills/add-source/scripts/probe_source.py <url> --out <scratchpad>/probe_<name>
```

Stop and record the source instead of building if any of these hold:

| Finding | Registry status | Why we stop |
|---|---|---|
| robots.txt disallows the path for `*` | Blocked | It's the owner saying no, even if pages load |
| Terms forbid automated access (LinkedIn) | Blocked | Legal and account risk |
| Login required to see listings | Blocked | Only public data is collected |
| 403/400 to a polite client, CAPTCHA, signed or tokenised API requests | Blocked | These are access controls; working around them is off-limits |
| Timeouts / DNS failure | Unavailable | Retry later; note the date |
| TLS certificate errors (self-signed etc.) | Decision needed | Disabling verification is the user's call, not yours |

A script-built (JavaScript) site is not automatically blocked: its data often comes from
a public, unsigned JSON endpoint you can find in the page's network calls or bundle. If
that endpoint needs a signature, token or session, it's an access control: stop.

## Gate 3: Is there anything relevant in it?

Before writing a collector, measure. Parse a real sample (a list page, an API page) and
run the app's own rules over the item texts:

```bash
uv run python .claude/skills/add-source/scripts/relevance_check.py <texts.json>
```

`texts.json` is a JSON list of strings (one per item: title + short description, as
published). The script reports how many items match a domain/service rule and which keyword
matched. Use real items only; don't type example titles.

Interpret honestly:
- A handful of matches in a few weeks of notices: worth building.
- 0 matches across a realistic window (hundreds of items or several months): record as
  **Not worth it** with the numbers ("0 of 243 notices mention Pakistan"). Good outcome.
- Generic titles ("Notice Inviting Tenders") with details only in PDFs: say so; the
  rules can't see inside PDFs, so expected yield is low. Ask the user before building.

## Gate 4: Build it

Follow `references/collector_pattern.md` (skeleton + checklist). The essentials:

1. **Fixture:** save one real page/response to `tests/fixtures/` unmodified, and add a row
   to `tests/fixtures/README.md` with its URL and fetch date.
2. **Config:** add a section to `src/bdleads/config/sources.toml` **with the Edit tool**
   (a targeted insert). Don't rewrite or truncate the file with a script; that once
   deleted the whole config.
3. **Collector** `src/bdleads/sources/<name>.py`:
   - `collect(...) -> CollectResult` returns a `RawItem` for **every** item read,
     relevant or not, with `data` = the fields exactly as parsed. Polite: use
     `PoliteClient`, follow pagination, stop at sensible limits.
   - `item_to_leads(item) -> list[Lead]` applies `classify(...)` (tenders/awards:
     `signal_groups={}`), builds `Evidence` with the item's real URL and a verbatim
     excerpt, and leaves any field the source doesn't state as `None`.
4. **Register** in `pipeline.SOURCES` and `pipeline._MODULES` (and CLI options if needed).
5. **Tests** in `tests/test_<name>.py` against the fixture: item count, every item kept
   raw, relevant ones become leads with an http(s) evidence URL, irrelevant ones don't,
   unstated fields stay `None`.

## Gate 5: Prove it on the live site

```bash
uv run pytest -q                          # everything, not just the new tests
uv run bdleads collect <name>             # live
uv run bdleads raw stats                  # items stored
uv run bdleads list --source "<source name>" --include-expired
uv run bdleads audit                      # must stay at 0 failures
```

Read the leads you created. Are the titles real communications work? If a keyword
matched boilerplate (like "as per advertisement"), fix the rule via the tune-rules
workflow rather than special-casing the collector.

## Gate 6: Record and hand over

1. Registry row → `Live` with evidence (counts, what you saw) and today's date,
   `app_source` = the collector name; `uv run bdleads sources validate`.
2. Docs: README sources table, AGENTS.md layout list, SOFAR.md (status + §4 sources).
3. If the dashboard is running, restart it: Streamlit doesn't reload changed modules.
4. Commit (if the user has asked for commits in this project) with a message stating
   what was checked and the evidence.

For a source you stopped at a gate, steps 1, 2 and 4 still apply: the registry row with
the reason is the deliverable.

## Report back

Keep it short and factual:

```
Source: <name> (<official URL>, found via <page>)
Allowed: yes/no — <robots/terms/access finding>
Relevance: <n> of <N> items matched (<window>), e.g. "<real matching title>"
Decision: built / not built (<status>)
Result: <items stored>, <leads>, tests <n> passing, audit 0 failures
Registry: <status> — <evidence>
Next: <follow-up, if any>
```
