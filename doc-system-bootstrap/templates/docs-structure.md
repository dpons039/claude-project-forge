# Docs Structure Template

Adapt this structure to your project. Only create docs for areas that exist.

## Always create

```
docs/
├── README.md              ← Project map (index + structure)
├── doc-system.md          ← Documentation system principles and rules
├── changelog.md           ← Recent changes, quarterly rotation
├── planning.md            ← Only pending tasks [ ]
├── decisions.md           ← Index of inline decisions (pointers only)
├── research-needed.md     ← Open questions
│
├── changes/               ← SDD proposals (active)
│   ├── README.md          ← Workflow documentation
│   └── _template/
│       └── proposal.md    ← Proposal template
│
├── db/                    ← DB schema (if project has a database)
│   └── .gitkeep
│
└── _archive/
    ├── changes/           ← Completed proposals
    │   └── .gitkeep
    └── changelog/         ← Rotated changelog entries
        └── .gitkeep
```

> **Note:** Add `.gitkeep` to empty directories so Git tracks them.
> These files can be removed once the directory has real content.

## Create per area (only if the area exists)

```
├── backend.md             ← If project has a backend/API
├── frontend.md            ← If project has a frontend/UI
├── security.md            ← If project has auth, encryption, access control
├── infrastructure.md      ← If project has Docker, CI/CD, deploy
├── design.md              ← If project has a design system / brand kit
├── api.md                 ← If project consumes external APIs
│
├── db/                    ← If project has a database
│   ├── index.md           ← Table index
│   └── [table].md         ← One per table
```

## Area doc skeleton

Each area doc follows this structure:

```markdown
# [Area] — Architecture

## Stack and structure
Brief technology stack and folder organization.

## [Domain sections]
What exists and how it works. Include:
- Compact indexes (1 line per endpoint/component/service)
- 1 canonical example showing the pattern
- Decisions inline: > **Decision:** why X instead of Y
- Diagrams of topology/architecture (ASCII or mermaid)

## Conventions
Team rules for this area that aren't in linters or types.
- Rule 1
- Rule 2

## If you touch...
Cross-file dependencies:
- **File X** → also update Y
- **New Z** → make sure W exists
```

## decisions.md skeleton

```markdown
# Architecture Decisions

Index of non-obvious decisions. Each decision lives inline in its area doc,
marked with `> **Decision:**`.

| # | Decision | Doc | Section |
|---|----------|-----|---------|
| 1 | [title] | [area].md | § [section] |
```

## README.md skeleton

```markdown
# [Project] — Documentation Index

Source of truth for project knowledge.

## Stack
- [Brief tech stack description]

## Structure
[Brief folder layout]

## Documentation
| File | Area | Content |
|------|------|---------|
| docs/[area].md | [Area] | [Brief description] |
| docs/db/ | Database | Schema per table |
| docs/infrastructure.md | Infra | Docker, deploy, CI/CD |
| docs/planning.md | Planning | Pending tasks |
| docs/changelog.md | Changelog | Recent changes |
| docs/decisions.md | Decisions | Index of architecture decisions |
| docs/doc-system.md | System | Documentation principles and rules |
```
