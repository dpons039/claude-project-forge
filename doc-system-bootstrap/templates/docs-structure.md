# Docs Structure Template

Adapt this structure to your project. Only create docs for areas that exist.

## Always create

```
docs/
├── README.md              ← Project map (index + structure, same section order everywhere)
├── doc-system.md          ← Documentation system principles and rules
├── changelog.md           ← Recent changes; rotation by size (>500 lines)
├── planning.md            ← Current phase only, hard cap 100 lines, entries 1-2 lines
├── roadmap.md             ← Full phase plan + deferred future scope, read on demand
├── decisions.md           ← Store + ONE home of decisions (### D-n each); superseded → _archive
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
    ├── decisions.md       ← Superseded decisions (history, never current state)
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
├── db.md                  ← If project has a database (schema index, conventions)
├── security.md            ← If project has auth, encryption, access control
├── infrastructure.md      ← If project has Docker, CI/CD, deploy
├── design.md              ← If project has a design system (tokens, hierarchy, themes)
├── voice.md               ← If the product has user-facing copy (tone, vocabulary)
├── testing.md             ← If project has a test suite (layout, runners, policies)
├── BrandKit.md            ← If project has a dev BrandKit page (how it works, how to
│                            add blocks) — created/maintained by the `brandkit-manager` skill,
│                            not by this bootstrap
├── api.md                 ← If project consumes external APIs (domain extras named
│                            after the API are allowed — always indexed in README.md)
│
├── db/                    ← If project has a database
│   └── [table].md         ← One per table: CREATE TABLE first, then
│                            "What the SQL cannot say", then "If you touch"
```



## Canonical contract (exact name parity across projects)

The set and the NAMES above are canonical: every project bootstrapped with this
system uses the same filenames, so an agent that jumps between projects finds
the same structure — only the stack changes. Domain extras are allowed but must
be indexed in README.md. At the project ROOT (outside docs/): `PRODUCT.md` —
the impeccable v4 `product-schema` record (successor of the old standalone
`.impeccable.md`): one product+design context file, never two.

## Area doc skeleton

Each area doc follows this structure:

```markdown
# [Area] — Architecture

## Stack and structure
Brief technology stack and folder organization.

## [Domain sections]
What exists and how it works — **present state only**. Include:
- Compact indexes (1 line per endpoint/component/service)
- 1 canonical example showing the pattern
- Diagrams of topology/architecture (ASCII or mermaid)

(No decision markers here — a decision lives only as a `### D-n` in `docs/decisions.md`.
The area doc records the decision's *consequences* — a convention, a gotcha — never the
decision or its ID.)

## [Unbuilt area, if any]
Not implemented yet — [proposal](changes/YYYY-MM-DD-slug/proposal.md).
(Always this shape: one line + pointer. Never specify future work in the
area doc as if it existed; specs live in the proposal.)

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

Store and ONE home of the project's non-obvious decisions — no area-doc marker, no
`D-n` in code. Only decisions in force are here; superseded ones move whole to
`_archive/decisions.md`. IDs are never reused. Recording procedure: the `doc-updater`
agent.

## Decisions

### D2 — <newer claim>
<a line if the why is a line; a block with trade-off + rejected alternatives otherwise>

### D1 — <claim>
<block; in force — no status line>

## How to search
- grep '^### D' (all, in force); ### D-n → next ### (one whole decision)
```

(See the full rules in `docs/decisions.md` and the `doc-updater` agent — this is the shape.)

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
| docs/decisions.md | Decisions | Store of decision reasoning (one `### D-n` each) |
| docs/doc-system.md | System | Documentation principles and rules |
```
