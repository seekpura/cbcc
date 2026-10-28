# CBCC v0.5.14 — Real Production Quality Preflight

## 1. Production failure addressed
The previous pipeline correctly froze strategy packages and routed providers, but provider execution could still receive too little operational information. In particular, a production job could know the package hash and QA booleans without receiving a sufficiently explicit contract for exact product-master use, decision-specific visual information shape, copy-to-evidence relationship, Photography/CMF intent and locally editable layers.

That gap creates practical failure modes: different assets converge on the same centered-product composition, product packaging is redrawn or beautified, copy becomes detached from visible evidence, and a one-field revision turns into a full-image regeneration.

## 2. Source product master binding
`build_project` now normalizes `source_product_assets` and writes `artifacts/source_product_assets.json`.

A local file is hashed and marked `HASH_VERIFIED_LOCAL`. An external provider handle may be accepted only with a declared hash and is marked `EXTERNAL_HANDLE_HASH_DECLARED`. Hash mismatch or missing source file is retained as an explicit non-ready state.

For LOCKED_PIXEL assets, the master contract preserves:
- product master pixels;
- logo;
- packaging print / label text;
- product geometry and proportions;
- product color identity.

Authorized transforms are limited to the supplied master contract, normally proportional scale, placement, masking/cropping and compositing.

## 3. Decision-specific visual production signature
Each asset carries a visual grammar derived from the actual shopper decision rather than a fixed asset order. Examples:
- IDENTIFY → identity-led hero, pack/label recoverability and deliberate negative space;
- PROOF → evidence-led hierarchy with traceable approved proof;
- USAGE → action/process relationship where the product participates in the operation;
- FIT_WEAR → on-body fit relationship;
- SIZE_CAPACITY → dimension / contents relationship;
- SEAL_LEAK → closure mechanism + orientation;
- CARE_MAINTENANCE → maintenance action / part-state relationship.

The exact count and sequence remain question-driven. This is not a Packshot → Hero → Proof → Human template.

## 4. Provider execution contract
A Provider Job now contains:
- frozen package and package hash;
- production contract hashes;
- exact source product asset IDs;
- locked-pixel rule;
- primary decision job;
- visual information grammar;
- decision-critical evidence plane;
- differentiation axis;
- target-surface production contract;
- copy-visual alignment contract;
- Photography/CMF contract;
- editable/frozen layer contract;
- required evidence-bearing result observations.

Provider substitution of the real product master is explicitly disallowed.

## 5. Result evidence, not checkbox completion
The old product/fact/claim/visual/culture/platform QA booleans remain for compatibility, but v0.5.14 production quality also requires structured observations with status and evidence for the dimensions relevant to that asset.

For LOCKED_PIXEL, the provider must also return the source product asset IDs used and the product-layer operation, such as `COMPOSITE_LOCKED` or `PLACEMENT_ONLY`. A boolean `true` without observation evidence is insufficient for the new quality dimensions.

## 6. Local revision scope
Review requests are translated from leaf fields into semantic layers. Examples:
- `headline_copy` → `typography_copy`;
- `composition` → `layout_spacing`;
- `spoon_presence` → `prop_context`;
- `logo` → frozen product identity and therefore held.

A local revision remains an overlay bound to the parent package hash; it does not mutate the base `00–11` package.

## 7. Learning routing
Observed production failures are routed to the smallest plausible execution layer. Product-master identity failures do not automatically rewrite Product Truth. Same-layout/homogeneity failures route to visual asset differentiation. Photography/CMF failures route to the photography execution layer. Copy-visual mismatch routes to visual attribution unless separate evidence implicates the copy itself.

## 8. What has and has not been validated
The runtime contract has been mechanically exercised with a test-only bound master and explicit provider-result observations to prove that the handoff/ingest/revision semantics work. That fixture is not evidence of real visual quality and is not shipped as a real product output.

No claim is made that v0.5.14 has already achieved RC-quality real image/video output across products. That requires exact product masters plus actual Provider outputs, independent review and local revisions.
