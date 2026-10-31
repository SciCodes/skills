# SciCodes skills

Agent skills for SciCodes member support.

## assess-scicodes-practices (experimental)

Helps research software registries and repositories assess adoption of published SciCodes best practices and produce an evidence-based report, an adoption checklist, and a structured JSON assessment (all member-review drafts). It is not a certification or ranking system, and it does not implement changes.

**Status: experimental.** The rubric is an assessment interpretation pending SciCodes review. Its detailed criteria are currently an unresolved skeleton because the primary sources could not be accessed when the repository was initialized (see `skills/assess-scicodes-practices/references/rubric.yaml`). Until they are filled in with verified, anchored criteria, assessments report criteria as `unknown`, and no practice receives a definitive tier.

### Invocation

A registry or repository URL is enough to begin, including a collection URL:

> Use the assess-scicodes-practices skill to assess <https://registry.example.org/codebases> against the SciCodes best practices.

The agent infers the resource name and scope, then follows relevant service-wide policy and documentation links. It assesses the repository service's practices; individual software records are only sampled evidence when needed. You can also supply a member name or clarify the scope.

Assumptions: the agent can browse public web pages (otherwise it assesses only evidence you supply and says current public evidence was not verified) and can write to a working directory (otherwise it returns the three outputs inline).

### Installation

The skill is the folder `skills/assess-scicodes-practices/` (a `SKILL.md` with `references/` and `assets/`). According to the GitHub Docs page "Adding agent skills for GitHub Copilot" (<https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills>, read 2026-10-31), Copilot project skills live in `.github/skills`, `.claude/skills`, or `.agents/skills` in a repository, and personal skills in `~/.copilot/skills` or `~/.agents/skills`; each skill is a lowercase-hyphenated subdirectory containing `SKILL.md`. Copy the folder to one of those locations. Per the same page, skills work with Copilot cloud agent, Copilot code review, GitHub Copilot CLI, the GitHub Copilot app, and agent mode in Visual Studio Code.

Not verified: installation for other agents, and any install commands. They are omitted deliberately. Compatibility above is documented, not tested; this skill has not been run end to end in any environment. The Agent Skills specification site could not be reached, so frontmatter is checked only against the GitHub Docs description (`name`, `description`, optional `license`).

### Development

```text
pip install -r requirements-dev.txt
make check      # lint + validate (default local and CI check)
make eval       # optional; needs a model (see scripts/eval.py), may incur cost
```

`make validate` checks skill frontmatter and reference paths, rubric and schema validity, fixture validation, and the tier boundary tests. The fixture in `tests/fixtures/` is fictional and uses reserved domains.

`make eval` supplies the skill, rubric, method, schema, and fixed fictional evidence to a model wrapper over stdin. It checks JSON output only; it does not test live browsing or report and checklist generation. A completed source-backed rubric and an end-to-end assessment with human review are still needed before claiming that URL-to-assessment behavior is validated.

## Sources and licensing

Original contributions are under the Apache License 2.0 (the existing `LICENSE`). Source materials are referenced, not copied or relicensed:

- SciCodes overview: <https://scicodes.net/best-practices-for-software-registries-and-repositories/>
- Detailed guide: <https://arxiv.org/abs/2012.13117>
- 2023 self-assessment: <https://docs.google.com/spreadsheets/d/1Ud2qsplv_17AjXKox7azES-L7LTqzj5rXaSpEaFAIjw/edit?gid=0#gid=0>

None of these three were readable during initialization; see `references/rubric.yaml` and `references/assessment-2023-crosswalk.md`.
