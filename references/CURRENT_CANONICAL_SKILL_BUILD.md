# CBCC Current Canonical Skill Build Authority

## Current rule
The canonical packaged Skill is built additively from the last verified mature Skill floor plus current authorities. `CURRENT` never means “whatever the latest source file happens to say”; VERSION, current builder, packaged override family, top/deep Skill and final ZIP proof must converge on one release family.

For current **v0.6.74**, `scripts/build_plugin_dist_v0674.py` calls the v0.6.73 canonical builder. v0.6.73 is the exact additive capability floor. The builder locks its UTF-8 bytes and SHA256 before adding the v0.6.74 authority section. During the bootstrap proof pass the digest is printed, then the observed digest must be hard-locked before final release publication.

The immutable lineage remains: v0.6.69 exact maturity floor → v0.6.70 semantic/prompt/Human parity → v0.6.71 final-package/Human/00–15 lineage parity → v0.6.72 fresh-K01 Runtime projection closure → v0.6.73 bilingual business-object/model-prompt consumption closure → v0.6.74 cross-scope regression closure. v0.6.74 is additive, not a rebase.

## Stable construction contract
1. `VERSION` identifies the current semantic release family and full authority version.
2. `scripts/build_plugin_dist_current.py.CURRENT_BUILDER_TARGET` must equal that family.
3. `references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json.current_release_version` must equal that family in repository and final ZIP.
4. The release builder must verify the previous exact Skill floor by bytes + SHA256 before adding current authority.
5. Current GitHub resources are copied from the current release head; historical versioned builders remain provenance/regression evidence.
6. Canonical Skill is written byte-identically to packaged top `SKILL.md` and `resources/SKILL.md`.
7. Manifest, both Skills, `resources/VERSION`, CURRENT override and CURRENT builder target belong to one family.
8. `scripts/check_current_release_package.py`, `scripts/check_v0674_release_delta.py` and every cumulative floor checker validate the exact built ZIP before installation.
9. CI records exact ZIP SHA256 + bytes and uploads that exact artifact; installation uses that verified artifact.
10. Installed plugin parity, active Host Skill snapshot parity, and fresh real K01 FULL behavior remain separate evidence.

## v0.6.74 Cross-Scope Regression Closure
- FULL aliases (`FULL_STRATEGY`, `FULL_E2E`, `FULL_PROJECT`, etc.) are consumed consistently across validation/export.
- Current explicit platform/market/site/locale and `visible_copy_locales` win; stale MY→SG/US leakage is cleared.
- Listing canonical lifecycle is `STRATEGY_READY / COPY_REVIEW_REQUIRED / PUBLISH_READY`, scoped to current target locale(s); legacy statuses remain compatibility metadata.
- Escaped Markdown pipes and YAML no-anchor serialization are closed.
- Source Truth produces a normalized Source Ledger with real status/path/hash/bytes.
- Model Prompt strips internal provenance metadata only, preserving co-located visual/camera/light/CMF/material instructions.
- v0.6.74 installs after mature v0.6.73 bootstrap and rebinds cached consumers.

## Proof boundary
Focused v0.6.74 tests are necessary but not sufficient. Exact final ZIP must pass cumulative v0.6.70–v0.6.73 floors, CURRENT identity, and v0.6.74 exact-ZIP checks. Installed readback follows. Fresh real K01 FULL against the exact Excel truth remains required for behavioral closure. Provider actual media/Review/Revision/provenance remain `E2E_PENDING` until genuine output exists.
