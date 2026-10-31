# Method

Evidence collection, verification, prioritization, output handling, and calibration. Criteria and score rules live only in [rubric.yaml](rubric.yaml).

## Resolve resource and scope

Start at the supplied URL and identify the registry or repository service from the page and its navigation. Infer the member name when omitted; if identity cannot be verified, use the hostname as a provisional name and record that limitation. Keep the supplied URL in `member.website` and describe the assessed service, scope, and identity uncertainty in `member.scope` and the report.

A collection or codebase-list URL is an entry point to assessing the service's practices. Follow relevant links to service-wide policies and documentation, including parent-site pages; count institutional policies only when their applicability to this service is clear. Individual software records may supply sampled evidence, but their software quality is not the assessment target. If several services share a site, assess the service identified by the entry URL and record ambiguity rather than combining unrelated policies.

## Bounded evidence search

Check, in roughly this order, and stop when the question is answered or the bound is reached:

1. Navigation, header, and footer links of the member website.
2. Policy, about, help, documentation, FAQ, and contact pages.
3. Metadata or schema documentation and any public API documentation.
4. Site search for each policy topic the rubric names.
5. Institutional policies that are linked from the member site, counted only where it is clear they apply to this resource.

Record material access limitations (login walls, robots exclusions, timeouts, blocked hosts) and each unsuccessful search. Do not crawl exhaustively. Sample records only when a specific question needs record-level evidence; document how they were selected and the limits, with no universal sample size.

## Using the published baseline

Read `criterion_policy` and each criterion's interpretation and applicability guidance in the rubric. The supplied 2022 paper is the pinned edition; page anchors refer to its printed PDF pagination. The paper is non-prescriptive: named resources and technologies illustrate approaches, rather than imposing specific tools, licenses, or preservation arrangements. Its policy-disclosure criteria generally assess what the resource states, not whether the promised behavior has been independently demonstrated. Keep that distinction in the report.

## Evidence distinctions

Label each evidence entry's `provenance` and keep these apart in findings:

- public statement versus verified implementation;
- internal evidence versus public disclosure;
- maintainer assertion versus independently observed behavior;
- repository code versus deployed behavior.

A statement alone supports "published", not "implemented", unless the criterion only asks for publication. Assess privacy and conditions of use against the published expectations, not legal adequacy.

## Unknown, not found, and exclusions

- Not found after bounded search: `unknown` with reason `not_found_after_search` and a member-confirmation request. It is not proof of noncompliance.
- Provisional exclusion: `unknown` with reason `applicability_unconfirmed`.
- `not_applicable` needs a documented basis and member confirmation recording who confirmed and when.
- Criteria whose `source_status` in the rubric is `unresolved` stay `unknown` with reason `baseline_unresolved`.

## Restricted evidence

Mark restricted evidence `visibility: restricted`. Prefer a restricted reference over copying sensitive excerpts. A finding supported only by restricted evidence sets `basis_publicly_verifiable: false`, and the report and checklist say so. Public export must sanitize every artifact, including the JSON. Default to member review before publication or aggregation.

## Verification

Before finalizing, recheck:

1. every negative (`unmet`), disputed, or consequential finding, prioritizing those that drive baseline-improvement actions or determine a practice result;
2. a reproducible sample of the other evidence: sort the remaining evidence IDs ascending and take every third entry starting with the first (at least one).

Record the evidence IDs and what was checked in `verification`. Same-agent checking is not independent review; set `same_agent: true` accordingly.

## Prioritization and actions

Order actions by member capacity, dependencies, and the smallest useful change. Separate the checklist into evidence requests, baseline improvements, and optional enhancements. Each task names the concrete change, affected practice, suggested responsible role, and an observable completion check. Prefer existing infrastructure and established community templates. Mark generated policy text unapproved and list decisions for the responsible owner. Estimate effort only when useful: state units and assumptions, and separate hands-on work from approval delays.

## Historical comparison

When differences from an earlier assessment appear, classify each as: documented resource change, newly discovered evidence, changed rubric or interpretation, access or method difference, or unknown cause. Use the mapping limits in [assessment-2023-crosswalk.md](assessment-2023-crosswalk.md).

## Outputs

Copy `rubric_version` from the loaded rubric. When `baseline.selected` names a source ID, use that ID and `baseline.version` in the assessment with status `pinned`. When no source is selected, use status `unresolved` and copy the rubric's baseline version; the assessment ID is only a descriptive placeholder. If the requested baseline differs, use `mismatch_deferred`, record the requested ID and version and an explanatory note, and leave findings unknown until the baseline is resolved.

Write `assessment.json`, `report.md`, and `checklist.md` to the user's output directory if given. Otherwise create `scicodes-assessments/<member-slug>-<YYYY-MM-DD>/` in the writable working area, outside the installed skill package. On collision append `-run2`, `-run3`, and so on; never overwrite silently. Report the resulting paths.

## Proposed calibration exercise (not yet conducted)

1. Choose one registry and one repository with differing resource functions, at least one represented in the 2023 assessment if feasible.
2. Audit each twice in fresh sessions.
3. Record model, skill version, rubric version, and material access differences.
4. Compare criterion decisions and supporting evidence.
5. Separate rubric ambiguity from evidence-discovery variance.
6. Use human adjudication to refine the relevant rubric or method text.
7. Record rubric changes separately from real member improvements.

Repository fixtures and automated tests use fictional resources only.
