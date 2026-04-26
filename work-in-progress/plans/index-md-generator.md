# Index `_index.md` generator — preliminary plan

## 1. Background

We are moving the catalog from flat single-segment shelves (`catalog/astronomy/`) to full-depth Library of Congress Classification, with folder names that encode both notation and human name (e.g. `QA76.73.P98-python/`). LCC trees can be deep and lopsided, so we need a way to skim a whole subtree from inside Obsidian without expanding ten folder levels in the file pane. This generator produces an auto-built `_index.md` (working name) at every directory level under `catalog/`. Each one lists the direct children, plus every catalog item anywhere beneath it.

This plan covers only the index generator. It assumes a separate plan/ADR delivers the LCC schedule database and the folder-naming convention.

## 2. Decisions (recommended)

These are the calls I am making now so the rest of the plan has something to lean on. Each is reversible; flag any you disagree with.

| # | Question | Recommendation |
|---|---|---|
| D1 | File name | `_index.md` literally, one per non-reserved directory under `catalog/` |
| D2 | Wholly generated, or section-only? | Wholly generated. No human edits survive. |
| D3 | Run trigger | Final pass in `categorize.py` after series rebuild, plus standalone `scripts/build_indexes.py` |
| D4 | Empty-folder cleanup | Yes — delete `_index.md` for folders with zero descendant items, and delete the folder itself if it is also empty of subfolders |
| D5 | Hide from quick switcher? | No. Leave them discoverable. |
| D6 | Wikilink form to children | Path-qualified: `[[Q-science/QA-mathematics/_index|QA — mathematics]]` |
| D7 | Source of human-readable names | Parse from folder name; do not query the LCC SQLite DB |

The thorniest is D1 vs the alternatives — see Section 5.

## 3. What an `_index.md` contains

### 3.1 Frontmatter

```yaml
---
type: index
lcc: "QA76.73"          # notation/range this folder represents; "" at catalog root
generated: true         # marker for tooling and humans
tags: []
---
```

- `type: index` is new. Add it to the `discover_*` walks in `catalog_common.py` so other tools can filter indexes out (same way `type: series` is handled in `categorize.py:836`).
- `tags: []` so the existing "untouched tags" gate (`r"^tags:\s*\[\s*\]\s*$"`) still recognizes the file as untagged. This costs nothing and keeps a single frontmatter shape.
- The `generated: true` flag is the explicit "do not hand-edit" sentinel. Manual readers see it; tooling can refuse to process indexes lacking it.

### 3.2 Body layout

```markdown
# QA76.73 — Programming languages

*51 items in this subtree; 6 direct subclasses.*

## Subclasses

- [[Q-science/QA-mathematics/QA75-QA76.95-calculating-machines-and-electronic-computers/QA76.7-QA76.76-computer-software/QA76.73-programming-languages/QA76.73.C153-c/_index|QA76.73.C153 — C]] (4)
- [[…/QA76.73.J38-java/_index|QA76.73.J38 — Java]] (12)
- [[…/QA76.73.P98-python/_index|QA76.73.P98 — Python]] (18)

## Items

### QA76.73.C153 — C
- [[K&R - The C Programming Language]]
- [[Modern C - Jens Gustedt]]

### QA76.73.J38 — Java
- [[Effective Java - Joshua Bloch]]
…
```

Sections, in order:

1. **Title** (`#`): `<notation> — <name>`. At catalog root: `# Catalog`.
2. **Summary line**: total descendant item count, direct child count.
3. **Subclasses**: one bullet per direct child folder, link points at that child's `_index.md`, count in parens.
4. **Items**: every catalog note in the subtree, **grouped by leaf folder** (`###` headings, sorted by LCC notation), each group sorted by note title case-insensitively. Series notes appear as a single bullet at the top of their group; their volumes appear as nested bullets so the structure mirrors `## Volumes` in series notes.

Why grouped-by-leaf rather than flat or grouped-by-`type`:
- Flat lists obscure where a note actually sits. A reader scanning `Q-science/_index.md` who sees `[[Effective Java]]` should be able to tell it's filed under `QA76.73.J38`.
- Grouping by `type:` (book/article/video) is interesting but cuts across the LCC story we just adopted — the value proposition of LCC is exactly the grouping we'd be discarding.
- Grouping by leaf folder is also the cheapest to render: one walk, one `dict[leaf_dir, list[note]]`.

For deep ancestor indexes (e.g. `Q-science/_index.md` covering thousands of items), the `### <leaf>` headers act as natural skim anchors. If item count exceeds a threshold (say 200), the renderer can collapse the Items section into a `> [!note]+ All items in subtree` Obsidian callout — open by default but visually demarcated. Treat the threshold as tunable, not a hard requirement.

### 3.3 Counts

- Direct child count: number of non-reserved subdirectories with at least one descendant item.
- Subtree item count: every `.md` under this directory (recursive) where `type:` is not `index`. Series notes count as 1 item each (they're real notes a reader cares about).

## 4. Generator behavior

### 4.1 Module shape

New module `scripts/build_indexes.py` exposing:

```python
def build_indexes(catalog_dir: Path) -> list[str]:
    """Regenerate every _index.md under catalog_dir. Returns log lines."""
```

…plus a `main()` for `uv run python scripts/build_indexes.py`. `categorize.py:main` imports `build_indexes` and calls it after the series rebuild loop (`categorize.py:1060–1073`).

### 4.2 Algorithm

1. **Walk**: `catalog_dir.rglob("*.md")` filtered the same way `discover_catalog_files` does (skip reserved parents). Read frontmatter via `split_frontmatter` (already in `categorize.py`; lift into `catalog_common.py`). Build `items_by_dir: dict[Path, list[NoteRef]]`.
2. **Enumerate dirs**: every directory containing or transitively containing a `.md` (other than its own `_index.md`). Walk bottom-up so child counts are known when a parent renders.
3. **Render**: for each directory, render the body using item lists collected in step 1 plus subdirectory metadata accumulated in step 2.
4. **Write**: write to `<dir>/_index.md` only if the rendered text differs from existing content (idempotent quiet runs). Use the same `read_text/write_text(encoding="utf-8")` pattern used elsewhere.
5. **Cleanup**: collect every existing `_index.md`; any not produced this run gets deleted. Then for each directory whose only contents were `_index.md` and which is now empty, delete the directory too. Do not recurse into reserved dirs at any step.

### 4.3 Idempotency rules

- The whole file is regenerated from disk state every run. This matches the `## Volumes` precedent (`rebuild_volumes_section`, `categorize.py:764`) but extends it to the entire file. Because the file has `generated: true` in frontmatter and exists nowhere except as output, no human contract is broken.
- The generator never touches files whose `type:` is not `index`. It is read-only on real notes.
- Like `rebuild_volumes_section`, only write if content changed (avoids spurious git churn).
- Compatible with `--reshelve`: items move shelves first, then indexes are regenerated against the post-move tree. Old indexes pointing at stale paths get overwritten, and orphaned indexes for emptied folders get cleaned up.

### 4.4 Discovery helpers to lift into `catalog_common.py`

Currently scattered, should be shared:

- `split_frontmatter` (in `categorize.py:534`) → move
- `parse_frontmatter_type` (`categorize.py:585`) → move
- `discover_catalog_files` (`categorize.py:646`) → move; teach it to skip a configurable set of filenames so `_index.md` is excluded the same way `index.md` already is (`INDEX_FILENAMES`, `categorize.py:61`).

The `INDEX_FILENAMES` set should grow to include `_index.md`. Right now it's `{"index.md"}` — the existing filter already anticipates index files. Keep both names: legacy `index.md` (if any exists) plus the new `_index.md`.

## 5. Naming conflicts with Obsidian

This is the load-bearing design decision. Three options were on the table:

### Option A: literal `_index.md` (recommended)

- Pros: trivial mental model; matches the Hugo convention readers may know; underscore prefix sorts the file to the top of the directory listing in Obsidian's file explorer; isolates index files from quick-switcher fuzzy hits on real titles (typing "index" matches all of them).
- Cons: every folder's index has the same filename. Bare `[[_index]]` is ambiguous. Obsidian's wikilink resolution falls back to a path-qualified target only when the resolver can't pick a unique file by basename, and the failure mode (link to "the wrong _index") is silent.
- Mitigation: **always emit path-qualified wikilinks** from this generator. Format:
  `[[<vault-relative-path-without-extension>|<display label>]]`.
  Example: `[[Q-science/QA-mathematics/_index|QA — mathematics]]`. Obsidian supports vault-root-relative paths in wikilinks; the alias after `|` keeps the rendered text human.
- The display label encodes the LCC notation plus the human name parsed from the folder name. Vary by depth: `_index.md` files higher up use shorter labels; deep ones use the leaf range.

### Option B: name the index after the folder (`QA76.73-programming-languages.md` inside `QA76.73-programming-languages/`)

- Pros: every index is uniquely named; bare `[[QA76.73-programming-languages]]` resolves correctly and the link shows a useful title in graph view and backlinks.
- Cons: long file names mixed with regular note names in the file pane (no visual separation); doesn't sort to the top; surfaces in quick switcher alongside real titles, polluting fuzzy results.

### Option C: stick with `_index.md`, no path qualification

- Pros: shortest links.
- Cons: relies on Obsidian's "shortest path when possible" resolution, which silently picks one file for a duplicated basename. Verifiable footgun. Reject.

**Recommendation: Option A with mandatory path-qualified wikilinks.** Document this rule in the script's module docstring; add a comment near the wikilink renderer pointing at it. If we later find Obsidian's resolution is reliable, we can drop the path qualifier — the inverse migration would be dangerous.

### Quick-switcher / search visibility

The existing `catalog/.obsidian/app.json` has `"userIgnoreFilters": ["files/"]` and `"attachmentFolderPath": "files"`. The user-ignore filter is what hides the attachments folder from quick switcher and search.

Recommendation: **do not** add `_index.md` (or a glob like `_index*`) to `userIgnoreFilters`. Indexes are exactly the navigation surface we are building, so suppressing them defeats the point. Quick-switcher fuzz on `_index` does pollute results; the underscore prefix limits this to people who actively type one. Acceptable.

If the pollution proves annoying, a follow-up can add a glob; this is reversible.

## 6. Schema interaction

The generator needs each folder's notation and human name. Two options:

- **Read the LCC SQLite DB** (planned in a separate ADR): authoritative, but couples this script to the schedule subsystem and means a malformed DB breaks index regeneration. Also needs the schema lookup keyed by the same notation we encode in folder names — circular if the DB becomes the source of truth and folder names are regenerated from it.
- **Parse the folder name** (recommended): the folder-naming convention already encodes both pieces. A simple regex splits on the first `-` after the notation tokens. For ranges like `QA75-QA76.95-calculating-machines-and-electronic-computers`, we need a notation-token grammar — but the schedule plan is going to define that grammar anyway, and the parser is short.

Recommendation: parse from folder name. Provide a hook (`fetch_folder_label(notation: str) -> str | None`) that the schedule DB can later override if we want canonical names from the schedule. Default implementation reads the folder name only.

The parser belongs in a new helper module (`scripts/lcc_naming.py` or in `catalog_common.py`) shared with whatever creates the folders in the first place. Out of scope for this plan, but flag the dependency.

## 7. Sequencing / phases

1. **Skeleton + CLI invocation.** Create `scripts/build_indexes.py` with arg parsing (`--catalog-dir`, `--dry-run`, `--verbose`). Walks the tree, prints what it would do. Lift `split_frontmatter`, `parse_frontmatter_type`, `discover_catalog_files` into `catalog_common.py`.
2. **Subtree walk + item collection.** Build `items_by_dir`. Compute per-directory descendant counts and direct child counts. Logged via `--verbose`.
3. **Render + write.** Implement the body renderer. Implement `render_index_frontmatter`. Path-qualified wikilink emitter with display labels parsed from folder names. Write only on diff.
4. **Orphan cleanup.** After writing, walk all existing `_index.md` files; delete those not produced this run. Walk directories bottom-up; delete now-empty non-reserved directories.
5. **Integration into `categorize.py`.** Final pass: `from build_indexes import build_indexes; build_indexes(catalog_dir)` after the series rebuild loop. Print summary log lines matching the existing format (`series:` lines, `wrote:` lines).
6. **Folder-name parser.** Pull the LCC-folder-name parser out of step 3 into `lcc_naming.py` so the folder-creation logic (separate plan) can share it.

Each phase is independently shippable. Phases 1–3 deliver value alone (you'd still hand-clean orphans). Phase 4 makes `--reshelve` safe. Phase 5 closes the loop so indexes regenerate without ceremony. Phase 6 is refactoring once the schedule plan lands.

## 8. Open questions / risks

- **R1 — Obsidian wikilink resolution for duplicated basenames is not formally documented.** I recommended path qualification (Option A, Section 5) precisely to sidestep this. Worth a five-minute manual test in the actual vault before committing: create two `_index.md`s, link to one with a path-qualified wikilink, confirm the link resolves and the alias displays.
- **R2 — Performance on large vaults.** Walking `rglob("*.md")` and reading frontmatter for every file is O(n) per generator run. At thousands of notes this is still subsecond on local SSD, but if the LCC tree explodes to tens of thousands, consider a single-pass walk that builds both `items_by_dir` and the directory tree at once. Premature for now; flag it.
- **R3 — `--reshelve` interaction.** The current `--reshelve` flow processes notes one at a time and rediscovers shelves between iterations (`categorize.py:1052`). Indexes generated mid-loop would be wrong for any folder reshuffled later. Solution: only run `build_indexes` after the loop terminates, in `main()`'s final pass. Don't try to keep indexes in sync per-iteration.
- **R4 — Git churn.** A regenerated index that differs in a single count number causes a commit-worthy diff. Generator-only diffs at every catalog run will be noisy. Mitigations: write only on changed content (already specified); consider gating on a meaningful diff (ignore whitespace changes); accept the churn — it accurately reflects vault state.
- **R5 — Series notes inside the LCC tree.** A series note (`type: series`) is a real catalog item from the index's perspective. It should appear in the Items section like any other note. Its volumes are also listed individually (each volume is also indexed under its LCC folder). This causes mild duplication: a series and its volumes both appear. I think that's correct — readers want both views — but flag it for confirmation.
- **R6 — `_index.md` at catalog root.** Top-level `catalog/_index.md` is the most useful single entry point. Make sure it gets generated. The walk's "every directory that contains items" rule covers it implicitly; just verify.
- **R7 — Conflict with `categorize.py:INDEX_FILENAMES`.** That set already excludes `index.md` from the categorizer's walk. Adding `_index.md` to it is a one-line change, but every other tool that walks the catalog (`catalog_documents.py`, `catalog_videos.py`) does its own filtering — audit them for the same fix.
- **R8 — `discover_existing_shelves` semantics.** Currently returns top-level folders directly under `catalog/` (`categorize.py:637`). Under LCC the "shelves" the agent picks become deep paths (`Q-science/QA-mathematics/.../python`). That is a separate plan's concern (the LCC adoption ADR), not this one — but our generator needs to coexist with whatever the agent writes. Flag the coupling.
- **R9 — Reserved-directory expansion.** If we ever introduce more reserved names (e.g. `templates/`), `RESERVED_CATALOG_DIRS` is the single source. Confirm the generator uses `is_reserved_dir_name` and doesn't hard-code its own list.

## 9. Concrete next actions

1. Confirm or override the seven decisions in Section 2.
2. Five-minute Obsidian sanity check on path-qualified wikilink resolution to two same-named files (R1).
3. Land the schedule/folder-naming ADR; specifically, the regex for splitting `<notation>-<human-name>` and `<range>-<human-name>` folder names.
4. Implement Phase 1 of Section 7 (`scripts/build_indexes.py` skeleton + helper lift into `catalog_common.py`).

### Critical files for implementation

- /mnt/d/library/scripts/categorize.py — final-pass integration point and the source of `split_frontmatter`, `parse_frontmatter_type`, `discover_catalog_files`, plus the precedent for "regenerate one section wholesale" (`rebuild_volumes_section`)
- /mnt/d/library/scripts/catalog_common.py — destination for the lifted helpers, owner of `RESERVED_CATALOG_DIRS` / `is_reserved_dir_name`, and home for `render_frontmatter`
- /mnt/d/library/scripts/build_indexes.py — new module to be created; the generator itself
- /mnt/d/library/catalog/.obsidian/app.json — verify `userIgnoreFilters` does not need changing (decision D5)
- /mnt/d/library/CLAUDE.md — once the generator lands, the "Idempotency rules" and "Where notes live" sections need a paragraph documenting `_index.md` as a fully-generated artifact, parallel to the series-note paragraph
