---
name: lead-analysis
description: Analyse leads from the bdleads database with every statement cited to its source - deep-dive a single tender or company signal (read the PPRA tender notice/document or PSX filing PDF, extract scope, eligibility, deadline, submission method), or summarise a set of leads by agency, sector, signal and urgency into a sourced brief. Use whenever the user asks "what's in this tender", "is this worth bidding", "what does this filing say", "summarise this week's leads", "what's the picture for the media agency", "brief me on Meezan Bank", "which sectors are active", or wants a lead turned into a go/no-go note or pitch brief - even if they only paste a lead id or a tender title.
---

# Lead analysis

Turn stored leads into analysis the BD team can act on, **where every sentence that
states a fact points to the source it came from**. Leads are only useful if directors
can trust them. An analysis that mixes sourced facts with plausible guesses is
worse than a short one, because nobody can tell which part is which.

## Ground rules (apply to every output)

1. **Cite inline.** After each fact, add a numbered marker `[1]` and list the sources
   at the end: `[1] <source_name> — <url> (fetched <date>)`.
2. **"Not stated" is an answer.** If the tender doesn't give a budget, write
   "Budget: not stated in the notice [1]". Never estimate one.
3. **Separate interpretation.** Put your judgement (fit, risks, recommendation) under a
   heading such as **Assessment (our view)**. It may reason from the cited facts, but
   it must not introduce new facts.
4. **Quote, don't paraphrase, the critical lines** (deadline, eligibility, submission
   method, bid security). People copy these into bid checklists.
5. If a document can't be fetched or read (scanned image, 403), say so and work from
   the stored excerpt, marked as such.

## A. Deep-dive on one lead

1. Load it:
   ```bash
   uv run bdleads show <lead_id>
   ```
   (If the user gave a title, find the id with `uv run bdleads list --text "<words>" --include-expired`.)
2. Read the evidence list. For tenders it usually has three entries:
   - the PPRA tender-details page (description, organisation, closing time),
   - **Download Advertisement**: the newspaper notice PDF,
   - **Download Tender Document**: the bidding document, when published.

   For PSX leads it has the company page and the filing PDF.
3. Fetch the documents. They are public, so use WebFetch for HTML pages. For PDFs,
   download with `curl -L -o <scratchpad>/doc.pdf "<url>"` and read the file (use the
   pdf skill for long or scanned documents).
4. Extract into this template. Fill each line only from a source, or write "not stated":

```
## <Title> — <Organisation>
Lead <id> · score <n> · status <status>

**What they want:** <scope in 1–3 sentences> [n]
**Domain / service:** <domain> / <service> · best-fit BU <BU> (rule match: <matched keyword>)
**Deadline:** "<verbatim closing date/time>" [n]
**Submission:** "<verbatim: EPADS / physical / email>" [n]
**Eligibility / prequalification:** "<verbatim key criteria>" [n]
**Bid security / fees:** "<verbatim>" or not stated [n]
**Budget:** <figure> or not stated [n]
**Contact:** <as printed> or not stated [n]

### Assessment (our view)
- Fit with <BU / service>: ...
- Risks / gaps: ... (e.g. "requires 5 years of government media buying, per [2]")
- Recommended next step: ...

### Sources
[1] ...
```

For a **PSX filing**, use: what changed (role, person, effective date, as stated), why it
matters for agency relationships (Assessment), and the next step (e.g. "watch for an
agency review in the next 3–6 months"). The 3–6 month window is a BD rule of thumb, so
keep it under Assessment, not as a fact.

For **"Material Information"** filings, the title says nothing. Read the PDF before
saying anything about the content. If you can't read it, say the content is unknown.

## B. Summary of many leads

1. Pull the set as JSON:
   ```bash
   uv run bdleads list --json --limit 200 [--agency X] [--sector Y]
   ```
2. Count with a short Python snippet run via `uv run python`, not by eye, so the
   numbers are exact: by agency, kind, sector, signal, and deadlines in the next 7/14/30 days.
3. Write:
   - **Headline numbers** (from the counts, with the date the data was fetched).
   - **Top leads** (up to 10, by score), each with its source link.
   - **Patterns**: e.g. "6 of 8 open tenders are from federal bodies", "3 CEO changes in
     banking since August". Every pattern must be checkable against the listed leads.
   - **Gaps**: sources not run recently, IMAP not configured, sectors with no leads.
     Data that is absent is a finding too. Don't fill gaps with general market commentary.

## Output location

For anything longer than a screen, also save a Markdown file to `exports/` (e.g.
`exports/analysis_<lead_id>.md`) so it can be shared, and tell the user the path.

## Related skills

- Finding leads first: **lead-search**. Prioritising and grouping: **lead-triage**.
- For a full tender response plan, hand the downloaded tender document to the
  **brief-to-plan** skill if it is available.
