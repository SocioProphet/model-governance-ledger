#!/usr/bin/env python3
"""Validate Workspace PROPHET ledger entry fixture."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "workspace-prophet-ledger-entry.v0.1.schema.json"
EXAMPLE = ROOT / "examples" / "workspace-prophet" / "ledger-entry.fixture_validated.json"

REQUIRED_REPOS = {
    "SocioProphet/prophet-core-contracts",
    "SocioProphet/prophet-platform",
    "SocioProphet/sherlock-search",
    "SocioProphet/sociosphere",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    schema = load_json(SCHEMA)
    example = load_json(EXAMPLE)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda error: list(error.path))
    if errors:
        print("Workspace PROPHET ledger entry failed schema validation:")
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            print(f" - {location}: {error.message}")
        return 1

    if example.get("production_ready") is not False:
        print("fixture ledger entry must not claim production readiness")
        return 1
    if example.get("readiness_state") != "fixture_validated":
        print("fixture ledger entry must remain fixture_validated")
        return 1

    repos = {item.get("repo") for item in example.get("validated_evidence", [])}
    missing = sorted(REQUIRED_REPOS - repos)
    if missing:
        print(f"ledger entry missing validated evidence repos: {missing}")
        return 1

    for item in example.get("validated_evidence", []):
        if item.get("observed_state") != "passed":
            print(f"validation evidence did not pass: {item}")
            return 1
        if item.get("evidence_class") != "local_user_observed":
            print(f"validation evidence class must remain local_user_observed for this fixture: {item}")
            return 1

    print("Workspace PROPHET ledger entry validates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
