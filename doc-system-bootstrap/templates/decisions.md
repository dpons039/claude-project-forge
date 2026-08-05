# Architecture Decisions

Index of non-obvious decisions. Each decision lives inline in its area doc,
marked with `> **Decision:** (YYYY-MM-DD, D-n)` — **the full reasoning lives
there; this file only contains pointers**. Entries here: 1–2 lines, the claim
without the argument.

IDs are assigned as the next free number in the `#` column and are never reused,
not even those of superseded decisions.

When a decision changes, never rewrite it — all four steps:

1. New decision inline in the area doc, with a new ID and a `Supersedes D-n` line.
2. Add `**Superseded by D-m (YYYY-MM-DD)** — doc.md § section` to the old block.
3. Move the old block to `_archive/decisions.md`, text intact.
4. Here: mark the old row `superseded by D-m`, point its Doc at `_archive/decisions.md`,
   and add the new row as `active`.

| # | Decision | Doc | Section | Status |
|---|----------|-----|---------|--------|
