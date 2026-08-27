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
- CLAUDE.md `# LAWS`: still ≤10 laws, each ~4-5 lines, each testable (a sim could detect
  its violation)? A new law → is an old one now redundant? NEVER grow the block past ~10
  without displacing one (the compliance cliff is ~15; 10 is the working ceiling). LAW10
  (USE-THE-PROCESS) is the momentum/process-skip anchor — do not merge it away.
- CLAUDE.md over **3.000 tok** (run `count-context-tokens.py` — it is the figure that
  tool flags, and it measures the WHOLE file: there is no "core" it can see)? → move a
  section to a rule/doc. The pre-commit's hard block is 20.000 chars (~5.000 tok); 3.000
  is where you act, 5.000 is where you are stopped. The target is TOKENS, not lines —
  the LAWS block is many short lines but few tokens; don't cut it for a line count.
- MEMORY.md growing? → project knowledge goes to docs, only personal preferences stay in memory

**Verify quarterly (or when degradation detected):**

- Review rules: any without clear trigger? → candidate for removal
- Review skills: any unused in 3+ months? → candidate for removal. Also: any skill named in
  a rule with a VAGUE trigger (a topic list, "activate by trigger") rather than a concrete
  "when you do X → invoke"? → sharpen it. A vague trigger is skipped under momentum (LAW10);
  a skill nobody's rule fires sharply on is dead weight either way.
- Review MEMORY.md: stale info? → correct or remove
- `docs/changes/{slug}/session.md` and `.attempt-counter.json` are EPHEMERAL (gitignored,
  live state) — a docs/config audit must NOT migrate them into `docs/`; they are discarded, not curated
- Audit docs vs code: invoke doc-updater subagent across the repo
- Check doc sizes: `find docs/ -maxdepth 1 -name "*.md" -exec wc -l {} + | sort -rn | head -10`

**Checklist for new configuration:**

- New rule: ALWAYS path-scoped + procedural, ≤500 tokens (rules must be clear; see the ≤500 line above)
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
