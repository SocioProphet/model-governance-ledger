# model-governance-ledger

Evidence ledger for model, adapter, dataset, eval, promotion, factsheet, compliance, rollback, and revocation records across SocioProphet.

## Role

This repository is the governance ledger for model lifecycle records. It is the right home for personal tuning contracts because those contracts define consent, data boundaries, evaluation requirements, promotion posture, and revocation semantics.

It does **not** run training jobs directly. Orchestration belongs in the opt-in automation layer, primarily `SociOS-Linux/socios`.

## Prophet Trust Chain model/runtime bindings

Model Governance Ledger owns the model-promotion slice of Prophet Trust Chain. The platform standard and admission contract live in `SocioProphet/prophet-platform`:

- `docs/standards/PROPHET_TRUST_CHAIN_V0.md`
- `docs/TRUST_CHAIN_ADMISSION_CONTRACT.md`
- `docs/standards/PROPHET_TRUST_CHAIN_IMPLEMENTATION_MAP.md`

This repo now carries a `TrustChainModelRuntimeBinding` contract proving that a model promotion is bound to both evaluation receipts and admitted runtime evidence.

Contracts and fixtures:

```text
schemas/trust-chain-model-runtime-binding.v0.1.schema.json
examples/trust-chain-model-runtime-binding.valid.json
examples/trust-chain-model-runtime-binding.blocked.json
tools/validate_trust_chain_model_runtime_binding.py
tools/tests/test_trust_chain_model_runtime_binding.py
```

Validation:

```bash
make validate-trust-chain-model-runtime-binding
python3 -m pytest -q tools/tests/test_trust_chain_model_runtime_binding.py
```

The valid fixture requires a model artifact, runtime asset, dataset artifacts, eval receipts, policy decision, guardrail decision, AgentPlane supply-chain validation, runtime receipt, and admission decision before production promotion is allowed.

The blocked fixture proves fail-closed behavior: production promotion remains blocked when AgentPlane supply-chain validation and runtime receipt evidence are missing, even when the model and eval refs exist.

Boundary: Model Governance Ledger records model lifecycle governance and promotion posture. It does not run training jobs, treat benchmark scores as production validation, certify runtime production readiness by itself, replace Lattice Forge runtime evidence, replace Policy Fabric policy profiles, replace Guardrail Fabric action admission, or replace AgentPlane validation/replay/receipt evidence.

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

## Governed-intelligence model lineage contracts

Reference document:

```text
docs/MODEL_LINEAGE_INFERENCE_LEARNING.md
```

Fixtures:

```text
examples/training-run.example.json
examples/inference-trace.example.json
examples/drift-event.example.json
examples/learning-event.example.json
```

Validation:

```bash
make validate
make test
```

## Fraud Decision Intelligence ledger contracts

Fraud Decision Intelligence records keep fraud models, benchmarks, feature-health evidence, labels, residual-fraud lift, threshold simulations, and drift monitors inside a governed ledger boundary.

Contracts:

```text
schemas/fraud-decision-ledger-record.v0.1.schema.json
examples/fraud-decision-ledger-record.example.json
examples/fraud-decision-ledger-record.benchmark-production.invalid.json
examples/fraud-decision-ledger-record.score-as-proof.invalid.json
```

Validation:

```bash
make validate-fraud-decision-ledger
```

Core invariants:

- Model scores are risk signals, not proof of fraud.
- Public benchmarks and Kaggle-style metrics are not production validation.
- Confirmed fraud labels require provenance.
- Human-impacting use requires policy authorization and approval evidence.
- Material feature-health issues require governed handling.

## Boundary

| Layer | Responsibility |
|---|---|
| `SourceOS-Linux/sourceos-model-carry` | Carries local model profiles and service references. |
| `SociOS-Linux/socios` | Opt-in orchestration for training/tuning workflows. |
| `SocioProphet/model-governance-ledger` | Consent, dataset lineage, eval receipts, promotion, rollback, revocation, fraud model governance, benchmark boundaries, feature-health records, label provenance, residual-lift records, factsheets, and Trust Chain model/runtime promotion bindings. |
| `SocioProphet/model-router` | Routes to base local model, personal adapter/model, fraud scoring candidate, or hosted fallback under policy. |
| `SocioProphet/sherlock-search` | Produces retrieval/evidence references used by explanation traces. |
| `SocioProphet/holmes` | Produces reasoning/explanation trace references consumed by inference traces. |
| `SocioProphet/guardrail-fabric` | Produces policy decisions that gate claim admission and model lifecycle actions. |
| `SocioProphet/sociosphere` | Owns claims and admission flow; consumes model outputs as proposals only. |
| `SocioProphet/agentplane` | Emits workflow, validation, replay, and receipt anchors referenced by traces and governance records. |

## Invariants

- No personal tuning without signed user intent.
- No personal tuning without explicit data boundary.
- No raw app database ingestion by default.
- No whole-home ingestion.
- No model promotion without evaluation receipts.
- No model production promotion without admitted runtime Trust Chain evidence.
- No tuned artifact activation without approval.
- Revocation must disable tuned artifacts and remove training data where policy requires it.
- No fraud model score as proof of fraud.
- No public benchmark as production fraud validation.
- No confirmed fraud label without provenance.
- No human-impacting fraud use without policy authorization.
