# Baseline Audit and v0.5.9 Notes

## Baseline authority

The only source baseline for this release is `cross-border-commerce-creative-v0.5.8-multicategory-strategy-specificity-depth.zip`. Earlier versions are historical construction nodes.

## Non-regression result

- v0.5.8 baseline files: **407**
- v0.5.8 paths preserved in v0.5.9: **407 / 407**
- missing baseline paths: **0**
- v0.5.9 total files after release-document additions: **418**
- additive paths: **11**

The release is cumulative. Existing Strategy Authority, per-asset `00–11`, Provider Job/Result architecture, Review, Local Revision, Package Hash, Source Adapter, causal analysis, Final Copy, terminology, prelight and multi-category visual/asset specificity are not removed.

## Additive paths

- `CHANGELOG_V059.md`
- `CATEGORY_COMMERCE_VALIDATION_V059.md`
- `BASELINE_AUDIT_AND_V059_NOTES.md`
- `knowledge/category_commerce_depth.md`
- `prompts/category_commerce_strategy_debias.md`
- `tests/fixtures/v059_category_commerce/README.md`
- `tests/fixtures/v059_category_commerce/apparel_tshirt.json`
- `tests/fixtures/v059_category_commerce/electronics_powerbank.json`
- `tests/fixtures/v059_category_commerce/food_tea.json`
- `tests/fixtures/v059_category_commerce/high_ticket_aircon.json`
- `tests/test_v059_category_commerce_depth.py`

## Primary modified baseline paths

- `VERSION`, `README.md`, `SKILL.md`, `CHANGELOG.md`, `CURRENT_HANDOFF.md`, `BUILD_MANIFEST.json`
- `knowledge/registry.json`, `prompts/registry.json`, `ontology/commerce_ontology.json`
- `runtime/cbcc/category_strategy.py`
- `runtime/cbcc/strategy_depth.py`
- `runtime/cbcc/strategy_sources.py`
- `runtime/cbcc/compiler.py`, `runtime/cbcc/state.py`
- historical compatibility tests whose version-prefix assertions now accept the current cumulative runtime.

## v0.5.9 focus

v0.5.9 deliberately targets category-commerce homogenization rather than adding more governance. It makes Listing objections, proof order, offer hypotheses, message sequence and content cadence category-aware while keeping all category-derived recommendations subordinate to Product Truth, actual service/policy capability, platform evidence and economics.

## Validation boundary

The four new fixtures are structured stress inputs and do not claim current marketplace availability or live performance. The compatibility test total is non-regression evidence only and is not a claim that the system is complete or Release Candidate ready.
