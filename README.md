# claude-project-forge

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

A skill system that builds, configures, and maintains the full infrastructure of a Claude Code project — documentation, conventions, hooks, agents, rules, and session management.

> **Disclaimer:** This project is provided **"AS IS"**, without warranty of any kind, express or implied. Use it at your own risk. The author is not responsible for any damage, data loss, or unintended behavior resulting from the use of these skills, templates, hooks, or configurations. Always review generated files before applying them to your projects.

Each skill is **independent** — install only what you need.

## Installation

```bash
# Install a specific skill
npx skills add <repo-url> --skill <skill-name>

# Install globally (available in all projects)
npx skills add <repo-url> --skill <skill-name> -g
```

Replace `<repo-url>` with this repository's Git URL.

## Skills

### project-bootstrap

Idempotent skill for managing Claude Code project configuration across projects.

| Mode | Trigger | What it does |
|------|---------|-------------|
| **Install** | New project (no CLAUDE.md) | Generates CLAUDE.md, rules, agents, hooks, settings. Asks which other skills to install |
| **Update project** | Existing project | Applies improvements from skill templates without touching project-specific config |
| **Update skill** | After improving a project | Propagates project changes back to skill templates for other projects to benefit |

```bash
npx skills add <repo-url> --skill project-bootstrap
```

### doc-system-bootstrap

One-time setup for a complete documentation system with SDD (change workflow).

| Phase | Trigger | What it does |
|-------|---------|-------------|
| **Install** | `install doc system` | Creates docs structure, agents (doc-updater, git-ops), hooks, rules, doc-coverage config |
| **Migrate** | `migrate docs` | Classifies and transfers content from existing docs.old/ to the new system |

Can be uninstalled after setup.

```bash
npx skills add <repo-url> --skill doc-system-bootstrap
```

### session-close

End-of-session checklist invoked manually with `/session-close`.

Runs 9 steps in order: area docs review, proposals, planning, changelog, memory, doc size audit, dotfile change detection, git commit, and summary.

If dotfiles changed during the session, suggests running `/project-bootstrap` mode 3 to propagate improvements.

```bash
npx skills add <repo-url> --skill session-close
```

## Workflows

### New project setup

```
1. Install project-bootstrap
2. Run /project-bootstrap → setup wizard
3. Wizard asks: install doc-system-bootstrap? session-close? other skills?
4. Done — project fully configured
```

### Keeping projects in sync

```
Project A improves a rule or hook
  → /project-bootstrap mode 3 → skill templates updated
Project B runs /project-bootstrap mode 2
  → receives the improvement
```

### Independent usage

Each skill works on its own:
- Only want docs? Install `doc-system-bootstrap`
- Only want session management? Install `session-close`
- Want everything orchestrated? Install `project-bootstrap`

## Requirements

- [Claude Code](https://claude.ai/code) CLI, desktop app, or IDE extension
- Node.js (for `npx skills` commands)
- Git
- [Superpowers](https://github.com/obra/superpowers) recommended (provides systematic-debugging, TDD, worktrees used by project-bootstrap)

## Contributing

Found a bug or have an improvement? Open an [issue](https://github.com/dpons039/claude-project-forge/issues) or submit a pull request. All contributions are subject to the same [CC BY-NC-SA 4.0](LICENSE) license.

## License

This project is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

- **Attribution** — You must credit this project and link back to the repository.
- **NonCommercial** — You may not use this material for commercial purposes.
- **ShareAlike** — Derivatives must be distributed under the same license.

See [LICENSE](LICENSE) for details.
