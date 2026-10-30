# CBCC Current Canonical Skill Build Authority

## Current rule
The canonical packaged Skill is built from the last verified installed mature textual baseline plus current additive authority sections. Current releases do **not** recursively regenerate today's Skill through historical versioned builder chains or historical marker assumptions.

## Stable construction contract
1. `VERSION` identifies the current semantic release family.
2. `scripts/build_plugin_dist_current.py` identifies the one current release builder target and must match `VERSION`.
3. The target builder uses the non-versioned base resource copier for the current GitHub repository.
4. Historical versioned builders remain provenance only; they do not control current Skill generation.
5. The current canonical Skill is written byte-identically to packaged top `SKILL.md` and `resources/SKILL.md`.
6. Current cumulative/verbatim requirements, strict requirement-consumer accounting, Source Lock, Product Truth/strategy/Asset/Art Direction/Prompt/production/workspace authorities and current Runtime are packaged from current GitHub main.
7. Manifest, top/deep Skill and `resources/VERSION` must belong to the same release family.

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
- `scripts/build_plugin_dist_current.py` points to the same semantic release family as `VERSION`;
- REQ-046/047 use CURRENT release-process consumers;
- REQ-048 uses version-agnostic `RELEASE_EVIDENCE_REQUIRED_CURRENT`, not a historical `PROVED_####` status.

## Evidence boundary
Installed plugin parity and active Host Skill snapshot parity are separate evidence. A stale active Host snapshot keeps positive Host-native FULL E2E pending even when installation/package parity is proven. Fresh real K01 FULL and actual Provider/Result/Review/Revision/QA remain required where their requirement rows are E2E pending.
