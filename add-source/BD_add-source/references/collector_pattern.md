# Collector pattern

Copy the shape of an existing collector rather than inventing one:
`src/bdleads/sources/worldbank.py` (JSON API), `ppra.py` (HTML list + detail pages),
`psx.py` (one page per entity), `rss.py` (feeds).

## Skeleton

```python
"""<Source name> (<official URL>).

<How the source is organised: pagination, sort order, what one item is.>
<Anything surprising found when probing, with the date.>
"""

from __future__ import annotations

from datetime import datetime

from bs4 import BeautifulSoup

from .. import config
from ..classify import classify
from ..models import Evidence, Lead, RawItem, utcnow
from ..score import score
from . import CollectResult, PoliteClient, clean


def parse_list(html: str) -> list[dict]:
    """Fields of each item exactly as shown on the page (strings, cleaned of whitespace)."""
    ...


def item_to_leads(item: RawItem) -> list[Lead]:
    d = item.data
    text = " ".join(filter(None, [d.get("title"), d.get("description")]))
    c = classify(text, sector_text=text, signal_groups={})   # tenders: no company-event signals
    if not c.agencies:
        return []
    lead = Lead(
        kind="tender",
        title=d["title"],
        source_key=item.key,
        organization=d.get("organization"),         # None unless the source states it
        published_on=...,                           # parsed from the source's own date, else None
        deadline=...,                               # same
        evidence=[Evidence(source_name=config.sources()["<name>"]["name"], source_url=item.url,
                           fetched_at=item.fetched_at, excerpt="<verbatim fields joined>",
                           published_at=...)],
        classification=c,
    )
    return [score(lead)]


def collect(max_pages: int | None = None) -> CollectResult:
    cfg = config.sources()["<name>"]
    res = CollectResult(source="<name>")
    http = PoliteClient()
    try:
        for page in range(1, (max_pages or cfg["max_pages"]) + 1):
            try:
                r = http.get(cfg["list_url"], params={"page": page})
            except Exception as e:  # noqa: BLE001 - record and stop, never invent
                res.errors.append(f"page {page}: {e}")
                break
            fetched_at = utcnow()
            rows = parse_list(r.text)
            if not rows:
                break
            res.fetched += len(rows)
            res.items.extend(RawItem(source="<name>", key=row["<stable id>"], url=row["<link>"],
                                     fetched_at=fetched_at, data=row) for row in rows)
    finally:
        http.close()
    return res
```

## Checklist

- [ ] Every item read becomes a `RawItem`: no relevance filtering inside `collect`.
- [ ] `key` is stable across runs (notice/contract/tender number, or the item URL).
- [ ] `url` is the item's own page if it has one; otherwise the list page.
- [ ] Dates parsed only from the source's own fields; unparseable → `None`, not a guess.
- [ ] `item_to_leads` makes no network calls (it runs again during `reclassify`).
- [ ] Detail pages fetched only for likely-relevant items, and stored in `data["detail"]`.
- [ ] Errors are appended to `res.errors`; the collector never fabricates a fallback.
- [ ] `sources.toml` section added with the Edit tool; `uv run pytest -q` passes, including
      `tests/test_registry.py::test_sources_config_is_complete` (update its section list).
- [ ] Registered in `pipeline.SOURCES` and `pipeline._MODULES`.
- [ ] Registry row updated; `uv run bdleads sources validate` clean.
