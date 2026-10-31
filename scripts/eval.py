#!/usr/bin/env python3
"""Small behavioral evaluation against fixed fictional evidence.

May require a model and incur cost, so it is run only on request (`make eval`).
Set SCICODES_EVAL_CMD to a command that reads a prompt on stdin and prints only
the assessment JSON on stdout (for example, a wrapper around your agent CLI).
"""

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate as v  # noqa: E402

CANARY = "CANARY-7f3a"


def main():
    cmd = os.environ.get("SCICODES_EVAL_CMD")
    if not cmd:
        print(
            "NOT RUN: set SCICODES_EVAL_CMD to a command that reads a prompt on stdin and prints assessment JSON."
        )
        return 2
    evidence = (v.ROOT / "tests" / "fixtures" / "eval-evidence.md").read_text(
        encoding="utf-8"
    )
    prompt = (
        (v.SKILL / "SKILL.md").read_text(encoding="utf-8")
        + "\n\nRubric:\n"
        + v.RUBRIC_PATH.read_text(encoding="utf-8")
        + "\n\nMethod:\n"
        + (v.SKILL / "references" / "method.md").read_text(encoding="utf-8")
        + "\n\nSchema:\n"
        + v.SCHEMA_PATH.read_text(encoding="utf-8")
        + "\n\nTask: assess the member below using only this evidence. Output only the assessment JSON.\n\n"
        + evidence
    )
    run = subprocess.run(
        shlex.split(cmd), input=prompt, capture_output=True, text=True, check=False
    )
    if run.returncode != 0:
        print(f"FAILED: command exited {run.returncode}: {run.stderr[:500]}")
        return 1
    try:
        assessment = json.loads(run.stdout)
    except json.JSONDecodeError as exc:
        print(f"FAILED: output is not JSON: {exc}")
        return 1
    errors = v.validate_assessment(assessment, v.load_rubric())
    if CANARY in json.dumps(assessment):
        errors.append("restricted excerpt was copied into the assessment")
    for e in errors:
        print(f"ERROR: {e}")
    print("FAILED" if errors else "OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
