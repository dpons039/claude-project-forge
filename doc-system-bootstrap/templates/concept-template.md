# Concept: {title}

> Date: {YYYY-MM-DD}
> Status: idea
> Author: {name}

<!-- A concept captures WHAT and WHY for a future phase. It does NOT hold verified
     premises, because those go stale — a proposal fixes file:line against the code
     as it is now, so writing one far ahead is the mistake. When this phase's turn
     comes, PROMOTE this in place: copy _template/proposal.md → proposal.md, port
     Context + Objective below, then fill the TBD sections by verifying against the
     code now (approval gate). Never implement from a concept. See .claude/rules/sdd.md. -->

## Context

<!-- Why this change will be needed. The problem it addresses. This persists (it does not depend on the code state). -->

## Objective

<!-- What it achieves. Rough "done" criteria. This persists (it does not depend on the code state). -->

## Rough scope

<!-- Approximate areas/surfaces touched. Not file:line — that is verified at promotion. -->

## Dependencies / order

<!-- What must exist first; where this sits in roadmap.md phase order. -->

---

## TBD until promoted

<!-- These are filled ONLY when promoting to proposal.md, verifying against the code now: -->
<!-- - Technical Design (approach, trade-offs, file:line premises) -->
<!-- - Tasks (the checklist) -->
<!-- - Affected Docs -->
