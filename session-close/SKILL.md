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
- Architectural decision → a `### D-n` in `decisions.md` (its only home — no area-doc
  marker, no `D-n` in code)
- Decision affected by a later one → **supersede** (the only relation): new `### D-m` +
  move the old `### D-n` (heading and all) to `_archive`. **The steps live in
  `doc-updater`** — delegate there, don't reimplement

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

**The filter (apply to EACH thing you're about to save):** is it a *project fact*
(domain rule, environment quirk, stack gotcha) or a *personal preference of the
user's* — or is it *how-to-work* guidance? If it's how-to-work AND a rule already
covers it (`.claude/rules/`: debugging, code-quality, code-search, frontend,
commits…), **do not save it to memory — it belongs in the rule, and duplicating
it just bloats every future session.** Memory is for what the rules don't capture:
domain facts and this user's preferences.

Decisions are docs, not memory:
- New architectural decisions → a `### D-n` in `decisions.md` (its only home — no
  area-doc marker, no `D-n` in code), not a memory
- Decisions affected during the session — verify the old `### D-n` carries its
  `Superseded by` line and **left `decisions.md` for `_archive/decisions.md`**
  (heading and all). If anything is missing → invoke `doc-updater`, which owns the
  process
- Discovered gotchas → § If you touch... in the area doc

**What actually goes to memory (passes the filter):**
- A domain fact the code can't tell you (a product-identity call, an authorization
  rule, a naming convention that isn't enforced)
- An environment/stack quirk (a tool that behaves unexpectedly here, a file that
  can't be read, a deploy template that only validates on the server)
- A preference of the user's about how they want to work that no rule states

Save the pattern, not the incident. Group the index by section
(Project / Feedback / Reference), don't let it grow into a flat list.

**A glance at the index you already have loaded:** if you notice entries that a
rule now covers, or the index reads as unmanageable, say so and propose pruning —
move project knowledge to docs, keep only facts and preferences. (No need to
measure — `.claude/count-context-tokens.py` exists for that but is a manual,
occasional audit, not part of the close.)

Act directly: save what passes the filter, update existing ones, prune what a rule
already covers.

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
Step 4). `decisions.md` is self-limiting — the hook warns only past a high fixed
backstop; if warned, a superseded `### D-n` never left for `_archive/decisions.md` —
move it. It also warns on single-source breaks (duplicate IDs, a `Superseded by` line
still in the store); fix by delegating to `doc-updater`.

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
