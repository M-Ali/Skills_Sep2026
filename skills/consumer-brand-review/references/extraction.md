# Extraction traps

Source documents resist reading in specific, recurring ways. Each trap below has
cost real time on a real review, and each looks like an absence of information
rather than a failure to extract — which is what makes them dangerous. You do
not get an error; you get a plausible, incomplete answer.

## Contents

- [PDFs with glyph-encoded fonts](#pdfs-with-glyph-encoded-fonts)
- [PowerPoint content inside grouped shapes](#powerpoint-content-inside-grouped-shapes)
- [Slides that are images](#slides-that-are-images)
- [Word documents with content in tables and text boxes](#word-documents-with-content-in-tables-and-text-boxes)
- [Sites that need a real browser](#sites-that-need-a-real-browser)
- [Wrong-entity pages](#wrong-entity-pages)
- [Open files on Windows](#open-files-on-windows)

---

## PDFs with glyph-encoded fonts

**Symptom:** extracted text is full of tokens like `/MT73/MT110/MT115` instead of
words, or comes back empty from a document that plainly has text.

**Cause:** the PDF embeds a subset font with a non-standard encoding. Extractors
emit glyph names rather than characters.

**Fix:** the numbers are usually ASCII decimal. Substitute them.

```python
import re
def decode(t):
    return re.sub(r"/MT(\d+)", lambda m: chr(int(m.group(1))), t)
```

Check the mapping on a page whose content you can guess — a title page or a
contents list — before trusting it across the document. If the prefix is not
`/MT`, look at what it is; the pattern is the same.

**Do not conclude a document is unreadable without trying this.** A 166-page
industry year book looked like binary noise and was fully recoverable with the
substitution above.

## PowerPoint content inside grouped shapes

**Symptom:** slides come back with only a title, or a heading and a footnote,
while the slide obviously carries data.

**Cause:** naive extraction walks `slide.shapes` and stops. Summary panels,
callouts and stat blocks are usually **grouped** shapes, and their text is one
level down.

**Fix:** walk recursively.

```python
def walk(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == 6:          # GROUP
            yield from walk(sh.shapes)
```

**This one is quietly expensive.** A media proposal read at top level gave up its
rate tables and looked complete. Re-read recursively, it also contained the
creative specification the whole plan assumed — spot duration, advertisement
sizes, publication count — which changed what the client needed to produce.
Nothing in the first pass suggested anything was missing.

## Slides that are images

**Symptom:** a slide has a title and a picture and no other text.

Extract the image and **look at it**. It may be decorative clipart, a background
texture, or the entire content of the slide.

```python
for i, s in enumerate(prs.slides, 1):
    for j, sh in enumerate([x for x in s.shapes if x.shape_type == 13], 1):
        (out / f"slide{i:02d}_{j}.{sh.image.ext}").write_bytes(sh.image.blob)
```

Note the empty case too: several slides headed with a promise and containing no
content is itself a finding worth raising, not a gap in your reading.

## Word documents with content in tables and text boxes

Reading `.docx` paragraphs through a document library commonly skips text inside
tables and text boxes. Going at `word/document.xml` directly picks them up:

```python
import zipfile, re, html
with zipfile.ZipFile(path) as z:
    xml = z.read("word/document.xml").decode("utf-8")
xml = re.sub(r"</w:p>", "\n", xml)
xml = re.sub(r"<[^>]+>", "", xml)
text = html.unescape(xml)
```

Word encodes some punctuation in the private-use range (U+F000–U+F0FF).
Normalise apostrophes and dashes on the way out, or comparisons against the
source will fail for invisible reasons.

## Sites that need a real browser

Many corporate sites and most social platforms return little or nothing to a
plain fetch. A headless browser gets the rendered page.

Two things worth knowing:

- **Some sites return 403 to automated retrieval regardless.** Say so in the
  review and name the weaker source you used instead. Never present a quote you
  could not read directly as though you had.
- **Auth walls are not uniform across a site.** A platform may wall its feed
  endpoint while still rendering recent content on the profile or company page
  to a logged-out visitor. Try the adjacent URL before concluding it is closed.

## Wrong-entity pages

**Symptom:** a page loads, looks right, and the numbers are implausible — a
global institution with 479 followers.

**Cause:** you guessed the URL slug, and landed on a fan page, a regional
subsidiary, or an unrelated organisation with a similar name.

**Fix:** verify identity from the page itself — description, size, location —
not from the fact that it loaded. Search for the entity rather than constructing
its address. Slugs with apostrophes, ampersands and punctuation are especially
easy to get wrong.

## Open files on Windows

**Symptom:** `PermissionError: [Errno 13]` writing an output file.

**Cause:** Office holds an exclusive lock while a document is open.

**Fix:** do not wait. Write to a dated filename instead, and say clearly which
file is current:

```
Report 2026-08-29.docx     <- current
Report.docx                <- stale, locked
```

Build every generator so the output path can be overridden, and a locked file
never blocks progress.
