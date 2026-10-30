# v0.6.66 Current Canonical Skill Build Authority

## Problem closed by this release
The v0.6.65 verification run proved the strict REQ-001..060 Consumer Map, but the final package builder still depended on a recursive historical chain (`v0665 → v0664 → v0663 → v0662 → v0659...`). The chain failed because v0.6.62 expected a marker in a historical generated v0.6.59 Skill that was no longer a valid invariant.

A current release must not depend on historical施工节点 successfully re-generating today's canonical Skill. Historical builders remain provenance, not current authority.

## Current Skill baseline
`references/CURRENT_PACKAGED_SKILL_BASELINE_V0665.md` is the **UTF-8 text-normalized baseline** copied from the actual installed v0.6.65 top Skill after installed top/deep parity was observed. The actual plugin file list reports 38,152 raw bytes, while the decoded Skill text exposed by Plugin Creator and committed here is 38,149 UTF-8 bytes. The exact 3-byte difference is the UTF-8 BOM representation boundary; the committed canonical source intentionally stores the decoded text without re-inserting a BOM.

The baseline contains the mature current authority through section 0.14. We preserve semantic/text content rather than polluting the source with artificial trailing bytes to mimic transport encoding.

v0.6.66 canonical Skill generation is additive:
1. read `CURRENT_PACKAGED_SKILL_BASELINE_V0665.md`;
2. normalize only release identity to v0.6.66;
3. insert the v0.6.66 current authority section before `## 1. FULL depth remains mandatory`;
4. write the exact resulting normalized UTF-8 text to both packaged top `SKILL.md` and `resources/SKILL.md`;
5. copy the current GitHub repository resources directly using the non-versioned base builder resource copier;
6. do not call any historical versioned `canonical_skill()` or `copy_repo_resources()` function.

## Required current authorities added by v0.6.66
- `REQUIREMENT_CONSUMER_MAP_V0664.json` — strict machine-level REQ-001..060 Consumer/proof map;
- `REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md` — human status summary subordinate to the strict map;
- `SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md` — CURRENT source lock;
- `HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md`;
- `canonical_authority_loading_map_v0665_addendum.md`;
- `scripts/check_v0664_requirement_consumer_map.py`.

## Build proof
Before release publication:
- strict Consumer Map: exactly 60 requirements / zero issues;
- frozen v0.6.65 normalized textual baseline byte size = 38,149 bytes; installed raw file size = 38,152 bytes because of the 3-byte BOM representation boundary;
- baseline retains all protected authority markers through section 0.14;
- final top/deep Skill byte-identical;
- manifest, top/deep Skill and `resources/VERSION` share v0.6.66 family;
- current Runtime files for long requirements, integrated render, full Art Direction, family/Presence audit and real-K01 shortcut audit are present in the final package;
- no v0.6.62 historical marker is required to build the release.

## Evidence boundary
This fixes release construction and one-to-one requirement accounting. It does not close fresh positive K01 FULL E2E or real Provider/Result/Review/Revision/QA evidence.