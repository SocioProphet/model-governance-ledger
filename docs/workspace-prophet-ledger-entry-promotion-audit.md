# Audit: workspace-prophet-ledger-entry as promotion record target

**Date:** 2026-06-11  
**Schema:** `schemas/workspace-prophet-ledger-entry.v0.1.schema.json`  
**Question:** Can `workspace-prophet-ledger-entry` serve as a model promotion record target?

---

## Verdict: Not in its current form — but the evidence substrate is reusable

The current v0.1 schema is not suitable as a promotion record target. Two hard invariants block it:

1. **`"production_ready": { "const": false }`** — The schema structurally prohibits any entry from declaring production readiness. A promotion record must be able to reach `promotionState: approved`.
2. **`"entry_type": { "const": "workspace_prophet_e2e_fixture" }`** — The schema is coupled to one specific entry kind. A promotion record needs a broader or different type discriminator.

Both of these are intentional design constraints for the current fixture-validation stage — not bugs. They correctly prevent premature promotion claims during the private-preview phase.

---

## What the schema does well (carry forward to v0.2)

| Pattern | Value |
|---------|-------|
| `validated_evidence` array | Structured `(repo, command, observed_state, evidence_class)` — exactly right for a promotion record's evidence chain |
| `non_claims` array | Explicit non-production claims are a strong pattern; promotion records should carry these |
| `readiness_state` enum | `planned → fixture_validated → runtime_observed → production_ready → blocked` is a clean progression; promote this to the promotion schema |
| `evidence_class` enum | `local_user_observed / ci_observed / fixture_declared / planned` differentiates evidence quality correctly |

---

## Path to v0.2: workspace-prophet-promotion-record schema

A new schema `workspace-prophet-promotion-record.v0.2.schema.json` should be created that:

- **Removes** `"production_ready": { "const": false }` → replace with `{ "type": "boolean" }`
- **Removes** `"entry_type": { "const": "workspace_prophet_e2e_fixture" }` → replace with `{ "enum": ["workspace_prophet_e2e_fixture", "workspace_prophet_promotion"] }`
- **Adds** `promotionState: { "enum": ["pending", "approved", "rejected", "rolled_back"] }` (required)
- **Adds** `modelRef`, `surfaceRef`, `rollbackRef` (optional, matching `promotion-record.example.json` conventions)
- **Retains** `validated_evidence`, `non_claims`, `readiness_state`, `evidence_thread_ref`, `receipt_ref`

The v0.1 schema and `examples/workspace-prophet/ledger-entry.fixture_validated.json` remain authoritative for the fixture-validation stage. The v0.2 schema extends the progression into the promotion stage.

---

## Gate for v0.2 creation

v0.2 should not be created until at least one workspace-prophet evidence chain reaches `readiness_state: runtime_observed` with `evidence_class: ci_observed` on at least 3 items. Creating a promotion schema before that evidence exists would be speculative schema ahead of the runtime.

Current state: `readiness_state: fixture_validated`, all items `local_user_observed`. **Not yet at the v0.2 gate.**

---

## Action items

- [ ] No schema change required now
- [ ] Revisit when `runtime_observed` evidence exists — open `workspace-prophet-promotion-record.v0.2.schema.json` PR at that point
- [ ] Link this audit from `MODEL_GOVERNANCE_LEDGER.md` under workspace-prophet section
