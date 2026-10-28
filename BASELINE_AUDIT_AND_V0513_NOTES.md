# CBCC v0.5.13 — Baseline Audit and Non-Regression Notes

## Baseline authority
Unique source baseline: uploaded `cross-border-commerce-creative-v0.5.12-production-learning-loop-depth.zip`.

No v0.3 / v0.4 alpha / v0.5.0–v0.5.11 tree was used as the source baseline for v0.5.13.

## Path preservation
- v0.5.12 baseline files: **443**
- Baseline paths preserved: **443 / 443**
- Missing baseline paths: **0**
- v0.5.13 final source files: **447**
- Additive paths: **4**
- Modified baseline paths: **28** after final `BUILD_MANIFEST.json` refresh

Missing paths: `[]`

## Additive paths
- `BASELINE_AUDIT_AND_V0513_NOTES.md`
- `CHANGELOG_V0513.md`
- `REAL_PRODUCT_QUALITY_VALIDATION_V0513.md`
- `tests/test_v0513_real_product_strategy_quality.py`

## Why modified-path count is larger than additive-path count
v0.5.13 is primarily an **integration/quality correction release**. Existing Runtime paths were changed in place so the established architecture remains authoritative instead of being forked into another parallel subsystem.

Modified baseline paths include the existing:
- Dynamic Asset / category-decision classifier;
- Listing/PDP and Strategy Authority compilation;
- Evidence Reconciliation;
- Host Strategy Authority application;
- Final Copy numeric audit;
- Prompt / Knowledge / Ontology registries;
- Delivery Builder;
- version/current-handoff documentation;
- historical compatibility tests whose version-prefix assertions needed to permit the current cumulative version.

The final exact modified-path list is recorded in `BUILD_MANIFEST.json`.

## v0.5.13 capability additions / corrections
- category-aware decision classification shared across Dynamic Asset, Listing/PDP and Evidence Reconciliation;
- atomic compound-question splitting with explicit decision-question audit/coverage;
- topic-aware asset merge rules so incremental buyer information is not silently removed;
- live consumer-decision coverage and decision-specific Listing jobs in Strategy Authority;
- decision-topic-specific proof contracts;
- corrected missing-economics Offer readiness boundary;
- formal `strategy_host_authoring_request.json` using the existing Strategy Annotation contract;
- protected deterministic authorities during Host Strategy synthesis;
- Host value translation / strategic rationale rendering in human-readable Strategy Authority;
- field-level approved-Claim authority for extra numeric Final Copy tokens without weakening untraced-number blocking.

## Real-product validation scope
v0.5.13 used current source-bound product inputs for:
- COSRX Advanced Snail 96 Mucin Power Essence;
- Anker Prime 20,000mAh Power Bank (200W);
- UNIQLO Round Mini Shoulder Bag;
- Owala FreeSip Stainless Steel Water Bottle 24oz.

See `REAL_PRODUCT_QUALITY_VALIDATION_V0513.md` for blind-test failures, before/after Strategy results and Final Copy behavior.

## Absolute non-regression checks
- Nine Strategy Authority sections remain intact.
- Every activated asset still compiles complete `00–11`.
- Dynamic asset count remains driven by consumer decisions rather than fixed 6/9/12 templates.
- Provider Job / Result / Review / Local Revision / Hash / Learning architecture remains intact.
- Parent asset packages remain immutable during local revision.
- Product Truth remains above Host Strategy interpretation and market/category priors.
- Missing economics remains missing.
- Final Copy still requires deterministic hard checks plus explicit current-version review dimensions.
- The v0.5.12 Production → Review → Local Revision → Learning loop remains available unchanged in principle.

## External-production boundary
No real image/video Provider execution is fabricated for the four public real-product cases. Exact locked product masters/reference files and a live external Provider connector were not supplied. This release validates Strategy, Listing, Asset architecture and Final Copy behavior; real external visual/video production remains the next quality stage.

## Validation posture
The compatibility suite is used only as non-regression evidence. v0.5.13 progress is defined by the real-product business-quality defects found and corrected, not by PASS count, Gate count, Prompt count or file count.
