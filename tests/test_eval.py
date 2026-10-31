"""Exercise the stdin-only evaluation interface without invoking a model."""

import contextlib
import importlib.util
import io
import json
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "skill_eval", ROOT / "scripts" / "eval.py"
)
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)


class Evaluation(unittest.TestCase):
    def run_wrapper(self, output):
        captured = {}

        def wrapper(command, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(returncode=0, stdout=json.dumps(output), stderr="")

        with (
            patch.dict(os.environ, {"SCICODES_EVAL_CMD": "fictional-model-wrapper"}),
            patch.object(evaluation.subprocess, "run", side_effect=wrapper),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            result = evaluation.main()
        return result, captured["input"]

    def test_stdin_wrapper_receives_required_method(self):
        fixture = json.loads(
            (ROOT / "tests/fixtures/fictional-assessment.json").read_text()
        )
        result, prompt = self.run_wrapper(fixture)
        self.assertEqual(result, 0)
        method = (evaluation.v.SKILL / "references/method.md").read_text()
        self.assertIn(method, prompt)

    def test_restricted_canary_is_rejected(self):
        fixture = json.loads(
            (ROOT / "tests/fixtures/fictional-assessment.json").read_text()
        )
        fixture["findings"][0]["note"] = evaluation.CANARY
        result, _ = self.run_wrapper(fixture)
        self.assertEqual(result, 1)

    def test_malformed_assessments_fail_without_crashing(self):
        for output in (
            [],
            None,
            {"practice_results": [{}]},
            {"practice_results": None},
        ):
            with self.subTest(output=output):
                result, _ = self.run_wrapper(output)
                self.assertEqual(result, 1)

    def test_verified_criterion_can_receive_a_definitive_result(self):
        fixture = json.loads(
            (ROOT / "tests/fixtures/fictional-assessment.json").read_text()
        )
        rubric = evaluation.v.load_rubric()
        rubric["baseline"].update(selected="fictional-guide", version="fictional-v1")
        fixture["baseline"].update(
            id="fictional-guide", version="fictional-v1", status="pinned"
        )
        criteria = next(p for p in rubric["practices"] if p["id"] == "BP1")["criteria"]
        for criterion in criteria:
            criterion.update(
                source_status="verified",
                source_anchor="https://example.org/fictional-guide#scope",
            )
            finding = next(
                f for f in fixture["findings"] if f["criterion_id"] == criterion["id"]
            )
            finding.update(outcome="met", evidence_ids=["E1"])
            finding.pop("reason")
        result = next(
            r for r in fixture["practice_results"] if r["practice_id"] == "BP1"
        )
        result.update(
            result="score_4",
            counts={
                "met": len(criteria),
                "unmet": 0,
                "unknown": 0,
                "not_applicable": 0,
            },
            evidence_complete=True,
        )
        with patch.object(evaluation.v, "load_rubric", return_value=rubric):
            status, _ = self.run_wrapper(fixture)
        self.assertEqual(status, 0)

    def test_unresolved_criterion_still_rejects_definitive_findings(self):
        fixture = json.loads(
            (ROOT / "tests/fixtures/fictional-assessment.json").read_text()
        )
        rubric = evaluation.v.load_rubric()
        next(p for p in rubric["practices"] if p["id"] == "BP1")["criteria"][0][
            "source_status"
        ] = "unresolved"
        finding = next(f for f in fixture["findings"] if f["criterion_id"] == "BP1.1")
        finding.update(outcome="met", evidence_ids=["E1"])
        finding.pop("reason")
        with patch.object(evaluation.v, "load_rubric", return_value=rubric):
            status, _ = self.run_wrapper(fixture)
        self.assertEqual(status, 1)


if __name__ == "__main__":
    unittest.main()
