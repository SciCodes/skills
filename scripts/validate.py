#!/usr/bin/env python3
"""Validate the skill package and SciCodes practice assessments.

Usage:
  python scripts/validate.py                    validate the repository
  python scripts/validate.py ASSESSMENT.json    validate one assessment

Checks structure and consistency only. Passing does not establish that the
underlying findings are correct. Tier decisions come from the ordered rules in
rubric.yaml; this module only interprets them.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "assess-scicodes-practices"
RUBRIC_PATH = SKILL / "references" / "rubric.yaml"
SCHEMA_PATH = SKILL / "assets" / "assessment.schema.json"
OUTCOMES = ("met", "unmet", "unknown", "not_applicable")
CONDITION_KEYS = {"exact", "min", "equals_total", "structure_valid", "otherwise"}


def load_rubric(path=RUBRIC_PATH):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_schema(path=SCHEMA_PATH):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check_rubric(rubric):
    """Return a list of rubric structure errors."""
    if not isinstance(rubric, dict):
        return ["rubric must be an object"]
    errors = []
    practices = rubric.get("practices")
    if not isinstance(practices, list) or not practices:
        return ["rubric practices must be a nonempty list"]
    seen, practice_ids = set(), []
    for practice in practices:
        if not isinstance(practice, dict):
            errors.append("practice must be an object")
            continue
        pid = practice.get("id")
        if not isinstance(pid, str) or not re.fullmatch(r"BP[1-9]", pid):
            errors.append(f"practice id {pid!r} does not match BP1-BP9")
            continue
        practice_ids.append(pid)
        criteria = practice.get("criteria")
        if not isinstance(criteria, list) or not criteria:
            errors.append(f"practice {pid} needs a nonempty criterion list")
            continue
        for crit in criteria:
            if not isinstance(crit, dict):
                errors.append(f"practice {pid}: criterion must be an object")
                continue
            cid = crit.get("id")
            if not isinstance(cid, str) or not re.fullmatch(re.escape(pid) + r"\.[0-9]+", cid):
                errors.append(f"criterion id {cid!r} does not belong to {pid}")
                continue
            if cid in seen:
                errors.append(f"duplicate criterion id {cid}")
            seen.add(cid)
            if crit.get("source_status") not in ("verified", "unresolved"):
                errors.append(f"criterion {cid} has invalid source_status")
            if crit.get("source_status") == "verified" and not crit.get("source_anchor"):
                errors.append(f"verified criterion {cid} needs a source_anchor")
    if len(practice_ids) != 9 or set(practice_ids) != {f"BP{i}" for i in range(1, 10)}:
        errors.append("practices must contain exactly BP1-BP9, each once")
    results = rubric.get("results")
    if not isinstance(results, dict) or not results:
        errors.append("rubric results must be a nonempty object")
        results = {}
    rules = rubric.get("decision_rules")
    if not isinstance(rules, list) or not rules:
        return errors + ["decision_rules must be a nonempty list"]
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            errors.append("decision rule must be an object")
            continue
        label = f"rule {rule.get('id')}"
        result = rule.get("result")
        if not isinstance(result, str) or result not in results:
            errors.append(f"{label} has unknown result")
        when = rule.get("when")
        if not isinstance(when, dict) or not when or set(when) - CONDITION_KEYS:
            errors.append(f"{label} needs nonempty supported conditions")
            continue
        if "otherwise" in when:
            if len(when) != 1 or when["otherwise"] is not True or index != len(rules) - 1:
                errors.append(f"{label}: otherwise must be standalone true on the final rule only")
        if index == len(rules) - 1 and (set(when) != {"otherwise"} or when.get("otherwise") is not True):
            errors.append("final decision rule must be standalone otherwise: true")
        if "structure_valid" in when and type(when["structure_valid"]) is not bool:
            errors.append(f"{label} has invalid structure_valid condition")
        for key in ("exact", "min"):
            if key not in when:
                continue
            condition = when[key]
            if not isinstance(condition, dict) or not condition:
                errors.append(f"{label} needs a nonempty {key} object")
                continue
            for outcome, n in condition.items():
                if outcome not in OUTCOMES or type(n) is not int or n < 0:
                    errors.append(f"{label} has invalid {key} condition")
        if "equals_total" in when:
            outcomes = when["equals_total"]
            if (not isinstance(outcomes, list) or not outcomes
                    or any(o not in OUTCOMES for o in outcomes)
                    or len(outcomes) != len(set(outcomes))):
                errors.append(f"{label} needs unique valid outcomes in equals_total")
    return errors


def _assessment_enum(schema, collection, field):
    """Read a vocabulary from the assessment schema's inline item properties."""
    node = schema
    for key in ("properties", collection, "items", "properties", field, "enum"):
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return node


def _vocabulary(values):
    if (not isinstance(values, list) or not values
            or any(not isinstance(value, str) for value in values)
            or len(values) != len(set(values))):
        return None
    return set(values)


def check_configuration(rubric, schema):
    """Validate configuration before any assessment or tier checks."""
    errors = [f"rubric: {e}" for e in check_rubric(rubric)]
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        errors.append(f"schema: {exc.message}")
    if errors:
        return errors
    vocabularies = (
        ("outcomes", rubric.get("outcomes"), _assessment_enum(schema, "findings", "outcome")),
        ("unknown_reasons", rubric.get("unknown_reasons"), _assessment_enum(schema, "findings", "reason")),
        ("results", list(rubric["results"]), _assessment_enum(schema, "practice_results", "result")),
    )
    for name, declared, allowed in vocabularies:
        if _vocabulary(declared) is None or _vocabulary(declared) != _vocabulary(allowed):
            errors.append(f"configuration: rubric {name} must match the schema enum")
    if _vocabulary(rubric.get("outcomes")) != set(OUTCOMES):
        errors.append("configuration: outcomes must match interpreter-supported outcomes")
    baseline = rubric.get("baseline")
    if (not isinstance(baseline, dict)
            or not isinstance(baseline.get("version"), str) or not baseline["version"]
            or "selected" not in baseline
            or (baseline["selected"] is not None and (
                not isinstance(baseline["selected"], str) or not baseline["selected"]))):
        errors.append("configuration: baseline needs a version and selected source ID or null")
    if not isinstance(rubric.get("rubric_version"), str) or not rubric["rubric_version"]:
        errors.append("configuration: rubric_version must be a nonempty string")
    return errors


def count_outcomes(outcomes):
    counts = Counter(outcomes)
    return {o: counts.get(o, 0) for o in OUTCOMES}


def derive_result(counts, rules, structure_valid=True):
    """Apply validated ordered rules to criterion counts; first match wins."""
    total = sum(counts.values())
    structure_valid = structure_valid and total > 0  # empty criterion set is invalid
    for rule in rules:
        when = rule["when"]
        if "otherwise" in when:
            if when["otherwise"] is True:
                return rule["result"]
            continue
        if not when:
            continue
        if "structure_valid" in when and when["structure_valid"] != structure_valid:
            continue
        if "exact" in when and any(counts[o] != n for o, n in when["exact"].items()):
            continue
        if "min" in when and any(counts[o] < n for o, n in when["min"].items()):
            continue
        if "equals_total" in when and sum(counts[o] for o in when["equals_total"]) != total:
            continue
        return rule["result"]
    return "invalid"


def _unique(items):
    seen, dupes = set(), set()
    for item in items:
        (dupes if item in seen else seen).add(item)
    return dupes


def validate_assessment(assessment, rubric, schema=None):
    """Return a list of errors; empty means structurally valid and consistent."""
    schema = load_schema() if schema is None else schema
    errors = check_configuration(rubric, schema)
    if errors:
        return errors
    errors = [
        f"schema: {'/'.join(map(str, e.absolute_path))}: {e.message}"
        for e in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(assessment)
    ]
    if errors:
        return errors

    crit_to_practice, crit_meta = {}, {}
    for practice in rubric["practices"]:
        for crit in practice["criteria"]:
            crit_to_practice[crit["id"]] = practice["id"]
            crit_meta[crit["id"]] = crit
    practice_ids = [p["id"] for p in rubric["practices"]]

    errors = _check_provenance(assessment, rubric)
    errors += _check_coverage(assessment, crit_to_practice, practice_ids)
    errors += _check_evidence(assessment, crit_meta)
    errors += _check_references(assessment, crit_to_practice, practice_ids)
    if errors:
        return errors
    return _check_results(assessment, rubric, crit_to_practice, practice_ids)


def _check_provenance(assessment, rubric):
    errors = []
    if assessment["rubric_version"] != rubric["rubric_version"]:
        errors.append("rubric_version does not match the loaded rubric")
    baseline = assessment["baseline"]
    selected = rubric["baseline"]["selected"]
    if baseline["status"] == "mismatch_deferred":
        if not baseline.get("note", "").strip():
            errors.append("baseline mismatch_deferred requires a note explaining the mismatch")
        if any(f["outcome"] != "unknown" for f in assessment["findings"]):
            errors.append("baseline mismatch_deferred requires unknown findings")
    else:
        expected_status = "unresolved" if selected is None else "pinned"
        if baseline["status"] != expected_status:
            errors.append(f"baseline status must be {expected_status} for the loaded rubric")
        if selected is not None and baseline["id"] != selected:
            errors.append("baseline id does not match the loaded rubric")
        if baseline["version"] != rubric["baseline"]["version"]:
            errors.append("baseline version does not match the loaded rubric")
    return errors


def _check_coverage(assessment, crit_to_practice, practice_ids):
    errors = []
    findings = assessment["findings"]
    ids = [f["criterion_id"] for f in findings]
    for cid in sorted(_unique(ids)):
        errors.append(f"duplicate criterion {cid}")
    for cid in sorted(set(ids) - set(crit_to_practice)):
        errors.append(f"unrecognized criterion {cid}")
    for cid in sorted(set(crit_to_practice) - set(ids)):
        errors.append(f"missing criterion {cid}")
    if not findings:
        errors.append("empty criterion set")

    reported = [r["practice_id"] for r in assessment["practice_results"]]
    for pid in sorted(_unique(reported)):
        errors.append(f"duplicate practice result {pid}")
    for pid in sorted(set(reported) - set(practice_ids)):
        errors.append(f"unrecognized practice result {pid}")
    for pid in sorted(set(practice_ids) - set(reported)):
        errors.append(f"missing practice result {pid}")

    return errors


def _check_evidence(assessment, crit_meta):
    errors = []
    findings = assessment["findings"]
    evidence = {e["id"]: e for e in assessment["evidence"]}
    if len(evidence) != len(assessment["evidence"]):
        errors.append("duplicate evidence id")
    for f in findings:
        cid = f["criterion_id"]
        refs = f.get("evidence_ids", [])
        for ref in refs:
            if ref not in evidence:
                errors.append(f"{cid}: unknown evidence {ref}")
        if f["outcome"] == "unknown" and f.get("reason") in (
            "not_found_after_search", "applicability_unconfirmed"
        ) and not f.get("member_confirmation_requested"):
            errors.append(f"{cid}: {f['reason']} requires member_confirmation_requested")
        if cid in crit_meta and crit_meta[cid]["source_status"] == "unresolved" and (
            f["outcome"] != "unknown" or f.get("reason") != "baseline_unresolved"
        ):
            errors.append(f"{cid}: unresolved criterion must be unknown/baseline_unresolved")
        known = [evidence[r] for r in refs if r in evidence]
        if known and all(e["visibility"] == "restricted" for e in known) and (
            f.get("basis_publicly_verifiable") is not False
        ):
            errors.append(f"{cid}: restricted-only basis must set basis_publicly_verifiable false")
    if assessment["review"]["public_export_sanitized"]:
        for e in evidence.values():
            if e["visibility"] == "restricted" and "excerpt" in e:
                errors.append(f"{e['id']}: restricted excerpt present in sanitized export")

    return errors


def _check_references(assessment, crit_to_practice, practice_ids):
    errors = []
    evidence = {e["id"] for e in assessment["evidence"]}
    action_ids = [a["id"] for a in assessment["actions"]]
    for aid in sorted(_unique(action_ids)):
        errors.append(f"duplicate action {aid}")
    for a in assessment["actions"]:
        if a["practice_id"] not in practice_ids:
            errors.append(f"{a['id']}: unknown practice {a['practice_id']}")
        for cid in a.get("criterion_ids", []):
            if crit_to_practice.get(cid) != a["practice_id"]:
                errors.append(f"{a['id']}: criterion {cid} not in {a['practice_id']}")
    for v in assessment["verification"]:
        for ref in v["evidence_ids"]:
            if ref not in evidence:
                errors.append(f"verification: unknown evidence {ref}")

    return errors


def _check_results(assessment, rubric, crit_to_practice, practice_ids):
    errors = []
    findings = assessment["findings"]
    by_practice = {pid: [] for pid in practice_ids}
    for f in findings:
        by_practice[crit_to_practice[f["criterion_id"]]].append(f["outcome"])
    for r in assessment["practice_results"]:
        counts = count_outcomes(by_practice[r["practice_id"]])
        result = derive_result(counts, rubric["decision_rules"])
        if r["counts"] != counts:
            errors.append(f"{r['practice_id']}: reported counts {r['counts']} != derived {counts}")
        if r["result"] != result:
            errors.append(f"{r['practice_id']}: reported {r['result']} != derived {result}")
        if r["evidence_complete"] != (counts["unknown"] == 0):
            errors.append(f"{r['practice_id']}: evidence_complete is inconsistent")
    return errors


def check_skill():
    errors = []
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        return ["SKILL.md: missing frontmatter"]
    meta = yaml.safe_load(match.group(1))
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(meta.get("name", ""))):
        errors.append("SKILL.md: name must be lowercase with hyphens")
    if meta.get("name") != SKILL.name:
        errors.append("SKILL.md: name must match the directory name")
    if not str(meta.get("description", "")).strip():
        errors.append("SKILL.md: description is required")
    for link in re.findall(r"\]\(([^)#]+)\)", text):
        if not link.startswith(("http://", "https://")) and not (SKILL / link).exists():
            errors.append(f"SKILL.md: broken reference {link}")
    for name in ("rubric.yaml", "method.md", "assessment-2023-crosswalk.md"):
        if f"references/{name}" not in text:
            errors.append(f"SKILL.md: does not link references/{name}")
    for name in ("report.md", "checklist.md", "assessment.schema.json"):
        if f"assets/{name}" not in text:
            errors.append(f"SKILL.md: does not link assets/{name}")
    return errors


def check_repository():
    errors = check_skill()
    rubric = load_rubric()
    schema = load_schema()
    configuration_errors = check_configuration(rubric, schema)
    if configuration_errors:
        return errors + configuration_errors
    fixtures = sorted((ROOT / "tests" / "fixtures").glob("*assessment*.json"))
    if not fixtures:
        errors.append("no assessment fixtures found")
    for path in fixtures:
        with open(path, encoding="utf-8") as fh:
            errors += [f"{path.name}: {e}" for e in validate_assessment(json.load(fh), rubric, schema)]
    return errors


def main(argv):
    if len(argv) > 1:
        with open(argv[1], encoding="utf-8") as fh:
            errors = validate_assessment(json.load(fh), load_rubric())
    else:
        errors = check_repository()
    for e in errors:
        print(f"ERROR: {e}")
    print("FAILED" if errors else "OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
