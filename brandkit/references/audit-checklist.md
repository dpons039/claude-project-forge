# audit — 16 mechanical checks, findings only

Read-only: the audit reports, it never fixes. Every finding cites its
evidence (file:line, command output). Severities: **BLOCKER** (gating — could
ship to prod), **HIGH** (drift that actively misleads), **MEDIUM** (real but
cosmetic drift), **LOW** (housekeeping).

Adapt names to the project (page dir, token files, locale dir, test file) —
the checks are canonical, the paths are not.

## The checks

| # | Check | Method | Sev |
|---|---|---|---|
| 1 | Entry absent from build inputs | Read the build config; no input covers the page entry | BLOCKER |
| 2 | Entry absent from real build output | Build (or use last build); `find dist/ -iname "*brandkit*"` → empty | BLOCKER |
| 3 | Zero hardcoded token values in the page | Grep hex/colour literals in tabs outside comments and documented exceptions (a never-rethemed mark is legitimate) | HIGH |
| 4 | Every token the page renders exists in the live stylesheet | For each token name listed in tabs → grep its declaration in the token CSS; zero-match names are flags | HIGH |
| 5 | Block count in BrandKit.md == real inventory | Count `<Section` per tab source; compare to the written count/list | HIGH |
| 6 | Voice-tab strings ⊆ voice.md | Grep each specimen string in voice.md; mismatches are **flags for human judgment** (wording licence vs different rule — a grep cannot distinguish) | HIGH |
| 7 | Locale-mirrored strings match the catalog | Grep the real locale files for strings the page claims to mirror; substance divergence is the finding | HIGH |
| 8 | Wireframe inline corrections still present | For each correction BrandKit.md enumerates, grep the embedded copy for the corrected form (a re-copy silently reverts them) | MEDIUM |
| 9 | Transcribed numbers match the live test | Grep each prose figure (ratios, ranges) in the theme test file | HIGH |
| 10 | Components shown are real imports, or documented recreations | Per `<Section>`, check import provenance; an undocumented local recreation is a flag | MEDIUM |
| 11 | design.md ↔ BrandKit.md ↔ page coherence | Values stated in `> **Decision:**` blocks vs token CSS vs what the page reads | MEDIUM |
| 12 | BrandKit.md size | `wc -l` — warn ≥ 350 (area-doc cap) | LOW |
| 13 | design.md / voice.md size | `wc -l` — context only, not this system's own defect | LOW |
| 14 | Missed cross-update | With git history: page content changed without its table-mates in the same range; without git: mtime (weak fallback). Also verify the doc-coverage warning trigger (page dir → BrandKit.md) exists | LOW |
| 15 | Canonical heading coverage | `templates/page/page-structure.md` (the canonical heading list, incl. Iconography and Motion in Foundations) vs the real blocks; absence without a "skipped: <reason>" note in BrandKit.md is a flag | MEDIUM |
| 16 | Encapsulation — the app never imports from the page | Grep imports of the page dir across `src/` outside it. One import pulls brandkit code into the prod bundle **without check #2 seeing it** (chunks are not named "brandkit") | BLOCKER |

## Process notes

- "The specimen sits where the defect can show" is a design rule for new
  blocks (checked at update time), not a re-triggerable audit finding — a past
  incident already fixed stays fixed.
- Checks 6/7 detect presence/absence, not semantic correctness of an allowed
  paraphrase. Report their mismatches as "for judgment", never as automatic
  failures.

## Report format

```markdown
# BrandKit Audit — <project> — <date>

## Summary
<N> checks · <X> PASS · <Y> flagged (<sev breakdown>)

## Findings (severity descending)
### BLOCKER / HIGH / MEDIUM / LOW
| Check | Result | Evidence |
|---|---|---|

## Passed cleanly
(one line each — keep the report about the flags)
```

Destination: summary in chat; full report as a file. In a project with an SDD
`docs/changes/` workflow, a `{date}-brandkit-audit/proposal.md` is the native
home — the findings are the proposal the fixes plan starts from.
