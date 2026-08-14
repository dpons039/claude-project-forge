#!/usr/bin/env python3
"""
doc-check.py — Stop hook + modo pre-commit

Two verification levels:
  • blocking_triggers: DB migrations, infra → BLOCKS commit if doc missing
  • warning_triggers: general code → WARNS but does not block (the agent decides)

Usage modes:
  • Stop hook (Claude Code):  invoked from settings.local.json with no arguments
  • Pre-commit (git hook):    invoked with --pre-commit from .githooks/pre-commit

Bypass: SKIP_DOC_CHECK=1 git commit -m "..."
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path


# ── Helpers ───────────────────────────────────────────────────────────────────

def repo_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        return Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))


def load_coverage(root: Path) -> dict:
    config_path = root / ".claude" / "doc-coverage.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"exempt": [], "blocking_triggers": [], "warning_triggers": []}


def is_exempt(path: str, exempt_patterns: list[str]) -> bool:
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


def is_doc(path: str) -> bool:
    doc_prefixes = ("docs/", "CLAUDE.md", ".claude/rules/", "memory/")
    return any(path == p or path.startswith(p) for p in doc_prefixes)


def consume_skip_authorization(root: Path) -> bool:
    auth_file = root / ".claude" / "skip-doc-authorized"
    if auth_file.exists():
        try:
            auth_file.unlink()
        except Exception:
            pass
        return True
    return False


INDEX_EXEMPT_PREFIXES = (
    "docs/_archive/",
    "docs/_template/",
    "docs/changes/",
)


def check_doc_index(root: Path, changed_files: list[str]) -> list[str]:
    readme_path = root / "docs" / "README.md"
    if not readme_path.exists():
        return []

    readme_content = readme_path.read_text(encoding="utf-8")

    uncovered = []
    for path in changed_files:
        if not path.startswith("docs/") or not path.endswith(".md"):
            continue
        if path == "docs/README.md":
            continue
        if any(path.startswith(prefix) for prefix in INDEX_EXEMPT_PREFIXES):
            continue
        path_without_docs = path.removeprefix("docs/")
        if path not in readme_content and path_without_docs not in readme_content:
            basename = os.path.basename(path)
            if basename not in readme_content:
                uncovered.append(path)

    return uncovered


def check_progress_docs(changed_files: list[str], config: dict) -> tuple[list[str], list[str]]:
    triggers = config.get("planning_triggers", [])
    if not triggers:
        return [], []

    triggered = []
    for f in changed_files:
        for pattern in triggers:
            if f.startswith(pattern):
                triggered.append(f)
                break

    if not triggered:
        return [], []

    missing_planning = [] if "docs/planning.md" in changed_files else triggered
    missing_changelog = [] if "docs/changelog.md" in changed_files else triggered
    return missing_planning, missing_changelog


def check_triggers(
    changed_files: list[str],
    triggers: list[dict],
    doc_files: set[str],
) -> tuple[list[str], dict[str, list[str]]]:
    """
    Check whether files matching a trigger have their expected doc in the commit.
    Returns (uncovered_files, {file: [expected_docs]}).
    """
    uncovered: list[str] = []
    suggestions: dict[str, list[str]] = {}

    for f in changed_files:
        if is_doc(f):
            continue

        matched_docs: list[str] = []
        for entry in triggers:
            pattern = entry.get("pattern", "")
            if f.startswith(pattern):
                matched_docs.extend(entry.get("docs", []))

        if not matched_docs:
            continue

        if not any(doc in doc_files for doc in matched_docs):
            uncovered.append(f)
            suggestions[f] = matched_docs

    return uncovered, suggestions


# ── Stop mode ─────────────────────────────────────────────────────────────────



# ── Size guardrails (2026-08: docs bloat is the failure mode 5.x models amplify) ──

SIZE_CAPS = {
    # path (repo-relative): (warn_lines, block_lines)
    "docs/planning.md": (100, 130),
    "docs/changelog.md": (500, 600),
    # A table, not prose: one row per phase plus a bullet per deferred idea. It should
    # bite well before a prose-sized cap would, because the fix here is archiving rows,
    # not compressing sentences.
    "docs/roadmap.md": (150, 200),
}
# Area docs (any other docs/*.md) grow legitimately — one decision block per ruling.
# Two thresholds, generous on purpose:
#   soft (500): suggest splitting into subdocuments (docs/X.md -> docs/X/). No block.
#   hard (1000): actually block — a 1000-line area doc is unmanageable, split it now.
# The soft/hard gap gives room to grow; the hard cap is the safety net so a doc
# can't balloon forever unnoticed. (Progress docs keep their own tighter SIZE_CAPS.)
AREA_DOC_SUBDIVIDE = 500
AREA_DOC_HARD = 1000

# decisions.md is the store of decision reasoning (### D-n per decision). It is now
# self-limiting: the moment a decision is superseded its ### D-n LEAVES for
# _archive/decisions.md, so the store only ever holds in-force decisions and grows only
# with genuine live complexity. No scaling formula — just a single high hard-cap WARN as
# a runaway backstop (never blocks; the fix is real single-source, see check_decisions).
DECISIONS_HARD = 1500          # absolute backstop (warn only)


def check_doc_sizes(root: Path, changed_files: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Sizes of progress + area docs touched this session.
    Returns (warnings, blockers, subdivide_suggestions). Progress docs block at
    their SIZE_CAPS; area docs suggest a split at 500 and hard-block at 1000."""
    warnings: list[str] = []
    blockers: list[str] = []
    subdivide: list[str] = []
    for f in changed_files:
        norm = f.replace("\\", "/")
        if not (norm.startswith("docs/") and norm.endswith(".md")):
            continue
        if "/_archive/" in norm or norm.startswith("docs/changes/"):
            continue
        p = root / norm
        try:
            n = sum(1 for _ in open(p, encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if norm in SIZE_CAPS:
            warn, block = SIZE_CAPS[norm]
            if n >= block:
                blockers.append(f"{norm}: {n} lines (hard cap {block})")
            elif n > warn:
                warnings.append(f"{norm}: {n} lines (cap {warn})")
        elif norm == "docs/decisions.md":
            # self-limiting store (superseded ### D-n leave for _archive) — only a high
            # fixed backstop WARN, never a blocker. Semantic checks live in check_decisions.
            if n > DECISIONS_HARD:
                warnings.append(f"{norm}: {n} lines (backstop {DECISIONS_HARD}) — "
                                f"superseded ### D-n should have left for _archive/decisions.md")
        elif norm.count("/") == 1:
            # area doc: split-suggestion at soft, hard block only at 1000
            if n >= AREA_DOC_HARD:
                blockers.append(f"{norm}: {n} lines (hard cap {AREA_DOC_HARD}) — split it now")
            elif n > AREA_DOC_SUBDIVIDE:
                subdivide.append(f"{norm}: {n} lines — consider splitting into docs/"
                                 f"{norm[len('docs/'):-len('.md')]}/")
    return warnings, blockers, subdivide


# ── Decisions single-source validator (warn-only) ─────────────────────────────
#
# One decision lives in exactly ONE place: a `### D-n` block in docs/decisions.md.
# When a decision is superseded, its block MOVES whole to docs/_archive/decisions.md
# and a `**Superseded by D-m**` line is added there. Nothing superseded stays in the
# store. This validator WARNS (never blocks) when that single-source invariant breaks.
# It reads _archive/decisions.md as the one explicit exception to the _archive scan-skip.

_D_HEADING = re.compile(r"^### (D\d+)\b", re.MULTILINE)
_SUPERSEDED_BY = re.compile(r"\bSuperseded by (D\d+)\b")
_SUPERSEDES = re.compile(r"\bSupersedes (D\d+)\b")


def _read_ids(path: Path) -> tuple[list[str], str]:
    """Return (list of ### D-n ids in file order, full text). Missing file → ([], '')."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], ""
    return _D_HEADING.findall(text), text


def _blocks_with_superseded_by(text: str) -> set[str]:
    """IDs of `### D-n` blocks whose body carries a `Superseded by` line.
    A block runs from its heading to the next `### ` (or EOF)."""
    out: set[str] = set()
    parts = re.split(r"(?m)^### (D\d+)\b", text)
    # parts = [preamble, id1, body1, id2, body2, ...]
    for i in range(1, len(parts) - 1, 2):
        did, body = parts[i], parts[i + 1]
        if _SUPERSEDED_BY.search(body):
            out.add(did)
    return out


def check_decisions(root: Path) -> list[str]:
    """Warn-only single-source checks on the decision store + its archive.
    Returns a list of warning strings (empty when the store looks consistent)."""
    store_path = root / "docs" / "decisions.md"
    archive_path = root / "docs" / "_archive" / "decisions.md"
    if not store_path.exists():
        return []

    store_ids, store_text = _read_ids(store_path)
    archive_ids, archive_text = _read_ids(archive_path)
    warnings: list[str] = []

    # 1. Unique IDs across store + archive (an ID is never reused, not even archived)
    seen: dict[str, int] = {}
    for did in store_ids + archive_ids:
        seen[did] = seen.get(did, 0) + 1
    dupes = sorted(d for d, c in seen.items() if c > 1)
    if dupes:
        warnings.append("duplicate decision id(s) across decisions.md + _archive: "
                        + ", ".join(dupes))

    # 2. No `Superseded by` line survives in the store — that block should have left
    stale = sorted(set(_SUPERSEDED_BY.findall(store_text)))
    store_id_set = set(store_ids)
    for tgt in stale:
        warnings.append(f"decisions.md still carries a 'Superseded by {tgt}' line — "
                        f"the superseded ### D-n must move to _archive/decisions.md")

    # 3. A superseded target must NOT still have a live heading in the store
    archive_supersedes = set(_SUPERSEDES.findall(archive_text))
    store_supersedes = set(_SUPERSEDES.findall(store_text))
    for tgt in sorted(archive_supersedes | store_supersedes):
        if tgt in store_id_set:
            warnings.append(f"{tgt} is named as superseded but still has a live ### {tgt} "
                            f"in decisions.md — it should be in _archive/decisions.md")

    # 4. Mirror check: each `Supersedes D-n` (new block) needs the archived ### D-n
    #    to exist AND carry its own `Superseded by` line (bidirectional link).
    archive_id_set = set(archive_ids)
    archive_marked = _blocks_with_superseded_by(archive_text)
    for tgt in sorted(store_supersedes | archive_supersedes):
        if tgt not in archive_id_set:
            warnings.append(f"a 'Supersedes {tgt}' line has no matching ### {tgt} in "
                            f"_archive/decisions.md (broken supersede link)")
        elif tgt not in archive_marked:
            warnings.append(f"### {tgt} in _archive/decisions.md lacks its "
                            f"'**Superseded by ...**' mirror line")

    return warnings


def run_stop_mode(root: Path) -> None:
    changes_path = root / ".session-changes.json"

    try:
        with open(changes_path, "r", encoding="utf-8") as f:
            changed_files: list[str] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return
    finally:
        try:
            changes_path.unlink(missing_ok=True)
        except Exception:
            pass

    if not changed_files:
        return

    config = load_coverage(root)
    doc_files = set(f for f in changed_files if is_doc(f))

    # Check sizes - only files touched this session. Progress docs can block;
    # area docs only ever suggest splitting (they grow legitimately).
    size_warnings, size_blockers, size_subdivide = check_doc_sizes(root, changed_files)
    if size_subdivide:
        print("\n[SPLIT] AREA DOC: large enough to split into subdocuments (not a block)\n", file=sys.stderr)
        for s in size_subdivide:
            print(f"   -> {s}", file=sys.stderr)
        print("\n   Area docs grow legitimately; when one gets big, split it (docs/X.md -> docs/X/)", file=sys.stderr)
        print("   and index the parts in docs/README.md. No rush — this is a suggestion.\n", file=sys.stderr)
    if size_warnings:
        print("\n[SIZE] DOC SIZE: over the cap - compress or archive before adding more\n", file=sys.stderr)
        for w in size_warnings:
            print(f"   -> {w}", file=sys.stderr)
        print("\n   planning.md: current phase only, 1-2 line entries (roadmap -> docs/roadmap.md)", file=sys.stderr)
        print("   changelog.md: rotate oldest entries to docs/_archive/changelog/\n", file=sys.stderr)
    if size_blockers:
        print("\n[BLOCK] DOC SIZE: hard cap exceeded - fix it NOW\n", file=sys.stderr)
        for b in size_blockers:
            print(f"   -> {b}", file=sys.stderr)
        print("\n   Compress the file (1-2 line entries, narrative -> _archive/ or a linked file)", file=sys.stderr)
        print("   then stop again. Rules: docs/doc-system.md\n", file=sys.stderr)
        sys.exit(2)

    # Decisions single-source (warn-only) — run when the store or its archive was touched
    if any(f.replace("\\", "/") in ("docs/decisions.md", "docs/_archive/decisions.md")
           for f in changed_files):
        decision_warnings = check_decisions(root)
        if decision_warnings:
            print("\n[DECISIONS] single-source check — a decision must live in ONE place\n", file=sys.stderr)
            for w in decision_warnings:
                print(f"   -> {w}", file=sys.stderr)
            print("\n   Fix: one ### D-n per decision; superseded ones move whole to", file=sys.stderr)
            print("   docs/_archive/decisions.md. Delegate to doc-updater. Rules: docs/doc-system.md\n", file=sys.stderr)

    # Check unindexed docs
    unindexed = check_doc_index(root, changed_files)
    if unindexed:
        print("\n📋 DOC INDEX: file(s) in docs/ not listed in docs/README.md\n", file=sys.stderr)
        for path in unindexed:
            print(f"   → {path}", file=sys.stderr)
        print("\n   Add them to docs/README.md\n", file=sys.stderr)

    # Check planning and changelog
    missing_planning, missing_changelog = check_progress_docs(changed_files, config)
    if missing_planning:
        print("\n📅 PLANNING: changes in tracked areas without updating docs/planning.md\n", file=sys.stderr)
        for path in missing_planning[:5]:
            print(f"   → {path}", file=sys.stderr)
        print("\n   Update the status in docs/planning.md if the task is still in progress\n", file=sys.stderr)
    if missing_changelog:
        print("\n📋 CHANGELOG: completed changes not recorded in docs/changelog.md\n", file=sys.stderr)
        for path in missing_changelog[:5]:
            print(f"   → {path}", file=sys.stderr)
        print("\n   Record the change in docs/changelog.md if the task is complete\n", file=sys.stderr)

    # Check blocking triggers (migrations, infra)
    blocking = config.get("blocking_triggers", [])
    uncovered_blocking, suggestions_blocking = check_triggers(changed_files, blocking, doc_files)
    if uncovered_blocking:
        print("\n📚 DOC REQUIRED: files with required coverage without updating docs\n", file=sys.stderr)
        printed: set[str] = set()
        for src, docs in suggestions_blocking.items():
            for doc in docs:
                if doc not in printed:
                    print(f"   → {doc}  (required by: {src})", file=sys.stderr)
                    printed.add(doc)
        print("", file=sys.stderr)

    # Check warning triggers (general code)
    warning = config.get("warning_triggers", [])
    uncovered_warning, suggestions_warning = check_triggers(changed_files, warning, doc_files)
    if uncovered_warning:
        print("\n💡 DOC SUGGESTED: changes in areas with associated area docs\n", file=sys.stderr)
        print("   If the change is architectural, consider updating:\n", file=sys.stderr)
        printed: set[str] = set()
        for src, docs in suggestions_warning.items():
            for doc in docs:
                if doc not in printed:
                    print(f"   → {doc}", file=sys.stderr)
                    printed.add(doc)
        print("", file=sys.stderr)


# ── Pre-commit mode ───────────────────────────────────────────────────────────

def run_precommit_mode(root: Path) -> None:
    # Two independent bypasses, OR'd. The file is a one-shot token: try to
    # consume it unconditionally so it never survives a commit. The env var is
    # a transient flag. Either one skips the doc-check.
    file_authorized = consume_skip_authorization(root)
    env_skip = os.environ.get("SKIP_DOC_CHECK", "0") == "1"
    if file_authorized or env_skip:
        sys.exit(0)

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True, text=True, check=True,
        )
        staged = [f.strip() for f in result.stdout.split("\n") if f.strip()]
    except subprocess.CalledProcessError:
        sys.exit(0)

    if not staged:
        sys.exit(0)

    config = load_coverage(root)
    doc_files = set(f for f in staged if is_doc(f))

    # Check unindexed docs (BLOCKING)
    unindexed = check_doc_index(root, staged)
    if unindexed:
        print("\n📋 COMMIT BLOCKED — file(s) in docs/ not listed in docs/README.md\n", file=sys.stderr)
        for path in unindexed:
            print(f"   → {path}", file=sys.stderr)
        print("\n   Add them to docs/README.md before committing\n", file=sys.stderr)
        print('   To skip: SKIP_DOC_CHECK=1 git commit -m "..."\n', file=sys.stderr)
        sys.exit(1)

    # Check planning and changelog (BLOCKING)
    missing_planning, missing_changelog = check_progress_docs(staged, config)
    if missing_planning or missing_changelog:
        print("\n📅 COMMIT BLOCKED — progress docs out of date\n", file=sys.stderr)
        if missing_planning:
            print("   ❌ docs/planning.md is not in the commit", file=sys.stderr)
            print("      Update the task status\n", file=sys.stderr)
        if missing_changelog:
            print("   ❌ docs/changelog.md is not in the commit", file=sys.stderr)
            print("      Record the completed change\n", file=sys.stderr)
        triggered = missing_planning or missing_changelog
        for path in triggered[:5]:
            print(f"   → {path}", file=sys.stderr)
        print('', file=sys.stderr)
        print('   To skip: SKIP_DOC_CHECK=1 git commit -m "..."\n', file=sys.stderr)
        sys.exit(1)

    # Check blocking triggers (BLOCKING — migrations, infra)
    blocking = config.get("blocking_triggers", [])
    uncovered_blocking, suggestions_blocking = check_triggers(staged, blocking, doc_files)
    if uncovered_blocking:
        print("\n📚 COMMIT BLOCKED — required docs not updated\n", file=sys.stderr)
        for f in uncovered_blocking[:8]:
            print(f"   • {f}", file=sys.stderr)
        print("\n   Docs that need updating:\n", file=sys.stderr)
        printed: set[str] = set()
        for src, docs in suggestions_blocking.items():
            for doc in docs:
                if doc not in printed:
                    print(f"   → {doc}", file=sys.stderr)
                    printed.add(doc)
        print('\n   To skip: SKIP_DOC_CHECK=1 git commit -m "..."\n', file=sys.stderr)
        sys.exit(1)

    # Check warning triggers (WARNING — general code, non-blocking)
    warning = config.get("warning_triggers", [])
    uncovered_warning, suggestions_warning = check_triggers(staged, warning, doc_files)
    if uncovered_warning:
        print("\n💡 NOTICE: changes in areas with associated docs\n", file=sys.stderr)
        print("   If the change is architectural, consider updating:\n", file=sys.stderr)
        printed: set[str] = set()
        for src, docs in suggestions_warning.items():
            for doc in docs:
                if doc not in printed:
                    print(f"   → {doc}", file=sys.stderr)
                    printed.add(doc)
        print("", file=sys.stderr)

    # Decisions single-source (NOTICE — non-blocking) when the store/archive is staged
    if any(f in ("docs/decisions.md", "docs/_archive/decisions.md") for f in staged):
        decision_warnings = check_decisions(root)
        if decision_warnings:
            print("\n💡 DECISIONS: single-source check (not blocking)\n", file=sys.stderr)
            for w in decision_warnings:
                print(f"   → {w}", file=sys.stderr)
            print("\n   One ### D-n per decision; superseded ones move to _archive/decisions.md\n", file=sys.stderr)

    sys.exit(0)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    root = repo_root()
    if "--pre-commit" in sys.argv:
        run_precommit_mode(root)
    else:
        try:
            sys.stdin.read()
        except Exception:
            pass
        run_stop_mode(root)


if __name__ == "__main__":
    main()
