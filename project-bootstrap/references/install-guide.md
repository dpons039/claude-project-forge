# Install Guide — Mode 1 Detail

Detailed process for setting up a new project from scratch.

## Phase 1: Data Collection

Ask these questions sequentially, one at a time:

1. **Project name + description** (1-2 sentences)
2. **Has frontend / backend / both?**
3. **Stack per layer** — languages, frameworks, DB, ORM
4. **OS/environment** — Windows+bash, macOS, Linux
5. **Code language / UI language / response language**
6. **Development branch + protected branch** (e.g.: dev / main)
7. **Mandatory conventions** — naming, PKs, enums, etc.
8. **Uses DB migrations? Which folder?** — for `.claudeignore` and database rule
9. **Code dirs that trigger doc updates (TRACKED_DIRS)** — e.g.: `backend/src/`, `frontend/src/`
10. **Has Superpowers installed?** — if not, provide instructions
11. **Additional skills** — show curated list from `references/skills-catalog.md`, user approves

## Phase 2: Generation

Execute in order, no more questions:

### 2.1 — CLAUDE.md
Read `templates/CLAUDE.md.template`. Replace all `[PLACEHOLDERS]` with collected data:
- `[PROJECT_NAME]`, `[PROJECT_DESCRIPTION]`, `[STACK]`
- `[CODE_LANG]`, `[UI_LANG]`, `[RESPONSE_LANG]`
- `[DEV_BRANCH]`, `[PROTECTED_BRANCH]`
- `[CONVENTIONS]` — one `- ` line per convention declared
- `[TRACKED_DIRS]` — comma-separated list
- `[MIGRATIONS_RESTRICTION]` — if uses migrations: "Never read files in `[MIGRATIONS_DIR]`..."
- `[UI_CONTROLS_CONVENTION]` — if has frontend with component library: "UI controls: always..."
- `[UI_REVIEWER_AGENT]` — if has frontend: add ui-reviewer line; else remove
- `[OS]`, `[IDE]`, `[REPO_URL]`, `[RUNTIME]`, `[PACKAGE_MANAGER]`
- `[ENV_RULE_FILE]` — `env-windows.md` if Windows, remove line if not

Write to `CLAUDE.md`.

### 2.2 — .claude/settings.json
Read `templates/claude/settings.json.template`. Adapt commands to the project's stack:
- Replace test commands with actual commands (e.g.: `npm run test`, `npx vitest run`)
- Replace lint/build commands
- Add project-specific deny rules if needed

Write to `.claude/settings.json`.

### 2.3 — .claude/TOKEN-BUDGET.md
Copy `templates/claude/TOKEN-BUDGET.md.template` as-is. User fills in actual values later.

### 2.4 — .claude/doc-coverage.json
Read `templates/claude/doc-coverage.json.template`. Replace placeholders:
- `[TRACKED_DIR_1]`, `[TRACKED_DIR_2]` with declared TRACKED_DIRS
- `[MIGRATIONS_DIR]` with declared migrations path (or remove block)
- `[DEPLOY_DIR]` with deploy path (or remove block)
- `[SOURCE_DIR_1]`, `[AREA_1]` etc. with source dirs and their area docs

Write to `.claude/doc-coverage.json`.

### 2.5 — Agents
Copy from `templates/claude/agents/`:
- `doc-updater.md` → `.claude/agents/doc-updater.md`
- `git-ops.md` → `.claude/agents/git-ops.md` (adapt shell note for OS)
- `migration-checker.md` → `.claude/agents/migration-checker.md` (if uses migrations)
- `ui-reviewer.md.template` → `.claude/agents/ui-reviewer.md` (if has frontend, replace placeholders)

### 2.6 — Hooks
Copy from `templates/claude/hooks/`:
- `secret-scanner.py` → `.claude/hooks/secret-scanner.py`
- `doc-check.py` → `.claude/hooks/doc-check.py`
- `doc-track.py` → `.claude/hooks/doc-track.py`

Create `.claude/settings.local.json` with hooks config (or merge if exists).

### 2.7 — Rules
Copy fixed rules from `templates/claude/rules/`:
- `system-health.md` → always
- `code-search.md` → always
- `debugging.md` → always
- `code-quality.md` → always (cross-cutting skills: clean-code, TDD, verification, code review, planning)
- `env-windows.md` → only if Windows (replace `[PROJECT_PATH]` placeholders)

Generate stack rules from templates (only those that apply):
- `frontend.md.template` → if has frontend
- `backend.md.template` → if has backend
- `database.md.template` → if has database
- `security.md.template` → if has auth/security
- `testing.md.template` → if has tests
- `infrastructure.md.template` → if has Docker/deploy
- `cross-domain.md.template` → if has both frontend AND backend

For each template rule, replace `[SKILL_*]` placeholders with the actual skills the user approved.

### 2.8 — Session-close skill
Copy `templates/claude/skills/session-close/SKILL.md` → `.claude/skills/session-close/SKILL.md`

### 2.9 — Dotfiles
- `.claudeignore` from `templates/claudeignore.template` (adapt migrations dir)
- `.prettierrc` from `templates/prettierrc.template`
- Append `templates/gitignore-claude.template` entries to `.gitignore` (create if doesn't exist)
- `.githooks/pre-commit` from `templates/githooks/pre-commit.template` (adapt to stack)
- `git config core.hooksPath .githooks`

### 2.10 — Skills installation
- If Superpowers not installed → show installation instructions, pause
- For each approved skill: ask user **local (default) or global (`-g`)**.
  Install local by default: `npx skills add <owner/repo@skill-name> -y`.
  Global only with explicit confirmation: add `-g`.
- Skills that live in this user's own forge repo
  (`https://github.com/dpons039/claude-project-forge`) are installed via:
  `npx skills add https://github.com/dpons039/claude-project-forge --skill <skill-name> -y`.
- If `doc-system-bootstrap` approved → install **local** from the forge
  repo and invoke it to set up docs (one-time skill, uninstall after).
- If `session-close` approved → install **local** from the forge repo
  (depends on the project being up to date).
- If `teach-impeccable` approved and has frontend → invoke after installation

## Phase 3: Confirmation

- List all generated files with paths
- List all installed skills
- Suggest first commit: `git add -A && git commit -m "chore: project bootstrap"`
