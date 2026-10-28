# v0.5.1 Strategy Depth

This build deepens the user-facing strategy rather than adding more gates.

- Preserves the complete alpha6/v0.5 per-asset package (`00`–`10`) and `11_strategy_authority_trace.json`.
- Adds shopper barrier / belief target / entry-exit state / RACE / success metric to dynamic assets.
- Replaces generic nine-section strategy scaffolding with professional decision depth.
- Adds Market → Strategy interpretation, SKU/Offer confidence logic, Positioning/Message architecture, Listing/Search decision architecture, platform-native content logic, visual/photography WHY, dynamic asset portfolio review and measurement/feedback routing.
- Integrates Ads and Feedback outputs into the final strategy rather than leaving them as sidecar calculations.
- Expands Prompt Registry and Knowledge Layer with domain-specific authoring authorities.
- Adds multi-campaign advertising portfolio analysis, Listing keyword coverage/repetition audit and Feedback source/severity matrices.

## Strategy-depth closure
- Added executive decision summary at the top of the human strategy report.
- RACE execution now compiles per target platform/site rather than only the primary platform.
- Added `STRATEGY_DECISION_INDEX.json` and `EXECUTIVE_SUMMARY.json`.
- Narrowed each asset `11_strategy_authority_trace.json` to relevant upstream decisions instead of copying whole strategy sections.
- Expanded `templates/project_input.md` to expose market files, economics, listing, ads/feedback, full photography/CMF, multi-platform targets, dynamic assets and professional annotations.
- Preserved the existing per-asset 00–10 package and additive 11 trace.

## Knowledge/prompt/tool integration closure
- `knowledge/`, `ontology/commerce_ontology.json` and `prompts/registry.json` are now consumed by runtime through `strategy_reasoning_context.json` instead of remaining passive files.
- Added dedicated prompt authorities for truth/value translation, unit-economics offer strategy, advertising diagnosis and feedback/revision routing.
- Fixed single-SKU role rationale so supplied market/economics evidence is reflected instead of still claiming it is missing.
- Advertising portfolio aggregate metrics, break-even economics and CPA headroom now feed the human strategy report.
- Unit economics now exposes contribution-before-ads, break-even ROAS, shared growth budget pool, current growth spend and remaining pool.
- Professional annotations now keep Executive Summary and decision index synchronized.
