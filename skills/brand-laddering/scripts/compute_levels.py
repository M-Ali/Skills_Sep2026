"""Per-brand Brand Meaning Ladder placement from classified items.

    uv run --with pandas python compute_levels.py levels.csv --out ladder_levels.csv

Input: a CSV with at least `brand` and `ladder_level` (1-6), one row per coded post or ad.
Output: one row per brand with n, count per level, modal level, mean and a split flag.

Placement rule: a brand sits on its MODAL rung with the mean shown beside it, so the row
and the number can never contradict each other. Ties on the mode go to the lower level,
because the ladder does not let a brand claim a rung it only reaches half the time. `split`
is true when modal and mean differ by more than one level; say so on the slide rather than
forcing one rung.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


def compute(df: pd.DataFrame) -> pd.DataFrame:
    missing = {"brand", "ladder_level"} - set(df.columns)
    if missing:
        raise SystemExit(f"input is missing columns: {sorted(missing)}")
    bad = df[~df.ladder_level.isin([1, 2, 3, 4, 5, 6])]
    if len(bad):
        raise SystemExit(f"{len(bad)} rows have ladder_level outside 1-6, e.g.\n{bad.head()}")

    rows = []
    for brand, g in df.groupby("brand", sort=True):
        counts = g.ladder_level.value_counts()
        top = counts.max()
        mode = int(min(counts[counts == top].index))  # tie -> lower level
        mean = float(g.ladder_level.mean())
        row = {"brand": brand, "n": len(g)}
        row.update({f"L{lv}": int(counts.get(lv, 0)) for lv in range(1, 7)})
        row.update({"mode": mode, "mean": round(mean, 2), "split": abs(mean - mode) > 1})
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["mode", "mean"]).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("levels_csv", type=Path)
    ap.add_argument("--out", type=Path, default=Path("ladder_levels.csv"))
    args = ap.parse_args()

    table = compute(pd.read_csv(args.levels_csv))
    table.to_csv(args.out, index=False)
    print(table.to_string(index=False))
    print(f"\nwrote {args.out}  ({len(table)} brands)")
    for _, r in table[table.split].iterrows():
        print(f"SPLIT: {r.brand} - modal L{r['mode']} but mean {r['mean']}; describe as split on the slide")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
