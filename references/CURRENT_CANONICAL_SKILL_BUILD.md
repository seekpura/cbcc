# CBCC Current Canonical Skill Build Authority

## Current rule
The canonical packaged Skill is built from the last verified mature textual floor plus current additive authority sections. Current releases do **not** recursively regenerate today's Skill through historical versioned builder chains or historical marker assumptions.

For the current v0.6.67 family, construction first reconstructs the exact verified v0.6.66 packaged Skill floor and hard-checks:
- UTF-8 bytes: `40612`;
- SHA256: `c9ac4577e38ef50cdfc033fae08f96f8b3d749583de89d360f35d390f684e06a`.

Any mismatch blocks the build before v0.6.67 authority is added.

## Stable construction contract
1. `VERSION` identifies the current semantic release family and full authority version.
2. `scripts/build_plugin_dist_current.py` identifies the one current release builder target and must match `VERSION`.
3. The target builder uses the non-versioned base resource copier for the current GitHub repository; it may not import a historical versioned builder chain.
4. Historical versioned builders remain provenance/regression evidence only; they do not define current release health.
5. The current canonical Skill is written byte-identically to packaged top `SKILL.md` and `resources/SKILL.md`.
6. Current cumulative/verbatim requirements, strict requirement-consumer accounting, Source Lock, Product Truth/strategy/Asset/Art Direction/Prompt/production/workspace authorities and current Runtime are packaged from current GitHub main.
7. Manifest, top/deep Skill, `resources/VERSION`, CURRENT requirement override family and CURRENT builder target must belong to the same semantic release family.
8. The final plugin ZIP is validated by `scripts/check_current_release_package.py`, whose expectations derive from CURRENT `VERSION`, not a hard-coded historical release.
9. The exact validated ZIP is hashed (SHA256 + bytes) and that exact artifact is the only installable release candidate.

## Strict requirement accounting
The effective REQ-001..060 map is:
- base: `REQUIREMENT_CONSUMER_MAP_V0664.json`;
- current release-process overrides: `REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json`.

The strict checker merges these sources before validation. Base rows REQ-046/047/048 are historical fallbacks and must be replaced by the CURRENT overrides in the effective map.

## Current release freshness
The strict checker must verify:
- effective IDs are exactly REQ-001..060;
- concrete Consumer paths exist;
- no generic/TBD/TODO consumer placeholders;
- `REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json.current_release_version` equals the semantic family in `VERSION`;
- `scripts/build_plugin_dist_current.py.CURRENT_BUILDER_TARGET` equals the same semantic family;
- REQ-046/047 use CURRENT release-process consumers;
- REQ-048 uses version-agnostic `RELEASE_EVIDENCE_REQUIRED_CURRENT`, not a historical `PROVED_####` status;
- the final package contains CURRENT builder/loading/source/consumer authorities and the required mature Runtime;
- the package top/deep Skill are byte-identical and share one current authority version.

## Current release workflow
`.github/workflows/current-release-verification.yml` is the stable current release proof path:
`CURRENT requirement accounting → build_plugin_dist_current → resolve exact ZIP → check_current_release_package → SHA/bytes metadata → upload exact verified artifact`.

Versioned workflows remain useful historical proof but cannot veto or certify a later CURRENT release merely because their old hard-coded expectations pass or fail.

## Evidence boundary
Installed plugin parity and active Host Skill snapshot parity are separate evidence. A stale active Host snapshot keeps positive Host-native FULL E2E pending even when installation/package parity is proven. Fresh real K01 FULL and actual Provider/Result/Review/Revision/QA remain required where their requirement rows are E2E pending.
