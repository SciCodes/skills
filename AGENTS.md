# Agent instructions

- Run `make check` before committing. Make targets create `.venv` and install development dependencies automatically; no activation is needed.
- Score logic lives only in `skills/assess-scicodes-practices/references/rubric.yaml` (`decision_rules`). Do not duplicate it in code, templates, or docs; `scripts/validate.py` interprets the rules.
- Never write quotations, anchors, criteria, or 2023 historical values that were not read from the primary source. Mark them unresolved or pending instead.
- Do not run real member audits or publish findings. Fixtures must be fictional and use reserved domains (example.org, example.com).

## Commits

- Use Conventional Commits: `type(scope): subject`, with an optional scope.
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `build`, `ci`.
- Use imperative mood and keep the subject line at most 72 characters. The body explains why the change is needed.
- Mark breaking changes with `!` after the type or scope and a `BREAKING CHANGE:` footer.
