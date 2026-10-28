# v0.5.4 — Research + Behavior + Final Copy Depth

## Baseline
Built cumulatively from `v0.5.3-portfolio-localization-depth`. No v0.5.3 source path is intentionally deleted. The nine-section Strategy Authority, complete dynamic per-asset `00–11` package, Provider/Review/Local Revision/Package Hash continuity, and runtime-consumed Knowledge/Ontology/Prompt layers remain the mainline.

## 1. Research source quality / freshness / representativeness
- Added `market_source_records`, `market_research_as_of`, and `market_research_scope` support.
- Market / keyword / review / competitor-listing datasets now report row-level source-ID coverage and source resolution.
- Source records can carry `observed_at|collected_at|verified_at`, `max_age_days`, market/site/platform/category scope, population scope, sample frame, sampling method, inclusion/exclusion criteria and coverage notes.
- Freshness is judged only against an explicitly supplied `max_age_days`; without a declared threshold, runtime records age but does not invent a stale/fresh boundary.
- Representativeness is never inferred from sample size or source prestige. Runtime records whether sampling metadata is documented and keeps the conclusion boundary explicit.
- Scope mismatch, unresolved source IDs and sources outside the declared freshness window now appear in Strategy Authority and risk planning.
- Opportunity confidence is no longer allowed to look “HIGH” from row completeness alone when source/sampling evidence is weak.

## 2. Behavioral SKU / Offer validation
- Added portfolio-level behavioral inputs under `offer_economics`:
  - `behavior_rows | portfolio_behavior_rows`
  - `pair_behavior_rows | portfolio_pair_rows`
  - `cohort_rows | portfolio_cohort_rows`
  - `incrementality_rows | portfolio_incrementality_rows`
- SKU behavior aggregates visitors/clicks/orders/new/repeat customers/revenue/contribution and descriptive rates.
- Pair behavior records cross-shopping/shared visitors, switch counts and paired/exclusive orders without converting them into invented cannibalization percentages.
- Cohort rows calculate descriptive repeat and contribution-per-acquired-customer metrics only within the supplied cohort definition/window.
- Treatment/control rows calculate arithmetic conversion/contribution lift while preserving whether randomization was declared and explicitly requiring statistical/causal review.
- Existing structural overlap hypotheses are now linked to observed pair behavior so Strategy Authority can distinguish `HYPOTHESIS_AWAITING_BEHAVIORAL_VALIDATION` from `BEHAVIORAL_EVIDENCE_AVAILABLE`.

## 3. Local-language Final Copy release workflow
- Transcreation tasks remain the authoring plan, but localized strings no longer become “final” merely because text exists.
- Added `_localized_copy_reviews` contract with explicit review dimensions:
  - `native_fluency`
  - `claim_equivalence`
  - `platform_fit`
  - `culture_fit`
  - `decision`
- Runtime performs deterministic hard checks such as literal numeric equivalence and field/title constraints.
- Final release state requires authored target copy + hard-check pass + explicit approval of all four professional review dimensions.
- Output states include `TO_AUTHOR`, `DRAFT_REVIEW_REQUIRED`, `REVISION_OR_REVIEW_REQUIRED`, `BLOCKED_HARD_CONSTRAINT`, and `APPROVED_FINAL`.
- Added `artifacts/listing_final_copy.json` and per-locale human-readable files under `artifacts/listing_final_copy/`.
- Project Delivery Builder now preserves Final Copy artifacts as a first-class delivery layer.

## 4. Platform-native commerce authoring systems
Strategy Authority now emits explicit platform-native authoring systems rather than one generic “localize for platform” note:
- `TIKTOK_SHOP_NATIVE_COMMERCE`
- `SHOPEE_COMPARISON_COMMERCE`
- `AMAZON_SEARCH_PROOF_SYSTEM`
- `DTC_MODULAR_PDP_LIFECYCLE`

Each system specifies entry logic, hook logic, message sequence, copy density, creator/UGC role, offer logic, measurement and WHY. Reuse means shared Product Truth / Positioning / Message Hierarchy / evidence, not identical copy or beat order.

## 5. Runtime-consumed Knowledge / Ontology / Prompt additions
New knowledge authorities:
- Research Source Quality / Freshness / Representativeness
- Portfolio Behavior / Cohort / Incrementality
- Local-language Final Copy Release
- Platform-native Commerce Authoring Systems

New prompt authorities:
- `PROMPT-RESEARCH-QUALITY`
- `PROMPT-PORTFOLIO-BEHAVIOR`
- `PROMPT-FINAL-COPY`
- `PROMPT-PLATFORM-NATIVE-SYSTEMS`

Ontology adds research dataset/source-quality, behavioral/cohort observations, portfolio incrementality evidence, Final Copy / Copy Review and Native Authoring System objects and constraints.

## 6. Strategy Authority integration
- Section 3 exposes source/freshness/representativeness contracts and their strategic implication.
- Section 4.1 exposes portfolio behavior/cohort/incrementality evidence alongside structural cannibalization hypotheses.
- Section 4.3 exposes native platform Listing profile and field-level Final Copy release state.
- Section 6 includes platform-specific native authoring systems per content row.
- Section 9 carries portfolio behavior/incrementality learning and source-quality risks into the measurement / next-action layer.

## 7. Compatibility / validation scope
- Existing v0.5.3 contracts remain backward-compatible: new function arguments are optional and old deterministic entry points continue to work.
- Existing per-asset `00–11` contract is unchanged.
- Regression tests are compatibility evidence only, not a claim that professional strategy depth is complete.
- Added a v0.5.4 integration test covering source freshness/sampling boundaries, behavioral SKU validation, Final Copy approval and TikTok/Shopee/Amazon/DTC native systems.

This remains a development build, not Release Candidate status.

## 8. Real fixture continuity check
The KIYUU Malaysia TikTok Shop fixture was recompiled after the v0.5.4 integration work. It retained 9 formal Strategy Authority sections and selected 3 dynamic assets based on the fixture's actual decision jobs; every activated asset retained the full `00–11` package. Delivery also preserved Review Workspace and the new locale Final Copy layer. Production remained `PENDING`; no provider execution/result was fabricated. Because the fixture does not supply native-language review/approval, its Final Copy artifacts remain `DRAFT_REVIEW_REQUIRED` / `TO_AUTHOR` rather than being falsely promoted to `APPROVED_FINAL`.
