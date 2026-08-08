# Architecture Decisions

This file is the **store** of the project's non-obvious decisions — the reasoning,
not an index. Each area doc carries a one-line marker
(`> **Decision:** (date, D-n) claim`); the `D-n` resolves to the `### D-n` here,
where the *why* lives. Only decisions still in force live in this file; superseded
ones move to `_archive/decisions.md`.

## How to fill this

### Levels (major / minor)

A decision earns a `### D-n` only if it passes the three-part test in
`doc-system.md` § Decisions (real alternative + reason invisible in code +
reverting hurts). Once it's in, grade it:

- **Major** — swapping one library for another, a cross-cutting pattern, an
  architectural choice, or any decision whose *why* names measured, rejected
  alternatives: a full block under the heading (claim, trade-off, alternatives,
  measurements). Huge derivations → point at a linked file or the proposal.
- **Minor** — passes the test but its *why* fits in half a sentence and there are
  no alternatives to record: a single line under the heading. No block.

When in doubt, major — keep the reasoning, don't lose it. IDs (`D1`, `D2`, …) are
the next free number, never reused, not even archived ones.

### Superseded / Refined

Never rewrite a decision. When a later one affects it, ask whether the old claim
still holds:

- **Superseded** (old claim now false) — new `### D-m` with `Supersedes D-n`; add a
  `**Superseded by D-m (date)**` line to the old `### D-n`; **move the old `### D-n`
  (heading and all) to `_archive/decisions.md`**; repoint the old area-doc marker at
  `_archive`. **No `Superseded by` line ever stays in this file** — a superseded
  entry has left for the archive.
- **Refined** (old claim still holds, narrowed or extended) — new `### D-m` with
  `Refines D-n`; add a `**Refined by D-m (date)**` line to the old `### D-n`, which
  **stays here** — its claim is still in force. Never archive a refined decision.

Only these two relations exist.

### Live surface

A major decision whose reasoning is rendered live in an external surface (a
BrandKit MDX page, next to its specimen) keeps its `### D-n` here, but the body
points at the surface **instead of** a full block — the prose is not duplicated.
This is an attribute, not a relation. If the surface is removed with no
replacement, move the `### D-n` to `_archive/decisions.md` marked
`**Detail archived**` (still in force — not superseded).

## How to search / find

- **List all** (every entry here is in force): `grep '^### D' decisions.md`
- **One decision, whole**: from its `### D-n` line to the next `### ` line
- **Refined ones** (still active): `grep 'Refined by' decisions.md`
- **Superseded / archived** live in `_archive/decisions.md`, not here

## Decisions

<!-- One `### D-n — claim` per decision, newest first.
     Major: full block below the heading. Minor: a single line.
     An active decision carries no status line; a refined one carries
     `**Refined by D-m (date)**`. Nothing superseded lives here. -->
