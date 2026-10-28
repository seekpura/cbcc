# v0.5.3 — Portfolio + Localization Depth

## Baseline
Built cumulatively from `v0.5.2-strategy-integration-depth`. No v0.5.2 source file was deleted. The nine-section Strategy Authority, dynamic asset curation, complete per-asset `00–11` package, Provider/Review/Local Revision/Package Hash workflow and Strategy Reasoning Context remain the mainline.

## 1. Competitor Listing × Review intelligence
- Added `competitor_listing_rows` / `market_competitor_listing_rows` ingestion.
- Aggregates observed title/claim, explicit message-theme, offer-type, proof-type, configuration, surface, locale, visual-pattern and source lineage.
- Joins competitor observations with explicit Customer Voice theme labels.
- Exact message-theme × review-theme overlap is emitted only as a research hypothesis, never causal proof.
- Supplemental market evidence can now compile even when a sales/GMV market table is not supplied.
- Strategy Authority Section 3 exposes the competitor intelligence map and its interpretation boundary.
- Positioning records market-tension candidates and competitive message context; own-product differentiation still requires Product Truth fit.

## 2. Multi-SKU / Offer portfolio architecture
- Scenario economics preserves buyer job, target segment, lifecycle stage, offer type, product family, unit count and channel metadata.
- Added pairwise SKU overlap / cannibalization hypotheses using explicit evidence and unknown-input tracking.
- Added Trade-up Architecture; price steps without an explicit value/configuration/job reason are flagged for strategy work rather than dressed up as “premium”.
- Added Lifecycle / Offer Map for acquisition/trial, conversion/AOV and retention/replenishment roles.
- These outputs are integrated into Section 4.1 Product / SKU / Offer Strategy, not left as calculator attachments.

## 3. Transcreation depth
- Listing now compiles `locale × field` Transcreation Tasks from the language contract.
- Each task carries semantic invariants, native adaptation rules, search-intent input and WHY.
- Supplied `_localized_copy` is audited for literal numeric equivalence to reduce size/concentration/quantity drift.
- Transcreation appears in the formal Listing Strategy Authority.

## 4. Platform-native content authoring
- Platform Content Matrix rows now include visible locales, per-locale authoring tasks, beat plans and copy contracts.
- Reuse means shared Strategy/Product Truth, not identical copy across platforms.
- Hook → decision answer → proof/risk reduction → native next action is a content beat contract, not a fixed asset-count template.

## 5. Dynamic Asset tool feedback
- Added `market_theme_fit` as an explicit route from validated market/review evidence into Dynamic Asset Curation.
- Market themes create additional asset jobs only when Product Truth fit is explicitly confirmed/approved.
- This prevents “competitor complaint → invented own-product advantage” while allowing validated insights to alter production.

## 6. Knowledge / Ontology / Prompt runtime
Added and runtime-bound authorities for:
- competitor Listing × Review intelligence,
- SKU portfolio / cannibalization / trade-up,
- transcreation / platform-native authoring.

Ontology adds `CompetitorListingObservation`, `CustomerVoiceTheme`, `CannibalizationHypothesis`, `TradeUpStep`, `LifecycleOfferRole`, and `LocaleAuthoringTask` plus corresponding relations/constraints.

## 7. Validation scope
- Existing regression suite remains green after the changes.
- Added a v0.5.3 integration test covering supplemental competitor research without market rows, multi-SKU overlap/trade-up/lifecycle, multi-locale transcreation, content authoring contracts and Strategy Reasoning Context selection.
- Recompiled the repository KIYUU Malaysia TikTok Shop fixture: nine Strategy Authority sections, dynamic 3-asset portfolio, complete `00–11` for every asset, and en-MY/ms-MY content authoring tasks remain intact.

This is still a development build, not Release Candidate status. Test counts are compatibility evidence only, not a claim of professional completeness.
