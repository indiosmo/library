# Plan: LCC schedule database & ISBN-to-call-number lookup

Status: preliminary. Phase A is well-scoped and shippable independently;
later phases depend on a few human decisions called out at the end.

## Goal

Build a one-time, local SQLite-backed lookup infrastructure that lets the categorizer:
- Map any LCC notation (`QA76.73.P98`) to a full schedule walk that includes range-node parents (`Q -> QA -> QA75-QA76.95 -> QA76.7-QA76.76 -> QA76.73 -> QA76.73.P98`).
- Resolve ISBN -> LoC-assigned call number via an authoritative source.
- Cache lookups so re-runs and `--reshelve` don't re-hit the network.

Pipeline integration follows in Phases C-E; this plan stays focused on the schedule + lookup layer.

---

## A. The LCC schedule database

### A.1 Source data — what's freely available and machine-parseable

I checked four paths and verified what they actually expose:

1. **`loc.gov/aba/publications/FreeLCC/`** — print-ready PDFs only (44 schedule volumes, May 2024 data selection). Parsing PDFs reliably to recover hierarchical depth is hard. Some schedules have a 2025 revision (e.g. `LCC_Q2025TEXT.pdf`). [FreeLCC](https://www.loc.gov/aba/publications/FreeLCC/freelcc.html)

2. **MARC 21 Classification at `loc.gov/marc/classification/`** — this is the *spec* for how classification data is encoded; the spec page does not itself host the LCC dataset. Field 153 is what we'd parse: subfield `$a` = single number or start of range, `$c` = end of range, `$h` (repeating) = each ancestor caption in order, `$j` = the caption for this entry. That gives notation, range, name, AND the full caption hierarchy in a single field — much friendlier than DDC/MARC bib data. [MARC 21 153](https://www.loc.gov/marc/classification/concise/cd153.html)

3. **ClassWeb / ClassWeb Plus** — paid subscription. CDS (Cataloging Distribution Service) sells full LCC in MARC 21 / MARCXML with a weekly update service. **Out of scope** unless the user is willing to license. [ClassWeb](https://www.loc.gov/cds/classweb/)

4. **`id.loc.gov` Linked Data Service** — this is the underrated freely-licensed option. LCC is published as SKOS/RDF + MADS/RDF; bulk downloads are offered as gzipped RDF/XML, Turtle, JSON-LD, and N-Triples. Each LCC entry has its own URI (e.g. `http://id.loc.gov/authorities/classification/QA76.73`) and links broader/narrower concepts. Updated continuously. **This is the recommended primary source.** [id.loc.gov](https://id.loc.gov/) [downloads](https://id.loc.gov/download/) (cited from search results — direct fetches were blocked from the planning sandbox by Cloudflare's JS challenge; see A.5 risk).

5. **GitHub third-party scrapes**, in order of usefulness:
   - **`thisismattmiller/lcc-pdf-to-json`** — outline-level only, JSON shape is `{id, parents[], prefix, start, stop, subject}`. Verified live: covers ranges as first-class entries with explicit `parents`. Outline depth, not full schedule. Useful as a fallback or sanity check, not as the primary source. [repo](https://github.com/thisismattmiller/lcc-pdf-to-json)
   - **`edsu/lcco`** — `lc_class.txt` is 7,828 lines of indented text scraped by Karen Coyle from PDFs. Outline-depth only, but goes a few levels deeper than the top-level outline and includes range entries. Verified raw fetch (size & content). Good fallback source if id.loc.gov bulk isn't workable. [repo](https://github.com/edsu/lcco) | [raw](https://raw.githubusercontent.com/edsu/lcco/master/lc_class.txt)
   - `sethwoodworth/LCC` — minimal, only 4 commits; not a usable data source. Skip.

### A.2 Recommendation: dual-source with a fallback ladder

**Primary**: id.loc.gov SKOS/RDF bulk download. Parse with `rdflib` (extra dependency) or even line-oriented N-Triples parsing for speed. SKOS gives us `skos:notation`, `skos:prefLabel`, `skos:broader`, `skos:narrower`, `madsrdf:classification`, scheme membership, and (importantly) ranges are themselves first-class concepts with their own URIs.

**Fallback**: `thisismattmiller/lcc-pdf-to-json` (`results.json`) committed-or-vendored as a static asset. It's outline-depth only, which is enough to get the `Q -> QA -> QA75-QA76.95 -> QA76.7-QA76.76 -> QA76.73` skeleton; we'd lose the leaf cutter-table topical entries (e.g. `QA76.73.P98 Python`) at this depth — which means the deepest "single notation" leaves often won't have a matching schedule entry. Two ways to live with that:
   - Truncate folder chains at the deepest schedule entry we *do* find and treat the original notation as a trailing folder with a generated label inferred from the LoC catalog record (the 050-derived caption from the agent or a topical lookup).
   - Keep the bulk-source path as Phase A.1 and add the leaf augmentation in a later phase.

Decision is deferred (see "Open questions"); plan ahead with primary path.

### A.3 Schema for the SQLite database

Single file at e.g. `scripts/data/lcc.sqlite` (committed; ~tens of MB compressed; check exact size before committing — see A.5). Two tables, plus a small metadata table.

```sql
-- One row per schedule entry. Range entries are first-class.
CREATE TABLE schedule (
  id              INTEGER PRIMARY KEY,
  notation        TEXT NOT NULL,        -- "QA76.73", "QA75-QA76.95", "Q"
  class_letter    TEXT NOT NULL,        -- "Q" — first letter(s), used to filter
  subclass        TEXT,                 -- "QA" — letter prefix without numbers
  start_number    REAL,                 -- numeric portion start (for range matching)
  end_number      REAL,                 -- equal to start when not a range
  is_range        INTEGER NOT NULL,     -- 0/1 boolean
  caption         TEXT NOT NULL,        -- "Calculating machines and electronic computers"
  depth           INTEGER NOT NULL,     -- 0 for class, 1 for subclass, ...
  parent_id       INTEGER REFERENCES schedule(id),
  source_uri      TEXT,                 -- id.loc.gov URI when present
  UNIQUE (notation)
);

CREATE INDEX idx_schedule_subclass    ON schedule(subclass);
CREATE INDEX idx_schedule_range_match ON schedule(class_letter, start_number, end_number);
CREATE INDEX idx_schedule_parent      ON schedule(parent_id);

-- Free-text search over captions for the agent's "find me the right slice" use case.
CREATE VIRTUAL TABLE schedule_fts USING fts5(
  notation, caption, content='schedule', content_rowid='id'
);

CREATE TABLE meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
-- meta rows: source_url, source_fetched_at, source_revision, schema_version
```

Notes on the design:
- **`start_number` / `end_number` as REAL** so `QA76.73` (76.73) sorts inside `QA76.7-QA76.76` (76.7..76.76) without string trickery. Cutter-bearing leaf entries don't end up in the schedule table; cutters only appear in user-supplied call numbers (see A.4).
- **`parent_id` is the authoritative hierarchy edge** — copied straight from `skos:broader`. Do *not* try to derive parent purely from notation arithmetic; the hierarchy is curated and sometimes skips intermediate ranges that don't exist in the schedule.
- **`source_uri`** lets us hyperlink each `_index.md` entry back to id.loc.gov for the curious — cheap to keep.
- **`schedule_fts`** is the data the index-generator and the categorizer's prompt can query for "captions matching `python OR programming language`" (see C.2).

### A.4 Walking a call number to a folder chain

Given an input like `QA76.73.P98` (cutter dropped per ADR — see A.4.b):

1. **Strip the cutter** — split on the first dotted decimal that's followed by an alphabetic Cutter letter. Regex sketch: `^([A-Z]{1,3})(\d+(?:\.\d+)?)(?:\.[A-Z]\d+)?(?:\s+\d{4})?$` — class letters, base number (with optional decimal extension), optional cutter, optional date. Keep the class letters + base number; discard the rest. So `QA76.73.P98 1997` -> `(QA, 76.73)`.

2. **Find the deepest matching range** — `SELECT id, notation, parent_id FROM schedule WHERE subclass = 'QA' AND start_number <= 76.73 AND end_number >= 76.73 ORDER BY (end_number - start_number) ASC LIMIT 1`. The smallest enclosing range is the leaf in the schedule.

3. **Walk parents** — recursive CTE up `parent_id` to the class root.

4. **Render folder names** — slugify each captured `(notation, caption)` pair with a stable convention. Suggested format: `<notation>-<kebab(caption)>`, e.g. `QA75-QA76.95-calculating-machines-and-electronic-computers`. Class roots get `<notation>-<kebab(caption)>` too: `Q-science`. The notation prefix preserves sortability and is the load-bearing identifier; the caption is the human-friendly part.

5. **Special rule for cutter leaves** — when an item's notation includes a cutter that *is* a topical Cutter (e.g. `QA76.73.P98 Python`), id.loc.gov *may* expose the cutter as a narrower concept; if it does, the leaf folder gets created. If not, the leaf is the deepest range and the cutter is dropped per the ADR. Verify with a few sample lookups during Phase A development.

#### A.4.b Cutter-handling clarification

Per the ADR, "Cutter numbers are dropped — stop at the topical portion of the call number." The cutter `.P98` for "Python" is *topical* (a translator-table cutter encoding the language name) — those should ideally be kept; the cutter `.K64` for "Knuth" (an author cutter) should be dropped. Distinguishing the two reliably is non-trivial: the schedule itself encodes which cutter ranges are topical (via "Translation Tables" / "By language, A-Z" instructions). For Phase A we should:
- Implement the simple rule first: drop everything after the first cutter.
- Flag entries where the schedule's caption hints at a topical cutter table ("By language, A-Z", "Special, A-Z", "By topic, A-Z") so a later phase can opt-in to keeping those.

### A.5 Build-time pipeline (offline, one-time)

A new `scripts/build_lcc_db.py` that:
1. Downloads the id.loc.gov LCC bulk dump (RDF) into a `scripts/data/cache/` directory (gitignored).
2. Parses, normalizes, and writes `scripts/data/lcc.sqlite`.
3. Validates by walking ~10 known notations against expected hierarchies (test fixtures).

This script is not part of the runtime pipeline — it's run on demand when the schedule needs refreshing. The DB itself is committed (it's the source of truth users actually consume).

**Deferred to human decision**: do we commit the sqlite file (predictable, no network needed at runtime) or treat it as a build artifact (smaller repo, requires Make-style first-run)? Recommendation: commit it; the sqlite file is in the low tens of MB and changes infrequently.

#### Verification gap & risks (A.5 risks)

- **Cloudflare gating**: `www.loc.gov` and `id.loc.gov` both serve a JavaScript challenge to non-browser User-Agents (verified live during exploration — both `curl` and the WebFetch tool hit the challenge page). The bulk RDF *download* URLs (under `id.loc.gov/download/...`) historically have served as direct files; some users report needing a real browser-derived UA or a one-time manual download. Plan accordingly: the build script may require a manual one-time download with the file dropped into the cache directory, rather than a fully automated fetch. **This needs to be confirmed with a real download attempt before committing to id.loc.gov as primary.**
- **`lx2.loc.gov:210/lcdb` (SRU)** is *not* Cloudflare-gated (verified live). That stays viable for Section B.
- **License**: LCC schedules are US Government work; treated as freely redistributable. ClassWeb T&Cs only bind the value-add interface, not the data itself. The id.loc.gov data is published under terms compatible with redistribution — plan flags but doesn't dwell.
- **Update cadence**: LoC publishes weekly classification updates on ClassWeb; id.loc.gov bulk dumps are refreshed periodically. We don't need bleeding-edge freshness. A yearly rebuild is fine; record the source date in `meta.source_fetched_at`.

---

## B. ISBN -> call number lookup

### B.1 Recommended primary: LoC SRU at `lx2.loc.gov`

**Verified live** during exploration: `http://lx2.loc.gov:210/lcdb?version=1.1&operation=searchRetrieve&query=bath.isbn=9780201896831&maximumRecords=1` returns MARCXML containing field `050` `(QA76.6 .K64 1997)` for The Art of Computer Programming. No auth, no Cloudflare gate, runs on port 210. [LC SRU servers](https://www.loc.gov/standards/sru/resources/lcServers.html)

The MARCXML record is rich: it includes 020 (ISBN), 050 (LCC call number, the load-bearing field), 082 (Dewey), 100 (author), 245 (title), 260 (publisher/year), 650 (subjects). All useful for the categorizer prompt downstream.

Etiquette: LoC documentation suggests "no more than 10 requests per minute" for catalog-related programmatic access (LCCN Permalink guideline; SRU likely shares the same posture). Plan a 6 s sleep between calls or a token bucket; cache aggressively (B.3).

Parse with a minimal MARCXML parser — `xml.etree.ElementTree` plus a 30-line walker is sufficient. `pymarc` has SRU/MARCXML support but adds a dependency just for this; defer unless we need MARC bib data more broadly. [pymarc](https://pypi.org/project/pymarc/)

### B.2 Fallback: Open Library `/isbn/<isbn>.json`

**Verified live**: `https://openlibrary.org/isbn/9780201896831.json` returns JSON with `lc_classifications: ["QA76.6 .K64 1997", "QA76.6.K64 1997", "QA76.6"]` and `dewey_decimal_class: ["005.1"]` and an `lccn` field. Rate limit per Open Library docs: 1 req/sec unidentified, 3 req/sec when sending `User-Agent` + email — we should always send our UA `library-pipeline/0.x (indiosmo@gmail.com)`.

Fallback is needed because:
- LoC SRU sometimes returns nothing for non-US books or pre-LCCN editions.
- LoC SRU may rate-limit or be down.
- Open Library's `lc_classifications` is community-aggregated and includes LCC values from non-LoC libraries — useful when LoC itself never assigned one.

Strategy: try SRU first; on empty or transport error, try Open Library.

### B.3 ISBN extraction in the existing pipeline

Currently `scripts/document_extract.py` returns a *text excerpt*, no structured metadata. ISBNs aren't extracted anywhere.

Plan:
- Add `extract_document_metadata(path) -> dict` returning `{"isbn": [...], "title": ..., "title_page_text": ...}`.
- For PDFs: scan the first 5-10 pages of text for ISBN-13 / ISBN-10 patterns (`\b97[89][0-9]{10}\b` and a checksum-validating ISBN-10 regex). The book's copyright page typically lists multiple ISBNs (paperback, hardcover, ebook); collect all and prefer ISBN-13.
- For EPUBs: pandoc already runs; better, peek into the EPUB's `META-INF/container.xml` -> `package.opf` -> `<dc:identifier opf:scheme="ISBN">`. EPUB metadata is more reliable than scanning text.
- For HTML / MOBI / DJVU: skip; ISBN extraction is best-effort.

Extracted ISBNs are passed through to the categorizer prompt builder, which calls B.4.

### B.4 Caching layer

Same SQLite file as the schedule DB. New table:

```sql
CREATE TABLE isbn_lookup (
  isbn          TEXT PRIMARY KEY,         -- ISBN-13 normalized (no hyphens)
  call_number   TEXT,                     -- raw 050 / lc_classifications value
  notation      TEXT,                     -- normalized (cutter stripped) e.g. "QA76.73"
  source        TEXT NOT NULL,            -- 'loc-sru' | 'openlibrary' | 'none'
  raw_record    TEXT,                     -- JSON blob of structured metadata from the source
  fetched_at    TEXT NOT NULL             -- ISO 8601
);
```

Negative caching: when both sources return nothing, write a row with `call_number = NULL`, `source = 'none'`, so we don't keep retrying. Add a `--refresh-isbn-cache` flag to the categorizer for occasional sweeps.

Single SQLite file keeps deployment simple (one path to back up, one schema migration story). It's a different access pattern from the schedule data (writes happen, reads are point lookups), but the volumes are tiny — keep them together.

---

## C. Integration with the existing pipeline

The seam in `categorize.py` is concentrated. Three things change:

### C.1 Replace `normalize_shelf` with `normalize_lcc_shelf_path`

`scripts/categorize.py:normalize_shelf` (lines 791-802) currently enforces single-segment kebab-lowercase. Replace with a function that:
- Takes the agent's response or a lookup result and returns a `Path` of folder segments (already in `<notation>-<kebab-caption>` form, see A.4).
- Validates every segment matches the expected pattern `[A-Z]{1,3}\d*(?:\.\d+)?(?:-[A-Z]{1,3}\d*(?:\.\d+)?)?-[a-z0-9-]+`.
- Refuses paths that don't terminate at a known schedule entry (forces the agent's outputs through the schedule).
- Returns `Path()` (empty) for the silent-drop case, mirroring current behavior.

The `move_to_shelf` function (lines 805-818) already uses `target_dir.mkdir(parents=True, exist_ok=True)` — no change needed; it'll create the multi-level path lazily, satisfying the "trees are lazy" decision.

`discover_existing_shelves` (lines 637-643) currently returns top-level shelf names. It should change to return *all* leaf paths under the catalog tree (skipping reserved + skipping `_index.md`). The agent is no longer reusing single-segment vocabulary; it's reusing fully-qualified placements.

### C.2 Inject schedule slices into the agent prompt

The current prompts pass `existing_shelves` so the agent can reuse vocabulary. With LCC, the full schedule is too big (tens of thousands of entries). Strategy:

- Before calling the agent, do a cheap LoC subject/author guess from the excerpt:
  - For documents we already have a title-page excerpt; pull a few salient nouns.
  - Hit `schedule_fts` with those terms to retrieve the top ~30 matching entries (notation + caption + class chain).
  - Render them in a "Candidate placements" section of the prompt.
- Always include the full top-level outline (the 21 letter classes A-Z minus a few) — it's tiny and grounds the agent.
- Always include the *existing in-use placements* from the catalog (the result of the new `discover_existing_shelves` walk).
- The agent's response shape changes from `"shelf": "astronomy"` to `"shelf_lcc": "QA76.73.P98"` (a notation, not a path). The categorizer then walks that notation to a path via the schedule DB. This keeps the agent's job simple — it picks an LCC, not a slugified path — and centralizes the path-building logic.

For books with a successful ISBN lookup, we can short-circuit the agent's shelf decision entirely (lookup-first per the ADR): pass the looked-up notation through the same walk, skip the agent for shelf placement, but still let the agent fill summary + tags + series. The shelf-only prompts (`*_SHELF_ONLY_PROMPT_TEMPLATE`) become unused for books; they remain for `--reshelve` over videos and articles.

### C.3 `--reshelve` semantics

`--reshelve` currently re-asks the agent for a shelf (lines 867-891). New behavior:
- For book notes that have an `lcc:` frontmatter field already populated: re-walk the schedule (no agent call, no network) and move the file. This is fast and free.
- For book notes without `lcc:`: try ISBN-extraction + lookup; if it succeeds, walk and move; if it fails, fall through to the agent.
- For videos and articles: agent path, with schedule slices in the prompt.

Add an `lcc:` frontmatter key to `render_frontmatter` in `catalog_common.py` (or, more minimally, write it inline in `categorize.py` once chosen). This makes future re-runs cheap.

### C.4 Exposing the schedule lookup to the `_index.md` generator

The `_index.md` generator (separate plan) needs:
- "Given a folder path, what is the canonical caption for this level and the children captions?" — answered by walking the path -> notation -> schedule row + child rows.
- "What's the parent's URI for backlinks?" — `source_uri` column.

Surface a small `lcc.py` module exporting:
```python
def walk_call_number(notation: str) -> list[ScheduleEntry]: ...
def lookup_by_path_segments(segments: list[str]) -> ScheduleEntry | None: ...
def children_of(notation: str) -> list[ScheduleEntry]: ...
def lookup_isbn(isbn: str) -> IsbnRecord | None: ...
```

These are pure read functions on the SQLite file. No business logic — the categorizer and the index generator each compose them.

---

## D. Sequencing

Each phase ends in a runnable artifact:

1. **Phase 1 — Schedule DB build script.** `scripts/build_lcc_db.py` produces `scripts/data/lcc.sqlite`. Test fixture: a JSON file of 20 known notations -> expected ancestor chains. Verifies depth, range nodes, captions, slug stability. **No pipeline changes.** Ship this first.

2. **Phase 2 — Lookup helpers.** `scripts/lcc.py` with the four functions above. Unit-tested against the fixture from Phase 1, plus a few hand-curated ISBN lookups (using a recorded HTTP fixture file so tests are offline).

3. **Phase 3 — ISBN extraction in `document_extract.py`.** Adds `extract_document_metadata`. Standalone; doesn't touch `categorize.py` yet. Verified by running over `catalog/files/` and printing ISBNs.

4. **Phase 4 — Lookup-first categorizer path.** Wire the ISBN lookup into `process_catalog_file` for `book` types. When the lookup succeeds, the agent is still called for summary + tags + series, but its `shelf_lcc` field is ignored in favor of the lookup. Adds `lcc:` frontmatter writeback. Add `--no-isbn-lookup` flag for debugging.

5. **Phase 5 — Agent fallback with schedule-slice injection.** Replace the old prompts. Build the FTS-driven candidate list. The agent now returns a notation, not a slug. Update `--reshelve` to use the no-agent fast path when `lcc:` is already present.

6. **Phase 6 (out of scope for this plan, just flagged) — Migration.** Existing notes live on single-segment shelves. We need a one-time pass that, for each existing note, infers an LCC notation (lookup or agent) and moves it. This is a destructive shuffle of the entire catalog; should be its own ADR-backed plan with a dry-run mode, manual review, and a clear rollback (git).

Phases 1-2 are pure offline work and unblock the rest.

---

## E. Open questions and risks

- **id.loc.gov bulk fetch behind Cloudflare** — could not verify the actual download URL works headless from the planning sandbox. **Action**: try a real `curl -A 'Mozilla/5.0' -L` against `https://id.loc.gov/static/data/authoritiesclassification.skos.nt.gz` (or the equivalent current path) before committing to it as primary. If it doesn't work, fall back to (a) manual one-time download outside the script, (b) `lcc-pdf-to-json` as primary with id.loc.gov as on-demand augmentation per-notation via SRU (which exposes classification authorities too on its `lcco` database).
- **Outline depth vs full schedule** — outline-depth data covers ranges down to maybe 4-5 levels. Cutter-table topical leaves (`QA76.73.P98` Python) require either the full MARC 21 Classification dump or per-notation lookups against id.loc.gov authorities. Decision needed: live with partial depth (good enough for most browsing), or invest in full-schedule extraction.
- **Cutter cleanup heuristics** — distinguishing topical cutters from author cutters is a real source of folder-tree quality. First pass: drop all cutters. Later pass: keep cutters when the parent caption matches keywords like "By language", "Special, A-Z", etc. This is a subtle judgment call; flag for human review of the first hundred items.
- **Multi-class items** — LoC sometimes assigns multiple 050 fields. Pick the first (`ind1=0 ind2=0`, "Library of Congress assigned"); record the others in frontmatter as `lcc_alternates:` for later cross-listing.
- **Items where lookup returns nothing** — defined behavior: write `source: 'none'` in cache, fall through to agent path. The agent might return a notation we've never seen — that notation should still walk cleanly via the schedule DB; the new folder gets created lazily. If the notation fails to walk, treat it like `normalize_shelf`'s current "invalid" case: silently drop, leave note at catalog root.
- **Schedule update cadence vs notation churn** — LoC occasionally renumbers or splits ranges. Folder names baked into the catalog from a 2024 build won't auto-rename when a 2027 rebuild changes captions. This is a manual hygiene concern; the build script's `meta.source_revision` row at least makes drift detectable. Not blocking.
- **Whether to commit the SQLite file** — preferred yes (predictable, offline, ~tens of MB). Confirm size after a real build before deciding.
- **Licensing** — LCC data on id.loc.gov is published under terms compatible with redistribution; not a blocker. Note in the build script header.
- **Cloudflare on `loc.gov` for the WebFetch / WebSearch agent path** — the agent may need to hit LoC pages during its categorization; the system already grants WebSearch + WebFetch but those may also be Cloudflare-gated. **Workaround**: prefer authoritative facts via SRU (server-side, in the categorizer) over scraping during the agent call.

---

## Critical files for implementation

- `/mnt/d/library/scripts/categorize.py` — main integration point; `normalize_shelf`, `move_to_shelf`, prompt templates, `process_catalog_file`, `--reshelve` handling all change.
- `/mnt/d/library/scripts/catalog_common.py` — `render_frontmatter` gains an optional `lcc:` key; `RESERVED_CATALOG_DIRS` may need to grow.
- `/mnt/d/library/scripts/document_extract.py` — adds the new `extract_document_metadata` ISBN extractor.
- `/mnt/d/library/scripts/lcc.py` — new module: walking, slug rendering, ISBN lookup, FTS queries.
- `/mnt/d/library/scripts/build_lcc_db.py` — new build-time tool that materializes `scripts/data/lcc.sqlite` from id.loc.gov bulk RDF (or the chosen fallback).

Sources cited above: [FreeLCC PDFs](https://www.loc.gov/aba/publications/FreeLCC/freelcc.html), [MARC 21 Classification 153](https://www.loc.gov/marc/classification/concise/cd153.html), [ClassWeb subscription](https://www.loc.gov/cds/classweb/), [id.loc.gov](https://id.loc.gov/), [id.loc.gov download](https://id.loc.gov/download/), [LC SRU server list](https://www.loc.gov/standards/sru/resources/lcServers.html), [thisismattmiller/lcc-pdf-to-json](https://github.com/thisismattmiller/lcc-pdf-to-json), [edsu/lcco](https://github.com/edsu/lcco), [pymarc](https://pypi.org/project/pymarc/), [Open Library APIs](https://openlibrary.org/developers/api).
