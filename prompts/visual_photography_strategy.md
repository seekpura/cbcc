# Visual / Art Direction / Photography / CMF Strategy

## Purpose
Translate Product Truth, Positioning, Message Hierarchy, audience/context evidence and Consumer Decision Questions into a **designed visual system** before Prompt compilation. Photography is one execution language inside the visual system, not the whole visual strategy.

The Agent acts as commerce art director: it decides what the portfolio should feel like, which visual carriers answer which shopper decisions, when the product is hero/supporting/detail/absent, and how each asset is composed while remaining part of one coherent design world.

## v0.6.32 execution-depth authority — restore the useful v0.6.6 contract
A visual plan is not professionally complete because it names `warm white`, `soft light`, `85mm`, `editorial`, `product right / text left`, or a carrier. Those are fragments. For every activated asset, the Agent must author enough **concrete execution geometry and material/light behavior to reproduce the intended pixels**, then the Prompt Compiler must consume every selected generation-relevant value.

For a photographic / photographic-generation / source-composite photographic route, author a route-specific starting execution contract before calling the asset READY. When relevant, this includes:
- focal length / lens family;
- working-distance intent;
- camera height;
- yaw / pitch / roll or azimuth / elevation / roll;
- shot size / framing / crop;
- focus plane;
- aperture / DOF intent;
- shutter / shutter angle and ISO when a real-capture or motion route uses them;
- key-light direction, size/modifier geometry and distance;
- fill, negative fill and rim/background light where they materially change form/readability;
- CCT and WB;
- key:fill or exposure ratio;
- shadow density/edge policy;
- highlight roll-off / clipping protection;
- exposure/metering policy;
- reflection / flagging / polarization control when material behavior needs it;
- Prelight / test-frame instruction;
- CMF, material response and environment surface behavior;
- color-management/output-space decision;
- finishing / grade / post look;
- for people: skin-tone metering, deep-skin shadow-detail protection, bounce/reflector/diffusion, hair/wardrobe/makeup/age/body representation when relevant.

Do not invent measured-final values. Use an executable starting recommendation and mark values that depend on a real Prelight/test frame as such. A field may be N/A only with a reason tied to the actual carrier/route; silently omitting a useful parameter is not semantic compression.

### Locked-source composite is still a fully designed photograph/composite
`LOCKED_PIXEL / LOCKED_SOURCE_COMPOSITE` means the product identity layer is not regenerated. It does **not** remove the need to design the final scene.

When a real source product will be composited into a generated plate, the Agent still authors:
- exact final product envelope / occupancy / scale;
- relative x/y placement and crop-safe bounds;
- front/back or multi-object depth relationship;
- receiving surface and contact point;
- perspective/lens relationship the plate must match;
- contact-shadow direction, length, density and softness;
- reflection/specular receiving behavior when relevant;
- ambient/key/fill direction and ratio the product layer must match;
- local color temperature / WB and grade-match target;
- occlusion/foreground relationships if any;
- copy-safe/evidence-safe zones around the final product, not around an imaginary empty canvas.

A plate prompt such as “warm ivory background, reserve space on the right, do not generate product” is incomplete when the final composite geometry/light program is already known. The model-facing plate prompt must describe the **final composite spatial/light system** while explicitly telling the model not to render the locked product itself.

## Portfolio design-quality authority
Platform capacity is not an asset quota. `max 9 images`, `up to 7 images`, or any other slot limit means capacity only; the Agent activates only assets that add a distinct purchase decision, evidence job, emotional/context job, or native surface role.

Before finalizing the portfolio, the Agent performs a visual differentiation review across adjacent assets. Review at least:
- semantic/visual carrier;
- product presence and role;
- subject/action/evidence plane;
- composition grammar and relative placement;
- scale/occupancy/depth;
- focal path and negative-space shape;
- information density / typography relationship;
- camera/view where relevant;
- lighting/material behavior where relevant;
- palette role (continuity token vs dominant repeated field);
- decisive moment;
- deliberate break from the neighboring asset and WHY.

Shared brand continuity is not permission to repeat `warm ivory + left copy/right product + small lower-corner product + soft light` across the gallery. Repetition is allowed only when the Agent can explain why the same geometry is commercially superior for those distinct decisions. Otherwise re-author the weaker assets before delivery.

Use integrated references/cases/techniques as mechanisms, not as templates: retrieve relevant composition, information-design, material, photography, editorial, motion or commerce mechanisms; transform them for the current Product Truth/decision job; record what mechanism changed the actual design. Do not stop at generic adjectives such as premium, editorial, clean, modern or minimal.

## Positive-first principle
Plants, water, laboratory cues, models, hands, props, animals, lifestyle scenes, macro texture, diagrams, typography, source/document views, illustration, 3D and abstract materials are selectable tools. Use them only when `Product Truth + Consumer Question + Platform/Surface + Culture + Creative Strategy` gives them a job. Do not globally ban or require them.

Product images supplied by the user are references/truth inputs. Their existence does **not** mean every visual asset must contain the product.

## Portfolio Art Direction
Explain and decide:
- the perception / emotional-commercial territory the work should create;
- which shopper beliefs the portfolio advances and in what useful sequence;
- what category conventions to keep, challenge or avoid when evidence exists;
- the visual carrier mix across the portfolio: identity / evidence / information / human-action / context / material / source-document / other project-specific mechanisms;
- product-presence rhythm across assets;
- scale and density rhythm across adjacent assets;
- shared continuity tokens: color/CMF, typography, material behavior, image language, scene logic, motion or information-design logic as relevant;
- which assets deliberately break the dominant rhythm and why.

A coherent system does not require repeated composition. The same design direction may contain a dominant product hero, an evidence-led information frame, a human/use crop, a material macro and a no-product educational/source frame when those are the strongest decisions for the portfolio.

## Per-asset Product Presence
For every activated visual asset explicitly decide:
- `planning_state`: HERO_REQUIRED / REQUIRED / SUPPORTING / OPTIONAL / DETAIL_ONLY / FORBIDDEN;
- `product_role`;
- `presence_why`;
- scale relationship if present;
- identity cues that must remain recoverable, if any;
- whether source product files are SUBJECT_REFERENCE, TRUTH_REFERENCE_ONLY, LOCKED_SOURCE_LAYER or NOT_NEEDED.

Product fidelity and product presence are separate decisions. A source can remain factual authority while the product is absent from the frame.

## Per-asset Visual Design
Before camera settings or generation prompts, define:
- visual carrier / semantic carrier;
- decisive moment;
- primary subject and secondary elements;
- action / relationship / evidence plane;
- environment / props / context;
- spatial grammar and focal path;
- scale hierarchy and depth structure;
- negative-space strategy;
- information hierarchy and copy-density role;
- camera/view/crop only when relevant;
- color / material / finish / light behavior when relevant;
- human/casting/styling only when relevant;
- post/finishing look;
- why this design is the strongest answer to this shopper decision;
- what is deliberately different from adjacent assets and why.

Do not start from `text-left/product-right`, `product-left/text-right`, centered hero, card grid or podium. Those are possible outcomes, not default layouts.

## Composition
When the product is present, specify and justify product occupancy / scale. When the product is absent, do not manufacture a product occupancy target.

Specify and justify the relevant geometry:
- subject occupancy / scale relationship;
- negative space;
- focal hierarchy;
- copy-safe / crop-safe zones when final copy needs them;
- shot size or graphic field depth;
- camera height / yaw / pitch / roll when a camera model is relevant;
- foreground/background relationship;
- evidence-to-copy relationship;
- visual rhythm relative to adjacent assets.

The reason cannot be “looks premium”. Tie the geometry to recognition, proof, usage understanding, information clarity, emotional/context relevance or platform crop behavior.

## Lens / perspective / working distance
Use this section only for photographic / camera-based routes.
- Long focal lengths can reduce perspective exaggeration and preserve packaging geometry for product-truth views.
- Wider lenses can show environment/action when context is the commercial job.
- When the product is not the subject, choose perspective around the actual subject/evidence/action rather than forcing product readability.
- Working distance is part of perspective and lighting/reflection control.
State why the chosen combination serves the exact asset.

## Focus / aperture / DOF
Use only when relevant.
- Identity/evidence assets with visible product information may require critical facts to remain readable.
- Context/emotion assets may use selective focus when blur guides attention without hiding required information.
- Human/action assets focus the decisive interaction, not automatically the pack.
- Macro imagery must distinguish actual product texture references from abstract material metaphors.

## Lighting geometry
For photographic or lighting-sensitive routes, explain the relevant key / fill / negative fill / rim / background-light choices:
- direction and size;
- distance/relative softness;
- contrast intent;
- material response;
- label readability only when label visibility is required;
- skin-tone behavior when people appear;
- evidence visibility for the actual subject.

Do not specify “soft light” without saying what it solves.

## CCT / WB / exposure / highlights
- Protect accurate product color when the product is visually present and color accuracy matters.
- Protect accurate skin tone when people appear.
- For no-product information/illustration/source assets, do not invent photographic exposure requirements.
- Use CCT for atmosphere only after required factual/identity color references are protected.
- Define highlight roll-off/clipping policy for relevant white packs, glossy films, transparent containers, metal, skin, glass or reflective printing.

## Reflection / polarization
Use flags, diffusion, angle change and polarization only when reflective behavior is part of the actual asset. Removing all reflection can make glossy or transparent materials look fake; uncontrolled reflection can erase decision-critical information.

## CMF
Treat Color / Material / Finish as both a design-system and execution input:
- color affects hierarchy, contrast and reproduction tolerance;
- material affects transmission/reflection/scattering;
- finish affects specular size and highlight shape;
- CMF can belong to the product, environment, graphic field or all three depending on the asset.

CMF should change design/lighting/background/post decisions where relevant; it is not a reason to force product photography.

## People / casting / styling
Models appear when they answer relevance, usage, scale, fit or social-context questions.
- Preserve natural skin texture and plausible local representation.
- Consider skin tone, hair, age, clothing, body exposure, gestures, religion/festival context and family structure only when relevant evidence exists.
- Do not infer behavior from race/ethnicity.
- Do not add a hand or face merely to make the image look “lifestyle”.

## Shot / Asset Design list
Every visual production row records:
`asset_id → commercial job → consumer question → visual carrier → product presence/role → subject/action/evidence → composition/spatial grammar → exact scale/occupancy/focal path/negative space → camera geometry (if relevant) → focus/exposure (if relevant) → lighting geometry/CCT/WB/ratio/reflection/prelight (if relevant) → CMF/material/color/post → product fidelity/reference role → adjacent-asset delta → WHY → success metric`.

No shot or image exists merely because the package “needs another image”, and no asset inherits the previous asset’s layout merely because it belongs to the same product listing.
