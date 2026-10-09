"""Run the app's own classification rules over real item texts from a candidate source.

Usage:
    uv run python .claude/skills/add-source/scripts/relevance_check.py <texts.json> [--show N]

<texts.json> is a JSON list of strings, one per item (title + short description, as
published by the source). Prints how many match an agency rule, which keywords matched,
and the matching texts. Read-only: nothing is stored.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

from bdleads.classify import classify


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("texts")
    ap.add_argument("--show", type=int, default=15)
    args = ap.parse_args()
    with open(args.texts, encoding="utf-8") as f:
        texts = [t for t in json.load(f) if isinstance(t, str) and t.strip()]
    hits, agencies, keywords = [], Counter(), Counter()
    for t in texts:
        c = classify(t, signal_groups={})
        if c.agencies:
            hits.append((t, c))
            agencies.update(c.agencies)
            keywords.update(m for m in c.matched if m.startswith("agency:"))
    print(f"Items checked: {len(texts)}")
    print(f"Matching an agency rule: {len(hits)}"
          + (f" ({len(hits) / len(texts):.1%})" if texts else ""))
    if agencies:
        print("By agency: " + ", ".join(f"{a} {n}" for a, n in agencies.most_common()))
        print("Keywords: " + "; ".join(f"{k} x{n}" for k, n in keywords.most_common(10)))
    for t, c in hits[: args.show]:
        print(f"  - {t[:140]}")
        print(f"      {'; '.join(m for m in c.matched if m.startswith('agency:'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
