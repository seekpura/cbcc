# CBCC v0.6.33 — Reference-Guided Native Product + Dynamic Asset Universe

## Why this release exists
v0.6.32 restored production-parameter depth, but two production semantics were still wrong for real commerce work: platform gallery capacity could still be mistaken for the total asset plan, and legacy `LOCKED_PIXEL / LOCKED_SOURCE_COMPOSITE` language could push real-product assets toward post-composite plates instead of native reference-guided generation.

## Native real-product generation authority
- Default real-product fidelity for visible product subjects is `REFERENCE_GUIDED_NATIVE_LOCK`.
- Supplied real product images are strong model Reference Inputs, not merely QA/truth files.
- The model generates the product natively inside the complete final image while preserving package geometry/proportions, closures/pumps/droppers, logo, brand wording, label layout/recognizable print, color identity and material appearance.
- Camera, perspective, lighting, depth, environment and human context may be re-authored by the Agent and generated natively while product identity remains locked.
- `EXACT_PIXEL_COMPOSITE` is explicit-only: it is used only when the user explicitly requires the original source pixels to remain immutable.
- Legacy `pixel_lock=true / LOCKED_PIXEL / LOCKED_SOURCE_COMPOSITE` inputs migrate to native identity locking unless exact-pixel intent is separately declared.
- Provider contracts require real-product reference bindings and result evidence that the reference input was actually used and the product was natively rendered in the final output.

## Dynamic Asset Universe
- Platform limits such as 7 or 9 listing images constrain only the simultaneous live activation set.
- Total Asset Universe has no fixed count authority. 20, 30, 50+ candidates are allowed when justified by shopper decisions, surfaces, creative hypotheses, testing and rotation needs.
- Multiple Hero variants on the same shopper question/surface are first-class assets: H01/H02/H03 etc. are not merged merely because role/surface/question match.
- Benefit/proof variants, paid ads, A+/PDP modules, rich/detail visuals, store banners, social/creator assets, short video/live assets and campaign/seasonal assets can coexist in the same universe.
- Operational pools include Live Candidates, Test Pool, Rotation Pool, Paid Media, PDP/A+ Content, Archive and Other.

## Human delivery
- Asset manifests preserve `variant_id`, `variant_cluster`, `deployment_state`, `testing_variant`, `test_hypothesis` and `activation_set_id`.
- `index.html` Asset Center groups the Asset Universe by operational pool instead of flattening everything into one gallery list.
- Per-asset Production / Assembly view explicitly shows native product reference generation, Reference Input requirement and whether the final product must be natively generated.

## Regression acceptance
- A 20-asset fixture with gallery capacity 9 remains 20 assets.
- Six Hero variants sharing the same shopper question/surface/family remain six independent Hero variants.
- Native product reference generation removes legacy “empty plate / do not render product” prompt language.
- Exact-pixel compositing remains available only under explicit exact-pixel intent.
- v0.6.32 parameter closure, v0.6.31 Model-Native Prompt separation and v0.6.30 Agent Art Direction/Product Presence authority remain covered by regression tests.
