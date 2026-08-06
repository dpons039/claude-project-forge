#!/usr/bin/env python3
"""
sdd-gate.py — SDD enforcement

The change workflow (propose -> plan -> implement -> close) is prose in CLAUDE.md and
docs/changes/README.md. Prose without verification degrades: a session reads the rule,
finds nothing contradicting it when skipped, and erodes it turn by turn. This hook is
the verification.

Two modes:

  • UserPromptSubmit (no args): injects the current phase and its proposal into context
    BEFORE any planning happens. The SDD *produces* the proposal, so a gate that fires
    at Write time is several turns too late.

  • --guard (PreToolUse on Write|Edit): blocks a source edit when the session has
    touched no proposal AND the target is outside the open phase's scope. It blocks on
    ABSENCE, never on judgment — no hook can decide "is this a new feature" from a path.
    A wrong classification stays visible in the diff; an absent one is invisible, which
    is the failure this exists to catch.

State is read, never written. Everything it needs already exists and is already
maintained by session-close:

  docs/roadmap.md          § Phase order — the row whose State is "in progress"
  docs/planning.md         § Current phase — cross-check
  .session-changes.json    written by doc-track.py, consumed by doc-check.py at Stop
  .claude/doc-coverage.json  path <-> area-doc mapping, reused to derive phase scope

Bypass: .claude/skip-doc-authorized — the same owner-authorized sentinel doc-check.py
uses. One bypass to learn, not two.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path


# ── Shared helpers (same shape as doc-check.py) ───────────────────────────────

def repo_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))


def load_coverage(root: Path) -> dict:
    try:
        with open(root / ".claude" / "doc-coverage.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def is_exempt(path: str, exempt_patterns: list[str]) -> bool:
    """Same matching doc-check.py uses, so one exempt list governs both hooks."""
    for pattern in exempt_patterns:
        if pattern.endswith("/") and path.startswith(pattern):
            return True
        if pattern == path:
            return True
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
        if pattern.endswith("*") and path.startswith(pattern[:-1]):
            return True
    return False


def consume_skip_authorization(root: Path) -> bool:
    """Owner-authorized one-shot bypass. Same file doc-check.py honours."""
    auth_file = root / ".claude" / "skip-doc-authorized"
    if auth_file.exists():
        try:
            auth_file.unlink()
        except OSError:
            pass
        return True
    return False


def session_changes(root: Path) -> list[str]:
    """Files written this session. Do NOT delete it — doc-check.py owns its lifecycle."""
    try:
        with open(root / ".session-changes.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


# ── Phase state ───────────────────────────────────────────────────────────────

# | F4 | Phase name | [YYYY-MM-DD-slug](changes/YYYY-MM-DD-slug/proposal.md) | **in progress** |
ROADMAP_ROW = re.compile(r"^\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]*)\|\s*$")
PROPOSAL_LINK = re.compile(r"\(([^)]*changes/([^/)]+))/proposal\.md\)")


def current_phase(root: Path) -> dict | None:
    """The roadmap row marked in progress. That table is where phase state lives."""
    path = root / "docs" / "roadmap.md"
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None

    for line in lines:
        m = ROADMAP_ROW.match(line)
        if not m:
            continue
        num, name, proposal_cell, state = (c.strip() for c in m.groups())
        if "in progress" not in state.replace("*", "").lower():
            continue
        link = PROPOSAL_LINK.search(proposal_cell)
        return {
            "id": num,
            "name": name,
            "slug": link.group(2) if link else "",
            "proposal": f"docs/{link.group(1)}/proposal.md" if link else "",
        }
    return None


def planning_proposal(root: Path) -> str:
    """The proposal planning.md points at, for cross-checking the roadmap."""
    try:
        text = (root / "docs" / "planning.md").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    m = PROPOSAL_LINK.search(text)
    return m.group(2) if m else ""


def phase_scope(root: Path, slug: str, config: dict) -> list[str]:
    """
    Derive the phase's paths from data that already exists.

    The slug encodes the area (`...-backend`, `...-frontend`); doc-coverage.json already
    maps paths to area docs. So: slug suffix -> docs/<area>.md -> the trigger patterns
    pointing at that doc. A second, hand-maintained scope map would only rot — the one
    in doc-coverage.json is already kept current because the doc checks depend on it.

    Empty result = unknown scope, and the caller then falls back to the proposal
    condition alone rather than blocking everything.
    """
    if not slug:
        return []

    triggers: list[dict] = []
    for key in ("warning_triggers", "blocking_triggers"):
        triggers.extend(config.get(key, []))

    # Longest area name first so "-frontend" cannot be shadowed by a shorter match.
    areas: list[str] = []
    for entry in triggers:
        for doc in entry.get("docs", []):
            name = os.path.basename(doc).removesuffix(".md").lower()
            if name and name not in areas:
                areas.append(name)
    areas.sort(key=len, reverse=True)

    slug_lower = slug.lower()
    for area in areas:
        if slug_lower.endswith(f"-{area}") or slug_lower.startswith(f"{area}-"):
            return [
                e["pattern"] for e in triggers
                if any(os.path.basename(d).removesuffix(".md").lower() == area
                       for d in e.get("docs", []))
                and e.get("pattern")
            ]
    return []


# ── Source classification ─────────────────────────────────────────────────────

def is_source(rel_path: str, config: dict) -> bool:
    """
    Config and docs are outside the SDD entirely.

    Any path whose first segment starts with "." is config: .claude/, .githooks/,
    .gitea/, .prettierrc. Stated as a rule rather than a list, so a dotfolder added
    later is covered without editing this hook. Those changes have their own route —
    session-close Step 7 sends them to /project-bootstrap mode 3.
    """
    norm = rel_path.replace("\\", "/")
    # removeprefix, never lstrip: lstrip strips a character SET, so "./" would eat the
    # leading dot of ".claude/..." and turn a config path into a source path.
    while norm.startswith("./"):
        norm = norm[2:]
    if not norm:
        return False
    if any(seg.startswith(".") for seg in norm.split("/") if seg):
        return False
    if norm.startswith("docs/") or norm == "CLAUDE.md" or norm.endswith(".md"):
        return False

    return not is_exempt(norm, config.get("exempt", []))


# ── Mode: UserPromptSubmit ────────────────────────────────────────────────────

def run_inject(root: Path) -> None:
    phase = current_phase(root)
    out: list[str] = ["## SDD state"]

    if phase:
        label = f"{phase['id']} {phase['name']}".strip()
        out.append(f"Open phase: **{label}** — `{phase['proposal'] or 'no proposal linked'}`")
        planning_slug = planning_proposal(root)
        if planning_slug and phase["slug"] and planning_slug != phase["slug"]:
            out.append(
                f"⚠️  roadmap.md and planning.md disagree: roadmap says `{phase['slug']}`, "
                f"planning.md points at `{planning_slug}`. Reconcile before working."
            )
    else:
        out.append("Open phase: **none** — no roadmap row is marked `in progress`.")

    out += [
        "",
        "Before planning or editing, say which of these the task is:",
        "- covered by the open phase's proposal → implement against it",
        "- significant (new feature, refactor >3 files, new migration, architecture"
        " change) → open `docs/changes/{YYYY-MM-DD}-{slug}/` FIRST",
        "- trivial (typo, one-liner, dependency bump) → proceed",
        "",
        "Greenfield mode means implementing against the phase proposal — it never means"
        " no proposal at all.",
    ]
    print("\n".join(out))
    sys.exit(0)


# ── Mode: PreToolUse guard ────────────────────────────────────────────────────

def run_guard(root: Path) -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    target = payload.get("tool_input", {}).get("file_path", "")
    if not target:
        sys.exit(0)

    try:
        rel = os.path.relpath(target, root).replace("\\", "/")
    except ValueError:
        sys.exit(0)
    if rel.startswith(".."):
        sys.exit(0)

    config = load_coverage(root)
    if not is_source(rel, config):
        sys.exit(0)

    # A proposal touched this session means the cycle was walked.
    changed = session_changes(root)
    if any(f.replace("\\", "/").startswith("docs/changes/") for f in changed):
        sys.exit(0)

    phase = current_phase(root)
    scope = phase_scope(root, phase["slug"], config) if phase else []

    # Inside the open phase's area: the proposal exists, written in an earlier session.
    if scope and any(rel.startswith(p) for p in scope):
        sys.exit(0)

    # Unknown scope is not evidence of a violation — degrade to allowing.
    if phase and not scope:
        sys.exit(0)

    if consume_skip_authorization(root):
        sys.exit(0)

    if phase:
        reason = (
            f"open phase is {phase['id']} {phase['name']} (scope: "
            f"{', '.join(scope)}), and this file is outside it"
        )
    else:
        reason = "no phase is marked `in progress` in docs/roadmap.md"

    print(f"\n[BLOCK] SDD: {rel} — {reason}\n", file=sys.stderr)
    print("   No proposal was opened or advanced this session. Either:", file=sys.stderr)
    print("   1. Open docs/changes/{YYYY-MM-DD}-{slug}/proposal.md for this work, or",
          file=sys.stderr)
    print("   2. Name the existing proposal that covers it and update its Status",
          file=sys.stderr)
    print("\n   Trivial fix (typo, one-liner)? Ask the owner to create", file=sys.stderr)
    print("   .claude/skip-doc-authorized — consumed on first use.\n", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    root = repo_root()
    if "--guard" in sys.argv:
        run_guard(root)
    else:
        try:
            sys.stdin.read()
        except Exception:
            pass
        run_inject(root)


if __name__ == "__main__":
    main()
