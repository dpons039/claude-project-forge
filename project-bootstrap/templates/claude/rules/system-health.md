---
description: Guardrails for keeping Claude Code configuration clean and scalable
paths:
  - "CLAUDE.md"
  - ".claude/**/*"
  - ".claudeignore"
---

# System Health — Guardrails

Documentation system principles: `docs/doc-system.md`. When modifying Claude Code config
(.claude/, CLAUDE.md, MEMORY.md):

**Verify before committing:**

- Duplication between CLAUDE.md, MEMORY.md and rules? → remove the redundant copy
- New rules have specific paths? → NEVER create rules with paths: ["**/*"]
- New rules are procedural? → pattern: "after doing X, update Y" (not just "read Z")
- Each rule < 350 tokens? → if larger, extract logic to a doc
- CLAUDE.md exceeds token budget? → move content to path-scoped rules
- MEMORY.md growing? → project knowledge goes to docs, only personal preferences stay in memory

**Verify quarterly (or when degradation detected):**

- Review rules: any without clear trigger? → candidate for removal
- Review skills: any unused in 3+ months? → candidate for removal
- Review MEMORY.md: stale info? → correct or remove
- Audit docs vs code: invoke doc-updater subagent across the repo
- Check doc sizes: `find docs/ -maxdepth 1 -name "*.md" -exec wc -l {} + | sort -rn | head -10`

**Checklist for new configuration:**

- New rule: ALWAYS path-scoped + procedural, <350 tokens
- New skill: only if used ≥1/month, doesn't contradict conventions, respects token budget
- New doc: update docs/README.md
- New memory entry: only if info does NOT exist in CLAUDE.md, rules, or docs

## Skills with verbal trigger

<!-- ADAPT: List your project's slash-command skills here -->
**`session-close`** — invoke at end of every session (`/session-close`).
Order: area docs → proposals → planning → changelog → memory → git status → summary.
