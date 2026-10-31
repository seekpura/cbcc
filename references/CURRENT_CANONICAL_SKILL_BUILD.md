# CBCC Current Canonical Skill Build Authority

## Current rule
The canonical packaged Skill is built additively from the last verified mature Skill floor plus current authorities. `CURRENT` never means “whatever the latest source file happens to say”; VERSION, current builder, packaged override family, top/deep Skill and final ZIP proof must converge on one release family.

For current **v0.6.73**, `scripts/build_plugin_dist_v0673.py` calls the v0.6.72 canonical builder. The v0.6.72 Skill is an exact frozen floor:
- UTF-8 bytes: `64023`;
- SHA256: `1ad5fcc7809daa72afcebfe2db452d4bc83a7a913b1d78da9ce0794bf5e319dc`;
- required markers include `0.21 Fresh K01 Runtime Projection Closure`, `0.20 Full Canonical Human + Package Lineage Parity`, `0.19 Canonical Materialization + Human Projection Parity`, and the FULL-depth authority marker.

The earlier immutable provenance remains underneath it: v0.6.69 exact maturity floor (`48517` bytes / SHA256 `f3ed58aafc24947e85fc268144ea787d4db5eaed66b31008f6a5cf87500cbd54`) → v0.6.70 semantic/prompt/Human parity floor → v0.6.71 real final-package/Human/00–15 lineage floor → v0.6.72 fresh-K01 Runtime projection closure → v0.6.73 bilingual business-object/model-prompt consumption closure. v0.6.73 is additive, not a rebase.

## Stable construction contract
1. `VERSION` identifies the current semantic release family and full authority version.
2. `scripts/build_plugin_dist_current.py.CURRENT_BUILDER_TARGET` must equal that family.
3. `references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json.current_release_version` must equal that family in repository and final ZIP.
4. The release builder must verify the previous exact Skill floor before adding current authority.
5. Current GitHub resources are copied from the current release head; historical versioned builders remain provenance/regression evidence.
6. Canonical Skill is written byte-identically to packaged top `SKILL.md` and `resources/SKILL.md`.
7. Manifest, both Skills, `resources/VERSION`, CURRENT override and CURRENT builder target belong to one family.
8. `scripts/check_current_release_package.py` plus every cumulative version checker validate the exact built ZIP before installation.
9. CI records exact ZIP SHA256 + bytes and uploads that exact artifact; installation may use only that verified artifact.
10. Installed plugin parity and active Host Skill snapshot parity remain separate evidence.

## v0.6.73 Bilingual Business-Object Delivery + Model Prompt Consumption Closure
This release is driven by a fresh 20-asset K01 FULL run through the installed v0.6.72 authority. It does not weaken any v0.6.70/v0.6.71/v0.6.72 guard. It closes four downstream consumer defects that only appeared when rich bilingual canonical objects were exercised end-to-end.

- `asset_compiler.py` preserves structured bilingual canonical values such as `{cn,en}` in machine objects. Human guidance selects Chinese-first display text only at the rendering boundary. Semantic comparisons flatten textual leaves without destroying the canonical object.
- `human_language_delivery.py` recognizes mature Listing fields `selling_points`, `specification` and `key_ingredients` with semantic Chinese labels. Compound measurement strings such as `30 g / 1.01 oz` are language-neutral only when alphabetic tokens are known measurement units; ordinary foreign prose still requires Chinese companion text.
- `video_creator.py` retains shopper questions as internal decision objects but prefers already-authored Visible Copy for the human-facing Hook when no explicit video-job Hook exists. Authored Chinese meaning is preserved; missing custom Chinese is never machine-invented.
- `model_native_prompt_contract.py` normalizes `MODEL_RENDER_INTEGRATED` and equivalent aliases to `MODEL_RENDER`, recursively resolves nested bilingual execution objects by language, and keeps relevance decisions such as `props.status=NOT_NEEDED` in Human/Design Card authority without leaking them into model prompts or generating false missing-consumption findings.

## Fresh K01 positive evidence
The v0.6.73 fresh K01 run uses `KIYUU_5款产品信息_纯粹版(7).xlsx` as product truth and a 20-asset portfolio with named Art Direction. Before release, the same candidate Runtime must prove:
- `PROMPT_CONSUMPTION_AUDIT = READY` and every production asset has `missing_decisions = []`;
- Human Language Audit, Delivery Language Matrix and Full Delivery Depth are PASS / 0;
- Full Canonical Parity, Workspace Prompt Continuity, Canonical Materialization Parity and Full Materialization Audit are PASS / 0;
- Product Presence remains independently authored per asset rather than globally forced;
- Provider/media completion remains explicitly pending unless real provider outputs exist.

The verified fresh-K01 structural ZIP from candidate validation is evidence for Runtime behavior, not a replacement for the release artifact. The release artifact must still pass every exact-ZIP checker and be re-read after installation.

## Strict requirement accounting
The effective REQ-001..060 map remains:
- base: `REQUIREMENT_CONSUMER_MAP_V0664.json`;
- CURRENT release-process overrides: `REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json`.

The strict checker must report exactly 60 requirements, concrete Consumer paths, concrete proof objects, no generic/TBD/TODO placeholders, and current release-process evidence for REQ-046/047/048.

## Current release workflow
`.github/workflows/current-release-verification.yml` is the stable release path:
`v0.6.73 bilingual/business-object + model-prompt regressions → v0.6.72 fresh-K01 regressions → v0.6.71 acceptance → v0.6.70 prior maturity + requirement freshness → build_plugin_dist_current → exact ZIP → cumulative v0.6.70/v0.6.71/v0.6.72/v0.6.73 release checks → SHA256/bytes metadata → upload exact verified artifact`.

## Evidence boundary
Passing source/unit/package tests proves implementation and package integrity. The fresh K01 positive run proves structural materialization and prompt-consumption behavior against the real Excel truth when the final package audits pass. It does **not** create Provider Result evidence. Actual generated product imagery/video, pixel-level Review, Local Revision and provenance remain `E2E_PENDING` until genuinely produced. A fresh Host context resolving the installed v0.6.73 release is separate Host-native evidence.
