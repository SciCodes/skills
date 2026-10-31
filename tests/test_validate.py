"""Tier boundary, coverage, and fixture tests. Run: python -m unittest discover tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import validate as v  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "fictional-assessment.json"
RUBRIC = v.load_rubric()
RULES = RUBRIC["decision_rules"]


def test_rubric(n):
    """Verified-source rubric: one practice (BP1) with n criteria."""
    crits = [
        {"id": f"BP1.{i}", "kind": "expectation", "source_status": "verified", "source_anchor": "test"}
        for i in range(1, n + 1)
    ]
    return {**RUBRIC, "practices": [{"id": "BP1", "title": "t", "criteria": crits}]}


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
        evidence=[a["evidence"][0]],
        findings=findings,
        actions=[],
        verification=[],
        practice_results=[{
            "practice_id": "BP1",
            "result": v.derive_result(counts, RULES),
            "counts": counts,
            "evidence_complete": counts["unknown"] == 0,
        }],
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


if __name__ == "__main__":
    unittest.main()
