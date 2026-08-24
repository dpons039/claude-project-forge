# Change Workflow (SDD)

Every significant change follows the cycle: **propose → plan → implement → close**.
LAW8 is the trigger (notable change → verified proposal+plan first; threshold by impact,
not file count). Full operating detail is in `.claude/rules/sdd.md`; this README is the
long reference.

## Artifacts per change — `docs/changes/{slug}/`

One folder per change holds up to four files:

| File | Persists | Role |
|---|---|---|
| `idea.md` | git-tracked | intention (WHAT/WHY) for a FUTURE phase — no verified premises |
| `proposal.md` | git-tracked | spec + `file:line` premises verified, scoped BEFORE starting |
| `plan.md` | git-tracked | step list (complex flow only) |
| `session.md` | **gitignored** | LIVE state during execution, ordered by reading urgency (awaiting/now/live decisions); pruned on the event, not a history log |

**idea → proposal.** A future phase is born `idea.md` (Status: `idea`) — WHAT/WHY, which
does not go stale (it does not depend on the code). Writing a full proposal far ahead is
the mistake: a proposal fixes premises against the code NOW. When the phase's turn comes,
**promote in place**: copy `_template/proposal.md`, port WHAT/WHY, verify every premise
against the code now (approval gate), fill the "TBD until promoted" sections. Never
implement from an `idea.md`. `roadmap.md` lists ideas; only the active phase has a proposal.

**session.md** bridges compactions (the conversation compacts and drops the "why" of past
decisions; the file is re-read from disk — LAW5). Create it from `_template/session.md`
when you open the `{slug}/`, alongside the proposal. It is ordered by reading urgency
(AWAITING OWNER → NOW → live decisions first, so a post-compaction re-read hits the
blocking gate and the next step, not buried history). A line stays only while it is LIVE:
the moment a chunk closes, a decision is superseded, or a render is approved, it LEAVES —
durable outcomes **graduate** to `decisions.md`/proposal/area docs, scaffolding is
**deleted**. Prune on that event, NOT "at close" (a long front never closes and the file
only grows). There is no line cap — size is a consequence of what is still live.
`planning.md` stays project-level
`[ ]` pending only.

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
2. **Verify** (approval gate — see below): re-check the proposal's premises against the repo → status `verified`
3. **Implement** (`executing-plans` or `subagent-driven-development` + `test-driven-development`): status `in-progress`, commits at session close
4. **Close** (`verification-before-completion` + `requesting-code-review`): when complete:
   - Integrate relevant content into area docs
   - Add executive summary to `docs/changelog.md` (≤5 bullets)
   - Remove items from `docs/planning.md`
   - Move the entire folder to `docs/_archive/changes/`

### Complex (multi-area, new architecture, ambiguous scope)

1. **Propose** (`brainstorming`): create `proposal.md` as spec → user reviews and approves
2. **Plan** (`writing-plans`): create `plan.md` in the same folder → user reviews and approves
3. **Verify** (approval gate — see below): re-check every premise against the repo → status `verified`
4. **Implement** (`executing-plans` or `subagent-driven-development` + `test-driven-development`): status `in-progress`, commits at session close
5. **Close** (`verification-before-completion` + `requesting-code-review`): when complete:
   - Integrate relevant content into area docs
   - Add executive summary to `docs/changelog.md` (≤5 bullets)
   - Remove items from `docs/planning.md`
   - Move the entire folder to `docs/_archive/changes/`

> **Criterion:** if you already know what to build → standard. If you need to explore alternatives or scope is unclear → complex.

> **Vertical slice:** a Complex change scoped to one user-facing surface —
> the minimum backend it needs plus its real frontend, together — shipped ahead
> of completing the rest of that area's backend. Same cycle, no new level or
> template; its `proposal.md` declares the "minimal backend + real frontend" cut
> and what defers to the later full-backend phase. Use it when breadth-first
> backend work would otherwise leave a headline screen an empty placeholder;
> breadth-first stays the default everywhere else.

## Approval gate — re-verify before implementing

A proposal/plan is edited many times before it is approved. Each edit can leave a
`file:line` reference stale, a number that no longer adds up, or two sections that
now contradict each other. **Between approval and implementation, re-check every
verifiable premise against the repo _now_ — not as it was when written:**

- For each `file:line` reference, each quoted line, and each "exists / doesn't
  exist / is identical" claim → **read the file and confirm** (read it, don't
  `grep`/`sed` a single line — the contradiction usually lives in the adjacent
  context; see `.claude/rules/code-search.md` § Read vs search).
- A premise that no longer holds invalidates its task → fix the proposal **before**
  implementing, not during.
- Only then set `Status: verified`. **Never implement from `approved` — only from
  `verified`.** `verified` is the mechanical mark that the premises were re-checked,
  not a judgement call.

Cost is proportional: a 2-task proposal is a minute; a 20-task one earns the full
gate. This is enforced by process, not a hook — a hook cannot read a file and judge
whether a premise still holds.

## Mandatory superpowers per phase

| Level | Phase | Superpowers | Output |
|---|---|---|---|
| **Standard** | Propose + Plan | `writing-plans` | `proposal.md` with inline plan |
| **Standard** | Verify | (read the files — approval gate) | `Status: verified` |
| **Standard** | Implement | `executing-plans` or `subagent-driven-development` + `test-driven-development` | Code ready, commits at close |
| **Standard** | Close | `verification-before-completion` + `requesting-code-review` | Verification + archive |
| **Complex** | Propose | `brainstorming` | `proposal.md` (spec) |
| **Complex** | Plan | `writing-plans` | Separate `plan.md` |
| **Complex** | Verify | (read the files — approval gate) | `Status: verified` |
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
