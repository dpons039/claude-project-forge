---
description: Change workflow (SDD) — when and how significant changes get a proposal/plan, how session.md tracks live state, concept→proposal promotion, doc-check bypass. Loads when working on changes.
paths:
  - "docs/changes/**"
  - "docs/planning.md"
  - "docs/roadmap.md"
---

# Change Workflow (SDD) — operating detail

LAW8 is the trigger (a notable change → verified proposal+plan before implementing;
threshold by impact, not file count). This rule is the HOW. Full flow, levels,
approval gate and the superpowers-per-phase table live in `docs/changes/README.md` —
read it when starting a change; this rule is the cargable hook + the parts that used
to sit in CLAUDE.md.

## Artifacts in `docs/changes/{slug}/`

One folder per change. It holds up to four files:

| File | Persists | Role |
|---|---|---|
| `concept.md` | git-tracked | intention: WHAT/WHY, no verified premises (a future phase; Status: `idea`) |
| `proposal.md` | git-tracked | spec + `file:line` premises verified, scoped BEFORE starting |
| `plan.md` | git-tracked | step list (complex flow only) |
| `session.md` | **gitignored** | LIVE state during execution, ordered by reading urgency (awaiting/now/live decisions); pruned on the event, not a history log |

`{slug}` = `{YYYY-MM-DD}-{short-slug}`. Several folders can coexist, but LAW9 says
work them one at a time; parallel folders exist only for a user-ordered pause.

## concept → proposal (promotion)

A future phase is born as `concept.md` (Status: `idea`) — it captures WHAT/WHY, which
does not go stale because it does not depend on the state of the code. Writing a full
`proposal.md` far ahead is the mistake: a proposal fixes `file:line` premises against
the code as it is NOW, so a phase implemented months later would be born stale.

When a phase's turn comes → **promote in place** (same folder):
1. Copy `_template/proposal.md` → `proposal.md`.
2. Port WHAT/WHY from `concept.md` (don't rewrite it — it already holds the intention).
3. **Verify every premise against the code now** (this IS the approval gate — read
   the files, don't grep a line; `Status: draft → approved → verified → in-progress`).
4. Fill the premise sections the concept left as "TBD until promoted".

**Staleness is not only a concept→proposal problem.** A proposal marked `approved` weeks
ago can go stale too: the code moved under it. `approved` is NOT a licence to implement
— only `verified` is, and `verified` means the premises were re-checked against the code
**as it stands right now**. Before entering `in-progress`, if any time has passed or the
code may have changed since approval, re-verify (re-read and re-quote each `file:line`
claim, don't assume it still holds) and only then advance to `verified`. The user saying
"implement the approved proposal" does not skip this — "approved" is their word for a
stage, not a waiver of the gate.

`concept.md` stays as the record of origin (or is archived at close). **Never implement
from a `concept.md`** — an unpromoted concept has no verified premises. `roadmap.md` lists
future phases; only the active phase has a proposal.

## plan.md — the durable step list (complex flow only)

Authored by `writing-plans`, seeded from `_template/plan.md`. The template is a minimal
bridge, not a second copy of the skill's skeleton: it reorders the header so the binding
block leads (Spec → this slug's `proposal.md`, the LAW8 `verified` gate, then Global
Constraints), and `writing-plans` fills the File map / Tasks / Verification / Self-Review
below the `---`, adapted to the real stack (not the skill's Python/pytest examples).

- **It argues FROM the proposal.** `Spec:` points at `./proposal.md`; the proposal is the
  verified spec, the plan is only the how. Don't restate the spec or its premises here —
  that is the proposal↔plan non-overlap the flow-selection comment already sets.
- **It is durable, git-tracked — NOT session.md.** No live state, no run status, no commit
  SHAs, no dated follow-ups. A plan.md that fills with `[x] DONE (sha)` and "status at a
  glance" has drifted into session.md's job; that live state belongs in session.md and is
  pruned there.
- **Commits stay owner-gated.** The skill's per-task `Commit` step is a SUGGESTED point,
  not an automatic action — executing it waits for the owner's word (Autonomy), and a UI
  change waits for the owner's render approval first (LAW2). The Global Constraints block
  carries this line so it governs every task.

## session.md — live state (LAW5)

Create it from `_template/session.md` when you open the `{slug}/`. It is the bridge
across compactions: the conversation compacts and takes the "why" of past decisions
with it, but this file is re-read from disk.

- **Ordered by reading urgency.** The sections run AWAITING OWNER → NOW → Live
  decisions → Discarded → Goal → Chunks → Files. What blocks or is next is at the TOP,
  because after a compaction LAW5 re-reads top-down — the blocking gate and the next
  step must land first, not be buried. Each section carries its own one-line legend
  (a jump straight to a section still explains what belongs there).
- **A line earns its place only if it is LIVE** — something you need for the next step.
  The criterion is nature, NOT size: a genuinely complex change may need many live
  lines, a simple one very few. Size is a consequence, never a target (there is no
  line cap — a cap was the old rule and it failed; a front that never closed only grew).
- **Prune on the event, not "at close".** The moment something stops being live —
  a chunk closes, a decision is superseded, a render is approved — it LEAVES the file
  right then (don't wait for the front to close; a long front never closes and the file
  only grows):
  - **durable** (a decision that still rules, a why that matters beyond this front) →
    **graduate** to `decisions.md` / the proposal / an area doc.
  - **scaffolding** (a done chunk, an approved render, an attempt already superseded by
    one that stuck) → **delete** it. session.md is not the history log.
- **Discarded stays, but compressed:** an approach rejected in THIS front lives as ONE
  line (what + why) so it isn't retried — never the narrative of how it was discovered.
- **Chunks are an index:** `[x]` done / `[ ]` pending, checkboxes only. The chunk's
  detail already graduated or was deleted; the checkbox is all that remains here.
- **AWAITING OWNER is the blocking-gate section.** A UI change waits there until the
  owner has seen the render (LAW2) — cleared when approved; that gate is what keeps
  unreviewed work out of a commit.
- `planning.md` stays project-level `[ ]` pending only; the fine progress of the
  active change lives in its `session.md`, not in planning.md.

## Greenfield mode

While the codebase is young (no stable base to break — roughly, before the first
deployed release), every task being "significant" makes the full cycle over-fire.
Use the light cycle: short proposal (≤1 page) → implement → close. Save `brainstorming`
+ full plans for genuinely ambiguous scope. The full cycle earns its cost once changes
land on a stable base. Greenfield still means a proposal — never none.

## Superpowers output routing

Superpowers skills default to `docs/superpowers/{plans,specs}/`; this project overrides
that (CLAUDE.md/rules win):
- `writing-plans` → `docs/changes/{slug}/plan.md`
- `brainstorming` (final spec) → `docs/changes/{slug}/proposal.md`
- Never write to `docs/superpowers/plans/` or `.../specs/`
- Create the `{slug}` folder if missing before writing
- Ephemeral brainstorm server state: `.superpowers/brainstorm/` (gitignored)

## SKIP_CHECKS — the work-in-progress commit switch (must stay unambiguous)

A per-block commit in a long session is a CHECKPOINT, not a deliverable — an intermediate
state of a multi-task plan is legitimately type-incomplete or carries unused scaffolds
(writing-plans / TDD produce exactly that). `SKIP_CHECKS=1 git commit` relaxes the
COMPLETENESS gates for that checkpoint:

- **Skipped outright:** the doc-check, the `planning.md [x]` gate, the CLAUDE.md-size gate,
  and the test suite (a checkpoint doesn't pay for tests).
- **Run but do NOT block (warn only):** the language checks (type-check, lint, dependency
  audit) — the pre-commit verdict still shows the checkpoint's real state, it just doesn't
  stop the commit.
- **ALWAYS enforced (outside this flag's scope):** the secret-scanner. A leaked secret is
  irreversible in git history, so it is an invariant, never relaxed by any flag.

The point: `SKIP_CHECKS` skips *completeness*, never *safety*. A later commit WITHOUT the
flag must be clean — the checkpoint's warn-only type/lint output is the signal of what is
still unfinished.

Two ways to trigger it, both requiring explicit owner authorization — Claude NEVER sets the
var or creates the file on its own. **If the owner authorizes it in the conversation, that
condition is met** — apply it and commit in one step, without asking again:

- **Env var `SKIP_CHECKS=1`** — transient: `SKIP_CHECKS=1 git commit -m "..."`. Nothing
  persists. This is the full WIP-commit switch (relaxes all the completeness gates above).
- **File `.claude/skip-doc-authorized`** — a one-shot token for the narrower case of
  skipping the DOC-CHECK only, without the env var. The doc-check consumes it (auto-deletes
  on the next commit), so it never survives to bypass a later one.

There is NO standing permission for either — every WIP commit gets an explicit owner OK.

## Known limits (accepted)

The doc-check trades precision for cost; two gaps are known and accepted, not bugs to fix:

- **Coverage = the expected doc is STAGED, not that it was meaningfully updated.** Staging
  any change to the required doc (even one character) satisfies its trigger; the hook does
  not validate the doc's content against the code change. The author is trusted here.
- **The index check is SUBSTRING-based.** A doc counts as indexed if its path or basename
  appears anywhere in `docs/README.md`'s text. Loose by design — a real index entry is
  expected regardless; a coincidental substring can pass, an unusual path can miss.

## Enforcement

By process, not a hook (a hook cannot read a file and judge whether a premise still
holds). Config paths (anything starting with `.`) are outside the SDD — those go
through `/project-bootstrap` mode 3.
