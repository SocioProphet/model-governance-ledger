# TrustOps Receipt Ledger Records v0.1

## Purpose

`TrustOpsReceiptLedgerRecord v0.1` records TrustOps receipt evidence in `model-governance-ledger` without turning the ledger into a runtime control plane.

The estate-wide boundary is:

```text
TrustOps receipt = evidence
Guardrail Fabric = runtime-control decision
Agent Registry = authority mutation decision
Model Governance Ledger = evidence and lifecycle ledger
```

This record keeps that separation explicit.

## What the ledger records

A ledger record captures:

```text
record_id
subject_ref
subject_kind
trustops_receipt_ref
receipt_digest
receipt_class
runner_ref
policy_decision_ref
policy_decision
evidence_refs
redaction_summary
data_boundary
provenance_refs
factsheet_refs
promotion_refs / rollback_refs / revocation_refs / waiver_refs
control_plane_boundary
recorded_at
```

The record may cite downstream control-plane records, but it does not perform those actions.

## Control-plane boundary

Every valid record must say:

```json
"control_plane_boundary": {
  "ledger_only": true,
  "runtime_action_performed": false,
  "authority_mutation_performed": false,
  "allowed_control_refs": []
}
```

For restrictive policy decisions such as `require-review`, `quarantine`, `block`, `rollback`, or `revoke`, `allowed_control_refs` should cite the control-plane surfaces expected to act later, for example:

```text
SocioProphet/guardrail-fabric#13
SocioProphet/agent-registry#17
```

Those refs are citations, not actions.

## Sensitive-data boundary

The ledger must not store raw regulated, customer-controlled, or personal data. It stores redacted evidence refs, digests, provenance refs, and factsheet refs.

The validator rejects:

- `raw_sensitive_data_stored = true`
- `raw_data_exported = true`
- evidence refs that look like raw data handles, such as `raw-email-body:*`
- non-`evidence://` evidence refs

## Validation

```bash
make validate-trustops-receipts
```

This validates:

- schema syntax;
- positive TrustOps receipt ledger fixture;
- raw-sensitive-data negative fixture;
- control-plane-boundary negative fixture.

## Non-goals

This record does not execute TrustOps runners.

It does not emit Guardrail Fabric runtime actions.

It does not mutate Agent Registry authority.

It does not promote, rollback, revoke, or waive anything by itself.

It records evidence and lifecycle references only.
