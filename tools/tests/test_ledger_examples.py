from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_ledger_examples_validate() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate_ledger_examples.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "OK: validated" in result.stdout


def test_promotion_record_contains_sourceos_carry_ref_without_authority_transfer() -> None:
    record = json.loads((ROOT / "examples" / "promotion-record.example.json").read_text(encoding="utf-8"))
    spec = record["spec"]
    assert spec["promotionState"] == "approved"
    assert spec["sourceosCarryRef"].startswith("sourceos-carry://")
    assert spec["approvedByRef"].startswith("human://")


def test_rollback_record_restores_promotion_record() -> None:
    record = json.loads((ROOT / "examples" / "rollback-record.example.json").read_text(encoding="utf-8"))
    assert record["kind"] == "RollbackRecord"
    assert record["spec"]["promotionState"] == "rollback-ready"
    assert record["spec"]["restoresPromotionRef"] == "ledger-record-promotion-demo-001"


def test_inference_trace_model_output_is_proposal_only() -> None:
    trace = json.loads((ROOT / "examples" / "inference-trace.example.json").read_text(encoding="utf-8"))
    assert trace["kind"] == "InferenceTrace"
    assert trace["spec"]["modelOutput"]["admissionStatus"] == "proposal"
    assert trace["spec"]["policyDecisionRefs"][0].endswith("/review_required")


def test_learning_event_links_drift_and_training_run() -> None:
    learning = json.loads((ROOT / "examples" / "learning-event.example.json").read_text(encoding="utf-8"))
    drift = json.loads((ROOT / "examples" / "drift-event.example.json").read_text(encoding="utf-8"))
    training = json.loads((ROOT / "examples" / "training-run.example.json").read_text(encoding="utf-8"))
    assert learning["kind"] == "LearningEvent"
    assert learning["spec"]["driftEventRef"] == drift["metadata"]["recordId"]
    assert learning["spec"]["trainingRunRef"] == training["metadata"]["recordId"]
