# Governance Audit Record v0

Status: v0.1 bounded record surface.

This document defines the first Model Governance Ledger record primitive for the Watson/Cyc/Semantic-Web/CHRONOS deployable loop.

## Purpose

The record captures a policy decision reference, source-quality summary, trace reference, result, and provenance references. It gives downstream integration a stable audit payload without introducing a storage backend or attribution algorithm.

## Added surfaces

```text
schemas/governance-audit-record.v0.schema.json
examples/governance-audit-record.valid.json
examples/governance-audit-record.missing-policy-ref.invalid.json
examples/governance-audit-record.research-only-safe.invalid.json
tools/check_record_v0.py
```

## Validation

Run:

```bash
make validate-v0
```

The target is included in:

```bash
make validate
```

The checker validates schema shape and rejects records where review-only source quality is marked implementation-safe.

## Boundary

This tranche does not implement a database, external compliance integration, production storage, or an attribution algorithm. It provides the v0 record carrier and fixture checks only.
