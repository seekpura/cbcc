# CBCC SOURCE REQUIREMENT NON-REGRESSION LOCK

## Purpose
This is the release-construction lock for Cross-Border Commerce Creative. Additive upgrades can still regress mature behavior when a local fix is implemented without re-reading the original source requirements that define the full system.

**The mandatory authorities below must be read before every release change that touches strategy, asset curation, Art Direction, Prompt compilation, production, Human Workspace, language, compliance or runtime behavior.** A release is not valid merely because the new local bug is fixed.

Mandatory original/current authorities:
- `references/CONVERSATION_REQUIREMENT_AUDIT.md` — detailed cumulative REQ-001..050 ledger; a heading-only projection is invalid;
- `references/CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md` — REQ-051..060 normalized release IDs;
- `references/USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md` — **verbatim user long-form source; sequence, thresholds, table columns, P0/P1/P2 definitions, visual-execution details and output-object requirements may not be summarized away**;
- `references/REQUIREMENT_IMPLEMENTATION_MATRIX_V0663.md` — current REQ-001..060 source → Runtime/Consumer → Human/package evidence → proof-status matrix;
- `references/REAL_K01_HOST_SHORTCUT_AUDIT_CLOSURE_V0663.md` — frozen real K01 `data/project.json + assets/` shortcut regression authority;
- `references/SOURCE_REQUIREMENT_NON_REGRESSION_LOCK_V0663_ADDENDUM.md`;
- `references/MASTER_CONSTRUCTION_CONTRACT.md`;
- `references/PROMPT_ART_DIRECTION_MASTER_CONTRACT.md`;
- `references/BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md`;
- `references/HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md`;
- `references/ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md`;
- `references/AUTHORITY_SOURCE_PARITY_LOCK.md`;
- current canonical loading map + v0.6.62/v0.6.63 addenda + current Skill authority.

`AUTHORITY_SOURCE_PARITY_LOCK.md` remains mandatory: a release is invalid when top-level Skill, packaged `resources/SKILL.md`, `resources/VERSION`, manifests or changed Runtime identify different release families. The actually installed plugin must be re-read after update; source/package intent alone is not proof.

## Conversation-requirement continuity
The latest user turn is never the whole specification unless the user explicitly replaces prior requirements. Before coding a fix, identify which cumulative requirement IDs the change touches and which adjacent capabilities could regress.

When the user supplies a concrete long-form block, preserve it verbatim whenever summarization could lose execution detail. IDs support traceability; verbatim sources preserve exact sequencing, columns, thresholds and mechanics.

`REQUIREMENT_IMPLEMENTATION_MATRIX_V0663.md` is the implementation-accounting layer. `E2E_PENDING` rows cannot be promoted merely because a requirement sentence, schema field, unit test or package guard exists.

## Additive release invariant
Every change preserves the complete existing capability set unless the user explicitly replaces a requirement. A fix is a regression if it improves one local dimension by deleting, compressing, hiding or bypassing another established dimension.

Protected authored dimensions include, independently: commercial decision/purchase barrier/target belief/WHY; people/subject/action/decisive moment; scene/environment/foreground-midground-background/props; Visual Carrier/hook/Hero Moment; Product Presence/Role/Fidelity/reference binding; composition/spatial relations/scale/depth/focal path/negative space/crop/safe zone; evidence hierarchy; copy/typography/localization; culture/intersectionality/inclusion; CMF/material/physical response/color; full camera/focus/exposure; full lighting/prelight/reflection/polarization; finishing/grade; Surface/device/output; Video/Creator/LIVE timing/motion/audio; hypothesis/metric/test variables; and QA/Review/smallest repair as separate downstream objects.

## Semantic-plane rule
Complete Art Direction does not mean all fields belong in Model Prompt:
- **Model Prompt**: selected pixel/frame/audio-changing execution;
- **Visible Copy Block**: exact consumer-visible copy + Chinese meaning/use;
- **Production / Assembly Notes**: source/reference/provider/editability/assembly/responsibility;
- **Review / QA / Revision**: post-output inspection, defect classification and smallest repair.
Semantic cleanup may remove orchestration from Model Prompt but may not delete neighboring people/scene/composition/camera/light/CMF/material/copy/culture/motion execution.

## Required release proof
Any release changing Prompt, asset curation, materialization, Human Workspace, strategy/culture execution or visual production must prove:
1. upstream structured Art Direction actually contains relevant selected decisions;
2. compatibility projection preserves concrete values;
3. final Model Prompt preserves every selected pixel/frame/audio-changing value relevant to route;
4. Excel/source authority/QA labels/repair workflow/provider internals do not leak into Model Prompt;
5. Production Notes and Review retain intentionally separated orchestration/QA;
6. final public compiler/provider path is tested, not only a helper;
7. Asset Universe, business density, Chinese Human Workspace and routed interaction remain intact;
8. top Skill, deep Skill, VERSION, manifests, builder and changed Runtime are same release family;
9. actual installed plugin is re-read;
10. actual FULL materialization uses mature compiler/export; a Host five-file shortcut is not an alternate schema;
11. Product Presence and copy-render route are per-asset decisions, not global product-everywhere/no-text/post-composite defaults;
12. a real FULL project is inspected after generation/materialization; if Provider execution is unavailable, actual-output QA cannot be claimed;
13. verbatim long-requirement locks are visible in relevant final objects: max-10 questions then continue; Product Truth four-way + A/B/C; four-context WHY; six-area P0 compliance; intersectionality; inclusive deep-skin photography; platform execution; regional localization; P0/P1/P2 tradeoff; RACE/culture tables; required Content Matrix columns; assumption/decision log; nine semantic output objects;
14. current implementation matrix is checked for every touched requirement;
15. Asset Opportunity Universe exposes 12-family sweep and Product Presence portfolio audit;
16. integrated-render assets cannot carry legacy no-text/no-product instructions unless route explicitly selects post-composite/no-copy/exact-pixel behavior;
17. pricing recommendations cannot outrun required unit-economics inputs;
18. **both** mature `ASSET_UNIVERSE.json + asset_packages/` and any Host shortcut `data/project.json + assets/` shape are audited;
19. every active mature production asset materializes Prompt CN, Prompt EN, machine Design Card, Visible Copy Block and Production/Assembly Notes;
20. the historical real K01 package triggers the 17 frozen structural regression classes.

A heading check, field-name check or self-authored PASS flag is insufficient. Use concrete-value regression fixtures and inspect the final downstream object.
