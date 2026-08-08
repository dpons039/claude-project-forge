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

### Decisions → Marker in the area doc, reasoning in `decisions.md`
The area doc where a decision applies carries only a one-line **marker**:
`> **Decision:** (YYYY-MM-DD, D-n) <one-line claim>.` — nothing else, no
trade-off. Every decision carries a short ID — `D1`, `D2`, … — assigned as the
next free number; IDs are never reused, not even those of archived decisions.
**The `D-n` is the pointer**: it means "read `### D-n` in `docs/decisions.md`".

**`decisions.md` is the store, not an index.** The reasoning lives there, as a
`### D-n` subsection per decision, graded by weight:

- **Major** — swapping one library for another, a cross-cutting pattern, an
  architectural choice, or any decision whose *why* needs to name the alternatives
  it measured and rejected: a full block (claim, trade-off, rejected alternatives,
  measurements). If a derivation is huge, the block points at a linked file or the
  proposal rather than inlining it.
- **Minor** — passes the three-part test below but its *why* fits in half a
  sentence and there are no alternatives to document: a single line under the
  heading (claim + reason), no block.

The agent classifies major/minor when it records the decision. When in doubt,
major (keep the reasoning, don't lose it). This split is *how much detail*, on top
of the three-part test which is *whether it's a decision at all* — not a relation.

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

**Passes all three → a `### D-n` in `decisions.md`** (major block or minor line).
Fails one but the value is still non-obvious → it lives in prose in its area doc
(or a live surface — see below), **with no `### D-n`**. The reasoning is never
lost; only *where it lives* changes. A design system generates many borderline
value-choices (a contrast figure, a radius); by this test those are calibration
and stay as prose in the area doc, they don't earn a decision entry.

**Never rewrite the text of a decision.** The only edits ever allowed on an
existing decision are its `Superseded by` / `Refined by` lines.

Two ways a decision can be affected by a later one. Pick by asking whether the
old claim still holds:

| | **Superseded** — the old claim is now false | **Refined** — the old claim still holds, narrowed or extended |
|---|---|---|
| Old `### D-n` | add `**Superseded by D-m (date)**` line to its body | add `**Refined by D-m (date)**` line to its body |
| New `### D-m` | `Supersedes D-n` | `Refines D-n` |
| Old `### D-n` moves | yes → `docs/_archive/decisions.md`, heading and all | **no** — stays in `decisions.md`, still in force |
| Area-doc marker | repoint the old marker at `_archive` | unchanged (the marker still resolves to `decisions.md`) |

Both directions always, in the same edit. A decision that only points forward
leaves the old entry reading as if nothing had happened.

**Consequence — no `Superseded by` ever lives in `decisions.md`.** A superseded
`### D-n` has left for `_archive`. So every `### D-n` still in `decisions.md` is in
force (active, or refined and still standing). "What no longer holds" is read in
`_archive/decisions.md`. An **active** decision carries no status line; a
**refined** one carries `**Refined by D-m**` and stays.

**Only these two relations exist.** Prose reaches for many verbs — reversed,
amended, corrected, revised, extends — and each new label is one more thing to
choose wrong. Map them:

| Prose says | Use | Because |
|---|---|---|
| reverses, undoes, replaces | `Superseded` | the old claim is now false |
| corrects, amends, revises, extends | `Refined` | one figure moves, the claim stands |
| renames a file/section the old one created | `Refined` | nothing it asserted changed |

The nuance ("corrects the 128 kB figure to 118") belongs in the new decision's
own text, where it reads naturally — not in a third label.

```markdown
# area doc — only markers (the D-n resolves to decisions.md)
> **Decision:** (2026-09-02, D14) Containers in development too.
> **Decision:** (2026-05-10, D26) No FKs between staging tables — allows atomic swap.

# decisions.md — the reasoning, one ### per decision (in force only)
### D14 — Containers in development too
Supersedes D7 (see `_archive/decisions.md`). <full block: trade-off, alternatives>

### D26 — No FKs between staging tables
**Refined by D63 (2026-09-02)**
<full block>  ← stays here; the claim still holds, D63 only carves an exception

# _archive/decisions.md — superseded, kept whole (heading included)
### D7 — Containers are production-only
<original block, unchanged>
**Superseded by D14 (2026-09-02)**
```

Never archive a refined decision: D26 above is still the rule, D63 only carves
out an exception to it. Archiving it would delete a claim that is still in force.

**Live surface (an attribute, not a third relation).** A major decision whose
reasoning is *rendered live* in an external surface — a BrandKit MDX page showing
the rule next to its specimen, say — keeps its long-form prose **there**, not in a
full block in `decisions.md`. This is orthogonal to Superseded/Refined: **only
those two relations exist** (a live surface neither replaces nor refines
anything). The decision stays **active and keeps its `### D-n`**; the attribute
changes only *where the block lives*:

- The `### D-n` carries the claim + one line pointing at the live surface (its path
  + the block that shows it), **instead of** the full block.
- Neither the area doc nor `decisions.md` carries a second copy of the prose — a
  value in three places (doc, live prose, rendered proof) is two bugs waiting.
- If the live surface is ever removed with no replacement, `_archive/decisions.md`
  is the fallback: move the `### D-n` there marked **`Detail archived`** — distinct
  from `Superseded`, because the decision is still in force. See the area-doc rule
  `Design system / Brand kit | Prescriptive | It IS the contract` below.

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
  alternative + reason invisible in code + reverting hurts): a one-line marker
  `> **Decision:** (date, D-n) claim` in the area doc + the reasoning as a `### D-n`
  in `decisions.md` (major = block, minor = one line). Fails the test but still
  non-obvious → prose only in the area doc, **no `### D-n`**.
- Decision that replaces an existing one → new `### D-m` + move the old `### D-n`
  (heading and all) to `_archive` with a `Superseded by` line; repoint the old marker
- Decision that refines an existing one → new `### D-m` + `Refined by` line on the
  old `### D-n`, which **stays** in `decisions.md`

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
| New architectural decision (passes the three-part test) | Marker `> **Decision:** (date, D-n)` in the area doc + `### D-n` in decisions.md (major block / minor line) |
| Non-obvious value that fails the test | Prose only in the area doc — **no** `### D-n` |
| Decision replaced (old claim now false) | New `### D-m` + move old `### D-n` (heading and all) to `_archive/decisions.md` with a `Superseded by` line + repoint old marker |
| Decision refined (old claim still holds) | New `### D-m` + `Refined by` line on the old `### D-n`, which **stays** in decisions.md |
| Decision whose reasoning is rendered live (BrandKit MDX) | `### D-n` stays a decision; its body points at the live surface instead of a full block; prose not duplicated |
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

### `decisions.md` size — a dynamic cap, not a fixed number

Because `decisions.md` now holds the reasoning, it grows with the project. A fixed
line cap would either choke a large project or let a small one bloat, so the soft
threshold **scales with the number of area docs**: roughly `base + k × (area docs
in docs/*.md)`. The hook **warns** past the soft threshold (never blocks) and a
high fixed hard cap is the backstop. Past the soft threshold, don't split the
file — instead rotate superseded `### D-n` to `_archive` (they don't belong in the
current store anyway) and make sure minors are one line, not creeping blocks.

## Detail level per doc type

Not all docs need the same level of detail:

| Doc type | Level | Reason |
|----------|-------|--------|
| Security | High | Highest cost of error. Complete defense model, never trim |
| Design system / Brand kit | Prescriptive | It IS the contract, not documentation of it. When it renders a decision's reasoning live, that decision uses the **live-surface** attribute (§ Decisions): its `### D-n` points here, the full block is not duplicated |
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
