# Photography + CMF Production Contract

This contract applies to real photography, AI photography emulation, CG and composite work when photographic realism is intended.
Values are product/category-specific; do not force one camera/light recipe across all assets.

## 1. Capture / camera geometry
For each asset specify as relevant:
- capture_mode: real_photo / composite / photoreal_ai / cg;
- lens_focal_length_mm and full-frame-equivalent if needed;
- camera_height relative to product or subject;
- working_distance / subject_distance;
- yaw / pitch / roll or plain-language view angle;
- shot_size and crop policy;
- perspective intent (orthographic-like, natural, compressed, wide-context);
- horizon / vanishing-line behavior;
- product occupancy: height %, width %, group width %, safe margins;
- negative-space region and typography-safe zone;
- focus plane, aperture/DOF intent, macro working distance where relevant.

For real capture also specify shutter/ISO only when useful; exposure consistency and motion needs matter more than arbitrary camera numbers.

## 2. Lighting contract
Specify:
- key azimuth/elevation and relative position;
- modifier type, approximate size relative to subject, and distance;
- key softness / specular size;
- fill source and level;
- negative fill position/strength when useful;
- rim/edge separation when useful;
- background light if independently controlled;
- key-to-fill or contrast target;
- CCT / white-balance intent;
- shadow direction, length, softness and density;
- highlight roll-off / clipping policy;
- reflection control: flags, diffusion, polarization/cross-polarization when appropriate;
- transparent/translucent material lighting strategy when relevant.

## 3. Exposure and skin-tone handling
For people, specify metering priority and highlight protection rather than skin-lightening targets.
For deeper skin tones consider large soft sources, controlled negative fill, edge separation, specular placement and background separation.
Preserve natural skin tone, pores and tonal depth; exposure decisions should retain highlight detail and shadow information.

## 4. Product-material handling
- glossy packaging: control specular strip shape, avoid label washout;
- matte packaging: preserve microtexture without flattening form;
- transparent pump/bottle: use edge/back separation and clean internal reflections;
- metallic/foil: flag reflections and retain legible printed/embossed detail;
- gel/liquid/cream: only represent actual product texture when source evidence exists; otherwise use clearly abstract material metaphors if approved.

## 5. Color management
Specify output color space (often sRGB for commerce unless another surface requires differently), white balance, reference neutral,
product-color fidelity priority and optional color-chart workflow for real shoots. Product/packaging color truth outranks campaign grading.

## 6. CMF
For product and campaign separately record:
- color / HEX or measured reference;
- material;
- finish (matte, satin, gloss, metallic, translucent, etc.);
- texture scale/direction;
- reflection/specular behavior;
- edge/emboss/deboss detail;
- allowed campaign materials and why they support the strategy.

## 7. Styling / human / props
Define styling, wardrobe, hair/makeup, hand grooming, props, set dressing and environmental context from the approved audience/culture strategy.
Props and semantic elements are chosen for narrative function; they are not automatically added to fill empty space.

## 8. Deliverable schema
Each relevant asset should produce a `photography_contract.json` or equivalent section containing the above fields at the precision needed for execution.
