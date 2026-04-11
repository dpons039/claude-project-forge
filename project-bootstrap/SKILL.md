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
11. Additional skills — show curated list from `references/skills-catalog.md`

### Phase 2: Generation

No more questions. Generate everything in order:

1. `CLAUDE.md` — from `templates/CLAUDE.md.template`, replacing all placeholders
2. `.claude/settings.json` — from template, adapting commands to declared stack
3. `.claude/TOKEN-BUDGET.md` — from template
4. `.claude/doc-coverage.json` — from template, with declared TRACKED_DIRS
5. Agents — copy from `templates/claude/agents/` (only those that apply)
6. Hooks — copy from `templates/claude/hooks/` (secret-scanner, doc-check, doc-track)
7. `.claude/settings.local.json` — create with hooks config (or merge if exists)
8. Rules — generate stack-specific rules from `templates/claude/rules/*.template`, copy fixed rules
9. `.claude/skills/session-close/` — copy from `templates/claude/skills/session-close/`
10. `.claudeignore`, `.prettierrc`, `.gitignore` entries, `.githooks/pre-commit`
11. `git config core.hooksPath .githooks`
12. Ask: install `doc-system-bootstrap`? → if yes, invoke it
13. Ask: install `session-close` skill? → if yes, install via `npx skills add`
14. Install Superpowers if not present (provide instructions)
15. Install approved additional skills via `npx skills add <owner/repo@skill-name> -g -y`
16. If has frontend + `teach-impeccable` approved → invoke it

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

- Fixed rules: `system-health.md`, `debugging.md`, `code-search.md`, `env-windows.md`
- Agents: `doc-updater.md`, `git-ops.md`, `migration-checker.md`, `ui-reviewer.md`
- Hooks: `secret-scanner.py`, `doc-track.py`, `doc-check.py`
- Skills: `session-close/SKILL.md`
- Config: `TOKEN-BUDGET.md`
- Git hooks: `.githooks/pre-commit`

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
├── CLAUDE.md.template              → CLAUDE.md
├── claudeignore.template           → .claudeignore
├── prettierrc.template             → .prettierrc
├── gitignore-claude.template       → appended to .gitignore
├── githooks/pre-commit.template    → .githooks/pre-commit
└── claude/
    ├── settings.json.template      → .claude/settings.json
    ├── TOKEN-BUDGET.md.template    → .claude/TOKEN-BUDGET.md
    ├── doc-coverage.json.template  → .claude/doc-coverage.json
    ├── agents/                     → .claude/agents/
    ├── hooks/                      → .claude/hooks/
    ├── rules/                      → .claude/rules/
    └── skills/session-close/       → .claude/skills/session-close/
```

Files ending in `.template` have `[PLACEHOLDERS]` that get replaced during install.
Files without `.template` extension are copied as-is.

## References

- `references/install-guide.md` — detailed Mode 1 steps
- `references/update-guide.md` — detailed Mode 2 & 3 steps
- `references/skills-catalog.md` — curated skill list with owner/repo sources
