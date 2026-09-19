#!/usr/bin/env python3
"""Identify which review app a storefront runs, and pull the ids needed to read it.

Usage:
    python detect_review_platform.py https://example.com
    python detect_review_platform.py https://example.com --page /products/some-product

Fetches the page, looks for each vendor's fingerprints, and prints the
identifiers the collection step needs (widget id, shop domain, app key). Sites
often run two or three review apps at once with the corpus in only one of them,
so this reports everything it finds rather than stopping at the first hit.

Only reads public HTML. Nothing here authenticates.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    sys.exit("pip install requests")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "review-analysis-skill/1.0 (public widget discovery)")

# name -> (fingerprints, {identifier: regex})
PLATFORMS: dict[str, tuple[tuple[str, ...], dict[str, str]]] = {
    "Loox": (
        ("loox.io", "looxReviews", "loox_global_hash", "loox-rating"),
        {"widget_id": r"loox\.io\\?/widget\\?/([A-Za-z0-9_-]{6,})",
         "shop": r"loox[^\"']{0,120}?shop=([a-z0-9-]+\.myshopify\.com)"},
    ),
    "Judge.me": (
        ("judge.me", "jdgm-widget", "jdgm_widget", "judgeme"),
        {"shop": r"data-shop-domain=[\"']([a-z0-9.-]+)[\"']",
         "public_token": r"jdgm[_-]?(?:public_?)?token[\"':= ]+[\"']?([A-Za-z0-9_-]{10,})"},
    ),
    "Yotpo": (
        ("yotpo", "staticw2.yotpo.com", "yotpo-widget"),
        {"app_key": r"(?:appkey|app_key|yotpo_app_key)[\"':= ]+[\"']?([A-Za-z0-9]{20,})"},
    ),
    "Okendo": (
        ("okendo", "oke-reviews", "okendoSettings"),
        {"subscriber_id": r"okendo[^\"']{0,80}?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}"
                          r"-[0-9a-f]{4}-[0-9a-f]{12})"},
    ),
    "Stamped.io": (
        ("stamped.io", "stamped-reviews-widget", "stamped-widget"),
        {"public_key": r"data-api-key=[\"']([A-Za-z0-9-]{16,})[\"']",
         "store_url": r"data-store-url=[\"']([a-z0-9.-]+)[\"']"},
    ),
    "Shopify Product Reviews": (
        ("shopify-product-reviews", "spr-badge", "spr-review"),
        {},
    ),
    "Trustpilot": (
        ("trustpilot.com", "trustpilot-widget", "tp-widget"),
        {"business_unit": r"data-businessunit-id=[\"']([A-Za-z0-9]+)[\"']"},
    ),
}


def fetch(url: str, timeout: int = 30) -> str:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout)
    r.raise_for_status()
    # Widgets rarely declare a charset; guessing mangles every curly quote.
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def detect(html: str) -> dict[str, dict]:
    low = html.lower()
    found: dict[str, dict] = {}
    for name, (fingerprints, patterns) in PLATFORMS.items():
        hits = {fp: low.count(fp.lower()) for fp in fingerprints}
        total = sum(hits.values())
        if not total:
            continue
        ids: dict[str, str] = {}
        for key, pattern in patterns.items():
            m = re.search(pattern, html, re.I)
            if m:
                ids[key] = m.group(1)
        found[name] = {
            "fingerprint_hits": total,
            "matched": {k: v for k, v in hits.items() if v},
            "identifiers": ids,
        }
    return found


def shopify_domain(html: str) -> str | None:
    m = re.search(r"([a-z0-9-]+\.myshopify\.com)", html, re.I)
    return m.group(1) if m else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url")
    ap.add_argument("--page", action="append", default=[],
                    help="Extra path to check, e.g. /products/foo. Repeatable.")
    ap.add_argument("--json", action="store_true", help="Machine-readable output.")
    args = ap.parse_args()

    targets = [args.url] + [urljoin(args.url, p) for p in args.page]
    merged: dict[str, dict] = {}
    shop = None

    for target in targets:
        try:
            html = fetch(target)
        except Exception as exc:  # noqa: BLE001 - report and carry on
            print(f"  ! could not read {target}: {exc}", file=sys.stderr)
            continue
        shop = shop or shopify_domain(html)
        for name, info in detect(html).items():
            if name not in merged:
                merged[name] = info
                merged[name]["seen_on"] = [target]
            else:
                merged[name]["fingerprint_hits"] += info["fingerprint_hits"]
                merged[name]["identifiers"].update(info["identifiers"])
                merged[name]["seen_on"].append(target)

    result = {"url": args.url, "shopify_domain": shop, "platforms": merged}

    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if merged else 1

    print(f"\n{args.url}")
    if shop:
        print(f"  Shopify store: {shop}")
    if not merged:
        print("\n  No known review app detected.")
        print("  Check a product page too (--page /products/<handle>) - some "
              "apps only load there.")
        return 1

    print(f"\n  {len(merged)} review app(s) detected:\n")
    for name, info in sorted(merged.items(),
                             key=lambda kv: -kv[1]["fingerprint_hits"]):
        print(f"  {name}  ({info['fingerprint_hits']} fingerprint hits)")
        for key, value in info["identifiers"].items():
            print(f"      {key}: {value}")
        if not info["identifiers"]:
            print("      (no identifiers extracted - check the page source by hand)")
    if len(merged) > 1:
        print("\n  More than one app is installed. The corpus is usually in only "
              "one of them;\n  check each and report which you read and which "
              "you did not.")
    print("\n  Next: references/platforms.md for this app's endpoint.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
