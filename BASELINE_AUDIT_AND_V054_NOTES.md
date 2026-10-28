# Baseline Audit + v0.5.4 Development Notes

## Baseline
Unique source baseline for this development pass: `v0.5.3-portfolio-localization-depth`.

This v0.5.4 tree is a cumulative enhancement. It does not intentionally delete the v0.5.3 Strategy Authority, per-asset `00–11` package, Provider/Review/Local Revision/Package Hash flows, platform packs, knowledge/prompt/ontology layers or existing tests.

## v0.5.4 changed code paths
- `runtime/cbcc/tools/market.py` — source-quality/freshness/sampling contracts and opportunity confidence boundary.
- `runtime/cbcc/tools/economics.py` — observed SKU behavior, pair cross-shopping/switching, cohort and treatment/control arithmetic; structural hypothesis → behavior linkage.
- `runtime/cbcc/tools/listing.py` — platform-native Listing profile and Final Copy release workflow.
- `runtime/cbcc/compiler.py` — source-quality inputs, behavioral portfolio inputs, Final Copy artifacts.
- `runtime/cbcc/strategy_depth.py` — formal Strategy Authority integration and platform-native authoring systems.
- `runtime/cbcc/strategy_sources.py` — runtime selection/binding of new knowledge/prompt/ontology authorities.
- `builders/project_delivery_builder.py` — preserve Final Copy artifacts in delivery.

## New professional authorities
Knowledge:
- `knowledge/research_source_quality.md`
- `knowledge/portfolio_behavior_incrementality.md`
- `knowledge/final_copy_release.md`
- `knowledge/platform_native_commerce_systems.md`

Prompts:
- `prompts/research_source_quality.md`
- `prompts/portfolio_behavior_incrementality.md`
- `prompts/final_copy_local_authoring.md`
- `prompts/platform_native_commerce_systems.md`

Test:
- `tests/test_v054_research_behavior_finalcopy.py`

## Important evidence boundaries
- Freshness is thresholded only against explicit `max_age_days`.
- Representativeness is never inferred from row count/sample size.
- Cross-shopping/switch/cohort patterns are descriptive, not causal cannibalization.
- Treatment/control lift is arithmetic until experiment design/statistics are reviewed.
- Native fluency/claim equivalence/platform fit/culture fit are explicit review authorities; deterministic runtime does not fake language judgment.
- Final Copy requires both authored text and review approval.

## Validation meaning
Regression tests only show that old contracts were not obviously broken by this pass. They are not evidence that the strategy system is professionally complete or Release Candidate-ready.

## Source-tree continuity check
Compared against the uploaded `cross-border-commerce-creative-v0.5.3-portfolio-localization-depth.zip` by relative path after excluding build/test caches:
- baseline source files: **346**
- baseline paths missing from v0.5.4: **0**
- current source files before final manifest regeneration: **357**
- newly added paths: **11**

The 11 additions are the v0.5.4 audit/changelog, four professional knowledge authorities, four professional prompt authorities, and the v0.5.4 integration test. Existing files were enhanced in place; no baseline path was removed to make the package smaller.

## KIYUU continuity recompilation
The repository KIYUU Malaysia TikTok Shop fixture was recompiled under v0.5.4 and then passed through the Project Delivery Builder.

Observed delivery structure:
- formal Strategy Authority sections: **9**
- dynamic assets selected by the fixture: **3**
- all 3 activated asset packages contain the full required `00_asset_manifest.yaml` through `11_strategy_authority_trace.json`: **yes**
- Review Workspace preserved in Delivery: **yes**
- Listing Final Copy layer preserved in Delivery: **yes** (`en-MY.md`, `ms-MY.md`)
- `PRODUCTION`: **PENDING**; no Provider Result was fabricated for the planning/review fixture

Final Copy status is intentionally not overstated: the fixture supplies English source/draft copy but no explicit professional review and no authored Bahasa Melayu copy. Therefore release counts are `DRAFT_REVIEW_REQUIRED: 2` and `TO_AUTHOR: 2`, with no `APPROVED_FINAL` item.

## Compatibility execution
Repository regression/integration execution after the v0.5.4 changes: **65 passed**. This is recorded only as a compatibility/non-regression signal; it is not used as evidence that strategy quality is complete or that the build is Release Candidate-ready.
