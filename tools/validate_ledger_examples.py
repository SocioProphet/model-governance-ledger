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


def main() -> int:
    for name in EXAMPLES:
        rc = validate_record(ROOT / "examples" / name)
        if rc:
            return rc
    rc = validate_professional_intelligence_links()
    if rc:
        return rc
    print(f"OK: validated {len(EXAMPLES)} ledger examples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
