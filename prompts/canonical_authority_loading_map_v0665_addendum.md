# v0.6.65 Current-Release Authority Loading Addendum

Load after the v0.6.64 addendum.

Current stable authorities:
- `references/REQUIREMENT_CONSUMER_MAP_V0664.json` — machine-level REQ-001..060 one-to-one Consumer/proof authority; strict checker must report 60 requirements / 0 issues;
- `references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md` — human-readable summary only; it cannot replace the strict Consumer Map;
- `references/SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md` (`CURRENT`);
- `references/SOURCE_REQUIREMENT_NON_REGRESSION_LOCK_V0664_ADDENDUM.md`;
- `references/HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md`;
- `references/AUTHORITY_TEXT_PARITY_V0665.md`;
- `scripts/check_v0664_requirement_consumer_map.py`.

Forward-carried completion gates must use `current installed release` rather than a hard-coded historical semantic version. Versioned historical addenda remain valid provenance, but stable current authorities must not require renaming on every patch solely to keep text current.

One-to-one implementation accounting is mandatory: every REQ-001..060 names concrete existing Consumer path(s), concrete proof object(s), and a non-ambiguous status. Generic placeholders are forbidden. The strict GitHub Actions check passed 60/60 with zero issues before this authority was promoted.

Installed-plugin parity and active Host Skill snapshot parity are separate evidence. If a plugin is updated after the current Host conversation loaded its Skill and the active Skill snapshot is stale, record `HOST_SKILL_SNAPSHOT_STALE`; that conversation cannot provide positive E2E proof for the new release. Use a fresh Host context that actually loads the current Skill.

Preserve the current business Runtime: detailed cumulative/verbatim requirements, long-requirement Runtime consumers, 12-family Asset Universe audit, Product Presence audit, integrated native render authority, real-K01 17-class negative fixture, mature materialization and four production objects. Fresh positive K01 FULL host/plugin E2E remains mandatory before behavioral closure.