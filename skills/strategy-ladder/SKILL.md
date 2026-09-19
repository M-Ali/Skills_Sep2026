---
name: strategy-ladder
description: "Diagnose where a brand sits on the Brand Meaning Ladder - six levels from product identification up to purpose - from Consumer Pulse evidence and coded competitor communication, then produce a sourced ladder, factor list, laddering chains, white spaces and a strategic conclusion on which level the brand can credibly own. Use whenever the user mentions the brand ladder, levels of branding, brand meaning ladder, laddering, means-end chains, attribute-to-benefit-to-value, brand purpose, 'move up the ladder', where a brand is positioned emotionally versus functionally, or wants a ladder slide for a pitch - even if they only say 'where does this brand sit' or 'is this brand functional or emotional'. Also use when checking an existing ladder slide whose placements or scores look asserted rather than computed."
---

# Strategy ladder (Brand Meaning Ladder)

A ladder slide is persuasive because it looks measured: brands placed on rungs, a number
beside each name, an arrow to where the client should go. That is also what makes it
dangerous. If the placements were typed rather than computed, the slide is an opinion
wearing a chart's clothes, and the first client who asks "how did you get 4.1?" ends the
argument.

This skill produces a ladder where every placement can be traced to evidence and every
recommendation passes a credibility test, not an "emotional sounds better" test.

## Where this sits

**Comm scan → Consumer insights → Brand laddering → The Big Idea.** This is stage 3, and it
needs both earlier stages: coded posts (`category-creative-scan`) give the ladder the level a
brand claims, consumer evidence (`comment-analysis`) gives it the level the brand has actually
earned. The gap between the two is the finding stage 4 builds on. For the deck section — the
divider, placement, factor list, category evidence and client ladder slides, with a builder
that refuses asserted placements — use `brand-laddering`.

## The six levels

| # | Level | Consumer question |
|---|---|---|
| 1 | Product identification | "Who are you?" |
| 2 | Product attributes | "What do you have?" |
| 3 | Product benefits | "What does it do for me?" |
| 4 | Psychological associations | "What does choosing this say about me / how does it make me feel?" |
| 5 | Human values / attitude / way of life | "What does this brand believe? What life does it represent?" |
| 6 | Purpose / philosophy | "What change does this brand want to create?" |

Full definitions, examples per level (including cooking-oil and telecom worked examples) and
the boundary rules are in `references/levels.md`. Read it before classifying anything - the
boundaries are where most errors happen.

These are **levels of meaning, not mandatory stages**. The job is to diagnose where the brand
operates, not to march it towards level 6.

## The things to get right

**1. Two ladders, not one: what the brand says versus what consumers believe.**
Coded brand posts tell you the level a brand is *claiming*. Consumer Pulse evidence (comments,
reviews, research) tells you the level it has *earned*. The most useful finding is usually the
gap between them - a brand advertising at level 5 while customers argue about its level-2
basics. Build both ladders and label them. Never let a claim-ladder placement stand in for a
consumer association.

**2. Classify by what the claim does, not by its topic.**
The same subject can sit on different rungs:
- "Pakistan's first telecom, 79 years" is **level 1** - heritage as recognition and presence.
- "Built the country's backbone so your business can run" is **level 3** - heritage as proof of reliability.
- "We believe every village deserves the same connection as Karachi" is **level 5** - a stated value.

A heritage or national-pride post is not automatically level 5. It reaches 5 only when it
expresses a belief or way of life, not a fact about the brand's age or size. Put each item at
the **deepest level the evidence actually supports**, and no deeper.

**3. Every number must be reproducible.**
If a slide shows a score, a script must be able to recompute it:
- Store a `ladder_level` (1-6) and a one-line `ladder_reason` for every coded item in the
  data file (e.g. a column in `codes.csv`), not only in the slide text.
- Compute per brand: n, the distribution across levels, the **modal level** and the mean.
- **Place the brand on the rung of its modal level**, and show the mean beside it. That way the
  row and the number can never contradict each other (a 4.1 mean printed in the level-5 row
  is exactly the inconsistency to prevent). If modal and mean differ by more than one level,
  say the brand is split rather than forcing a single rung.
- If a mapping from an existing code (e.g. `claim_primary`) to a level is used, write it as an
  explicit table in the script and list the ambiguous codes that were hand-classified.

**4. Place every brand that was scanned.**
Dropping brands from the ladder silently changes the finding. If a competitor is left off,
state why on the slide or in the notes. Check specifically whether any omitted brand sits on
the rung you are claiming is empty or owned by the client.

**5. Higher is not better.**
The recommended level must be relevant, credible, distinctive and defensible. A strong,
owned benefit position often beats an unearned values claim. Recommend moving up only when
the brand has evidence of permission; otherwise recommend strengthening the level below.

## Evidence discipline

Tag every important factor:
- **OBSERVED** - directly supported by the evidence; cite it (post id, comment, count, source).
- **INFERRED** - a reasonable strategic reading of the evidence; say what it is inferred from.
- **OPPORTUNITY** - not currently associated with the brand, but relevant given consumer needs
  and category dynamics.

Never present an inference or an opportunity as an existing association. Never invent
perceptions, statistics, competitor positions or quotes. Where evidence is thin, write
"insufficient evidence" - for level 6 specifically, write **"NO CLEAR PURPOSE EVIDENCE"** unless
the purpose is relevant, credible, connected to the category, evidenced and distinctive.

## Workflow

1. **Gather inputs.** Look for Consumer Pulse output (from the `comment-analysis` skill),
   coded posts (from `category-creative-scan` / `competitor-comms-audit`) and any brand review.
   If there is no consumer evidence, you can build only the claim ladder - say so plainly and
   do not produce consumer associations.
2. **Read the evidence before classifying.** Work through the diagnostic questions in
   `references/levels.md` (what consumers know, why they choose, what they resent, what they
   want and are not getting).
3. **Classify** each coded post and each consumer theme to a level, writing the level and reason
   into the data.
4. **Compute** per-brand distributions with a script; save the table (e.g.
   `workspace/<scan>/ladder_levels.csv`). Check that every scanned brand is present.
5. **Compare competitively:** table stakes, crowded levels, occupied territories, white spaces,
   and where the client has permission to move.
6. **Write the output** below. Then check it: does every placement trace to the table, does
   every OBSERVED tag have a citation, is any omitted brand hiding on a "vacant" rung?

## Output

Produce these sections, in this order:

**A. Brand diagnosis** - 3-5 sentences, decided, not hedged.

**B. Brand Meaning Ladder** - for each of the six levels: level; consumer question; current
brand associations; supporting evidence; strength (Strong / Moderate / Weak / Not established);
potential opportunity. Show the claim ladder and the consumer ladder side by side where both
exist.

**C. Factor list** - per level, separated into current factors, potential factors and
unsupported factors. Build it for the **category first**, then the brand:

- **Start from the framework's own list for each level** (`references/levels.md` - e.g. the
  Level 5 territories: progress, family wellbeing, freedom, equality, ... social mobility).
  Keep every factor from that list; do not silently drop the ones that do not fit.
- **Sort each factor for this category:**
  - **Current** - seen in the category's communication (the coded posts). Only mark a factor
    current if you can point to posts; if it is a judgement call, flag it for review.
  - **Potential** - relevant to this category but not yet claimed by anyone.
  - **Unsupported** - little link to this category (e.g. "healthy living" or "packaging" for a
    connectivity service). This is where non-fitting framework factors go.
- **Add category-specific factors only when evidence calls for them** (the framework's lists
  are "possible territories include", not exhaustive), and mark every addition with **†** so
  nobody mistakes it for a framework factor. Typical sources: the consumer pulse (what
  customers judge on) and the category scan.
- For Level 6, if no brand in the category states a purpose, write "No clear purpose
  evidence in the category" under current.

**D. Laddering chains** - 5-10 chains, only strategically plausible ones:

```
ATTRIBUTE
↓
FUNCTIONAL BENEFIT
↓
PSYCHOLOGICAL ASSOCIATION
↓
HUMAN VALUE / LIFESTYLE
↓
POTENTIAL PURPOSE
```

A chain may stop early if the evidence stops. A chain that breaks at a rung the brand does not
deliver (e.g. "reliable broadband" when consumers report outages) is a finding, so mark the
break rather than hiding it.

**E. Brand white space** - 3-5 areas, each with: opportunity; why consumers may care; current
evidence; brand permission; competitive clutter; risk.

**F. Strategic conclusion** - answer directly:
1. Where does the brand currently sit (claimed and earned)?
2. Which level is most strongly owned?
3. Which level is overcrowded in the category?
4. Which higher level has the strongest credible opportunity?
5. What evidence would we need to validate that opportunity?

**G. Method note** - the level mapping, n per brand, any hand-classified codes, brands excluded
and why. This is what lets a slide say "computed" honestly.

## For a deck

Tell the ladder story in this order, so the client sees how the framework works in their
category before seeing where their brand should stand:

1. **The factors at each level (the category)** - rows are levels 6 down to 1; columns are
   Level + consumer question | Current | Potential | Unsupported. The standfirst defines the
   three columns and the † mark. No brand placements on this slide.
2. **How the ladder works in the category (the evidence)** - per level: what brands claim
   (with post counts and leading brands), what customers judge on, and what is open.
   Footnote that a coded claim can sit at more than one level, so counts show where factors
   appear, not per-level totals.
3. **The client's ladder and recommendation** - per level: what the client says, what
   consumers say, and the placement (e.g. hold / prove / place here / next / later / not now).

Slide rules:
- Rows run from level 6 at the top down to level 1.
- When brands are placed on rungs, each appears on its modal rung with `Brand (mean, n)`, and
  the footnote states "mean level across n coded items; placement = modal level" and points
  to the computed table.
- Mark claimed and earned positions for the client separately.
- Check that six rows fit above any conclusion band; long factor lists (typically Level 4
  potential) need a smaller type size rather than a taller row.
- Save as a new deck version; never overwrite an existing one.
