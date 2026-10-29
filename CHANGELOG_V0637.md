# v0.6.37 — Commercial Operator Density + Autonomous Integrated Render

## Goal
Move CBCC from “capability continuity proven” to **“operator can directly execute commercial work”**.

The release bar is not file presence, schema completeness, or provider transport success. It is:

> Strategy chooses, prompts are production-grade, assets can be generated/shot now, operators receive exact execution objects, actual outputs are reviewed, and learning routes back to the smallest responsible layer.

## P0 — Autonomous Integrated Render Authority

### Integrated native generation is the default
- Finished commercial visual assets default to integrated native generation.
- Product, market-facing copy, typography, scene, people, props, evidence graphics, lighting, CMF/material and finishing may be generated as one final-image problem.
- Product presence is a per-asset Agent Art Direction decision; ecommerce does not imply product in every asset.
- `POST_COMPOSITE` / `EXACT_PIXEL_COMPOSITE` remain valid explicit specialist routes.
- Missing copy render mode no longer becomes an operator-facing `COPY_RENDER_MODE_REQUIRED` gate when visible copy exists; the autonomous default is `MODEL_RENDER`.
- Historical “no marketing text / reserve copy zone / deterministic text after generation” instructions are removed from active integrated routes.
- An explicitly selected post-composite asset keeps its deliberate no-text requirement; v0.6.37 does not force the opposite global rule.

### Restrictions are exception-only
Hard visual restrictions require one of:
- explicit user lock;
- Product Truth / approved Claim / compliance / platform rule;
- explicit exact-pixel or post-composite route;
- material provider/model limitation.

Historical workflow habit is not a hard constraint.

## P0 — Commercial visual prompt density
Added `prompts/commercial_visual_generation_authority.md` covering:
- commerce objective and shopper state;
- creative thesis / visual carrier;
- product/reference role;
- decisive scene / moment;
- composition geometry / focal path / scale / depth;
- integrated exact copy / typography;
- evidence representation;
- camera / perspective / focus;
- lighting geometry / WB / exposure / reflection;
- CMF / material physics;
- color / grade;
- human / culture execution;
- platform/surface behavior;
- truth boundary;
- candidate generation strategy;
- actual-output QA;
- bounded repair routing.

Added `prompts/asset_photography_causal_reasoning.md` depth so camera/lens/light parameters require a visible commercial WHY instead of becoming decorative technical numbers.

Added deep CMF/material/lighting authority including material diagnosis, reflection/specular control, prelight-dependent values, color management and actual-result QA.

## P0 — Video becomes a commercial creative studio
Added `prompts/commercial_video_generation_authority.md`.

Video now authors:
- shopper tension and commercial hypothesis;
- dynamic narrative carrier;
- first frame / first 1–3 seconds;
- per-shot subject/action/environment;
- product reference and presence timing;
- camera/motion/focus/transition;
- copy/VO/subtitles/sound;
- cover/thumbnail;
- production route per shot;
- landing/attribution handoff;
- creative-test delta;
- rendered-video QA and local repair.

The legacy universal fallback `NATIVE_HOOK → PRODUCT_OR_ACTION_REVEAL → PROOF_DEMO → BELIEF_CLOSE → CTA_HANDOFF` is removed as a default. Explicit Agent-authored shot plans remain authoritative; runtime fallback is decision-derived from fit/scale, package trust, tactile/material, creator context or other supplied decision evidence.

## P0 — Operator execution density
Added `prompts/operator_execution_density.md`, `runtime/cbcc/operator_execution_board.py` and `runtime/cbcc/operator_delivery_html.py`.

The Chinese-first human workspace now prioritizes:
- `Launch Board` — what to do now, owner, object, dependency, completion check;
- `Listing Release` — final target-market copy + Chinese companion + release state;
- `Asset Production Board` — asset job, exact copy, product role, prompt/package/reference/output spec, production state;
- `Video Production Board`;
- `Paid Test Queue`;
- `Review Revision Queue`;
- `Economics Control Panel`;
- business-facing `Release Status`.

`Runtime / Consumer / hashes / technical status` remain available as a secondary Inspector rather than the primary operator experience.

## P1 — Seven first-class tools become an operating system
`prompts/seven_agent_orchestration.md` no longer expresses the capability as a mandatory `01→02→03→04→05→06→07` waterfall.

All seven capabilities remain first-class, but orchestration is relevance-driven:
1. Market Research — evidence → decision impact / research stop rule;
2. Product Strategy — primary thesis / SKU / offer / economics choice;
3. Listing Creative — publishable copy, search, claim and objection coverage;
4. Product Image — dynamic decision-driven asset architecture and final-image production;
5. Product Video — dynamic time-based commercial hypotheses;
6. Advertising Optimization — causal diagnosis, economics, creative decomposition, test/budget queue;
7. Review Analysis — VOC semantic intelligence, responsibility routing and local revisions.

Every activated tool must close with: **what to do, where, which final object to use, why, what stays frozen, completion condition, and what evidence determines the next move**.

## P1 — Prompt authoring upgrades
Expanded thin prompt stubs into senior-operator systems:
- `advertising_diagnosis.md` → causal media diagnosis, economics, creative fatigue/decomposition, P0/P1/P2 actions, creative tests and scale boundaries;
- `feedback_revision_routing.md` → raw VOC semantic coding, theme clustering, defect/expectation/service responsibility, positive-value mining, local revision + verification;
- `final_copy_local_authoring.md` → publishable field-level ecommerce copy with search/claim/objection/localization trace;
- `host_copy_authoring_orchestration.md` → complete native-market author/revise task output rather than translation notes;
- `copy_iteration_loop.md` → version-bound bounded revision;
- `economics_offer_strategy.md` → price/promo/creator/paid/bundle operating system and decision cliffs;
- `measurement_iteration.md` → causal operator learning loop and creative learning memory;
- `causal_experiment_design.md` / `advanced_causal_design.md` → decision-first experiment design, counterfactuals, clusters/geos/matching/CUPED/sequential/interference boundaries;
- `surface_production_contracts.md` → native surface adaptation, reuse/recompose/net-new production logic;
- `production_contract_provider_binding.md` → full provider job binding + actual-result handoff;
- `cmf_material_lighting.md` → material-physics-led shot design;
- `master_strategy_authoring.md` → decision-dense strategy instead of mandatory framework parade.

### Framework policy correction
STP / JTBD / RACE / AIDA / FABE / 4P / Fogg / Means-End / Signaling / FIRST / Cognitive Budget and related frameworks remain available as analysis lenses. They are no longer mandatory report sections. A framework is used only when it changes a real commercial decision.

## P1 — Prompt activation, not prompt file presence
The audit found that registry presence alone did not guarantee a prompt entered reasoning context. `runtime/cbcc/strategy_sources.py` is patched so active projects actually consume:
- `PROMPT-SEVEN-TOOLS`;
- `PROMPT-COMMERCIAL-INTEGRATED-VISUAL`;
- `PROMPT-OPERATOR-EXECUTION-DENSITY`;
- `PROMPT-COMMERCIAL-VIDEO` when video is relevant.

This closes the “capability exists in repository but Agent never sees it” regression class.

## P1 — Commercial prompt density regression guard
Added `scripts/check_commercial_prompt_density.py`.

It protects **24 first-class / senior commercial authoring authorities** with:
- minimum depth floors appropriate to each authoring role;
- required commercial reasoning concepts;
- active-runtime checks against legacy global text-suppression / unresolved copy-render behavior.

This is intentionally not a global “longer is better” rule. Small adapters/checkpoints may remain concise; senior commercial authoring systems may not silently regress into a few-line stub.

## Runtime
Added `runtime/cbcc/commercial_operator_density_authority.py`.

The final authority:
- resolves visible-copy default to `MODEL_RENDER`;
- preserves explicit `POST_COMPOSITE`;
- removes legacy text-suppression only for integrated routes;
- removes deterministic-text-composition as a default renderer authority;
- keeps target-market copy verbatim while preventing Chinese delivery/semantic annotations from leaking into English provider prompts;
- attaches `commercial_visual_qa_contract`;
- attaches operator-facing release metadata;
- keeps hard-input blocking separate from normal creative decisions.

## Migration
Added `scripts/apply_v0637_commercial_operator_density.py` to:
- wire the v0.6.37 authority after existing prompt/reference compatibility layers;
- patch legacy base copy defaults so the old policy is no longer the conceptual source;
- change unresolved visible-copy fallback to integrated `MODEL_RENDER`;
- remove duplicated legacy reference-closure code;
- activate new commercial reasoning prompts;
- remove the fixed video fallback;
- compile operator execution board and inject it ahead of the Runtime Inspector;
- update Skill precedence and prompt registry;
- bump seven-tool contract version.

The script is executed twice in CI to verify migration idempotency.

## Tests / CI
Added/updated tests for:
- integrated visible-copy default;
- explicit post-composite exception;
- no-visible-copy behavior;
- real-output visual QA contract;
- no global product-presence forcing;
- bilingual production semantics / no Chinese delivery-text leakage into English model prompt;
- operator execution board;
- operator-first HTML ordering and idempotency;
- decision-derived video narrative vs legacy fixed five-beat fallback;
- prompt activation into real reasoning context;
- forward compatibility of the v0.6.31 Model-Native Prompt contract.

Current v0.6.37 branch CI passes:
- migration script twice;
- Python `compileall`;
- commercial prompt density contract;
- all v0.6.37 authority tests;
- forward-compatible v0.6.31 prompt regression;
- base smoke suite;
- toolkit smoke suite;
- authority-source and activation checks.

## Audit
See `AUDIT_V0637_COMMERCIAL_OPERATOR_DENSITY.md` for the complete P0/P1 capability-density audit, tool-by-tool findings, external benchmark implications and acceptance contract.

## Release boundary
v0.6.37 removes the major architecture/prompt/operator-density regressions found in this audit. It does **not** claim that every future image/video is automatically commercially excellent merely because the contract passes. Commercial release still requires inspection of the actual generated/rendered output and bounded repair when the pixels/frames fail the authored decision job.