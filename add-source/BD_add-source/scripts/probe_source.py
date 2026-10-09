"""Probe a candidate source politely and report what's there.

Usage:
    uv run python .claude/skills/add-source/scripts/probe_source.py <url> [--out DIR]

Reports: HTTP status and final URL (or the connection/TLS error), content type and size,
robots.txt rules that apply to all bots, page title, tables (with first rows), likely
listing/notice links, pagination hints, JSON top-level keys, and whether the page looks
script-built. Saves the body (and robots.txt) to --out for closer reading.
Uses the bdleads User-Agent. Makes two requests (page + robots.txt); nothing else.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from bdleads import config

KEYWORDS = re.compile(r"tender|bid|procure|advert|notice|opportunit|rfp|eoi|contract|award", re.I)


def robots_rules(text: str) -> list[str]:
    """Lines from the 'User-agent: *' group(s)."""
    out, applies = [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip().lower(), val.strip()
        if key == "user-agent":
            applies = val == "*"
        elif applies and key in ("allow", "disallow", "crawl-delay"):
            out.append(f"{key}: {val}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default="probe_out")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ua = config.sources()["http"]["user_agent"]
    client = httpx.Client(headers={"User-Agent": ua}, timeout=45, follow_redirects=True)

    print(f"URL: {args.url}")
    try:
        r = client.get(args.url)
    except httpx.HTTPError as e:
        print(f"FETCH FAILED: {type(e).__name__}: {e}")
        print("  -> TLS/certificate errors: status 'Decision needed'. Timeouts: 'Unavailable'.")
        return 1
    print(f"Status: {r.status_code}   Final URL: {r.url}")
    ctype = r.headers.get("content-type", "")
    print(f"Content-Type: {ctype}   Size: {len(r.content):,} bytes")
    ext = ".json" if "json" in ctype else ".xml" if "xml" in ctype else ".html"
    body_path = out / f"body{ext}"
    body_path.write_bytes(r.content)
    print(f"Saved body: {body_path}")

    origin = f"{r.url.scheme}://{r.url.host}"
    try:
        rb = client.get(urljoin(origin, "/robots.txt"))
        if rb.status_code == 200 and "<html" not in rb.text[:500].lower():
            (out / "robots.txt").write_text(rb.text, encoding="utf-8")
            rules = robots_rules(rb.text)
            print("robots.txt (User-agent: *): " + ("; ".join(rules) if rules else "no rules for *"))
            path = urlparse(str(r.url)).path or "/"
            blocked = [x for x in rules if x.startswith("disallow:") and x.split(":", 1)[1].strip()
                       and path.startswith(x.split(":", 1)[1].strip())]
            if blocked:
                print(f"  !! Path {path} is disallowed for all bots: {blocked} -> status 'Blocked'")
        else:
            print(f"robots.txt: none (HTTP {rb.status_code} or an HTML page)")
    except httpx.HTTPError as e:
        print(f"robots.txt: not fetched ({type(e).__name__})")

    if r.status_code >= 400:
        print("  -> 4xx/5xx to a polite client: don't work around it; record as Blocked/Unavailable.")
        return 1

    if "json" in ctype:
        try:
            data = r.json()
            keys = list(data)[:20] if isinstance(data, dict) else f"list of {len(data)}"
            print(f"JSON top-level: {keys}")
        except ValueError:
            print("JSON: could not parse")
        return 0
    if "xml" in ctype and ("<rss" in r.text[:500] or "<feed" in r.text[:500]):
        print(f"Feed: {r.text.count('<item')} <item> / {r.text.count('<entry')} <entry> elements")
        return 0

    soup = BeautifulSoup(r.content, "html.parser")
    print(f"Title: {soup.title.get_text(strip=True) if soup.title else '-'}")
    text_len = len(soup.get_text(" ", strip=True))
    scripts = soup.find_all("script", src=True)
    if text_len < 2000 and scripts:
        print(f"Looks script-built: {text_len} chars of text, {len(scripts)} script files. "
              "Find the data endpoint; if it needs a signature/token/session, it's an access control.")
    m = re.search(r"(showing|total)[^<]{0,60}\d[\d,]*[^<]{0,30}", soup.get_text(" "), re.I)
    if m:
        print(f"Count text: {' '.join(m.group(0).split())}")
    tables = soup.find_all("table")
    print(f"Tables: {len(tables)}")
    for i, t in enumerate(tables[:3]):
        rows = t.find_all("tr")
        print(f"  table {i}: {len(rows)} rows")
        for tr in rows[:3]:
            cells = [" ".join(c.get_text(" ", strip=True).split())[:50] for c in tr.find_all(["th", "td"])]
            print(f"    {cells}")
    links = sorted({urljoin(str(r.url), a["href"]) for a in soup.find_all("a", href=True)
                    if KEYWORDS.search(a["href"]) or KEYWORDS.search(a.get_text(" ", strip=True))})
    print(f"Listing-like links: {len(links)}")
    for l in links[:15]:
        print(f"  {l}")
    pages = sorted(set(re.findall(r'href="([^"]*[?&](?:page|p|start|offset)=\d+[^"]*)"', r.text)))
    if pages:
        print(f"Pagination hints: {pages[:5]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
