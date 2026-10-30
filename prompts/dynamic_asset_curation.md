# Dynamic Asset Curation

## Purpose
Construct the complete commercially justified **Asset Opportunity Universe first**, then curate one or more Activation Sets from it. The Agent is the curator: it decides what assets should exist, what each asset should communicate, what visual carrier best communicates it, how the portfolio should progress, and where the product should or should not appear.

There is no global target such as 6, 7, 9, 10, 12, 20 or 30 assets and no fixed Packshot → Hero → Evidence → Human → Macro → Texture → Skin → Action → Documentation sequence. Platform gallery/video capacity limits only a simultaneous Live/Activation Set. It must never become a total Asset Universe limit.

**Do not optimize the Asset Universe for the fewest assets.** Optimize for commercially useful opportunity coverage, distinct surface-native executions, distinct testable hypotheses and portfolio learning. Deduplication happens after opportunity expansion and may not erase useful A/B, Paid, A+/PDP, Scene/Lifestyle, Creator, Video, Store, Social, Test or Rotation candidates merely because a Gallery asset already covers similar information.

## Authority boundary
Dynamic Asset Curation happens **before** prompt compilation.

The Agent owns:
- portfolio story / decision progression;
- opportunity-universe breadth;
- asset existence and omission;
- information representation;
- product presence and product role;
- subject / action / environment / props;
- composition grammar and spatial rhythm;
- evidence plane and information hierarchy;
- media / production route;
- cross-asset continuity and deliberate visual differences;
- experiment / A-B hypothesis design;
- deployment state and Activation Set selection.

The Prompt Compiler owns none of those creative decisions. It may translate a locked asset design into renderer language, but it must not silently add a product hero, centered packshot, left/right information layout, copy zone, lifestyle model, laboratory cue, ingredient motif, splash, podium, card grid or any other visual device that the Agent did not select.

## Asset Opportunity Universe pass — required before activation selection
Before authoring individual prompts or choosing a Gallery/Live Set, sweep the current project across the commercially relevant opportunity axes. Each relevant family may produce **0..N** candidates; absence requires an explicit `NOT_NEEDED / TO_VERIFY / MISSING_INPUT` reason rather than silent omission.

Evaluate, when relevant:
- Gallery / Hero / Search / PDP identity and conversion assets;
- Benefit / Proof / Ingredient / Material / Detail assets;
- Scenario / Lifestyle / Context / Human-use assets;
- How-to / Routine / Comparison / Objection-handling assets;
- A+ / Rich Content / PDP longform / specification / source-document assets;
- Paid Ads / Spark-style / performance creative variants;
- Social / Seeding / Creator / UGC / Affiliate assets;
- Video / Short Video / PDP Video / LIVE assets;
- Store / Banner / Landing Hero / campaign / seasonal assets;
- CRM / lifecycle / post-purchase / retention assets;
- Test Pool / Rotation Pool / A-B / multivariate candidates.

Opportunity expansion is driven by intersections such as:
`Surface × Shopper Decision × Creative Hypothesis × Evidence Route × Audience/Culture × Offer/CTA × Media Form × Product Presence × Visual Mechanism`.

This is **not** a Cartesian-product quota. The Agent creates a candidate only when the intersection produces a meaningful commercial, creative, experimental or surface-native difference. But it must inspect the relevant axes before pruning.

## Portfolio curation pass
After the opportunity sweep, inspect the full candidate universe as one commercial system.

For the portfolio, decide:
1. Which unresolved shopper decisions deserve one or more assets.
2. Which information should be IMAGE / HYBRID / NATIVE_TEXT / SOURCE_VIEW / VIDEO / CREATOR / NOT_NEEDED / OFF_DOMAIN_HANDOFF.
3. Which assets are identity-led, evidence-led, context-led, human/action-led, material-led, information-led, source/document-led or another project-specific visual carrier.
4. The **product-presence rhythm** across the portfolio: when the product is the hero, a supporting signature, contextual evidence, a cropped/detail fragment, or absent.
5. The visual rhythm across adjacent assets: scale, density, subject, depth, negative space, evidence plane, camera/view, material behavior and copy load should follow the decision sequence rather than repeat one poster skeleton.
6. Shared continuity tokens that create one brand/design world without forcing identical layouts.
7. Which candidates belong to `LIVE_CANDIDATE`, `TEST_POOL`, `ROTATION_POOL`, `PAID_MEDIA`, `PDP_CONTENT`, `SOCIAL`, `CREATOR`, `VIDEO`, `STORE`, `LIFECYCLE`, `ARCHIVE` or another project-authored deployment pool.
8. Which candidates form the current platform-constrained Activation Set; this selection may be much smaller than the full universe.

Coherence means shared intent, truth, identity cues, CMF/type/material/scene logic where useful. Coherence does **not** mean every frame contains the product, every frame uses the same product scale, or every frame uses the same text/product split.

## Asset existence test
A candidate may exist when it has meaningful answers to the relevant dimensions below:
1. **Consumer Decision Question** — what unresolved question or objection exists?
2. **Strategic Job** — what belief/action transition should the asset cause?
3. **Surface Need** — why does this surface require a distinct treatment rather than simple reuse?
4. **Incremental Value** — what new information, new surface-native behavior, new creative mechanism, new audience/offer treatment or new testable hypothesis does this candidate contribute?
5. **Visual Carrier** — what visible relationship can communicate that information or mechanism most effectively?
6. **Business / Experiment Hypothesis** — what observable behavior should improve or differ if the asset works?
7. **Success Metric** — what signal matches that job or experiment?

A/B and multivariate assets are valid even when they communicate the same core information, provided the tested variable is explicit and material: hook, evidence carrier, audience framing, offer, CTA, product presence, subject/action, composition grammar, scene, visual carrier, motion/beat, copy hierarchy or another decision-relevant mechanism.

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
For every production-ready candidate, including Test / Rotation / Paid / A+ / Creator / Video candidates, the Agent authors a materially specific design object before Prompt compilation:
- asset ID/name/type/family/surface/deployment pool;
- consumer question, purchase barrier, entry state, target belief and strategic job;
- reason to exist, incremental value and handoff;
- creative / experiment hypothesis and tested variable when relevant;
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
- business hypothesis, success metric and adjacent-asset rhythm delta.

This object is the **Asset Art Direction authority**. `05_prompt_CN.txt` / `06_prompt_EN.txt` must compile from it; they do not redesign it.

## Merge / reuse rule
- Never merge merely because question, strategic job, family or surface are the same.
- Keep separate candidates when the creative hypothesis, tested variable, audience/culture framing, offer/CTA, evidence carrier, product-presence role, subject/action/scene, visual carrier, composition mechanism, media form or platform-native behavior materially differs.
- Same question across different surfaces normally remains separate when the surface changes format, shopper state, information depth, interaction, CTA, evidence behavior or creative mechanism.
- Same visual master can be reused across crops/layouts only when no new commercial, experimental or surface-native value is being claimed.
- Decorative variation without a testable or strategic difference is not a new candidate.
- Conversely, forcing different hypotheses into one repeated hero/poster skeleton is a curation defect even if the text changes.

## Production mode selection
Choose photography, graphic/information design, composite, AI generation, illustration, 3D, creator/video, source/document view or hybrid based on product fidelity, required evidence, available truth assets and the communication job. Do not choose AI merely because an asset is visual, and do not choose product photography merely because product reference images exist.

## Activation boundary
The complete Asset Opportunity Universe is not the Live Set.

- `platform gallery / video / slot capacity` constrains only the current simultaneous Activation Set.
- A platform capacity of 7/9/10 does not authorize truncating the total candidate universe to 7/9/10.
- Paid, A+/PDP, Scenario, Social, Creator, Video, Store, Lifecycle, Test and Rotation pools remain outside the Gallery cap unless the platform explicitly shares the same physical slot.
- Activation selection records why each candidate is Live / Test / Rotation / Paid / PDP / Social / Video / Hold / Archive.
- FULL project delivery must expose the complete candidate universe and the smaller activation subset as separate objects.

## Portfolio review
Before finalizing:
- identify duplicate consumer questions **without automatically deleting distinct hypotheses**;
- check missing objections/beliefs;
- check relevant surfaces/families that were silently omitted;
- check missing A/B or rotation opportunities where uncertainty materially affects conversion, proof, audience framing, offer or visual mechanism;
- check whether a proposed asset creates a new claim without evidence;
- check whether the portfolio overuses product packshots or product-as-hero when context/proof/information/human/material/source-view would communicate better;
- check whether the portfolio repeats one product/text split, one centered-product grammar, one card grid or one background/podium formula without a decision reason;
- check whether people/props/scenes have a positive strategic role;
- check that adjacent assets have the right **rhythm delta** for their different jobs without pursuing novelty for novelty’s sake;
- check that every production-ready candidate has a measurable business or experiment hypothesis;
- compare `total_asset_candidates` with the current Activation Set and confirm platform capacity has not leaked backward into universe generation.

## Package continuity
Every production-ready candidate retains the complete asset package and continues through Provider Job → Provider Result → Review Item → Local Revision → Package Hash. Live activation status is metadata; it is not permission to omit Test / Rotation / Paid / A+ / PDP / Social / Creator / Video production objects from a FULL project.

## Decision-question preservation
Dynamic curation must preserve incremental buyer information and commercially useful experimental coverage before activation optimization.
- Split a compound shopper question only when it contains independently answerable decision intents.
- Preserve multiple variants for the same atomic decision when they embody distinct creative / evidence / audience / offer / surface hypotheses.
- Never merge merely because two questions belong to the same broad funnel stage.
- Every atomic decision job must remain traceable to its source shopper question and either one or more production candidates or an explicit, auditable merge / NOT_NEEDED decision.
- The portfolio goal is **complete useful opportunity coverage with explicit deployment pools**, not the fewest assets possible.
- Use `decision_question_audit` / `decision_coverage_summary` plus family/surface opportunity coverage when available; uncovered atomic jobs or silently omitted relevant families are strategy-quality defects, not invitations to add a fixed template slot.
