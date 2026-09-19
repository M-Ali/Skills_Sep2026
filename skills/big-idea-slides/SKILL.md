---
name: big-idea-slides
description: "Build the Big Idea section of a pitch or strategy deck - a divider, one slide per insight (consumer, category, brand), the convergence slide where the three lines become one organising thought, the strategy statement and comms platform with alternatives considered, and the price of the idea. Each insight slide carries its line, its evidence and its source, so the idea arrives as a conclusion rather than an assertion. Use whenever the user wants Big Idea slides, an insight section, 'three insights one idea', a convergence slide, a strategy statement or comms platform slide, alternatives considered, or asks to turn a consumer analysis plus category scan plus client brief into the strategy part of a deck - even if they only say 'add the big idea' or 'put the insights into slides'. Also use to rebuild or audit an existing Big Idea section whose insight lines are restated findings, whose idea is really a tagline, or that presents an idea without saying what it asks of the client."
---

# The Big Idea - the deck section

Research produces findings; findings do not brief anyone. The Big Idea section is where a
deck stops reporting and starts deciding. It works when the audience can see the idea coming:
three evidenced lines, each from a different source, converging on one thought that none of
them could have produced alone.

The method - how to find the three insights and test the idea - is in `references/method.md`.
Read it before writing lines. This skill covers turning that work into slides that hold up
when a client pushes back, and it bundles a builder so the section is rendered from a spec
rather than hand-placed.

## What the section contains

| # | Slide | The job it does |
|---|---|---|
| 1 | Divider - "The Big Idea" | Signals the turn from evidence to decision |
| 2 | Consumer insight | What people feel that the category ignores - **relevance** |
| 3 | Category insight | What everyone else does and what it leaves open - **distinctiveness** |
| 4 | Brand insight | What the client has or faces that makes the space its own - **ownership** |
| 5 | Convergence - the Big Idea | The three lines, an arrow, the organising thought |
| 6 | From idea to strategy | Strategy statement, comms platform, why it holds, alternatives considered |
| 7 | The price of the idea (recommended) | What the client must commit to, and the media principles |

Slides 2-4 share one layout: a kicker ("STEP 1 · CONSUMER INSIGHT · FROM THE CONSUMER PULSE"),
the insight in large quoted type against a red rule, evidence bullets on the left, an
interpretation panel on the right, and a source line. Geometry is in
`references/slide-specs.md`; the PTCL section this was distilled from is in
`references/worked-example-ptcl.md`.

## How to write the three insight slides

**The line is one sentence and contains a tension.** A fact is not an insight. "Customers
complain about rising bills" is a finding; "customers don't mind paying more, they mind
finding out after they have committed" is an insight, because it names the want and the
barrier in the same breath. If a line needs a semicolon to hold two thoughts together, it is
two candidates, not one insight.

**Each slide names its own source, and its own limits.** The consumer slide says what corpus
and how it was read; the category slide says how many posts across how many brands; the brand
slide says which document and page. Where the evidence is thin or the client has not supplied
something, say so on the slide - the builder supports a red PROVISIONAL tag for exactly this.
A client who sees a caveat trusts the rest more, not less.

**The interpretation panel is where you earn the line.** Evidence bullets show what was said;
the panel says what it means ("the words are fraud, chor, zulm - the language of being taken
advantage of, not of slow service"). Use it for the register of the language, the mechanism
behind the category's behaviour, or the place the brief and the customer disagree.

**Say where a client document and the evidence disagree, diplomatically but plainly.** That
contradiction is frequently the brand insight and the most valuable thing in the section. Cite
both sides, and let the brief's own words carry the point where they can.

**Beware the insight drawn from a filtered subset.** An insight built only from comments that
mention the client is about the client's customers, not about the category. Either read the
whole corpus or label the line accordingly. Presenting a subset finding as "what customers
think" is the mistake most likely to be caught in the room.

## The convergence slide

Three short forms of the lines, each tagged with the role it plays (Relevant / Distinctive /
Ownable), an arrow, then the idea in a navy band, then one sentence of what it means for the
brand, then the removal test.

The short forms must say the same thing as the full lines on slides 2-4 - shortened, never
changed. The builder derives them from the insight slides' `short` field and refuses to build
if one is missing, because a convergence slide that quietly restates an insight is how a
section drifts away from its own evidence.

**The idea is a thought, not a tagline.** "PTCL is the connection you can hold to its word" is
an organising thought: a media planner, a social team and a film director can each act on it.
The line that goes on air comes later, from `campaign-concept`. If the idea and the comms
platform are the same words, one of them is doing no work - the builder flags it.

**Run the removal test on the slide, not just in your head.** Remove the consumer insight and
the idea becomes a corporate virtue; remove the category insight and it is table stakes;
remove the brand insight and a competitor could run it tomorrow. Print that test so the
audience can check it.

## Strategy, platform and alternatives

- **Strategy statement:** "Re-frame [brand] from [current perception] to [desired role] by
  [how]." The builder warns when from / to / by are not all present, because a statement
  missing one of them is a sentiment rather than a strategy.
- **Comms platform:** "Position [brand] as [THE ROLE]." One line, in the accent colour, that
  every channel can be briefed from.
- **Why it holds:** one line each for relevant, distinctive, ownable - tying back to the three
  insights.
- **Alternatives considered:** the other candidate ideas with their trade-offs, one marked
  recommended, plus the swap test (what a named competitor could also claim, and what they
  could not). This panel is what turns a presentation into a decision: it shows the client the
  road not taken and why. A section with no alternatives reads as the only idea anyone had.

## The price of the idea

If the idea requires the client to change something - terms, service standards, staffing -
say so explicitly, as a numbered list of commitments, before any line is written. Clients
reward being told the price, and an idea whose proof never arrives damages the brand more
than no campaign at all. State plainly what to do if the client will not commit (usually:
recommend the runner-up idea and name the trade-off).

Pair the commitments with media principles drawn from the channel insight - where the
decision is actually made, and what the brand must do there.

## Building the slides

Write the content as a JSON spec (shape: `assets/example_spec.json`) and run:

```bash
uv run --with python-pptx python <skill>/scripts/build_big_idea_section.py spec.json \
    [--base existing_deck.pptx --insert-at N]
```

It builds the section in the house style, never overwrites (writes the next free `-vN`), and
refuses to build when the section would mislead:

- an insight is missing its `short` form, its evidence or its source;
- the big idea repeats the comms platform verbatim;
- no alternative is marked `recommended`, or fewer than two alternatives are given;
- `requires_commitments` is true but the commitments list is empty.

Warnings (printed, not fatal): an insight line that holds two thoughts, a strategy statement
missing from / to / by, an insight with only one piece of evidence.

## Check before handing over

Render every slide to an image and look at it - text that fits in python-pptx can still
overflow in PowerPoint. On Windows export via PowerPoint COM; elsewhere use LibreOffice. Then:

- The three short lines on the convergence slide match the full lines on slides 2-4.
- Every number, quote and page reference on a slide exists in the source file it cites.
- Quotes are verbatim; translations are labelled as translations.
- Anything provisional is tagged, and nothing inferred reads as observed.
- The idea, the strategy statement and the platform all say the same thing in different
  registers. If the platform introduces a new promise, the section has two ideas.

## Client-facing version

For a client presentation, keep the shape but lower the volume: drop the verbatims that
accuse, the file names and the corpus caveats; keep the three insights, the idea, the strategy
and the platform. Keep the commitments - they are the ask - but frame them as proof points the
client can choose. The internal version argues; the client version decides.
