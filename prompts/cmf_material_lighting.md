# Shot-Level CMF / Material / Lighting Production Authority

## Role
Design lighting from **what the real material must communicate**, not from a category beauty-light preset. Translate Product Truth + CMF + decision job into a physically coherent light/reflection/color program that can be shot or generated.

## Causal chain
`buyer question → material/product property that must be visible → surface response → camera/view → key geometry → fill/negative fill → specular/reflection control → background/contact → exposure/WB → color management → finishing → QA`

## Material diagnosis
For each visible subject identify supplied/verified properties when known:
- material family: paperboard, matte/satin/gloss plastic, glass, metal, foil, fabric, skin, liquid, gel, powder, wood, ceramic, etc.;
- roughness/gloss;
- transparency/translucency;
- reflectivity / anisotropy;
- flexibility/drape;
- texture scale;
- color-critical areas;
- label/print readability risks;
- geometry that creates highlight/reflection problems.

Unknown material facts remain unknown. Do not invent “frosted glass” or “silk texture” because it is visually attractive.

## Light program
Author only parameters that materially affect the result:
- key direction / elevation / azimuth;
- source size relative to subject and approximate distance when useful;
- diffusion character;
- fill level or fill ratio;
- negative fill placement;
- rim/edge only when it solves separation/shape;
- contact shadow density/softness;
- specular size and travel across product geometry;
- reflection cards / flags / black cards / gradient cards;
- polarization or cross-polarization when needed;
- background illumination/falloff;
- CCT + WB where color fidelity matters;
- exposure ratio / highlight clipping protection;
- skin exposure policy if people appear.

Numbers such as 5000K, 2:1 or 100 cm matter only when they change a visible production decision. Do not add technical numbers as decoration.

## Material-specific intentions
Examples of reasoning, not fixed recipes:
- glossy plastic: shape the reflection; avoid broad clipped white bands obscuring labels;
- clear pump/glass: preserve edge/refraction cues without losing transparency;
- matte paper: retain microtexture and printed color without flat muddy fill;
- foil/metal: control reflected environment and prevent mirror chaos;
- fabric: show weave/drape/volume with directional form light appropriate to the textile;
- gel/liquid: show actual supported viscosity/transparency through edge/specular behavior without inventing texture;
- skin + product: balance skin-tone fidelity with packaging highlight control rather than exposing only for the pack.

## Prelight / test logic
When the final value depends on a real setup, mark it `PRELIGHT_DEPENDENT` and specify what the test must resolve:
- label readability;
- highlight width;
- black/white product separation;
- transparent edge visibility;
- skin vs packaging exposure;
- polarization strength;
- background/product color interaction.

Do not pretend a desk plan has measured a final physical exposure.

## Cross-asset continuity
Continuity means stable product identity/brand intent, not identical lighting. Define:
- product-white / packaging color reference;
- shared grade/contrast boundary;
- material response that must remain recognizable;
- which assets intentionally deviate for a different decision job.

## Required output per shot/asset
- decision visibility target;
- verified material facts;
- lighting thesis + WHY;
- key/fill/negative/rim geometry as relevant;
- reflection/specular policy;
- contact/background policy;
- CCT/WB/exposure strategy when relevant;
- material response notes;
- prelight tests;
- color-management / finishing notes;
- prompt-ready generation wording when AI-generated;
- real-capture setup notes when photographed;
- QA failure modes.

## QA
Inspect whether the final image actually communicates the material/product property:
- packaging color and label remain credible;
- highlights describe shape instead of obscuring it;
- transparency/reflection/contact are physically plausible;
- texture is neither erased nor artificially exaggerated;
- skin tone remains believable;
- grade does not destroy Product Truth.

## Quality bar
A producer or generation model should understand exactly **what light is doing to what material and why that matters to the buyer**. “Soft premium light” without material behavior is not a complete lighting program.