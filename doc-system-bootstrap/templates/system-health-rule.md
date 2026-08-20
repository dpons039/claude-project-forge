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
- Each rule ≤ 500 tokens? → if larger, extract logic to a doc. EXCEPTION: the SDD rule
  (`sdd.md`) may exceed it — it is lazy and path-scoped to `docs/changes/**` (where its
  content is exactly what's relevant) and replaces content that used to be eager in
  CLAUDE.md. Do NOT fragment it artificially.
- CLAUDE.md `# LAWS`: still ≤9 laws, each ~4-5 lines, each testable (a sim could detect
  its violation)? A new law → is an old one now redundant? NEVER grow the block past ~9
  without displacing one.
- CLAUDE.md core over ~1.800 tok (run `count-context-tokens.py`)? → move a section to a
  rule/doc. The target is TOKENS, not lines — the LAWS block is many short lines but few
  tokens; don't cut it for a line count.
- MEMORY.md growing? → project knowledge goes to docs, only personal preferences stay in memory

**Verify quarterly (or when degradation detected):**

- Review rules: any without clear trigger? → candidate for removal
- Review skills: any unused in 3+ months? → candidate for removal
- Review MEMORY.md: stale info? → correct or remove
- `docs/changes/{slug}/session.md` is EPHEMERAL (gitignored, live state of one change) — a docs audit must NOT migrate it into `docs/`; it is discarded with its folder
- Audit docs vs code: invoke doc-updater subagent across the repo
- Check doc sizes: `find docs/ -maxdepth 1 -name "*.md" -exec wc -l {} + | sort -rn | head -10`

**Checklist for new configuration:**

- New rule: ALWAYS path-scoped + procedural, ≤500 tokens (SDD rule excepted, see above)
- New skill: only if used ≥1/month, doesn't contradict conventions, respects token budget
- New doc: update docs/README.md
- New memory entry: only if info does NOT exist in CLAUDE.md, rules, or docs

## Skills with verbal trigger

<!-- ADAPT: List your project's slash-command skills here -->
**`session-close`** — invoke at end of every session (`/session-close`).
Order: area docs → proposals → planning → changelog → memory → git status → summary.

**`brandkit-manager`** — if the skill is installed: **verbal maintenance triggers only** —
"audit the brandkit", "add a block", "brandkit is stale". Operations: init-docs /
init-page / update / audit (ambiguous trigger → audit, read-only). The *build-time*
trigger (invoke when building/changing UI) lives in `frontend.md`, which loads on
frontend paths — this rule loads only on config, so it cannot fire during UI work.
