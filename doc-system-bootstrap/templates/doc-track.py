#!/usr/bin/env python3
"""
doc-track.py — PostToolUse hook (Write + Edit)

Registers files modified by Claude during the session in .session-changes.json.
Lightweight: writes one line and exits.

The .session-changes.json file is read at session end by doc-check.py (Stop hook)
to verify documentation coverage.
"""

import json
import os
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    file_path: str = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    try:
        repo_root = os.environ.get("CLAUDE_PROJECT_DIR", "")
        if repo_root:
            file_path = os.path.relpath(file_path, repo_root)
        file_path = file_path.replace("\\", "/")
    except ValueError:
        sys.exit(0)

    changes_path = os.path.join(
        os.environ.get("CLAUDE_PROJECT_DIR", "."),
        ".session-changes.json",
    )

    try:
        if os.path.exists(changes_path):
            with open(changes_path, "r", encoding="utf-8") as f:
                changes: list[str] = json.load(f)
        else:
            changes = []

        if file_path not in changes:
            changes.append(file_path)

        with open(changes_path, "w", encoding="utf-8") as f:
            json.dump(changes, f, ensure_ascii=False)
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
