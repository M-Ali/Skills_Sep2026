# Theme taxonomy

A starter taxonomy for coding review text. The five **groups** generalise across
categories; the **words** do not - rewrite the patterns for the category you are
working in, using the vocabulary that actually appears in the corpus.

## How to build the pattern list

Read 50 reviews before writing a single pattern. Then read the 20 most
distinctive words from the low-star set (log-odds, see SKILL.md) and make sure
every one of them lands in a theme. Anything left over is either a new theme or
noise.

Keep patterns as regex, case-folded, and prefer word boundaries (`\bsmall\b`) so
"small" does not match "smaller-than" oddly or "smallpox".

## The five groups

### Job - what the product was hired to do

The problem the customer was trying to solve. These usually rate *above* average
when they appear, because a review that names the job is a review from someone
the product worked for.

Examples from an intimate-care catalogue: odour control, pH and infection,
dryness, cycle and cramps, feeling clean, confidence and intimacy.

Transferable prompt: what would the customer have typed into a search box the
week before they bought?

### Experience - what it was like physically

Scent, texture, taste, irritation or reaction, noise, fit, weight. These are the
themes most likely to be **bimodal** - the same attribute is the most praised
thing about a product and the most complained about. When that happens the
answer is usually a variant, not a reformulation, and it is worth saying so.

### Friction - what cost money or goodwill

Price and value, size and how long it lasts, shipping and delivery, packaging
and leaks, customer service, subscription and billing.

This group is where the actionable findings almost always are, because these are
operational problems with named owners rather than product problems needing R&D.

### Outcome - did it work

Two themes, and the order they are tested in matters:

- `efficacy_negative` - test this **first**. Patterns like
  `(?:not|no|never|didn'?t|doesn'?t|don'?t|wasn'?t)\s+(?:\w+\s+){0,2}work`,
  "no difference", "nothing changed", "waste of money", "not what it says",
  "false advertising", "just another <category noun>".
- `efficacy_positive` - test second and **exclude** any row that matched the
  negative theme, or "it didn't work" scores as a positive on the word "work".

This pair produces the largest rating gap in almost every corpus, usually well
over a full star, and it is the theme that identifies the product to fix first.

### Loyalty - the signals worth more than the star

Will buy again / already has, recommends it, bought it as a gift. These are
worth counting separately because they are the sentences that can be quoted
back in marketing, and because a high repurchase-intent count on a product with
a mediocre rating is a very different situation from a low one.

## Reporting the taxonomy

Always publish, in the method section:

- how many themes,
- the minimum-mentions floor used for the pain-point ranking,
- the **coverage share** - what proportion of reviews with text matched at least
  one theme.

Coverage of 55-70% is normal and healthy. The unmatched remainder is mostly
short affirmations ("love it", "great product", "thank you") that carry no
codeable subject. Reporting the number honestly is what makes the coded
percentages credible; hiding it invites the question you cannot answer.

## Worked example of a gap table

| Theme | Mentions | Mean rating | Gap vs 4.87 | Under 4★ |
| --- | --- | --- | --- | --- |
| Said it did not work | 16 | 3.25 | −1.62 | 50% |
| Size / how long it lasts | 60 | 4.22 | −0.65 | 22% |
| Price & value | 64 | 4.34 | −0.53 | 17% |
| Customer service | 47 | 4.51 | −0.36 | 15% |

Read it as: mention count tells you how *often* a subject comes up; the gap
tells you what it *costs* when it does. Rank on the gap, then use the mention
count to decide whether it is worth a project or a footnote.
