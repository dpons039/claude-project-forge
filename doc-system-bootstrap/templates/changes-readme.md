# Change Workflow (SDD)

Every significant change follows the cycle: **propose → plan → implement → close**.

## Flow

```
planning.md (future) ←→ changes/{slug}/proposal.md (spec or spec+plan)
                         changes/{slug}/plan.md    (complex only) → changelog.md (past)
                                                                  → area docs (reference)
                                                                  → _archive/changes/ (archive)
```

There are two flow levels depending on change complexity:

### Standard (clear scope, ≤5 files, known pattern)

1. **Propose + Plan** (`writing-plans`): create `proposal.md` with inline plan → user reviews and approves
2. **Implement** (`executing-plans` or `subagent-driven-development` + `test-driven-development`): status `in-progress`, commits at session close
3. **Close** (`verification-before-completion` + `requesting-code-review`): when complete:
   - Integrate relevant content into area docs
   - Add executive summary to `docs/changelog.md` (≤5 bullets)
   - Remove items from `docs/planning.md`
   - Move the entire folder to `docs/_archive/changes/`

### Complex (multi-area, new architecture, ambiguous scope)

1. **Propose** (`brainstorming`): create `proposal.md` as spec → user reviews and approves
2. **Plan** (`writing-plans`): create `plan.md` in the same folder → user reviews and approves
3. **Implement** (`executing-plans` or `subagent-driven-development` + `test-driven-development`): status `in-progress`, commits at session close
4. **Close** (`verification-before-completion` + `requesting-code-review`): when complete:
   - Integrate relevant content into area docs
   - Add executive summary to `docs/changelog.md` (≤5 bullets)
   - Remove items from `docs/planning.md`
   - Move the entire folder to `docs/_archive/changes/`

> **Criterion:** if you already know what to build → standard. If you need to explore alternatives or scope is unclear → complex.

## Mandatory superpowers per phase

| Level | Phase | Superpowers | Output |
|---|---|---|---|
| **Standard** | Propose + Plan | `writing-plans` | `proposal.md` with inline plan |
| **Standard** | Implement | `executing-plans` or `subagent-driven-development` + `test-driven-development` | Code ready, commits at close |
| **Standard** | Close | `verification-before-completion` + `requesting-code-review` | Verification + archive |
| **Complex** | Propose | `brainstorming` | `proposal.md` (spec) |
| **Complex** | Plan | `writing-plans` | Separate `plan.md` |
| **Complex** | Implement | `executing-plans` or `subagent-driven-development` + `test-driven-development` | Code ready, commits at close |
| **Complex** | Close | `verification-before-completion` + `requesting-code-review` | Verification + archive |

Transversal (any phase): `systematic-debugging` on failures, `dispatching-parallel-agents` when tasks are independent.

> **Domain skills and dedicated agents** are mandatory per phase according to the work area. Rules loaded by context (`.claude/rules/`) indicate which skills and agents to activate — not repeated here.

## What counts as "significant change"

| Requires proposal | No proposal needed |
|---|---|
| New feature | Simple bugfixes |
| Refactor touching >3 files | Typos |
| Schema change (new migration) | Minor dependency updates |
| New CI/CD workflow | Style adjustments |
| Architecture change | |

## Proposal structure

```
docs/changes/{YYYY-MM-DD}-{slug}/
├── proposal.md     ← spec or spec+plan inline (see _template/)
├── plan.md         ← complex flow only (output of writing-plans)
└── (optional attachments: diagrams, CSVs, etc.)
```

## Archive

Completed proposals are moved to `docs/_archive/changes/` keeping
the folder intact. Consult as historical reference for decisions.
