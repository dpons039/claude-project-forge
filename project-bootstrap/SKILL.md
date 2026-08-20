---
name: project-bootstrap
description: "Set up, update, or sync a project's Claude Code configuration. THREE MODES: (1) Install — new project setup with CLAUDE.md, rules, agents, hooks, skills. (2) Update project — apply skill improvements to an existing project. (3) Update skill — propagate project improvements back to the skill templates. Trigger on: 'bootstrap project', 'set up project', 'project setup', 'configure claude', 'update project config', 'sync project', 'propagate changes', 'update bootstrap'. Use this skill whenever a user wants to initialize a new project for Claude Code, update an existing project's configuration, or sync improvements between projects."
---

# Project Bootstrap

Idempotent skill with three modes for managing Claude Code project configuration.

## Mode Detection

Examine the current project to determine which mode to use:

1. Read `CLAUDE.md` in the project root
2. Decide:
   - If `CLAUDE.md` doesn't exist or contains `[PLACEHOLDERS]` → **Mode 1: Install**
   - If `CLAUDE.md` exists and is configured → ask the user:
     - "Update this project from skill templates" → **Mode 2: Update Project**
     - "Propagate this project's changes to the skill" → **Mode 3: Update Skill**

---

## Mode 1 — Install (new project)

Set up a complete Claude Code configuration from scratch.

Read `references/install-guide.md` for the detailed step-by-step process.

### Phase 1: Data Collection

Ask questions sequentially, one at a time. These determine what gets generated:

1. Project name + description
2. Has frontend / backend / both?
3. Stack per layer (languages, frameworks, DB, ORM)
4. OS/environment (Windows+bash, macOS, Linux)
5. Code language / UI language / response language
6. Development branch + protected branch
7. Mandatory conventions (naming, PKs, enums, etc.)
8. Uses DB migrations? Which folder?
9. Code dirs that trigger doc updates (TRACKED_DIRS)
10. Has Superpowers installed? (if not → provide instructions)
11. Additional skills — show curated list from `references/skills-catalog.md`.
    If the project has or wants a dev BrandKit page, offer `brandkit-manager`
    (DESIGN section) — its install is step 17, after PRODUCT.md exists

### Phase 2: Generation

No more questions. Generate everything in order:

1. `CLAUDE.md` — from `templates/CLAUDE.md.template`, replacing all placeholders
2. `.claude/settings.json` — from template, adapting commands to declared stack
3. `.claude/TOKEN-BUDGET.md` — from template
4. `.claude/doc-coverage.json` — from template, with declared TRACKED_DIRS
5. Agents — copy from `templates/claude/agents/` (only those that apply)
6. Hooks — copy from `templates/claude/hooks/` (secret-scanner, doc-check, doc-track).
   Also copy `templates/claude/count-context-tokens.py` → `.claude/` (budget measurer;
   under templates/ so Mode 2 updates it), then fill TOKEN-BUDGET.md `Current` (step 3)
7. `.claude/settings.local.json` — create with hooks config (or merge if exists)
8. Rules — generate stack-specific rules from `templates/claude/rules/*.template`, copy fixed rules
9. `session-close` skill — NOT copied here; installed from the forge repo via `npx skills` (step 13)
10. `.claudeignore`, `.prettierrc`, `.prettierignore`, `.gitignore` entries, `.githooks/pre-commit`
11. `git config core.hooksPath .githooks`
12. Ask: install `doc-system-bootstrap`? → if yes, invoke it. Install **local to
    the project** (one-time skill, can be uninstalled after running). If the user
    says yes, `doc-system-bootstrap` will replace the stub § Change Workflow in
    CLAUDE.md with the full SDD block (Standard/Complex levels + mandatory
    superpowers per phase + Superpowers output routing). The SDD is enforced by
    process, not a hook.
13. Ask: install `session-close` skill? → if yes, install **local to the
    project** via
    `npx skills add https://github.com/dpons039/claude-project-forge --skill session-close -y`
    (session-close depends on the project being up to date; keeping it
    local matches its scope).
14. Install Superpowers if not present (provide instructions)
15. Install approved additional skills. **Default: local to the project**
    (`npx skills add <owner/repo@skill-name> -y`). Before running each
    install, ask the user explicitly whether they want it local
    (default) or global (`-g`, user-level). Global only with explicit
    confirmation.
16. If has frontend and no `PRODUCT.md` at the root → install `impeccable` (pbakaus) temporarily, run `/impeccable teach` to generate PRODUCT.md (v4 successor of the old standalone `teach-impeccable`/`.impeccable.md`), then uninstall it (design-skill rule: only `frontend-design` stays installed)
17. If `brandkit-manager` approved (step 11) → install **local** from the forge repo
    (`npx skills add https://github.com/dpons039/claude-project-forge --skill brandkit-manager -y`)
    and invoke its `init-docs` (no frontend dependency; runs after step 16 so
    PRODUCT.md exists for the § Brand Commitments append). If the frontend
    already exists, offer `init-page` too.

### Phase 3: Confirmation

- List all generated files
- List all installed skills
- Suggest first commit

---

## Mode 2 — Update Project

Apply improvements from skill templates to an existing project without touching
project-specific configuration.

Read `references/update-guide.md` § "Mode 2" for full details.

### What gets updated (system files)

- Fixed rules: `system-health.md`, `debugging.md`, `code-search.md`, `code-quality.md`
- Agents: `doc-updater.md`, `git-ops.md`, `migration-checker.md`
- Hooks: `secret-scanner.py`, `doc-track.py`, `doc-check.py`, `count-context-tokens.py`
- Skills: none are template-copied. `session-close`, `doc-system-bootstrap` and
  `brandkit-manager` are lock-managed — update each by re-running
  `npx skills add https://github.com/dpons039/claude-project-forge --skill <name> -y`

**NOT auto-updatable** (placeholders or project-measured — diff only, never
overwrite): `ui-reviewer.md`, `env-windows.md`, `.githooks/pre-commit`,
`TOKEN-BUDGET.md`. See `references/update-guide.md` § "NOT auto-updatable".

### What is NEVER touched (project files)

- `CLAUDE.md`, stack rules, `settings.json`, `doc-coverage.json`, `.gitignore`, `.mcp.json`, `docs/`

### Process

1. Read system files from project
2. Compare against skill templates
3. Show diff summary (NEW / UPDATED / UP TO DATE)
4. Apply changes approved by user

---

## Mode 3 — Update Skill

Propagate improvements from a project back to the skill templates so other
projects can benefit.

Read `references/update-guide.md` § "Mode 3" for full details.

### What gets scanned

All dotfiles and dotfolders at the project root that are system-level:
- `.claude/rules/` (fixed rules only), `.claude/agents/`, `.claude/hooks/`
- `.claude/skills/session-close/`, `.claude/TOKEN-BUDGET.md`
- `.claude/skills/brandkit-manager/` — special destination: propagates to the forge's
  top-level `brandkit-manager/` folder (the skill's source), NOT to project-bootstrap
  templates
- `.claudeignore`, `.githooks/`, `.prettierrc`, `.gitattributes`

### What is NEVER propagated

Project-specific files: `.mcp.json`, `.gitignore`, `.claude/settings.json`,
`.claude/settings.local.json`, `CLAUDE.md`, stack rules, `doc-coverage.json`, `docs/`

### Process

1. Scan candidate dotfiles
2. Compare against current skill templates
3. Show diff per file
4. User approves/rejects each file
5. Update approved templates in the skill

---

## Templates

All templates live in the `templates/` directory, organized by destination:

```
templates/
├── CLAUDE.md.template              → CLAUDE.md  (# LAWS block + # PROJECT CONTEXT)
├── session.md.template             → docs/changes/{slug}/session.md (created when a change opens, gitignored)
├── claudeignore.template           → .claudeignore
├── prettierrc.template             → .prettierrc
├── prettierignore.template         → .prettierignore (protects .claudeignore/.claude from format passes)
├── gitignore-claude.template       → appended to .gitignore (incl. docs/changes/**/session.md)
├── githooks/pre-commit.template    → .githooks/pre-commit
└── claude/
    ├── settings.json.template      → .claude/settings.json
    ├── TOKEN-BUDGET.md.template    → .claude/TOKEN-BUDGET.md
    ├── doc-coverage.json.template  → .claude/doc-coverage.json
    ├── agents/                     → .claude/agents/
    ├── hooks/                      → .claude/hooks/  (incl. session-reinject.py — SessionStart matcher=compact, Variant B)
    └── rules/                      → .claude/rules/  (fixed: system-health, code-search, debugging, code-quality, engineering)
```

The SDD rule (`sdd.md`) and `idea.md` template are NOT here — they are generated by
`doc-system-bootstrap` (its Step 7 + templates). `project-bootstrap`'s CLAUDE.md.template
only carries the pointers to `sdd.md`.

`session-close`, `doc-system-bootstrap` and `brandkit-manager` are standalone skills
installed from the forge repo via `npx skills` — never copied from templates.

Files ending in `.template` have `[PLACEHOLDERS]` that get replaced during install.
Files without `.template` extension are copied as-is.

## References

- `references/install-guide.md` — detailed Mode 1 steps
- `references/update-guide.md` — detailed Mode 2 & 3 steps
- `references/skills-catalog.md` — curated skill list with owner/repo sources
