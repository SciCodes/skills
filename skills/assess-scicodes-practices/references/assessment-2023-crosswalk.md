# Best Practices Tracking Scorecard crosswalk

Status: **verified against the supplied ODS export**. The title in `Sheet1.B1` is "Best Practices Tracking Scorecard". Read on 2026-10-30 from `2023-9 Best Practices Self Assessment.ods`, supplied by the user. SHA-256: `e367dccdbf30656799d48f15246b15428ca2b0e2a0f6a57363949e99ad43eee7`.

The previously referenced [Google spreadsheet](https://docs.google.com/spreadsheets/d/1Ud2qsplv_17AjXKox7azES-L7LTqzj5rXaSpEaFAIjw/edit?gid=0#gid=0) has not been verified live against this export. The export is the source for this crosswalk. Its internal-use statement is source context, not permission to publish member ratings. No member ratings or contact details are reproduced here, and the original workbook is not bundled with the skill.

## Practice mapping

The following are direct mappings of tracking headings and order from `Sheet1` row 3. Score columns alternate with evidence or note columns. This does not establish equivalence of historical assessment criteria with the source-backed criteria now defined in [rubric.yaml](rubric.yaml).

| Score column | Evidence/notes column | Heading (verbatim) | Practice |
|---|---|---|---|
| B | C | Provide a public scope statement | BP1 |
| D | E | Provide user guidance | BP2 |
| F | G | Provide guidance to software contributors | BP3 |
| H | I | Establish an authorship policy | BP4 |
| J | K | Share metadata schema | BP5 |
| L | M | Stipulate conditions of use | BP6 |
| N | O | State a privacy policy | BP7 |
| P | Q | Provide a retention policy | BP8 |
| R | S | Disclose your end-of-life policy | BP9 |

Column A identifies the resource. Metadata headings in T–X are `Completed_by`, `Date of completion`, `Comments`, `Average`, and `Sum`. Embedded cell annotations must be read separately from the displayed score; annotation paragraphs are not part of a numeric cell's value.

## Scale and interpretation

`Sheet1.B2` defines a 0–4 scale and N/A. The source descriptions and new-score decision rules have their single authoritative home in [rubric.yaml](rubric.yaml).

The source leaves interpretation of coverage to each registry's discretion and suggests comparing desirable guidance items with items met. The skill records its reproducible criterion-count interpretation separately in `scorecard_alignment`. That interpretation and applicability choices must be disclosed when comparing with historical scores; equal numbers alone do not prove equal implementation or assessment standards.

## Historical comparison rules

- Preserve the original displayed score as text, including fractions, N/A, and blanks. A blank is not zero. Entries outside the declared scale are retained with a discrepancy note, never silently clamped or rounded.
- The export contains fractional scores and an out-of-scale numeric entry. Do not infer an expanded scale from those observations or generate fractional new scores.
- Preserve the adjacent evidence text, cell annotations, completion-date text, and row comments. A historical score may coexist with a note that evidence was not found; do not resolve that disagreement by silently changing either field.
- The filename is not a timestamp for every observation. Completion dates extend into 2024, and some row comments identify third-party assessment in 2025. Distinguish the recorded completion date from subsequent annotations and unknown edit dates.
- `Average`, `Sum`, and summary rows are historical spreadsheet outputs, not authoritative practice judgments. Blank practice cells can coexist with a zero sum. Do not use aggregates to fill missing values, rank members, or produce new overall member scores.
- Link each historical observation to its sheet and cell addresses, plus this file's name and hash. In `historical_comparison.reference`, retain the raw label/value and source location; include date or annotation context in the report. Load the user-supplied workbook when actual member history is needed. If it is unavailable, request it rather than reconstructing rows from this crosswalk.
- Treat historical scores as historical assertions, not verified current implementation. Use the difference categories in [method.md](method.md), retaining unknown cause when the evidence does not distinguish resource change from changed interpretation or discovery.

For future labels or sources, classify mappings as **direct** (same subject and meaning), **approximate** (overlapping but different; explain), or **unsupported** (leave unmapped). Do not manufacture criterion-level mappings from these practice headings.
