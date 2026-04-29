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
