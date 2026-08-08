# Skills Catalog — Curated List

Present this list to the user during install. Show only the sections relevant to their
declared stack. User approves which to install.

## Installation command

Default is **local to the project** (no `-g`). Ask the user before
each install whether they want local (default) or global.

```bash
npx skills add <owner/repo@skill-name> -y
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
| ast-grep | ast-grep/agent-skill | Structural code search. **Required by the fixed rule `code-search.md`, which routes structural searches to it — install it or that rule points at a missing tool.** |
| session-close | https://github.com/dpons039/claude-project-forge (skill: `session-close`) | End-of-session checklist |
| doc-system-bootstrap | https://github.com/dpons039/claude-project-forge (skill: `doc-system-bootstrap`) | Documentation system + SDD workflow. **Setup tool, not permanent: uninstall (skill dir + skills-lock entry) once the doc system is created** |

## SECURITY (always suggest, user decides)

| Skill | Source | Description |
|-------|--------|-------------|
| security-review | affaan-m/everything-claude-code | Auth, input validation, SQL injection, XSS, CSRF, secrets |

## FRONTEND — React / Vite

| Skill | Source | Description |
|-------|--------|-------------|
| frontend-patterns | affaan-m/everything-claude-code | React patterns, hooks, state |
| frontend-design | pbakaus/impeccable | Visual quality, anti-AI-slop. **Design-skill rule: exactly ONE design skill per project** — the candidates (this, anthropics/skills `frontend-design`, pbakaus `impeccable` v4) are mutually exclusive. Two installed at once = two conflicting design personas competing for every frontend trigger |
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
| ~~teach-impeccable~~ | pbakaus/impeccable | **Legacy** (wrote `.impeccable.md`). Current procedure: install `impeccable` v4, run `/impeccable teach` → writes `PRODUCT.md` at the root, then uninstall the skill |
| color-palette | jezweb/claude-skills | OKLCH palette generation |
| brandkit-manager | https://github.com/dpons039/claude-project-forge (skill: `brandkit-manager`) | Dev-only BrandKit page (MDX-driven, config-parameterised: universal chrome copy-paste + `.mdx`/`.examples.tsx` per tab) + satellite docs (BrandKit.md/design.md/voice.md/PRODUCT.md § Brand Commitments). FOUR operations: init-docs, init-page, update, audit. **Exempt from the design-skill rule above** — it documents and verifies the design system, it is not a design-authoring persona. Install AFTER PRODUCT.md exists (its init-docs appends a section to it) |

---

## Notes

- All skill sources have been resolved
- `[user's skill repo]` refers to the repo where project-bootstrap itself lives
- Default install is **local to the project** (no `-g`). Ask the user
  before each install whether they want it local (default) or global
  (`-g`, user-level). Install global only with explicit confirmation.
- `-y` skips confirmation prompts
- `[user's skill repo]` in this catalog resolves to
  `https://github.com/dpons039/claude-project-forge`. Install its skills
  via:
  ```
  npx skills add https://github.com/dpons039/claude-project-forge --skill <skill-name> -y
  ```
