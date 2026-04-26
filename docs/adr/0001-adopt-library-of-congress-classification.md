# 1. Adopt full-depth Library of Congress Classification for shelves

**Status:** accepted

**Date:** 2026-04-26

## Context and Problem Statement

Shelves are currently single-segment kebab-case folders under `catalog/`
(`physics`, `cryptography`, `philosophy`). Naming is conventional, not
controlled: the categorizer picks a shelf per item against the existing
list, but nothing checks the choice against an external taxonomy, and
nothing prevents synonyms from accumulating ("ml" vs "machine-learning",
"history-of-mathematics" vs "math-history") as the catalog grows. The
flat layout also has no internal structure once any single shelf grows
large.

We want a structured taxonomy that scales across videos, books,
articles, lectures, and web snapshots; that the agent can verify
against a published reference instead of inferring from prior runs;
and that lets a reader navigate the catalog at varying levels of
abstraction.

## Decision Drivers

- Modern topic coverage (computing, web, machine learning).
- Granularity for STEM and humanities materials.
- Schedules freely available so the categorizer can verify a choice.
- Useful classification depth — the system should still subdivide
  meaningfully five levels in.
- Reproducible placement: same item, same path, every run.

## Considered Options

1. Keep single-segment kebab shelves.
2. Adopt Dewey Decimal Classification (DDC) with deep nesting.
3. Adopt Library of Congress Classification (LCC) with deep nesting.

## Decision Outcome

We will adopt full-depth LCC. Concretely:

- Replace flat shelves with a folder hierarchy mirroring the LCC
  schedule. Folder names retain the notation: `Q-science/`,
  `QA-mathematics/`, `QA75-QA76.95-calculating-machines-and-electronic-computers/`,
  down to a leaf like `QA76.73.P98-python/`.
- Treat schedule-defined ranges as first-class folders. When the
  schedule defines a topic as a range with a name (`BD418-BD418.5
  Mind and body`), that range becomes a folder, even when no item
  sits exactly there. The tree mirrors the actual schedule, not raw
  notation parent chains.
- Drop Cutter numbers. Stop at the topical portion of the call
  number; basenames already make notes unique within a leaf.
- Lookup-first, infer-fallback. For items with ISBNs (books), look
  up the LoC-assigned call number from an authoritative source and
  trust it. For items without (videos, lectures, web pages, papers
  without LoC records), the agent infers placement using the
  schedule as reference data, not from existing shelf vocabulary.
- Trust the LoC-assigned classification. Subjective "this belongs
  elsewhere" overrides go to tags, not to a different call number.
- Lazy folder creation: only directories with content exist on disk.
- Generate a static `_index.md` at every directory level listing all
  items in that subtree, regenerated wholesale on each pipeline run
  (mirrors the existing series-note `## Volumes` regeneration). This
  preserves browsability when the tree is deep and lopsided.
- Build a one-time SQLite database of the LCC schedules so the
  categorizer can resolve full ancestor chains and inject relevant
  schedule slices into the agent prompt.

LCC was chosen over DDC because its STEM and humanities subdivisions
are deeper, its schedules are freely browsable through the LoC, and
its notation maps cleanly into a mnemonic folder tree. DDC's
strengths (cleaner numeric sort, smaller stable top-level) only
mattered while shelves were flat; once nesting is on the table,
classification depth and free machine-verifiable schedules dominate.

### Consequences

- Good: items in the LoC catalog land in deterministic, reproducible
  paths without involving the agent at all.
- Good: the agent has a referenceable schedule to cite, narrowing
  drift compared with picking ad-hoc shelf names.
- Good: tags retain their role as the cross-cutting facet; every
  shelf placement is a single LCC location.
- Good: deep subtrees stay browsable through generated index notes.
- Bad: adopting LCC requires upfront work — a schedule database, an
  ISBN lookup path, prompt restructuring, an index generator —
  before any items can move.
- Bad: folder paths are longer and noisier than `physics/`.
- Bad: items not in LoC's catalog still depend on agent inference,
  with the variance that implies. Lookup coverage is uneven across
  formats.
- Bad: `--full-refresh` and `--reshelve` semantics need to be
  reworked around the new tree.
- Neutral: existing notes need a one-time migration when the new
  pipeline goes live.

### Confirmation

The decision is confirmed in practice when:

- New books with ISBNs land in LoC-assigned paths without manual
  edits.
- New non-book items land in plausible paths the agent can defend
  by citing schedule excerpts.
- Browsing through `_index.md` works at every level without manual
  upkeep.

## Pros and Cons of the Options

### Decision matrix

Weights reflect what the catalog actually needs: machine
verifiability, modern topic coverage, and useful hierarchy depth
weigh heaviest (3); cosmetic and stability concerns weigh least (1).
Scores are 1-5.

| # | Criterion | Weight | LCC | DDC | Kebab status quo |
|---|-----------|:------:|:---:|:---:|:----------------:|
| 1 | Granularity for STEM / computing | 3 | 5 | 2 | 1 |
| 2 | Granularity for humanities | 2 | 5 | 4 | 2 |
| 3 | Modern topic coverage | 3 | 4 | 2 | 2 |
| 4 | LLM familiarity for shelf-picking | 1 | 4 | 4 | 5 |
| 5 | Filesystem sorts in classification order | 1 | 3 | 5 | 1 |
| 6 | Schedules freely browsable | 2 | 5 | 2 | n/a |
| 7 | Cultural neutrality | 1 | 3 | 2 | 4 |
| 8 | Cross-disciplinary handling | 1 | 3 | 3 | 3 |
| 9 | Useful hierarchy depth | 3 | 5 | 3 | 1 |
| 10 | Notation mnemonic when nested | 1 | 4 | 3 | n/a |
| 11 | Picker discipline / stable shape | 1 | 3 | 4 | 2 |
| 12 | Agent can verify its own choice | 3 | 5 | 2 | 1 |
| | **Weighted total** | | **97** | **60** | **34** |

### Option 1: Keep single-segment kebab shelves

- Good: short paths, easy to type and link.
- Good: humans intuitively read `physics/` faster than `Q-science/QC-physics/`.
- Bad: no controlled vocabulary — synonyms accumulate over time.
- Bad: no machine verification; every placement is an inference.
- Bad: doesn't scale once any single shelf grows large.

### Option 2: DDC with deep nesting

- Good: pure decimal notation sorts naturally in classification
  order on the filesystem.
- Good: ten stable top-level classes discourage drift.
- Bad: famously cramped on technology — 004-006 has to cover all
  of computing.
- Bad: full schedules live behind OCLC's WebDewey subscription, so
  the categorizer cannot verify a choice against the source. Free
  summaries cover only top levels.
- Bad: subdivisions past three digits get arbitrary and uneven.

### Option 3: LCC with deep nesting (chosen)

- Good: STEM and humanities subdivisions go deep with substance —
  `QA76.73.A-Z` alone subdivides programming languages by name.
- Good: the Library of Congress publishes the schedules in MARC 21
  Classification format and as free PDFs. The categorizer can read
  them.
- Good: notation is mnemonic when nested (`Q` -> `QA` -> `QA76` ->
  `QA76.73` reads as science -> mathematics -> computer science ->
  programming languages).
- Bad: paths are longer and visually noisier than DDC's.
- Bad: alphanumeric sort on disk is uglier than DDC's pure decimals.
- Bad: 21 main classes plus deep subdivision invite excessive depth
  if not bounded by the schedule itself.

