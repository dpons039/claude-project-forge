#!/usr/bin/env bash
# pre-commit — Documentation coverage and quality checks before commit
#
# ADAPT: Replace __PLACEHOLDER__ sections with your project's language checks.
# Remove sections that don't apply.
#
# SKIP_CHECKS=1 git commit -m "..."  → work-in-progress commit.
#   A per-block commit in a long session is a CHECKPOINT, not a deliverable: an
#   intermediate state of a multi-task plan is legitimately type-incomplete or carries
#   unused scaffolds (writing-plans / TDD produce exactly that). Under SKIP_CHECKS the
#   completeness gates relax:
#     • skipped outright:  doc-check, planning.md [x] gate, CLAUDE.md-size gate, tests
#     • run but DO NOT block (warn only): the language checks (type-check, lint, audit) —
#       the verdict still shows the checkpoint's state, it just doesn't stop the commit
#   The secret-scanner is NOT one of these gates: a leaked secret is irreversible in git
#   history, so it is an invariant outside this flag's scope and always blocks. (It is a
#   separate Claude PreToolUse hook, not run from this wrapper at all.)
#
# ORDER MATTERS: cheap, high-frequency doc gates run FIRST, the expensive
# language/test suite runs LAST. A commit blocked on a missing doc must fail in
# milliseconds — never after paying for a full type-check or test run that is
# thrown away when the doc gate rejects the commit anyway.

REPO_ROOT=$(git rev-parse --show-toplevel)
STAGED=$(git diff --cached --name-only --diff-filter=ACM)

# The WIP-commit switch. Read once. "1" → completeness gates relax (see header).
SKIP="${SKIP_CHECKS:-0}"

# Soft-gate outcomes, filled in by the run blocks and read by the verdict.
LANG_STATE="not run"
TESTS_STATE="not run"
[ "$SKIP" = "1" ] && TESTS_STATE="skipped (SKIP_CHECKS)"

# ═══ DOC-GOVERNANCE GATES (skipped entirely under SKIP_CHECKS) ════════════════
if [ "$SKIP" != "1" ]; then

    # ── CLAUDE.md size limit ─────────────────────────────────────────────────
    CLAUDE_MD="$REPO_ROOT/CLAUDE.md"
    if [ -f "$CLAUDE_MD" ]; then
        CHAR_COUNT=$(wc -c < "$CLAUDE_MD")
        if [ "$CHAR_COUNT" -gt 20000 ]; then
            echo "" >&2
            echo "❌ CLAUDE.md exceeds ~5000 token limit" >&2
            echo "   Current size: $CHAR_COUNT chars (limit: 20,000 chars)" >&2
            echo "   Move content to docs/ or .claude/rules/" >&2
            echo "" >&2
            exit 1
        fi
    fi

    # ── Clean planning (no [x] completed items) ──────────────────────────────
    if echo "$STAGED" | grep -q '^docs/planning.md$'; then
        CHECKED_ITEMS=$(git show :docs/planning.md 2>/dev/null | grep -c '^\- \[x\]' || true)
        if [ "$CHECKED_ITEMS" -gt 0 ]; then
            echo "" >&2
            echo "📋 COMMIT BLOCKED: planning.md contains $CHECKED_ITEMS completed [x] item(s)." >&2
            echo "   Move details to changelog.md and remove [x] from planning.md." >&2
            echo "" >&2
            exit 1
        fi
    fi

    # ── Documentation coverage (blocking + warning) ──────────────────────────
    # This can BLOCK on missing required docs — so it runs before any test suite.
    python "$REPO_ROOT/.claude/hooks/doc-check.py" --pre-commit || exit 1

fi

# ── Multi-area change detection → doc-updater reminder (non-blocking) ─────────
AREAS=0
# __PLACEHOLDER_AREA_DETECTION__
# Count how many source areas are in the staged files:
# echo "$STAGED" | grep -q '^src/api/' && AREAS=$((AREAS+1))
# echo "$STAGED" | grep -q '^src/web/' && AREAS=$((AREAS+1))
# echo "$STAGED" | grep -q '^deploy/' && AREAS=$((AREAS+1))

if [ "$AREAS" -ge 2 ] && [ "$SKIP" != "1" ]; then
    echo "" >&2
    echo "🔄 MULTI-AREA: changes in $AREAS areas detected." >&2
    echo "   Consider invoking the doc-updater subagent before committing." >&2
    echo "" >&2
fi

# ═══ CODE GATES (always run; block normally, warn-only under SKIP_CHECKS) ═════
# ADAPT: type-check / lint / dependency-audit for your language. Under SKIP_CHECKS
# these must RUN (so the verdict shows the checkpoint's state) but NOT exit — record
# a warning instead. The pattern for each gate:
#
#   __PLACEHOLDER_LANGUAGE_CHECKS__
#   if echo "$STAGED" | grep -q '\.tsx\?$'; then
#       echo "🔍 Checking TypeScript..." >&2
#       if ! (cd "$REPO_ROOT/src" && npx tsc --noEmit 2>&1); then
#           if [ "$SKIP" = "1" ]; then
#               LANG_STATE="FAILED — not blocked (SKIP_CHECKS)"
#           else
#               echo "❌ COMMIT BLOCKED — TypeScript errors" >&2
#               exit 1
#           fi
#       else
#           [ "$LANG_STATE" = "not run" ] && LANG_STATE="passed"
#       fi
#   fi

# ── Tests (non-blocking — run dead last; SKIPPED under SKIP_CHECKS) ───────────
# ADAPT: your test runner. Wrap in the SKIP guard so a checkpoint commit doesn't
# pay for the suite:
#
#   if [ "$SKIP" != "1" ]; then
#       if echo "$STAGED" | grep -q '^src/'; then
#           echo "🧪 Running tests..." >&2
#           if (cd "$REPO_ROOT" && <test command> 2>&1); then
#               TESTS_STATE="passed"
#           else
#               TESTS_STATE="FAILED"
#           fi
#       fi
#   fi

# ═══ VERDICT (dead last — the one thing a truncated read still sees) ══════════
echo "" >&2
echo "════════════════════════════════════════════════════════════" >&2
if [ "$SKIP" = "1" ]; then
    echo " PRE-COMMIT VERDICT — SKIP_CHECKS (work-in-progress commit)" >&2
    echo "════════════════════════════════════════════════════════════" >&2
    echo "" >&2
    echo " SKIPPED (SKIP_CHECKS — not checked this commit)" >&2
    echo "   doc coverage, planning.md [x], CLAUDE.md size, tests" >&2
    echo "" >&2
    echo " ADVISORY (ran, did NOT block — a checkpoint, not a deliverable)" >&2
    echo "   language checks: $LANG_STATE" >&2
    echo "" >&2
    echo " ALWAYS ENFORCED" >&2
    echo "   secret-scanner (a leaked secret is irreversible — never relaxed)" >&2
else
    echo " PRE-COMMIT VERDICT" >&2
    echo "════════════════════════════════════════════════════════════" >&2
    echo "" >&2
    echo " BLOCKING (all passed — a failure would have stopped the commit)" >&2
    echo "   doc coverage, planning.md, CLAUDE.md size, language checks" >&2
    echo "" >&2
    echo " INFORMATIONAL (never blocks a commit)" >&2
    echo "   tests: $TESTS_STATE" >&2
fi
echo "" >&2
echo "════════════════════════════════════════════════════════════" >&2
