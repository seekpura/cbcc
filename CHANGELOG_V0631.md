# CBCC v0.6.31 — Model-Native Prompt Integrity

## Why this release exists
A real FULL delivery exposed a prompt-layer regression: the human workspace labeled engineering/assembly prose as generation prompts, English prompts contained Chinese creative instructions, a universal deterministic post-layout text rule leaked into every asset, parameter consumption was audited by generic field names rather than concrete values, and upstream visual/content depth could be compressed while repeated prompt boilerplate expanded.

v0.6.31 corrects the responsibility model without rolling back v0.6.30 Agent Art Direction Authority.

## Model-native production objects
Every activated production asset now separates:
1. `Model Prompt CN` — Chinese model-facing generation instructions.
2. `Model Prompt EN` — English model-facing generation instructions. Target-market visible copy may remain in the original market language, but Chinese explanations never masquerade as English instructions.
3. `Visible Copy Block` — exact market-facing copy, secondary copy, Chinese delivery translation, copy budget and typography direction.
4. `Production / Assembly Notes` — Product Fidelity, source binding, copy-render route, locked/editable layers, provider/assembly and revision rules.

`prompt_cn` and `prompt_en` remain compatibility aliases of the model-facing prompts only.

## Copy rendering is an Agent/production decision
Visible copy uses an explicit route: `MODEL_RENDER`, `POST_COMPOSITE`, `HYBRID` or `NO_VISIBLE_COPY`. Runtime no longer globally decides that text is a deterministic post-layout operation. Missing copy-render intent returns `COPY_RENDER_MODE_REQUIRED`.

## Language integrity
English model instructions are checked for Chinese leakage. If upstream creative semantics exist only in Chinese, the system returns `BILINGUAL_RENDER_SEMANTICS_REQUIRED` instead of emitting a mixed-language English prompt.

## Concrete parameter continuity
Prompt Consumption Audit now traces actual selected values into the correct object/language. Generic rows such as `surface size / composition / palette / camera` are not accepted as evidence of consumption.

The model-native prompt compiler can consume, when relevant: output size/aspect/color space; visual objective/carrier/language/thesis; subject/action/environment/props/people; product presence/role; composition/spatial rhythm/layout geometry/scale-depth/product occupancy/focal path/negative space; evidence hierarchy; camera/lens/perspective/focus; lighting/CCT/contrast/reflection/prelight; CMF/material response/palette/color management; copy zone/typography; inclusive human execution; post look; and video timing/shot/motion/transition/audio.

## Photography remains carrier-aware
Photography is not restored as a universal template. If the Agent selects photographic grammar, the selected asset can consume strategy-level camera/lens/light/inclusive-photography decisions. Graphic/illustration/source/document assets are not forced to invent shutter/ISO/camera fields.

Human photography continuity explicitly preserves deep-skin shadow detail, skin-reference metering, reflector/bounce/diffusion and representation/bias controls when relevant.

## Locked source stays strict in the correct layer
`LOCKED_PIXEL` and `LOCKED_SOURCE_LAYER` still bind exact product pixels and renderer layers, but those engineering constraints live in Production / Assembly Notes and the renderer contract rather than polluting the model prompt.

## Human delivery depth
The human asset workspace now exposes complete Agent Art Direction rather than only a thin projection: visual carrier, product presence/role, decisive moment, subject/action/environment/props, composition/spatial rhythm/layout geometry, scale/depth/product occupancy/focal path/negative space, evidence hierarchy, copy zones, camera/light/CMF/color when relevant, output spec, post look, WHY and video motion/timing when relevant.

`delivery_contract` now uses carrier-aware FULL visual depth and rejects shallow per-asset reasoning while not forcing photography fields onto non-photographic carriers.

## Workspace terminology
Prompt Lab and asset pages now explicitly label `Model Prompt CN / EN`. `Visible Copy` and `Production / Assembly Notes` are separate human objects. Legacy UI wording such as “确定性排版规则”, “中文规范生产提示词” and “Prompt 是执行合同” is removed from the active workspace.

## Continuity
v0.6.31 retains v0.6.30 Agent authority: product presence cannot be recovered by runtime heuristics, Surface remains advisory, per-asset Art Direction wins over direction-level defaults, missing creative decisions return to the Agent, and FORBIDDEN product states never regain a product layer.
