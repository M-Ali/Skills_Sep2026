# Worked example - PTCL, Pakistani fixed broadband (September 2026)

This is the ladder section this skill was distilled from: slides 23-27 of
`pakistan_fixed_broadband_category_creati_2026-09-11-v14_S.pptx`. The inputs were 336 coded
Instagram posts across 14 brands and 976 YouTube comments. `assets/example_spec.json` holds
the same content in builder form, corrected as described in the last section below.

## Slide 23 - divider

"The Brand Meaning Ladder." / "A simple way to understand how consumers see a brand - from
what it is and does, to what it means to them." / "From functional benefits -> to emotions ->
to values and purpose."

## Slide 24 - placement

| Level | Brands | Marker |
|---|---|---|
| 6 Mission / philosophy | Nobody in this category. | |
| 5 Human values | PTCL - claims heritage or nation, in the pride register | WHERE PTCL IS TALKING |
| 4 Psychological | Transworld (3.8), Ufone (3.9) - household truths, nostalgia | THE DIFFERENTIATION GAP |
| 3 Product benefits | Tapmad (3.0), Multinet (3.2), Jazz Business (3.3) - problem-led | WHERE PTCL MUST EARN |
| 2 Product attributes | StormFiber (2.6), Zong (2.8), Optix (2.9), Jazz (2.9) - speed, price, coverage | WHERE THE CATEGORY SITS |
| 1 Name only | Nobody - every brand has moved past recognition. | |

Conclusion: "PTCL is communicating roughly two levels above where it is delivering - and
the ladder does not let a brand skip."

## Slide 25 - factor list (abridged)

- **L6:** current = no clear purpose evidence. Potential = democratizing technology,
  connecting people and communities, enabling economic opportunity... Unsupported = making
  healthcare accessible...
- **L5:** current = national development, responsibility, innovation. Potential = progress,
  inclusion, community... fairness †. Unsupported = healthy living.
- **L4:** current = pride, modernity, aspiration, belonging. Potential = smart choice,
  control, confidence... respected as a customer †.
- **L3:** current = better connectivity, reliability, entertainment at home †, value for
  money †. Potential = peace of mind, a bill that stays predictable †, a fault fixed without
  pleading †, leaving without a penalty †.
- **L2:** current = speed, fibre, coverage, price, packages, devices †. Potential = proof of
  speed (independent tests) †, published price terms †, published fault-response time †.
- **L1:** current = name, logo, heritage, availability. Potential = distinctive assets, recall.

Conclusion: "Current factors cluster at levels 1-3. The unclaimed territory sits at levels
4-6 - but higher is not better."

## Slide 26 - category evidence (abridged)

- **L3:** brands claim "business keeps running (50: Multinet 20, Jazz Business 16, Wateen 13);
  entertainment at home (49: Tapmad 23, Shoq 14); value for money (31)". Customers judge on
  "work, study and stream without breaks; a fault fixed quickly; a bill that stays
  predictable". Open: "a bill that does not change without notice; a fault fixed without
  pleading; a clean exit".
- **L2:** open = "Proof - 0 of 336 posts cite a speed test".
- **L1:** customers name PTCL 92, Ufone 89, Jazz 41 times; open = "table stakes".

Conclusion: "The category talks at levels 1-3. Nobody makes the relationship itself a
benefit, and that is where customers judge hardest."

## Slide 27 - client ladder

Computed from `ptcl_ladder_levels.csv`: PTCL n = 24, mode L1, mean 2.4.

| Level | Says | Heard | Placement |
|---|---|---|---|
| 6 | 0 posts | No clear purpose evidence | NOT NOW - no permission yet |
| 5 | 2 - water CSR, Humanitarian Day | Not established | LATER - fairness, once proven |
| 4 | 6 - hockey and esports pride | Negative | NEXT - respected, in control |
| 3 | 1 - "the one constant across every home" | Weak - "if your location is good" | **PLACE PTCL HERE - fair terms you can count on** |
| 2 | 5 - device retail, Flash Fiber | Mixed | PROVE - publish terms and speed |
| 1 | 10 - 79-years teasers, national days | Strong - most-mentioned brand | HOLD - heritage = recognition |

Conclusion: "Place PTCL at Level 3: fair terms you can count on. Nobody in the category claims
it, it answers the customer pulse directly, and PTCL can prove it with commercial decisions."

## The mistakes this section shipped with (why the skill has its rules)

1. **Slide 24 and slide 27 disagree about the client.** Slide 24 put PTCL on Level 5 with a mean
   of 4.1 that was typed into a YAML file, never computed. Slide 27 computed mode L1, mean 2.4
   from the classified posts. PTCL's hockey and esports posts are Level 4 and its heritage
   posts are Level 1 recognition, not Level 5 values. The honest slide-24 row is "PTCL (2.4) -
   split: L1 heritage-as-recognition (10 posts) and L4 pride through sport (6)". The
   "communicating above where it delivers" argument still stands: L4 claims against L2-3
   customer judgement. Hence: compute placements, place on the modal rung, show the mean, and
   have the builder cross-check slide 2 against the table.
2. **Only PTCL was classified post by post.** The other brands' means on slide 24 had no file
   behind them. Hence: classify every scanned brand.
3. **Slide 24 overflowed.** Rows started at y1.95 on a 0.81 in step, so the Level 1 row ran
   under the conclusion band and the footnote fell off the slide at y7.42. Hence: fixed row
   geometry ending at 6.50, and rendering every slide before handover.
4. **The client deck repeated the error after the internal deck was fixed.** Its one-slide
   ladder was written by hand from the internal slides, so "heritage and national pride" stayed
   at Level 5 while the corrected internal slide had moved it to Level 1. Hence: build the
   client slide from the same computed table, and check both when a placement changes.
5. **The consumer "Heard" column came from PTCL-mentioning comments only.** Reading the whole
   corpus later showed the category-wide pattern was broader: distrust of any claim about
   internet service. Hence: the rule to label filtered evidence, and to read the whole corpus
   for category-level cells.
