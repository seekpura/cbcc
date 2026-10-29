# CBCC v0.6.32 — Production Parameter Closure + Creative Depth

## Why this release exists
v0.6.31 correctly separated Model Prompt CN/EN, Visible Copy and Production / Assembly Notes, but a real KIYUU K01 delivery exposed a serious regression from the useful v0.6.6 production contract: prompt separation was being treated as permission to compress away design and photography decisions that actually change pixels.

The observed failure mode was not cosmetic. A Design Card could contain a product occupancy, copy zone or broad camera/light idea while the final model prompt collapsed to something like a warm-ivory background, reserved empty space and a no-product instruction. The upstream planning then stopped controlling generation.

This release restores the causal contract:

`Product Truth + Commerce Strategy → Portfolio Visual Program → Per-Asset Art Direction → Production Parameter Closure → Model Prompt / Visible Copy / Production Notes → Provider/Renderer → Agent Review`

The host Agent remains the creative authority. Runtime validates, serializes, compiles, traces, executes and returns missing decisions; it does not invent creative parameters.

## 1. Restore and extend v0.6.6 photography execution depth
For photographic, photographic-generation and photographic locked-source-composite routes, the Agent now authors the route-specific execution depth needed to reproduce the intended result, including where relevant:

- focal length / lens family;
- working distance;
- camera height;
- yaw / pitch / roll or equivalent camera orientation;
- shot size / framing / crop;
- focus plane and aperture / DOF intent;
- shutter / shutter angle and ISO for real-capture or motion routes;
- key / fill / negative fill / rim/background light geometry;
- modifier size / type / distance;
- CCT and WB;
- key:fill / exposure ratio;
- shadow, highlight and exposure policy;
- reflection / flagging / polarization;
- Prelight / test-frame instruction;
- CMF and material response;
- color management and finishing / grade;
- skin-tone metering and deep-skin shadow-detail protection when people are present.

Values that depend on a real Prelight may be marked Prelight-dependent; the system must not invent measured-final facts.

## 2. Production Parameter Closure
New runtime authority: `runtime/cbcc/production_parameter_closure.py`.

Every selected value that changes image/video/composite behavior must be consumed by the correct production object. The closure records:

- selected concrete parameters;
- route applicability;
- required parameter groups;
- missing required parameters;
- missing English render semantics;
- concrete additions compiled into Model Prompt CN/EN;
- locked-source final-composite plate closure;
- project completion vs model-generation blocking status.

A field-name audit is no longer enough. `camera / palette / composition` appearing on both sides does not prove anything; concrete authored values must survive.

When route-specific execution depth is missing, the model prompt is not READY and reports `ART_DIRECTION_EXECUTION_DEPTH_REQUIRED` rather than silently compiling generic prose.

## 3. Locked source product does not mean empty-background prompting
`LOCKED_PIXEL / LOCKED_SOURCE_COMPOSITE` protects the real product layer. It does not delete final-scene design.

The environment plate is authored and prompted around the final composite:

- exact product envelope / occupancy / relative placement;
- front/back depth relationship;
- receiving surface / contact point;
- perspective / lens relationship;
- contact shadow direction, density and softness;
- reflection/specular receiving behavior;
- ambient/key/fill relationship;
- CCT/WB and grade-match target;
- foreground/occlusion relationship where relevant;
- copy/evidence-safe space around the final product.

The model is told not to redraw the locked product itself, while still generating a plate that will integrate the real product as one coherent scene.

## 4. Photography is route-aware, not a universal template
A bug found during this release caused schema field names such as `camera` / `lighting` to make a graphic asset look photographic. This is fixed. Route detection now uses Agent-authored values, not the existence of generic schema slots.

Graphic, illustration, native-text and source/document assets do not inherit fake camera parameters. Photographic assets cannot omit useful camera/light parameters after the Agent selected that route.

## 5. Portfolio Visual Program is first-class Agent authority
The design-quality problem was not only prompt loss. The reviewed KIYUU output also showed portfolio-level sameness: repeated warm-white/ivory fields, repeated left/right relationships and excessive post-composite plate logic.

v0.6.32 adds first-class Agent decisions for:

- `PORTFOLIO_VISUAL_PROGRAM_AND_RHYTHM`;
- `PORTFOLIO_VISUAL_DIFFERENTIATION_REVIEW`;
- `PRODUCTION_PARAMETER_CLOSURE`.

The Portfolio Visual Program covers visual territory, carrier mix, product-presence rhythm, scale/density rhythm, composition rhythm, continuity tokens, deliberate breaks, delete/merge logic and transformed reference/Technique mechanisms.

Runtime may detect obvious repeated visual signatures or missing adjacent-asset delta and return them to the Agent. Runtime may not redesign the portfolio itself.

## 6. Platform slot limits are capacity, not quotas
`max 9 images`, `up to 7 images` and similar platform limits no longer imply that all slots should be activated.

An asset must add an incremental purchase decision, evidence job, emotional/context job or native Surface role. Repeated/ornamental/low-information assets should be merged, omitted or redesigned.

## 7. Anti-homogenization requirement
Shared brand continuity is not permission to repeat one composition template.

Before delivery, adjacent assets are reviewed across:

- carrier;
- product presence / role;
- subject/action/evidence plane;
- composition grammar / relative placement;
- scale/depth/occupancy;
- focal path / negative-space shape;
- information density;
- camera/view;
- lighting/material behavior;
- palette role;
- decisive moment;
- deliberate difference and WHY.

A gallery that is merely `warm ivory + left/right split + small corner product + soft light + editorial` is returned for Agent re-authoring unless the repeated geometry has a real commercial reason.

## 8. Full human Design Card visibility
The HTML asset workspace now exposes the execution-depth fields rather than hiding them behind a thin summary. Photography/CMF can show working distance, camera height/orientation, shot size, focus/aperture, modifier/light distance, WB, ratio, exposure, shadow/highlight, reflection/polarization, Prelight, material response, color management, skin-tone execution and other authored fields when relevant.

Production / Assembly also shows Production Parameter Closure status, selected parameters, missing parameters, bilingual render gaps and locked-source plate closure.

## 9. Model Prompt / Visible Copy / Production Notes separation remains
v0.6.31's useful fix remains intact:

- Model Prompt CN is Chinese model-facing generation language;
- Model Prompt EN uses English execution language;
- target-market visible copy stays exact in Visible Copy Block with Chinese human-delivery companion;
- locked-source, layer, provider and assembly rules remain in Production / Assembly Notes unless a visual consequence must be described to the generation model;
- copy rendering uses explicit `MODEL_RENDER / POST_COMPOSITE / HYBRID / NO_VISIBLE_COPY`, not a universal deterministic-post rule.

The correction in v0.6.32 is that separation must be **lossless with respect to generation-relevant decisions**.

## Verification focus
Targeted release acceptance covers:

- concrete photo/composite parameters survive into Model Prompt;
- missing photo execution depth prevents false prompt readiness;
- locked-source composite gets final-composite geometry/light plate instructions;
- non-photographic assets do not receive fake camera requirements;
- bilingual prompt semantics remain separated;
- Product Presence / Agent Art Direction authority from v0.6.30 remains intact;
- portfolio visual program and differentiation review are Agent-owned;
- repeated visual signatures return to Agent rather than being auto-redesigned;
- full Art Direction and closure values are visible in human HTML.
