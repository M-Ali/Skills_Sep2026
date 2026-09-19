---
name: brand-laddering
description: "Build the Brand Meaning Ladder section of a pitch or strategy deck - a divider plus four slides that take the audience from how the framework works, to where the category and each competitor sit, to the client's own ladder and the level it should own. Every placement is computed from coded communication and checked against consumer evidence, never typed. Use whenever the user wants brand laddering slides, a ladder section, levels of branding, the Brand Meaning Ladder in a deck, factor lists per level, 'where does the category sit', 'where should the client stand on the ladder', or asks to turn a category scan plus consumer comments into ladder slides - even if they only say 'add the ladder' or 'do the laddering for this brand'. Also use to rebuild or audit an existing ladder section whose numbers or placements look asserted, inconsistent between slides, or overflowing the slide."
---

# Brand laddering - the deck section

A ladder section persuades because it looks measured: brands sitting on rungs, a number
beside each name, an arrow to where the client should go. That is exactly why it has to be
real. If one slide puts the client on Level 5 and the next computes Level 1, the first
person in the room who compares them ends the argument. This skill produces a five-slide
section where every placement traces to a file and the story runs in the order an audience
can follow.

The method underneath (six levels, boundary rules, evidence tags) is the Brand Meaning
Ladder. The full framework is in `references/levels.md`; read it before classifying
anything, because the boundaries between levels are where nearly all errors happen.

## Strictly no guesswork

A ladder slide is a set of claims about brands, dressed as measurement. Every cell on it must
be traceable to a file, or it must not be on the slide. This is not a counsel of perfection -
it is what stops the section collapsing when a client asks "how did you get that?".

**The rule: if you cannot name the file and the count behind a cell, the cell is wrong.** Three
ways this discipline gets broken, all of them observed in real decks:

1. **A number nobody computed.** A mean typed into a content file (4.1) put a client two rungs
   above where its classified posts actually sat, and contradicted the very next slide. Means
   and modal levels come from `compute_levels.py` output and nowhere else.
2. **A brand placed without being classified.** Placing competitors from impression - "Transworld
   feels emotional, Jazz feels functional" - produces a tidy slide with no evidence under it.
   Classify a brand's posts, or describe what it does without scoring it. A descriptive row is
   honest; an invented number is not.
3. **A factor at the wrong level because of its topic.** Heritage placed at Level 5 because it
   *feels* like a value. Heritage as "we are 79 years old" is Level 1 recognition; it only
   reaches Level 5 when a belief is stated. Classify by what the claim does (Step 1).

Where evidence genuinely runs out, say so on the slide - "no clear purpose evidence in the
category", "posts not yet classified" - and put the gap in the footnote. A stated gap costs
nothing; an invented number costs the whole section. The builder enforces what it can
(`validate()` refuses off-modal placements and unclassified brands); the rest is on you.

**This applies to the client-facing version too.** Simplifying means shorter words and fewer
numbers, never looser facts. When a cell is compressed for a client audience, it must still be
the same finding: "10 of 24 posts" may become "most of its communication", but it may not
become a level the data does not support.

## What you need before starting

| Input | Typically from | Used for |
|---|---|---|
| Coded communication - one row per post/ad with brand and a claim or focus code | `category-creative-scan`, `competitor-comms-audit` | What brands *say*: the claim ladder |
| Consumer evidence - comments, reviews, research | `comment-analysis` | What customers *judge on*: the earned ladder |
| Client brief / brand documents | `brief-to-plan` | Client assets and constraints for the placement column |

If there is no consumer evidence, you can build slides 1-3 but not an honest client ladder
(slide 5). Say so and stop there; don't fill the "heard" column from imagination.

If the consumer evidence came from a filtered subset (e.g. only comments that mention the
client), label it as such. Findings from a subset must not be presented as what "customers"
think. Read the whole corpus for the category-level column.

## The five slides, in order

The order is deliberate: the audience learns the framework, sees it filled in for their
category, sees where everyone stands, and only then sees the recommendation. Showing the
client's placement first invites argument about the framework instead of the finding.

1. **Divider - "The Brand Meaning Ladder".** One line on what it is ("how consumers see a
   brand - from what it is and does, to what it means to them") and one on the direction
   ("from functional benefits -> to emotions -> to values and purpose").
2. **Placement - "Levels of branding: where the category is, and where [client] is talking".**
   Six rows, Level 6 at the top. Each row: level name + consumer voice ("I am here", "Reason
   to buy me" ...), the brands whose modal level it is with `Brand (mean)`, and a short red
   marker on the rows that matter (WHERE THE CATEGORY SITS / WHERE [CLIENT] MUST EARN /
   THE DIFFERENTIATION GAP / WHERE [CLIENT] IS TALKING).
3. **Factor list - "The Brand Meaning Ladder for [category]: the factors at each level".**
   Columns Level | Current | Potential | Unsupported. No brand placements on this slide.
4. **Category evidence - "How the Brand Meaning Ladder works in [category]".** Columns
   Level | What brands claim (with post counts and leading brands) | What customers judge on
   | Open - nobody claims.
5. **Client ladder - "[Client]'s Brand Meaning Ladder: the category's factors, and where to
   stand".** Columns Level | Factors in the category (In use / Open) | [Client] today
   (Says / Heard) | Placement (HOLD / PROVE / PLACE [CLIENT] HERE / NEXT / LATER / NOT NOW).
   Exactly one row is the target, highlighted.

Each content slide ends with a navy conclusion band carrying the one sentence the slide
exists to say, and a small footnote naming the framework and the source files. Exact
geometry, fonts and colours are in `references/slide-specs.md`. The PTCL section this skill
was distilled from is written out in `references/worked-example-ptcl.md`, including the two
mistakes it shipped with.

## Step 1 - Classify every coded item to a level

Classify by **what the claim does**, not by its topic. The same subject lands on different
rungs:

- "79 years of PTCL" - **Level 1**: heritage as recognition and presence.
- "Built the backbone so your business keeps running" - **Level 3**: heritage as proof of a benefit.
- "Every village deserves the same connection as the city" - **Level 5**: a stated value.

A national-day or pride post is not automatically Level 5. It reaches 5 only when it states
a belief or a way of life; a flag and a date is Level 1 presence, and pride through sport or
celebrity is Level 4 association. Put each item at the **deepest level the evidence
supports, and no deeper**.

Write the result into data, not only into slide text: a CSV with `post_id, brand,
ladder_level (1-6), ladder_reason`. If you map from an existing code (e.g. `product_focus`
or `claim_primary`) to a level, keep the mapping as an explicit table in a script and list
the codes you judged by hand. Classify **every scanned brand**, not only the client - slide 2
needs all of them.

## Step 2 - Compute the placements

Run the bundled script rather than eyeballing counts:

```bash
uv run --with pandas python <skill>/scripts/compute_levels.py <levels.csv> --out ladder_levels.csv
```

It writes per brand: n, count at each level, **modal level**, mean and a `split` flag (modal
and mean more than one level apart). The rules it implements, and why:

- **A brand sits on the rung of its modal level, with the mean shown beside it.** Then the
  row and the number cannot contradict each other. A mean of 4.1 printed in the Level-5 row
  is precisely the inconsistency to prevent.
- **If `split` is true, say the brand is split** ("PTCL - split: L1 recognition and L4 pride")
  instead of forcing one rung.
- **Place every scanned brand.** Dropping a brand silently changes the finding. If one is left
  off, give the reason in the footnote. Check specifically whether an omitted brand sits on a
  rung you are about to call empty.

## Step 3 - Build the factor list (slide 3)

Start from the framework's own factor list for each level (`references/levels.md`) and keep
every factor - sort, don't delete:

- **Current** - seen in the category's coded communication. Only mark a factor current if you
  can point to posts.
- **Potential** - relevant to this category, not yet claimed by anyone.
- **Unsupported** - little link to the category (healthy living or packaging for a
  broadband service). This is where framework factors that don't fit go, so the audience can
  see they were considered.
- **Add category-specific factors only when the evidence calls for them**, and mark each with
  **†** so nobody mistakes them for framework factors. The consumer evidence is the usual
  source (e.g. "a bill that stays predictable †").
- For Level 6, if no brand states a purpose, write "No clear purpose evidence in the category".

## Step 4 - Build the category evidence slide (slide 4)

Per level, three short cells:

- **What brands claim** - the factors with counts and the leading brands:
  "value for money (31: Zong 9, Optix 7)".
- **What customers judge on** - from the consumer evidence, in their terms, quoted sparingly.
- **Open - nobody claims** - the gap at that level.

Footnote that a coded claim can sit at more than one level, so counts show where factors
appear, not per-level totals. Otherwise someone will add the column up and find it doesn't
reach N.

## Step 5 - Build the client ladder and decide (slide 5)

Per level: **In use** (category) and **Open**; **Says** (client's own post count at that level,
from the computed table) and **Heard** (consumer evidence, with a strength word - Strong /
Mixed / Weak / Negative / Not established); then the placement.

The placement is a decision, not a menu. Choose **the deepest level that is relevant,
credible, distinctive and defensible** - the framework's own test. Higher is not better:

- Recommend moving up only when the client has evidence of permission. A values claim while
  customers dispute the basics widens the credibility gap rather than closing it.
- A strong, provable benefit position usually beats an unearned values position.
- Levels above the target get NEXT / LATER / NOT NOW with the condition that earns them;
  levels below get HOLD (already owned) or PROVE (must be demonstrated for the target to hold).

Use the evidence tags from the framework when you write the cells: OBSERVED (cite it),
INFERRED (say from what), OPPORTUNITY (not a current association). Never let an opportunity
read as something customers already believe.

## Step 6 - Render the slides

Write the content as a JSON spec (shape: `assets/example_spec.json`) and build:

```bash
uv run --with python-pptx python <skill>/scripts/build_ladder_section.py spec.json \
    --levels ladder_levels.csv [--base existing_deck.pptx --insert-at N]
```

The script builds the five slides in the house style. With `--base` it inserts them into a
copy of an existing deck. It **never overwrites**: it writes the next free `-vN` next to the
spec's `out` path. With `--levels` it refuses to build if a brand in the computed table does
not appear on its modal rung on slide 2, or if the client's slide-5 "Says" counts disagree
with the table. That is the check that would have caught the PTCL mismatch.

## Step 7 - Check before handing over

Render the slides to images and look at every one. Text that fits in python-pptx can still
overflow in PowerPoint. On Windows, export via PowerPoint COM; elsewhere use LibreOffice.

- Six rows end above the conclusion band, and the footnote is on the slide. Long factor lists
  (Level 4 potential is the usual culprit) get smaller type, not taller rows.
- Slide 2's client row, slide 5's target row and the conclusion sentences all name the same
  level.
- Every number on the slides is in `ladder_levels.csv` or the source counts.
- Every † factor traces to evidence; every OBSERVED cell has a citation somewhere.
- Headline claims about "customers" rest on the whole consumer corpus, not a filtered subset.

## Client-facing version

The internal section carries counts, file names and verbatims. For a client presentation,
collapse slides 2-5 into a single ladder slide (Level | The category | [Client]'s own posts |
Direction), drop footnotes and file names, and replace hostile verbatims with neutral themes.
The direction column and the decision stay the same - only the register changes.

Build the client slide from the same computed table as the internal one, not from memory of
what the internal slides said. Restating them by hand is how a corrected placement survives in
the client deck after the internal deck is fixed - which is exactly what happened on the PTCL
job, where "heritage and national pride" sat at Level 5 in the client version for a week after
the internal slide had been rebuilt.

Two habits that keep the client version honest while staying light:

- **Head the client column "[Client]'s own posts", not "[Client] today".** It says what the
  column is: what the brand publishes, not a verdict on the brand.
- **Keep the fraction where it carries the argument.** "10 of 24 posts" is not fine print; it is
  the finding. Drop the method, the file names and the caveats - never the count that makes the
  gap visible.
