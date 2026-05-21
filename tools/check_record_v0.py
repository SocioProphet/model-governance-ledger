#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError as exc:
    raise SystemExit("jsonschema is required: python3 -m pip install jsonschema") from exc

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "governance-audit-record.v0.schema.json"
VALID = ROOT / "examples" / "governance-audit-record.valid.json"
INVALIDS = [
    ROOT / "examples" / "governance-audit-record.missing-policy-ref.invalid.json",
    ROOT / "examples" / "governance-audit-record.research-only-safe.invalid.json",
]
LOW_TRUST = {"plausible_needs_source", "speculative_do_not_use"}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("root must be object")
    return data


def check_data(data: dict[str, Any]) -> None:
    if data["source_quality"] in LOW_TRUST and data["implementation_safe"]:
        raise ValueError("low trust source marked safe")
    if not data.get("policy_decision_ref"):
        raise ValueError("missing policy decision ref")
    if not data.get("trace_ref"):
        raise ValueError("missing trace ref")
    if not data.get("provenance_refs"):
        raise ValueError("missing provenance refs")


def check(path: Path, schema: dict[str, Any]) -> None:
    data = load_json(path)
    jsonschema.validate(data, schema)
    check_data(data)


def main() -> int:
    schema = load_json(SCHEMA)
    check(VALID, schema)
    passed = []
    for path in INVALIDS:
        try:
            check(path, schema)
        except Exception:
            continue
        passed.append(path.name)
    if passed:
        raise SystemExit("invalid records passed: " + ", ".join(passed))
    print("OK: v0 record examples validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
