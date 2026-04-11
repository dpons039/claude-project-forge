# Change Workflow (SDD)

Every significant change follows the cycle: **propose → implement → archive**.

## Flow

```
planning.md (future) ←→ changes/{slug}/proposal.md (in progress) → changelog.md (past)
                                                                   → area docs (reference)
                                                                   → _archive/changes/ (archive)
```

1. **Propose**: create `docs/changes/{YYYY-MM-DD}-{slug}/proposal.md` copying `_template/`
2. **Review**: user reviews and approves (status: `draft` → `approved`)
3. **Implement**: partial commits ok, status `in-progress`, mark tasks `[x]`
4. **Close**: when all tasks complete:
   - Integrate relevant content into area docs
   - Add executive summary to `docs/changelog.md` (≤5 bullets)
   - Remove items from `docs/planning.md`
   - Move entire folder to `docs/_archive/changes/`

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
├── proposal.md     ← main document (see _template/)
└── (optional attachments: diagrams, CSVs, etc.)
```

## Archive

Completed proposals are moved to `docs/_archive/changes/` keeping
the folder intact. Consult as historical reference for decisions.
