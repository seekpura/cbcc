# Creative Direction / Surface / Model-Native Prompt Compiler

## Objective
Compile production-ready asset objects from **already-authored commerce strategy + portfolio curation + per-asset Art Direction**.

The Prompt Compiler is a compiler, not the creative director. It preserves Agent decisions and translates them into the exact artifacts needed by the selected production route. It must not invent the asset’s composition, product role/presence, subject, scene, hierarchy, visual carrier, copy-render route or media language because those decisions are missing upstream.

## Authority order
`Product Truth / Evidence → Commerce Strategy → Portfolio Curation → Creative Direction → Per-asset Art Direction → Surface adaptation → Model Prompt + Visible Copy + Production Notes → Provider/Renderer`

Later layers may faithfully translate or technically adapt earlier decisions. They may not silently redesign them.

## v0.6.32 lossless production-parameter closure — highest prompt precedence
**Prompt compression may remove repeated words; it may not remove a selected value that changes pixels, timing, motion, composition, light, material response, source integration or output behavior.** If the Agent selected it because it matters to the result, the production chain must consume it.

For every asset, build a `production_parameter_closure` from the authored Art Direction before calling the Model Prompt READY:
- selected parameter/value;
- why it matters to this asset;
- route applicability;
- projection target;
- exact or semantically faithful consumption in Model Prompt / Visible Copy / Production Notes;
- explicit N/A reason where appropriate;
- unresolved/missing parameter requiring Agent completion.

A Prompt Consumption Audit that proves only field names or broad categories is invalid. Concrete values such as `85mm`, `camera height 12 cm above product center`, `pitch -3°`, `working distance 1.2 m`, `f/8-equivalent deep label focus`, `key 45° camera-left through 120 cm diffusion at 1.1 m`, `negative fill camera-right`, `5200K / neutral WB`, `2:1 key-fill`, `protect white-pack highlights below clipping`, `#0B3B31`, `product envelope 68% frame height`, `copy-safe left 36%`, `final grade neutral-warm with restrained specular roll-off` are the evidence of closure when those values were selected upstream.

### Photography execution depth
When the selected carrier/route uses photographic grammar, the Agent must author a useful route-specific starting contract before Prompt compilation. Depending on the asset, this can include focal length/lens family, working distance, camera height/yaw/pitch/roll, shot size, focus plane, aperture/DOF, shutter/ISO for real capture or motion, key/fill/negative/rim geometry, modifier size/distance, CCT/WB, light ratio, exposure/shadow/highlight policy, reflection/polarization, Prelight, CMF/material response, color management and finishing look.

The compiler must not replace a missing execution contract with `soft light`, `editorial`, `premium`, `85mm look`, or `warm white`. If a useful parameter is missing, expose `ART_DIRECTION_EXECUTION_DEPTH_REQUIRED` for Model Prompt readiness and return to the Agent. Wider project/strategy delivery may continue; the incomplete Prompt is the part that is not READY.

### Locked-source composite / plate prompting
A locked source product is not a reason to compile an empty-background prompt.

If the final visual contains `LOCKED_PIXEL / LOCKED_SOURCE_COMPOSITE` product layers, the **generated plate prompt still describes the final composite system**:
- product envelope / occupancy / relative placement;
- depth relationship between real source layers;
- receiving surface / contact point;
- camera/perspective relationship the environment must match;
- contact-shadow direction/density/softness;
- reflection/specular receiving behavior where relevant;
- ambient/key/fill direction and ratio;
- CCT/WB / grade-match target;
- foreground/occlusion relation where relevant;
- copy/evidence safe areas around the final composition.

The model is told not to render the locked product itself, but it must generate a plate designed **around the real final product geometry and light**. `warm ivory background + reserve space + no product` is not production-ready when the final geometry/light program is already known.

### No lossy hand-authored Prompt override
If `asset_art_direction.model_prompt_cn/en` is supplied manually, it does not bypass parameter closure. The compiler/audit still compares that Prompt against all selected generation-relevant values. A hand-written short Prompt that drops selected camera/light/composition/CMF/video parameters must be returned for revision.

## Four distinct production objects — never collapse them
When production prompts are requested, every activated visual/video asset uses four distinct objects:

1. **Model Prompt CN** — Chinese model-facing generation prompt. It describes what the image/video should become in natural model-native language.
2. **Model Prompt EN** — English model-facing generation prompt. Instructional prose must be English. Target-market visible copy may remain Malay/Arabic/etc. as exact quoted copy, but Chinese explanation/translation must not leak into this prompt.
3. **Visible Copy Block** — exact market-facing copy, secondary/proof/CTA copy, locale, Chinese delivery translation/usage note, hierarchy and copy budget.
4. **Production / Assembly Notes** — source-image role, Product Fidelity, locked-source compositing, copy-render mode, editable/frozen layers, provider route, assembly order, QA and revision boundaries.

`prompt_cn` / `prompt_en` are backward-compatible aliases of **Model Prompt CN / EN only**. They are not a place to dump machine contracts, renderer plans, audit logs or post-production policy.

## Model Prompt language rules
- EN prompt: no Chinese instructional prose. If upstream creative semantics exist only in Chinese, return `BILINGUAL_RENDER_SEMANTICS_REQUIRED`; runtime must not pretend a mixed-language block is an English prompt.
- CN prompt may retain exact target-market copy in its original language when that copy is part of the visual.
- Do not include internal engineering vocabulary such as `deterministic`, `renderer layer`, `machine contract`, `authority hash`, `prompt consumption audit`, `provider transport` or `post-layout` in a model-facing prompt.
- Express a visual need visually. Example: when exact copy will be assembled separately, the model prompt may say “preserve a clean typography-safe field; generate no marketing text,” while the reason/assembly method lives in Production Notes.

## Copy-render authority
Whether visible copy is rendered by the generation model is **not a global runtime default**. The Agent/production plan resolves one of:
- `MODEL_RENDER` — exact visible copy is included in the model prompt because the selected model/route is intended to render it.
- `POST_COMPOSITE` — model generates the visual field and typography-safe space; exact copy is composed in the production/assembly stage.
- `HYBRID` — some copy is model-rendered and some is composed separately.
- `NO_VISIBLE_COPY` — no visible market copy is needed.

If an asset has visible copy but this decision is missing, return `COPY_RENDER_MODE_REQUIRED`. Do not silently force every asset into post-composite typography.

## Required Agent Art Direction consumption
The compiler consumes, when relevant to the chosen carrier/production route:
1. Current shopper question, purchase barrier, belief shift and decision answer.
2. Visual carrier / information representation.
3. Explicit Product Presence: `HERO_REQUIRED | REQUIRED | SUPPORTING | OPTIONAL→PRESENT|ABSENT | DETAIL_ONLY | FORBIDDEN | NOT_APPLICABLE`, plus product role, scale relationship and source-reference role.
4. Decisive moment and subject/action/environment/props/people.
5. Composition grammar, spatial rhythm, layout geometry/relative placement, scale/depth, product occupancy, focal path and negative space.
6. Evidence/proof hierarchy and information relationship.
7. Camera/view/lens/perspective/focus only when relevant.
8. Lighting, CCT, contrast/exposure ratio, reflection/polarization/prelight only when relevant.
9. CMF/material response, palette HEX/color-world and color-management decisions.
10. Typography role, copy zone/safe zone and copy hierarchy when visible copy is relevant.
11. Human/casting/representation and exposure logic when people are relevant.
12. Output dimensions/aspect/color space/platform behavior.
13. Post look / finishing characteristics.
14. For video: duration, beat timing, shot sequence, subject motion, camera motion, transition/audio direction, CTA hold and platform-native rhythm.
15. Product Fidelity, source-reference role, editable/frozen layers and local revision boundaries — in Production Notes, not as model-prompt engineering prose.

Do not force photography fields onto graphic, illustration, source/document or other non-photographic carriers. Do not omit photography parameters from a photographic route after the Agent selected them.

## Model-native prompt order
Prefer natural positive-first generation language rather than schema dumps.

### Image / still
`output/canvas → visual objective/style → carrier/scene → subject/action/product role → composition/layout/scale/focal path/negative space → evidence hierarchy → camera geometry/focus/exposure (if relevant) → light geometry/material/CMF/color (if relevant) → human representation (if relevant) → exact copy behavior → finishing look → truth constraints`

### Video
`duration/aspect/platform → hook/decision objective → shot/beat progression → subject/product role → camera/subject motion → frame rate/stabilization when relevant → lighting/CMF → visible copy/CTA behavior → transition/audio rhythm → finishing look → truth/safety constraints`

The prompt should read like something an expert would actually give a current image/video generation model, not like a debug trace or JSON schema rendered into prose. Detailed execution does not mean dumping labels; write concrete values as natural visual instructions.

## Product presence rules
- **No silent default to product subject.** Missing Product Presence is an upstream Art Direction gap.
- `FORBIDDEN` / `ABSENT` / `NOT_APPLICABLE` means the model prompt and production layer plan must not add a packshot, corner product, silhouette, podium object or product layer.
- `TRUTH_REFERENCE_ONLY` can bind source files for factual/identity honesty while keeping them visually absent.
- Product identity/fidelity metadata may remain in Production Notes even when the product is absent. Truth authority is not visible presence.

## Layout / composition rules
- Never default to text-left/product-right, product-left/text-right, centered hero, card grid, podium hero or split-screen merely because the asset is ecommerce.
- Surface safe zones constrain authored placement; they do not author the layout.
- Copy budget constrains information density; it does not determine geometry.
- Coherence comes from selected continuity tokens. Different decision jobs may and often should create materially different spatial structures.
- Do not chase arbitrary novelty; differences must come from different information relationships, evidence, actions, subjects, scale or Surface behavior.
- Platform maximum asset count is capacity, not a target. Do not activate every slot merely because it exists.

## Parameter Consumption Audit — concrete values, not field names
Prompt readiness is proven by **actual selected values**. A row such as `surface size / composition / palette / camera` repeated in both Selected and Projected is not evidence.

For each selected execution decision record:
- decision path/name;
- concrete selected value;
- projection target (`MODEL_PROMPT`, `VISIBLE_COPY_BLOCK`, `PRODUCTION_NOTES`, or combination);
- whether that concrete value is present/consumed;
- why a value is intentionally omitted or N/A.

Also validate:
- English model-prompt language purity;
- absence of runtime/assembly jargon inside model prompts;
- exact visible-copy preservation in the correct object;
- product-presence consistency between Art Direction, model prompt and layer plan;
- selected photographic/video parameters only when relevant;
- locked-source plate/final-composite geometry closure;
- no fake readiness when bilingual creative semantics, execution-depth parameters or copy-render route is unresolved.

## Human delivery depth / no silent compression
Semantic compression may remove repeated explanation; it may **not** remove materially distinct strategy, visual, content or per-asset decisions.

The human workspace must preserve:
- the full project Visual Master / CMF / platform specification logic;
- per-asset Art Direction with the concrete parameters that change pixels/behavior;
- production-parameter closure and explicit N/A reasons;
- content/platform execution matrices at their authored decision depth;
- Model Prompt CN/EN separately from Visible Copy and Production Notes;
- Prompt Consumption Audit as a diagnostic, not the dominant content of the delivery.

The asset Inspector must not collapse the Design Card to a few fields such as `carrier / occupancy / composition / camera / lighting`. Show the authored decisive moment, subject/action/environment/props, spatial grammar, scale/depth, focal path, negative space, evidence hierarchy, CMF/material response, camera/focus/exposure, light geometry, copy zone, finishing look, video timing/motion and WHY when applicable.

Do not let repeated Prompt boilerplate consume more information budget than the strategy/visual/content decisions that created it.

## Mandatory output qualities
- Positive-first, model-native description of the desired image/video/design.
- Prompt reflects per-asset Art Direction rather than a generic ecommerce template.
- Product identity, pack text, claims and evidence are never invented.
- Copy is attributable to actual evidence when evidence is required.
- Camera/lighting appear only when relevant and include selected values that materially change the result.
- Human models appear because the decision job needs them, not because “lifestyle” was selected.
- Product absence is respected.
- Adjacent assets preserve intentional rhythm delta.
- Surface behavior is native rather than mechanically resized.
- No internal strategy-state/gate chatter, IDs, RACE/KPI metadata, audit prose or runtime assembly implementation in the model prompt.

## Failure behavior
If requested production reaches the compiler without a per-asset decision that materially affects pixels/behavior—especially visual carrier, product presence, composition hierarchy, subject, bilingual render semantics, copy-render mode or route-specific execution parameters—expose the missing Agent decision. Do not hide it with a product hero, generic left/right layout, generic photography recipe, mixed-language “English” prompt, empty-background plate or universal post-composite text rule.

This is production readiness, not permission to erase strategy/Listing/curation work already completed.

## Paid / Creator / Live
Paid creative has its own objective, audience state, tension, proof/offer, landing handoff and test hypothesis. Creator content is first-person/action native with real handling. Live is an interactive objection/demo/offer loop. None inherits PDP layout merely because the same product is sold.
