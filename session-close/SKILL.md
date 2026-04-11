---
name: session-close
description: "End-of-session checklist. Use when the user says 'done', 'wrap up', 'session close', 'acabamos', 'fin de sesión', 'terminamos', 'cerramos', or indicates the conversation is ending. Runs a structured close-out: docs, planning, changelog, memory, git, summary. Always trigger on session-ending phrases — even if the user says 'just commit and close', run the full checklist."
---

# Session Close

End-of-session protocol. Execute ALL steps in order, autonomously and without pausing for confirmation.

## Step 1 — Area docs (only if architectural change)

Review session changes against the doc-updater checklist:

**DO update area doc if there was:**
- New file, module, route, or service → add to compact index
- New pattern others should follow
- Change to an existing convention
- New cross-file dependency → § If you touch...
- Architectural decision → inline with `> **Decision:**` + entry in `decisions.md`

**DO NOT update area doc if there was only:**
- Value change, bug fix, internal refactor
- New props/params/types
- New tests
- New item in existing domain (only 1 line to compact index)

**Before adding content to an area doc, verify:**
1. Derivable from code? → DO NOT add
2. Already exists in another doc? → pointer, don't duplicate
3. Doc exceeds 300 lines? → find what to remove before adding

If changes are multi-area → invoke `doc-updater` agent.

## Step 2 — Proposals

Review open proposals in `docs/changes/`:
- Completed proposals → integrate into area docs and archive to `docs/_archive/changes/`
- Partial proposals → annotate current status in the proposal

## Step 3 — Planning

Read `docs/planning.md` and update:
- Standalone task completed → delete the line (NEVER `[x]`)
- Group task completed → ~~strikethrough~~ but DO NOT delete (shows group progress)
- All group tasks ~~struck through~~ → delete entire group block
- Partially advanced tasks → annotate current status
- Newly discovered tasks → add

## Step 4 — Changelog

Read `docs/changelog.md` and record each completed change with date and brief description (max 5 bullets + pointers to area docs).

If `changelog.md` exceeds 500 lines → rotate previous quarter entries to `docs/_archive/changelog/YYYY-QN.md`.

## Step 5 — Memory

Review if during the session there were:
- New architectural decisions (mark with `> **Decision:**` in area doc + entry in `decisions.md`)
- Discovered gotchas or errors (add to § If you touch... in area doc)
- Stack or configuration changes
- User feedback on workflow

Act directly: save new memories, update existing ones, clean up stale ones.

## Step 6 — Doc size check

Run:
```bash
find docs/ -maxdepth 1 -name "*.md" -exec wc -l {} + | sort -rn | head -10
```

If any area doc exceeds 350 lines → report in summary as ⚠️.
If any doc exceeds 300 lines → verify it has no REF derivable from code.

## Step 7 — Dotfile change detection

Check if any dotfiles or dotfolders at the project root (files/folders starting with `.`) were modified during this session:
- `.claude/` — rules, agents, hooks, skills, settings, TOKEN-BUDGET
- `.claudeignore`, `.gitignore`, `.gitattributes`
- `.githooks/` — git hooks
- `.gitea/` — Gitea workflows
- `.prettierrc`, `.eslintrc`, `.mcp.json`, and any other configuration dotfiles

If changes detected → suggest running `/project-bootstrap` (mode 3: update skill) to propagate improvements to the shared skill templates.

This step ensures project-level improvements to configuration are not lost and can be shared across projects.

## Step 8 — Git commit

Invoke `git-ops` agent to get current status.

- If there are uncommitted changes → commit directly with descriptive message (DO NOT ask for confirmation)
- If no changes → continue
- Include ALL relevant modified/new files (except secrets)
- Commit message: describe the session changes

## Step 9 — Summary

Generate brief summary:

```
### Session [date]
**Done:** [brief list]
**Pending:** [next steps]
**Notes:** [decisions, gotchas, or nothing]
**Docs:** [docs updated or "no architectural changes"]
**Doc size:** [if any exceeds 300 lines, list]
```

## Constraints

- DO NOT modify CLAUDE.md, `.claude/rules/`, `.claude/agents/`
- Use `docs/` as source of truth
- Area docs are SSOT for architecture, NOT implementation catalogs
