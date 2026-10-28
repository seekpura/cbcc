# v0.5.12 — Production Learning Loop Depth

## Purpose
Complete the executable post-strategy loop without replacing the existing Strategy Authority or per-asset `00–11` packages.

## Added
- `runtime/cbcc/learning_loop.py`:
  - compile explicit Review revision requests into scope-limited Local Revision Provider Jobs;
  - preserve immutable parent asset packages and parent package hash;
  - ingest revision results, validate `changed_fields` against `allowed_fields`, and record revised-output SHA256 lineage;
  - expose revised outputs as independently addressable Review Items;
  - compile post-change metric learning with descriptive-vs-causal separation;
  - apply bounded Learning Ledger / local strategy overlays to Strategy Authority;
  - materialize `artifacts/production_learning_loop.json`.
- CLI lifecycle:
  - `revision-compile`
  - `revision-ingest`
  - `learning-apply`
- Review state now gives every local revision request a stable `revision_request_id` and closes the matching request when an accepted Local Revision Output is reviewed.
- Delivery now preserves `local_revisions/`, `learning_cycles/`, `learning_latest.json`, and `production_learning_loop.json`.
- New runtime-consumed Knowledge/Prompt authority for Production → Review → Local Revision → Learning.
- Ontology entities/relations/constraints for revision lineage and bounded learning.

## Learning boundary
- Provider completion is not Review acceptance.
- Local revision never mutates the parent `00–11` package.
- Empty `allowed_fields` is held rather than widened implicitly.
- Before/after movement is descriptive unless explicit valid causal evidence is supplied.
- Learning modifies only the evidence-implicated strategy layer and records unrelated frozen layers.
- Product Truth is never auto-rewritten by a post-production metric movement.

## Final Copy continuity
Existing Host Final Copy version/review contracts remain unchanged. Validation demonstrates an explicit Host-authored locale version reaches `APPROVED_FINAL` only when the exact version receives native-fluency, claim-equivalence, platform-fit and culture-fit approval.

## Compatibility
All v0.5.11 baseline paths remain preserved. See `BASELINE_AUDIT_AND_V0512_NOTES.md`.
