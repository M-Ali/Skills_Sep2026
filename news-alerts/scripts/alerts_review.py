"""How each connected Google Alert is doing: results, leads, noise, samples.

Read-only (database and config). No fetching.

    uv run python .claude/skills/news-alerts/scripts/alerts_review.py
    uv run python .claude/skills/news-alerts/scripts/alerts_review.py --samples 5 --json

Per alert:
  results       entries stored from the feed (raw items)
  leads         results that make a lead under the CURRENT rules and pass the screen
                (rules.toml [screen]); re-applied here, so a rule change shows up at once
  screened      results the rules matched but the screen held back (not about Pakistan,
                public-body notice, AI-summary page); same-story merges are counted as
                leads here (they reach BD as an extra source on another lead)
  team dropped  of those leads, how many the BD team marked "dropped": the noise measure
  stale         leads still in the database from this alert that the current rules no
                longer make (e.g. after the 2026-10-09 headline-only rule); listed, not
                deleted
plus the latest result, last fetch problem, samples, and a suggested action that the
user decides on:
  too early     connected fewer than --min-days days (default 7): no verdict yet
  noisy         at least --noisy-min leads and half or more of them marked dropped by the
                team: read the dropped samples, then reword the alert or tighten the rule
  keep          produced at least one lead the team hasn't mostly dropped
  tune          results arrive but none became a lead: reword the alert if the samples
                are off-topic, or use tune-rules if they're relevant but missed
  reword/drop   no results at all after --min-days days

Also checks that no alert lead cites a google.com link instead of the real page (that
would be a collector bug).
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from datetime import date

from bdleads import config
from bdleads.models import RawItem
from bdleads.screen import screen
from bdleads.sources import rss


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-days", type=int, default=7)
    ap.add_argument("--noisy-min", type=int, default=4, help="leads needed before judging noise")
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    db = os.environ.get("BDLEADS_DB", "data/bdleads.db")
    c = sqlite3.connect(db)
    c.row_factory = sqlite3.Row
    alerts = [f for f in config.sources()["rss"]["feeds"] if f.get("google_alert")]
    last_rss = c.execute(
        "SELECT started, error FROM runs WHERE source IN ('rss', 'rss/quick') ORDER BY started DESC LIMIT 1").fetchone()
    today = date.today()
    status = {r["id"]: r["status"] for r in c.execute("SELECT id, status FROM leads")}

    out, google_links = [], []
    for f in alerts:
        name = f["name"]
        added = f.get("added")
        days = (today - date.fromisoformat(added)).days if added else None
        raw = c.execute(
            "SELECT key, url, data, first_fetched, last_fetched FROM raw_items "
            "WHERE source='rss' AND json_extract(data,'$.feed')=? ORDER BY first_fetched DESC", (name,)).fetchall()
        current, non_leads, screened = [], [], []
        for r in raw:
            item = RawItem(source="rss", key=r["key"], url=r["url"],
                           fetched_at=r["last_fetched"], data=json.loads(r["data"]))
            leads = rss.item_to_leads(item)
            hit = screen(leads[0], item.data) if leads else None
            if hit:
                screened.append({"title": item.data.get("title"), "rule": hit[0], "url": r["url"]})
            elif leads:
                l = leads[0]
                current.append({"id": l.id, "title": l.title, "score": l.score,
                                "status": status.get(l.id, "not saved yet"),
                                "signals": l.classification.signals, "url": l.evidence[0].source_url})
            else:
                non_leads.append({"title": item.data.get("title"), "url": r["url"]})
        current.sort(key=lambda x: -x["score"])
        current_ids = {x["id"] for x in current}
        stale = [dict(r) for r in c.execute(
            "SELECT DISTINCT l.id, l.title, l.status FROM leads l JOIN evidence e ON e.lead_id=l.id "
            "WHERE e.source_name=?", (name,)) if r["id"] not in current_ids]
        for r in c.execute("SELECT DISTINCT e.source_url FROM evidence e WHERE e.source_name=?", (name,)):
            if "google.com" in r["source_url"]:
                google_links.append((name, r["source_url"]))
        dropped = [x for x in current if x["status"] == "dropped"]
        problem = None
        if last_rss and last_rss["error"] and name in last_rss["error"]:
            problem = next((p for p in last_rss["error"].split("; ") if name in p), last_rss["error"])
        if days is None or days < a.min_days:
            action = "too early"
        elif len(current) >= a.noisy_min and len(dropped) * 2 >= len(current):
            action = "noisy"
        elif current:
            action = "keep"
        elif raw:
            action = "tune"
        else:
            action = "reword/drop"
        out.append({
            "alert": name, "added": added, "days_connected": days, "results": len(raw),
            "leads": len(current), "screened": len(screened), "team_dropped": len(dropped), "stale": len(stale),
            "latest_result": raw[0]["first_fetched"][:16] if raw else None, "problem_last_run": problem,
            "suggested": action,
            "lead_samples": [x for x in current if x["status"] != "dropped"][: a.samples],
            "dropped_samples": dropped[: a.samples],
            "non_lead_samples": non_leads[: a.samples],
            "screened_samples": screened[: a.samples],
            "stale_leads": stale,
        })

    if a.json:
        print(json.dumps({"db": db, "last_rss_run": last_rss["started"] if last_rss else None,
                          "google_links_in_evidence": google_links, "alerts": out},
                         indent=2, ensure_ascii=False))
        return
    print(f"Database: {db}; last news/alerts run: {last_rss['started'][:16] if last_rss else 'never'}")
    print(f"{len(out)} connected alerts; verdicts need at least {a.min_days} days connected.")
    tot = {k: sum(o[k] for o in out) for k in ("results", "leads", "screened", "team_dropped", "stale")}
    print(f"Totals: results {tot['results']}, leads {tot['leads']} (team dropped {tot['team_dropped']}), "
          f"screened out {tot['screened']}, stale {tot['stale']}")
    print("Google links in evidence: " + ("none (OK)" if not google_links else f"{len(google_links)} - COLLECTOR BUG"))
    print()
    for o in out:
        print(f"- {o['alert']}  (connected {o['added']}, {o['days_connected']} days)")
        print(f"    results {o['results']}, leads {o['leads']}, screened {o['screened']}, team dropped {o['team_dropped']}, "
              f"stale {o['stale']}, latest {o['latest_result'] or '-'}  -> suggested: {o['suggested'].upper()}")
        if o["problem_last_run"]:
            print(f"    problem in last run: {o['problem_last_run']}")
        for s in o["lead_samples"]:
            print(f"    lead    [{s['score']}] {s['title'][:85]}  {s['url']}")
        for s in o["dropped_samples"]:
            print(f"    dropped [{s['score']}] {s['title'][:85]}  {s['url']}")
        for s in o["screened_samples"]:
            print(f"    screened [{s['rule']}] {str(s['title'])[:80]}  {s['url']}")
        for s in o["non_lead_samples"]:
            print(f"    other   {str(s['title'])[:85]}  {s['url']}")
        for s in o["stale_leads"]:
            print(f"    stale   {s['title'][:85]}  [status: {s['status']}]")


if __name__ == "__main__":
    main()
