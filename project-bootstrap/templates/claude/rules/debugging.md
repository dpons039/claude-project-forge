---
description: Activate systematic-debugging on any error or unexpected behavior
---

# Debugging — Mandatory Skill

**`systematic-debugging`** — invoke ALWAYS on:
- Any compilation error, test failure, or startup crash
- Unexpected API or frontend behavior
- Performance problems or slow queries
- Integration errors (rate limits, pagination, auth flows)

## The iron law

**DO NOT propose fixes without completing root cause investigation (Phase 1).**

If 3+ fixes have been attempted without success → stop and rethink the architecture, don't try another fix.

## On tool or script failures

Report to the user what failed and why before retrying or continuing.
Don't use `systematic-debugging` as an excuse to retry the same failed command.
