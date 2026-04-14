---
description: Cross-cutting skills for writing code (clean-code, TDD, verification, code review, planning)
---

# Code Quality — Cross-cutting Skills

These skills apply to **any code change** in the project, regardless of the area. Stack rules
(frontend, backend, database, etc.) add domain-specific skills on top; this rule is the baseline.

## Before starting to write

- **`writing-plans`** — for multi-step tasks (≥3 files or logic with several decisions). Output to `docs/changes/{slug}/plan.md` for complex flow, or inline in the proposal for standard flow. See `docs/changes/README.md`.
- **`brainstorming`** — before complex proposals (multi-area, ambiguous scope).

## When writing or refactoring code

- **`clean-code`** — naming, short functions, SOLID principles, separation of concerns. Apply when introducing new code and when refactoring existing code.
- **`test-driven-development`** — write the test before the implementation when adding new behavior (does NOT apply to trivial fixes or config changes).

## When executing a plan

- **`executing-plans`** — when there's an approved `plan.md`. Walk phases with checkpoints.
- **`subagent-driven-development`** — when the plan has independent tasks parallelizable in the same session.
- **`dispatching-parallel-agents`** — for 2+ tasks without shared state.

## On failures / unexpected behavior

- **`systematic-debugging`** — MANDATORY before proposing a fix. Investigate root cause in Phase 1, do not patch. See `.claude/rules/debugging.md`.

## Before declaring work complete

- **`verification-before-completion`** — run `build`, `test`, `lint` and confirm output BEFORE marking tasks done or asking for a commit. No claim without evidence.
- **`requesting-code-review`** — before merging large features, ask for review with `requesting-code-review` (separate Claude instance, clean context).

## When receiving review feedback

- **`receiving-code-review`** — verify each suggestion technically; do not implement blindly.

## Conventions

- Significant work (≥3 files, new feature, refactor, migration) → follow the SDD cycle: proposal in `docs/changes/`, plan, implement, close. See `docs/changes/README.md`.
- Reuse before creating: `Glob`/`Grep` to find existing utilities before writing new ones.
- No "boy scout" cleanup in fix commits (a fix is a fix; refactors go separately).
- Comments only when the "why" is not obvious from the name/structure.

## If you touch...

Any code change → check whether the stack skills of the area also apply:
- Frontend → see `.claude/rules/frontend.md`
- Backend → see `.claude/rules/backend.md`
- Database (SQL/migrations) → see `.claude/rules/database.md`
- Tests → see `.claude/rules/testing.md`
- Security-sensitive → see `.claude/rules/security.md`
- Infra (Docker, deploy) → see `.claude/rules/infrastructure.md`
