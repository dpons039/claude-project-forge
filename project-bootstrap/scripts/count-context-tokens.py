#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
"""
count-context-tokens.py — Context Load Simulation for Claude Code

Simulates what Claude Code injects into the context window at startup
and during a session. Based on observed Claude Code behavior (Mar 2026).

Classification based on documented behavior:
  EAGER  = always in context window from first message
  LAZY   = loaded on-demand when relevant (skill invoked, command run, etc.)
  PARSED = read by Claude Code internally but NOT injected as text
  OPAQUE = known to exist but token count not measurable

Sources:
  - code.claude.com/docs/en/sub-agents (agents = eager)
  - code.claude.com/docs/en/settings (settings = parsed internally)
  - TDS "Claude Skills and Subagents" Feb 2026 (skills = lazy, ~100 tok metadata eager)
  - github.com/anthropics/claude-code/issues/7336 (MCP = eager)
  - github.com/anthropics/claude-code/issues/8997 (agents = eager, confirmed)

Estimation: len(text) // 4 (~±10% vs cl100k_base tokenizer)
For exact count: anthropic API client.messages.count_tokens()

Usage:
  python scripts/claude/count-context-tokens.py           # auto-detect repo root
  python scripts/claude/count-context-tokens.py /path     # explicit root
  python scripts/claude/count-context-tokens.py --verbose  # show file-level detail in lazy
"""

import json
import os
import sys
import glob
import re


# ═══════════════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════════════

VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv

# Thresholds for warnings
EAGER_WARN_HIGH = 5000
EAGER_WARN_MOD = 3000
SINGLE_FILE_WARN = 800  # warn if a single eager file exceeds this


# ═══════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════

def tok(text: str) -> int:
    """Estimate tokens. ~±10% vs cl100k_base."""
    return len(text) // 4


def read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, PermissionError, IsADirectoryError, UnicodeDecodeError):
        return ""


def parse_frontmatter(content: str) -> dict:
    """Extract name, description, paths from YAML frontmatter (no PyYAML)."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not m:
        return {}
    raw = m.group(1)
    result = {}
    for key in ("description", "name", "model"):
        match = re.search(rf'^{key}:\s*["\']?(.*?)["\']?\s*$', raw, re.MULTILINE)
        if match:
            result[key] = match.group(1)
    # paths: simple YAML list
    in_paths = False
    paths = []
    for line in raw.split("\n"):
        if re.match(r"^paths:\s*$", line):
            in_paths = True
            continue
        if in_paths:
            pm = re.match(r'^\s+-\s+["\']?(.*?)["\']?\s*$', line)
            if pm:
                paths.append(pm.group(1))
            else:
                break
    if paths:
        result["paths"] = paths
    return result


def body_size(content: str) -> int:
    """Size of body after frontmatter (loaded lazy for skills)."""
    m = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
    return len(content) - len(m.group(0)) if m else len(content)


def extract_at_imports(content: str) -> list:
    return re.findall(r"^@(\S+)", content, re.MULTILINE)


def extract_doc_references(content: str) -> list:
    refs = set()
    refs.update(re.findall(r'`(docs/[^`]+)`', content))
    refs.update(re.findall(r'(?:^|\s)(docs/\S+\.md)', content, re.MULTILINE))
    return sorted(refs)


def find_repo_root(start: str) -> str:
    current = os.path.abspath(start)
    candidates = {".git": None, "CLAUDE.md": None, ".claude": None}
    while True:
        for marker in candidates:
            if os.path.exists(os.path.join(current, marker)) and candidates[marker] is None:
                candidates[marker] = current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    for marker in (".git", "CLAUDE.md", ".claude"):
        if candidates[marker]:
            return candidates[marker]
    return os.path.abspath(start)


def glob_md(directory: str) -> list:
    return sorted(glob.glob(os.path.join(directory, "*.md"))) if os.path.isdir(directory) else []


def glob_subdirs(directory: str, filename: str) -> list:
    return sorted(glob.glob(os.path.join(directory, "*", filename))) if os.path.isdir(directory) else []


def fmt_tok(n: int) -> str:
    return f"~{n:>6,} tok"


def fmt_ch(n: int) -> str:
    return f"{n:>7,} ch"


# ═══════════════════════════════════════════════════════
# Collector
# ═══════════════════════════════════════════════════════

class ContextItem:
    def __init__(self, label, chars, tokens, detail=""):
        self.label = label
        self.chars = chars
        self.tokens = tokens
        self.detail = detail


class ContextCategory:
    def __init__(self, name, load_type, explanation=""):
        self.name = name
        self.load_type = load_type  # EAGER, LAZY, PARSED, OPAQUE
        self.explanation = explanation
        self.items = []

    def add(self, label, content, detail=""):
        if not content:
            return
        self.items.append(ContextItem(label, len(content), tok(content), detail))

    def total_tokens(self):
        return sum(i.tokens for i in self.items)

    def total_chars(self):
        return sum(i.chars for i in self.items)


# ═══════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if args:
        explicit = os.path.abspath(args[0])
        if not os.path.isdir(explicit):
            print(f"Error: {args[0]} is not a directory")
            sys.exit(1)
        repo = explicit
    else:
        repo = find_repo_root(os.getcwd())

    home = os.path.expanduser("~")
    dot_claude = os.path.join(repo, ".claude")

    categories = []

    # ─────────────────────────────────────────────────
    # EAGER: CLAUDE.md (ancestor walk)
    # ─────────────────────────────────────────────────
    cat_claude = ContextCategory(
        "CLAUDE.md (ancestor walk)", "EAGER",
        "Merged top-down. All content injected into system prompt."
    )
    for fname in ("CLAUDE.md", "CLAUDE.local.md"):
        current = os.path.abspath(repo)
        while True:
            candidate = os.path.join(current, fname)
            if os.path.isfile(candidate):
                rel = os.path.relpath(candidate, repo)
                if rel == fname:
                    rel = "."
                cat_claude.add(f"{fname} ({rel})", read(candidate))
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
    # .claude/CLAUDE.md alternative
    alt = os.path.join(dot_claude, "CLAUDE.md")
    if os.path.isfile(alt) and os.path.abspath(alt) != os.path.abspath(os.path.join(repo, "CLAUDE.md")):
        cat_claude.add(".claude/CLAUDE.md", read(alt))
    # Global
    for fname in ("CLAUDE.md", "CLAUDE.local.md"):
        gpath = os.path.join(home, ".claude", fname)
        content = read(gpath)
        if content:
            cat_claude.add(f"~/.claude/{fname}", content)
    categories.append(cat_claude)

    # ─────────────────────────────────────────────────
    # EAGER: Rules (project + global)
    # ─────────────────────────────────────────────────
    cat_rules = ContextCategory(
        "Rules", "EAGER",
        "Loaded by path match. paths: ['**/*'] = always loaded."
    )
    for path in glob_md(os.path.join(dot_claude, "rules")):
        content = read(path)
        fm = parse_frontmatter(content)
        paths_info = ", ".join(fm.get("paths", ["(no paths)"])) if fm else "(no frontmatter)"
        cat_rules.add(
            f".claude/rules/{os.path.basename(path)}",
            content,
            detail=f"paths: [{paths_info}]"
        )
    for path in glob_md(os.path.join(home, ".claude", "rules")):
        content = read(path)
        fm = parse_frontmatter(content)
        paths_info = ", ".join(fm.get("paths", ["(no paths)"])) if fm else "(no frontmatter)"
        cat_rules.add(
            f"~/.claude/rules/{os.path.basename(path)}",
            content,
            detail=f"paths: [{paths_info}]"
        )
    categories.append(cat_rules)

    # ─────────────────────────────────────────────────
    # EAGER: Agents (.claude/agents/*.md)
    # ─────────────────────────────────────────────────
    cat_agents = ContextCategory(
        "Agents (subagents)", "EAGER",
        "FULL content loaded at startup, in EVERY prompt.\n"
        "  Ref: github.com/anthropics/claude-code/issues/8997"
    )
    agents_file = os.path.join(repo, "AGENTS.md")
    content = read(agents_file)
    if content:
        cat_agents.add("AGENTS.md", content)
    for path in glob_md(os.path.join(dot_claude, "agents")):
        content = read(path)
        fm = parse_frontmatter(content)
        model = fm.get("model", "default")
        name = fm.get("name", os.path.basename(path))
        cat_agents.add(
            f".claude/agents/{os.path.basename(path)}",
            content,
            detail=f"name: {name}, model: {model}"
        )
    categories.append(cat_agents)

    # ─────────────────────────────────────────────────
    # EAGER: @path imports in CLAUDE.md
    # ─────────────────────────────────────────────────
    cat_imports = ContextCategory(
        "@path imports", "EAGER",
        "Files referenced with @path in CLAUDE.md. Inlined at startup."
    )
    for fname in ("CLAUDE.md", "CLAUDE.local.md"):
        fpath = os.path.join(repo, fname)
        for imp in extract_at_imports(read(fpath)):
            full = os.path.join(repo, imp)
            c = read(full)
            if c:
                cat_imports.add(f"@{imp}", c)
    categories.append(cat_imports)

    # ─────────────────────────────────────────────────
    # EAGER: Skills — METADATA ONLY (name + description)
    # ─────────────────────────────────────────────────
    cat_skills_meta = ContextCategory(
        "Skills (metadata eager)", "EAGER",
        "Only name + description loaded at startup (~100 tok/skill).\n"
        "  Full body loaded LAZY when skill is invoked.\n"
        "  Ref: TDS 'Claude Skills and Subagents' Feb 2026"
    )
    skill_bodies_lazy = []

    for base, prefix in [(repo, ""), (home, "~/")]:
        for path in glob_subdirs(os.path.join(base, ".claude", "skills"), "SKILL.md"):
            content = read(path)
            fm = parse_frontmatter(content)
            name = fm.get("name", os.path.basename(os.path.dirname(path)))
            desc = fm.get("description", "")
            fm_text = f"name: {name}\ndescription: {desc}"
            body_ch = body_size(content)
            body_tok = tok(content) - tok(fm_text)
            cat_skills_meta.add(
                f"skill: {prefix}{name}",
                fm_text,
                detail=f"body: {body_ch} ch (~{body_tok} tok lazy)"
            )
            if body_ch > 0:
                skill_bodies_lazy.append((f"skill body: {prefix}{name}", body_ch, body_tok))
    categories.append(cat_skills_meta)

    # ─────────────────────────────────────────────────
    # EAGER: User memory (MEMORY.md + individual files)
    # ─────────────────────────────────────────────────
    cat_memory = ContextCategory(
        "User memory", "EAGER",
        "MEMORY.md always loaded. Individual memory files loaded by relevance.\n"
        "  Lives in ~/.claude/projects/<project-slug>/memory/"
    )
    # Find the project memory directory by matching repo path
    projects_dir = os.path.join(home, ".claude", "projects")
    memory_dir = None
    if os.path.isdir(projects_dir):
        repo_norm = os.path.normpath(repo).replace("\\", "-").replace("/", "-").replace(":", "-").lower()
        for entry in os.listdir(projects_dir):
            entry_lower = entry.lower()
            candidate = os.path.join(projects_dir, entry, "memory")
            if os.path.isdir(candidate) and (
                entry_lower == repo_norm
                or repo_norm.endswith(entry_lower)
                or entry_lower.endswith(repo_norm)
                or all(part in entry_lower for part in os.path.normpath(repo).replace("\\", "/").split("/")[-2:])
            ):
                memory_dir = candidate
                break
        # Fallback: search all project dirs for one containing MEMORY.md
        if not memory_dir:
            for entry in os.listdir(projects_dir):
                candidate = os.path.join(projects_dir, entry, "memory")
                if os.path.isfile(os.path.join(candidate, "MEMORY.md")):
                    # Check if entry slug matches repo path parts
                    slug_parts = entry.lower().replace("-", " ").split()
                    repo_parts = [p.lower() for p in os.path.normpath(repo).replace("\\", "/").split("/") if p]
                    if any(rp in slug_parts for rp in repo_parts[-2:]):
                        memory_dir = candidate
                        break

    if memory_dir:
        # MEMORY.md is always eager
        memory_md = os.path.join(memory_dir, "MEMORY.md")
        cat_memory.add("MEMORY.md (index)", read(memory_md))
        # Individual memory files — loaded by relevance (count as eager for worst case)
        for path in sorted(glob.glob(os.path.join(memory_dir, "*.md"))):
            if os.path.basename(path).upper() == "MEMORY.MD":
                continue
            content = read(path)
            fm = parse_frontmatter(content)
            mtype = fm.get("type", "unknown")
            cat_memory.add(
                f"memory: {os.path.basename(path)}",
                content,
                detail=f"type: {mtype} (lazy by relevance)"
            )
    categories.append(cat_memory)

    # ─────────────────────────────────────────────────
    # PARSED: Settings
    # ─────────────────────────────────────────────────
    session_start_hooks = []
    mcp_servers = []
    plugins = []

    cat_settings = ContextCategory(
        "Settings", "PARSED",
        "Processed internally (permissions, hooks, env).\n"
        "  NOT injected as text into the context window."
    )
    settings_paths = [
        (os.path.join(dot_claude, "settings.json"), ".claude/settings.json"),
        (os.path.join(dot_claude, "settings.local.json"), ".claude/settings.local.json"),
        (os.path.join(home, ".claude", "settings.json"), "~/.claude/settings.json"),
    ]
    for spath, label in settings_paths:
        content = read(spath)
        if not content:
            continue
        cat_settings.add(label, content)
        try:
            cfg = json.loads(content)
            for h in cfg.get("hooks", {}).get("SessionStart", []):
                for hook in h.get("hooks", []):
                    cmd = hook.get("command", "")
                    if cmd:
                        session_start_hooks.append((label, cmd[:120]))
            for pname, enabled in cfg.get("enabledPlugins", {}).items():
                if enabled:
                    plugins.append(pname)
        except (json.JSONDecodeError, AttributeError):
            pass
    categories.append(cat_settings)

    # ─────────────────────────────────────────────────
    # PARSED: Custom JSON in .claude/
    # ─────────────────────────────────────────────────
    cat_custom = ContextCategory(
        "Custom files in .claude/", "PARSED",
        "Your custom JSON/config. NOT loaded into context.\n"
        "  Claude only sees them if it reads .claude/ directory."
    )
    skip_json = {"settings.json", "settings.local.json"}
    for path in sorted(glob.glob(os.path.join(dot_claude, "*.json"))):
        basename = os.path.basename(path)
        if basename in skip_json:
            continue
        cat_custom.add(f".claude/{basename}", read(path))
    categories.append(cat_custom)

    # ─────────────────────────────────────────────────
    # LAZY: Commands (.claude/commands/*.md)
    # ─────────────────────────────────────────────────
    cat_commands = ContextCategory(
        "Commands (slash)", "LAZY",
        "Loaded only when invoked via /command-name."
    )
    for path in glob_md(os.path.join(dot_claude, "commands")):
        cat_commands.add(f".claude/commands/{os.path.basename(path)}", read(path))
    for path in glob_md(os.path.join(home, ".claude", "commands")):
        cat_commands.add(f"~/.claude/commands/{os.path.basename(path)}", read(path))
    categories.append(cat_commands)

    # ─────────────────────────────────────────────────
    # LAZY: Skill bodies
    # ─────────────────────────────────────────────────
    cat_skills_body = ContextCategory(
        "Skills (body lazy)", "LAZY",
        "Full SKILL.md body loaded when skill is invoked."
    )
    for label, chars, tokens in skill_bodies_lazy:
        cat_skills_body.items.append(ContextItem(label, chars, tokens))
    categories.append(cat_skills_body)

    # ─────────────────────────────────────────────────
    # LAZY: Doc references in CLAUDE.md
    # ─────────────────────────────────────────────────
    doc_refs = []
    for fname in ("CLAUDE.md",):
        fpath = os.path.join(repo, fname)
        doc_refs.extend(extract_doc_references(read(fpath)))
    doc_refs = sorted(set(doc_refs))

    cat_docs = ContextCategory(
        "Docs referenced in CLAUDE.md", "LAZY",
        "Claude reads these when working in the relevant area."
    )
    for ref in doc_refs:
        full = os.path.join(repo, ref)
        if os.path.isfile(full):
            cat_docs.add(ref, read(full))
        elif os.path.isdir(full):
            dir_content = ""
            file_count = 0
            for f in sorted(glob.glob(os.path.join(full, "*.md"))):
                dir_content += read(f)
                file_count += 1
            if dir_content:
                cat_docs.items.append(ContextItem(
                    f"{ref} ({file_count} files)", len(dir_content), tok(dir_content)
                ))
        elif VERBOSE:
            cat_docs.items.append(ContextItem(ref, 0, 0, "(not found)"))
    categories.append(cat_docs)

    # ─────────────────────────────────────────────────
    # MCP servers (opaque, collected from .mcp.json)
    # ─────────────────────────────────────────────────
    for spath in (os.path.join(repo, ".mcp.json"), os.path.join(home, ".claude", "settings.json")):
        content = read(spath)
        if not content:
            continue
        try:
            cfg = json.loads(content)
            servers = cfg.get("mcpServers", {})
            if not servers and ".mcp" in os.path.basename(spath):
                servers = cfg
            for name in servers:
                if name not in mcp_servers:
                    mcp_servers.append(name)
        except (json.JSONDecodeError, AttributeError):
            pass

    # ═══════════════════════════════════════════════════════
    # Output
    # ═══════════════════════════════════════════════════════

    eager_cats = [c for c in categories if c.load_type == "EAGER" and c.items]
    lazy_cats = [c for c in categories if c.load_type == "LAZY" and c.items]
    parsed_cats = [c for c in categories if c.load_type == "PARSED" and c.items]

    eager_total = sum(c.total_tokens() for c in eager_cats)
    lazy_total = sum(c.total_tokens() for c in lazy_cats)

    max_label = 48
    for c in categories:
        for item in c.items:
            max_label = max(max_label, len(item.label) + 4)

    W = max(max_label + 28, 72)

    print(f"\n{'═' * W}")
    print(f"  Claude Code — Context Load Simulation")
    print(f"  Repo: {repo}")
    print(f"{'═' * W}")

    # ── EAGER ──
    print(f"\n  ┌─ EAGER (in context window from message #1)")
    for cat in eager_cats:
        print(f"  │")
        print(f"  ├─ [{cat.name}]")
        if cat.explanation:
            for line in cat.explanation.split("\n"):
                print(f"  │   {line}")
        for item in cat.items:
            detail = f"  ← {item.detail}" if item.detail else ""
            print(f"  │   {item.label:<{max_label}}  {fmt_ch(item.chars)}  {fmt_tok(item.tokens)}{detail}")
        print(f"  │   {'subtotal':<{max_label}}  {'':>7}     {fmt_tok(cat.total_tokens())}")
    print(f"  │")
    print(f"  └─ TOTAL EAGER  {fmt_tok(eager_total)}")

    # ── LAZY ──
    if lazy_cats:
        print(f"\n  ┌─ LAZY (loaded on-demand when relevant)")
        for cat in lazy_cats:
            print(f"  │")
            print(f"  ├─ [{cat.name}]")
            if cat.explanation:
                for line in cat.explanation.split("\n"):
                    print(f"  │   {line}")
            if VERBOSE or cat.name not in ("Docs referenced in CLAUDE.md", "Skills (body lazy)"):
                for item in cat.items:
                    detail = f"  ← {item.detail}" if item.detail else ""
                    print(f"  │   {item.label:<{max_label}}  {fmt_ch(item.chars)}  {fmt_tok(item.tokens)}{detail}")
            else:
                count = len(cat.items)
                print(f"  │   ({count} items)  total: {fmt_ch(cat.total_chars())}  {fmt_tok(cat.total_tokens())}")
                top = sorted(cat.items, key=lambda x: x.tokens, reverse=True)[:3]
                for item in top:
                    print(f"  │     top: {item.label:<{max_label - 2}}  {fmt_tok(item.tokens)}")
            print(f"  │   {'subtotal':<{max_label}}  {'':>7}     {fmt_tok(cat.total_tokens())}")
        print(f"  │")
        print(f"  └─ TOTAL LAZY (if all loaded)  {fmt_tok(lazy_total)}")

    # ── PARSED ──
    if parsed_cats:
        print(f"\n  ┌─ PARSED (read internally, NOT in context window)")
        for cat in parsed_cats:
            print(f"  │")
            print(f"  ├─ [{cat.name}]")
            if cat.explanation:
                for line in cat.explanation.split("\n"):
                    print(f"  │   {line}")
            for item in cat.items:
                print(f"  │   {item.label:<{max_label}}  {fmt_ch(item.chars)}")
        print(f"  └─ (0 tok in context window)")

    # ── OPAQUE ──
    print(f"\n  ┌─ OPAQUE (exists but not measurable)")
    print(f"  │   System prompt interno de Claude Code   ~2,000-4,000 tok (estimated)")
    print(f"  │   Tool definitions (bash, read, edit…)   ~1,000-3,000 tok (estimated)")
    print(f"  │   Git info (branch, remotes, tree)       ~200-500 tok (estimated)")
    if session_start_hooks:
        print(f"  │   SessionStart hooks output:")
        for source, cmd in session_start_hooks:
            print(f"  │     ({source}): {cmd}")
    if mcp_servers:
        print(f"  │   MCP servers (tool defs = EAGER):       ~500-1,500 tok/server")
        for name in mcp_servers:
            print(f"  │     • {name}")
    if plugins:
        print(f"  │   Plugins:")
        for pname in plugins:
            print(f"  │     • {pname}")
    opaque_min = 3200 + len(mcp_servers) * 500
    opaque_max = 7500 + len(mcp_servers) * 1500
    print(f"  └─ Estimated opaque: ~{opaque_min:,}-{opaque_max:,} tok")

    # ═══════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════

    print(f"\n{'─' * W}")
    print(f"  SUMMARY")
    print(f"{'─' * W}")
    print(f"  Eager (measurable)   {fmt_tok(eager_total):>14}")
    print(f"  Opaque (estimated)   ~{opaque_min:,}-{opaque_max:,} tok")
    real_min = eager_total + opaque_min
    real_max = eager_total + opaque_max
    print(f"  ─────────────────────────────────")
    print(f"  TOTAL at startup     ~{real_min:,}-{real_max:,} tok")
    print(f"  Lazy available       {fmt_tok(lazy_total):>14}  (added when consulted)")
    worst_case = real_max + lazy_total
    print(f"  Worst case (all)     ~{worst_case:,} tok")

    ctx_window = 200_000
    pct_min = (real_min / ctx_window) * 100
    pct_max = (real_max / ctx_window) * 100
    print(f"\n  200K window usage:")
    print(f"    At startup: {pct_min:.1f}%-{pct_max:.1f}% consumed")
    print(f"    Free for work: ~{ctx_window - real_max:,}-{ctx_window - real_min:,} tok")

    # ── Cost per call ──
    print(f"\n  Eager context cost per call:")
    for name, price in [("Haiku", 1.0), ("Sonnet", 3.0), ("Opus", 5.0)]:
        cost = (eager_total / 1_000_000) * price
        print(f"    {name:<8} ${cost:.6f}  (${price}/1M input)")

    # ── Breakdown % ──
    if eager_total > 0:
        print(f"\n  Eager distribution:")
        for cat in eager_cats:
            pct = cat.total_tokens() / eager_total * 100
            bar = "█" * int(pct / 2.5)
            print(f"    {cat.name:<35} {cat.total_tokens():>5} tok  {pct:>5.1f}%  {bar}")

    # ── Warnings ──
    print()
    if eager_total > EAGER_WARN_HIGH:
        print(f"  ⚠  Eager context HIGH ({eager_total} tok).")
    elif eager_total > EAGER_WARN_MOD:
        print(f"  ℹ  Eager context moderate ({eager_total} tok).")
    else:
        print(f"  ✓  Eager context light ({eager_total} tok).")

    # Per-file warnings
    big_files = []
    for cat in eager_cats:
        for item in cat.items:
            if item.tokens > SINGLE_FILE_WARN:
                big_files.append((cat.name, item.label, item.tokens))
    if big_files:
        print(f"\n  ⚠  Large eager files (>{SINGLE_FILE_WARN} tok):")
        for cat_name, label, tokens in sorted(big_files, key=lambda x: -x[2]):
            print(f"     {tokens:>5} tok  {label}  ({cat_name})")

    # Rules **/*
    always_rules = []
    for cat in categories:
        if cat.name != "Rules":
            continue
        for item in cat.items:
            for path in glob_md(os.path.join(dot_claude, "rules")) + glob_md(os.path.join(home, ".claude", "rules")):
                if os.path.basename(path) in item.label:
                    fm = parse_frontmatter(read(path))
                    if "**/*" in fm.get("paths", []):
                        always_rules.append((item.label, item.tokens))
    if always_rules:
        print(f"\n  ℹ  Rules with paths: ['**/*'] (loaded ALWAYS):")
        for label, tokens in always_rules:
            print(f"     {label} (~{tokens} tok)")

    # ── Recommendations ──
    print(f"\n{'─' * W}")
    print(f"  RECOMMENDATIONS")
    print(f"{'─' * W}")

    recs = []

    # Agent too big
    for cat in categories:
        if cat.name != "Agents (subagents)":
            continue
        for item in cat.items:
            if item.tokens > 500:
                recs.append(
                    f"  • {item.label} ({item.tokens} tok eager): agents load FULL content\n"
                    f"    in EVERY message. Consider moving detailed logic to a skill\n"
                    f"    (lazy) and keeping only metadata + core instructions in agent."
                )

    # CLAUDE.md too big
    for item in cat_claude.items:
        if item.tokens > 2000:
            recs.append(
                f"  • {item.label} ({item.tokens} tok): consider moving sections\n"
                f"    that only apply to specific areas to rules with restricted paths."
            )

    # model-routing as **/* rule
    for label, tokens in always_rules:
        if tokens > 400:
            recs.append(
                f"  • {label} ({tokens} tok): rule with paths: ['**/*'].\n"
                f"    Compress examples or move detail to a lazy doc."
            )

    # Skills metadata total
    for cat in eager_cats:
        if cat.name == "Skills (metadata eager)" and cat.total_tokens() > 800:
            recs.append(
                f"  • {cat.total_tokens()} tok in {len(cat.items)} skill descriptions.\n"
                f"    Keep descriptions short (<50 words). Each skill ≈{cat.total_tokens() // len(cat.items)} tok avg."
            )

    if not recs:
        print(f"  ✓  No specific recommendations.")
    else:
        for r in recs:
            print(r)

    print(f"\n  ⚠  Estimation ±10%. For exact count: anthropic API count_tokens()")
    print()


if __name__ == "__main__":
    main()
