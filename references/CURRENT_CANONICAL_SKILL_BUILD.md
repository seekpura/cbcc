# CBCC Current Canonical Skill Build Authority

## Current rule
The canonical packaged Skill is built from the last verified mature textual floor plus current additive authority sections. Current releases do **not** recursively regenerate today's Skill through historical versioned builder chains or historical marker assumptions.

For the current v0.6.69 family, construction first reconstructs the exact verified/frozen v0.6.68 packaged Skill floor and hard-checks:
- UTF-8 bytes: `45014`;
- SHA256: `4c244d58fb4289fe9f32a38ea0eef9fbb974c9c6ac2a39b7f01618a65cea913d`.

Any mismatch blocks the build before v0.6.69 authority is added. v0.6.68 is therefore the mature capability floor for subsequent additive iteration.

## Stable construction contract
1. `VERSION` identifies the current semantic release family and full authority version.
2. `scripts/build_plugin_dist_current.py` identifies the one current release builder target and must match `VERSION`.
3. The target builder uses the non-versioned base resource copier for the current GitHub repository; it may not import a historical versioned builder chain.
4. Historical versioned builders remain provenance/regression evidence only; they do not define current release health.
5. The current canonical Skill is written byte-identically to packaged top `SKILL.md` and `resources/SKILL.md`.
6. Current cumulative/verbatim requirements, strict requirement-consumer accounting, Source Lock, Product Truth/strategy/Asset/Art Direction/Prompt/production/workspace authorities and current Runtime are packaged from current GitHub main.
7. Manifest, top/deep Skill, `resources/VERSION`, CURRENT requirement override family and CURRENT builder target must belong to the same semantic release family.
8. The final plugin ZIP is validated by `scripts/check_current_release_package.py`, whose expectations derive from CURRENT `VERSION`, not a hard-coded historical release.
9. The package checker directly reads the packaged `REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json.current_release_version`; missing/stale values fail with `PACKAGED_CURRENT_OVERRIDE_RELEASE_VERSION_MISMATCH`.
10. The final package must contain `runtime/cbcc/strategy_culture_materialization.py` and the bootstrap bindings that make its strategy, Human projection and FULL audit wrappers active.
11. The exact validated ZIP is hashed (SHA256 + bytes) and that exact artifact is the only installable release candidate.

## v0.6.69 strategy/culture materialization contract
The frozen v0.6.68 floor remains intact. v0.6.69 adds first-class materialization for requirements that previously could exist as fields/rules without being equally visible in Human delivery:
- Product Truth four-way audit: 真实卖点 / 可感知利益 / 情绪价值 / 不可宣称项 + A/B/C; C级不得作硬宣称;
- fact / assumption / decision log with basis and tradeoff;
- platform × region × audience × race-ethnicity-culture WHY;
- intersectionality: race/ethnicity × gender × age × income × geography;
- P0 claim/compliance and inclusive-photography execution;
- platform execution, localization and TO_VERIFY handling;
- RACE / STP / JTBD / AIDA / FABE / 4P / Funnel role + basis + tradeoff + execution;
- visual execution checklist including HEX/contrast/light/lens/camera/scene/props/casting and deep-skin Prelight-dependent exposure + reflector/diffusion;
- Content Matrix with RACE stage, culture/taboo checks, platform mechanics and attribution;
- RACE execution table and race/ethnicity cultural-adaptation table;
- explicit P0/P1/P2 keep/cut/defer/why/restore-condition rows;
- fabrication/WHY/culture/compliance/metric/assumption pre-output self-check rows.

These are semantic business objects and Human-delivery tables, not permission to create nine fixed pages or a capability-menu shell.

## Strict requirement accounting
The effective REQ-001..060 map is:
- base: `REQUIREMENT_CONSUMER_MAP_V0664.json`;
- current release-process overrides: `REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json`.

The strict checker merges these sources before validation. Base rows REQ-046/047/048 are historical fallbacks and must be replaced by the CURRENT overrides in the effective map.

## Current release freshness
The strict checker and final package checker together verify:
- effective IDs are exactly REQ-001..060;
- concrete Consumer paths exist;
- no generic/TBD/TODO consumer placeholders;
- repository CURRENT override `current_release_version` equals the semantic family in `VERSION`;
- packaged CURRENT override `current_release_version` also equals the exact plugin ZIP release family;
- `scripts/build_plugin_dist_current.py.CURRENT_BUILDER_TARGET` equals the same semantic family;
- REQ-046/047 use CURRENT release-process consumers;
- REQ-048 uses version-agnostic `RELEASE_EVIDENCE_REQUIRED_CURRENT`, not a historical `PROVED_####` status;
- the final package contains CURRENT builder/loading/source/consumer authorities, the mature v0.6.68 Runtime and v0.6.69 strategy/culture materialization Runtime;
- `strategy_culture_materialization.py` retains product truth / assumption log / intersectionality / framework / visual / tradeoff / self-check tokens and strict missing-object audit codes;
- `commercial_continuity_bootstrap.py` binds strategy materialization, Human projection and FULL audit wrappers;
- the package top/deep Skill are byte-identical and share one current authority version.

## Current release workflow
`.github/workflows/current-release-verification.yml` is the stable current release proof path:
`CURRENT requirement accounting → build_plugin_dist_current → resolve exact ZIP → check_current_release_package → SHA/bytes metadata → upload exact verified artifact`.

Versioned workflows remain useful historical proof but cannot veto or certify a later CURRENT release merely because their old hard-coded expectations pass or fail.

## Evidence boundary
Installed plugin parity and active Host Skill snapshot parity are separate evidence. A stale active Host snapshot keeps positive Host-native FULL E2E pending even when installation/package parity is proven. Fresh real K01 FULL and actual Provider/Result/Review/Revision/QA remain required where their requirement rows are E2E pending.
