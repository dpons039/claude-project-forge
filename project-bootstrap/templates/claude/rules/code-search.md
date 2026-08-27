---
description: Code search strategy — right tool for each search type
---

# Code Search — Tool by Problem Type

If you already read the file this session → use what you have in context, don't search again.

## By search type

| I need to... | Tool | Example |
|---|---|---|
| Find files by name/pattern | **Glob** | `*.test.ts`, `stores/*.ts` |
| Search literal text or name | **Grep** | string, variable, TODO, import `from "x"` |
| Search code structure | **`ast-grep`** skill | functions without try/catch, components with a hook, calls with N args |

Grep and ast-grep solve different problems — choose by what you're searching for, don't escalate from one to the other.

## Read vs search

Search finds *where*; reading tells you *what it says*. Don't confuse them:

- About to **edit** a file, or **confirm what a specific line says** → **Read the
  whole file** (if ≲300 lines; if larger, Read the range with margin above and
  below — never a single isolated line). The adjacent context is where the
  contradictions hide: a line can be correct and the line above it invalidate it.
- Only need to **locate** which file/line something is in, among many → Grep. Then
  Read it.
- A `grep`/`sed` of one isolated line **never** settles a claim. "Line N says X"
  requires having read its surroundings.

## Which file — by PLACE, not by mechanism

`Read vs search` picks the tool. This picks the **target**, and it is the one that goes
wrong silently: you find a file, it does something like what you need, and you never
learn it was the wrong one.

- **By mechanism** — "how is a picker mounted inside a modal?", "where else is this hook
  used?" — every lookalike qualifies. The candidate set is large and each member looks
  right, so the first hit wins on nothing but search order.
- **By place** — "what does the surface the user NAMED use?" — leaves exactly one file,
  and it admits no substitute.

When the user names a surface (a screen, a dialog, a view), search by place:

1. Resolve the UI name to a path — the area doc's pointer for that surface, or grep the
   user-visible string in the locale/copy files to reach the key, then its component.
2. **Say which path you resolved it to** (LAW4) before reading or searching anything else.
3. Read THAT file. Then work.

**A file that uses the pattern is not the file that owns it.** The one that mounts a
shared component is a consumer; the one that defines the family is the contract. Copying
the consumer reproduces its approximations, not the pattern — and the difference is
invisible to a type-check and to a behaviour test, so it only surfaces as the owner
saying "it's still not the same".

## When to activate `ast-grep`

The search depends on **syntactic structure**, not text:
- Async functions without error handling
- Calls to a function with specific parameters
- React components using a specific hook
- Code within a context (class method, conditional block)
- Absent patterns (e.g.: tests without cleanup)

## Invoking the binary

- The CLI is the npm package **`@ast-grep/cli`**, invoked as **`ast-grep`**. From Bash,
  run it by that name.
- `sg` still resolves, but from 0.45.0 it prints
  `WARNING: 'sg' is deprecated. Use 'ast-grep' instead.` Do not use it.
- **On Windows, from a Python script, `subprocess.run(["ast-grep", …])` fails** with
  `FileNotFoundError: [WinError 2]`. npm installs `ast-grep`, `ast-grep.cmd` and
  `ast-grep.ps1`, and `CreateProcess` does not resolve `PATHEXT` — it only tries the
  bare name and `.exe`, so the `.cmd` is invisible. Both of these work:
  `subprocess.run(["ast-grep.cmd", …])`, or `shell=True` with the command as a string.

Without this, a session that tries to follow the rule above hits `command not found`,
silently falls back to Grep, and the structural search never happens.

## Restriction

Never run Grep without scoping by directory (`path:`) or extension (`glob:`/`type:`).
