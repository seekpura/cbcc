# Changelog

## 0.6.11 — Source Master Binding + Frozen Revision Enforcement
- Added machine-readable source-product bindings to Renderer Recipe and Provider Job, including resolver/locator, SHA256, pixel lock, allowed transforms and identity features.
- Re-verified local product-master existence and SHA256 at provider handoff instead of trusting compile-time ingest state.
- Required LOCKED_PIXEL result lineage for source asset IDs + SHA256 and bound results to a `source_binding_hash`.
- Enforced frozen-layer mutation reporting and revision changed-layer scope.
- Extended source-binding requirements to every LOCKED_PIXEL provider mode, including graphic-design placement workflows.
- Real KIYUU three-asset provider run verified 3/3 jobs bind the same verified source master.
- Focused v0.6.7–v0.6.11 regression: 18 passed. Full suite: 107 passed / 12 existing failures.
- See `CHANGELOG_V0611.md`.

## 0.6.10 — Visual Execution + Locked Copy Continuity
- Propagated approved visual elements, precision boundaries, editable/frozen layers and product-fidelity mode into CN/EN Render Prompts and the human Visual production workspace.
- Routed structured `information_design.locked_visible_copy` into the human Copy workspace instead of relying on legacy copy fields or Markdown fallback.
- Removed exact locked visible copy from renderer-facing Surface / Copy Budget JSON while preserving deterministic copy overlay and human review visibility.
- Added Parameter Trace coverage for Visual Execution Boundaries / Editability and real KIYUU three-asset regression coverage.
- Full suite: 103 passed / 12 remaining failures; no v0.6.9 passing test regressed, and one prior provider-quality preflight failure now passes with the richer execution trace.
- See `CHANGELOG_V0610.md`.

## 0.6.9 — Photography Execution Continuity
- Preserved explicit capture/composite mode, complete composition execution data, and output color-management contract in each Design Card.
- Propagated that contract into CN/EN Canonical Prompts, Parameter Trace, Machine Visual Contract, and the human Photography / CMF production workspace.
- Removed composition-field whitelist fragility: future execution keys such as negative-space or subject-clearance survive without compiler-specific registration.
- Locked the continuity with the real KIYUU Malaysia TikTok fixture and a future-field regression case.
- Full suite: 100 passed / 13 pre-existing baseline failures; no new failures.
- See `CHANGELOG_V069.md`.

## 0.6.8 — Asset Production Workspace
- Replaced the generic per-asset `module-shell` with a production-decision workspace.
- Dynamically groups asset content into Design Card / decision, visual execution, photography / CMF, copy, Prompt execution, and QA / source trace.
- CN and EN / target-model Canonical Prompts now share one execution console instead of becoming separate document tabs.
- Legacy / unknown asset views fall back into QA for lossless compatibility.
- Added real KIYUU HTML compile verification and dedicated asset-workspace regression coverage.
- See `CHANGELOG_V068.md`.

## 0.6.0 — Capability-Complete Rebase
- Rebased the active creative-production mainline around capability completion rather than additional validation wrappers.
- Corrected Campaign RACE semantics to PLAN → Reach → Act → Convert → Engage and propagated stage assignment to decision-specific assets.
- Added a 6–12 mechanism Creative Opportunity Universe followed by 3–5 current-product Direction Synthesis / Council; route IDs remain downstream compatibility tags rather than a fixed visual-style library.
- Added Product Visual Intelligence plus dynamic Foundation / Creative Anchor planning.
- Added Dynamic Surface Architecture, Information Assetization, deliberate Product Presence and Surface Copy Budget.
- Expanded content families to Rich Content, Live, Social, Store and Lifecycle while preserving exact platform capability/research boundaries.
- Added decision-specific Visual Expression Variants to prevent same-layout collapse under one design system.
- Replaced thin prompt summaries with complete per-asset Design Cards and canonical Chinese/English production prompts.
- Added `12_design_card.json` and `13_prompt_contract.json` while preserving the canonical `00–11` package.
- Provider Jobs now inherit Canonical Prompt Contract, Renderer Recipe and QA Target.
- Added independent Paid Campaign Architecture and deeper Creator / Video / Live execution contracts.
- Preserved prior Market/Competitor/Search, SKU/Economics, Listing/Final Copy, Platform/Locale, Evidence, real-product master fidelity, Review, Local Revision and Learning systems.
- See `CHANGELOG_V060.md` and `CAPABILITY_COMPLETE_REBASE_V060.md`.


## 0.5.14 — Real Production Quality Preflight
- Added exact source-product-master binding and hash lineage; missing LOCKED_PIXEL masters now hold real-product handoff.
- Added decision-specific visual production signatures plus editable/frozen production layers.
- Upgraded Provider Jobs with executable product-lock, surface, copy-visual and Photography/CMF quality contracts.
- Upgraded Provider Results from generic QA booleans to evidence-bearing production observations.
- Enforced semantic Local Revision scope and routed production failures to the smallest visual execution learning layer.
- Preserved Strategy / Listing / dynamic assets / full `00–11` / Provider → Review → Local Revision → Learning continuity.
- Pre-RC: live external real-product image/video quality still requires actual product masters and Provider outputs.
- See `CHANGELOG_V0514.md` and `REAL_PRODUCTION_PREFLIGHT_V0514.md`.

## 0.5.13 — Real Product Strategy Quality Depth
- Real-product blind validation across beauty/electronics/fashion/home durable.
- Atomic decision-question preservation from shopper question → Strategy → Listing → Asset.
- Topic-specific Proof Contracts and missing-economics Offer boundary fix.
- Explicit Host Strategy Authoring Request with protected deterministic authorities.
- Field-level approved-Claim numeric authority for Final Copy without weakening untraced numeric drift blocking.
- See `CHANGELOG_V0513.md` and `REAL_PRODUCT_QUALITY_VALIDATION_V0513.md`.

## 0.5.12-production-learning-loop-depth
- Completed executable Provider Result → Review → scope-limited Local Revision → revised-output re-review → post-change Learning loop.
- Parent asset packages remain immutable; revision lineage retains parent package hash and independent revised-output hash.
- Added bounded Strategy Authority Learning Ledger/local overlays with explicit causal-credit boundary.
- Added loop visibility and Delivery preservation. See `CHANGELOG_V0512.md`.

## 0.5.11-integration-quality-depth
- Audited actual capability wiring instead of using file/test counts as completion evidence.
- Added quality-weighted evidence reconciliation, Market Evidence → Product Truth Fit contracts, and Ads/Feedback Strategy Revision Routing.
- Added runtime `capability_integration_map.json` and included integration artifacts in Delivery.
- Unified legacy root calculators behind canonical Runtime engines while retaining old CLI entrypoints.
- Stabilized historical Knowledge Authority IDs.
- See `CHANGELOG_V0511.md` and `INTEGRATION_AUDIT_V0511.md`.

## 0.5.10-evidence-commerce-reconciliation-depth
- Reframed Category Commerce profiles as priors and added deterministic reconciliation against Product Truth, own shopper/behavior evidence and current scoped market/search/review/competitor evidence.
- Added evidence-priority, category-prior conflict trace, effective objection/proof/message sequencing and proof evidence-condition outputs.
- Added descriptive promo-response, bundle-affinity and repeat/replacement-cycle analysis to Offer Strategy with explicit non-causal/test-candidate boundaries.
- Added platform × category intersection logic for TikTok Shop, Shopee, Amazon and DTC without changing the underlying Product Truth/evidence priority.
- Fixed cross-category intent contamination where generic `prepare` language could outrank delivery/installation intent.
- Added runtime-consumed Category Evidence Reconciliation and Offer Response Evidence Knowledge/Prompt/Ontology authorities.
- Added category-conflict and same-product cross-platform stress validation.
- Preserved nine-section Strategy Authority, dynamic assets, complete `00–11`, Provider/Review/Local Revision/Package Hash continuity.
- See `CHANGELOG_V0510.md` and `EVIDENCE_COMMERCE_VALIDATION_V0510.md`.


## 0.5.9-category-commerce-depth
- Extended category specificity into Listing objection architecture, proof hierarchy, category offer hypotheses, message architecture and content cadence.
- Added apparel-fit and high-ticket-durable category families plus new decision intents for ingredient/dietary, sensory/prep, performance, site fit, delivery/install, service/warranty and total-cost questions.
- Added category-aware PDP sequence and platform content script structures while retaining the generic belief sequence as compatibility reference.
- Added category offer architecture with explicit Product Truth / economics / service-capability boundaries; category patterns do not become locked offers automatically.
- Added category cadence models based on information-module rotation and refresh triggers, never arbitrary fixed posting frequency.
- Replaced risky substring intent matching with word-boundary / phrase matching for controlled deterministic fallbacks.
- Added runtime-consumed Category Commerce Knowledge/Prompt/Ontology authority and four-category validation fixtures/tests.
- Preserved nine-section Strategy Authority, dynamic assets, complete `00–11`, Provider/Review/Local Revision/Package Hash continuity.
- See `CHANGELOG_V059.md` and `CATEGORY_COMMERCE_VALIDATION_V059.md`.

## 0.5.8-multicategory-strategy-specificity-depth
- Added real beauty / fashion-accessory / home-durable validation fixtures and a category-specific runtime integration test.
- Added category-family execution profiles and decision-intent classification for dynamic asset curation.
- Added semantic decision-intent question merging while preserving explicit authored asset jobs.
- Fixed platform-pack capability governance so unsupported/unverified surfaces remain strategy-planning candidates with research-required status instead of being censored from the content graph.
- Added category-specific visual territory, photography-plan fallbacks and material-aware lighting guidance when no explicit photography contract is supplied.
- Added textile/fabric CMF lighting reasoning and strategy-derived photography contracts that remain explicitly provisional until prelight.
- Added runtime-consumed multi-category-specificity knowledge/prompt/ontology authority.
- Preserved nine Strategy Authority sections, dynamic asset curation, complete per-asset `00–11`, Provider/Review/Local Revision/Package Hash continuity.
- See `CHANGELOG_V058.md`.

## 0.5.7-adapter-cursor-causal-terminology-provider-prelight-depth
- Added marketplace/search/review/market adapter-family cursor/checkpoint resumability metadata.
- Added cluster/geo/CUPED/sequential causal-design diagnostics with explicit inference boundaries.
- Added locale terminology memory and cross-field Final Copy consistency auditing.
- Bound platform-pack Surface Production Contracts and photography/layout hashes into Provider Jobs.
- Added prelight/test-shot, lighting diagram, measured exposure-ratio, polarization and cross-shot color-consistency plans.
- Preserved nine Strategy Authority sections, dynamic asset curation, complete per-asset `00–11`, Provider/Review/Local Revision/Package Hash continuity.

## 0.5.6-adapter-causal-copy-production-cmf-depth
- Added source-adapter normalization and incremental refresh with primary-key change sets, high-watermarks, source-record injection and review-only semantic-near-duplicate detection.
- Added experiment-design readiness: assignment/randomization, pre-period balance, MDE/power planning, contamination/spillover/interference review and segmented exploratory summaries.
- Extended holdout marginal contribution with segment/cohort/period preservation and arithmetic rollups with explicit causal limits.
- Added Host/model Final Copy author→revise→re-review orchestration with version-bound review staleness and separate generation/release authority.
- Added platform-surface production contracts and propagated them into activated asset `04_layout_contract.json` / `09_production_notes.md`.
- Added CMF/material-specific shot-level lighting reasoning and propagated it into asset visual/photography contracts.
- Added runtime-consumed source-adapter, causal-experiment, Host-copy, surface-production and CMF-lighting knowledge/prompt/ontology authorities.
- Preserved nine-section Strategy Authority, dynamic asset count, complete `00–11`, Provider/Review/Local Revision/Package Hash continuity.
- See `CHANGELOG_V056.md`.

## 0.5.5-evidence-incrementality-authoring-surface-depth
- Added `runtime/cbcc/tools/evidence.py` for exact same-source fingerprints, opt-in exact dedup, cross-source duplicate review, entity version/conflict review and source lineage.
- Market analysis now consumes research-ingestion outputs while preserving report-only behavior unless exact dedup is explicitly enabled.
- Added directional SKU switch matrices with explicit-denominator requirements, cohort comparability metadata review, and holdout net marginal-contribution arithmetic with causal-design boundaries.
- Added version-aware localized-copy history and stale-review detection; older approvals never release a revised current version.
- Materialized authoring / revision / review task artifacts for the Final Copy loop and included them in Delivery supporting analysis.
- Added surface-level native authoring contracts underneath TikTok Shop / Shopee / Amazon / DTC platform systems.
- Added asset-level photography causal WHY and copied it into every applicable asset `02_visual_spec.md` / `03_photography_contract.json`.
- Added runtime-consumed evidence-ingestion, marginal-contribution, copy-iteration and asset-photography knowledge/prompt/ontology authorities.
- Preserved nine-section Strategy Authority, dynamic asset count, complete `00–11`, Provider/Review/Local Revision/Package Hash continuity.
- See `CHANGELOG_V055.md`.

## 0.5.4-research-behavior-finalcopy-depth
- Added source freshness/scope/sampling contracts and source-quality-aware market interpretation.
- Added observed SKU behavior, pair cross-shopping/switching, cohort and treatment/control portfolio validation.
- Added explicit local-language Final Copy release workflow and per-locale delivery artifacts.
- Added TikTok Shop / Shopee / Amazon / DTC platform-native commerce authoring systems.
- Added runtime-bound research-quality, portfolio-behavior, Final-Copy and platform-native knowledge/prompt/ontology authorities.
- Preserved nine-section Strategy Authority, dynamic asset count, complete `00–11`, Provider/Review/Local Revision/Hash continuity.
- See `CHANGELOG_V054.md`.

## 0.5.3-portfolio-localization-depth
- Added source-bounded Competitor Listing × Review intelligence and allowed supplemental market evidence without a sales table.
- Added multi-SKU overlap/cannibalization hypotheses, trade-up justification and lifecycle/offer architecture.
- Added locale × field transcreation tasks, localized numeric-equivalence review and platform-native authoring contracts.
- Added explicit Product-Truth-fit market-theme routing into Dynamic Asset Curation.
- Added runtime-bound competitor/portfolio/transcreation knowledge, prompts and ontology entities.
- Preserved nine-section Strategy Authority, dynamic asset count, complete `00–11`, Provider/Review/Local Revision/Hash continuity.
- See `CHANGELOG_V053.md`.

## 0.5.2-strategy-integration-depth
- Deepened Market/Competitor/Search, SKU/Offer/Economics, Positioning/Message, Listing, Visual/Photography WHY, Platform Content and Dynamic Asset Curation.
- Added content-level Knowledge/Ontology/Prompt runtime consumption and Strategy Authority bindings.
- Hardened the complete per-asset `00–11` package while preserving Provider/Review/Local Revision/Package Hash continuity.
- See `CHANGELOG_V052.md` for detailed changes.

## 0.5.0-strategy-rebase
- Rebased the product around positive-first professional strategy authoring.
- Added nine-part Strategy Authority output and WHY decision contract.
- Added Product/SKU strategy, Positioning, Value Proposition and Message Hierarchy runtime.
- Added knowledge, ontology and prompt-registry layers.
- Deepened Market/Economics/Listing/Ads/Feedback engines and market file intake.
- Strategy now continues when only exact submission rules remain unresolved.
- Preserved alpha6 asset package files, Provider/Review/Local Revision flows; added upstream strategy trace to each asset.


## v0.6.3 — Complete Commerce Editorial HTML Delivery
- `index.html` is now the complete formal human deliverable rather than a navigation shell.
- Full strategy/listing/content/visual/source documents are rendered directly in HTML.
- Every asset keeps an inline full Design Card and CN/EN Canonical Prompt; no Markdown click is required to read them.
- Added project-wide search, copy controls, expandable asset contracts, source visual gallery, CMF-aware visual theme, responsive desktop/mobile design and print/PDF styles.
- Markdown/JSON remain editable/machine sources and are no longer the required reading path.
