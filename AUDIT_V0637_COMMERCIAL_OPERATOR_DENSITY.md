# CBCC v0.6.37 — Commercial Operator Density Audit

## Audit objective

The acceptance bar is not “the capability exists” and not “the gate passes”. The acceptance bar is:

> A cross-border ecommerce operator can open the delivery, understand what to do, and immediately execute listing, image, video, offer, ads, review-driven revisions and production without reconstructing the strategy from diagnostics.

The system must behave like an autonomous senior ecommerce strategy + creative + production agent. Runtime validation protects truth, economics and platform constraints; it must not replace creative authorship with generic defaults or turn normal production decisions into operator-facing permission gates.

## Executive finding

v0.6.36 materially improved continuity, economics integrity, source traceability and reference-guided product generation, but continuity is not yet capability density. The current system is strongest at deterministic analysis and weakest at three interfaces:

1. **Agent authorship → commercial production depth** — several domain prompts remain short policy notes rather than senior-operator playbooks.
2. **Commercial visual intent → final generated asset** — old post-composite / locked-copy assumptions still survive in the base compiler and are corrected by later wrappers. This creates regression paths and weakens integrated generation.
3. **Analysis → operator action** — delivery exposes many contracts, diagnostics and runtime states, but does not yet make “what the operator does next” the primary information architecture.

The architecture currently uses multiple compatibility wrappers to reverse or reinterpret earlier defaults. This is the largest systemic regression risk.

---

## P0 — Integrated native generation authority is not clean at the source

### Current contradiction

The canonical creative prompt document correctly defines four copy routes — `MODEL_RENDER`, `POST_COMPOSITE`, `HYBRID`, `NO_VISIBLE_COPY` — and explicitly says not to force every asset into post-composite typography.

However the legacy/base compiler still contains assumptions equivalent to:

- reserve typography zones for later composition;
- do not ask the image model to render final marketing copy;
- exact copy is deterministically composed after generation;
- `deterministic_text_composition` and locked typography are normal renderer concepts.

Later wrappers overwrite parts of this behavior. Therefore the effective policy is correct only when every wrapper is applied in the expected order.

### Required v0.6.37 authority

**Autonomous Integrated Render Authority**

- Finished commercial visual assets default to one integrated native generation problem.
- Product, market-facing copy, typography, hierarchy, environment, people, props, lighting, material response, information graphics and finishing may all be generated together when that is the best production route.
- The Agent decides whether an asset contains product and/or visible copy from the asset’s decision job and portfolio rhythm.
- Absence is an authored choice, not a system default.
- `POST_COMPOSITE` and exact-pixel compositing remain valid specialist production routes, but they are explicit exceptions chosen for a concrete fidelity, editability, platform or provider reason.
- Missing copy-render choice is not an operator-facing gate. The Agent resolves it internally from asset intent + provider capability + required fidelity.
- Hard blocking is reserved for truth/compliance impossibility, missing mandatory real source inputs for an explicitly locked route, or provider inability to execute the chosen contract.

### Why this matters now

Modern image-generation workflows can render exact copy, preserve reference identity, create structured commercial layouts and support iterative edits. Treating “no text in model output” as the safe default discards current production capability and forces unnecessary assembly complexity.

---

## P0 — Wrapper tower creates policy regression

Current package initialization composes prompt behavior through successive layers including Agent Art Direction projection, model-native prompt conversion, audit correction, human-delivery projection, canonical-status preservation, production-parameter closure and reference-guided authority.

This makes policy precedence difficult to reason about and allows an old default to survive underneath a newer authority.

### Required direction

Move toward one canonical commercial production authority with explicit stages:

`Product Truth + Strategy Authority → Agent Portfolio Curation → Per-Asset Commercial Art Direction → Provider Capability Selection → Commercial Model Prompt → Production Execution → Output QA → Local Repair / Revision → Operator Release`

Compatibility modules may translate old schemas into this authority, but they may not independently redefine generation policy.

---

## P0 — Commercial image prompt density is not yet consistently production grade

A production-grade commercial prompt is not “style + camera + light”. It must express the full commerce problem in model-native language.

### Required prompt density for still/image assets

When relevant, a READY prompt must carry the following authored decisions:

1. **Commerce objective** — shopper state, barrier, belief shift, decision answer, asset role.
2. **Visual thesis** — why this visual idea is the right persuasion carrier for this asset.
3. **Product role** — hero/support/detail/absent; reference role; identity attributes that matter.
4. **Decisive scene/moment** — subject, action, interaction, environment, props, human context.
5. **Composition geometry** — framing, hierarchy, scale, depth, relative placement, eye path, negative space, crop behavior.
6. **Integrated typography** — exact visible copy where model-rendered; placement, hierarchy, font character, alignment, contrast, line count, relationship to product/evidence.
7. **Evidence representation** — what fact/proof appears visually and how it is made understandable without inventing evidence.
8. **Camera / optical grammar** — only where relevant; viewpoint, perspective, focal behavior, focus plane, DOF, distortion intent.
9. **Lighting program** — source geometry, softness/hardness, ratio, shadow/contact policy, specular control, CCT/WB and mood where material.
10. **CMF / physical response** — actual material, transparency, roughness/gloss, liquid/gel/fabric/metal/plastic behavior, reflection and contact realism.
11. **Color system** — product-truth color, brand palette, background relationship, local contrast, grade and output color space where material.
12. **Human execution** — casting logic, body/hand interaction, believable grip/usage, skin exposure, grooming/wardrobe, cultural context when people are useful.
13. **Platform behavior** — aspect ratio, mobile readability, safe zones, crop variants, thumbnail behavior, surface-specific rules.
14. **Finishing** — retouching level, grain/sharpness, highlight rolloff, edge fidelity, microtexture, intended polish level.
15. **Truth boundary** — only constraints that protect verified product identity, claim truth, legal/platform rules or an explicitly selected production route.
16. **Variant hypothesis** — what is intentionally different from adjacent assets and what business question this variant tests.

The prompt should read like a senior creative director / commercial photographer / ecommerce art director briefing a capable current model, not like a JSON field dump and not like a defensive negative-prompt list.

### Anti-patterns to remove

- generic “premium / editorial / soft light / clean background” without material or commerce meaning;
- universal left-copy/right-product layouts;
- universal podium / splash / floating particle grammar;
- a product in every frame merely because the project is ecommerce;
- forced product absence because a compositor exists;
- forced text absence because exact text used to be difficult;
- camera numbers that do not change the image;
- long audit/gate language inside model-facing prompts;
- one-shot generation with no result evaluation.

---

## P0 — Output QA is weaker than transport QA

Provider lifecycle, hashes, receipts and source bindings are comparatively strong. Commercial visual QA is not equivalently strong.

### Required Commercial Visual QA

Every generated candidate should be judged on the output itself, not only the input contract:

- product identity / packaging / geometry / color fidelity;
- visible copy spelling, exactness, hierarchy and mobile legibility;
- first-scan clarity and decision-answer visibility;
- composition and crop safety;
- commercial relevance / conversion clarity;
- material realism, contact shadow, reflection, transparency and physical plausibility;
- hands/body/interaction plausibility when humans appear;
- unwanted artifacts / warping / duplicated objects / malformed labels;
- evidence and claim truth;
- brand continuity without portfolio sameness;
- platform-specific readiness;
- delta versus adjacent/test assets.

A failed candidate should route to the smallest useful correction: prompt revision, local edit, regeneration, copy fix, crop adaptation, source/reference strengthening or provider/model change.

---

## P1 — Seven-tool continuity is not seven-tool depth

### 01 Market Research — strong deterministic substrate, needs stronger operator synthesis

Strengths:
- conservative field normalization;
- source provenance and freshness;
- representativeness boundaries;
- concentration, price-band and configuration analysis;
- separation between deterministic facts and strategy interpretation.

Needed depth:
- operator-ready market opportunity memo, not only analysis objects;
- explicit demand/competition/price/configuration/keyword/customer-voice synthesis;
- decision-impact ranking: “what changes product/offer/listing/creative now?”;
- research stop rule based on decision value;
- competitor pattern → differentiation hypothesis → execution implication;
- confidence and source disagreement handling visible to operator.

### 02 Product Strategy — strong structure, needs sharper commercial choice

Strengths:
- value ladder, evidence boundaries, category strategy, SKU/economics integration.

Needed depth:
- one primary commercial thesis with explicit sacrifices;
- offer architecture and promo logic tied to economics + behavior;
- hero / entry / trade-up / bundle / retention roles only when evidence supports them;
- launch plan and testable decisions;
- clearer conversion from facts into operator actions by channel.

### 03 Listing Creative — strong validation substrate, authoring layer is too thin

Strengths:
- keyword architecture;
- field decision jobs;
- numeric/claim trace;
- localization and transcreation contracts;
- objection routing.

Weakness:
- final-copy and host-copy prompts are policy summaries, not senior ecommerce copywriter systems.

Needed depth:
- field-by-field copy strategy before writing;
- query-intent ordering and semantic coverage without stuffing;
- title information economy;
- benefit → proof → specification sequencing;
- objection and expectation management;
- variant / locale / platform-specific rewrite patterns;
- mobile scan QA and duplicate-information audit;
- final publishable field objects, not only authoring tasks.

### 04 Product Image — strategic depth exists, effective authority is inconsistent

Strengths:
- dynamic asset universe;
- curation and opportunity universe;
- per-asset Art Direction;
- photography/CMF parameter closure;
- source reference bindings.

Weaknesses:
- old post-composite assumptions still live in base compiler;
- prompt quality depends heavily on upstream Art Direction completeness;
- QA focuses more on contract consumption than the actual generated pixels;
- no canonical generate → inspect → repair loop;
- too many readiness statuses can become a substitute for Agent self-resolution.

Needed depth:
- Autonomous Integrated Render Authority;
- commercial prompt density contract;
- provider/model capability-aware prompt adaptation;
- candidate generation and visual comparison;
- output QA and local repair loop;
- portfolio-level visual rhythm and anti-clone evaluation.

### 05 Product Video — planning exists, default narrative is still too generic

Strengths:
- shot objects, subtitle/VO/rights/landing/attribution fields;
- strategy/CMF/photography binding when supplied.

Weakness:
- fallback structure gravitates to a generalized hook → reveal → proof → close → CTA sequence;
- does not yet operate like a creative testing studio with materially different narrative hypotheses;
- limited motion-specific production grammar and first-frame/cover experimentation.

Needed depth:
- narrative hypothesis families derived from shopper tension, not a fixed beat template;
- per-shot action choreography, camera behavior, sound design, text timing and continuity;
- creator-native vs studio vs demo vs POV vs problem/solution vs comparison/evidence routes;
- retention checkpoints and alternate openings;
- cover/first-frame variants;
- production feasibility and asset reuse plan;
- output review for motion continuity, hand/object integrity and subtitle safe zones.

### 06 Advertising Optimization — math/causal routing is good, media-operator depth is thin

Strengths:
- economics-aware CPA/CPC/ROAS logic;
- causal routing: reach → click → PDP → economics;
- no invented benchmark thresholds;
- incrementality boundary.

Weakness:
- current Agent prompt is only a short diagnosis instruction;
- lacks a full media buying operating system: campaign structure, query/audience/placement diagnosis, creative-fatigue state, marginal scaling, test queue, budget reallocation and creative-to-ad lineage.

Needed depth:
- P0/P1/P2 operator action queue with owner, exact change, hold-constant variables and recheck window;
- creative performance decomposition by hook/message/carrier/creator/offer/landing;
- marginal performance and saturation;
- experiment design and minimum decision evidence;
- creative refresh queue tied to content production;
- budget shift recommendations only within economic bounds.

### 07 Review / Return / CS Analysis — routing is useful, semantic intelligence is too shallow

Strengths:
- defect vs communication distinction;
- local revision routing and frozen unrelated layers.

Weakness:
- aggregator assumes semantic categories are already supplied upstream;
- current prompt does not define robust extraction of customer language, severity, frequency, expectation, use context, product/communication responsibility and positive-value mining.

Needed depth:
- raw review/return/CS text → semantic coding with confidence;
- theme clustering and temporal/SKU/variant/source segmentation;
- exact customer-language phrases for copy/creative research;
- defect vs expectation vs misuse vs logistics attribution;
- positive-value mining for message evidence;
- revision backlog mapped to listing/image/video/product/CX;
- pre/post revision verification.

---

## P1 — Prompt registry is broad but uneven in density

The registry has strong anchor prompts for master strategy, market interpretation, listing architecture, visual/photography, dynamic asset curation and canonical prompt compilation.

But many important prompts are only short instructions: advertising diagnosis, feedback routing, measurement iteration, economics/offer, causal design, CMF, production binding, copy iteration and host copy orchestration.

A broad registry with thin entries produces the appearance of capability breadth without the thinking density required for senior execution.

### v0.6.37 rule

Every first-class tool must have:

1. deterministic / programmatic substrate where appropriate;
2. senior Agent authoring prompt;
3. operator-ready output contract;
4. evidence/truth boundaries;
5. measurable next-action loop;
6. direct handoff to downstream tools;
7. regression fixture using a realistic commerce case, not only field-presence tests.

---

## P1 — Operator workspace is still system-centric

The workspace currently shows capability cards, runtime entries, consumers, business outputs, status and economic diagnostics. That is useful for proving the system, but an operator does not primarily need to know which module produced a result.

### Required operator-first IA

The default workspace should answer:

- What are we selling and to whom?
- What is the current commercial thesis?
- What should I publish now?
- What assets do I need now?
- Which exact copy/prompt/script/file do I use?
- What is ready, what is a test, what is blocked by a real hard dependency?
- What should I do today / this week?
- What numbers determine whether we keep, scale, revise or stop it?

Runtime traceability stays available as a secondary inspector.

### Minimum operator objects

- `Launch Board` — priority, owner, action, dependency, artifact, metric.
- `Listing Release` — final localized fields + Chinese companion + keyword/claim trace.
- `Asset Production Board` — each asset’s job, exact copy, model prompt, reference files, output spec, production route, QA state.
- `Paid Test Queue` — hypothesis, creative, audience/query/placement, budget boundary, metric, decision rule.
- `Review Revision Queue` — issue, evidence, responsible layer, exact revision, frozen layers, verification metric.
- `Economics Control Panel` — price, contribution, break-even CPA/CPC/ROAS, promo/commission ceilings.
- `Release Status` — PUBLISH / TEST / NEEDS_HARD_INPUT / HOLD_FOR_COMPLIANCE.

---

## P1 — Gate density must be replaced with autonomous resolution density

Statuses such as `COPY_RENDER_MODE_REQUIRED`, `BILINGUAL_RENDER_SEMANTICS_REQUIRED`, `MODEL_PROMPT_NEEDS_AGENT_DECISIONS` are useful diagnostics inside development. They are poor default operator UX when the Agent has enough context to make the decision itself.

### Required behavior

- Agent resolves normal creative and production choices internally.
- Runtime may surface a diagnostic, but orchestration re-enters Agent authoring rather than asking the operator to select a technical mode.
- Only hard business inputs become operator blockers: unknown product truth that affects a claim, missing actual product reference for an explicitly identity-locked route, unresolved legal/compliance requirement, missing economics required before spending/discounting, or provider failure.

---

## P1 — Regression tests prove structure more than commercial quality

Current tests are useful for schema and policy invariants, but commercial-grade output needs eval fixtures.

### Add representative eval suite

At minimum:

- skincare PDP gallery with exact Malay/English copy and real product references;
- fabric/storage product where material/scale/hand interaction matters;
- hard-goods product where dimensions/compatibility matter;
- TikTok creator video with text, VO, hand interaction and hook variants;
- Amazon MAIN + secondary image set with surface-specific rules;
- multilingual listing with native rewrite and claim preservation;
- ads dataset with creative fatigue + economics constraints;
- raw review/return dataset driving a bounded revision queue.

Evaluate not just presence of fields but business usefulness and visual/copy output quality.

---

## External benchmark implications

Current generation systems support exact text rendering, structured visual composition, reference-based editing, identity-sensitive workflows and iterative edits. Production guidance recommends checking the generated result for text accuracy, identity/product preservation and unwanted changes. Therefore CBCC should optimize for integrated generation + result QA, not pre-emptively remove text/product from generation.

Marketplace and social surfaces also require different asset logic. Amazon MAIN images impose strict product-only rules while secondary images can communicate features and use; TikTok performance creative expects vertical, platform-native, hook-first, text-capable, materially varied and continuously refreshed creative. Surface rules must be authored per asset rather than promoted into global visual restrictions.

---

## v0.6.37 acceptance contract

v0.6.37 is not accepted until all of the following are true:

### A. Authority
- Integrated native generation is the default commercial visual authority.
- Product presence and visible copy are authored per asset.
- Post-composite and exact-pixel modes are explicit specialist routes.
- Normal production choices are Agent-resolved, not operator gates.

### B. Prompt density
- First-class tools have senior-authoring prompts, not policy stubs.
- Image/video prompts contain concrete commercial + visual execution depth when relevant.
- Prompts are model-native and do not leak audit/runtime jargon.

### C. Tool depth
- Every first-class tool produces an operator decision/action object.
- Ads and Review tools are upgraded from deterministic diagnostics/aggregation to full Agent interpretation + execution queues.
- Video has dynamic narrative hypotheses rather than a single fallback beat formula.

### D. Production QA
- Generated outputs are visually inspected/evaluated.
- Failed candidates route to bounded repair/regeneration.
- Provider receipt is not treated as proof of commercial quality.

### E. Operator delivery
- Chinese-first human workspace.
- Exact target-market copy is accompanied by Chinese meaning/usage.
- Publishable/testable assets are one click/object away from their copy, prompt, references, specs and QA.
- Runtime internals are secondary, not the main operating surface.

### F. Regression
- Legacy post-composite defaults cannot leak into integrated generation.
- Realistic multi-category fixtures prove commercial usefulness.
- Existing truth/economics/provider integrity remains intact.

---

## Severity summary

| Area | Current maturity | v0.6.37 target | Severity |
|---|---:|---:|---|
| Market deterministic analytics | 8/10 | 9/10 | P1 |
| Product/economics substrate | 8/10 | 9/10 | P1 |
| Listing validation architecture | 8/10 | 9/10 | P1 |
| Final listing authoring density | 5.5/10 | 9/10 | P0/P1 |
| Visual strategy / Art Direction model | 8/10 | 9.5/10 | P0 |
| Effective image generation prompt | 6/10 | 9.5/10 | P0 |
| Integrated product + copy generation authority | 5/10 | 9.5/10 | P0 |
| Generated-output visual QA / repair | 4.5/10 | 9/10 | P0 |
| Video creative studio depth | 6/10 | 9/10 | P1 |
| Ads operator system | 6/10 | 9/10 | P1 |
| Review intelligence | 5/10 | 9/10 | P1 |
| Provider transport / receipts | 8/10 | 9/10 | P1 |
| Operator workspace direct usability | 6/10 | 9.5/10 | P0/P1 |
| Architecture policy coherence | 4/10 | 9/10 | P0 |

The current product is a capable strategy/runtime framework. v0.6.37 must turn it into a commercially dense operating system that produces actions and assets, not a framework that proves its own contracts.