# Review platform endpoints

How to collect the full corpus from each of the common Shopify/DTC review apps.
All of these read the **public** widget - the same thing a visitor's browser
loads. None requires authentication. If a platform needs an API key you have not
been given, stop and ask the user for it rather than looking for a way around.

Always: set `r.encoding = "utf-8"`, sleep 0.5-1s between requests, and reconcile
your row count against the widget's own rating histogram.

---

## Loox

**Fingerprints in page source:** `loox.io`, `loox_global_hash`, `looxReviews`,
a `loox.io/widget/<WIDGET_ID>/loox.<build>.js?shop=<shop>.myshopify.com` script tag.

**Widget id** is the path segment after `/widget/` (e.g. `F6xVT4Jbro`).

**Endpoint:** `https://loox.io/widget/<WIDGET_ID>/reviews?page=<N>`

- Returns HTML, 20 reviews per page, from page 1.
- Stop when a page returns fewer than 20 items, or zero.
- `?rating=<1-5>` filters to a single star rating - useful for pulling the
  low-star set quickly without walking the whole corpus.
- Sort options exist in the UI but the query params are not reliable; walk the
  default order and sort locally.

**Parsing (BeautifulSoup + lxml):**

| Field | Selector |
| --- | --- |
| container | `.grid-item` |
| review id | `[data-testid]` → strip `review-` prefix and the trailing `-title` |
| author | `.block.title` (strip the trailing "Verified") |
| verified | presence of `.loox-verified-badge` |
| date | `.block.time` → `data-time` attribute, epoch **milliseconds** |
| rating | count of `svg[data-lx-fill=full]` |
| body | `.pre-wrap.main-text` |
| product | `.block.product-box` |
| media | presence of `.item-img img` |

**Histogram for the completeness check:** `.rating-dist-row .reviews-num`,
five elements in order 5★ → 1★, formatted like `(3,046)`.

---

## Judge.me

**Fingerprints:** `judge.me`, `jdgm-widget`, `data-shop-domain`.

**Endpoint:**
`https://judge.me/reviews/reviews_for_widget?url=<shop>.myshopify.com&shop_domain=<shop>.myshopify.com&platform=shopify&page=<N>`

- Returns JSON containing an `html` field; parse that HTML.
- Containers are `.jdgm-rev`, with `data-score`, `data-verified-buyer` and
  `.jdgm-rev__timestamp` / `.jdgm-rev__body` / `.jdgm-rev__product-link`.
- Per-product: add `&product_id=<shopify_product_id>`.

---

## Yotpo

**Fingerprints:** `yotpo`, `staticw2.yotpo.com`, an `appkey` in the page source.

**Endpoint:**
`https://api.yotpo.com/v1/widget/<APP_KEY>/products/<PRODUCT_ID>/reviews.json?page=<N>&per_page=150`

- Clean JSON. Per-product only, so you must enumerate products first (the
  Shopify `/products.json` endpoint, or the collection pages).
- Site-wide alternative: `https://api.yotpo.com/v1/apps/<APP_KEY>/reviews?count=100&page=<N>`
  (may require a token depending on the plan).

---

## Okendo

**Fingerprints:** `okendo`, `oke-reviews`, a subscriber id like `<uuid>` in
`okendoSettings`.

**Endpoint:**
`https://api.okendo.io/v1/stores/<SUBSCRIBER_ID>/reviews?limit=100&offset=<N>`

- JSON, well structured, includes attributes and media.

---

## Stamped.io

**Fingerprints:** `stamped.io`, `stamped-reviews-widget`, a public key in
`data-widget-*` attributes.

**Endpoint:**
`https://stamped.io/api/widget/reviews?productId=<ID>&storeUrl=<shop>.myshopify.com&apiKey=<PUBLIC_KEY>&page=<N>`

---

## Trustpilot

Public, paginated HTML at `https://www.trustpilot.com/review/<domain>?page=<N>`.
Reviews are embedded as JSON in a `__NEXT_DATA__` script tag - parse that rather
than the DOM, it is far more stable.

Note Trustpilot reviews are about the **company**, not individual products, so
they answer service and delivery questions but not product-quality ones.

---

## Amazon

Do not scrape Amazon review pages. It is against their terms, heavily
rate-limited and bot-protected. If the user needs Amazon review data, point them
at the Product Advertising API or an official data export.

---

## When the markup has changed

These parsers depend on vendor class names and will eventually break. Symptoms
and responses:

- **Zero rows parsed** - the container selector changed. Print the first 2KB of
  the page and re-derive the selectors from the live markup.
- **Right count, empty text** - only the body selector changed.
- **Ratings all zero** - the star markup changed; look for a `data-*` attribute
  carrying the score before counting filled icons.
- **Count disagrees with the histogram** - pagination changed, or the widget
  deduplicates across pages. Track review ids in a set and stop on no-new-ids
  rather than trusting page size alone.
