# Model Governance Ledger

Model Governance Ledger records evidence for SocioProphet model fabric.

It is not a model registry for weights and it does not store datasets. It records references: model/service refs, dataset refs, adapter refs, eval refs, guardrail decisions, route decisions, promotion state, rollback refs, and evidence refs.

## Role in model fabric

- `model-router` emits route decision refs.
- `guardrail-fabric` emits guardrail decision refs.
- `agent-registry` emits authority/session refs.
- `prophet-platform` registers platform service records.
- `sourceos-model-carry` consumes approved carry refs only.

## SourceOS boundary

SourceOS may carry approved refs, client launch profiles, cache policy, and evidence collectors.

SourceOS must not promote models, replace service artifacts, or own mutable model lifecycle authority.

## First record kinds

- `ModelEvidenceRecord`
- `RouteEvidenceRecord`
- `PromotionRecord`
- `RollbackRecord`

## Governed-intelligence lineage contracts

See `docs/MODEL_LINEAGE_INFERENCE_LEARNING.md` for `TrainingRun`, `InferenceTrace`, `DriftEvent`, and `LearningEvent` responsibilities and fixtures.

## Validation

```bash
make validate
make test
```

## Current boundary

This repository must not store model weights, datasets, secrets, credentials, raw private prompts, or compliance-certification claims.

## workspace-prophet promotion path

The `workspace-prophet-ledger-entry.v0.1.schema.json` is the current fixture-validation target. A promotion record schema (v0.2) is gated on `readiness_state: runtime_observed` with CI-observed evidence on at least 3 items. See [workspace-prophet-ledger-entry-promotion-audit.md](workspace-prophet-ledger-entry-promotion-audit.md) for the full assessment and v0.2 design note.
