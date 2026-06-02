from __future__ import annotations

import json
from pathlib import Path

from tools.validate_trust_chain_model_runtime_binding import main as validate_trust_chain_model_runtime_binding


ROOT = Path(__file__).resolve().parents[2]
VALID_FIXTURE = ROOT / "examples" / "trust-chain-model-runtime-binding.valid.json"
BLOCKED_FIXTURE = ROOT / "examples" / "trust-chain-model-runtime-binding.blocked.json"


def test_trust_chain_model_runtime_binding_validator() -> None:
    assert validate_trust_chain_model_runtime_binding() == 0


def test_valid_binding_allows_production_promotion() -> None:
    fixture = json.loads(VALID_FIXTURE.read_text(encoding="utf-8"))
    assert fixture["promotion"]["environment"] == "production"
    assert fixture["promotion"]["decision"] == "allowed"
    assert fixture["promotion"]["requires_runtime_evidence"] is True
    assert fixture["promotion"]["requires_eval_receipts"] is True
    assert fixture["trust_chain_refs"]["agentplane_supply_chain_validation_ref"]
    assert fixture["trust_chain_refs"]["runtime_receipt_ref"]


def test_blocked_binding_requires_runtime_repair() -> None:
    fixture = json.loads(BLOCKED_FIXTURE.read_text(encoding="utf-8"))
    assert fixture["promotion"]["environment"] == "production"
    assert fixture["promotion"]["decision"] == "blocked"
    assert fixture["trust_chain_refs"]["agentplane_supply_chain_validation_ref"] is None
    assert fixture["trust_chain_refs"]["runtime_receipt_ref"] is None
    assert fixture["remediation"]
    assert all(item["required_before_promotion"] is True for item in fixture["remediation"])
