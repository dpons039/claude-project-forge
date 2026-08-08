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
├── decisions.md           ← Store of decision reasoning (### D-n each); dynamic size cap
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
- Decision markers only: > **Decision:** (YYYY-MM-DD, D-n) one-line claim.
  No trade-off here — the reasoning is the `### D-n` in `decisions.md` (the `D-n`
  is the pointer). Only decisions in force — superseded ones leave for
  `_archive/decisions.md`
- Diagrams of topology/architecture (ASCII or mermaid)

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

Store of the project's non-obvious decisions. Each area doc carries a one-line
marker `> **Decision:** (date, D-n) claim`; the `D-n` resolves to the `### D-n`
here, where the reasoning lives. Only decisions in force are here; superseded ones
move to `_archive/decisions.md`. IDs are never reused.

## How to fill this
### Levels (major / minor)   ← major = full block, minor = one line
### Superseded / Refined     ← superseded leaves for _archive; refined stays
### Live surface             ← ### D-n points at the surface, no duplicate block

## How to search / find      ← grep '^### D' (all); ### D-n → next ### (one)

## Decisions

### D2 — <newer claim>
<full block if major, one line if minor>

### D1 — <claim>
**Refined by D2 (date)**
<block; still in force>
```

(See the full rules in `docs/decisions.md` itself — this is just the shape.)

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
