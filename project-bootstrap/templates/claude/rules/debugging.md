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

## The iron law — count your attempts out loud

**DO NOT propose fixes without completing root cause investigation (Phase 1).**

The failure mode is silent repeat-patching: each hand-fix feels like the first, so a
"3+ attempts" threshold never trips because nothing counts. Make the count observable:

- Before ANY fix on a symptom you've already patched once, **state "attempt N on
  `<symptom>`" out loud** in your reply.
- Name the symptom by its **effect, not your hypothesis** — "header won't stay sticky",
  not "z-index is wrong". Re-labelling the hypothesis ("this is a *different* fix") does
  NOT reset the count; the effect is unchanged, so N keeps climbing.
- At **N ≥ 2 without a completed Phase-1 root-cause pass → STOP.** No further patch.
  Invoke `systematic-debugging`. A user naming the next tweak is not a reset either —
  their instruction plus your count collide as two facts; surface the conflict, don't
  quietly patch (this is LAW10).

The `attempt-counter` hook backs this externally: it warns after several edits with no
verify-run between, even if you skip the ritual. The hook is the net; the ritual is the
discipline.

## On tool or script failures

Report to the user what failed and why before retrying or continuing.
Don't use `systematic-debugging` as an excuse to retry the same failed command.
