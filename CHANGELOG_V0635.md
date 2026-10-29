# CBCC v0.6.35 — Native-Reference Provider Integrity

This release closes the execution gap between planning a real-product reference workflow and actually proving that the provider consumed the real product reference image during native generation.

## Real product reference reaches the provider as a native subject input
- `REFERENCE_GUIDED_NATIVE_LOCK` remains the default real-product-visible route.
- Product source files are materialized into the portable Provider Job and transmitted through `vendor_request.source_assets`.
- Native-reference source bindings now retain semantic fields: `usage_role=NATIVE_SUBJECT_REFERENCE`, `source_usage=MODEL_REFERENCE_INPUT`, `reference_input_required=true`, `native_generation_required=true`, `pixel_copy_required=false`, plus fidelity and identity-lock metadata.
- Provider contracts for native-reference generation require these semantic binding fields rather than accepting an untyped generic asset locator.
- External adapter discovery requires `REFERENCE_IMAGE_INPUT` for `AI_REFERENCE_PRODUCT / AI_REFERENCE_HUMAN_PRODUCT` and native-lock fidelity.

## Provider evidence may not be fabricated by Runtime
- For native-reference jobs, Runtime no longer infers or auto-passes `product_reference_input_used`, `native_product_rendered_in_final_output`, or `product_identity_preserved` when the provider did not explicitly report them.
- Missing provider evidence remains `UNVERIFIED` and therefore cannot masquerade as proof that the reference image was consumed correctly.
- Source IDs/hashes used by the provider must also be explicitly reported for native-reference proof instead of being copied from planned bindings and treated as execution evidence.

## Receipt and lineage semantics
- Native-reference generation requires `source_binding_hash` lineage in the production receipt but does not require a pixel-layer manifest.
- `EXACT_PIXEL_COMPOSITE` remains the explicit-only route that requires exact pixel-layer lineage/layer-manifest evidence.
- Historical pixel-layer portability tests now use explicit `EXACT_PIXEL_COMPOSITE`, preserving that capability without redefining normal real-product generation as compositing.

## Authority cleanup
- Removes the lower historical section titled `Product Reference / Fidelity — current authority`; it is replaced by a compatibility note explicitly superseded by v0.6.35.
- Collapses duplicate native provider-mode entries accumulated during iterative migration.
- Current authority remains: visible real product → strong model Reference Input → native final render preserving real product identity; exact-pixel compositing only on explicit request.

## Asset Universe and creative depth remain intact
- Platform gallery capacity limits only the simultaneous live activation set, not the total Asset Universe.
- 20/30/50+ asset candidates, multiple Hero variants, benefit variants, paid ads, A+/PDP/detail modules, banners, social/creator/video and testing/rotation pools remain first-class.
- v0.6.32 production-parameter closure, v0.6.31 Model-Native Prompt separation and v0.6.30 Agent Art Direction/Product Presence authority remain covered by regression tests.
