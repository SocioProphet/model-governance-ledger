.PHONY: validate validate-v0 test release-dry-run

validate: validate-v0
	python3 tools/validate_ledger_examples.py

validate-v0:
	python3 tools/check_record_v0.py

test:
	python3 -m pytest -q tools/tests

release-dry-run: validate test
	python3 tools/release_dry_run.py
