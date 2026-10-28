---
name: cbcc-truth-intake
description: Build the project's verified source of truth, facts, specs, claims, and real-asset registry.
---

# Truth & Intake

## Goal
Convert user files and confirmed information into a structured source of truth without filling gaps with guesses.

## Required outputs
- `source_registry.json`
- `product_facts.json`
- `spec_table.json`
- `claim_ledger.json`
- `real_asset_registry.json`
- `missing_information.md`
- `truth_conflicts.md`

## Rules
- Every factual field must cite at least one `source_id`.
- Material conflicts emit `[TRUTH_CONFLICT]`.
- Unknown values remain unknown.
- Packaging photos/manuals outrank generic model knowledge.
- Real product assets must declare fidelity: `LOCKED_PIXEL`, `REFERENCE_CONSTRAINED`, or `GENERATIVE`.

## Handoff
Downstream modules consume IDs, never paraphrased substitutes.
