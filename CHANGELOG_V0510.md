# v0.5.10 — Evidence Commerce Reconciliation Depth

## Why this release exists
v0.5.9 made Listing objections, proof hierarchy, offer hypotheses, message sequencing and cadence category-specific. The remaining risk was that a useful category prior could become a new template and override stronger current evidence. v0.5.10 makes the authority order explicit and pressure-tests the conflict.

## Runtime changes
### Evidence reconciliation
- Added `runtime/cbcc/evidence_reconciliation.py`.
- Category Commerce is a prior, not Product Truth.
- Reconciles own shopper questions, current search demand, labelled review/customer-voice themes and competitor proof observations into evidence pressure.
- Reorders objection/proof/message priority while preserving prior rank and conflict trace.
- Market evidence may change priority; it may not create unsupported claims or facts.

### Offer response evidence
- Added descriptive promo-response analysis. Approximate arc elasticity is descriptive only and is not treated as causal because traffic, seasonality, placement and selection can confound it.
- Added bundle-affinity analysis with an explicit denominator requirement. Attach rate is not incrementality.
- Added repeat/replacement-cycle observations. Observed repeat timing is not converted into invented recommended usage or CRM frequency.
- Offer patterns can become `EVIDENCE_SUPPORTED_TEST_CANDIDATE_NOT_LOCKED`; they still require Product Truth, capability, unit economics and incrementality before lock.

### Proof evidence conditions
- Proof hierarchy now carries evidence-condition templates and input evidence support.
- Category-typical proof forms are never treated as if the underlying evidence already exists.

### Platform × category intersection
- Added platform-specific entry priority, information density, proof rule and offer role.
- The same electronics evidence priority was validated across TikTok Shop, Shopee, Amazon and DTC while surface expression changed.

### Classifier safety
- Fixed a real cross-category collision where `prepare` in a delivery/installation question could be misclassified as food sensory/preparation intent. Hard fulfillment/service intent now outranks generic preparation language.

## Runtime authority
Added and consumed:
- `KNOW-CATEGORY-EVIDENCE-RECONCILIATION`
- `KNOW-OFFER-RESPONSE-EVIDENCE`
- `PROMPT-CATEGORY-EVIDENCE-RECONCILIATION`
- `PROMPT-OFFER-RESPONSE-EVIDENCE`

Added ontology entities/relations for EvidencePriority, CategoryEvidenceReconciliation, ProofEvidenceCondition, PromoResponseObservation, BundleAffinityObservation, RepeatReplacementCycle and PlatformCategoryIntersection.

## Validation
Structured conflict cases intentionally made current evidence disagree with the category prior:
- Food: `DIETARY_FIT` prior → `TASTE_PREP` effective.
- Electronics: `COMPATIBILITY` prior → `SERVICE` effective.
- Apparel: `SIZE_SELECTION` prior → `MATERIAL_CARE` effective.
- High-ticket durable: `SITE_FIT` prior → `DELIVERY_INSTALL` effective.

Same electronics Product Truth/evidence priority was also compiled for TikTok Shop, Shopee, Amazon and DTC to verify platform expression changes without rewriting the product truth.

## Non-regression principle
This release is cumulative. It does not collapse the nine Strategy Authority sections, dynamic asset curation, complete per-asset `00–11`, Provider/Review/Local Revision/Package Hash, Final Copy, Adapter, causal, terminology or prelight chains. Regression tests are compatibility evidence only, not a completion claim.
