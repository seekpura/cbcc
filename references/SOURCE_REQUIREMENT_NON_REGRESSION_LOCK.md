# CBCC SOURCE REQUIREMENT NON-REGRESSION LOCK — CURRENT

## Mandatory authorities before any relevant release change
These authorities must be **read before every release change** affecting strategy, assets, Art Direction, Prompt, production, Human Workspace, language, compliance, economics, review or Runtime. A newer wording or summary may not erase an older semantic requirement.

Read and consume all current sources below:
- `CONVERSATION_REQUIREMENT_AUDIT.md` — **detailed** cumulative REQ-001..050 definitions; heading-only projection is invalid;
- `CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md` — REQ-051..060;
- `USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md` — verbatim long-form user authority; exact sequence, thresholds, table columns, P0/P1/P2 definitions, photography requirements and output-object requirements may not be summarized away;
- `REQUIREMENT_CONSUMER_MAP_V0664.json` — **machine-level one-to-one authority** for REQ-001..060; every requirement names concrete existing Consumer paths, concrete proof objects, and a non-ambiguous proof status;
- `REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md` — human-readable implementation summary; it never substitutes for the strict Consumer Map;
- `HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md` — installed plugin release and active Host Skill snapshot must match before that Host context can supply positive E2E evidence;
- `AUTHORITY_PARITY_REPAIR_V0664.md` — installed authority-drift regression history and repair proof;
- `AUTHORITY_TEXT_PARITY_V0665.md` — current-release wording stability;
- `REAL_K01_HOST_SHORTCUT_AUDIT_CLOSURE_V0663.md` — frozen real K01 shortcut regression authority;
- `SOURCE_REQUIREMENT_NON_REGRESSION_LOCK_V0663_ADDENDUM.md`;
- `SOURCE_REQUIREMENT_NON_REGRESSION_LOCK_V0664_ADDENDUM.md`;
- `MASTER_CONSTRUCTION_CONTRACT.md`;
- `PROMPT_ART_DIRECTION_MASTER_CONTRACT.md`;
- `BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md`;
- `HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md`;
- `ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md`;
- `AUTHORITY_SOURCE_PARITY_LOCK.md`;
- current canonical loading map/addenda and current Skill.

The latest user turn is never the whole specification unless the user explicitly replaces earlier requirements. Requirement IDs aid traceability; they may not replace the verbatim source or detailed cumulative definitions.

## One-to-one implementation accounting
Every REQ-001..060 must have all of the following simultaneously:
1. a detailed/verbatim source requirement;
2. one or more concrete named Consumer paths in `REQUIREMENT_CONSUMER_MAP_V0664.json`;
3. one or more concrete downstream proof objects;
4. an explicit status that distinguishes code/package/release enforcement from `E2E_PENDING`.

Generic entries such as `relevant Runtime consumer`, `current Skill/contract`, `TBD` or `TODO` are not acceptable implementation accounting. `scripts/check_v0664_requirement_consumer_map.py` must pass all 60 requirement rows with zero issues before publication. A human summary matrix may be shorter, but it cannot override or weaken the strict map.

## Additive invariant
A local fix is invalid if it deletes, compresses, hides or bypasses another mature capability. Protected dimensions include Product Truth, seven tools, pricing/economics, complete Listing, open Asset Universe, structured Art Direction, people/action/scene/props/composition/evidence/copy/culture/CMF/material, full camera/focus/exposure/lighting/prelight/finishing, dynamic Video/Creator/LIVE, integrated final render, Product Presence/Fidelity independence, four production objects, real Provider/Review/Revision/QA lineage, Chinese-first human delivery, mature routed workspace, and measurement/learning.

Historical Chinese capability anchors remain explicit and protected: **人物、场景、道具、摄影、灯光、CMF、材质、构图、文案、文化、视频**. A cleanup or modernization may not delete these dimensions from planning, structured Art Direction, Prompt/production projection, Human Workspace or review where they are relevant.

## Semantic planes
- Model Prompt: selected model-visible pixel/frame/audio-changing execution only.
- Visible Copy Block: exact consumer-visible copy + Chinese meaning/use.
- Production / Assembly Notes: source/reference/provider/editability/assembly/responsibility.
- Review / QA / Revision: post-output inspection, defect classification and smallest repair.
Semantic cleanup may remove orchestration from Prompt but may not delete neighboring people/scene/composition/camera/light/CMF/material/copy/culture/motion execution.

## Required release proof
For every touched requirement:
1. identify its detailed/verbatim source;
2. identify its concrete Consumer path(s) from the strict Consumer Map;
3. inspect the actual downstream proof object, not a heading, field name or boolean;
4. keep unknown current laws/platform mechanics/fees/holidays/logistics as TO_VERIFY/MISSING_INPUT;
5. preserve structured Art Direction before Prompt and concrete selected-value continuity;
6. preserve integrated render as normal route; post-composite/no-copy/product-absent/exact-pixel remain per-asset professional choices;
7. preserve 12-family Asset Opportunity sweep and structured Product Presence with WHY;
8. audit both mature `ASSET_UNIVERSE.json + asset_packages/` and Host shortcut `data/project.json + assets/` shapes;
9. reject the historical real K01 package for the frozen 17 structural regression classes;
10. require active mature assets to contain Prompt CN, Prompt EN, machine Design Card, Visible Copy Block and Production/Assembly Notes;
11. require real Provider Result/media/Review/Revision before claiming actual-output QA;
12. block own-SKU price recommendation when required unit-economics inputs are missing;
13. preserve project-authored routed workspace and reject fixed capability-menu/route taxonomy regression;
14. read back the **actual installed plugin** after update: manifests, top/deep Skill, VERSION, detailed ledger, strict Consumer Map, CURRENT matrix, CURRENT source lock and changed Runtime;
15. top/deep Skill and all release identity files must be one current release family;
16. read the active Host Skill resource used by the execution context and compare its release family to the installed release;
17. if the Host Skill snapshot is stale, record `HOST_SKILL_SNAPSHOT_STALE` and keep positive Host-native FULL E2E pending rather than treating stale execution as evidence;
18. a fresh positive K01 FULL run through a Host context that actually loaded the current installed Skill remains mandatory before FULL behavioral closure;
19. inspect the **actual FULL project materialization path** end to end; source contracts, unit tests, helper output or a hand-authored replacement package cannot substitute for the real Host/Runtime materialization path.

## Version-string hygiene
Current release-proof instructions use version-agnostic wording such as `current installed release`. Do not hard-code a historical release number into a forward-carried completion gate. Stable current authorities use `CURRENT` filenames where their semantics are release-independent; historical addenda retain versioned names only for traceability.

Rules without consumed downstream evidence are intent, not completion. Negative-fixture success does not substitute for positive E2E.