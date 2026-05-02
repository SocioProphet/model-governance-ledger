#!/usr/bin/env python3
"""Validate PersonalTuningContract examples.

This validator is intentionally lightweight and stdlib-only for bootstrap CI.
It enforces the critical invariants that personal tuning is consented,
revocable, scoped, evidence-backed, and orchestrated through the opt-in layer.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/personal-tuning-contract.schema.json"
EXAMPLES = sorted((ROOT / "examples").glob("personal-tuning-contract.*.json"))


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


def validate_contract(path: Path, doc: dict[str, Any]) -> None:
    require(doc.get("schemaVersion") == "v0.1", f"{path}: schemaVersion must be v0.1")
    require(doc.get("kind") == "PersonalTuningContract", f"{path}: kind must be PersonalTuningContract")
    require(str(doc.get("contractId", "")).startswith("urn:socioprophet:personal-tuning-contract:"), f"{path}: contractId must be a personal tuning URN")

    consent = doc.get("consent", {})
    require(consent.get("status") == "granted", f"{path}: example consent must be granted")
    require(consent.get("signedIntentRef"), f"{path}: signedIntentRef is required")
    require(consent.get("revocable") is True, f"{path}: personal tuning must be revocable")

    data_boundary = doc.get("dataBoundary", {})
    require(data_boundary.get("egressPolicy") in {"local-only", "tenant-private", "encrypted-allowed", "external-denied"}, f"{path}: invalid egressPolicy")
    require(data_boundary.get("redactionRequired") is True, f"{path}: redaction is required")
    denied = set(data_boundary.get("deniedSources", []))
    for required_denial in {"whole-home", "browser-profiles", "notes-raw-db", "photos-library", "token-stores"}:
        require(required_denial in denied, f"{path}: deniedSources must include {required_denial}")

    training = doc.get("trainingScope", {})
    require(training.get("requiresHumanReview") is True, f"{path}: human review is required")
    require(training.get("maxExamples", 0) > 0, f"{path}: maxExamples must be positive")

    evaluation = doc.get("evaluation", {})
    require(evaluation.get("evalPlanRef"), f"{path}: evalPlanRef is required")
    require(evaluation.get("requiredReceipts"), f"{path}: requiredReceipts must be non-empty")

    promotion = doc.get("promotion", {})
    require(promotion.get("requiresApproval") is True, f"{path}: promotion requires approval")
    require(promotion.get("defaultState") in {"not-promoted", "personal-only", "workspace-candidate", "tenant-candidate", "rejected"}, f"{path}: invalid defaultState")

    revocation = doc.get("revocation", {})
    require(revocation.get("supported") is True, f"{path}: revocation must be supported")
    require(revocation.get("deleteTrainingData") is True, f"{path}: training data deletion must be supported")
    require(revocation.get("disableTunedArtifact") is True, f"{path}: tuned artifact disablement must be supported")

    orchestration = doc.get("orchestration", {})
    require(orchestration.get("orchestrator") == "SociOS-Linux/socios", f"{path}: personal tuning examples must orchestrate through SociOS-Linux/socios")
    require(orchestration.get("optInRef"), f"{path}: optInRef is required")


def main() -> int:
    load_json(SCHEMA)
    if not EXAMPLES:
        print("ERR: no PersonalTuningContract examples found", file=sys.stderr)
        return 2

    try:
        for example in EXAMPLES:
            doc = load_json(example)
            validate_contract(example.relative_to(ROOT), doc)
            print(f"ok: {example.relative_to(ROOT)}")
    except ValidationError as exc:
        print(f"ERR: {exc}", file=sys.stderr)
        return 1

    print("Personal tuning contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
