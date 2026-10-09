"""Read-only health report for the bdleads app.

Usage (from the project root):
    uv run python .claude/skills/health-check/scripts/health_check.py [--tests] [--json]

Checks, each reported as OK / WARN / FAIL with the evidence:
  config      sources.toml and rules.toml load and have every required section
  registry    source_registry.csv validates
  audit       every lead has evidence with an http(s) URL
  schedule    Windows scheduled tasks "bdleads quick"/"bdleads full": last run, result, next run
  last_run    the newest block in logs/collect.log: exit code and problems
  sources     per collector: last fetch time, and errors in its most recent run
  dashboard   whether http://localhost:8501 answers
  tests       (only with --tests) uv run pytest -q
Nothing is fetched from the internet and nothing is changed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path.cwd()
RESULTS: list[dict] = []


def add(check: str, status: str, detail: str) -> None:
    RESULTS.append({"check": check, "status": status, "detail": detail})


def check_config() -> None:
    try:
        from bdleads import config
        s, r = config.sources(), config.rules()
    except Exception as e:  # noqa: BLE001
        add("config", "FAIL", f"config files don't load: {type(e).__name__}: {e}")
        return
    need = ["http", "ppra", "psx", "rss", "worldbank", "imap"]
    missing = [x for x in need if x not in s]
    if missing:
        add("config", "FAIL", f"sources.toml is missing section(s) {missing}; "
            "compare with git (`git diff src/bdleads/config/sources.toml`)")
        return
    rmissing = [x for x in ("agencies", "sectors", "signals", "scoring") if x not in r]
    if rmissing:
        add("config", "FAIL", f"rules.toml is missing section(s) {rmissing}")
        return
    n = sum(len(v) for v in s["psx"]["watchlist"].values())
    add("config", "OK", f"sources.toml and rules.toml complete; {n} PSX symbols, {len(s['rss']['feeds'])} feeds")


def check_registry() -> None:
    try:
        from bdleads import pipeline, registry
        problems = registry.validate(registry.load(), pipeline.SOURCES)
    except Exception as e:  # noqa: BLE001
        add("registry", "FAIL", f"{type(e).__name__}: {e}")
        return
    add("registry", "OK" if not problems else "WARN",
        "source_registry.csv valid" if not problems else "; ".join(problems[:5]))


def check_audit() -> None:
    try:
        from bdleads.store import Store
        st = Store()
        total = st.conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        orphans = len(st.orphan_leads())
        bad = st.conn.execute("SELECT COUNT(*) FROM evidence WHERE source_url NOT LIKE 'http%' "
                              "OR length(trim(excerpt)) < 5").fetchone()[0]
    except Exception as e:  # noqa: BLE001
        add("audit", "FAIL", f"database not readable: {type(e).__name__}: {e}")
        return
    add("audit", "OK" if not (orphans or bad) else "FAIL",
        f"{total} leads; {orphans} without evidence; {bad} evidence rows failing checks")


def check_schedule() -> None:
    if sys.platform != "win32":
        add("schedule", "WARN", "not Windows: scheduled tasks not checked")
        return
    for task in ("bdleads quick", "bdleads full"):
        try:
            out = subprocess.run(["schtasks", "/Query", "/TN", task, "/V", "/FO", "LIST"],
                                 capture_output=True, text=True, timeout=30)
        except Exception as e:  # noqa: BLE001
            add("schedule", "WARN", f"{task}: could not query ({e})")
            continue
        if out.returncode != 0:
            add("schedule", "WARN", f"{task}: not found in Task Scheduler")
            continue
        info = {}
        for line in out.stdout.splitlines():
            k, _, v = line.partition(":")
            if k.strip() in ("Last Run Time", "Last Result", "Next Run Time", "Status", "Scheduled Task State"):
                info[k.strip()] = v.strip()
        last = info.get("Last Result", "?")
        # Windows shows 11/30/1999 (result 267011) for a task that has never run.
        never = info.get("Last Run Time", "").startswith(("11/30/1999", "N/A"))
        status = "OK" if last == "0" or never else "FAIL"
        if info.get("Scheduled Task State", "Enabled") != "Enabled":
            status = "WARN"
        ran = "has not run yet" if never else f"last run {info.get('Last Run Time', '?')}, result {last}"
        add("schedule", status, f"{task}: {ran}, next run {info.get('Next Run Time', '?')}, "
            f"state {info.get('Scheduled Task State', '?')}")


def check_last_run() -> None:
    log = ROOT / "logs" / "collect.log"
    if not log.exists():
        add("last_run", "WARN", "logs/collect.log not found (no scheduled run yet?)")
        return
    text = log.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"(?m)^==== (?=\S.*mode=)", text)
    last = blocks[-1] if len(blocks) > 1 else text
    header = (last.splitlines()[0] if last else "?").replace("====", "").strip()
    m = re.search(r"collect exit code (\d+)", last)
    problems = [l.strip() for l in last.splitlines() if "problem:" in l or "Error" in l or "Traceback" in l]
    if not m:
        add("last_run", "WARN", f"latest log block ({header}) has no 'finished' line: still running or killed")
        return
    code = int(m.group(1))
    expected = [p for p in problems if "IMAP not configured" in p]
    other = [p for p in problems if p not in expected]
    status = "OK" if code == 0 and not other else "FAIL" if code else "WARN"
    detail = f"latest run {header.strip()}: exit code {code}"
    if other:
        detail += "; problems: " + " | ".join(other[:4])
    if expected:
        detail += "; (expected until the shared inbox is set up: IMAP not configured)"
    add("last_run", status, detail)


def check_sources() -> None:
    try:
        from bdleads.store import Store
        st = Store()
        now = datetime.now(timezone.utc)
        for r in st.raw_stats():
            last = datetime.fromisoformat(r["last_fetched"])
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            age_h = (now - last).total_seconds() / 3600
            run = st.conn.execute("SELECT started, fetched, kept, error FROM runs WHERE source LIKE ? "
                                  "ORDER BY id DESC LIMIT 1", (f"{r['source']}%",)).fetchone()
            err = run["error"] if run else None
            status = "OK"
            if age_h > 50:
                status = "WARN"
            if err:
                status = "WARN"
            detail = (f"{r['source']}: {r['items']} items stored, last fetched {age_h:.0f}h ago"
                      + (f"; last run read {run['fetched']} kept {run['kept']}" if run else "")
                      + (f"; error: {err[:160]}" if err else ""))
            add("sources", status, detail)
    except Exception as e:  # noqa: BLE001
        add("sources", "FAIL", f"{type(e).__name__}: {e}")


def check_dashboard() -> None:
    try:
        code = httpx.get("http://localhost:8501", timeout=5).status_code
        add("dashboard", "OK" if code == 200 else "WARN", f"http://localhost:8501 answered {code}")
    except httpx.HTTPError:
        add("dashboard", "WARN", "not running on http://localhost:8501 (start: uv run bdleads dashboard)")


def check_tests() -> None:
    out = subprocess.run(["uv", "run", "pytest", "-q"], capture_output=True, text=True, timeout=600)
    tail = (out.stdout.strip().splitlines() or ["(no output)"])[-1]
    add("tests", "OK" if out.returncode == 0 else "FAIL", tail)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", action="store_true", help="also run the test suite")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    for fn in (check_config, check_registry, check_audit, check_schedule, check_last_run,
               check_sources, check_dashboard):
        fn()
    if args.tests:
        check_tests()
    if args.json:
        print(json.dumps(RESULTS, indent=2))
    else:
        for r in RESULTS:
            print(f"[{r['status']:<4}] {r['check']:<9} {r['detail']}")
        worst = "FAIL" if any(r["status"] == "FAIL" for r in RESULTS) else \
            "WARN" if any(r["status"] == "WARN" for r in RESULTS) else "OK"
        print(f"\nOverall: {worst}")
    return 1 if any(r["status"] == "FAIL" for r in RESULTS) else 0


if __name__ == "__main__":
    sys.exit(main())
