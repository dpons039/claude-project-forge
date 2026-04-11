#!/usr/bin/env python3
"""
doc-check.py — Stop hook + modo pre-commit

Dos niveles de verificación:
  • blocking_triggers: migraciones BD, infra → BLOQUEA commit si falta doc
  • warning_triggers: código general → AVISA pero no bloquea (el agente decide)

Modos de uso:
  • Stop hook (Claude Code):  invocado desde settings.local.json sin argumentos
  • Pre-commit (git hook):    invocado con --pre-commit desde .githooks/pre-commit

Bypass: SKIP_DOC_CHECK=1 git commit -m "..."
"""

from __future__ import annotations

import fnmatch
import json
import os
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
    Verifica si ficheros que matchean un trigger tienen su doc esperado en el commit.
    Retorna (ficheros_sin_cobertura, {fichero: [docs_esperados]}).
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


# ── Modo Stop ─────────────────────────────────────────────────────────────────

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

    # Check docs no indexados
    unindexed = check_doc_index(root, changed_files)
    if unindexed:
        print("\n📋 DOC INDEX: fichero(s) en docs/ no registrados en docs/README.md\n", file=sys.stderr)
        for path in unindexed:
            print(f"   → {path}", file=sys.stderr)
        print("\n   Añádelos a docs/README.md\n", file=sys.stderr)

    # Check planning y changelog
    missing_planning, missing_changelog = check_progress_docs(changed_files, config)
    if missing_planning:
        print("\n📅 PLANNING: cambios en áreas de progreso sin actualizar docs/planning.md\n", file=sys.stderr)
        for path in missing_planning[:5]:
            print(f"   → {path}", file=sys.stderr)
        print("\n   Actualiza el estado en docs/planning.md si la tarea sigue en curso\n", file=sys.stderr)
    if missing_changelog:
        print("\n📋 CHANGELOG: cambios completados sin registrar en docs/changelog.md\n", file=sys.stderr)
        for path in missing_changelog[:5]:
            print(f"   → {path}", file=sys.stderr)
        print("\n   Registra el cambio en docs/changelog.md si la tarea está completada\n", file=sys.stderr)

    # Check blocking triggers (migraciones, infra)
    blocking = config.get("blocking_triggers", [])
    uncovered_blocking, suggestions_blocking = check_triggers(changed_files, blocking, doc_files)
    if uncovered_blocking:
        print("\n📚 DOC OBLIGATORIO: ficheros con cobertura requerida sin actualizar docs\n", file=sys.stderr)
        printed: set[str] = set()
        for src, docs in suggestions_blocking.items():
            for doc in docs:
                if doc not in printed:
                    print(f"   → {doc}  (requerido por: {src})", file=sys.stderr)
                    printed.add(doc)
        print("", file=sys.stderr)

    # Check warning triggers (código general)
    warning = config.get("warning_triggers", [])
    uncovered_warning, suggestions_warning = check_triggers(changed_files, warning, doc_files)
    if uncovered_warning:
        print("\n💡 DOC SUGERIDO: cambios en áreas con docs de área asociados\n", file=sys.stderr)
        print("   Si el cambio es arquitectónico, considera actualizar:\n", file=sys.stderr)
        printed: set[str] = set()
        for src, docs in suggestions_warning.items():
            for doc in docs:
                if doc not in printed:
                    print(f"   → {doc}", file=sys.stderr)
                    printed.add(doc)
        print("", file=sys.stderr)


# ── Modo pre-commit ───────────────────────────────────────────────────────────

def run_precommit_mode(root: Path) -> None:
    if os.environ.get("SKIP_DOC_CHECK", "0") == "1":
        if consume_skip_authorization(root):
            sys.exit(0)
        print("\n🔒 SKIP_DOC_CHECK=1 requiere autorización previa del propietario\n", file=sys.stderr)
        print("   Crea manualmente el fichero .claude/skip-doc-authorized para autorizar", file=sys.stderr)
        print("   un bypass puntual (se elimina automáticamente tras el uso)\n", file=sys.stderr)
        sys.exit(1)

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

    # Check docs no indexados (BLOCKING)
    unindexed = check_doc_index(root, staged)
    if unindexed:
        print("\n📋 COMMIT BLOQUEADO — fichero(s) en docs/ no registrados en docs/README.md\n", file=sys.stderr)
        for path in unindexed:
            print(f"   → {path}", file=sys.stderr)
        print("\n   Añádelos a docs/README.md antes de commitear\n", file=sys.stderr)
        print('   Para saltar: SKIP_DOC_CHECK=1 git commit -m "..."\n', file=sys.stderr)
        sys.exit(1)

    # Check planning y changelog (BLOCKING)
    missing_planning, missing_changelog = check_progress_docs(staged, config)
    if missing_planning or missing_changelog:
        print("\n📅 COMMIT BLOQUEADO — docs de progreso desactualizados\n", file=sys.stderr)
        if missing_planning:
            print("   ❌ docs/planning.md no está en el commit", file=sys.stderr)
            print("      Actualiza el estado de la tarea\n", file=sys.stderr)
        if missing_changelog:
            print("   ❌ docs/changelog.md no está en el commit", file=sys.stderr)
            print("      Registra el cambio completado\n", file=sys.stderr)
        triggered = missing_planning or missing_changelog
        for path in triggered[:5]:
            print(f"   → {path}", file=sys.stderr)
        print('', file=sys.stderr)
        print('   Para saltar: SKIP_DOC_CHECK=1 git commit -m "..."\n', file=sys.stderr)
        sys.exit(1)

    # Check blocking triggers (BLOCKING — migraciones, infra)
    blocking = config.get("blocking_triggers", [])
    uncovered_blocking, suggestions_blocking = check_triggers(staged, blocking, doc_files)
    if uncovered_blocking:
        print("\n📚 COMMIT BLOQUEADO — docs obligatorios no actualizados\n", file=sys.stderr)
        for f in uncovered_blocking[:8]:
            print(f"   • {f}", file=sys.stderr)
        print("\n   Docs que necesitan actualización:\n", file=sys.stderr)
        printed: set[str] = set()
        for src, docs in suggestions_blocking.items():
            for doc in docs:
                if doc not in printed:
                    print(f"   → {doc}", file=sys.stderr)
                    printed.add(doc)
        print('\n   Para saltar: SKIP_DOC_CHECK=1 git commit -m "..."\n', file=sys.stderr)
        sys.exit(1)

    # Check warning triggers (WARNING — código general, no bloquea)
    warning = config.get("warning_triggers", [])
    uncovered_warning, suggestions_warning = check_triggers(staged, warning, doc_files)
    if uncovered_warning:
        print("\n💡 AVISO: cambios en áreas con docs asociados\n", file=sys.stderr)
        print("   Si el cambio es arquitectónico, considera actualizar:\n", file=sys.stderr)
        printed: set[str] = set()
        for src, docs in suggestions_warning.items():
            for doc in docs:
                if doc not in printed:
                    print(f"   → {doc}", file=sys.stderr)
                    printed.add(doc)
        print("", file=sys.stderr)

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
