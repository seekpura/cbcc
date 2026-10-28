# CMF / Material-specific Lighting Authority

## Principle
Lighting is a material-description system, not a generic "premium" effect.

Use supplied Color / Material / Finish and real product tests to decide:
- specular vs diffuse response,
- highlight gradient size/shape,
- edge separation,
- reflection-card / flag geometry,
- fill vs negative fill,
- whether polarization helps or destroys truthful cues,
- background luminance relationship,
- texture/embossing visibility,
- color-management reference.

## Typical optical concerns
- Glass/clear: edges/refraction can disappear; front reflections can hide labels.
- Gloss plastic/lacquer: hotspots and broad-source flattening need controlled gradients/negative fill.
- Metal/foil: reflected environment is the "light"; polarization may not remove metallic reflections.
- Matte/paper/soft-touch: texture may need controlled oblique light but should not be exaggerated beyond normal perception.

When CMF is under-specified, require a material test frame. Do not invent a finish.
