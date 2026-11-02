# Agent instructions

- Run `make check` before committing. Make targets create `.venv` and install
  development dependencies automatically; no activation is needed.
- Score logic lives only in
  `skills/assess-scicodes-practices/references/rubric.yaml` (`decision_rules`).
  Do not duplicate it in code, templates, or docs; `scripts/validate.py`
  interprets the rules.
- Never write quotations, anchors, criteria, or 2023 historical values that were
  not read from the primary source. Mark them unresolved or pending instead.
- Do not automatically run real member audits or publish findings. Fixtures must
  be fictional and use reserved domains (example.org, example.com).
- Prefer open technologies and dependencies with modest operational overhead.
- Keep rigor proportionate to risk. Avoid speculative abstractions and tests
  that merely mirror implementation.
- Flag changes to scientific assumptions or interpretation explicitly.
- Keep this file small: record project-specific constraints and recurring
  corrections. Link to authoritative documentation rather than duplicating it.

## Commit conventions

- Use Conventional Commits with imperative descriptions. Aim for subjects within
  72 characters, including type and scope; favor clarity over strict length.
- Use scopes only for established repository areas.
- For non-trivial changes, use concise lowercase `-` bullets in the body to
  explain rationale and operationally relevant details.
- Keep each bullet concrete and independently legible; omit the body when the
  subject explains the complete change.
- Prefer branch-wide issue references in the pull request description.
- Do not repeat the same issue footer across every commit in a branch.
- Add a lowercase commit footer only when standalone traceability matters, such
  as for a direct fix, backport, or independently cherry-picked change.
