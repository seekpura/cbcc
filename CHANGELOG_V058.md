# CBCC v0.5.8 — Multi-Category Strategy Specificity Depth

## Purpose
v0.5.8 deliberately pauses framework expansion and validates the existing commerce runtime against materially different categories. The objective is to find category-homogenization defects and fix them in Runtime without weakening the v0.5.7 evidence, localization, Provider, Review or asset-package chain.

## Real defects found
1. **Platform capability censorship:** exact platform packs could remove unverified GALLERY/VIDEO/CX surfaces from the strategy graph, allowing governance to censor strategic thinking.
2. **Generic visual fallback:** when no photography contract was supplied, different categories could inherit the same generic commercial-visual description and weak camera guidance.
3. **Category-blind decision classification:** decision questions such as fit/wear, capacity, leak/seal, stacking and care could collapse into generic commerce jobs.
4. **Question dedupe was lexical, not decision-semantic:** two differently worded questions solving the same purchase decision could become redundant assets.
5. **Textile CMF was under-specified:** material lighting logic was much stronger for glass/glossy/matte surfaces than for woven/fabric products.

## Runtime corrections
- Added `runtime/cbcc/category_strategy.py` with category-family inference, decision-intent classification, decision profiles, category-aware surface scoring and category execution profiles.
- Added category-specific strategy families for beauty/personal care, fashion/accessory, home durable, food/beverage, electronics and general commerce fallback.
- Added category-neutral decision intents including `FIT_WEAR`, `SIZE_CAPACITY`, `SEAL_LEAK`, `STORAGE_STACKING`, `WEATHER_BOUNDARY`, `CARE_MAINTENANCE`, `COMPATIBILITY`, `MATERIAL_SENSORY`, `PROOF`, `RELEVANCE`, `USAGE`, `PACKAGE_CONTENTS` and `IDENTIFY`.
- Auto-curated assets now merge repeated purchase questions by semantic decision intent + surface + family while explicit user-authored asset jobs preserve exact author intent.
- Platform-pack capability/surface verification now changes verification/submission status, not whether strategy is allowed to plan the surface. Unsupported/unverified surfaces remain `STRATEGY_PLANNING_RESEARCH_REQUIRED`.
- Visual Strategy now emits category-specific visual territory, purchase-decision priorities, proof visuals, human-use rules, camera-range recommendations and lighting logic.
- When no user photography contract exists, IMAGE assets receive a `STRATEGY_DERIVED_PHOTOGRAPHY_PLAN` with `prelight_required=true`; the recommendation is explicitly not Product Truth.
- Expanded CMF reasoning for textile/fabric/nylon/polyester/cotton/leather/woven materials.
- Added `KNOW-MULTICATEGORY-SPECIFICITY` and `PROMPT-MULTICATEGORY-SPECIFICITY`, consumed by Strategy Runtime and bound to sections 04/05/06.
- Added `CategoryDecisionProfile`, `DecisionIntent` and `CategoryPhotographyPlan` ontology objects and relations.

## Multi-category validation
Using the same runtime and intentionally comparable target-channel conditions:
- Beauty fixture: **4** auto-curated assets.
- Fashion/accessory fixture: **5** auto-curated assets.
- Home-durable fixture: **6** auto-curated assets.

Observed semantic merges:
- Two wear/adjustment questions became one `FIT_WEAR` asset.
- Two capacity questions became one `SIZE_CAPACITY` asset.

The three categories no longer share one visual territory or one photography fallback. Asset count remains question-driven rather than fixed 6/9/12.

## Non-regression
- Complete nine-section Strategy Authority preserved.
- Every activated asset retains `00_asset_manifest.yaml` through `11_strategy_authority_trace.json`.
- Provider Job / Provider Result ingest / Review / Local Revision / Package Hash architecture preserved.
- v0.5.7 baseline paths preserved; final counts are recorded in `BASELINE_AUDIT_AND_V058_NOTES.md` and `BUILD_MANIFEST.json`.
- Regression test count is compatibility evidence only and is not a release-completeness claim.

## Validation boundary
Category execution profiles are strategy recommendations. They cannot create product facts, claims, platform submission rules or unverified photography measurements. Real product truth, verified market/platform evidence and prelight remain authoritative.
