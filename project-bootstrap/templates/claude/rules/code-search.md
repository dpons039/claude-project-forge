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

## When to activate `ast-grep`

The search depends on **syntactic structure**, not text:
- Async functions without error handling
- Calls to a function with specific parameters
- React components using a specific hook
- Code within a context (class method, conditional block)
- Absent patterns (e.g.: tests without cleanup)

## Restriction

Never run Grep without scoping by directory (`path:`) or extension (`glob:`/`type:`).
