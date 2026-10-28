# ASSET COMPILER SPEC

Compiler converts Strategy Authority + Product Truth + Surface/Asset architecture into independent production folders. It preserves upstream intent and makes execution precise; it does not decide asset count by a fixed template.

## Required strategic inputs
PRODUCT TRUTH / SOURCE TRACE, TARGET CONTEXT, CONSUMER DECISION QUESTIONS, POSITIONING / VALUE PROPOSITION / MESSAGE HIERARCHY, LISTING/SEARCH, CULTURE, VISUAL/CMF/PHOTOGRAPHY, DYNAMIC ASSET ARCHITECTURE and available platform/surface contracts.

## Asset admission / existence
An activated asset must explain:
`Consumer Decision Question → Strategic Job → Surface Need → Incremental Information → Business Hypothesis → Success Metric`.

Repeated question + repeated job + repeated surface should merge/reuse by default. A cross-surface duplicate needs a materially different platform-native job, shopper state, information depth or CTA.

## Traceability
SOURCE → PRODUCT FACT → CLAIM → CONSUMER QUESTION → PURCHASE BARRIER / BELIEF → STRATEGIC JOB → SURFACE NEED → LISTING/CONTENT ROLE → VISUAL/PHOTOGRAPHY EXECUTION → GENERATION/LAYOUT CONTRACT → BUSINESS HYPOTHESIS / METRIC.

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

`03_photography_contract.json` may carry `NOT_APPLICABLE_OR_NOT_SUPPLIED` for non-photography assets; the file remains to protect package continuity. `11_strategy_authority_trace.json` remains even when upstream Strategy Authority is unavailable and records that status explicitly.

## Positive-first generation contract
Start with the desired result: product truth, asset job, visual objective, composition/geometry/product scale, camera/lens when relevant, lighting, CMF/color, background, human/culture behavior, approved semantic elements, typography-safe area and platform-surface behavior.

Add `precision_boundaries` only for details that protect product fidelity, claims, rights/safety, current platform/regulatory requirements or frozen revision scope. Plants, water, models, props, laboratory cues, animals and scenes are neither globally banned nor globally required.

## Product fidelity
For `LOCKED_PIXEL`, use the real product as the product layer. When a generator cannot guarantee that fidelity, generate only the permitted environment/context/light/shadow/human/layout layer for later compositing.

## Prompt-state isolation
Final generation prompts contain only execution-relevant content. Keep workflow state, QA prose, source IDs, evidence grades and version history outside the prompt.

## Production / review continuity
Each package continues through Provider Job → Provider Result → Review Item → Local Revision → Package Hash. Local revision changes only the approved fields and preserves unrelated strategic/visual layers.
