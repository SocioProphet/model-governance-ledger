# model-governance-ledger

Evidence ledger for model, adapter, dataset, eval, promotion, factsheet, compliance, rollback, and revocation records across SocioProphet.

## Role

This repository is the governance ledger for model lifecycle records. It is the right home for personal tuning contracts because those contracts define consent, data boundaries, evaluation requirements, promotion posture, and revocation semantics.

It does **not** run training jobs directly. Orchestration belongs in the opt-in automation layer, primarily `SociOS-Linux/socios`.

## Personal tuning contracts

Personal tuning must be per-user, consented, scoped, revocable, and evidence-backed.

Contracts:

```text
schemas/personal-tuning-contract.schema.json
examples/personal-tuning-contract.local-llama32-user.json
```

Validation:

```bash
python3 tools/validate_personal_tuning_contracts.py
```

## Boundary

| Layer | Responsibility |
|---|---|
| `SourceOS-Linux/sourceos-model-carry` | Carries local model profiles and service references. |
| `SociOS-Linux/socios` | Opt-in orchestration for training/tuning workflows. |
| `SocioProphet/model-governance-ledger` | Consent, dataset lineage, eval receipts, promotion, rollback, revocation, and factsheets. |
| `SocioProphet/model-router` | Routes to base local model, personal adapter/model, or hosted fallback under policy. |

## Invariants

- No personal tuning without signed user intent.
- No personal tuning without explicit data boundary.
- No raw app database ingestion by default.
- No whole-home ingestion.
- No model promotion without evaluation receipts.
- No tuned artifact activation without approval.
- Revocation must disable tuned artifacts and remove training data where policy requires it.
