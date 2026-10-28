# CBCC v0.5.12 — Production Learning Loop Validation

## Purpose
This validation checks the executable production-learning chain itself, not test-count progress. All Host and Provider responses used here are explicit local fixtures; they are **not** live third-party executions.

## Executed chain
`Host Final Copy → Provider Job → explicit Provider Result → Review → bounded Local Revision Request → Revision Provider Job → explicit Revision Provider Result → Revision Review → post-change measurement → Strategy Learning`

## Final-copy result
- Runtime: `0.5.12-production-learning-loop-depth`
- Strategy Authority sections: **9**
- Dynamic assets: **3**
- Every activated asset retains complete `00–11`: **True**
- Final Copy release counts: `{"APPROVED_FINAL": 4}`
- All supplied locale/field versions final: **True**

The validation deliberately supplies Host-authored `ms-MY` versions and exact-version professional review records. Runtime does not infer native-language approval.

## Initial Provider production
- Production status: **COMPLETE**
- Explicit Provider results ingested: **3 / 3**
- Provider completion remains distinct from Review acceptance.

## Bounded local revision
One production output is reviewed with a single permitted change:
- Revision ID: `LR-c113dbb87886b6`
- Revision request ID: `LRQ-f93f504a0e52`
- Asset: `AST-1429947A45`
- Allowed fields: `headline_copy`
- Parent package hash: `06285a2f0e0297224330db2ba511c347d122e53abe6ecb66e7e76076ffefe9e3`
- Revised output SHA256: `584d244d1d4ea66e7883251133777dca26ef86fe5c44a295765f327e1dfa0a70`
- Revised output review status: **ACCEPTED**

The Revision Provider Job keeps the original parent package hash and cannot widen the `allowed_fields` scope implicitly.

## Immutable parent proof
- Product Truth hash unchanged: **True**
- Every original base asset-package file unchanged byte-for-byte: **True**

The parent `00–11` package is therefore not rewritten to represent a local revision. The revised output is tracked through separate lineage.

## Post-change learning
Observed metrics:
- `cvr`: 0.02 → 0.026 (30.0% relative), verdict **IMPROVED**
- `return_rate`: 0.08 → 0.06 (-25.0% relative), verdict **IMPROVED**


Learning decision:
- Recommendation: **KEEP_LOCAL_CHANGE_MONITOR**
- Causal credit allowed: **False**
- Applied edit layer: `LISTING_HERO`
- Frozen layers: `PRODUCT_TRUTH`, `POSITIONING`, `OFFER`, `VISUAL_SYSTEM`
- Learning capability state after application: **INTEGRATED_ACTIVE**

Because no valid causal experiment is supplied, the runtime keeps the improvement descriptive and returns `KEEP_LOCAL_CHANGE_MONITOR`; it does not claim that the headline caused the CVR/return-rate movement.

## Review / learning state
- PRODUCTION: `READY_REVIEW`
- MEASUREMENT: `READY_REVIEW`
- LEARNING: `READY_REVIEW`

## What this proves
1. Exact-version Final Copy review can release copy without bypassing review authority.
2. Provider output can enter Review without being treated as accepted by default.
3. Review can create a scope-limited revision job rather than regenerate the whole strategy/asset package.
4. Revision result receives a distinct output hash and its own Review Item.
5. Post-change observation creates a bounded Strategy Authority learning overlay rather than rewriting Product Truth or unrelated layers.
6. `production_learning_loop.json` exposes the complete chain in one audit artifact.

## What this does **not** prove
- It is not a live TikTok/Shopee/Amazon Provider execution.
- It is not a live native-language professional review service.
- It is not causal proof of the observed metric improvement.
- It does not make v0.5.12 Release Candidate-ready by itself.
