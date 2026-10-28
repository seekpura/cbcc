# CHANGELOG — v0.5.9 Category Commerce Depth

## Purpose

v0.5.8 proved that asset curation, visual territory and photography could diverge across categories. v0.5.9 targets the next real homogenization risk: the commercial strategy itself was still too generic across categories.

## Runtime changes

### Category commerce profile
Added `category_commerce_profile(request)` with category-specific:
- objection priorities;
- proof hierarchy;
- offer architecture hypotheses;
- message architecture;
- content cadence;
- explicit truth boundary.

Profiles now cover beauty/personal care, apparel fit, fashion accessory, food/beverage, electronics, home durable, high-ticket durable and general commerce fallback.

### Consumer decision intents
Added or deepened deterministic intents for `SIZE_FIT`, `SITE_FIT`, `INGREDIENT_DIETARY`, `SENSORY_PREP`, `PERFORMANCE_PROOF`, `WARRANTY_SERVICE`, `DELIVERY_INSTALLATION` and `TOTAL_COST_OWNERSHIP`.

Intent matching now uses controlled word-boundary/phrase matching for ASCII terms so substrings cannot manufacture false intent.

### Listing / Positioning / Message
Formal Strategy Authority now exposes:
- category objection checks;
- category proof hierarchy;
- category message architecture;
- category-specific PDP sequence;
- generic belief sequence retained only as compatibility reference.

### Offer strategy
SKU/Product strategy now carries category offer architecture with status `CATEGORY_OFFER_HYPOTHESES_REQUIRE_ECONOMICS_AND_PRODUCT_FIT`. Category patterns can suggest what to test, but they cannot create service, financing, discount, bundle or return facts. Economics and real capability remain required before locking an offer.

### Platform content cadence
Section 6 now carries category message sequence, category proof hierarchy, category-specific script structure, cadence model and cadence role. Cadence is defined as information-module rotation + refresh triggers; `fixed_posting_frequency` remains false unless an external factual plan explicitly supplies one.

## Runtime authority
Added:
- `knowledge/category_commerce_depth.md`
- `prompts/category_commerce_strategy_debias.md`
- `KNOW-CATEGORY-COMMERCE-DEPTH`
- `PROMPT-CATEGORY-COMMERCE-DEPTH`
- ontology entities `CategoryCommerceProfile`, `ObjectionPriority`, `ProofHierarchy`, `OfferArchitecture`, `ContentCadence` plus relations/constraint.

These authorities are selected by `strategy_reasoning_context.json` and bound to formal Strategy Authority sections; they are not passive documentation.

## Validation
Added structured stress fixtures for:
- food/beverage;
- electronics;
- apparel sizing/fit;
- high-ticket durable.

The validation asserts real differences in objection priorities, top proof, message sequences, offer boundaries, cadence models and decision-intent assets while keeping every asset package complete `00–11`.

## Non-regression principle
This release is cumulative. It does not remove v0.5.8 multi-category visual/asset specificity or any earlier Source Adapter, causal, Final Copy, Provider binding, Review, Local Revision or Package Hash chain. Test counts are compatibility evidence only and are not a claim of professional completeness.
