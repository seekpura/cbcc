# CBCC Canonical Authority Loading Map — CURRENT

For FULL / repair / release work, load current authorities in this order:
1. `references/CONVERSATION_REQUIREMENT_AUDIT.md` — detailed cumulative REQ-001..050;
2. `references/CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md` — REQ-051..060;
3. `references/USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md` — verbatim user authority;
4. `references/REQUIREMENT_CONSUMER_MAP_V0664.json` + `references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json` — effective machine-level REQ-001..060 Consumer/proof map; the CURRENT override release family must equal `VERSION`;
5. `references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md` — human summary only;
6. `references/SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md`;
7. `references/CURRENT_CANONICAL_SKILL_BUILD.md`;
8. `references/HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md`;
9. `references/MASTER_CONSTRUCTION_CONTRACT.md`, `PROMPT_ART_DIRECTION_MASTER_CONTRACT.md`, `BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md`, `HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md`, `ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md`, `MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md`;
10. `scripts/build_plugin_dist_current.py`, `scripts/check_v0664_requirement_consumer_map.py`, `scripts/check_current_release_package.py` for release construction/proof;
11. current Skill and current Runtime.

Public-path order remains:
`verbatim/cumulative requirements → Agent research/strategy/asset authoring → structured Art Direction → Asset Universe family/Presence audit → Prompt compilation → integrated render authority → final semantic membrane → mature asset package → Provider Job/Result → Review/Local Revision → Human Workspace → FULL package audit`.

Current release proof path is stable and release-agnostic:
`effective requirement freshness → build_plugin_dist_current → exact plugin ZIP → check_current_release_package → SHA256/bytes metadata → upload exact verified artifact → installed plugin readback → active Host Skill snapshot comparison`.

Historical versioned builders/workflows remain provenance and regression evidence only. They do not define the health of a later CURRENT release.

Release proof must separately verify actual installed plugin parity and the active Host Skill snapshot release family. `HOST_SKILL_SNAPSHOT_STALE` means the active context cannot prove the newly installed release positively.
