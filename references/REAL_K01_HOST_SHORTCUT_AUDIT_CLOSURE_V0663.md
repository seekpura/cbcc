# v0.6.63 Real K01 Host-Shortcut Audit Closure

## Why this patch exists
v0.6.62 installed the cumulative/verbatim requirement consumers, but a fresh reverse-test against the real 2026-10-30 K01 delivery exposed one remaining audit bypass: the historical Host shortcut stored its thin asset rows in `data/project.json` and five-file folders under `assets/`, while the mature audit primarily inspected `ASSET_UNIVERSE.json` and `asset_packages/`.

A negative fixture is not implemented if the exact real shortcut can still escape the package audit. v0.6.63 closes that path.

## Real K01 shortcut paths now consumed
The FULL package audit now inspects, when present:
- `data/project.json`;
- `assets/<id>/` five-file shortcut packages;
- the shortcut project's `visual.fidelity`, `pricing`, asset rows, Prompt CN/EN and `index.html` routes;
- mature `ASSET_UNIVERSE.json` + `asset_packages/` in parallel.

## Required structural failures for the historical K01 package
The verified historical package must be rejected for all of these structural classes:
1. `MATURE_ASSET_PACKAGE_INCOMPLETE` — 15/15 shortcut asset folders are materially incomplete;
2. `STRUCTURED_ASSET_ART_DIRECTION_MISSING` — 15/15 thin rows lack structured Art Direction authority;
3. `PRODUCT_PRESENCE_DECISION_NOT_STRUCTURED` — Product Presence is not authored as `planning_state + presence_why`;
4. `PRODUCT_EVERYWHERE_PORTFOLIO_REVIEW_REQUIRED` — all 15 assets carry product presence and therefore require explicit portfolio-level justification rather than default acceptance;
5. `ASSET_OPPORTUNITY_SWEEP_MISSING`;
6. `GLOBAL_POST_COMPOSITE_POLICY`;
7. `GLOBAL_NO_VISIBLE_COPY_PATTERN`;
8. `GLOBAL_NO_PRODUCT_GENERATION_PATTERN`;
9. `ACTUAL_GENERATED_OUTPUT_MISSING`;
10. `PROVIDER_RESULT_MISSING`;
11. `ACTUAL_OUTPUT_REVIEW_MISSING`;
12. `LOCAL_REVISION_LINEAGE_MISSING`;
13. `INFORMATION_ASSUMPTION_DECISION_LOG_MISSING`;
14. `PRICING_RECOMMENDATION_AHEAD_OF_ECONOMICS`;
15. `HOST_SHORTCUT_ASSET_PACKAGE_FORBIDDEN`;
16. `FIXED_CAPABILITY_MENU_SHELL`;
17. `FIXED_CAPABILITY_ROUTE_TAXONOMY`.

Fresh local verification against the real uploaded `KIYUU_K01_Malaysia_TikTok_CBCC` package produced `INCOMPLETE` with exactly these 17 structural issue classes. The older independent package audit had already identified the same real-world failure families; v0.6.63 brings them into the packaged Runtime audit itself.

## Four production objects are no longer optional for production-ready assets
Every active mature production asset must materialize, at minimum:
- `05_prompt_CN.txt` — Model Prompt CN;
- `06_prompt_EN.txt` — Model Prompt EN;
- `12_design_card.json` — machine-readable Design Card / structured Art Direction projection;
- `14_visible_copy_block.json` — Visible Copy Block;
- `15_production_assembly_notes.json` — Production / Assembly Notes.

Missing any of these produces `PRODUCTION_OBJECTS_INCOMPLETE`. This prevents the previous loophole where Prompt CN existed while Prompt EN / Design Card / Visible Copy / Production Notes silently disappeared.

## Completion boundary
This patch proves package-audit behavior against the historical negative fixture. It does **not** by itself prove a fresh positive K01 FULL project. REQ-038/039/049 and all fresh-output rows remain E2E pending until a new project is authored through the installed public plugin path and its real Provider/Result/Review/Revision/QA objects exist.
