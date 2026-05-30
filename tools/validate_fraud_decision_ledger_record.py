#!/usr/bin/env python3
"""Validate FraudDecisionLedgerRecord examples.

The validator is intentionally stdlib-only for bootstrap CI. It performs
structural checks plus the critical fraud-control-plane invariants that JSON
Schema alone cannot safely express without a full schema engine.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "fraud-decision-ledger-record.v0.1.schema.json"
VALID_EXAMPLE = ROOT / "examples" / "fraud-decision-ledger-record.example.json"
INVALID_EXAMPLES = {
    ROOT / "examples" / "fraud-decision-ledger-record.benchmark-production.invalid.json": "benchmark production claim",
    ROOT / "examples" / "fraud-decision-ledger-record.score-as-proof.invalid.json": "model score as proof or approval without label provenance",
}


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def require_fields(obj: dict[str, Any], fields: set[str], path: str) -> None:
    missing = sorted(fields - set(obj))
    require(not missing, f"{path}: missing fields {missing}")


def validate_record(path: Path, doc: dict[str, Any]) -> None:
    require(doc.get("apiVersion") == "model-governance.socioprophet.ai/v0.1", f"{path.name}: apiVersion invalid")
    require(doc.get("kind") == "FraudDecisionLedgerRecord", f"{path.name}: kind invalid")

    metadata = doc.get("metadata", {})
    require_fields(metadata, {"recordId", "createdAt", "capabilityRef", "doctrineRef"}, f"{path.name}: metadata")
    require(str(metadata["recordId"]).startswith("urn:socioprophet:fraud-ledger:"), f"{path.name}: recordId must be fraud ledger URN")
    require(metadata["capabilityRef"] == "fraud-decision-intelligence-control-plane", f"{path.name}: capabilityRef invalid")
    require("ProCybernetica" in metadata["doctrineRef"], f"{path.name}: doctrineRef must anchor ProCybernetica doctrine")

    spec = doc.get("spec", {})
    require_fields(
        spec,
        {
            "modelCard",
            "benchmarkRecord",
            "featureHealthRecords",
            "labelProvenanceRecords",
            "residualFraudLift",
            "thresholdSimulation",
            "driftMonitoring",
            "claimBoundaries",
            "promotion",
        },
        f"{path.name}: spec",
    )

    model_card = spec["modelCard"]
    require(model_card.get("scoreInterpretation") == "risk_signal_not_proof", f"{path.name}: model score must be risk_signal_not_proof")

    benchmark = spec["benchmarkRecord"]
    require(benchmark.get("productionValidationClaim") in {"not_claimed", "separate_validation_required"}, f"{path.name}: benchmark cannot claim production validation")
    require(isinstance(benchmark.get("benchmarkRefs"), list) and benchmark["benchmarkRefs"], f"{path.name}: benchmarkRefs required")

    feature_health = spec["featureHealthRecords"]
    require(isinstance(feature_health, list) and feature_health, f"{path.name}: featureHealthRecords must be non-empty")
    for index, feature in enumerate(feature_health):
        prefix = f"{path.name}: featureHealthRecords[{index}]"
        require_fields(
            feature,
            {"featureName", "availability", "missingnessStatus", "leakageRisk", "operationalAvailability", "recommendedHandling"},
            prefix,
        )
        if feature.get("missingnessStatus") == "material-delta":
            require(feature.get("recommendedHandling") in {"monitor", "quarantine", "investigate", "exclude", "impute"}, f"{prefix}: material-delta feature requires governed handling")
        if feature.get("leakageRisk") in {"high", "unknown"}:
            require(feature.get("recommendedHandling") in {"quarantine", "investigate", "exclude"}, f"{prefix}: high/unknown leakage risk requires quarantine, investigate, or exclude")

    labels = spec["labelProvenanceRecords"]
    require(isinstance(labels, list) and labels, f"{path.name}: labelProvenanceRecords must be non-empty")
    for index, label in enumerate(labels):
        prefix = f"{path.name}: labelProvenanceRecords[{index}]"
        require_fields(label, {"labelRef", "labelValue", "labelSource", "confidence", "availableAtDecisionTime", "reversible"}, prefix)
        require(isinstance(label["confidence"], (int, float)) and 0 <= label["confidence"] <= 1, f"{prefix}: confidence must be between 0 and 1")
        if label.get("labelValue") in {"confirmed_fraud", "confirmed_non_fraud"}:
            require(label.get("labelSource") not in {"", "unknown", "public-benchmark-only"}, f"{prefix}: confirmed label requires concrete provenance source")

    residual = spec["residualFraudLift"]
    require_fields(
        residual,
        {"incumbentCaught", "incumbentMissed", "modelOnlyCaught", "ruleOnlyCaught", "bothCaught", "neitherCaught", "falsePositivesByControlPath"},
        f"{path.name}: residualFraudLift",
    )

    threshold = spec["thresholdSimulation"]
    require(threshold.get("requiresHumanReview") is True or model_card.get("humanImpactingUse") is False, f"{path.name}: human-impacting use requires human review")

    drift = spec["driftMonitoring"]
    require(drift.get("monitoringRequired") is True, f"{path.name}: drift/adversarial displacement monitoring is required")

    boundaries = spec["claimBoundaries"]
    require(boundaries.get("modelScoreBoundary") == "risk_signal_not_proof", f"{path.name}: invalid model score boundary")
    require(boundaries.get("benchmarkBoundary") == "not_production_validation", f"{path.name}: invalid benchmark boundary")
    require(boundaries.get("labelBoundary") == "requires_provenance", f"{path.name}: invalid label boundary")
    require(boundaries.get("humanImpactBoundary") == "requires_policy_authorization", f"{path.name}: invalid human impact boundary")

    promotion = spec["promotion"]
    if promotion.get("productionReadinessClaim") == "approved_with_policy_receipt":
        require(promotion.get("approvalRef"), f"{path.name}: production readiness approval requires approvalRef")
    if promotion.get("promotionState") == "approved":
        require(promotion.get("requiresApproval") is True, f"{path.name}: approved promotion must require approval")
        require(promotion.get("approvalRef"), f"{path.name}: approved promotion requires approvalRef")
    if model_card.get("humanImpactingUse") is True:
        require(promotion.get("productionReadinessClaim") != "not_claimed", f"{path.name}: human-impacting use cannot be paired with no production readiness claim")


def main() -> int:
    load_json(SCHEMA)

    try:
        validate_record(VALID_EXAMPLE.relative_to(ROOT), load_json(VALID_EXAMPLE))
        print(f"ok: {VALID_EXAMPLE.relative_to(ROOT)}")

        for invalid_path, expected_reason in INVALID_EXAMPLES.items():
            try:
                validate_record(invalid_path.relative_to(ROOT), load_json(invalid_path))
            except ValidationError as exc:
                print(f"ok: rejected {invalid_path.relative_to(ROOT)} ({expected_reason}): {exc}")
                continue
            raise ValidationError(f"{invalid_path.relative_to(ROOT)} unexpectedly passed validation")

    except ValidationError as exc:
        print(f"ERR: {exc}", file=sys.stderr)
        return 1

    print("Fraud decision ledger validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
