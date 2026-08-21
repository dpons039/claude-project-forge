#!/usr/bin/env python3
"""
attempt-counter.py — PostToolUse hook (Write|Edit and Bash), warn-only.

Backs LAW10 / debugging.md's iron law externally: the failure mode is silent
repeat-patching (each hand-fix feels like the first, so a "3+ attempts" threshold
never trips because nothing counts). This hook COUNTS.

Mechanism — a symptom window, path-agnostic on purpose:
  • Write|Edit: append this edit to a rolling window in .attempt-counter.json.
    When the window holds >= THRESHOLD code edits with NO verify-run between them,
    print a warning to stderr. NEVER blocks (exit 0 always).
  • Bash: if the command looks like a verify (test/build/typecheck/lint), RESET the
    window. A real "I tested between patches" clears the count; that is what keeps
    deliberate, verified multi-file work from tripping the warning.

Why path-agnostic within the window: a single bug (e.g. a sticky CSS element) is
fixed across child + parent + a stacking-context file. A per-file counter would read
1-1-1 and never fire on exactly the cross-file shape that matters. Counting recent
edits regardless of path, reset by a verify, catches the pelea and not honest work.

Honest limit (documented, not hidden): the reset detects that a verify RAN, not that
it tested THIS symptom. That imprecision is why this is warn-only — a false trip costs
one ignorable line, never a blocked action. A hook that cried wolf by blocking would
get disabled, and a disabled guard protects nothing.

State file .attempt-counter.json is gitignored and ephemeral (per working spell of
edits). Doc/config edits are excluded from the count — they are not "patches".
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

THRESHOLD = 3            # code edits with no verify between -> warn
WINDOW_MAX = 12          # cap stored entries so the file can't grow unbounded

# A Bash command matching this clears the window (a real verify ran).
VERIFY_RE = re.compile(
    r"\b(test|vitest|jest|mocha|pytest|build|tsc|typecheck|type-check|lint|eslint|"
    r"check|ci)\b",
    re.IGNORECASE,
)

# Edits to these are not "patches" — don't count them toward a debugging spiral.
NON_CODE_SUFFIXES = (".md", ".mdx", ".txt", ".json", ".lock", ".yml", ".yaml",
                     ".toml", ".ini", ".cfg", ".env")
NON_CODE_DIR_HINTS = ("/docs/", "\\docs\\", "/.claude/", "\\.claude\\")


def state_path(root: Path) -> Path:
    return root / ".attempt-counter.json"


def load_window(p: Path) -> list[str]:
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return []


def save_window(p: Path, window: list[str]) -> None:
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(window[-WINDOW_MAX:], f, ensure_ascii=False)
    except Exception:
        pass


def is_code_edit(path: str) -> bool:
    low = path.lower()
    if low.endswith(NON_CODE_SUFFIXES):
        return False
    if any(h in low for h in NON_CODE_DIR_HINTS):
        return False
    return True


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    sp = state_path(root)

    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input", {}) or {}

    # ── Bash: reset the window on a verify-run ────────────────────────────────
    if tool == "Bash":
        command = tool_input.get("command", "") or ""
        if VERIFY_RE.search(command):
            save_window(sp, [])
        return 0

    # ── Write|Edit: accumulate, warn at the threshold ─────────────────────────
    if tool in ("Write", "Edit", "MultiEdit"):
        file_path = tool_input.get("file_path", "") or ""
        if not file_path or not is_code_edit(file_path):
            return 0

        try:
            rel = os.path.relpath(file_path, str(root)).replace("\\", "/")
        except ValueError:
            rel = file_path.replace("\\", "/")

        window = load_window(sp)
        window.append(rel)
        save_window(sp, window)

        if len(window) >= THRESHOLD:
            n = len(window)
            distinct = len(set(window))
            print("", file=sys.stderr)
            print(f"[PATCH-COUNT] {n} code edits with no test/build run between them "
                  f"({distinct} file(s)).", file=sys.stderr)
            print("   If you are patching the same symptom, this is the LAW10 / "
                  "debugging.md trip:", file=sys.stderr)
            print("   STOP hand-patching -> invoke systematic-debugging (root cause "
                  "before the next fix).", file=sys.stderr)
            print("   Ran a real verify since the last patch? It will reset this. "
                  "(warning only, nothing blocked)", file=sys.stderr)
            print("", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
