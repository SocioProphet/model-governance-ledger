#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "trust-chain-model-runtime-binding.v0.1.schema.json"
VALID_FIXTURE = ROOT / "examples" / "trust-chain-model-runtime-binding.valid.json"
BLOCKED_FIXTURE = ROOT / "examples" / "trust-chain-model-runtime-binding.blocked.json"

REQUIRED_TRUST_CHAIN_REFS = {
    "policy_decision_ref",
    "guardrail_decision_ref",
    "agentplane_supply_chain_validation_ref",
    "runtime_receipt_ref",
    "admission_decision_ref",
}


class ValidationError(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def json_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def type_matches(value: Any, expected: str) -> bool:
    actual = json_type_name(value)
    if expected == "number":
        return actual in {"integer", "number"}
    return actual == expected


def validate_schema(schema: dict[str, Any], value: Any, path: str = "$") -> None:
    if "const" in schema and value != schema["const"]:
        fail(f"{path}: expected const {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        fail(f"{path}: {value!r} not in enum {schema['enum']!r}")
    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(type_matches(value, item) for item in expected_types):
            fail(f"{path}: expected type {expected_types!r}, got {json_type_name(value)!r}")
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                fail(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                fail(f"{path}: unexpected properties {extra!r}")
        additional = schema.get("additionalProperties")
        for key, item in value.items():
            child_schema = properties.get(key)
            if child_schema is None and isinstance(additional, dict):
                child_schema = additional
            if child_schema is not None:
                validate_schema(child_schema, item, f"{path}.{key}")
    if isinstance(value, list):
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                validate_schema(item_schema, item, f"{path}[{index}]")


def validate_common(record: dict[str, Any], path: Path) -> None:
    if not str(record.get("model_artifact_ref", "")).startswith("model://"):
        fail(f"{path}: model_artifact_ref must start with model://")
    if not str(record.get("runtime_asset_ref", "")).startswith("runtime-asset://"):
        fail(f"{path}: runtime_asset_ref must start with runtime-asset://")
    if not record.get("dataset_artifact_refs"):
        fail(f"{path}: dataset_artifact_refs must not be empty")
    if not record.get("eval_receipt_refs"):
        fail(f"{path}: eval_receipt_refs must not be empty")
    promotion = record.get("promotion", {})
    if promotion.get("environment") == "production":
        if promotion.get("requires_runtime_evidence") is not True:
            fail(f"{path}: production promotion requires runtime evidence")
        if promotion.get("requires_eval_receipts") is not True:
            fail(f"{path}: production promotion requires eval receipts")


def validate_allowed(record: dict[str, Any], path: Path) -> None:
    validate_common(record, path)
    promotion = record["promotion"]
    if promotion.get("decision") != "allowed":
        fail(f"{path}: allowed fixture must have promotion.decision=allowed")
    if not promotion.get("approval_ref"):
        fail(f"{path}: allowed production promotion requires approval_ref")
    refs = record.get("trust_chain_refs", {})
    missing = sorted(key for key in REQUIRED_TRUST_CHAIN_REFS if not refs.get(key))
    if missing:
        fail(f"{path}: allowed production binding missing Trust Chain refs: {missing}")
    if record.get("remediation") not in ([], None):
        fail(f"{path}: allowed fixture must not require remediation")


def validate_blocked(record: dict[str, Any], path: Path) -> None:
    validate_common(record, path)
    promotion = record["promotion"]
    if promotion.get("decision") != "blocked":
        fail(f"{path}: blocked fixture must have promotion.decision=blocked")
    if promotion.get("approval_ref") is not None:
        fail(f"{path}: blocked fixture must not carry approval_ref")
    refs = record.get("trust_chain_refs", {})
    if refs.get("agentplane_supply_chain_validation_ref") is not None:
        fail(f"{path}: blocked fixture should not carry agentplane_supply_chain_validation_ref")
    if refs.get("runtime_receipt_ref") is not None:
        fail(f"{path}: blocked fixture should not carry runtime_receipt_ref")
    remediation = record.get("remediation", [])
    if not isinstance(remediation, list) or not remediation:
        fail(f"{path}: blocked fixture requires remediation")
    for item in remediation:
        if item.get("required_before_promotion") is not True:
            fail(f"{path}: remediation must be required before promotion")
        if not item.get("authority"):
            fail(f"{path}: remediation requires authority")


def main() -> int:
    try:
        schema = load_json(SCHEMA)
        valid = load_json(VALID_FIXTURE)
        blocked = load_json(BLOCKED_FIXTURE)
        validate_schema(schema, valid)
        validate_schema(schema, blocked)
        validate_allowed(valid, VALID_FIXTURE)
        validate_blocked(blocked, BLOCKED_FIXTURE)
    except ValidationError as exc:
        print(f"ERR: {exc}", file=sys.stderr)
        return 2
    print("OK: Trust Chain model-runtime binding validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
