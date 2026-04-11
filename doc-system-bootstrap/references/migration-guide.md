# Migration Guide — Phase 2 Detail

Detailed process for migrating content from `docs.old/` to the new documentation system.

## Step 1 — Inventory docs.old/

```bash
find docs.old/ -name "*.md" -exec wc -l {} + | sort -rn
```

List all files with sizes. Identify:
- Area docs (frontend.md, backend.md, security.md, etc.)
- DB docs (db/*.md)
- Planning, changelog, research
- Proposals (changes/, _archive/)
- Other files

## Step 2 — Migrate structural files

Each structural file is **rewritten** in the new format. The existing content is read,
classified, and transformed — not copied with a new header on top.

For each file: read old → show user what was found → transform → write new → confirm.

### Direct copies (no transformation needed)

| Source | Destination | Treatment |
|--------|------------|-----------|
| `docs.old/db/*` | `docs/db/` | Copy as-is (schema reference) |
| `docs.old/_archive/*` | `docs/_archive/` | Copy as-is |
| `docs.old/voice.md` | `docs/voice.md` | Copy as-is |
| Any other `.md` not listed below | Evaluate: area doc → Step 3. Unknown → ask user |

### planning.md — rewrite to new format

1. Read `docs.old/planning.md` entirely
2. Classify each block/section:
   - Prose descriptions or context → **DISCARD** (planning only has tasks)
   - `[x]` items that are standalone → **DISCARD** (already completed)
   - `[x]` items in a group with pending `[ ]` → convert to ~~strikethrough~~ (group progress)
   - `[ ]` pending items → **KEEP**
   - ~~struck through~~ groups where ALL items are done → **DISCARD**
   - ~~struck through~~ items in groups with pending → **KEEP** as ~~strikethrough~~
   - Tables, stats, summaries → **DISCARD** (not tasks)
3. Show classification to user before writing
4. Write `docs/planning.md` using template header, then only the KEEP items
5. Show: "planning.md: N lines → M lines"

### changelog.md — rewrite with rotation

1. Read `docs.old/changelog.md` entirely
2. Classify each entry:
   - Entries with >5 bullets → **COMPRESS** to ≤5 bullets + pointers
   - Entries with implementation detail → **TRIM** to summary level
   - Entries older than current quarter → **ROTATE** to `docs/_archive/changelog/YYYY-QN.md`
3. Show what will be rotated and what will be compressed
4. Write `docs/changelog.md` using template header + transformed entries

### decisions.md — build from scratch

1. If `docs.old/decisions.md` exists → read it, extract any existing decision entries
2. The bulk of decisions.md will be populated in Step 5 by scanning area docs
   for `> **Decision:**` markers
3. Write `docs/decisions.md` using template with whatever entries exist so far

### research-needed.md — clean up

1. Read `docs.old/research-needed.md` if it exists
2. For each entry:
   - Question answered elsewhere → **DISCARD**
   - Question still open → **KEEP**
3. Write using template header + open questions

### Proposals (SDD)

- `docs.old/changes/*/` (active proposals) → copy to `docs/changes/` preserving folder structure
- `docs.old/changes/README.md` → **DON'T copy** (the new system installed a fresh one)
- `docs.old/changes/_template/` → **DON'T copy** (the new system installed a fresh one)
- Proposals in status `done` that weren't archived → move to `docs/_archive/changes/`

## Step 3 — Classify area doc content

For each area doc in docs.old/, read it and classify EVERY section/heading:

| Type | What it is | Destination |
|------|-----------|-------------|
| **REF** (code-derivable) | Params, props, values, file trees, test counts | **DISCARD** |
| **REF** (architecture) | What exists, how organized, compact indexes | **AREA DOC** |
| **ARCH** (decisions) | Why, trade-offs, alternatives | **AREA DOC** inline `> **Decision:**` |
| **GUIDE** (conventions) | Team rules not in linters | **AREA DOC** `## Conventions` |
| **STATUS** (temporal) | "175 tests", "session X" | **DISCARD** or **CHANGELOG** |
| **GOTCHA** (cross-file) | "If you change X, update Y" | **AREA DOC** `## If you touch...` |
| **DIAGRAM** (topology) | Network, security layers | **AREA DOC** keep as-is |
| **DIAGRAM** (layout) | ASCII UI layout | **KEEP only if prescriptive** (design contract) |
| **PRESCRIPTIVE** | Spacing tables, breakpoints, density | **AREA DOC** keep as-is |

### DISCARD review — check for hidden value

Before discarding, verify each DISCARD section:

| Hidden value | Example | Action if found |
|-------------|---------|----------------|
| Rationale embedded in REF | "Uses X because Y" | Extract as `> **Decision:**`, discard the rest |
| Non-obvious thresholds | "Polling every 15min = API TTL" | Keep as decision or convention |
| Semantic usage rules | "Warning color only for alerts" | Keep as convention |
| Accessibility decisions | "WCAG AA contrast mapping" | **KEEP** — cross-cutting, not inferrable |
| Non-obvious behavior | "Accepts unauthenticated requests" | Keep as architecture note |
| Config location knowledge | "Config lives in X, uses CSS vars Y" | Keep as pointer (1 line) |

Mark uncertain sections as **REVIEW** and show them to the user.

**Show the full classification to the user before writing.**

## Step 4 — Write new area docs

For each area doc, write the new version:

```markdown
# [Area] — Architecture

## Stack and structure
[Architecture-level REF]

## [Domain sections]
[Compact indexes: 1 line per endpoint/component/service]
[1 canonical example per pattern]
> **Decision:** [inline where they apply]

## Conventions
[All GUIDE content consolidated]

## If you touch...
[All GOTCHA content consolidated]
```

**Differentiated detail levels:**

| Doc type | Level | Guideline |
|----------|-------|-----------|
| security | HIGH | Complete defense model, never trim |
| brand-kit / design | PRESCRIPTIVE | Keep ALL contract tables |
| backend, frontend | STANDARD | Compact index + 1 canonical example + patterns |
| infrastructure | STANDARD | Topology diagram + deploy flow |

## Step 5 — Build decisions.md index

Scan all new area docs for `> **Decision:**` markers. Build the index:

```markdown
| # | Decision | Doc | Section |
|---|----------|-----|---------|
| 1 | [title] | [area].md | § [section] |
```

## Step 6 — Update README.md

Update `docs/README.md` with all files that now exist.

## Step 7 — Verify consistency

```bash
# No references to old paths
grep -rn "docs\.old" docs/ CLAUDE.md .claude/ 2>/dev/null

# No duplication between area docs
for term in sameSite envPrefix credentials; do
  count=$(grep -rl "$term" docs/*.md 2>/dev/null | wc -l)
  [ "$count" -gt 1 ] && echo "⚠️  '$term' in $count docs — deduplicate"
done

# Size check
for f in docs/*.md; do
  lines=$(wc -l < "$f" 2>/dev/null)
  [ "$lines" -gt 350 ] && echo "⚠️  $f: $lines lines (>350 threshold)"
done
```

## Step 8 — Review memory for doc-worthy content

Project memory often accumulates decisions and conventions that belong in docs.

1. Read all memory sources
2. Classify each entry:
   - Architecture decision → Move to area doc + decisions.md
   - Convention → Move to area doc `## Conventions`
   - Gotcha → Move to area doc `## If you touch...`
   - Personal preference → **KEEP in memory**
   - Workflow preference → **KEEP in memory**
   - Stale/outdated → **DELETE**
3. Show classification to user before making changes
4. Clean up memory: remove moved and stale entries

## Step 9 — Migration summary

```
### Migration complete
| Doc | Before | After | Reduction |
|-----|--------|-------|-----------|
| frontend.md | X lín | Y lín | -Z% |
| ... | ... | ... | ... |

### Decisions extracted: N
### Conventions consolidated: N sections
### Content discarded: ~N lines (code-derivable)
### Memory entries moved to docs: N

### Next steps
- Review new docs to verify nothing important was lost
- When satisfied: rm -rf docs.old/
- You can now uninstall this skill
```
