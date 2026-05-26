#!/usr/bin/env python3
"""Validate TrustOpsReceiptLedgerRecord v0.1 fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "trustops-receipt-ledger-record.v0.1.schema.json"

REQUIRED = {
    "schemaVersion",
    "recordType",
    "record_id",
    "subject_ref",
    "subject_kind",
    "trustops_receipt_ref",
    "receipt_digest",
    "receipt_class",
    "runner_ref",
    "policy_decision_ref",
    "policy_decision",
    "evidence_refs",
    "redaction_summary",
    "data_boundary",
    "provenance_refs",
    "factsheet_refs",
    "control_plane_boundary",
    "recorded_at",
}
POLICY_DECISIONS = {"pass", "warn", "require-review", "quarantine", "block", "rollback", "revoke"}
RECEIPT_CLASSES = {
    "robustness",
    "fairness",
    "explanation",
    "uncertainty",
    "ranking-fairness",
    "rag-trust",
    "dataset-risk",
    "agent-trust",
    "reasoning-failure",
}
SUBJECT_KINDS = {"model", "adapter", "dataset", "service", "agent", "rag-package", "knowledge-base", "functional-service"}
RAW_REF_PREFIXES = ("raw:", "raw-", "raw_", "pii:", "personal-data:", "customer-data:", "raw-email-body:")


class ValidationError(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(ROOT)}: expected JSON object")
    return payload


def require_string(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        fail(f"{key}: expected non-empty string")
    return value


def require_string_list(record: dict[str, Any], key: str, *, allow_empty: bool = False) -> list[str]:
    value = record.get(key)
    if not isinstance(value, list):
        fail(f"{key}: expected list")
    if not allow_empty and not value:
        fail(f"{key}: expected non-empty list")
    seen: set[str] = set()
    out: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            fail(f"{key}[{index}]: expected non-empty string")
        if item in seen:
            fail(f"{key}: duplicate entry {item}")
        seen.add(item)
        out.append(item)
    return out


def validate_schema(schema: dict[str, Any]) -> None:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        fail("schema must use JSON Schema draft 2020-12")
    if schema.get("type") != "object":
        fail("schema must describe an object")
    if schema.get("additionalProperties") is not False:
        fail("schema must be strict")
    missing = sorted(REQUIRED - set(schema.get("required", [])))
    if missing:
        fail(f"schema missing required fields: {missing}")
    props = schema.get("properties", {})
    if props.get("schemaVersion", {}).get("const") != "model-governance-ledger.trustops-receipt-ledger-record.v0.1":
        fail("schemaVersion const mismatch")
    if props.get("recordType", {}).get("const") != "TrustOpsReceiptLedgerRecord":
        fail("recordType const mismatch")


def validate_record(record: dict[str, Any]) -> None:
    missing = sorted(REQUIRED - set(record))
    if missing:
        fail(f"missing required fields: {missing}")
    if record["schemaVersion"] != "model-governance-ledger.trustops-receipt-ledger-record.v0.1":
        fail("schemaVersion mismatch")
    if record["recordType"] != "TrustOpsReceiptLedgerRecord":
        fail("recordType mismatch")

    for key in (
        "record_id",
        "subject_ref",
        "subject_kind",
        "trustops_receipt_ref",
        "receipt_digest",
        "receipt_class",
        "runner_ref",
        "policy_decision_ref",
        "policy_decision",
        "recorded_at",
    ):
        require_string(record, key)

    if record["subject_kind"] not in SUBJECT_KINDS:
        fail(f"unknown subject_kind: {record['subject_kind']}")
    if not record["trustops_receipt_ref"].startswith("trustops-receipt:"):
        fail("trustops_receipt_ref must be trustops-receipt: ref")
    if not record["receipt_digest"].startswith("sha256:"):
        fail("receipt_digest must be sha256-bound")
    if record["receipt_class"] not in RECEIPT_CLASSES:
        fail(f"unknown receipt_class: {record['receipt_class']}")
    if record["policy_decision"] not in POLICY_DECISIONS:
        fail(f"unknown policy_decision: {record['policy_decision']}")

    evidence_refs = require_string_list(record, "evidence_refs")
    require_string_list(record, "provenance_refs")
    require_string_list(record, "factsheet_refs", allow_empty=True)
    for key in ("promotion_refs", "rollback_refs", "revocation_refs", "waiver_refs"):
        if key in record:
            require_string_list(record, key, allow_empty=True)

    for ref in evidence_refs:
        if ref.startswith(RAW_REF_PREFIXES):
            fail(f"raw sensitive evidence refs are not allowed: {ref}")
        if not ref.startswith("evidence://"):
            fail(f"evidence_refs must use evidence:// refs: {ref}")

    validate_redaction(record.get("redaction_summary"))
    validate_data_boundary(record.get("data_boundary"))
    validate_control_boundary(record.get("control_plane_boundary"), record["policy_decision"])


def validate_redaction(value: Any) -> None:
    if not isinstance(value, dict):
        fail("redaction_summary must be an object")
    if value.get("raw_sensitive_data_stored") is not False:
        fail("ledger must not store raw sensitive data")
    if not isinstance(value.get("redacted_fields"), list):
        fail("redaction_summary.redacted_fields must be a list")
    require_string(value, "sensitive_data_policy_ref")


def validate_data_boundary(value: Any) -> None:
    if not isinstance(value, dict):
        fail("data_boundary must be an object")
    require_string(value, "boundary_ref")
    for key in ("regulated_data", "customer_controlled_data", "personal_data"):
        if not isinstance(value.get(key), bool):
            fail(f"data_boundary.{key} must be boolean")
    if value.get("raw_data_exported") is not False:
        fail("ledger records must not export raw data")


def validate_control_boundary(value: Any, policy_decision: str) -> None:
    if not isinstance(value, dict):
        fail("control_plane_boundary must be an object")
    if value.get("ledger_only") is not True:
        fail("TrustOps ledger records must remain ledger-only")
    if value.get("runtime_action_performed") is not False:
        fail("ledger records must not perform runtime actions")
    if value.get("authority_mutation_performed") is not False:
        fail("ledger records must not mutate authority")
    allowed = value.get("allowed_control_refs")
    if not isinstance(allowed, list):
        fail("control_plane_boundary.allowed_control_refs must be a list")
    if policy_decision in {"require-review", "quarantine", "block", "rollback", "revoke"} and not allowed:
        fail("restrictive policy decisions must cite downstream control-plane refs")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_trustops_receipt_ledger_record.py <record.json>", file=sys.stderr)
        return 2
    try:
        validate_schema(load_json(SCHEMA))
        validate_record(load_json(Path(argv[1])))
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: {argv[1]} validates as TrustOpsReceiptLedgerRecord v0.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
