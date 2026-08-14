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

## Present state only

Area docs describe **what exists now**. Unbuilt or planned work appears as a
"Not implemented yet" line + pointer to its proposal in `docs/changes/` — never
specified in the area doc as if it existed. Specs for future phases live in
their proposals. Post-mortems and incident write-ups get their own linked file
(or the changelog entry); the area doc keeps the resulting rule, in 1–3 lines.

## Content types and rules

### Architecture + Patterns → REWRITE when changed
What exists and how it works. Compact indexes. 1 canonical example per pattern.
The agent rewrites sections with current state — never appends.

### Conventions → Stable, rarely change
Team rules. Live in `## Conventions` section of each area doc.
Agent doesn't modify without explicit instruction.

### Decisions → live only in `docs/decisions.md`
A decision lives in **exactly one place**: a `### D-n` block in `docs/decisions.md`.
No marker in the area doc, no `D-n` reference in code — a decision's *consequences*
are documented wherever they land (a convention, an "If you touch…" gotcha, the code
itself), but the decision and its ID stay in `decisions.md`. Find decisions with
`grep '^### D' docs/decisions.md`. Every decision has a short ID — `D1`, `D2`, … —
the next free number; IDs are never reused, not even archived ones.

An entry is **as long as its reasoning requires**: a single line if the *why* is a
line; a block with trade-off, rejected alternatives and measurements if that's what
the *why* contains. No major/minor grade to assign — the content sets the length.

**Is it a decision? The three-part test.** A change earns a `### D-n` only if it
passes all three — otherwise it is a fact, a value, or calibration, and it does
not belong in `decisions.md`:

1. **Real alternative** — there were ≥2 viable paths. If only one existed, it is
   a fact, not a decision. Applying an external standard as-is (WCAG, NIST, a
   vendor spec) is compliance, not a choice — **unless you chose to deviate from
   it**, and then the deviation is what's recorded.
2. **Reason invisible in the code** — the *why* cannot be read off the code.
   Record only what the code cannot say: the trade-off you rejected, the external
   constraint, the "looks like a bug but is intentional".
3. **Reverting hurts** — undoing it is not a find-replace. If reverting forces a
   data re-migration, a security re-audit, or breaks a contract → architecture.
   If it's changing a px or a hex → calibration.

**Passes all three → a `### D-n` in `decisions.md`.** Fails one but the value is
still non-obvious → it lives in prose in its area doc, **with no `### D-n`**. The
reasoning is never lost; only *where it lives* changes. A design system generates
many borderline value-choices (a contrast figure, a radius); by this test those are
calibration and stay as prose in the area doc, they don't earn a decision entry.

**Never rewrite the text of a decision.** The only relation is **supersede**
(archive-and-replace) — when a later decision changes an earlier one:

1. New `### D-m` in `decisions.md` with a `Supersedes D-n` line, restating the FULL
   current claim (whatever the old one still asserted, plus the change).
2. Add `**Superseded by D-m (date)**` to the old `### D-n` body.
3. **Move the old `### D-n` (heading and all) to `docs/_archive/decisions.md`**,
   text intact.

**Consequence — no `Superseded by` ever lives in `decisions.md`.** A superseded
`### D-n` has left for `_archive`. So every `### D-n` still in `decisions.md` is in
force; "what no longer holds" is read in `_archive/decisions.md`. An in-force
decision carries no status line. The nuance a change carries ("corrects the 128 kB
figure to 118", "carves out an exception") belongs in the new decision's own text,
where it reads naturally.

```markdown
# decisions.md — the ONE home, one ### per decision (in force only)
### D14 — Containers in development too
Supersedes D7 (see `_archive/decisions.md`). <trade-off, rejected alternatives>

# _archive/decisions.md — superseded, kept whole (heading included)
### D7 — Containers are production-only
<original block, unchanged>
**Superseded by D14 (2026-09-02)**
```

### Cross-file dependencies → `## If you touch...`
"If you change X, also update Y." Each area doc has this section at the end.

### Status → Flows and rotates
`changelog.md`: rotation **by size** — over 500 lines, move the oldest entries
to `_archive/changelog/` until under; entries ≤5 bullets of one line each.
`planning.md`: hard cap **100 lines**, current phase only (full phase plan and
future scope live in `roadmap.md`); entries 1–2 lines + pointer, no inline
diagnoses or narrative. Only `[ ]` pending tasks. Never `[x]`.
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
- New architectural decision → **only if it passes the three-part test** (real
  alternative + reason invisible in code + reverting hurts): a `### D-n` in
  `docs/decisions.md` — its one and only home (no area-doc marker, no `D-n` in code).
  Fails the test but still non-obvious → prose only in the area doc, **no `### D-n`**.
- Decision that replaces an existing one → new `### D-m` (`Supersedes D-n`) + move
  the old `### D-n` (heading and all) to `_archive` with a `Superseded by` line

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
| New architectural decision (passes the three-part test) | A `### D-n` in decisions.md — its only home (no area-doc marker, no `D-n` in code) |
| Non-obvious value that fails the test | Prose only in the area doc — **no** `### D-n` |
| Decision replaced (old claim now false) | New `### D-m` (`Supersedes D-n`) + move old `### D-n` (heading and all) to `_archive/decisions.md` with a `Superseded by` line |
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
| Architecture decisions | docs (`### D-n` in `decisions.md`) | "sameSite:lax because OAuth callback" |
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

### `decisions.md` size — self-limiting, one fixed backstop

`decisions.md` holds only in-force decisions: the moment one is superseded its
`### D-n` **leaves for `_archive`**, so the store never accumulates history and its
size tracks live complexity, not project age. No scaling formula — the hook only
warns past a single high fixed backstop. If it warns, a superseded entry never left
for `_archive` — move it; the store is not the place to split.

## Detail level per doc type

Not all docs need the same level of detail:

| Doc type | Level | Reason |
|----------|-------|--------|
| Security | High | Highest cost of error. Complete defense model, never trim |
| Design system / Brand kit | Prescriptive | It IS the contract, not documentation of it. A decision behind a rule it renders still lives as a `### D-n` in `decisions.md` — the page may link to that decision, but never holds the decision's only copy |
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
