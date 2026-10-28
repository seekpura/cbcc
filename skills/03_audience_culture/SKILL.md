---
name: cbcc-audience-culture
description: Build STP, JTBD, race/ethnicity cultural adaptation, intersectionality, inclusive representation and casting constraints without stereotyping.
---
# Audience & Culture

## Inputs
- product_truth
- market / region / city when relevant
- platform
- known audience data
- known race/ethnicity/language/religion/cultural context
- price / channel / lifestyle context

## Process
1. Segment by need, behavior, price sensitivity, lifestyle, geography, culture, usage frequency and product maturity.
2. Select primary/secondary targets; do not reduce targeting to age/gender.
3. Build JTBD: Functional, Emotional, Social, Trigger, Desired Outcome, Anxiety, Purchase Barrier, Switching Barrier, Alternative.
4. Run intersectionality: ethnicity × gender × age × income × geography × lifestyle.
5. Build culture adaptation constraints: language, religion, festivals, taboos, clothing, skin tone, hair, body, age, disability, family structure, gesture/body-contact, props, colors and CTA.
6. Translate findings into casting, wardrobe, hair/makeup, scene, copy and platform implications.

## Rules
- Never infer behavior solely from ethnicity/religion.
- Never use a single identity symbol as shorthand for a whole culture.
- Cultural judgments must be `VERIFIED`, `LIKELY`, `ASSUMPTION`, or `PENDING`, with source/confidence.
- If cultural evidence is missing, state uncertainty; do not invent local norms.
- Inclusive representation is strategic and truthful, not quota decoration.

## Required outputs
- `stp.json`
- `jtbd.json`
- `audience.json`
- `culture_constraints.json`
- `intersectionality.md`
- `culture_adaptation_checklist.md`
- `casting_constraints.json`
- downstream handoff fields for positioning/listing/visual.

## Runtime handoff
`audience_culture` compiles into `culture_context.json`, ContentObject upstream hashes, asset visual implications and casting/copy contracts. Locale typography is resolved through `runtime/cbcc/locale.py`.
