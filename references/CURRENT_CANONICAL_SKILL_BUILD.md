# CBCC Current Canonical Skill Build Authority

## Current rule
The canonical packaged Skill is built additively from the last verified mature Skill floor plus current authorities. `CURRENT` never means “whatever the latest source file happens to say”; VERSION, current builder, packaged override family, top/deep Skill and final ZIP proof must converge on one release family.

For current **v0.6.72**, `scripts/build_plugin_dist_v0672.py` calls the v0.6.71 canonical builder. The v0.6.71 Skill is an exact frozen floor:
- UTF-8 bytes: `60081`;
- SHA256: `07008d4d41a3e5a2736110fa54b3fdfe4da5be3190ff2eb3f307d491b6705aab`;
- required markers include `0.20 Full Canonical Human + Package Lineage Parity`, `0.19 Canonical Materialization + Human Projection Parity`, and the FULL-depth authority marker.

The earlier immutable provenance remains underneath it: v0.6.69 exact maturity floor (`48517` bytes / SHA256 `f3ed58aafc24947e85fc268144ea787d4db5eaed66b31008f6a5cf87500cbd54`) → v0.6.70 semantic/prompt/Human parity floor (`54752` bytes) → v0.6.71 real final-package/Human/00–15 lineage floor → v0.6.72 fresh-K01 Runtime projection closure. v0.6.72 is additive, not a rebase.

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

## v0.6.72 Fresh K01 Runtime Projection Closure
This release is driven by a fresh K01 FULL structural run against the exact Library source `KIYUU_5款产品信息_纯粹版(7).xlsx`. It does not weaken the v0.6.70/v0.6.71 guards; it closes producer/consumer gaps discovered only after those guards were exercised on a real product project.

- `portfolio_visual_authority.py` consumes canonical `portfolio_rhythm_delta` / `rhythm_delta` so the portfolio review does not falsely report a missing adjacent-asset delta while Prompt/Human/lineage already use that field. Duplicate-signature detection remains unchanged.
- `canonical_visual_master_projection_v0672.py` losslessly aggregates already-authored per-asset environment/scene and props into missing project Visual Master slots. Explicit project-level decisions win; Runtime invents nothing.
- `delivery_companion_projection_v0672.py` reuses already-authored delivery-locale (`zh-CN`) same-field copy as the Chinese companion for target-market/English final-copy rows. Missing Chinese remains unresolved; there is no arbitrary machine translation.
- the same language closure recognizes mature `14_visible_copy_block.json → raw.chinese_meaning`, preserves authored video/creator Chinese hook/CTA companions including nested Art Direction values, and bilingualizes only Runtime-owned fixed default Creator CTA copy.
- bootstrap order is now a tested release invariant: importing CBCC must not eagerly import `cbcc.compiler` before v0.6.70/v0.6.71 Strategy completion wrappers install.
- `canonical_human_compaction_v0672.py` keeps generic Human field coverage while materializing heavy Asset/Asset-Universe families only once on their dedicated surfaces; Search/Copy remain safe DOM behavior.

## Fresh K01 structural evidence
The v0.6.72 regression suite directly covers the defects surfaced by the real K01 run: canonical portfolio delta consumption, authored asset-world → Visual Master projection, authored Chinese companion reuse, Visible Copy nested Chinese meaning, video hook/CTA companion propagation, bootstrap import-order safety and deduplicated Human projection.

The old v0.6.69 positional-shift fixture remains a regression target: mature asset fields are semantically guarded, CN/EN/Design Card lineage is one canonical source, and 00–15 package/Human parity remains enforced by v0.6.70/v0.6.71.

## Strict requirement accounting
The effective REQ-001..060 map remains:
- base: `REQUIREMENT_CONSUMER_MAP_V0664.json`;
- CURRENT release-process overrides: `REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json`.

The strict checker must report exactly 60 requirements, concrete Consumer paths, concrete proof objects, no generic/TBD/TODO placeholders, and current release-process evidence for REQ-046/047/048.

## Current release workflow
`.github/workflows/current-release-verification.yml` is the stable release path:
`v0.6.72 bootstrap/fresh-K01 regressions → v0.6.71 acceptance → v0.6.70 prior maturity + requirement freshness → build_plugin_dist_current → exact ZIP → cumulative release-delta checks → SHA256/bytes metadata → upload exact verified artifact`.

## Evidence boundary
Passing source/unit/package tests proves implementation and package integrity. The fresh K01 Runtime run proves structural materialization behavior against the real Excel truth when the final package itself passes export audits. It does **not** create Provider Result evidence. Actual generated product imagery/video, pixel-level Review, Local Revision and provenance remain `E2E_PENDING` until genuinely produced. A fresh Host context resolving the installed v0.6.72 release is also separate Host-native evidence.
