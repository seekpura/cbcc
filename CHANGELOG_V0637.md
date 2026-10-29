# v0.6.37 — Commercial Operator Density + Autonomous Integrated Render

## Goal
Move CBCC from “capability continuity proven” to “operator can directly execute commercial work”.

## P0 authority change

### Autonomous Integrated Render Authority
- Finished commercial visual assets default to integrated native generation.
- Product, market-facing copy, typography, scene, people, props, evidence graphics, lighting, CMF/material and finishing may be generated as one final-image problem.
- Product presence remains a per-asset Agent Art Direction choice; ecommerce does not imply product in every asset.
- `POST_COMPOSITE` / `EXACT_PIXEL_COMPOSITE` remain valid explicit specialist routes.
- Missing copy render mode no longer becomes an operator-facing `COPY_RENDER_MODE_REQUIRED` gate when visible copy exists; the autonomous default is `MODEL_RENDER`.
- Historical “no marketing text / reserve copy zone / deterministic text after generation” instructions are stripped only for integrated model-render routes. Explicit post-composite assets keep their deliberate no-text instruction.

### Restrictions are exception-only
Hard visual restrictions require one of:
- explicit user lock;
- Product Truth / Claim / compliance / platform rule;
- explicit exact-pixel or post-composite route;
- material provider/model limitation.

Historical workflow habit is not a hard constraint.

## Commercial visual prompt density
Added `prompts/commercial_visual_generation_authority.md` covering:
- commerce objective;
- creative thesis / visual carrier;
- product/reference role;
- decisive scene;
- composition geometry;
- integrated exact copy / typography;
- evidence representation;
- camera / perspective;
- lighting;
- CMF / material physics;
- color / grade;
- human / culture execution;
- surface behavior;
- truth boundary;
- candidate generation;
- output QA;
- bounded repair routing.

## Operator execution density
Added `prompts/operator_execution_density.md`.

Human delivery must prioritize operating objects:
- Launch Board;
- Listing Release;
- Asset Production Board;
- Paid Test Queue;
- Review Revision Queue;
- Economics Control Panel;
- business-facing Release Status.

Normal professional choices are Agent-owned; operator blockers are reserved for real hard inputs.

## Prompt upgrades
Expanded thin prompt stubs into senior-operator systems:
- `advertising_diagnosis.md` → media/operator causal diagnosis, economics, fatigue, creative decomposition, action/test/budget queues;
- `feedback_revision_routing.md` → raw VOC semantic intelligence, responsibility attribution, positive-value mining, local revision + verification;
- `final_copy_local_authoring.md` → publishable field-level ecommerce copy with search/claim/objection/localization trace;
- `economics_offer_strategy.md` → price/promo/creator/paid/bundle operating system;
- `measurement_iteration.md` → causal operator learning loop and decision memory.

## Runtime
Added `runtime/cbcc/commercial_operator_density_authority.py`.

The final authority:
- resolves visible-copy default to `MODEL_RENDER`;
- preserves explicit `POST_COMPOSITE`;
- removes legacy text-suppression only for integrated routes;
- removes deterministic-text-composition as default renderer authority;
- attaches `commercial_visual_qa_contract`;
- attaches operator-facing release metadata;
- keeps hard-input blocking separate from normal creative decisions.

## Migration
Added `scripts/apply_v0637_commercial_operator_density.py` to:
- wire the v0.6.37 authority after existing prompt/reference wrappers;
- patch legacy base copy defaults so the old policy is no longer the conceptual source;
- change unresolved visible-copy fallback to integrated `MODEL_RENDER`;
- remove duplicated legacy reference-closure code;
- update Skill precedence and prompt registry;
- bump seven-tool contract version.

## Tests
Added `tests/test_v0637_commercial_operator_density.py` covering:
- integrated visible-copy default;
- explicit post-composite exception;
- no-visible-copy behavior;
- real-output visual QA contract;
- no global product-presence forcing.

## Audit
See `AUDIT_V0637_COMMERCIAL_OPERATOR_DENSITY.md` for the full P0/P1 capability-density audit and acceptance contract.