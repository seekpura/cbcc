# CHANGELOG — v0.5.11 Integration Quality Depth

## Why this release exists
The release does not add another framework family. It audits whether previously built professional capabilities actually change the final strategy/asset/production system. v0.5.10 still had three real wiring gaps: research quality did not directly weight evidence reconciliation, Ads/Feedback lacked explicit local Strategy Revision Routing, and Market Search/Review/Competitor evidence required manual `market_theme_fit` to reach Dynamic Asset Curation.

## Runtime integration changes
- Added evidence-quality multipliers covering source-id traceability, freshness, representativeness metadata, scope match, caller-declared source quality, and cross-source agreement/conflict.
- Preserved authority order: Product Truth / verified policy → own shopper/feedback/behavior → quality-weighted current market evidence → Category prior → generic fallback.
- Added `MarketEvidenceFitContract`: current Search / Review / Competitor observations automatically create fit-review candidates but cannot create own-product assets until Host explicitly confirms Product Truth fit.
- Fixed domain-activation ordering so Market supplied only through `research_source_adapters` also activates Evidence Quality Weighting and Category Evidence Reconciliation Prompt/Knowledge authorities.
- Added `StrategyRevisionRoute` for Ads and Feedback with explicit `edit_layers` and `freeze_layers`.
- Materialized `market_evidence_fit_contract.json`, `strategy_revision_routing.json`, and `capability_integration_map.json`.
- Added the new integration artifacts to Project Delivery supporting analysis.

## Knowledge / Prompt / Ontology
- Added `PROMPT-EVIDENCE-QUALITY-WEIGHTING` / `KNOW-EVIDENCE-QUALITY-WEIGHTING`.
- Added `PROMPT-REVISION-INTEGRATION` / `KNOW-REVISION-INTEGRATION`.
- Added `EvidenceQualityWeight`, `MarketEvidenceFitContract`, `StrategyRevisionRoute`, and `CapabilityIntegrationMap`.
- Added stable IDs to the five historical strategy-depth knowledge files so authority traces never depend on null IDs.

## Canonical-engine cleanup
The root `calculators/` scripts are retained for compatibility, but Market, Unit Economics, Ad Economics and Experiment relative-change entrypoints now delegate to canonical `runtime/cbcc/tools/*` engines. This removes a second business-formula authority without deleting old CLI capability.

## Integration validation
- Identical review signal held constant: weak/stale/scope-mismatched evidence weighted to 6.0 and did not overrule the Food category prior; strong/current/scope-matched evidence weighted to 108.0 and could reorder to TASTE_PREP.
- Integrated stress project: Market Evidence Fit assets changed 0 → 1 only after explicit Product Truth fit confirmation.
- Ads + Feedback generated four local Strategy Revision Routes.
- 20 defined core Runtime capability rows produced no `INTEGRATION_GAP`; capabilities with no project input remain `INTEGRATED_INACTIVE_NO_PROJECT_INPUT` rather than being falsely called active.
- Eight compiled assets generated eight frozen Provider Jobs; external execution remained unauthorized.

## Non-regression boundary
Regression counts are compatibility evidence only, never product-completion evidence. Nine Strategy Authority sections, complete per-asset `00–11`, Provider / Result / Review / Local Revision / Package Hash contracts remain mandatory.
