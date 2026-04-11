# Skills Catalog — Curated List

Present this list to the user during install. Show only the sections relevant to their
declared stack. User approves which to install.

## Installation command

```bash
npx skills add <owner/repo@skill-name> -g -y
```

For git URLs (private repos):
```bash
npx skills add <GIT_URL> --skill <skill-name>
```

---

## UNIVERSAL (always recommended)

| Skill | Source | Description |
|-------|--------|-------------|
| superpowers | obra/superpowers | Base system: plans, debugging, TDD, worktrees |
| clean-code | sickn33/antigravity-awesome-skills | Code quality and readability |
| systematic-debugging | obra/superpowers | Root cause analysis before proposing fixes |
| session-close | [user's skill repo] | End-of-session checklist |
| doc-system-bootstrap | [user's skill repo] | Documentation system + SDD workflow |

## SECURITY (always suggest, user decides)

| Skill | Source | Description |
|-------|--------|-------------|
| security-review | affaan-m/everything-claude-code | Auth, input validation, SQL injection, XSS, CSRF, secrets |

## FRONTEND — React / Vite

| Skill | Source | Description |
|-------|--------|-------------|
| frontend-patterns | affaan-m/everything-claude-code | React patterns, hooks, state |
| frontend-design | pbakaus/impeccable | Visual quality, anti-AI-slop |
| vite | antfu/skills | Vite config, plugins, SSR |
| vitest | antfu/skills | Fast unit testing |
| tailwind-responsive-ui | pproenca/dot-skills | Responsive patterns |
| tailwindcss-advanced-layouts | josiahsiegel/claude-plugin-marketplace | Grid, flexbox patterns |
| typescript-advanced-types | wshobson/agents | Generics, mapped, conditional |
| writing-for-interfaces | andrewgleave/skills | UX copy, microcopy |
| pwa-expert | erichowens/some_claude_skills | Service workers, offline |
| heroui-ref | heroui-inc/heroui | HeroUI/RAC tokens, components |
| security-vite | igorwarzocha/opencode-workflows | VITE_* exposure, build secrets |

## BACKEND — Node.js / Express

| Skill | Source | Description |
|-------|--------|-------------|
| nodejs-backend-patterns | wshobson/agents | Middleware, routing, errors |
| javascript-testing-patterns | wshobson/agents | AAA, factories, DI |

## DATABASE

### MySQL / MariaDB
| Skill | Source | Description |
|-------|--------|-------------|
| mysql-best-practices | mindrally/skills | Schema design, query optimization |

### PostgreSQL
| Skill | Source | Description |
|-------|--------|-------------|
| postgresql-table-design | wshobson/agents | Table design, schema |
| postgres-rls | troykelly/claude-skills | Row Level Security |

### Supabase
| Skill | Source | Description |
|-------|--------|-------------|
| supabase-postgres-best-practices | supabase/agent-skills | PG optimization in Supabase |
| supabase-help | yoanbernabeu/supabase-pentest-skills | Supabase security reference |

## STATE MANAGEMENT

| Skill | Source | Description |
|-------|--------|-------------|
| zustand-patterns | yonatangross/orchestkit | Slices, middleware, Immer |

## INFRASTRUCTURE

| Skill | Source | Description |
|-------|--------|-------------|
| docker-expert | sickn33/antigravity-awesome-skills | Dockerfiles, compose, security |

## AUTOMATION — n8n

| Skill | Source | Description |
|-------|--------|-------------|
| n8n-workflow-patterns | czlonkowski/n8n-skills | Workflow architecture |
| n8n-node-configuration | czlonkowski/n8n-skills | Node-specific config |
| n8n-code-javascript | czlonkowski/n8n-skills | Code nodes, $input/$json |
| n8n-expression-syntax | czlonkowski/n8n-skills | {{}} expressions |
| n8n-validation-expert | czlonkowski/n8n-skills | Validation error interpretation |
| n8n-mcp-tools-expert | czlonkowski/n8n-skills | MCP tool usage |

## DESIGN (requires frontend)

| Skill | Source | Description |
|-------|--------|-------------|
| teach-impeccable | pbakaus/impeccable | One-time design context setup |
| color-palette | jezweb/claude-skills | OKLCH palette generation |

## UTILITIES

| Skill | Source | Description |
|-------|--------|-------------|
| ast-grep | ast-grep/agent-skill | Structural code search |

---

## Notes

- All skill sources have been resolved
- `[user's skill repo]` refers to the repo where project-bootstrap itself lives
- The `-g` flag installs globally (user-level)
- `-y` skips confirmation prompts
