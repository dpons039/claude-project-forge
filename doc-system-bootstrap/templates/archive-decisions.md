# Archived Decision Detail

This file mirrors `decisions.md` — a **list of `### D-n` sections, no table**. Two
different reasons a decision lands here; read each heading's status line, they are
not the same claim:

1. **Superseded** — the decision is no longer true. Its `### D-n` was moved here
   whole (heading included), marked `**Superseded by D-m**`. **This is not the
   current state** — to know how the project works today, read `decisions.md`;
   nothing superseded is in force.
2. **Detail archived** — the decision is **still active**; only its `### D-n` moved
   here, because its live surface (a BrandKit MDX page) was removed with no
   replacement. The claim still governs the project. Marked `**Detail archived**`,
   not `**Superseded**`.

A decision that was merely *refined* does **not** come here — it stays in
`decisions.md`, its claim still holds.

Ordered by ID, newest first. Never edit the text of an archived decision: a
superseded one carries its `Superseded by` line; a detail-archived one is moved
verbatim. That is the only edit either receives. Each `### D-n` is copied whole —
heading and all — so `grep '^### D'` and `### D-n` → next `###` work here too.

```markdown
### D7 — Containers are production-only
<original block, whole, with its trade-off>

**Superseded by D14 (2026-09-02)**
```

```markdown
### D48 — <claim>
<original block, whole, with its trade-off>

**Detail archived (2026-09-02)** — was shown live in BrandKit § Colour; the
surface was removed. Still active — this is the fallback source, not history.
```
