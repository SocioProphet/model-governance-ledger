# OrgGov Model and Tool Receipts

## Purpose

OrgGov Model and Tool Receipts connect Organization Governance Control Plane work orders to the model, adapter, tool, dataset, context-boundary, eval, rollback, and revocation evidence managed by the Model Governance Ledger.

The shared OrgGov loop is:

```text
Objective → Workroom → Actor → Role → Policy → Asset → Action → Evidence → Review → Outcome → Score → Learning
```

Model Governance Ledger owns the model/tool/data/eval/rollback/revocation receipt side of the loop. It does not run training jobs, execute agents, or own the product UX.

## Contract files

- `schemas/orggov-model-tool-receipt.v0.1.schema.json`
- `examples/orggov-model-tool-receipt.v0.1.example.json`
- `tools/validate_orggov_model_tool_receipts.py`

## Invariants

- Every receipt references a workroom, work order, actor, and session.
- Every receipt declares model route, tool refs, dataset refs, context-boundary refs, eval refs, outputs, rollback, revocation, and evidence refs.
- Public fixtures must keep `provenance.nonSecret` true.
- Raw private prompts, secrets, credentials, or unbounded user data do not belong in committed receipts.
- Promotion posture must be explicit; v0 fixtures should default to `review_required` unless a stronger approval record exists.

## Cross-repo links

- Parent: `SocioProphet/prophet-platform#406`
- Ledger workstream: `SocioProphet/model-governance-ledger#13`
- AgentPlane evidence binding: `SocioProphet/agentplane#104`
- Policy gates: `SocioProphet/policy-fabric#57`
- Agent authority: `SocioProphet/agent-registry#18`
