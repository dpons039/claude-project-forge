# Architecture Decisions

The **store** of the project's non-obvious decisions — and the ONE place any decision
lives. No marker in an area doc, no `D-n` in code: a decision's consequences are
documented wherever they land, but the decision and its ID stay here. Only decisions
still in force are here; superseded ones move whole to `_archive/decisions.md`. The
recording procedure lives in the `doc-updater` agent — read it before editing.

## Decisions

<!-- One `### D-n — claim` per decision, newest first. Next free ID, never reused
     (not even archived ones). An entry is as long as its reasoning needs: a line if
     the *why* is a line; a block (claim, trade-off, rejected alternatives) if that is
     what the *why* contains. An in-force decision carries no status line. Nothing
     superseded lives here — it has left for `_archive/decisions.md`. -->

## How to search

- **List all** (every entry here is in force): `grep '^### D' decisions.md`
- **One decision, whole**: from its `### D-n` line to the next `### ` line
- **Superseded / archived** live in `_archive/decisions.md`, not here
