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

[OMF Skill installation instructions](https://github.com/openmodelingfoundation/skills/blob/main/docs/install.md).

#### npx

```bash
npx skills add SciCodes/skills --list
npx skills add SciCodes/skills
```

#### gh cli

```bash
gh skill install SciCodes/skills --all
```

**Recommended: project-specific installation.** Copy the folder into a project's `.agents/skills/` and avoid global installation. Global skills are visible in every project and might steer unrelated tasks toward this assessment's way of organizing information. For multiple assessments, create a dedicated shell project that manages a locally versioned skill installation and tracks results and feedback.

### Development

```text
make setup      # create .venv and install development dependencies
make lint       # apply safe Python and Markdown fixes, format Python, then check
make lint-check # check lint and formatting without modifying files
make check      # lint-check + validate (default local and CI check)
make eval       # optional; needs a model (see scripts/eval.py), may incur cost
```

Make targets use `.venv` directly and run setup automatically when needed; activation is unnecessary. Python 3 with `venv` support is required. Set `PYTHON` to choose the interpreter or `VENV` to choose a different environment directory.

`make lint` applies the fixes supported by Ruff and PyMarkdown, then reports remaining issues. YAML linting and issues without an automatic fix require manual edits.

`make validate` checks skill frontmatter and reference paths, rubric and schema validity, fixture validation, and the score boundary tests. The fixture in `tests/fixtures/` is fictional and uses reserved domains.

`make eval` supplies the skill, rubric, method, schema, and fixed fictional evidence to a model wrapper over stdin. It checks JSON output only; it does not test live browsing or report and checklist generation. An end-to-end assessment with human review is still needed before claiming that URL-to-assessment behavior is validated.

## Sources and licensing

Original contributions are under the Apache License 2.0 (the existing `LICENSE`). The selected paper is CC-BY-4.0. The rubric attributes and paraphrases its recommendations; no paper PDF or member scorecard rows are bundled. Source materials retain their own licenses:

- SciCodes overview: <https://scicodes.net/best-practices-for-software-registries-and-repositories/>
- Selected published baseline: Garijo et al. (2022), <https://doi.org/10.7717/peerj-cs.1023>
- 2023 self-assessment: <https://docs.google.com/spreadsheets/d/1Ud2qsplv_17AjXKox7azES-L7LTqzj5rXaSpEaFAIjw/edit?gid=0#gid=0>

The supplied `peerj-cs-08-1023.pdf` has been read and pinned by publication date, DOI, and SHA-256 in the rubric.

A user-supplied `2023-9 Best Practices Self Assessment.ods` export has been read; its provenance and historical comparison limits are recorded in `skills/assess-scicodes-practices/references/assessment-2023-crosswalk.md`.
