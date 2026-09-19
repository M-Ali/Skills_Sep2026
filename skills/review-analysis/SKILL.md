---
name: review-analysis
description: Mine a brand's own customer reviews into a decided analysis - collect the full corpus from whatever review app the site runs (Loox, Judge.me, Yotpo, Okendo, Stamped, Trustpilot), code every review against a theme taxonomy, and produce pain points, satisfaction drivers, product-level risk and a ranked action list. Use this whenever the user mentions customer reviews, review analysis, ratings, star ratings, testimonials, review scraping, voice of customer, customer feedback, complaints, pain points, what customers are saying, satisfaction, NPS-style sentiment, or product quality signals - and also whenever a site audit, growth review or ecommerce analysis has surfaced a review widget that nobody has read as data. Applies even if the user only says "they have loads of reviews, can we do something with that".
---

# Review analysis

A brand's review corpus is usually the only dataset about its customers that is
already public, already written in their own words, and already free. It is also
almost never read as data - it sits in a widget being used as decoration.

This skill turns that corpus into a defensible analysis: what goes wrong, what
goes right, which products carry risk, and what to do about it.

## The one thing to get right

**The average rating is not the finding.** Almost every store running a review
app sits between 4.6 and 4.9, because the request only goes to people who bought
and the quietly disappointed mostly do not answer. If you lead with "4.87 out of
5" you have told the client nothing they did not know and nothing they can act
on.

The information lives in three places, and the whole analysis is built around
them:

1. **The reviews under four stars.** Usually 2-5% of the corpus, which makes
   them few enough to read individually and specific enough to act on.
2. **The spread between products**, once listings are merged properly.
3. **The themes that move the rating when they appear** - measured as a gap
   against the corpus average, not as a raw mention count.

Say the ceiling-effect point explicitly on a slide. It reframes the entire deck
from a scorecard into a defect list, and it is the sentence that earns trust
with a client who has been told for years that 4.87 means everything is fine.

## Workflow

### 1. Find the review platform

Fetch the homepage and one product page and look for the app's fingerprints.
`scripts/detect_review_platform.py <url>` does this and prints the identifiers
you need (shop domain, widget id, app key).

Sites commonly run two or three review apps at once, with the corpus in only one
of them. Check all of them and say in the output which you read and which you
did not - a client who knows they have Judge.me will ask.

Endpoint recipes per platform are in `references/platforms.md`. Read that file
once you know which app you are dealing with.

### 2. Collect the whole corpus

Read the same public pages a visitor's browser reads, one page at a time, with a
delay (0.5-1s) between requests. Do not authenticate, do not use an API key you
were not given, and do not collect anything that is not already displayed
publicly on the site.

Three things that will bite you:

- **Force UTF-8.** Most widgets do not declare a charset and `requests` then
  guesses latin-1, turning every curly apostrophe in the corpus into mojibake.
  Set `r.encoding = "utf-8"` explicitly.
- **Verify completeness.** Widgets publish their own rating histogram. Sum it
  and check your row count against it, then report the ratio. "3,273 of 3,273"
  is a much stronger claim than "3,273 reviews", and if the numbers disagree you
  have found a pagination bug before the client does.
- **Fail loudly on an empty page.** These parsers read HTML class names, which
  the vendor can change at any time. A parser that silently returns zero rows
  produces an analysis of nothing.

Fields worth capturing: review id, rating, date, author, verified badge, product
title, body text, and whether it carries a photo or video.

### 3. Canonicalise the products before you count anything

This is the step that is always skipped and always wrong.

Review apps store the **listing title**, not the product. A store that rewrites
its marketing copy relists the same product under a new title, and the reviews
split across both. In one real case a single product had 358 reviews spread over
five listings - so every per-product rating was computed on a fragment, and no
product page ever showed a shopper more than a fraction of its own social proof.

Collapse titles to the product: strip launch markers (`NEW!!`), then cut the
marketing tail at the first quote or spaced dash, then apply an alias map for
genuine renames. Two traps:

- Strip the launch marker **before** cutting the tail, or `NEW!! -Women's
  Precision Trimmer` gets cut at the dash and the product is named "NEW".
- Never return an empty string. A title that lives entirely inside its own
  quotes has nothing before the first one; fall back to the original.

Report the listing-to-product ratio. The relisting itself is a finding worth a
slide, because merging listings is cheap housekeeping that multiplies visible
social proof.

### 4. Code the themes deterministically

Use a fixed pattern-matching taxonomy, **not** a model, for two reasons. The
counts get quoted to a client ("312 reviews mention scent"), so they have to be
reproducible rather than resampled every run. And every theme has to be
traceable to the reviews that matched it, so a claim can be checked by reading
them.

A starter taxonomy, grouped as Job / Experience / Friction / Outcome / Loyalty,
is in `references/theme-taxonomy.md`. Adapt the vocabulary to the category -
the groups generalise, the words do not.

Rules that matter:

- **Test negated outcomes before positive ones.** "It didn't work" must never
  score as a positive on the bare word "work". Match the negated pattern first
  and exclude those rows from the positive theme.
- **Multi-label.** A review can carry several themes or none.
- **Report coverage.** State what share of reviews the taxonomy actually
  matched. Typically 55-70%; the remainder are short affirmations like "love
  it" that carry no codeable subject. Saying so is what makes the rest credible.

### 5. Measure pain points by rating gap, not mention count

For each theme, compute the mean rating of the reviews that mention it and
subtract the corpus average. That gap is what the rating *does* when a subject
comes up, and it is a far better guide to what is broken than how often people
mention it. A theme mentioned 60 times at 4.22 matters more than one mentioned
600 times at 4.86.

Filter to themes with enough mentions to mean anything (15+ is a reasonable
floor) and say what the floor was.

Run the same measurement on the low-star subset alone - "what share of your
unhappy customers mention X" - because that is the number a client acts on.

### 6. Find the language that separates happy from unhappy

Use a log-odds ratio with an informative Dirichlet prior, not raw frequency.
Plain counts just return the commonest words in both groups; a raw ratio hands
the top of the list to words used twice. The output is the vocabulary the
brand's own customers use, which belongs on the product pages and in the ads.

### 7. Write it as decisions

Structure the output as an argument, not a data tour:

```
Cover
Source & method          what was collected, and the self-selection caveat
The ceiling effect       why the average is not the finding
SECTION: What goes wrong
  Pain points            themes by rating gap
  Inside the low stars   what share of unhappy reviews mention each theme
  Product risk           ratings by product, after merging listings
  The worst product      one page, with verbatims
SECTION: What goes right
  Delight drivers        themes above the average + distinctive language
SECTION: The asset
  Review velocity        volume over time - it usually collapses
  What it is not doing   schema markup, photo share, app consolidation
SECTION: What to do
  Ranked actions         consequence first, not ease
Method & limits
```

Put real verbatims on the page next to every claim. A quote with a star rating
and a product name against it is what makes an analysis land with a founder who
believes their reviews are all glowing.

## Things to check that clients rarely have

These come up almost every time and are worth looking for:

- **Review velocity over time.** Volume usually falls year on year while the
  business grows, which means the review request itself stopped reaching people
  - a broken flow, a send delay longer than the repurchase cycle, or three
  review apps competing for the same customer. Chart it.
- **Structured data.** A corpus of thousands of reviews that emits no
  `AggregateRating` schema cannot appear as stars in search results. Check the
  product pages for JSON-LD.
- **Photo/video share.** Usually tiny. Photo reviews convert better and are
  free ad creative.
- **Thin products.** Count products under ten reviews - below that a rating is
  noise and shoppers discount it.

## Handling complaints about safety or efficacy

Health, supplement, cosmetic and intimate-care categories will surface reviews
reporting a reaction, an infection, or a product not doing what its name claims.
Handle these carefully and factually:

- Report them as **what a customer wrote**, never as a clinical finding. A
  review is not a diagnosis, and the write-up must say so.
- Give the count plainly and do not inflate it. "A small number of reviews
  report X" with the actual number is both more honest and more persuasive than
  alarm.
- Separate the three things that usually get conflated: a **claims** problem
  (the product did not do what the page promised), a **component** defect (the
  applicator, the seal, the pump), and **adverse reports**. They have different
  owners and different urgency.
- Where the brand also makes clinical-sounding marketing claims, say plainly
  that these reviews are that exposure showing up in public on the brand's own
  product page. That is a factual observation about risk, not legal advice, and
  it is usually the most valuable sentence in the deck.

Do not soften findings to keep a deck comfortable, and do not sensationalise
them either. State the count, quote the review, name the owner.

## Method page - always include one

State: how many reviews, from where, on what date, how many pages read, and the
completeness check. Then the coding rules, the theme count and the coverage
share. Then the limits, which must always include:

- Reviews are self-selected. The ratio of happy to unhappy in the corpus is not
  the ratio in the customer base and must never be quoted as satisfaction.
- Which review apps were not read.
- That product titles are as the app stores them, and how listings were merged.

## Reference files

| File | Read it when |
| --- | --- |
| `references/platforms.md` | You know which review app the site runs and need its endpoints |
| `references/theme-taxonomy.md` | Building the coding taxonomy for a new category |
| `scripts/detect_review_platform.py` | First step - identifies the app and pulls its identifiers |
