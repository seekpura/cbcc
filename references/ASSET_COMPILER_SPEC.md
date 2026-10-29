# ASSET COMPILER SPEC

Compiler converts Strategy Authority + Product Truth + Portfolio Curation + per-asset Art Direction + Surface/Asset architecture into independent production folders. It preserves upstream intent and makes execution precise; it does not decide asset count by a fixed template and it does not become a substitute creative director.

## Required strategic inputs
PRODUCT TRUTH / SOURCE TRACE, TARGET CONTEXT, CONSUMER DECISION QUESTIONS, POSITIONING / VALUE PROPOSITION / MESSAGE HIERARCHY, LISTING/SEARCH, CULTURE, VISUAL/ART DIRECTION/CMF/PHOTOGRAPHY, DYNAMIC ASSET ARCHITECTURE, explicit PRODUCT PRESENCE, per-asset VISUAL EXPRESSION / DESIGN CARD and available platform/surface contracts.

## Asset admission / existence
An activated asset must explain:
`Consumer Decision Question → Strategic Job → Surface Need → Incremental Information → Visual Carrier → Product Presence / Role → Business Hypothesis → Success Metric`.

Repeated question + repeated job + repeated surface should merge/reuse by default only when one visual carrier can answer the job without losing information. A cross-surface duplicate needs a materially different platform-native job, shopper state, information depth, interaction or CTA.

## Creative-authority boundary
The compiler consumes a per-asset Art Direction decision. It must not silently invent:
- product-as-hero or product visibility;
- left/right product-copy split;
- centered packshot / podium / card-grid composition;
- lifestyle person or hand;
- lab / ingredient / splash / particle / botanical symbolism;
- a generic ecommerce poster hierarchy.

When a pixel-affecting design decision is missing, preserve that gap in the production-readiness contract instead of hiding it with a reusable fallback composition.

`product_presence = FORBIDDEN` means no product subject/layer is added downstream. Product Truth and source files may still remain available as factual/reference authority without appearing in the rendered frame.

## Traceability
SOURCE → PRODUCT FACT → CLAIM → CONSUMER QUESTION → PURCHASE BARRIER / BELIEF → STRATEGIC JOB → SURFACE NEED → VISUAL CARRIER → PRODUCT PRESENCE / ROLE → ASSET ART DIRECTION → VISUAL/PHOTOGRAPHY EXECUTION → GENERATION/LAYOUT CONTRACT → BUSINESS HYPOTHESIS / METRIC.

## Required per-asset folder
Every activated asset contains all files below:
- `00_asset_manifest.yaml`
- `01_strategy.md`
- `02_visual_spec.md`
- `03_photography_contract.json`
- `04_layout_contract.json`
- `05_prompt_CN.txt`
- `06_prompt_EN.txt`
- `07_generation_guidance.txt`
- `08_copy.md`
- `09_production_notes.md`
- `10_source_trace.md`
- `11_strategy_authority_trace.json`

`02_visual_spec.md` / `04_layout_contract.json` carry the authored visual carrier, product presence/role, subject/action/environment, spatial grammar, hierarchy, evidence plane, copy-density and continuity/difference decisions. These are upstream design authorities, not layouts synthesized by the Prompt Compiler.

`03_photography_contract.json` may carry `NOT_APPLICABLE_OR_NOT_SUPPLIED` for non-photography assets; the file remains to protect package continuity. `11_strategy_authority_trace.json` remains even when upstream Strategy Authority is unavailable and records that status explicitly.

## Positive-first generation contract
Start with the desired result: asset job, visual objective, selected visual carrier, product-presence decision, subject/action/environment, composition/spatial hierarchy, evidence relationship, camera/lens only when relevant, lighting, CMF/color, background, human/culture behavior, approved semantic elements, typography-safe area and platform-surface behavior.

When the product is present, specify only the product scale / identity / fidelity decisions that the authored design requires. When it is absent, do not reintroduce it for generic ecommerce recognizability.

Add `precision_boundaries` only for details that protect product fidelity, claims, rights/safety, current platform/regulatory requirements or frozen revision scope. Plants, water, models, props, laboratory cues, animals and scenes are neither globally banned nor globally required.

## Product fidelity
Product fidelity is distinct from product presence.

For `LOCKED_PIXEL`, if the authored asset actually shows the product, use the real product as the product layer. When a generator cannot guarantee that fidelity, generate only the permitted environment/context/light/shadow/human/layout layer for later compositing.

If the authored asset omits the product, a locked product source remains reference/truth authority only and does not force a visible product layer.

## Prompt-state isolation
Final generation prompts contain only execution-relevant content. Keep workflow state, QA prose, source IDs, evidence grades and version history outside the prompt.

Prompt compilation preserves the locked Art Direction; it does not perform late-stage re-curation.

## Production / review continuity
Each package continues through Provider Job → Provider Result → Review Item → Local Revision → Package Hash. Local revision changes only the approved fields and preserves unrelated strategic/visual layers.
