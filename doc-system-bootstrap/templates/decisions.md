# Architecture Decisions

Index of non-obvious decisions. Each decision lives inline in its area doc,
marked with `> **Decision:** (YYYY-MM-DD, D-n)` — **the full reasoning lives
there; this file only contains pointers**. Entries here: 1–2 lines, the claim
without the argument.

IDs are assigned as the next free number in the `#` column and are never reused,
not even those of superseded decisions.

When a decision changes, never rewrite it. Ask whether the old claim still holds:

**Superseded** (old claim now false) — new decision inline with `Supersedes D-n`;
`**Superseded by D-m (date)** — doc.md § section` added to the old block; old block
moved to `_archive/decisions.md`; here, old row → `superseded by D-m` with its Doc
pointing at `_archive/decisions.md`, new row → `active`.

**Refined** (old claim still holds, narrowed or extended) — new decision inline with
`Refines D-n`; `**Refined by D-m (date)** — doc.md § section` added to the old block;
the old block **stays in its area doc**; here, old row → `active (refined by D-m)`.
Never archive a refined decision — it is still in force.

| # | Decision | Doc | Section | Status |
|---|----------|-----|---------|--------|
