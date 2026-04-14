# Update Guide — Modes 2 & 3 Detail

## Mode 2 — Update Project

Apply improvements from the skill templates to an existing project.

### System files (updatable)

These files are generic infrastructure, not project-specific:

| Category | Files |
|----------|-------|
| Rules (fixed) | `system-health.md`, `debugging.md`, `code-search.md`, `code-quality.md`, `env-windows.md` |
| Agents | `doc-updater.md`, `git-ops.md`, `migration-checker.md`, `ui-reviewer.md` |
| Hooks | `secret-scanner.py`, `doc-track.py`, `doc-check.py` |
| Skills | `session-close/SKILL.md` |
| Config | `TOKEN-BUDGET.md` |
| Git hooks | `.githooks/pre-commit` |

### Project files (DO NOT touch)

These are configured specifically for this project:

- `CLAUDE.md`
- `.claude/rules/` stack rules (frontend.md, backend.md, database.md, security.md, testing.md, infrastructure.md, cross-domain.md)
- `.claude/settings.json`, `.claude/settings.local.json`
- `doc-coverage.json`
- `.gitignore`, `.mcp.json`
- `docs/` (all documentation)

### Process

1. Read all system files from the project
2. Read corresponding templates from the skill
3. Compare each pair — identify:
   - Files in skill templates that don't exist in project → **NEW** (suggest install)
   - Files that exist in both but differ → **UPDATED** (show diff)
   - Files identical in both → **UP TO DATE** (skip)
4. Show summary to user:
   ```
   ### Update summary
   NEW:     system-health.md (not in project)
   UPDATED: doc-updater.md (12 lines changed)
   UPDATED: secret-scanner.py (3 new patterns)
   OK:      git-ops.md (identical)
   OK:      debugging.md (identical)
   ```
5. Apply changes approved by user
6. Show final summary of changes applied

### Comparison rules

- Compare content, not timestamps
- For `.py` files: normalize line endings before comparing
- For `.md` files: ignore trailing whitespace
- Show meaningful diffs, not raw git diff (summarize what changed)

---

## Mode 3 — Update Skill

Propagate improvements from a project back to the skill templates.

### Dotfiles scanned (candidates to propagate)

Scan all dotfiles and dotfolders at the project root (files/folders starting with `.`):

| Category | Paths |
|----------|-------|
| Rules (fixed) | `.claude/rules/system-health.md`, `debugging.md`, `code-search.md`, `code-quality.md`, `env-windows.md` |
| Agents | `.claude/agents/` (all) |
| Hooks | `.claude/hooks/` (all .py files) |
| Skills | `.claude/skills/session-close/` |
| Config | `.claude/TOKEN-BUDGET.md` |
| Dotfiles | `.claudeignore`, `.githooks/`, `.gitea/`, `.prettierrc`, `.gitattributes` |

### Dotfiles EXCLUDED (project-specific)

Never propagate these — they contain project-specific data:

- `.mcp.json` — tokens, URLs
- `.gitignore` — project-specific entries
- `.claude/settings.json` — stack-specific commands
- `.claude/settings.local.json` — local config
- `CLAUDE.md` — project content
- `.claude/rules/` stack rules — frontend.md, backend.md, database.md, etc.
- `.claude/doc-coverage.json` — project-specific paths
- `docs/` — all documentation

### Process

1. Scan candidate dotfiles in the project
2. For each candidate, find corresponding template in the skill:
   - Map project path → skill template path
   - e.g.: `.claude/rules/system-health.md` → `templates/claude/rules/system-health.md`
3. Compare content of each pair
4. Show diff per file with what changed
5. User approves/rejects each file individually
6. For approved changes:
   - Read the skill template file
   - Write the updated content from the project
7. Show summary:
   ```
   ### Skill updated
   UPDATED: templates/claude/rules/system-health.md
   UPDATED: templates/claude/hooks/secret-scanner.py
   SKIPPED: templates/claude/agents/git-ops.md (user rejected)
   NEW:     templates/claude/rules/new-rule.md (added to skill)
   ```

### Path mapping

| Project path | Skill template path |
|-------------|-------------------|
| `.claude/rules/system-health.md` | `templates/claude/rules/system-health.md` |
| `.claude/rules/debugging.md` | `templates/claude/rules/debugging.md` |
| `.claude/rules/code-search.md` | `templates/claude/rules/code-search.md` |
| `.claude/rules/code-quality.md` | `templates/claude/rules/code-quality.md` |
| `.claude/agents/doc-updater.md` | `templates/claude/agents/doc-updater.md` |
| `.claude/agents/git-ops.md` | `templates/claude/agents/git-ops.md` |
| `.claude/agents/migration-checker.md` | `templates/claude/agents/migration-checker.md` |
| `.claude/hooks/secret-scanner.py` | `templates/claude/hooks/secret-scanner.py` |
| `.claude/hooks/doc-check.py` | `templates/claude/hooks/doc-check.py` |
| `.claude/hooks/doc-track.py` | `templates/claude/hooks/doc-track.py` |
| `.claude/skills/session-close/SKILL.md` | `templates/claude/skills/session-close/SKILL.md` |
| `.claude/TOKEN-BUDGET.md` | `templates/claude/TOKEN-BUDGET.md.template` |
| `.claudeignore` | `templates/claudeignore.template` |
| `.prettierrc` | `templates/prettierrc.template` |
| `.githooks/pre-commit` | `templates/githooks/pre-commit.template` |

For files not in this mapping → ask user if they should be added to the skill templates.
