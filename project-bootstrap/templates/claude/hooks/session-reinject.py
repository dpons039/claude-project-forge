#!/usr/bin/env python3
"""SessionStart hook (matcher: compact) — re-inject the active change's session.md
after a compaction so the live state (decisions, discarded, status) survives.

Mechanism (verified against code.claude.com/docs/en/hooks.md):
- SessionStart is one of the few events whose PLAIN-TEXT STDOUT is added as context
  Claude can see. (PreCompact cannot inject — its stdout is not surfaced; it can only
  block, which we never want.)
- source values include "compact". Wire this on SessionStart with matcher "compact".

Behaviour: read the most-recently-modified docs/changes/*/session.md, print it to
stdout wrapped in a clear header, exit 0. If none exists, exit 0 silently. NEVER
block, NEVER raise to the caller.
"""
import sys
from pathlib import Path


def main() -> int:
    try:
        project = Path(__file__).resolve().parents[2]  # .claude/hooks/ -> project root
        changes = project / "docs" / "changes"
        if not changes.is_dir():
            return 0

        # Active session logs, newest first. One per open {slug}/.
        logs = sorted(
            (p for p in changes.glob("*/session.md") if p.is_file()),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not logs:
            return 0

        # Re-inject the most recent (the one being worked on). LAW9 keeps work to
        # one front at a time, so the newest is almost always the only live one.
        newest = logs[0]
        text = newest.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            return 0

        rel = newest.relative_to(project)
        print("## Restored session state (post-compaction)")
        print(f"Live state of the active change, re-read from {rel} (LAW5).")
        print("Re-read the full file before continuing if you need more than this.")
        print()
        print(text)
        return 0
    except Exception:
        # A hook must never break the session. Swallow everything.
        return 0


if __name__ == "__main__":
    sys.exit(main())
