---
description: Engineering principles for dependencies, build, and determinism — the generic-but-necessary directives that no other rule covers in full. Loads on dependency/build/infra files.
paths:
  - "package.json"
  - "package-lock.json"
  - "*.lock"
  - "*.config.*"
  - "Dockerfile*"
  - "docker-compose*"
  - "scripts/**"
  - "deploy/**"
  - "deploy*.sh"
  - ".github/workflows/**"
  - ".gitea/**"
  - ".gitlab-ci*"
  - "k8s/**"
  - "helm/**"
  - "*.tf"
  - "Procfile"
  - "fly.toml"
  - "*.nomad"
---

# Engineering — Dependencies, Build, Determinism

Cross-cutting directives that survive because they are NOT what a model does by
default. Kept out of CLAUDE.md (eager) and off `['**/*']` — they matter here, on
dependency/build/infra files. Testable, not exhortations.

## Dependencies

- Pin versions; no floating ranges for anything load-bearing.
- Justify each new library in one line (why it, why not the stdlib/existing dep).
- Before adding a dependency, check whether an existing one already does it.

## Determinism

- Prefer idempotent scripts and explicit configs over implicit/ambient state.
- Any non-deterministic behaviour (time, randomness, network order) is documented
  where it lives.

## Operational hygiene

- No fragile hacks, no undocumented config.
- Before updating a dependency or infra: identify breaking changes AND a rollback
  path first — never a blind bump.

## Stack-awareness

- Adapt to the real environment (the declared runtime, OS, container setup) before
  reaching for a new technology. New tech needs a reason the current stack can't meet.

## Fail-safe by default

- When a choice is ambiguous and the user isn't available, take the conservative
  option and flag it (this is the execution-time complement of LAW4 ASK-DON'T-GUESS).
