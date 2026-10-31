# CBCC Current Canonical Skill Build Authority

## Current rule
The canonical packaged Skill is built additively from the last verified mature Skill floor plus current authorities. `CURRENT` never means “whatever the latest source file happens to say”; VERSION, current builder, packaged override family, top/deep Skill and final ZIP proof must converge on one release family.

For current **v0.6.75**, `scripts/build_plugin_dist_v0675.py` calls the v0.6.74 canonical builder. v0.6.74 is the exact verified additive capability floor and is hard-locked to **71,400 UTF-8 bytes / SHA256 `8d5e62a0486c83712b61c31010b83b7bc59af0439e7546ba02f48627caecefc8`** before v0.6.75 identity normalization.

The immutable lineage remains: v0.6.69 exact maturity floor → v0.6.70 semantic/prompt/Human parity → v0.6.71 final-package/Human/00–15 lineage parity → v0.6.72 fresh-K01 Runtime projection closure → v0.6.73 bilingual business-object/model-prompt consumption closure → v0.6.74 cross-scope regression closure → v0.6.75 formal full-package identity closure. v0.6.75 is additive and introduces no business-runtime delta from v0.6.74.

## Stable construction contract
1. `VERSION` identifies the current semantic release family and full authority version.
2. `scripts/build_plugin_dist_current.py.CURRENT_BUILDER_TARGET` must equal that family.
3. `references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json.current_release_version` must equal that family in repository and final ZIP.
4. The release builder must verify the previous exact Skill floor by bytes + SHA256 before adding current authority.
5. Canonical Skill is written byte-identically to packaged top `SKILL.md` and `resources/SKILL.md`.
6. Manifest, both Skills, `resources/VERSION`, CURRENT override and CURRENT builder target belong to one family.
7. Exact final ZIP must pass CURRENT checks, v0.6.70–v0.6.74 cumulative floors, and current exact-release checks before installation.
8. CI records exact ZIP SHA256 + bytes and uploads that exact artifact; installation uses that verified full artifact, not an overlay.
9. Installed plugin parity and active Host Skill snapshot parity remain separate evidence.
10. Fresh real K01 FULL against the exact workbook remains required for behavioral closure.

## v0.6.75 identity closure
The host already consumed semantic version 0.6.74 for an earlier partial overlay. Because same-version Plugin Creator updates auto-bump patch versions, the exact verified v0.6.74 full artifact cannot be installed under the same plugin ID without creating another identity mismatch. v0.6.75 therefore republishes the exact verified v0.6.74 capability floor as the next clean complete-plugin release. No Product Truth, strategy, Listing, asset, Prompt, Runtime, Provider or Human Workspace behavior is intentionally changed.

## Proof boundary
Package/release proof does not replace fresh product-truth behavior proof. Provider actual media/Review/Revision/provenance remain `E2E_PENDING` until genuine output exists.
