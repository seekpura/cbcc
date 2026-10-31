# CBCC LOCKED IMPLEMENTATION PLAN — CURRENT

## Status
**LOCKED PLAN / IMPLEMENTATION IN PROGRESS**

This plan is the execution authority for repairing CBCC after the v0.6.75 K01 regression. It is intentionally broader than asset/prompt repair.

No task may be marked complete because a document, heading, field, test boolean or file exists. Completion requires the proof object named below.

If implementation reveals that a locked requirement is wrong or conflicts with a newer explicit user decision, stop that task and update the requirement authority/plan first. Do not silently improvise a different product decision.

## Mandatory authority set
Every task starts by reading:
- `CONVERSATION_REQUIREMENT_AUDIT.md` — REQ-001..050
- `CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md` — REQ-051..060
- `CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md` — REQ-061..090
- `USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md`
- `MASTER_CONSTRUCTION_CONTRACT.md`
- `BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md`
- `PROMPT_ART_DIRECTION_MASTER_CONTRACT.md`
- `FINAL_OUTPUT_CONTRACT.md`
- `HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md`
- `ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md`
- `MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md`
- CURRENT canonical loading map and CURRENT Skill.

## Execution protocol
For every implementation task:
1. **LOCKED REQUIREMENT** — name exact REQ IDs and source authority.
2. **RED** — add/extend the smallest deterministic regression/characterization test; confirm it fails for the intended missing behavior.
3. **GREEN** — implement the smallest coherent production change.
4. **FOCUSED VERIFY** — run the focused test and inspect the real produced object, not only status flags.
5. **CROSS-SCOPE VERIFY** — run adjacent regressions so the fix does not thin another domain.
6. **LEDGER UPDATE** — record changed consumers, proof objects and status in the CURRENT requirement consumer map/matrix.
7. **MATERIALIZATION VERIFY** — where applicable, inspect JSON → MD → HTML → Prompt/Production/package projections.
8. **REAL FIXTURE VERIFY** — for behavior touching FULL materialization, run the exact K01 FULL fixture before claiming behavioral closure.

No later task is allowed to make an earlier verified requirement thinner.

---

# Phase 0 — Freeze the regression and lock the new authority

### P0.1 Lock REQ-061..090 in source
Goal: make the explicit historical requirements non-optional release authorities.

Files:
- `references/CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_02.md`
- `references/SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md`
- `prompts/canonical_authority_loading_map_CURRENT.md`
- `references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md`
- machine CURRENT consumer map/override or a new current cumulative map.

Test/proof:
- release checker proves Extension 02 and this plan exist in source and built plugin;
- source lock and loading map name them;
- package readback proves files exist under plugin `resources/references/`.

Acceptance: no build/release path can omit the new authority documents without failing.

### P0.2 Freeze v0.6.75 K01 as a positive-repair target and current output as negative evidence
Goal: preserve the uploaded failed K01 behavior as a regression target without treating it as authority.

Proof criteria include:
- thin canonical object;
- JSON/MD/HTML drift or content loss;
- weak per-object strategy/photography/prompt density;
- shortcut `PACKAGE_AUDIT` that passes structure without business depth;
- missing mature FULL objects;
- missing lineage;
- incomplete opportunity-family evaluation;
- prompt parameter consumption gaps.

Acceptance: tests/audits reject an equivalent shortcut package as FULL complete.

---

# Phase 1 — Build one canonical commerce object graph

REQ: 001, 002, 006–018, 045, 052–060, 061, 062, 087, 088.

Goal: stop separately authoring Strategy, HTML, Prompt and asset files. Establish one canonical project graph that contains the full commercial project.

Primary existing consumers to inspect/modify:
- strategy/master-strategy Runtime consumers named by `REQUIREMENT_CONSUMER_MAP_V0664.json`;
- `runtime/cbcc/agent_autonomy.py`
- `runtime/cbcc/agent_plan_input_bridge.py`
- delivery/materialization consumers;
- supporting-analysis materializers;
- Listing/Economics/Ads/Review current consumers from the strict map.

Canonical graph must expose stable object IDs for:
- project/source/evidence;
- information audit/questions/assumptions/decision log;
- Product Truth/claims/value;
- research/market/competitor/search/reviews;
- audience/culture/intersectionality/localization;
- economics/offer;
- strategy/frameworks/message hierarchy;
- Listing/search;
- content matrix/RACE;
- Visual Master;
- opportunity universe and production portfolio;
- image/graphic/scene/negative/IP/video/creator/LIVE objects;
- Ads;
- Review Analysis;
- compliance/risk;
- measurement/tests;
- operations;
- production/review/revision lineage.

RED proof:
- construct a FULL canonical project where all above objects are required;
- current shortcut representation fails because objects are absent/flattened.

GREEN acceptance:
- one machine object graph contains all relevant objects;
- absent domains use `NOT_ACTIVE / TO_VERIFY / MISSING_INPUT` with WHY rather than disappearing;
- no asset-level field substitutes for Listing/Economics/Ads/Reviews/Research.

---

# Phase 2 — Full business-object density before any asset/prompt work

REQ: 006–018, 045, 053–060, 062, 087, 088.

Goal: restore senior-operator commercial depth independently of visual production.

Objects and required proof:
1. Information audit + ≤10 questions + assumptions + decision log.
2. Product Truth four-way audit + A/B/C + Claim→Evidence trace.
3. Market/search/competition/price-band/review opportunity research with source recency/confidence.
4. Platform×region×audience×culture WHY.
5. Intersectionality and culture adaptation checklist.
6. Positioning/VP/message hierarchy/STP/JTBD/AIDA/FABE/4P/Funnel/RACE as applied decisions.
7. Pricing/Economics/Offer with missing-input integrity.
8. Complete publishable Listing/Search object.
9. Content Matrix with hook/script/visual/CTA/metric/RACE/culture/platform execution/attribution.
10. Ads optimization object.
11. Review Analysis/root-cause/repair loop.
12. Measurement/A-B/P0-P1-P2/next-input plan.

Acceptance: every major row has `WHAT/WHY/EVIDENCE/TRADEOFF/EXECUTION/MEASUREMENT`; no section passes with headings plus generic prose.

---

# Phase 3 — Explicit opportunity-family evaluator

REQ: 019–024, 063–079.

Goal: prevent “TikTok = 9 images” and prevent specific historical families from being forgotten behind an abstract Asset Universe label.

Primary existing consumers:
- `runtime/cbcc/asset_universe_authority.py`
- `runtime/cbcc/asset_universe_family_audit.py`
- `runtime/cbcc/asset_architecture.py`
- `runtime/cbcc/asset_portfolio_taxonomy.py`
- `prompts/dynamic_asset_curation.md`

Required explicit family registry/evaluation:
1. Product identity/package truth
2. Hero/search/click identity
3. Benefit/value/belief shift
4. Ingredient/formula/mechanism
5. Material/texture/detail/macro
6. Packaging trust/contents/unboxing/size/compatibility
7. Scenario/lifestyle/context/human-use
8. How-to/routine/usage/care
9. FAQ/objection/expectation management
10. Comparison/decision clarification
11. Negative/counterexample/misconception/misuse/boundary
12. Source/document/evidence
13. Brand IP/distinctive memory/brand world
14. A+/PDP/rich/longform/specification
15. Paid/performance/Spark-style
16. Social/seeding/organic
17. Creator/UGC/affiliate
18. Product/PDP/short video
19. LIVE
20. Store/banner/landing
21. Campaign/seasonal/launch-event
22. CRM/lifecycle/post-purchase
23. Test/rotation/A-B/multivariate

RED:
- a fixture omitting Scene/Negative/IP/Video/Creator/Longform/Test without explicit decisions must fail.

GREEN acceptance:
- every relevant family is `ACTIVATED`, `NOT_NEEDED`, `TO_VERIFY` or `MISSING_INPUT` with WHY;
- Activation Set capacity never truncates the full universe;
- distinct hypotheses survive deduplication.

---

# Phase 4 — Visual Master + route-specific Art Direction

REQ: 024–032, 057, 080, 081, 084–086.

Goal: restore project-level visual strategy and full per-object art direction for still, graphic, scene, negative, IP, video, creator and other surfaces.

Primary consumers:
- `runtime/cbcc/agent_art_direction_authority.py`
- `runtime/cbcc/art_direction_projection.py`
- visual/photography consumers named in strict map;
- `prompts/visual_photography_strategy.md`
- `prompts/commercial_visual_generation_authority.md`
- `prompts/commercial_video_generation_authority.md`

Visual Master acceptance:
- visual thesis;
- moodboard/mechanism direction;
- continuity tokens;
- palette + HEX + contrast logic;
- type roles;
- information-density rules;
- scene/material/light world;
- culture/inclusion;
- product-presence rhythm;
- portfolio scale/depth/composition rhythm;
- deliberate breaks and WHY.

Per-object Art Direction acceptance when relevant:
- shopper question/barrier/entry/target belief/job/increment;
- visual/narrative carrier;
- product presence/role/reference behavior;
- subject/person/object/action/decisive moment;
- environment/props;
- composition/spatial geometry/scale/depth/focal path/negative space/safe zones;
- evidence hierarchy;
- exact copy/type/localization;
- culture/inclusion;
- CMF/material/color;
- camera/focus/exposure;
- lighting/prelight/reflection;
- finishing/output;
- motion/audio/timing for dynamic routes;
- portfolio delta;
- QA/repair responsibility.

Photography values must be scene-derived; repeated presets across unrelated objects fail unless justified.

---

# Phase 5 — Commercial-grade Prompt compiler and parameter-consumption audit

REQ: 033–036, 082, 083.

Goal: Prompt becomes a lossless model-facing projection of locked Art Direction, not a short recap and not an engineering dump.

Primary consumers:
- `runtime/cbcc/agent_authority_prompt_compiler.py`
- Prompt compiler/projection consumers named by strict map;
- `references/PROMPT_ART_DIRECTION_MASTER_CONTRACT.md`
- `references/MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md`
- `prompts/creative_direction_surface_prompt_compiler.md`

RED:
- prompt containing only product/background/camera/light must fail density/consumption audit;
- selected concrete geometry/light/material/copy/culture/motion values missing from acting plane must fail;
- source paths/QA/hash/authority prose leaking into Model Prompt must fail semantic membrane.

GREEN acceptance:
- Model Prompt CN + EN preserve all relevant pixel/frame/audio-changing decisions;
- Visible Copy Block is separate and exact;
- Production/Assembly Notes hold source/provider/editability/assembly metadata;
- Review/QA/Revision stays post-output;
- `missing_decisions=0` or equivalent concrete-value audit passes for READY objects;
- no arbitrary minimum byte count is used as a substitute for completeness.

---

# Phase 6 — JSON / MD / HTML same-source projection

REQ: 016–018, 042–045, 061, 089.

Goal: eliminate independently authored HTML/MD summaries.

Primary consumers:
- `runtime/cbcc/delivery_export.py`
- `runtime/cbcc/delivery_workspace.py`
- `runtime/cbcc/delivery_html.py`
- `runtime/cbcc/commercial_workspace_shell.py`
- human-language projection consumers named by strict map.

Required rule:
- canonical JSON business graph is source;
- MD renders the same objects completely;
- HTML renders the same objects through routed interaction;
- object IDs and canonical value signatures remain stable across projections.

RED:
- remove one strategy/Listing/Prompt/Art Direction value from HTML or MD and parity audit must fail.

GREEN acceptance:
- no human-relevant canonical object exists only in JSON/MD;
- HTML summary cards are entrances, not replacements;
- target-market copy + Chinese companion remain co-located;
- one primary route at a time, subviews/lenses, `asset/<id>` or equivalent object detail, search/copy/back/hash/responsive/print are preserved;
- IA is project-authored, not a permanent fixed capability menu.

---

# Phase 7 — FULL materialization/package continuity

REQ: 037, 045, 060, 090.

Goal: one mature export path creates all machine/human/editable/production objects. Host-native and Runtime exports are semantically equivalent.

Required outputs when relevant:
- `index.html`
- `00_PROJECT_HUB.md`
- `01_LISTING_UPLOAD_READY.md`
- `HUMAN_DELIVERY.json`
- strategy authorities/decision indexes/context/audits
- supporting analyses
- `ASSET_UNIVERSE.json`
- complete per-production-object packages
- Video/Creator/Paid/Social/LIVE/Longform/etc objects when activated
- language audits
- platform scope
- source truth/media/source ledger
- full object manifest
- materialization audit
- delivery manifest

RED:
- shortcut five-file/summary package must fail.

GREEN acceptance:
- `FULL_MATERIALIZATION_AUDIT` validates semantic object coverage and same-source parity, not file count only.

---

# Phase 8 — Provider / Result / Review / smallest repair lineage

REQ: 038–041, 090.

Goal: planning and production evidence remain distinct.

Primary consumers:
- Provider bridge/executor/transport modules from strict consumer map;
- review/production-learning consumers;
- asset package lineage consumers.

Acceptance:
- Provider Job binds exact final prompt/reference/copy/route;
- Provider Result stores actual media/result metadata;
- Review inspects actual pixels/frames/audio;
- defect classified to smallest responsible layer;
- Local Revision recorded;
- hashes/provenance preserved;
- without actual provider output, actual-output status remains `E2E_PENDING`.

---

# Phase 9 — Requirement consumer map 001..090

Goal: every requirement has exact implementation accounting.

Create/upgrade a cumulative machine map where each REQ-001..090 contains:
- detailed source authority;
- exact consumer path(s);
- exact proof object(s);
- test(s);
- human surface(s) where relevant;
- status: `LOCKED`, `IMPLEMENTED_CODE`, `PACKAGE_ENFORCED`, `E2E_PENDING`, `VERIFIED_E2E`, etc.

Generic “relevant consumer” entries fail.

Acceptance: strict checker reports `requirement_count=90` and `issue_count=0` for mapping integrity; this proves accounting only, not behavioral E2E.

---

# Phase 10 — Real K01 FULL regression through actual public path

Goal: prove the repaired system on the exact real fixture, not a synthetic toy.

Inputs:
- exact `KIYUU_5款产品信息_纯粹版(7).xlsx` as product authority;
- real K01 product/package images available in the project fixture;
- Malaysia TikTok Shop scope and target-language requirements.

Must inspect actual output for:
- all relevant non-asset commerce objects at professional depth;
- explicit 23-family opportunity evaluation;
- dynamic candidate universe larger than Live slots when justified;
- scene/negative/IP/video/creator/paid/longform/test decisions present or explicitly not-needed with WHY;
- complete Visual Master;
- complete per-object Art Direction;
- commercial-grade Prompt CN/EN and parameter-consumption audit;
- exact Visible Copy + Chinese companion;
- JSON/MD/HTML same-source parity;
- routed human workspace with full objects;
- mature package lineage;
- no fabricated current platform/legal/economic facts;
- Provider/actual-output status honestly pending unless real generation is executed.

Behavioral closure is impossible until this real fixture passes.

---

# Phase 11 — Independent review + final verification + release

Before claiming completion:
1. deliberate correctness/spec review against REQ-001..090;
2. code-quality/maintainability review;
3. focused tests for every changed task;
4. full relevant suite;
5. CURRENT build;
6. exact package checker;
7. unzip/readback;
8. actual installed plugin readback after update;
9. fresh K01 FULL public-path proof;
10. no claim of Provider actual-output QA without actual Provider output.

---

# Progress ledger rule
Implementation must maintain a machine-readable/current human ledger with one row per task/REQ set:
`Task → REQ IDs → RED evidence → changed consumers → focused verification → cross-scope verification → materialization proof → K01 proof → status → unresolved risks`.

A task cannot move to DONE if its proof column is empty.

# Non-negotiable completion rule
The project is not complete when “all tests pass”. It is complete only when the tests **and** actual canonical business objects **and** JSON/MD/HTML projections **and** production objects **and** real K01 FULL output satisfy the locked requirements without making an earlier dimension thinner.
