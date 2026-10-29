# Dynamic Asset Curation

## Purpose
Create the smallest sufficient **curated commerce portfolio** that answers unresolved purchase decisions across the required surfaces. The Agent is the curator: it decides what assets should exist, what each asset should communicate, what visual carrier best communicates it, how the portfolio should progress, and where the product should or should not appear.

There is no global target such as 6, 7, 9 or 12 assets and no fixed Packshot → Hero → Evidence → Human → Macro → Texture → Skin → Action → Documentation sequence. A category prior may suggest possibilities, but it is never an asset template.

## Authority boundary
Dynamic Asset Curation happens **before** prompt compilation.

The Agent owns:
- portfolio story / decision progression;
- asset existence and omission;
- information representation;
- product presence and product role;
- subject / action / environment / props;
- composition grammar and spatial rhythm;
- evidence plane and information hierarchy;
- media / production route;
- cross-asset continuity and deliberate visual differences.

The Prompt Compiler owns none of those creative decisions. It may translate a locked asset design into renderer language, but it must not silently add a product hero, centered packshot, left/right information layout, copy zone, lifestyle model, laboratory cue, ingredient motif, splash, podium, card grid or any other visual device that the Agent did not select.

## Portfolio curation pass
Before authoring individual prompts, inspect the full requested portfolio as one commercial sequence.

For the portfolio, decide:
1. Which unresolved shopper decisions actually deserve their own asset.
2. Which information should be IMAGE / HYBRID / NATIVE_TEXT / SOURCE_VIEW / VIDEO / CREATOR / NOT_NEEDED / OFF_DOMAIN_HANDOFF.
3. Which assets are identity-led, evidence-led, context-led, human/action-led, material-led, information-led, source/document-led or another project-specific visual carrier.
4. The **product-presence rhythm** across the portfolio: when the product is the hero, a supporting signature, contextual evidence, a cropped/detail fragment, or absent.
5. The visual rhythm across adjacent assets: scale, density, subject, depth, negative space, evidence plane, camera/view, material behavior and copy load should follow the decision sequence rather than repeat one poster skeleton.
6. Shared continuity tokens that create one brand/design world without forcing identical layouts.

Coherence means shared intent, truth, identity cues, CMF/type/material/scene logic where useful. Coherence does **not** mean every frame contains the product, every frame uses the same product scale, or every frame uses the same text/product split.

## Asset existence test
An asset may exist only when it has meaningful answers to:
1. **Consumer Decision Question** — what unresolved question or objection exists?
2. **Strategic Job** — what belief/action transition should the asset cause?
3. **Surface Need** — why does this surface require a distinct treatment rather than simple reuse?
4. **Incremental Information** — what does the shopper learn that existing assets do not already communicate?
5. **Visual Carrier** — what visible relationship can communicate that information most effectively?
6. **Business Hypothesis** — what observable behavior should improve if the asset works?
7. **Success Metric** — what signal matches that job?

## Product Presence Decision — mandatory per activated visual asset
Product presence is a creative/commercial decision, not a default.

Each activated visual asset must explicitly declare:
- `planning_state`: `HERO_REQUIRED | REQUIRED | SUPPORTING | OPTIONAL | DETAIL_ONLY | FORBIDDEN`;
- `product_role`: what the product contributes to this specific decision frame;
- `presence_why`: why showing or omitting the product improves the shopper decision;
- `scale_relationship`: dominant / balanced / subordinate / detail / absent as appropriate;
- `identity_requirement`: which product identity cues, if any, must remain recoverable;
- `source_reference_role`: `SUBJECT_REFERENCE | TRUTH_REFERENCE_ONLY | LOCKED_SOURCE_LAYER | NOT_NEEDED`.

Rules:
- Product Truth / source references can remain available as factual or identity authority even when the product is visually absent.
- `FORBIDDEN` means the product is not a generated/composited subject and no product layer is added by downstream Prompt/Renderer logic.
- `OPTIONAL` does not mean “include by default”; the Agent must still decide whether the final design uses it.
- Proof, ingredient, education, routine, cultural/context, human, material, source/document and information-design assets may legitimately work with supporting, detail-only or absent product presence when that is the strongest communication design.
- Identity/primary hero assets may legitimately require dominant product presence.

## Per-asset Art Direction contract
For every activated visual asset, the Agent authors a materially specific design object before Prompt compilation:
- asset ID/name/type/family/surface;
- consumer question, purchase barrier, entry state, target belief and strategic job;
- reason to exist, incremental information and handoff;
- selected visual carrier / representation;
- product presence decision and product role;
- decisive moment;
- primary subject, action, environment and props;
- composition grammar, spatial rhythm, scale hierarchy and focal path;
- camera/view/crop/orientation when relevant;
- evidence plane and primary/secondary/proof hierarchy;
- copy density / typography role / negative-space strategy;
- lighting, CMF, material behavior and color logic when relevant;
- human/casting/wardrobe/hair/makeup only when the decision job needs people;
- production mode and fidelity/source-reference role;
- editable/frozen layers;
- business hypothesis and success metric.

This object is the **Asset Art Direction authority**. `05_prompt_CN.txt` / `06_prompt_EN.txt` must compile from it; they do not redesign it.

## Merge / reuse rule
- Same question + same strategic job + same surface: merge by default only when the same visual carrier can answer both without losing information.
- Same question across different surfaces: retain separate assets only when native format, shopper state, information depth, interaction or CTA materially changes the job.
- Same visual master can be reused across crops/layouts when no new information is required.
- Decorative variation is not incremental information.
- Conversely, forcing different decision jobs into one repeated hero/poster skeleton is a curation defect even if the text changes.

## Production mode selection
Choose photography, graphic/information design, composite, AI generation, illustration, 3D, creator/video, source/document view or hybrid based on product fidelity, required evidence, available truth assets and the communication job. Do not choose AI merely because an asset is visual, and do not choose product photography merely because product reference images exist.

## Portfolio review
Before finalizing:
- identify duplicate consumer questions and duplicate visual carriers;
- check missing objections/beliefs;
- check surfaces with no useful decision job;
- check whether a proposed asset creates a new claim without evidence;
- check whether the portfolio overuses product packshots or product-as-hero when context/proof/information/human/material/source-view would communicate better;
- check whether the portfolio repeats one product/text split, one centered-product grammar, one card grid or one background/podium formula without a decision reason;
- check whether people/props/scenes have a positive strategic role;
- check that adjacent assets have the right **rhythm delta** for their different jobs without pursuing novelty for novelty’s sake;
- check that every asset has a measurable hypothesis.

## Package continuity
Every activated asset retains the complete `00_asset_manifest.yaml` through `11_strategy_authority_trace.json` package and continues through Provider Job → Provider Result → Review Item → Local Revision → Package Hash. Strategy depth is additive; it never collapses assets into one master document.

## Decision-question preservation
Dynamic curation must preserve incremental buyer information before optimizing asset count.
- Split a compound shopper question only when it contains independently answerable decision intents.
- Merge only when the jobs share the same decision intent, decision topic, surface need and compatible visual carrier, or when one clause is merely a boundary qualifier of the other.
- Never merge merely because two questions belong to the same broad funnel stage.
- Every atomic decision job must remain traceable to its source shopper question and either an activated asset or an explicit, auditable merge target.
- The portfolio goal is the fewest assets that preserve all incremental purchase information **and** communicate it through the strongest project-specific visual system, not the fewest assets possible.
- Use `decision_question_audit` / `decision_coverage_summary` when available; uncovered atomic jobs are a strategy-quality defect, not an invitation to add a fixed template slot.
