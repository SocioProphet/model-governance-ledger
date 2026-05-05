# Professional Intelligence Model Governance Ledger

## Purpose

This document defines the Model Governance Ledger evidence records for the Professional Intelligence OS Gate 3 demo path.

Model Governance Ledger does not run agents, route models, author policy, or own workspace UX. It records evidence for model/service decisions, route decisions, promotion posture, rollback readiness, eval references, guardrail references, and dataset/context inputs.

## Evidence records

Professional Intelligence examples live under `examples/`:

- `professional-intelligence-route-evidence-record.example.json`
- `professional-intelligence-model-evidence-record.example.json`
- `professional-intelligence-promotion-record.example.json`
- `professional-intelligence-rollback-record.example.json`

These records connect:

- Agentplane workflow evidence;
- Model Router routing decisions;
- Guardrail Fabric runtime-control pack;
- Memory Mesh context pack;
- Sherlock search packet;
- Prophet Core Query context query;
- DelEx demo acceptance posture.

## Validation

Validate locally through the existing ledger path:

```bash
make validate
make test
```

The validator checks:

- all ledger examples have valid kind, metadata, promotion state, and evidence references;
- Professional Intelligence route evidence references the review-packet route decision;
- Professional Intelligence model evidence references the guardrail pack;
- promotion evidence references model and route evidence records;
- rollback records restore the promotion record;
- model and route evidence point at the rollback record.

## Gate 3 role

This fills the evidence-ledger gap in the Gate 3 demo slice. The ledger records prove that the route, model/action, promotion candidate, and rollback-ready posture are represented as governance artifacts before demo credit is claimed.
