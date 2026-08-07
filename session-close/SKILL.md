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
- Architectural decision → inline with `> **Decision:** (date, D-n)` + entry in `decisions.md`
- Decision affected by a later one → `Superseded by` (old claim false → archive it) or
  `Refined by` (old claim still holds → stays put) on the old block, both rows marked in
  the index. **The four steps live in `doc-updater`** — delegate there, don't reimplement

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
- Advance the `> Status:` line to match reality: a proposal being implemented is
  `in-progress`, not `draft`. A folder still in `docs/changes/` marked `done` is an
  error — archive it now. A `Status` never advanced makes the field meaningless

## Step 3 — Planning

Read `docs/planning.md` and update:
- Standalone task completed → delete the line (NEVER `[x]`)
- Group task completed → ~~strikethrough~~ but DO NOT delete (shows group progress)
- All group tasks ~~struck through~~ → delete entire group block
- Partially advanced tasks → annotate current status
- Newly discovered tasks → add

If a phase started or finished this session → update its `State` in `docs/roadmap.md`
§ Phase order, in the same commit. That table is the ONLY place phase state lives;
`planning.md` references the active phase but never repeats its state (no second
place to keep in sync).

## Step 4 — Changelog

Read `docs/changelog.md` and record each completed change with date and brief description (max 5 bullets + pointers to area docs).

If `changelog.md` exceeds 500 lines → rotate the **oldest entries** to `docs/_archive/changelog/` until it is back under 500 — by size, with no quarter condition (a young project's entries are all current-quarter and a quarter rule never fires). Entries: ≤5 bullets of one line each.

## Step 5 — Memory

Review if during the session there were:
- New architectural decisions (mark with `> **Decision:** (date, D-n)` in area doc + entry in `decisions.md`)
- Decisions affected during the session — verify the old block carries its `Superseded by`
  or `Refined by` line, that superseded ones reached `_archive/decisions.md` and refined ones
  did NOT, and that the index rows match. A decision left without that line reads as still in
  force. If anything is missing → invoke `doc-updater`, which owns the process
- Discovered gotchas or errors (add to § If you touch... in area doc)
- Stack or configuration changes
- User feedback on workflow — an instruction repeated, a value of theirs overridden,
  "you didn't ask me". Save the pattern, not the incident

Act directly: save new memories, update existing ones, clean up stale ones.

## Step 6 — Doc size check

Run:
```bash
find docs/ -maxdepth 1 -name "*.md" -exec wc -l {} + | sort -rn | head -10
```

If any area doc exceeds 350 lines → report in summary as ⚠️.
If any doc exceeds 300 lines → verify it has no REF derivable from code.
If `planning.md` exceeds 100 lines → **fix it now, not just report**: move
roadmap/future content to `roadmap.md`, compress entries to 1–2 lines +
pointer, delete struck narrative. Same for `changelog.md` over 500 (rotate,
Step 4) and `decisions.md` entries over 2 lines (compress — the reasoning
lives inline in the area doc).

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

Invoke `git-ops` agent to get current status (`git status` / `git diff --cached`).

Commit **without asking** if and only if ALL of these hold (mechanical check, not a
judgement call — verifiable from `git status`):
- everything modified is under `docs/`, `.claude/`, or was created/edited this session
- no untracked files the session did not create
- no merge/rebase in progress
- the secret-scanner reports nothing

If all hold → commit directly with a descriptive message covering the session
changes (all relevant files except secrets). **If any fails** → list what is
foreign, propose the message, and wait for the user.
If no changes → continue.

(This is the single exception to CLAUDE.md's "never commit automatically": the user
invoked `/session-close` precisely to close out.)

## Step 9 — Summary

Generate brief summary:

```
### Session [date]
**Done:** [brief list]
**Pending:** [next steps]
**Notes:** [decisions, gotchas, or nothing]
**Memory:** [what was saved/updated/deleted, or "nothing new"]
**Docs:** [docs updated or "no architectural changes"]
**Doc size:** [if any exceeds 300 lines, list]
```

## Constraints

- DO NOT modify CLAUDE.md, `.claude/rules/`, `.claude/agents/`
- Use `docs/` as source of truth
- Area docs are SSOT for architecture, NOT implementation catalogs
