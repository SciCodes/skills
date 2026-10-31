"""Tier boundary, coverage, and fixture tests. Run: python -m unittest discover tests"""
import contextlib
import copy
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import validate as v  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "fictional-assessment.json"
RUBRIC = v.load_rubric()
RULES = RUBRIC["decision_rules"]


def test_rubric(n):
    """Full rubric with n fictional verified criteria for BP1."""
    crits = [
        {"id": f"BP1.{i}", "kind": "expectation", "source_status": "verified", "source_anchor": "test"}
        for i in range(1, n + 1)
    ]
    rubric = copy.deepcopy(RUBRIC)
    next(p for p in rubric["practices"] if p["id"] == "BP1")["criteria"] = crits
    return rubric


def make(outcomes):
    """Fictional assessment for BP1 with the given outcomes and correct derived values."""
    rubric = test_rubric(len(outcomes))
    findings = []
    for i, o in enumerate(outcomes, 1):
        f = {"criterion_id": f"BP1.{i}", "outcome": o}
        if o in ("met", "unmet"):
            f["evidence_ids"] = ["E1"]
        elif o == "unknown":
            f.update(reason="evidence_inaccessible")
        else:
            f["exclusion"] = {"basis": "fictional", "confirmed_by": "Fictional Person", "confirmed_at": "2026-01-01"}
        findings.append(f)
    counts = v.count_outcomes(outcomes)
    a = copy.deepcopy(json.loads(FIXTURE.read_text()))
    a.update(
        findings=findings + [f for f in a["findings"] if not f["criterion_id"].startswith("BP1.")],
        actions=[],
        verification=[],
        practice_results=[{
            "practice_id": "BP1",
            "result": v.derive_result(counts, RULES),
            "counts": counts,
            "evidence_complete": counts["unknown"] == 0,
        }] + [r for r in a["practice_results"] if r["practice_id"] != "BP1"],
    )
    return a, rubric


class TierBoundaries(unittest.TestCase):
    CASES = [
        (["met", "met", "unmet", "unknown"], "tier_1", False),
        (["met", "met", "unknown"], "undetermined", False),
        (["unmet", "unmet", "unknown"], "undetermined", False),
        (["not_applicable", "met", "met"], "tier_2", True),
        (["unmet", "unmet", "unmet"], "tier_0", True),
        (["not_applicable", "not_applicable"], "not_applicable", True),
        (["unknown", "met", "met"], "undetermined", False),  # unconfirmed applicability blocks Tier 2
        (["unknown", "unmet", "unmet"], "undetermined", False),  # ... and Tier 0
        (["met", "unmet"], "tier_1", True),
    ]

    def test_derivation_and_validation(self):
        for outcomes, expected, complete in self.CASES:
            with self.subTest(outcomes=outcomes):
                a, rubric = make(outcomes)
                self.assertEqual(a["practice_results"][0]["result"], expected)
                self.assertEqual(a["practice_results"][0]["evidence_complete"], complete)
                self.assertEqual(v.validate_assessment(a, rubric), [])

    def test_no_matching_rule_is_invalid(self):
        self.assertEqual(v.derive_result(v.count_outcomes([]), RULES), "invalid")
        self.assertEqual(v.derive_result(v.count_outcomes(["met"]), RULES, structure_valid=False), "invalid")

    def test_wrong_results_are_rejected(self):
        a, rubric = make(["met", "unmet"])
        a["practice_results"][0]["result"] = "tier_2"
        self.assertTrue(any("derived tier_1" in e for e in v.validate_assessment(a, rubric)))
        a, rubric = make(["met", "unmet", "unknown"])
        a["practice_results"][0]["counts"]["unknown"] = 0
        self.assertTrue(any("reported counts" in e for e in v.validate_assessment(a, rubric)))
        a, rubric = make(["met", "unknown"])
        a["practice_results"][0]["evidence_complete"] = True
        self.assertTrue(any("evidence_complete" in e for e in v.validate_assessment(a, rubric)))


class Coverage(unittest.TestCase):
    def check(self, mutate, expected):
        a, rubric = make(["met", "unmet"])
        mutate(a)
        errors = v.validate_assessment(a, rubric)
        self.assertTrue(any(expected in e for e in errors), errors)

    def test_missing(self):
        self.check(lambda a: a["findings"].pop(), "missing criterion")

    def test_duplicate(self):
        self.check(lambda a: a["findings"].append(copy.deepcopy(a["findings"][0])), "duplicate criterion")

    def test_unrecognized(self):
        self.check(lambda a: a["findings"][0].update(criterion_id="BP1.99"), "unrecognized criterion")

    def test_empty(self):
        self.check(lambda a: a.update(findings=[]), "empty criterion set")

    def test_unrecognized_outcome(self):
        self.check(lambda a: a["findings"][0].update(outcome="partial"), "schema")

    def test_definitive_findings_require_evidence(self):
        for outcome in ("met", "unmet"):
            with self.subTest(outcome=outcome):
                a, rubric = make([outcome])
                a["findings"][0]["evidence_ids"] = []
                a["evidence"] = []
                self.assertTrue(any("evidence_ids" in e for e in v.validate_assessment(a, rubric)))

    def test_not_found_needs_member_confirmation(self):
        a, rubric = make(["met", "unknown"])
        a["findings"][1]["reason"] = "not_found_after_search"
        self.assertTrue(any("member_confirmation" in e for e in v.validate_assessment(a, rubric)))
        a["findings"][1]["member_confirmation_requested"] = True
        self.assertEqual(v.validate_assessment(a, rubric), [])

    def test_restricted_only_basis_flagged(self):
        a, rubric = make(["met", "unmet"])
        a["evidence"][0]["visibility"] = "restricted"
        self.assertTrue(any("restricted-only" in e for e in v.validate_assessment(a, rubric)))

    def test_exclusion_requires_confirmation(self):
        a, rubric = make(["met", "not_applicable"])
        del a["findings"][1]["exclusion"]
        self.assertTrue(any("schema" in e for e in v.validate_assessment(a, rubric)))

    def test_action_links(self):
        a, rubric = make(["met", "unmet"])
        a["actions"] = [{"id": "A1", "type": "baseline_improvement", "practice_id": "BP1",
                         "criterion_ids": ["BP9.1"], "change": "x", "responsible_role": "x",
                         "completion_check": "x"}]
        self.assertTrue(any("not in BP1" in e for e in v.validate_assessment(a, rubric)))


class Repository(unittest.TestCase):
    def test_repository_checks_pass(self):
        self.assertEqual(v.check_repository(), [])

    def test_real_rubric_unresolved_criteria_cannot_be_met(self):
        a = json.loads(FIXTURE.read_text())
        a["findings"][0].update(outcome="met", evidence_ids=["E1"])
        a["findings"][0].pop("reason")
        self.assertTrue(any("unresolved criterion" in e for e in v.validate_assessment(a, RUBRIC)))


class Configuration(unittest.TestCase):
    def test_vocabularies_must_agree(self):
        for name, collection, field in (("outcomes", "findings", "outcome"),
                                        ("unknown_reasons", "findings", "reason"),
                                        ("results", "practice_results", "result")):
            rubric = copy.deepcopy(RUBRIC)
            schema = v.load_schema()
            allowed = schema["properties"][collection]["items"]["properties"][field]["enum"]
            allowed.append("extra_value")
            with self.subTest(name=name):
                self.assertTrue(any(name in e for e in v.check_configuration(rubric, schema)))

    def test_unrecognized_interpreter_outcome_is_rejected_even_if_schema_agrees(self):
        rubric = copy.deepcopy(RUBRIC)
        schema = v.load_schema()
        rubric["outcomes"].append("partial")
        schema["properties"]["findings"]["items"]["properties"]["outcome"]["enum"].append("partial")
        self.assertTrue(any("interpreter" in e for e in v.check_configuration(rubric, schema)))

    def test_new_rule_result_must_be_supported_by_schema(self):
        rubric = copy.deepcopy(RUBRIC)
        rubric["results"]["new_result"] = "Fictional result"
        rubric["decision_rules"][2]["result"] = "new_result"
        self.assertTrue(any("results" in e for e in v.check_configuration(rubric, v.load_schema())))

    def test_missing_or_malformed_vocabulary_is_rejected(self):
        for value in (None, [], ["met", "met"], [{}]):
            rubric = copy.deepcopy(RUBRIC)
            rubric["outcomes"] = value
            with self.subTest(value=value):
                self.assertTrue(v.check_configuration(rubric, v.load_schema()))
        self.assertTrue(v.check_configuration(RUBRIC, True))

    def test_fixture_builder_is_independent_of_order(self):
        fixture = json.loads(FIXTURE.read_text())
        rubric = copy.deepcopy(RUBRIC)
        rubric["practices"].reverse()
        fixture["findings"].reverse()
        fixture["practice_results"].reverse()
        with patch.dict(RUBRIC, rubric), patch.object(Path, "read_text", return_value=json.dumps(fixture)):
            assessment, modified_rubric = make(["met", "unmet"])
        self.assertEqual(v.validate_assessment(assessment, modified_rubric), [])

    def test_malformed_rubric_shapes(self):
        cases = [None, [], "rubric"]
        for key in ("practices", "decision_rules", "results"):
            for value in (None, [], "bad", 1):
                cases.append({**RUBRIC, key: value})
        cases += [
            {**RUBRIC, "practices": [None]},
            {**RUBRIC, "practices": [{"id": []}]},
            {**RUBRIC, "decision_rules": [None]},
        ]
        for rubric in cases:
            with self.subTest(rubric=rubric):
                self.assertTrue(v.check_rubric(rubric))

    def test_exact_practice_coverage(self):
        for mode in ("missing", "duplicate"):
            rubric = copy.deepcopy(RUBRIC)
            if mode == "missing":
                rubric["practices"].pop()
            else:
                duplicate = copy.deepcopy(rubric["practices"][0])
                duplicate["criteria"][0]["id"] = "BP1.99"
                rubric["practices"].append(duplicate)
            with self.subTest(mode=mode):
                self.assertTrue(any("exactly BP1-BP9" in e for e in v.check_rubric(rubric)))

    def test_invalid_conditions(self):
        conditions = [
            None, [], {}, {"unsupported": True},
            {"otherwise": False}, {"otherwise": True}, {"otherwise": 1},
            {"otherwise": True, "min": {"met": 1}},
            {"structure_valid": 0}, {"structure_valid": "false"},
        ]
        for key in ("exact", "min"):
            conditions += [{key: value} for value in (None, [], {}, 1, {"met": True},
                                                      {"met": -1}, {"met": 1.5}, {"other": 1})]
        conditions += [{"equals_total": value} for value in
                       (None, "met", {}, [], ["met", "met"], ["other"], [[]])]
        for condition in conditions:
            rubric = copy.deepcopy(RUBRIC)
            rubric["decision_rules"][1]["when"] = condition
            with self.subTest(condition=condition):
                self.assertTrue(v.check_rubric(rubric))

    def test_final_fallback_is_required(self):
        for condition in ({}, {"otherwise": False}, {"otherwise": 1},
                          {"min": {"met": 1}}, {"otherwise": True, "exact": {"met": 0}}):
            rubric = copy.deepcopy(RUBRIC)
            rubric["decision_rules"][-1]["when"] = condition
            with self.subTest(condition=condition):
                self.assertTrue(v.check_rubric(rubric))

    def test_final_fallback_is_executed(self):
        rubric = copy.deepcopy(RUBRIC)
        rubric["decision_rules"] = [
            {"id": "match", "result": "tier_2", "when": {"min": {"met": 2}}},
            {"id": "fallback", "result": "undetermined", "when": {"otherwise": True}},
        ]
        self.assertEqual(v.check_rubric(rubric), [])
        self.assertEqual(v.derive_result(v.count_outcomes(["met"]), rubric["decision_rules"]), "undetermined")

    def test_invalid_configuration_stops_both_cli_modes(self):
        bad_rubric = copy.deepcopy(RUBRIC)
        bad_rubric["decision_rules"][0]["when"] = {"min": []}
        for rubric, schema in ((bad_rubric, v.load_schema()), (RUBRIC, {"type": 123})):
            for argv in (["validate.py"], ["validate.py", str(FIXTURE)]):
                with self.subTest(argv=argv, schema=schema), \
                        patch.object(v, "load_rubric", return_value=rubric), \
                        patch.object(v, "load_schema", return_value=schema), \
                        patch.object(v, "derive_result", side_effect=AssertionError("must not derive")), \
                        contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(v.main(argv), 1)
                    self.assertIn("FAILED", output.getvalue())

    def test_repository_stops_before_assessment_on_invalid_rubric(self):
        with patch.object(v, "load_rubric", return_value={}), \
                patch.object(v, "validate_assessment", side_effect=AssertionError("must not validate")):
            self.assertTrue(v.check_repository())

    def test_date_formats(self):
        for field in ("audit_date", "accessed"):
            assessment = json.loads(FIXTURE.read_text())
            target = assessment if field == "audit_date" else assessment["evidence"][0]
            target[field] = "2026-02-30"
            with self.subTest(field=field):
                self.assertTrue(any(field in e for e in v.validate_assessment(assessment, RUBRIC)))


class Provenance(unittest.TestCase):
    def test_unrelated_rubric_version_is_rejected(self):
        assessment = json.loads(FIXTURE.read_text())
        assessment["rubric_version"] = "unrelated"
        self.assertTrue(any("rubric_version" in e for e in v.validate_assessment(assessment, RUBRIC)))

    def test_unresolved_baseline_cannot_claim_a_pin_or_another_version(self):
        for change in ({"status": "pinned"}, {"version": "999"}):
            assessment = json.loads(FIXTURE.read_text())
            assessment["baseline"].update(change)
            with self.subTest(change=change):
                self.assertTrue(any("baseline" in e for e in v.validate_assessment(assessment, RUBRIC)))

    def test_pinned_baseline_identity_and_version_must_match(self):
        rubric = copy.deepcopy(RUBRIC)
        rubric["baseline"].update(selected="fictional-guide", version="fictional-v1")
        assessment = json.loads(FIXTURE.read_text())
        assessment["baseline"].update(id="fictional-guide", version="fictional-v1", status="pinned")
        self.assertEqual(v.validate_assessment(assessment, rubric), [])
        for change in ({"id": "other-guide"}, {"version": "v2"}, {"status": "unresolved"}):
            changed = copy.deepcopy(assessment)
            changed["baseline"].update(change)
            with self.subTest(change=change):
                self.assertTrue(any("baseline" in e for e in v.validate_assessment(changed, rubric)))

    def test_mismatch_requires_note_and_deferred_findings(self):
        assessment = json.loads(FIXTURE.read_text())
        assessment["baseline"].update(status="mismatch_deferred", id="requested-guide", version="v2")
        self.assertTrue(any("note" in e for e in v.validate_assessment(assessment, RUBRIC)))
        assessment["baseline"]["note"] = "Requested fictional guide differs from the installed baseline."
        self.assertEqual(v.validate_assessment(assessment, RUBRIC), [])
        assessment, rubric = make(["met"])
        assessment["baseline"].update(status="mismatch_deferred", note="Different guide requested.")
        self.assertTrue(any("requires unknown findings" in e for e in v.validate_assessment(assessment, rubric)))


if __name__ == "__main__":
    unittest.main()
