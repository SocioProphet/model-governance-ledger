#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = [
    "model-evidence-record.example.json",
    "route-evidence-record.example.json",
    "promotion-record.example.json",
    "rollback-record.example.json",
    "professional-intelligence-model-evidence-record.example.json",
    "professional-intelligence-route-evidence-record.example.json",
    "professional-intelligence-promotion-record.example.json",
    "professional-intelligence-rollback-record.example.json",
]
MODEL_GOVERNANCE_EXAMPLES = [
    "training-run.example.json",
    "inference-trace.example.json",
    "drift-event.example.json",
    "learning-event.example.json",
]
REQUIRED_SPEC_FIELDS = {
    "surfaceRef",
    "serviceRef",
    "datasetRefs",
    "adapterRefs",
    "evalRefs",
    "guardrailDecisionRefs",
    "routeDecisionRefs",
    "promotionState",
    "rollbackRef",
    "evidenceRefs",
}
RECORD_KINDS = {
    "ModelEvidenceRecord": "model-evidence",
    "RouteEvidenceRecord": "route-evidence",
    "PromotionRecord": "promotion",
    "RollbackRecord": "rollback",
}
PROMOTION_STATES = {"candidate", "approved", "rejected", "rollback-ready", "rolled-back", "deprecated"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(msg: str) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return 1


def validate_record(path: Path) -> int:
    doc = load(path)
    if doc.get("apiVersion") != "ledger.socioprophet.dev/v1":
        return fail(f"{path.name}: apiVersion invalid")
    kind = doc.get("kind")
    if kind not in RECORD_KINDS:
        return fail(f"{path.name}: kind invalid")
    metadata = doc.get("metadata", {})
    if not metadata.get("recordId") or not metadata.get("createdAt"):
        return fail(f"{path.name}: metadata.recordId and createdAt required")
    if metadata.get("recordKind") != RECORD_KINDS[kind]:
        return fail(f"{path.name}: metadata.recordKind must be {RECORD_KINDS[kind]}")
    spec = doc.get("spec", {})
    missing = sorted(REQUIRED_SPEC_FIELDS - set(spec))
    if missing:
        return fail(f"{path.name}: missing spec fields {missing}")
    if not (spec.get("modelRef") or spec.get("serviceRef")):
        return fail(f"{path.name}: modelRef or serviceRef required")
    if spec["promotionState"] not in PROMOTION_STATES:
        return fail(f"{path.name}: promotionState invalid")
    for list_field in ["datasetRefs", "adapterRefs", "evalRefs", "guardrailDecisionRefs", "routeDecisionRefs", "evidenceRefs"]:
        if not isinstance(spec[list_field], list):
            return fail(f"{path.name}: {list_field} must be a list")
    if not spec["evidenceRefs"]:
        return fail(f"{path.name}: evidenceRefs must be non-empty")
    if kind == "PromotionRecord" and not spec.get("approvedByRef"):
        return fail(f"{path.name}: PromotionRecord requires approvedByRef")
    if kind == "RollbackRecord" and not spec.get("restoresPromotionRef"):
        return fail(f"{path.name}: RollbackRecord requires restoresPromotionRef")
    return 0


def validate_professional_intelligence_links() -> int:
    examples = {
        name: load(ROOT / "examples" / name)
        for name in EXAMPLES
        if name.startswith("professional-intelligence-")
    }
    route = examples["professional-intelligence-route-evidence-record.example.json"]
    model = examples["professional-intelligence-model-evidence-record.example.json"]
    promotion = examples["professional-intelligence-promotion-record.example.json"]
    rollback = examples["professional-intelligence-rollback-record.example.json"]

    route_id = route["metadata"]["recordId"]
    model_id = model["metadata"]["recordId"]
    promotion_id = promotion["metadata"]["recordId"]
    rollback_id = rollback["metadata"]["recordId"]

    if route["spec"]["routeDecisionRefs"] != ["route-decision://pi-demo-0001/review-packet"]:
        return fail("professional-intelligence route evidence must reference the review-packet route decision")
    if "guardrail-pack://professional-intelligence/gate-3-demo" not in model["spec"]["guardrailDecisionRefs"]:
        return fail("professional-intelligence model evidence must reference the guardrail pack")
    if route_id not in promotion["spec"]["evidenceRefs"] or model_id not in promotion["spec"]["evidenceRefs"]:
        return fail("professional-intelligence promotion must reference model and route evidence")
    if rollback["spec"].get("restoresPromotionRef") != promotion_id:
        return fail("professional-intelligence rollback must restore the promotion record")
    if rollback["metadata"]["recordId"] != promotion["spec"].get("rollbackRef"):
        return fail("professional-intelligence promotion rollbackRef must match rollback record")
    if rollback_id != model["spec"].get("rollbackRef") or rollback_id != route["spec"].get("rollbackRef"):
        return fail("professional-intelligence evidence records must reference rollback record")
    return 0


def validate_training_run(path: Path) -> int:
    doc = load(path)
    if doc.get("kind") != "TrainingRun":
        return fail(f"{path.name}: kind invalid")
    metadata = doc.get("metadata", {})
    if not metadata.get("recordId") or not metadata.get("createdAt"):
        return fail(f"{path.name}: metadata.recordId and createdAt required")
    spec = doc.get("spec", {})
    required_fields = {
        "datasetManifestRef",
        "splitManifestRef",
        "modelCardRef",
        "evaluationReportRefs",
        "policyDecisionRefs",
    }
    missing = sorted(required_fields - set(spec))
    if missing:
        return fail(f"{path.name}: missing spec fields {missing}")
    if not isinstance(spec["evaluationReportRefs"], list) or not spec["evaluationReportRefs"]:
        return fail(f"{path.name}: evaluationReportRefs must be a non-empty list")
    if not isinstance(spec["policyDecisionRefs"], list) or not spec["policyDecisionRefs"]:
        return fail(f"{path.name}: policyDecisionRefs must be a non-empty list")
    return 0


def validate_inference_trace(path: Path) -> int:
    doc = load(path)
    if doc.get("kind") != "InferenceTrace":
        return fail(f"{path.name}: kind invalid")
    metadata = doc.get("metadata", {})
    if not metadata.get("recordId") or not metadata.get("createdAt"):
        return fail(f"{path.name}: metadata.recordId and createdAt required")
    spec = doc.get("spec", {})
    required_fields = {
        "inputAnchorRef",
        "modelRefs",
        "modelVersions",
        "scores",
        "explanationRefs",
        "outputClaimRefs",
        "confidence",
        "uncertainty",
        "policyDecisionRefs",
        "claimClassEvaluations",
        "modelOutput",
    }
    missing = sorted(required_fields - set(spec))
    if missing:
        return fail(f"{path.name}: missing spec fields {missing}")
    list_fields = {
        "modelRefs",
        "modelVersions",
        "explanationRefs",
        "outputClaimRefs",
        "policyDecisionRefs",
        "claimClassEvaluations",
    }
    for field in list_fields:
        if not isinstance(spec[field], list) or not spec[field]:
            return fail(f"{path.name}: {field} must be a non-empty list")
    if not isinstance(spec["scores"], dict) or not spec["scores"]:
        return fail(f"{path.name}: scores must be a non-empty object")
    if not isinstance(spec["confidence"], (int, float)) or not 0.0 <= spec["confidence"] <= 1.0:
        return fail(f"{path.name}: confidence must be between 0 and 1")
    if not isinstance(spec["uncertainty"], (int, float)) or not 0.0 <= spec["uncertainty"] <= 1.0:
        return fail(f"{path.name}: uncertainty must be between 0 and 1")
    output = spec["modelOutput"]
    if not isinstance(output, dict):
        return fail(f"{path.name}: modelOutput must be an object")
    if output.get("admissionStatus") != "proposal":
        return fail(f"{path.name}: model outputs must remain proposal only")
    for item in spec["claimClassEvaluations"]:
        if not isinstance(item, dict) or not item.get("claimClassRef") or not item.get("evaluationReportRef"):
            return fail(f"{path.name}: claimClassEvaluations items require claimClassRef and evaluationReportRef")
    return 0


def validate_drift_event(path: Path) -> int:
    doc = load(path)
    if doc.get("kind") != "DriftEvent":
        return fail(f"{path.name}: kind invalid")
    metadata = doc.get("metadata", {})
    if not metadata.get("recordId") or not metadata.get("createdAt"):
        return fail(f"{path.name}: metadata.recordId and createdAt required")
    spec = doc.get("spec", {})
    required_fields = {"inferenceTraceRef", "signalType", "signalValue", "policyDecisionRefs"}
    missing = sorted(required_fields - set(spec))
    if missing:
        return fail(f"{path.name}: missing spec fields {missing}")
    if spec.get("signalType") not in {"drift", "calibration"}:
        return fail(f"{path.name}: signalType must be drift or calibration")
    if not isinstance(spec["policyDecisionRefs"], list) or not spec["policyDecisionRefs"]:
        return fail(f"{path.name}: policyDecisionRefs must be a non-empty list")
    return 0


def validate_learning_event(path: Path) -> int:
    doc = load(path)
    if doc.get("kind") != "LearningEvent":
        return fail(f"{path.name}: kind invalid")
    metadata = doc.get("metadata", {})
    if not metadata.get("recordId") or not metadata.get("createdAt"):
        return fail(f"{path.name}: metadata.recordId and createdAt required")
    spec = doc.get("spec", {})
    required_fields = {
        "inferenceTraceRef",
        "driftEventRef",
        "trainingRunRef",
        "datasetManifestRef",
        "policyDecisionRefs",
    }
    missing = sorted(required_fields - set(spec))
    if missing:
        return fail(f"{path.name}: missing spec fields {missing}")
    if not isinstance(spec["policyDecisionRefs"], list) or not spec["policyDecisionRefs"]:
        return fail(f"{path.name}: policyDecisionRefs must be a non-empty list")
    return 0


def validate_model_governance_links() -> int:
    training = load(ROOT / "examples" / "training-run.example.json")
    inference = load(ROOT / "examples" / "inference-trace.example.json")
    drift = load(ROOT / "examples" / "drift-event.example.json")
    learning = load(ROOT / "examples" / "learning-event.example.json")
    if drift["spec"]["inferenceTraceRef"] != inference["metadata"]["recordId"]:
        return fail("drift-event inferenceTraceRef must reference inference trace record")
    if learning["spec"]["inferenceTraceRef"] != inference["metadata"]["recordId"]:
        return fail("learning-event inferenceTraceRef must reference inference trace record")
    if learning["spec"]["driftEventRef"] != drift["metadata"]["recordId"]:
        return fail("learning-event driftEventRef must reference drift-event record")
    if learning["spec"]["trainingRunRef"] != training["metadata"]["recordId"]:
        return fail("learning-event trainingRunRef must reference training-run record")
    return 0


def main() -> int:
    for name in EXAMPLES:
        rc = validate_record(ROOT / "examples" / name)
        if rc:
            return rc
    rc = validate_training_run(ROOT / "examples" / "training-run.example.json")
    if rc:
        return rc
    rc = validate_inference_trace(ROOT / "examples" / "inference-trace.example.json")
    if rc:
        return rc
    rc = validate_drift_event(ROOT / "examples" / "drift-event.example.json")
    if rc:
        return rc
    rc = validate_learning_event(ROOT / "examples" / "learning-event.example.json")
    if rc:
        return rc
    rc = validate_professional_intelligence_links()
    if rc:
        return rc
    rc = validate_model_governance_links()
    if rc:
        return rc
    print(f"OK: validated {len(EXAMPLES) + len(MODEL_GOVERNANCE_EXAMPLES)} ledger examples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
