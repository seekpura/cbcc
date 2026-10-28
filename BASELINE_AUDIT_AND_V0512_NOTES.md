# CBCC v0.5.12 — Baseline Audit and Non-Regression Notes

## Baseline authority
Unique source baseline: uploaded `cross-border-commerce-creative-v0.5.11-integration-quality-depth.zip`.

No older v0.3 / v0.4 alpha / v0.5.0–v0.5.10 tree was used as the source baseline.

## Path preservation
- v0.5.11 baseline files: **436**
- Baseline paths preserved: **436 / 436**
- Missing baseline paths: **0**
- v0.5.12 final source files (excluding caches and `BUILD_MANIFEST.json` self-entry behavior does not change the tree count): **443**
- Additive paths: **7**
- Modified baseline paths: **18** after final `BUILD_MANIFEST.json` refresh

Missing paths: `[]`

## Additive paths
- `BASELINE_AUDIT_AND_V0512_NOTES.md`
- `CHANGELOG_V0512.md`
- `PRODUCTION_LEARNING_VALIDATION_V0512.md`
- `knowledge/production_learning_loop.md`
- `prompts/production_learning_loop.md`
- `runtime/cbcc/learning_loop.py`
- `tests/test_v0512_production_learning_loop.py`

## v0.5.12 capability additions
- executable scope-limited Local Revision Provider Jobs;
- revision-result ingest with changed-field enforcement and revised-output SHA256 lineage;
- independently reviewable Local Revision Output items;
- post-change Learning Cycle with descriptive-vs-causal separation;
- bounded Strategy Authority learning overlays and Section 9 Learning Ledger;
- `production_learning_loop.json` full-chain summary;
- CLI lifecycle `revision-compile`, `revision-ingest`, `learning-apply`;
- Runtime-consumed Production Learning Knowledge / Prompt / Ontology authority;
- Delivery preservation of Local Revision and Learning artifacts.

## Absolute non-regression checks
- Nine Strategy Authority sections remain intact.
- Every activated asset still compiles complete `00–11`.
- Parent asset packages remain immutable during local revision.
- Provider Job / Result / Review / Local Revision / Hash lineage remains explicit.
- Dynamic asset count remains driven by decision questions rather than fixed 6/9/12 templates.
- Product Truth remains higher authority than post-production observations.
- Host Final Copy and external Provider execution remain explicit external boundaries.

## Validation posture
The full compatibility suite passes, but pass count is used only as non-regression evidence. v0.5.12 progress is defined by the executable production-learning loop and the resulting Strategy/Asset/Production lineage, not by the number of tests.
