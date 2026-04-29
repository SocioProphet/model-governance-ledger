.PHONY: validate test

validate:
	python3 tools/validate_ledger_examples.py

test:
	python3 -m pytest -q tools/tests
