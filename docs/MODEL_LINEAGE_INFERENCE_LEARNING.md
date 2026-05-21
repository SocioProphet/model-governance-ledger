# Model Lineage, Inference Trace, and Learning Events

## Scope and boundary

This document defines Model Governance Ledger responsibilities for governed-intelligence model lineage and model-output governance in the canonical loop:

`Observe -> Anchor -> Normalize -> Propose -> Explain -> Verify -> Govern -> Act -> Receipt -> Learn`

Model Governance Ledger owns:

- `Learn` records for model/eval lineage and lifecycle feedback.
- model-output governance records in `Propose -> Explain` as proposal evidence only.

Model Governance Ledger does not implement retrieval (`sherlock-search`), reasoning (`holmes`), policy execution (`guardrail-fabric`), or claim admission (`sociosphere`).

## Canonical contract mapping

| Ledger object | Canonical contract mapping (Ontogenesis) | Notes |
|---|---|---|
| `TrainingRun` | `TrainingRun` | Run-level lineage for a model build/update. |
| `DatasetManifest` | `DatasetManifest` | Dataset identity, version, and source lineage reference. |
| `SplitManifest` | `SplitManifest` | Train/validation/test partition contract. |
| `ModelCard` | `ModelCard` | Intended use, limits, and safety/performance metadata. |
| `EvaluationReport` | `EvaluationReport` | Evaluation artifacts attached to claim-consuming classes. |
| `InferenceTrace` | `InferenceTrace` | End-to-end model execution trace with evidence references. |
| `ModelOutput` | `ModelOutput` | Model proposal payload (never admitted truth by itself). |
| `ExplanationTrace` refs | `ExplanationTrace` (reference) | Cross-repo explanation provenance references. |
| `LearningEvent` | `LearningEvent` | Retraining/recalibration trigger with policy linkage. |
| `DriftEvent` | `DriftEvent` | Drift or calibration signal bound to inference evidence. |
| `PolicyDecision` refs | `PolicyDecision` (reference) | Policy gate outcomes produced by Guardrail Fabric. |

## Required invariant

Model output is a proposal, not admitted truth. A model output may support a `Claim` object only after downstream evidence, explanation, validation, and policy checks succeed in consuming systems.

## Minimum `InferenceTrace` fields

- `inputAnchorRef`
- `modelRefs`
- `modelVersions`
- `scores`
- `explanationRefs`
- `outputClaimRefs`
- `confidence`
- `uncertainty`
- `policyDecisionRefs`

The fixture also carries:

- `modelOutput` with `admissionStatus: "proposal"`
- `claimClassEvaluations` to bind claim classes to `EvaluationReport` references

## Evaluation-report attachment to claim classes

Inference traces include `claimClassEvaluations[]` items:

- `claimClassRef`: claim class that consumes model output.
- `evaluationReportRef`: evaluation receipt used to qualify model output usage for that class.

This creates an auditable bridge from model output to class-specific evaluation evidence.

## Worked example A: text classifier proposal flow

1. `InferenceTrace` records classifier scores, phrase evidence (`sherlock-search`), and rule trace (`holmes`).
2. `ModelOutput` proposes a claim (`admissionStatus: "proposal"`).
3. `policyDecisionRefs` records governance status (`review_required`), keeping claim admission external to this repository.

Fixture: `examples/inference-trace.example.json`

## Worked example B: inference trace to learning event

1. `InferenceTrace` is observed by monitors.
2. `DriftEvent` records calibration/drift signal for that trace.
3. `LearningEvent` references the inference trace, drift signal, and a linked training run, with policy authorization for retraining action.

Fixtures:

- `examples/drift-event.example.json`
- `examples/learning-event.example.json`
- `examples/training-run.example.json`

## Deterministic validation expectations

Validation hook: `tools/validate_ledger_examples.py`

Expected behavior:

- validates fixture structure for `TrainingRun`, `InferenceTrace`, `DriftEvent`, and `LearningEvent`
- enforces `InferenceTrace` minimum fields
- enforces `modelOutput.admissionStatus == "proposal"`
- validates deterministic links: inference -> drift -> learning and learning -> training run

Run:

```bash
make validate
make test
```
