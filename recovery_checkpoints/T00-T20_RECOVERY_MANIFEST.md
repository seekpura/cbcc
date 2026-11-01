# CBCC v0.6.76 recovery checkpoint — T00–T20

This is a **recovery checkpoint**, not a release claim and not a substitute for materializing the implementation branch.

- Stable base commit: `160cb40c8a96710eb3572b5ef2a82da43f3848ce`
- Verified snapshot artifact: `cross-border-commerce-creative-plugin-v0.6.75.zip` produced after T20 verification
- Snapshot bytes: `2582008`
- Snapshot SHA256: `14c90fb5ae359e60e8016707afcb93a9b0a974e1ee624788a8cd62af0feceeab`
- Diff versus stable installed v0.6.75 plugin source: `73` files (`33` added, `40` modified)
- Scope completed in snapshot: T00–T20, including authority/design/plan locks, Canonical Commerce Object Graph, lineage, Product Truth, Research, Audience/Culture, Economics/Offer, Strategy, Listing, Content/RACE, Ads/Reviews/Measurement, 23-family Opportunity Registry, typed Production Objects, Visual Master, route-aware Art Direction, scene-derived Photography/Lighting/CMF, Prompt decision consumption, and Video/Creator/LIVE temporal compilation.

## Recovery rule
The original local Git object database for T00–T20 was lost when the execution container was remounted. Do **not** fabricate replacement historical commit SHAs. The verified T20 snapshot is the byte authority for recovering the current implementation state.

From T21 onward, each completed Task must create a remote checkpoint commit on `backup/v0676-task-checkpoints` immediately after focused/cross-scope/materialization verification. GitHub Actions are not a per-Task blocking gate; they are checked at milestone/release gates.

The formal integration branch remains `work/v0676-full-system-recovery-clean`; `main` is not edited during construction.

## Key new source objects present in the T20 snapshot
- `runtime/cbcc/canonical_commerce_graph.py`
- `runtime/cbcc/canonical_project_assembler.py`
- `runtime/cbcc/inclusive_photography.py`
- `runtime/cbcc/opportunity_family_registry.py`
- `runtime/cbcc/production_object.py`
- `schemas/canonical_commerce_graph.schema.json`
- `schemas/production_object.schema.json`
- `references/CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md`
- `references/LOCKED_BASELINE_TRACE_MATRIX_CURRENT.md`
- `references/LOCKED_FULL_SYSTEM_DESIGN_SPEC_CURRENT.md`
- `references/LOCKED_IMPLEMENTATION_PLAN_CURRENT.md`
- `references/REQUIREMENT_EXECUTION_LEDGER_CURRENT.json`
- `references/V0676_REGRESSION_CHARACTERIZATION.md`
- `tests/test_v0676_*` through `test_v0676_temporal_media_compiler.py`

## Boundary
This checkpoint records recoverability and provenance. T21–T29 still require their own RED → GREEN → verification → remote checkpoint commits and final integration/release materialization.