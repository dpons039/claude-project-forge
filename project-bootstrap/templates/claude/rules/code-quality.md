---
description: Cross-cutting skills for writing code (clean-code, TDD, verification, code review, planning)
---

# Code Quality — Cross-cutting Skills

These skills apply to **any code change** in the project, regardless of the area. Stack rules
(frontend, backend, database, etc.) add domain-specific skills on top; this rule is the baseline.

## Before starting to write

- **`writing-plans`** — for multi-step tasks (≥3 files or logic with several decisions). Output to `docs/changes/{slug}/plan.md` for complex flow (seed it from `_template/plan.md` — a bridge that points Spec at the proposal, gates on LAW8 `verified`, and keeps per-task commits owner-gated; the skill fills the rest below the `---`), or inline in the proposal for standard flow. See `docs/changes/README.md`.
- **`brainstorming`** — before complex proposals (multi-area, ambiguous scope).

## When writing or refactoring code

- **`clean-code`** — naming, short functions, SOLID principles, separation of concerns. Apply when introducing new code and when refactoring existing code.
- **`test-driven-development`** — write the test before the implementation when adding new behavior (does NOT apply to trivial fixes or config changes). **Presentation-layer UI is a named exception:** for a screen/page or a purely visual component, drive it with a behaviour/integration test written against what the user observes (renders, submits, shows an error), not a unit test written before the markup exists. Test-first still governs the logic underneath — stores, hooks, services, pure functions. The point is to stop deferring screens because unit-first fits them badly, not to skip testing them.

## When executing a plan

- **`executing-plans`** — when there's an approved `plan.md`. Walk phases with checkpoints.
- **`subagent-driven-development`** — when the plan has independent tasks parallelizable in the same session.
- **`dispatching-parallel-agents`** — for 2+ tasks without shared state.

## On failures / unexpected behavior

- **`systematic-debugging`** — before proposing a fix for anything non-trivial or
  already-attempted, investigate root cause first (don't patch blind). When it
  applies and when a typo is just a typo: see `.claude/rules/debugging.md`.

## Before declaring work complete

- **`verification-before-completion`** — before declaring something done, run the
  verification commands **the project actually declares** and confirm their output.
  If there are none, or the change isn't executable (doc, config), say so — don't
  invent a verification. And don't fire build/test on an approach the user hasn't
  validated yet (a rejected approach makes that whole run wasted).
- **`requesting-code-review`** — before merging large features, ask for review with `requesting-code-review` (separate Claude instance, clean context).

## When receiving review feedback

- **`receiving-code-review`** — verify each suggestion technically; do not implement blindly.

## Conventions

- Significant work (≥3 files, new feature, refactor, migration) → follow the SDD cycle: proposal in `docs/changes/`, plan, implement, close. See `docs/changes/README.md`.
- Reuse before creating: `Glob`/`Grep` to find existing utilities before writing new ones.
- No "boy scout" cleanup in fix commits (a fix is a fix; refactors go separately).
- Minimum sufficient complexity: write the simplest code that correctly solves it; don't abstract before you need to. Clever loses to obvious.
- Explain a decision in one line with the real trade-off, not just what — never verbose.
- Comments only when the "why" is not obvious from the name/structure.
- Never cite a decision ID (`D-n`) in code or comments. A decision lives only as a
  `### D-n` in `docs/decisions.md`; code carries its *consequence*, not a back-reference
  to the decision. (The `why` belongs in the decision, discoverable by `grep`, not
  pinned to a line that will drift.)

## Delegation — how to act when delegating

The `When executing a plan` section decides *whether* to delegate (inline vs
subagent-driven). This is *how*, once you do:

- **Threshold:** delegate only when the task spans **≥3 independent files**, or a broad
  search whose result fits in a summary. Otherwise inline — a subagent that reads code to
  hand it back compressed loses more signal than it saves.
- **Context restrictions in the prompt:** `.claudeignore` does NOT block a subagent's
  direct Read — state restrictions in its prompt. Minimum: "Use `docs/` as source of
  truth. DO NOT read files excluded in `.claudeignore`." Name the skills it must load.
- **Never delegate the commit.** Main context proposes the message and runs `git add` +
  `git commit`. `git-ops` is read-only.
- **Model per task:** Explore/read-only → haiku. Scoped implementation → sonnet.
  Design/ambiguous → the session model or Plan.

## If you touch...

Any code change → check whether the stack skills of the area also apply:
- Frontend → see `.claude/rules/frontend.md`
- Backend → see `.claude/rules/backend.md`
- Database (SQL/migrations) → see `.claude/rules/database.md`
- Tests → see `.claude/rules/testing.md`
- Security-sensitive → see `.claude/rules/security.md`
- Infra (Docker, deploy) → see `.claude/rules/infrastructure.md`
