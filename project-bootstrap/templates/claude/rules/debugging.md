---
description: Activate systematic-debugging on any error or unexpected behavior
---

# Debugging — when to run the protocol

**`systematic-debugging`** — invoke when **any** of these holds:
- the failure is not obvious at a glance, **or**
- a first fix attempt already failed, **or**
- it spans more than one subsystem (integration: rate limits, pagination, auth flows).

A typo, a missing import, a visible off-by-one → fix it directly and move on; the
protocol would cost more than the bug. Reach for it the moment the cause isn't
plain, or the first fix bounced.

Applies to: compilation errors, test failures, startup crashes, unexpected
API/frontend behavior, slow queries — whenever they clear the bar above.

## The iron law

**DO NOT propose fixes without completing root cause investigation (Phase 1).**

If 3+ fixes have been attempted without success → stop and rethink the architecture, don't try another fix.

## On tool or script failures

Report to the user what failed and why before retrying or continuing.
Don't use `systematic-debugging` as an excuse to retry the same failed command.
