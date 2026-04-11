#!/usr/bin/env bash
# pre-commit — Documentation coverage and quality checks before commit
# Bypass: SKIP_DOC_CHECK=1 git commit -m "..."
#
# ADAPT: Replace __PLACEHOLDER__ sections with your project's language checks.
# Remove sections that don't apply.

[ "${SKIP_DOC_CHECK:-0}" = "1" ] && exit 0

REPO_ROOT=$(git rev-parse --show-toplevel)

# ── CLAUDE.md size limit ─────────────────────────────────────────────────────
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

# ── Language-specific checks (ADAPT TO YOUR PROJECT) ────────────────────────
STAGED=$(git diff --cached --name-only --diff-filter=ACM)

# __PLACEHOLDER_LANGUAGE_CHECKS__
# Example for TypeScript:
# if echo "$STAGED" | grep -q '\.tsx\?$'; then
#     echo "🔍 Checking TypeScript..." >&2
#     if ! (cd "$REPO_ROOT/src" && npx tsc --noEmit 2>&1); then
#         echo "❌ COMMIT BLOCKED — TypeScript errors" >&2
#         exit 1
#     fi
# fi

# ── Multi-area change detection → doc-updater reminder ──────────────────────
AREAS=0
# __PLACEHOLDER_AREA_DETECTION__
# Count how many source areas are in the staged files:
# echo "$STAGED" | grep -q '^src/api/' && AREAS=$((AREAS+1))
# echo "$STAGED" | grep -q '^src/web/' && AREAS=$((AREAS+1))
# echo "$STAGED" | grep -q '^deploy/' && AREAS=$((AREAS+1))

if [ "$AREAS" -ge 2 ]; then
    echo "" >&2
    echo "🔄 MULTI-AREA: changes in $AREAS areas detected." >&2
    echo "   Consider invoking the doc-updater subagent before committing." >&2
    echo "" >&2
fi

# ── Clean planning (no [x] completed items) ──────────────────────────────────
if git diff --cached --name-only | grep -q '^docs/planning.md$'; then
    CHECKED_ITEMS=$(git show :docs/planning.md 2>/dev/null | grep -c '^\- \[x\]' || true)
    if [ "$CHECKED_ITEMS" -gt 0 ]; then
        echo "" >&2
        echo "📋 COMMIT BLOCKED: planning.md contains $CHECKED_ITEMS completed [x] item(s)." >&2
        echo "   Move details to changelog.md and remove [x] from planning.md." >&2
        echo "" >&2
        exit 1
    fi
fi

# ── Documentation coverage (blocking + warning) ─────────────────────────────
python "$REPO_ROOT/.claude/hooks/doc-check.py" --pre-commit
