# Baseline Audit and v0.5.8 Notes

## Unique baseline
The only source baseline for this increment is:
`cross-border-commerce-creative-v0.5.7-adapter-cursor-causal-terminology-provider-prelight-depth.zip`

Historical packages remain construction history and are not restart points.

## Baseline preservation
- v0.5.7 baseline files: **396**
- baseline paths preserved in v0.5.8: **396 / 396**
- missing baseline paths: **0**
- v0.5.8 final source files: **407**
- additive paths versus v0.5.7: **11**

Added paths:
- `BASELINE_AUDIT_AND_V058_NOTES.md`
- `CHANGELOG_V058.md`
- `MULTICATEGORY_VALIDATION_V058.md`
- `knowledge/multicategory_category_specificity.md`
- `prompts/multicategory_strategy_debias.md`
- `runtime/cbcc/category_strategy.py`
- `tests/fixtures/v058_multicategory/README.md`
- `tests/fixtures/v058_multicategory/beauty_kiyuu.json`
- `tests/fixtures/v058_multicategory/fashion_uniqlo_bag.json`
- `tests/fixtures/v058_multicategory/home_ikea365_container.json`
- `tests/test_v058_multicategory_strategy_validation.py`

## What this release validates
v0.5.8 is a multi-category specificity increment, not a Gate-count increment. It tests whether one runtime can change strategy, asset curation, surfaces, visual territory and photography reasoning when the consumer decision and product category change.

The validation set uses:
- beauty/personal care,
- fashion/accessory,
- home-durable food storage.

The non-KIYUU fixtures use public official product facts as stress-test inputs and do not assert that those products are sold through the selected validation target channel.

## Real defects fixed
1. Platform verification authority was able to suppress unverified strategic surfaces.
2. Generic photography fallback produced cross-category visual homogenization.
3. Purchase-decision intent classification was too beauty/generic.
4. Auto-curated question merging was lexical rather than semantic.
5. Textile/fabric CMF needed material-specific lighting treatment.

## Result
- Beauty: 4 assets.
- Fashion/accessory: 5 assets.
- Home durable: 6 assets.
- Fashion wear/adjustment duplication merged to one `FIT_WEAR` job.
- Home capacity duplication merged to one `SIZE_CAPACITY` job.
- All activated asset packages remain complete `00–11`.
- Category-specificity Knowledge/Prompt/Ontology authorities are consumed by Runtime.

## Compatibility evidence
The repository regression suite is required to remain clean after the increment. Test counts are recorded only as compatibility evidence and must not be interpreted as professional-system completion.
