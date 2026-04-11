# Documentation System — Principles

## Core rule

> **Only document what can't be read from the code.**

The docs are the SSOT for project knowledge. Claude reads docs for architecture;
reads code for implementation details.

## What goes in docs vs what's in the code

| In docs (SSOT) | In code (Claude reads it) |
|----------------|--------------------------|
| Architecture: what exists, how it's organized | Implementation: params, props, types, values |
| Patterns with 1 canonical example | Every instance of the pattern |
| Conventions: team rules not in linters | What linters already validate |
| Decisions: why it was done this way (inline) | The result of the decision |
| Cross-file dependencies: "if you touch A, update B" | Individual files |
| Topology/architecture diagrams | Config spread across files |
| Design contracts (prescriptive specs) | CSS tokens implementing the contract |
| DB schema (avoids queries) | Migration code |
| Compact indexes (1 line per endpoint/component) | Params and response of each one |
| Gotchas and known traps | Code that avoids them |

## Compression target

> **Eliminate everything derivable from code.** No fixed line target.
> Each doc settles at its natural size based on how much non-code knowledge it has.

## Content types and rules

### Architecture + Patterns → REWRITE when changed
What exists and how it works. Compact indexes. 1 canonical example per pattern.
The agent rewrites sections with current state — never appends.

### Conventions → Stable, rarely change
Team rules. Live in `## Conventions` section of each area doc.
Agent doesn't modify without explicit instruction.

### Decisions → Inline, append-only markers
Marked with `> **Decision:**` in the area doc where they apply.
`decisions.md` is just a pointer index, not a copy.
Never edit a decision — if it changes, add a new one referencing the old.

### Cross-file dependencies → `## If you touch...`
"If you change X, also update Y." Each area doc has this section at the end.

### Status → Flows and rotates
`changelog.md`: quarterly rotation to `_archive/changelog/YYYY-QN.md`.
`planning.md`: only `[ ]` pending tasks. Never `[x]`.
When a task is completed:
- **Standalone task** → delete the line + add summary to changelog
- **Task in a group/phase** → ~~strikethrough~~ but keep in the file (shows progress within the group)
- **All tasks in a group ~~struck through~~** → delete the entire group block + add summary to changelog

## Doc-updater agent checklist

### YES update area doc if:
- New file, module, route, or service → add to compact index
- New pattern others should follow → document with example
- Convention changed → update `## Conventions`
- New cross-file dependency → add to `## If you touch...`
- New architecture decision → inline with `> **Decision:**`

### NO update area doc if:
- Value change (config, size, color, text)
- Internal refactor (interface unchanged)
- Bug fix
- Adding/modifying props, params, types
- Adding tests
- New item in existing domain (just 1 index line)

## How the system grows

| Event | Action |
|-------|--------|
| New architecture decision | Inline `> **Decision:**` + entry in decisions.md |
| New DB table | Create `db/[table].md` + update index |
| Architectural change in an area | Rewrite section in area doc |
| New convention | Add to `## Conventions` of area doc |
| New cross-file gotcha | Add to `## If you touch...` |
| Completed feature | Entry in changelog.md |
| Infrastructure change | Rewrite section in infrastructure.md |
| Normal implementation change | Only changelog.md |

## Research needed

`docs/research-needed.md` tracks open questions that need investigation before a decision
can be made — things the team doesn't know yet and that aren't tied to a specific proposal.
Add an entry BEFORE doing web research so other sessions don't repeat the same search.
Remove entries once answered (move the answer to the relevant area doc or decision).

## Memory vs docs

Project knowledge and personal preferences live in different places:

| Type | Where | Examples |
|------|-------|---------|
| Architecture decisions | docs (area doc `> **Decision:**`) | "sameSite:lax because OAuth callback" |
| Conventions | docs (area doc `## Conventions`) | "Always use component library, never native HTML" |
| Gotchas | docs (area doc `## If you touch...`) | "Change inline script → regenerate CSP hash" |
| Personal preferences | memory | "User prefers Spanish", "commit style" |
| Workflow preferences | memory | "Use /session-close at end" |

If a memory entry contains project knowledge → move it to the relevant doc and remove from memory.
Session-close enforces this at the end of every session.

## Hooks — Two levels

- **blocking_triggers**: migrations, infra → commit blocked without docs
- **warning_triggers**: general code → suggests doc update, doesn't block

## When to split an area doc

Area docs stay **flat** (1 file) while manageable. The `docs/db/` model (1 file per table)
works because tables are independent. Area docs are NOT independent: endpoints depend on
middleware, middleware depends on services.

### Split rule

```
IF an area doc exceeds 350 lines post-compression
AND has 2+ genuinely independent subtopics
   (you don't need to read A to understand B)
THEN:
  1. Verify no code-derivable content remains (compress first)
  2. If still >350 → split into docs/{area}/
  3. index.md has: overview + links + conventions + if-you-touch
  4. Each subtopic.md is self-contained
IF NOT → keep flat
```

350, not 250, because 1 file of 350 lines read once beats 4 files of 80
requiring navigation decisions.

## Detail level per doc type

Not all docs need the same level of detail:

| Doc type | Level | Reason |
|----------|-------|--------|
| Security | High | Highest cost of error. Complete defense model, never trim |
| Design system / Brand kit | Prescriptive | It IS the contract, not documentation of it |
| Backend / Frontend | Standard | Compact index + 1 canonical example + patterns |
| Infrastructure | Standard | Topology diagram + deploy flow |

## Change workflow (SDD)

Significant changes follow the cycle: **propose → implement → archive**.

### What requires a proposal

| Requires proposal | No proposal needed |
|---|---|
| New feature | Simple bugfixes |
| Refactor touching >3 files | Typos |
| Schema change (new migration) | Minor dependency updates |
| New CI/CD workflow | Style adjustments |
| Architecture change | |

### Lifecycle

1. **Propose**: create `docs/changes/{YYYY-MM-DD}-{slug}/proposal.md` from template BEFORE implementing
2. **Review**: user reviews and approves (status: `draft` → `approved`)
3. **Implement**: partial commits ok, status `in-progress`, mark tasks `[x]` in proposal
4. **Close**: when all tasks complete:
   - Integrate relevant content into area docs
   - Add summary to `changelog.md` (≤5 bullets)
   - Update `planning.md`: standalone → delete line; group task → ~~strikethrough~~;
     all group tasks struck → delete entire block.
   - Move folder to `docs/_archive/changes/`

### Connections

```
planning.md (future) ←→ changes/{slug}/proposal.md (in progress) → changelog.md (past)
                                                                   → area docs (reference)
                                                                   → _archive/changes/ (archive)
```

## Adaptation notes

- **Language**: adapt conventions, section names and agent responses to the project's language (defined in CLAUDE.md)
- **CLAUDE.md size limit**: the pre-commit hook uses 20,000 chars (~5,000 tokens) as heuristic. Adjust in `.githooks/pre-commit` if your project uses a different threshold
- **Shell environment**: git-ops agent assumes standard bash. On Windows with Git Bash, add the MINGW64 note to the agent
