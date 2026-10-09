---
name: health-check
description: Check whether the bdleads app is healthy and explain problems in plain language - scheduled collection runs (did today's run work?), the collect.log, each source's freshness and errors, the provenance audit, config files, the source registry, the dashboard and the tests - then diagnose the cause and propose (not silently apply) the fix. Use whenever the user asks "is the app working", "did the morning run go OK", "why are there no new leads", "leads look stale/old", "the dashboard shows an error", "something broke", "check everything before the BD meeting", after a code or config change, or when returning to the project after a break - even if they only say "status?".
---

# bdleads health check

The app runs unattended (Task Scheduler at 08:00), so failures are silent until someone
notices stale leads. On 8 Oct 2026 a damaged config file made the morning run fail and
nobody saw it for hours. This skill exists to catch that fast and to say clearly what's
wrong, what it affects, and how to fix it.

**Read-only by default.** Gather and diagnose; propose fixes and apply them only when the
user agrees. Exception: re-running a failed collection is fine to offer as a one-liner.

## 1. Run the report

From the project root:

```bash
uv run python .claude/skills/health-check/scripts/health_check.py --tests
```

(Drop `--tests` for a faster check.) Each line is OK / WARN / FAIL:

| Check | What it looks at |
|---|---|
| config | `sources.toml` / `rules.toml` load and have every section the collectors need |
| registry | `source_registry.csv` validates |
| audit | every lead has evidence with a real link (the no-made-up-data rule) |
| schedule | the two Task Scheduler jobs: last run, result code, next run |
| last_run | the newest block of `logs/collect.log`: exit code and problems |
| sources | per collector: items stored, hours since last fetch, last run's error |
| dashboard | whether http://localhost:8501 answers |
| tests | the full test suite |

## 2. Diagnose

Read the evidence before concluding. Open the log around the failure
(`logs/collect.log`), and for a source problem look at its recent runs
(`uv run bdleads audit` prints them).

| Symptom | Likely cause | Fix to propose |
|---|---|---|
| `KeyError: '<section>'`, config FAIL | Config file damaged or truncated | `git diff src/bdleads/config/` to see what changed; restore with `git checkout -- <file>` if the change wasn't intended; run tests; re-run collection |
| Task "Last Result" non-zero | The run crashed; see last_run | Fix the cause, then `schtasks /Run /TN "bdleads quick"` |
| Task "has not run yet" | Normal for the Sunday task before its first Sunday | Nothing |
| Source last fetched > 2 days ago, no errors | PC was off / logged out at 08:00 and hasn't caught up, or the task is disabled | Check the schedule line; run `uv run bdleads collect --quick` |
| Source read 0 items, or "contained no feed entries" | Site layout changed, or the site is down | Probe the page (add-source skill's `probe_source.py`); if the layout changed, update the parser with a fresh fixture. Don't loosen tests to pass |
| HTTP 403/400 for a source that used to work | Site now blocks automated clients | Don't work around it; record in `source_registry.csv` as Blocked, with the date |
| Timeouts / connection errors | Network or site outage | Retry later; WARN, not FAIL, unless it persists for days |
| `IMAP not configured` | Shared inbox not set up yet | Expected; nothing to fix until the inbox exists |
| audit FAIL (leads without evidence) | Something wrote leads bypassing the model, or a migration went wrong | Serious: stop and investigate with the user before anything else; the backups are in `data/` |
| dashboard not answering | Not started, or crashed after a code change | `uv run bdleads dashboard`; after code changes it must be restarted (Streamlit doesn't reload imported modules) |
| tests FAIL | Code or config changed | Read the failing test; fix the code, not the test |

If a check fails for a reason not in this table, say what you see and what you'd
check next. Don't guess a cause.

## 3. Report

Lead with the answer, then the evidence. Plain language: the reader may be a BD manager,
not a developer.

```
Status: OK | needs attention | broken
<One sentence: is collection running, and are today's leads in?>

Problems (most serious first):
- <what's wrong> — <evidence: log line / timestamp / count> — <what it affects>
  Fix: <proposed action>  (needs your OK / I can do this now)

All clear: <checks that passed, one line>
Last successful collection: <time>; next scheduled: <time>
```

When everything is OK, keep it to three or four lines. Nobody needs a table of green
ticks.

## After fixing something

Re-run the report to confirm, and if a collection was missed, re-run it
(`schtasks /Run /TN "bdleads quick"` uses the same path as the schedule). If the cause
was a change to code or config, say what would prevent a repeat (a test, a check), and
note the incident in `SOFAR.md`.
