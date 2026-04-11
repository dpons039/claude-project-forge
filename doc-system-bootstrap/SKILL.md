---
name: doc-system-bootstrap
description: "Bootstrap a complete documentation system for any project. TWO COMMANDS: (1) 'install doc system' — sets up agents, hooks, docs structure, SDD workflow. If docs/ exists, renames to docs.old/. (2) 'migrate docs' — migrates content from docs.old/ to the new system. Also trigger on: 'doc bootstrap', 'set up docs', 'documentation setup', 'migrate docs.old', 'install documentation'. This is a ONE-TIME setup skill — after running, it can be uninstalled."
---

# Documentation System Bootstrap

One-time skill with two phases:

1. **Install** — Creates the full documentation system (agents, hooks, docs structure, SDD workflow).
   If `docs/` already exists, renames it to `docs.old/` first.
2. **Migrate** — Takes content from `docs.old/`, classifies it, extracts what's valuable
   into the new system, and discards what duplicates the code.

---

## Phase 1: Install

Trigger: user says "install doc system", "set up docs", "doc bootstrap", etc.

### Step 1 — Analyze the project

```bash
# Project structure
ls -la
find . -maxdepth 1 -type d | grep -v node_modules | grep -v .git | sort

# Source directories
find . -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.go" -o -name "*.rs" -o -name "*.java" | head -5
find . -type d -name "migrations" -o -name "migration" 2>/dev/null
find . -name "docker-compose*" -o -name "Dockerfile" 2>/dev/null
find . -name "*.yml" -path "*workflows*" -o -name "*.yaml" -path "*workflows*" 2>/dev/null

# Existing docs
ls docs/ 2>/dev/null
cat CLAUDE.md 2>/dev/null | head -50
```

Determine: source areas, infrastructure, database, tech stack, existing docs.

### Step 2 — Handle existing docs

If `docs/` **doesn't exist** → skip to Step 3.

If `docs/` **exists** → STOP and ask the user before doing anything:

1. Show a quick inventory:
```bash
echo "=== docs/ already exists ==="
find docs/ -maxdepth 1 -name "*.md" | wc -l
echo "files at root level"
find docs/ -name "*.md" | wc -l
echo "total .md files"
du -sh docs/
```

2. Ask the user:
   - **"Move and migrate"** — Rename `docs/` to `docs.old/`, install fresh system,
     then run Phase 2 (migrate) to transfer content with classification.
   - **"Install alongside"** — Keep existing `docs/` as-is, only add what's missing
     (agents, hooks, coverage, doc-system.md, changes/ structure).
   - **"Cancel"** — Stop and let the user organize manually first.

3. Proceed based on user's choice:
   - If **move and migrate**: `mv docs/ docs.old/`
     Tell the user: "Existing docs preserved in `docs.old/`. Run 'migrate docs' after install."
   - If **install alongside**: skip the move, proceed to Step 3 but only create
     files/dirs that don't already exist (never overwrite).
   - If **cancel**: stop.

### Step 3 — Create docs structure

Read `templates/docs-structure.md` for the directory template.

Create all directories and add `.gitkeep` to empty ones:

```bash
mkdir -p docs/db \
         docs/changes/_template \
         docs/_archive/changes \
         docs/_archive/changelog

touch docs/db/.gitkeep \
      docs/_archive/changes/.gitkeep \
      docs/_archive/changelog/.gitkeep
```

Create these files (adapt to the project — only create area docs for areas that exist):
- `docs/README.md` — Project map, adapt from `templates/docs-structure.md` § README skeleton
- `docs/doc-system.md` — Copy from `templates/doc-system.md`
- `docs/decisions.md` — Copy from `templates/decisions.md`
- `docs/planning.md` — Copy from `templates/planning.md`
- `docs/changelog.md` — Copy from `templates/changelog.md`
- `docs/research-needed.md` — Copy from `templates/research-needed.md`
- `docs/changes/README.md` — Copy from `templates/changes-readme.md`
- `docs/changes/_template/proposal.md` — Copy from `templates/proposal-template.md`
- Area doc skeletons (from `templates/docs-structure.md` § Area doc skeleton)

### Step 4 — Install agents and rules

**doc-updater** (agent — Claude auto-delegates before multi-area commits):
- Read `templates/doc-updater.md` → copy to `.claude/agents/doc-updater.md`

**git-ops** (agent — invoked by session-close for git status):
- If `.claude/agents/git-ops.md` already exists → skip
- If doesn't exist → copy `templates/git-ops.md` to `.claude/agents/git-ops.md`
- Adapt shell note: remove "Git Bash (MINGW64)" if not on Windows

**system-health** (rule — auto-triggered when touching .claude/ or CLAUDE.md):
- Read `templates/system-health-rule.md`
- If `.claude/rules/system-health.md` already exists → merge guardrails from template,
  keep any project-specific entries
- If doesn't exist → copy template to `.claude/rules/system-health.md`
- Adapt the `## Skills with verbal trigger` section to list the project's actual skills
- Create `.claude/rules/` directory if it doesn't exist: `mkdir -p .claude/rules`

### Step 5 — Generate doc-coverage.json

Read `templates/doc-coverage.template.json` for the structure.
Adapt to the project:

1. `exempt` — project's non-source files
2. `planning_triggers` — project's source directories
3. `blocking_triggers` — paths that ALWAYS need docs (migrations, infra)
4. `warning_triggers` — source areas with associated area docs

Write to `.claude/doc-coverage.json`.

### Step 6 — Install hooks

Copy from templates:
- `templates/doc-check.py` → `.claude/hooks/doc-check.py`
- `templates/doc-track.py` → `.claude/hooks/doc-track.py`

For the pre-commit hook:
- Read `templates/pre-commit.sh`
- Adapt language checks to the project
- Copy to `.githooks/pre-commit` (or project's hooks dir)
- `chmod +x .githooks/pre-commit`
- `git config core.hooksPath .githooks` if needed

**Configure Claude Code hooks** in `.claude/settings.local.json` (CRITICAL — without this
the hooks won't execute). Create or merge into the existing file:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "python .claude/hooks/secret-scanner.py"}]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [{"type": "command", "command": "python .claude/hooks/doc-track.py"}]
      },
      {
        "matcher": "Edit",
        "hooks": [{"type": "command", "command": "python .claude/hooks/doc-track.py"}]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "python .claude/hooks/doc-check.py"}]
      }
    ]
  }
}
```

If `.claude/settings.local.json` already exists, **merge** the hooks entries — don't overwrite
existing hooks. Add `.claude/settings.local.json` to `.gitignore` if it contains user-specific config.

### Step 7 — Update CLAUDE.md

Add documentation and SDD workflow references to CLAUDE.md. Adapt language to match the project's:

```markdown
## Documentation

- SSOT: `docs/` — read before working, update after architectural changes
- Index: `docs/README.md` — read the area doc BEFORE touching code
- System: `docs/doc-system.md` — principles and rules
- Decisions: inline with `> **Decision:**` — index in `docs/decisions.md`
- Agent: `doc-updater` — invoke before multi-area commits

When creating new file in `docs/`: update `docs/README.md`.

**SKIP_DOC_CHECK:** Claude NEVER creates `.claude/skip-doc-authorized` without
explicit authorization from the owner.

## Change Workflow (SDD)

- **Significant changes** (new feature, refactor >3 files, new migration,
  architecture change): create proposal in `docs/changes/{YYYY-MM-DD}-{slug}/proposal.md`
  copying the template BEFORE implementing
- On completing standalone task from `planning.md`: delete the line + summary to changelog
  **in the same commit**. If group task: ~~strikethrough~~ but don't delete.
- `planning.md`: only `[ ]` pending — NEVER `[x]`. Completed group tasks get
  ~~struck through~~ (progress). Entire group struck → delete block.
- `changelog.md`: new entries ≤5 bullets + pointers to area docs
- Cycle: proposal → approval → implementation → area docs → changelog → archive
- See detail: `docs/changes/README.md`
```

### Step 8 — Summary

```bash
echo "=== Installed ==="
find docs/ -name "*.md" | sort
find .claude/agents/ -name "*.md" 2>/dev/null | sort
find .claude/rules/ -name "*.md" 2>/dev/null | sort
find .claude/hooks/ -type f | sort
ls .githooks/pre-commit 2>/dev/null
[ -d docs.old ] && echo -e "\n=== Pending migration ===" && echo "docs.old/ exists — run 'migrate docs' to transfer content"
```

Tell the user:
- "Documentation system installed: agents (`doc-updater`, `git-ops`) + rule (`system-health`) + hooks + docs structure + SDD workflow."
- If docs.old/ exists: "Run **'migrate docs'** to transfer content from docs.old/."
- If no docs.old/: "Fill your area docs by describing your project's architecture."
- "After everything is set up, you can uninstall this skill."

---

## Phase 2: Migrate

Trigger: user says "migrate docs", "migrate docs.old", "transfer old docs", etc.

Prerequisite: `docs.old/` exists AND Phase 1 has been completed (docs/ has the new structure).

Read `references/migration-guide.md` for the detailed migration process.

Summary of steps:
1. Inventory docs.old/
2. Migrate structural files (planning, changelog, decisions, research-needed, proposals)
3. Classify area doc content (REF/ARCH/GUIDE/STATUS/GOTCHA/DIAGRAM/PRESCRIPTIVE)
4. Write new area docs with differentiated detail levels
5. Build decisions.md index from `> **Decision:**` markers
6. Update docs/README.md
7. Verify consistency (no old references, no duplication, size check)
8. Review memory for doc-worthy content (move project knowledge to docs)
9. Migration summary with before/after stats

---

## Principles (reference for both phases)

Read `templates/doc-system.md` for the full principles document. Key rules:

- **SSOT**: docs = project knowledge. Code = implementation detail.
- **No code duplication**: if Claude can read it from source → don't document it.
- **Rewrite, don't append**: docs describe current state, not history.
- **Decisions inline**: `> **Decision:**` marker, indexed in decisions.md.
- **Conventions in area docs**: `## Conventions`, 1-in-1-out rule.
- **Cross-file deps**: `## If you touch...` in each area doc.
- **Split threshold**: >350 lines + independent subtopics → subdirectory.
- **Two-level hooks**: blocking (migrations, infra) + warning (general code).
- **Size audit**: every session close checks `wc -l` on area docs.
- **SDD workflow**: significant changes require a proposal BEFORE implementation.
- **Memory vs docs**: project knowledge (decisions, conventions, gotchas) → docs. Personal preferences → memory.

## Templates

All templates are in the `templates/` directory:

| Template | Installs to | Type |
|----------|------------|------|
| `doc-updater.md` | `.claude/agents/` | Agent (auto-delegated) |
| `git-ops.md` | `.claude/agents/` | Agent (invoked by session-close) |
| `system-health-rule.md` | `.claude/rules/system-health.md` | Rule (auto-triggered) |
| `doc-system.md` | `docs/` | Reference doc |
| `docs-structure.md` | Reference only | Guide |
| `planning.md` | `docs/` | Template with rules |
| `changelog.md` | `docs/` | Template with rules |
| `decisions.md` | `docs/` | Template with rules |
| `research-needed.md` | `docs/` | Template with rules |
| `changes-readme.md` | `docs/changes/README.md` | SDD workflow |
| `proposal-template.md` | `docs/changes/_template/proposal.md` | SDD template |
| `doc-coverage.template.json` | `.claude/` (adapted) | Config |
| `doc-check.py` | `.claude/hooks/` | Hook |
| `doc-track.py` | `.claude/hooks/` | Hook |
| `pre-commit.sh` | `.githooks/` (adapted) | Git hook |
