# Creative Direction → Surface → Per-Asset Art Direction → Prompt System

## Authority purpose
A commerce visual system must produce **coherence without sameness**. The host Agent is the creative authority: it authors portfolio curation, direction synthesis and every activated asset's Art Direction. Runtime may validate, serialize, compile and execute those decisions; it must not originate product presence, subject, composition, camera, lighting, CMF or layout when Agent authority is active.

The selected direction defines shared principles and continuity tokens. Every asset still receives an independently authored visual solution based on the shopper decision it must resolve. Shared direction is not permission to repeat a layout.

## Search before selection — Creative Opportunity Universe
- Before creating directions, explore as many mechanism-level Creative Opportunities as the current project needs. Relevant domains may include product identity geometry, evidence relationships, human decisive moments, material/optical behavior, scale/space calibration, process/sequence, risk/boundary, system/compatibility, package/contents reveal, information hierarchy, category whitespace and remote-domain spatial grammar.
- There is **no fixed opportunity count and no fixed direction count**. Stop when additional exploration is unlikely to create a materially different, evidence-supported option that could change the creative decision.
- Score or reason about mechanisms from Product Visual Intelligence, atomic decision intents, Surface roles, current evidence, material/scale/use/risk/system signals and declared reference whitespace/cliches.
- Borrow mechanisms, never copy a finished reference composition.
- Direction breadth is task-dependent. A direction is useful only when it changes the shopper experience or production logic materially enough to justify comparison.
- Stable downstream route IDs are compatibility tags, not a style library and not a source of creative authority.

## Direction council
Evaluate Product Truth fit, buyer-decision fit, platform/surface fit, culture/localization fit, differentiation, production feasibility and decision coverage. Select a coherent system. Direction-level principles establish continuity; they do **not** overwrite per-asset Art Direction.

When an asset needs a different proof carrier, human action, material study, source evidence, graphic structure, scene or spatial grammar, the Agent authors that difference directly at the asset level.

## Product Visual Intelligence
Compile known product geometry, structure, material, finish, transparency/reflectivity, label/printed faces, canonical views, capture risks and source masters before downstream visual production. Unknown properties stay unknown. Product/source files are truth and identity references according to their declared role; their existence does not force the product to appear in every asset.

## Foundation vs Creative Anchors
- Foundation Assets answer **who/what the product is** when that information needs a dedicated asset.
- Creative Anchors answer **how the selected visual system behaves** when continuity needs a reference.
- Possible anchor roles include Hero Keyframe, Lighting Reference, Material Response and Scene Language, but create only those required by the current project.
- Anchors improve continuity; they never force all assets into one layout, one camera, one product scale or one scene grammar.

## Dynamic Surface Architecture
Asset/surface count is a result of shopper decisions, evidence and platform roles—not a quota. Candidate expressions may include search/listing, hero, gallery, longform/A+, specification/comparison, video, creator/live, paid/social/store, FAQ, CRM and post-purchase.

Before creating a visual asset, the Agent decides whether the information should be IMAGE, HYBRID, NATIVE_TEXT, SOURCE_VIEW, VIDEO, CREATOR, another native carrier, NOT_NEEDED or OFF_DOMAIN_HANDOFF. Precision-heavy warranty/logistics/care content may be better as native text/hybrid than as a dense poster.

**Surface architecture may suggest representation or product usefulness, but that suggestion is not production authority.** Product visibility and visual carrier are finalized by per-asset Agent Art Direction.

## Product presence — Agent decision
Product presence is independent from product fidelity and independent from the existence of source product files.

For every activated visual asset, the Agent explicitly decides a production state such as:
- `HERO_REQUIRED` — product is the dominant identity carrier;
- `REQUIRED` — product must be visible to resolve the decision;
- `SUPPORTING` — product is visible but not the primary subject;
- `DETAIL_ONLY` — only a decision-critical product detail is visible;
- `OPTIONAL` — Agent must still resolve PRESENT or ABSENT before generation;
- `FORBIDDEN` — the product must not appear;
- `NOT_APPLICABLE` — product presence is irrelevant to this carrier.

Also author `product_role`, `presence_why`, scale relationship, identity requirement and `source_reference_role` (`SUBJECT_REFERENCE`, `TRUTH_REFERENCE_ONLY`, `LOCKED_SOURCE_LAYER` or `NOT_NEEDED`) when relevant.

`FORBIDDEN` means no packshot, corner signature, ghost silhouette, podium product or product layer. `TRUTH_REFERENCE_ONLY` means the source can constrain facts/identity without becoming a visible subject.

If product presence is missing, runtime returns `AGENT_ART_DIRECTION_REQUIRED` / `AUTHOR_PER_ASSET_ART_DIRECTION`. It does not silently insert a product.

## Surface copy budget
Use semantic budgets first: primary decision answer, supporting proof and copy layers. Only use hard character/occupancy limits when a current platform rule supplies them. Overflow secondary detail to the next native surface rather than shrinking everything into one frame.

## Per-asset Art Direction / Design Card
Every activated visual asset should be authored independently. The Agent decides, as relevant:
- consumer question, purchase barrier, entry state, target belief and exit state;
- commercial hypothesis, incremental information, success metric and handoff;
- visual carrier and why this carrier is appropriate;
- product presence, product role and why the product is or is not visible;
- decisive moment / first-read relationship;
- subject, action, environment, props and human/casting role;
- composition grammar, spatial rhythm, scale relationships, focal path and negative-space behavior;
- camera/view/crop only when the carrier actually needs camera logic;
- evidence plane, information hierarchy and what must be primary/secondary;
- lighting, material, CMF and color behavior only when relevant;
- typography/copy role and deterministic text boundary;
- production mode, product fidelity, source-reference role and editable/frozen layers;
- continuity tokens shared with the portfolio and deliberate differences from adjacent assets;
- surface-native behavior and local-revision scope.

This per-asset object is the **Art Direction authority**. Direction-level systems and runtime heuristics may not overwrite it.

## Canonical Prompt
The Prompt Compiler is a compiler, not a designer. It translates the Agent-authored Design Card into renderer instructions while preserving Product Truth and execution boundaries.

The causal chain is:

`shopper decision → Agent portfolio curation → selected direction → per-asset Art Direction → product presence / visual carrier → visible evidence relationship → relevant execution parameters → locked copy → Product Truth → Surface behavior → renderer/layer plan`.

If a design decision is missing, expose the missing Agent decision rather than hiding it with a centered hero, left-text/right-product layout, card grid, podium, generic lifestyle scene or automatic packshot.

Exact approved visible text should be composed deterministically when accuracy matters; do not ask image generation to repeatedly retype approved copy.

## Anti-collapse rules
- Do not default to centered product + giant headline + generic cards.
- Do not default to text-left/product-right or its mirrored version.
- Do not repeat the previous asset composition merely to maintain “brand consistency”.
- Do not add splash, particles, laboratory cues, bokeh, chrome, plants or generic lifestyle props unless they solve the current decision job.
- Do not force product presence into every frame.
- Do not convert source-reference availability into visible-product requirement.
- Do not use one “premium” lighting recipe across different materials, people and evidence tasks.
- Do not turn every valuable fact into an image.
- Do not let deterministic intent/surface mappings substitute for Agent Art Direction in FULL visual projects.
