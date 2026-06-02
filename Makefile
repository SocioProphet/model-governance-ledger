.PHONY: validate validate-v0 validate-trustops-receipts validate-fraud-decision-ledger validate-trust-chain-model-runtime-binding test release-dry-run

validate: validate-v0 validate-trustops-receipts validate-fraud-decision-ledger validate-trust-chain-model-runtime-binding
	python3 tools/validate_ledger_examples.py

validate-v0:
	python3 tools/check_record_v0.py

validate-trustops-receipts:
	python3 -m json.tool schemas/trustops-receipt-ledger-record.v0.1.schema.json >/dev/null
	python3 -m json.tool examples/trustops-receipt-ledger-record.example.json >/dev/null
	python3 -m json.tool examples/trustops-receipt-ledger-record.raw-sensitive.invalid.json >/dev/null
	python3 -m json.tool examples/trustops-receipt-ledger-record.control-plane.invalid.json >/dev/null
	python3 tools/validate_trustops_receipt_ledger_record.py examples/trustops-receipt-ledger-record.example.json
	! python3 tools/validate_trustops_receipt_ledger_record.py examples/trustops-receipt-ledger-record.raw-sensitive.invalid.json
	! python3 tools/validate_trustops_receipt_ledger_record.py examples/trustops-receipt-ledger-record.control-plane.invalid.json

validate-fraud-decision-ledger:
	python3 -m json.tool schemas/fraud-decision-ledger-record.v0.1.schema.json >/dev/null
	python3 -m json.tool examples/fraud-decision-ledger-record.example.json >/dev/null
	python3 -m json.tool examples/fraud-decision-ledger-record.benchmark-production.invalid.json >/dev/null
	python3 -m json.tool examples/fraud-decision-ledger-record.score-as-proof.invalid.json >/dev/null
	python3 tools/validate_fraud_decision_ledger_record.py

validate-trust-chain-model-runtime-binding:
	python3 -m json.tool schemas/trust-chain-model-runtime-binding.v0.1.schema.json >/dev/null
	python3 -m json.tool examples/trust-chain-model-runtime-binding.valid.json >/dev/null
	python3 -m json.tool examples/trust-chain-model-runtime-binding.blocked.json >/dev/null
	python3 tools/validate_trust_chain_model_runtime_binding.py

test:
	python3 -m pytest -q tools/tests

release-dry-run: validate test
	python3 tools/release_dry_run.py
