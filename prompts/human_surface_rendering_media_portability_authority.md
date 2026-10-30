# Human Surface Language + Standalone Media Authority — v0.6.50

## Purpose
This authority fixes a concrete Host-native regression: a package can contain `_cn` fields and source images while the actual `index.html` still renders English-only operator prose and broken relative media. Completion is judged on the **actual human-visible surface**, not field existence.

## A. Chinese-first means rendered Chinese-first
For Chinese-default operator delivery, every human-facing base/operator surface must be understandable directly in Chinese:
- overview/project hub;
- Product Truth, information audit and assumptions;
- market/audience/culture evidence and implications;
- strategy, message hierarchy, framework explanations and tradeoffs;
- visual master, composition, camera, lighting, CMF/material and fidelity explanation;
- asset library cards and asset detail business/visual/production explanations;
- compliance/risk/evidence/operations/A-B/content-matrix views;
- Production / Assembly Notes and other operator instructions.

Foreign technical terms may remain as secondary annotations, e.g. `信息层级（Message Hierarchy）`, `构图（Composition）`. Do not use English-only headings/paragraphs/values as the primary operator layer.

### Allowed foreign-first zones
These may keep original/target language as primary, but still need the required Chinese companion in the same object:
- exact target-market Listing copy;
- exact visible asset copy / hook / subtitle / VO / CTA;
- `Model Prompt EN`;
- raw source quotations/titles when fidelity requires them;
- platform raw keys, proper nouns, technical IDs, INCI/ingredient nomenclature, code and URLs.

A generic English field name such as `composition`, `camera`, `why`, `metric`, `fact`, `effect`, `audience`, `tradeoff`, `production_notes` is **not** an exemption when its value is shown to the operator. If the visible value is foreign-language prose, the same visible object must show Chinese meaning/explanation.

## B. Asset language contract
1. Final consumer-visible language/no-copy route is authored per asset from market/platform/audience/creative strategy.
2. Every production-ready asset has `Model Prompt CN` and **mandatory `Model Prompt EN`**.
3. `Model Prompt EN` execution prose must be English/provider-readable; do not leave Chinese shopper questions/jobs inside the EN prompt except exact target-market copy or proper names that intentionally remain unchanged.
4. If visible copy is non-English, the same asset object keeps exact target-language copy + English semantic baseline + Chinese translation/use explanation.
5. If visible copy is English, keep English exact copy + Chinese translation/use.
6. Text-free assets remain text-free in the final image; English-layer requirements do not force visible English.

## C. Same-object Chinese companion
Do not hide translations in a separate appendix. Listing, asset card/detail, video/creator, ad, market evidence, review/customer voice and production notes must expose Chinese interpretation in the same object or one directly bound subview.

## D. Standalone HTML media portability
`index.html` is a human deliverable and MUST remain usable when opened or previewed by itself.

For every image/video/audio actually displayed in HTML:
- preferred: embed as `data:` URI or equivalent inline/base64 Blob reconstruction in the HTML;
- editable/source originals should still remain in `sources/` inside the package;
- a plain relative `src="sources/..."` **without an embedded fallback is not standalone-safe and fails completion**;
- broken/blank media must not be hidden by a PASS audit.

If the source is too large to inline, provide an intentional embedded preview/thumbnail and a visible source-file link/status. The default product/pack visual used as project identity must have an inline preview.

## E. Final human-surface acceptance
Before completion:
1. open/inspect the final `index.html`, not only its JSON;
2. traverse each primary route and at least one representative detail per object family;
3. verify Chinese-first operator prose on the actual rendered surface;
4. verify foreign target-market copy has same-object Chinese companion;
5. verify every production asset has EN + CN prompt layers;
6. verify EN prompt execution prose is provider-readable English;
7. verify every displayed local media has embedded data/fallback and renders in standalone HTML;
8. only then may `HUMAN_LANGUAGE_AUDIT`, `SOURCE_TRUTH_MEDIA_AUDIT` or equivalent say PASS.

Presence-only audits are invalid. If a package says PASS while the human surface violates these conditions, the audit is itself a failure.
