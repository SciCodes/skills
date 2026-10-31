# SciCodes skills

Agent skills for SciCodes member support.

## assess-scicodes-practices (experimental)

Helps research software registries and repositories assess adoption of published SciCodes best practices and produce an evidence-based report, an adoption checklist, and a structured JSON assessment (all member-review drafts). It is not a certification or ranking system, and it does not implement changes.

**Status: experimental.** Rubric `0.1.0-draft` contains 52 source-backed recommendations across nine practices, paraphrased from Garijo et al. (2022), *Nine best practices for research software registries and repositories*, PeerJ Computer Science 8:e1023. Each criterion has a PDF page/section anchor, an assessor interpretation, and applicability guidance. Four optional enhancements remain outside baseline counts. Criterion grouping and applicability remain assessment interpretations pending SciCodes review; this is not certification.

New assessments use the supplied tracking scorecard’s 0–4 scale plus N/A, with `undetermined` for missing evidence or unresolved criteria. The historical crosswalk verifies the headings and records comparison limits from the supplied ODS export.

### Invocation

A registry or repository URL is enough to begin, including a collection URL:

> Use the assess-scicodes-practices skill to assess <https://registry.example.org/codebases> against the SciCodes best practices.

The agent infers the resource name and scope, then follows relevant service-wide policy and documentation links. It assesses the repository service's practices; individual software records are only sampled evidence when needed. You can also supply a member name or clarify the scope.

Assumptions: the agent can browse public web pages (otherwise it assesses only evidence you supply and says current public evidence was not verified) and can write to a working directory (otherwise it returns the three outputs inline).

### Installation

The skill is the folder `skills/assess-scicodes-practices/` (a `SKILL.md` with `references/` and `assets/`). According to the GitHub Docs page "Adding agent skills for GitHub Copilot" (<https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills>, read 2026-10-31), Copilot project skills live in `.github/skills`, `.claude/skills`, or `.agents/skills` in a repository, and personal skills in `~/.copilot/skills` or `~/.agents/skills`; each skill is a lowercase-hyphenated subdirectory containing `SKILL.md`. Copy the folder to one of those locations. Per the same page, skills work with Copilot cloud agent, Copilot code review, GitHub Copilot CLI, the GitHub Copilot app, and agent mode in Visual Studio Code.

Canonical references (not yet read; the sites were unreachable from the authoring environment, so nothing here is derived from them): the Agent Skills specification at <https://agentskills.io/home>, its client guidance at <https://agentskills.io/client-implementation/adding-skills-support>, and the skills directory and CLI at <https://www.skills.sh/>. Pending verification against those pages: `npx skills add` / `npx skills update`, and the choice between project-specific and global installation. Prefer project-specific installation: a global skill can bias unrelated tasks toward this assessment's way of organizing information.

Not verified: installation for other agents, and any install commands. They are omitted deliberately. Compatibility above is documented, not tested; this skill has not been run end to end in any environment. The Agent Skills specification site could not be reached, so frontmatter is checked only against the GitHub Docs description (`name`, `description`, optional `license`).

### Development

```text
pip install -r requirements-dev.txt
make check      # lint + validate (default local and CI check)
make eval       # optional; needs a model (see scripts/eval.py), may incur cost
```

`make validate` checks skill frontmatter and reference paths, rubric and schema validity, fixture validation, and the score boundary tests. The fixture in `tests/fixtures/` is fictional and uses reserved domains.

`make eval` supplies the skill, rubric, method, schema, and fixed fictional evidence to a model wrapper over stdin. It checks JSON output only; it does not test live browsing or report and checklist generation. An end-to-end assessment with human review is still needed before claiming that URL-to-assessment behavior is validated.

## Sources and licensing

Original contributions are under the Apache License 2.0 (the existing `LICENSE`). The selected paper is CC-BY-4.0. The rubric attributes and paraphrases its recommendations; no paper PDF or member scorecard rows are bundled. Source materials retain their own licenses:

- SciCodes overview: <https://scicodes.net/best-practices-for-software-registries-and-repositories/>
- Selected published baseline: Garijo et al. (2022), <https://doi.org/10.7717/peerj-cs.1023> (user-supplied PDF read)
- Earlier concise guide: <https://arxiv.org/abs/2012.13117> (not read)
- 2023 self-assessment: <https://docs.google.com/spreadsheets/d/1Ud2qsplv_17AjXKox7azES-L7LTqzj5rXaSpEaFAIjw/edit?gid=0#gid=0>

The supplied `peerj-cs-08-1023.pdf` has been read and pinned by publication date, DOI, and SHA-256 in the rubric. Online successors and the overview have not been verified. A user-supplied `2023-9 Best Practices Self Assessment.ods` export has now been read; its provenance and historical comparison limits are recorded in `skills/assess-scicodes-practices/references/assessment-2023-crosswalk.md`. The live spreadsheet has not been verified against the export.
