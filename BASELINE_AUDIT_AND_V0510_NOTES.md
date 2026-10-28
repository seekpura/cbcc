# Baseline Audit and v0.5.10 Notes

## Baseline authority
- Unique source baseline: `cross-border-commerce-creative-v0.5.9-category-commerce-depth.zip`.
- Historical v0.5.8 and earlier packages remain construction history only.
- v0.5.10 is cumulative; no baseline path was removed.

## Path-level non-regression
- v0.5.9 baseline files: **418**
- v0.5.10 current files: **427**
- baseline paths preserved: **418 / 418**
- missing baseline paths: **0**
- additive paths: **9**

### Added paths
- `BASELINE_AUDIT_AND_V0510_NOTES.md`
- `CHANGELOG_V0510.md`
- `EVIDENCE_COMMERCE_VALIDATION_V0510.md`
- `knowledge/category_evidence_reconciliation.md`
- `knowledge/offer_response_evidence.md`
- `prompts/category_evidence_reconciliation.md`
- `prompts/offer_response_evidence.md`
- `runtime/cbcc/evidence_reconciliation.py`
- `tests/test_v0510_evidence_commerce_reconciliation.py`

### Modified baseline paths
18 baseline files changed in place to integrate v0.5.10 while preserving their paths:
- `BUILD_MANIFEST.json`
- `CHANGELOG.md`
- `CURRENT_HANDOFF.md`
- `README.md`
- `SKILL.md`
- `VERSION`
- `knowledge/registry.json`
- `ontology/commerce_ontology.json`
- `prompts/registry.json`
- `runtime/cbcc/category_strategy.py`
- `runtime/cbcc/compiler.py`
- `runtime/cbcc/state.py`
- `runtime/cbcc/strategy_depth.py`
- `runtime/cbcc/strategy_sources.py`
- `runtime/cbcc/tools/economics.py`
- `tests/test_v056_adapter_causal_copy_production_cmf.py`
- `tests/test_v057_adapter_cursor_causal_terminology_provider_prelight.py`
- `tests/test_v059_category_commerce_depth.py`

## v0.5.10 capability focus
1. Category Commerce profiles are priors, not the final authority.
2. Evidence reconciliation uses Product Truth / verified evidence, own shopper/behavior evidence, current scoped external evidence, category prior, then generic fallback.
3. Effective objection/proof/message priorities preserve category-prior trace and evidence-pressure trace.
4. Proof hierarchy declares evidence conditions and current input support.
5. Promo response, bundle affinity and repeat/replacement observations can support test candidates but do not establish causal incrementality or final offers.
6. Platform × category intersection changes expression, density and offer role without rewriting Product Truth.
7. Cross-category classifier ordering was corrected so delivery/installation intent cannot be swallowed by generic preparation language.

## Continuity verified
- Nine formal Strategy Authority sections remain.
- Dynamic asset curation remains question/job/surface/incremental-information/business-hypothesis driven.
- Every activated KIYUU asset retained complete `00–11`.
- Provider Job/Result, Review Item, Local Revision and Package Hash implementation remains in source. The KIYUU fixture did not request production, so no production/provider result was fabricated.
- Final Copy remains review-gated; KIYUU continues with 2 `DRAFT_REVIEW_REQUIRED` + 2 `TO_AUTHOR`, 0 approved finals.

## Validation boundary
The structured evidence-conflict suite validates Runtime authority behavior. It is not a live marketplace population study and does not establish causal business performance. Regression tests are non-regression evidence only, not a completion claim.
