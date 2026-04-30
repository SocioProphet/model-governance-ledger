.PHONY: validate test release-dry-run

validate:
	python3 tools/validate_ledger_examples.py

test:
	python3 -m pytest -q tools/tests

release-dry-run: validate test
	python3 tools/release_dry_run.py
