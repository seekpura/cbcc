# CBCC Conversation Requirement Ledger — current cumulative authority

## Purpose
This file is the cumulative requirement ledger for Cross-Border Commerce Creative. It exists specifically so that a later patch cannot treat the latest user message, latest bug, latest builder or latest test as the whole product specification.

**Every release that changes strategy, research, listing, economics, asset curation, Art Direction, Prompt, production, review, Human Workspace, language or runtime behavior MUST re-read this ledger together with the source contracts named in `SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md`.**

A local fix is invalid if any earlier requirement below disappears, becomes thinner, becomes hidden from the human delivery, or is replaced by a Runtime shortcut.

---

## A. Product / agent operating model

### REQ-001 — Additive-only evolution
Upgrades only add. A fix may not solve one dimension by deleting, compressing, hiding or bypassing another established capability. Historical mature behavior remains part of the current contract unless the user explicitly replaces it.

### REQ-002 — Agent owns the work
The host Agent owns research, strategy, listing, pricing decisions, portfolio curation, per-asset Art Direction, product/text presence decisions, creative hypotheses, production route, Prompt, review and revision. Runtime/Python may validate, serialize, compile, execute, trace, package and test; it must not silently substitute a generic creative template for missing Agent decisions.

### REQ-003 — Auto-complete rather than gate workflow
For FULL projects, audit information, ask at most the small set of genuinely blocking questions when needed, record assumptions, then continue. Normal professional decisions are not converted into user gates. Holds are reserved for truth/compliance/economics/provider conditions that would otherwise force fabrication, illegal publication or incorrect spending.

### REQ-004 — Validation is evidence, not the product
Tests, gates, preflight and PASS counts exist to prevent regressions and prove real downstream effect. They do not replace capability implementation, actual production, human delivery or real-output inspection.

### REQ-005 — Host-native / Skills-only is a first-class production path
FULL projects must be producible through the actual host/plugin path. A hand-authored replacement report, mock workspace or custom shortcut is not acceptable evidence that the plugin path works.

---

## B. Commercial / strategy depth

### REQ-006 — Seven first-class commerce capabilities
Market Research; Product Strategy including Pricing/Economics/Offer; Listing Creative; Product Image; Product Video; Advertising Optimization; Review Analysis remain first-class capabilities. Visual/Prompt work may not push the commercial tools out of the current product.

### REQ-007 — FULL nine-domain decision depth
FULL work preserves the complete decision-depth contract: information completeness/unknowns/assumptions/decision log; Product Truth and claim evidence; platform × region × audience × culture; positioning/value/message/frameworks; visual/photography; platform content matrix; RACE; cultural adaptation; compliance/risk/measurement/priority/next inputs. These are completeness domains, not fixed pages or fixed menu items.

### REQ-008 — Product Truth and claim grading
Separate real product facts / real selling points, perceptible benefits, emotional value and prohibited/unsupported claims. A/B/C evidence grading remains explicit: A = test/certification/reproducible measurement; B = supplier/spec/formula/mechanism bounded support; C = subjective/pending. C may not become a hard claim.

### REQ-009 — Claim → Evidence → Asset traceability
Claims must trace to evidence objects/sources and to the Listing/Asset/Creator/Video/Ad expressions that consume them. “Excel + mechanism” or a source-name label is not enough when a more specific evidence object exists.

### REQ-010 — Platform × market × audience × culture WHY
Major decisions answer WHAT → WHY → EVIDENCE/ASSUMPTION → TRADEOFF → EXECUTION → MEASUREMENT, including why this platform, market/region, audience and cultural context changes the decision.

### REQ-011 — Intersectionality and cultural adaptation
At minimum inspect ethnicity/race × gender × age × income × geography, plus language/religion/lifestyle when relevant. Do not infer behavior from identity stereotypes. Cultural adaptation may change shopper priorities, evidence, copy, people, props, color, composition, CTA and media behavior.

### REQ-012 — RACE / STP-JTBD / AIDA-FABE / 4P-Funnel are execution tools
RACE = Research → Action → Communication → Evaluation. STP/JTBD shape strategy; AIDA/FABE shape content when useful; 4P/conversion funnel shape offer and conversion. They must appear as applied decisions, not glossary definitions.

### REQ-013 — Pricing/Economics input integrity
Unknown product cost, platform/payment fee, fulfillment, affiliate commission, tax, return reserve, CVR or other required inputs remain `MISSING_INPUT/UNKNOWN`. Market price-band evidence is not automatically a KIYUU price recommendation. Break-even CPA/CPC/ROAS require the necessary explicit inputs.

### REQ-014 — Listing is a complete object
Listing covers search → click → identify → understand → proof → fit → objection → trust → action, with final publishable title/keywords/bullets/description/attributes/usage/package/FAQ/claim mapping as relevant. Target-market copy remains exact and publishable.

### REQ-015 — Review / CS / return / search / creator feedback loop
Review Analysis is not a source list. Feedback is classified to root cause, linked to Listing/Offer/Asset/Surface revisions, measured, and fed back into strategy without inventing causality.

---

## C. Language / human delivery

### REQ-016 — Chinese-first without density loss
Human/operator delivery is Chinese canonical unless the user requests otherwise. Chinese transformation must not summarize or reduce business, visual or Prompt depth.

### REQ-017 — Target language + English semantic baseline + Chinese meaning
Target-market consumer copy stays in the market language. Non-English markets retain an English semantic baseline plus Chinese meaning/use in the same business object. English-target markets retain English plus Chinese meaning/use.

### REQ-018 — HTML is a complete human workspace
`index.html` must independently expose the complete useful human delivery. MD/JSON/YAML remain editable/source/machine layers, but the user must not be forced to open them to recover strategy, Listing, Art Direction, Prompt, Production Notes, Evidence or Review that should be visible in the workspace.

---

## D. Asset Universe / curation

### REQ-019 — Open-world Asset Opportunity Universe
Discover commercially justified opportunities before pruning. Platform 7/9/10 slots constrain only the current Activation Set, never the total universe. No fixed minimum or maximum and no “smallest sufficient portfolio” objective.

### REQ-020 — Relevant family omissions require explicit reason
Inspect Gallery/Hero/Search/PDP, Benefit/Proof/Ingredient/Material/Detail, Scenario/Lifestyle/Human-use, How-to/Routine/Comparison/Objection, A+/Rich/PDP longform/source, Paid, Social/Seeding, Creator/UGC/Affiliate, Video/LIVE, Store/Banner/Landing/Campaign, CRM/Lifecycle, Test/Rotation/A-B as relevant. Missing relevant families require `NOT_NEEDED / TO_VERIFY / MISSING_INPUT + WHY`; silent omission is a defect.

### REQ-021 — Variants preserve real hypotheses
Same shopper question/surface may have multiple assets when hook, evidence carrier, audience, offer, CTA, product presence, subject/action/scene, composition, copy hierarchy, motion/beat or another tested mechanism differs. Runtime may not merge them merely because the core message matches.

### REQ-022 — Product Presence is independent from Product Fidelity
Whether the product appears is a per-asset creative/commercial decision. Product can be hero/support/detail/absent as the decision job requires. Real references being available do not imply every asset contains the product.

### REQ-023 — No product-everywhere default
A portfolio where every asset gets a product anchor because a source product exists is a curation regression unless each presence is independently justified. Product-presence rhythm must be authored across the portfolio.

### REQ-024 — Anti-template / portfolio rhythm
Coherence does not mean repeated warm-white + forest-green + left/right product/text + small anchor + soft light + water-film. Adjacent assets must differ where their job differs: carrier, subject, evidence plane, decisive moment, scale/depth, composition grammar, negative-space shape, camera/view, light/material, copy density, motion or platform-native behavior.

---

## E. Integrated commercial visual production

### REQ-025 — Integrated final render is the normal default
Commercial visual generation is normally a complete final-image/final-frame problem. Product, target-market visible copy, typography/layout, scene, people, props, evidence graphics, photography/light, CMF/material and finishing may be generated together when appropriate.

### REQ-026 — POST_COMPOSITE / NO_VISIBLE_COPY / PRODUCT_ABSENT are per-asset routes, not globals
`POST_COMPOSITE`, `EXACT_PIXEL_COMPOSITE`, `NO_VISIBLE_COPY` and `PRODUCT_ABSENT` are professional options selected for an asset because of explicit user lock, truth/compliance, platform rule, chosen professional route or real provider limitation. Historical workflows may not reintroduce them as defaults.

### REQ-027 — Reference-guided native product is the default real-product route
When a visible real product is required and reference images exist, default to `REFERENCE_GUIDED_NATIVE_LOCK`: bind the real product references into the provider job and generate the product naturally inside the complete final composition while preserving real geometry, structure, identity cues, pack color/material and required packaging identity. Exact source pixels are immutable only under explicit exact-pixel intent.

### REQ-028 — Product/text presence decisions belong to curation
The Prompt Compiler must not globally decide “do not generate product”, “leave a product zone”, “do not generate text”, “exact copy later”, “left copy/right product” or similar creative defaults. These decisions come from the Asset Art Direction and provider reality.

### REQ-029 — Visible Copy may be integrated
When the selected route is model-render/integrated and the provider can act on it, exact target-market visible copy and typography/layout belong in the generation instruction. Deterministic/post copy composition remains available when explicitly selected or technically necessary; it is not the global renderer policy.

---

## F. Per-asset Art Direction / Prompt

### REQ-030 — Complete structured Asset Art Direction exists before Prompt
Every production-ready candidate has a structured Art Direction authority, not only a prose Prompt. Relevant fields include business decision, purchase barrier, entry/target belief, WHY, hypothesis/metric/handoff, subject/person/animal/object, action/decisive moment, scene/environment/props, product role/presence, composition/spatial grammar/layout geometry, scale/depth/occupancy, focal path/negative space, evidence hierarchy, copy/typography/localization, culture/inclusion, CMF/material/color, camera/focus/exposure, lighting/prelight/reflection, finishing/output, dynamic timing/motion/audio, portfolio rhythm delta and repair ownership.

### REQ-031 — Photography is selected from the scene, not stamped from a template
Focal length, working distance, camera height/yaw/pitch/roll, shot size, perspective, focus/aperture/DOF, shutter/ISO, key/fill/negative/rim, modifier geometry, CCT/WB, ratio, shadow/highlight, reflection/polarization, Prelight, skin metering, color management and finishing are authored only when relevant and derive from the specific visual intention. Repeating f/8 / ISO100 / 1/125 / 5200K / 2:1 across unrelated assets without scene reasoning is a defect.

### REQ-032 — People/inclusion are full execution objects
When people appear, relevant role, age, skin tone, hair/texture, grooming/makeup, wardrobe/accessories, body/age/disability, cultural/religious presentation, pose, expression, gaze, hands, product interaction and scene relationship are authored. Inclusion includes casting, exposure, beauty-standard risk and AI-bias review, not a one-line principle.

### REQ-033 — Prompt is a lossless model-facing projection, not the whole design object
Prompt compilation consumes the already-authored Art Direction. It must preserve all selected pixel/frame/audio-changing values relevant to the chosen route while keeping source authority, file paths, QA labels, revision workflow and internal runtime state in their proper semantic planes.

### REQ-034 — Prompt must not collapse to camera/style words
Camera-only, style-only, product+background-only or a few commercial-task lines are inadequate. Prompt density must reflect the full selected scene, subject/action, composition, evidence, typography when integrated, culture, CMF/material, lighting, platform behavior and dynamic direction relevant to the asset.

### REQ-035 — Prompt parameter consumption audit
For activated/production-ready assets, selected generation-relevant values must be auditable from structured Art Direction into Model Prompt CN/EN or the proper production plane. A field-name/heading check is not enough; use concrete values and `missing_decisions=0` (or an equivalent zero-loss result) for the selected route before calling the Prompt READY.

### REQ-036 — Four production objects stay distinct and complete
Every production-ready asset retains Model Prompt CN, Model Prompt EN, Visible Copy Block and Production/Assembly Notes. Production Notes contain source/reference/fidelity/provider/editability/assembly/output boundaries; they must not become a dumping ground that makes the Model Prompt visually thin.

---

## G. Materialization / production / review

### REQ-037 — Full per-asset package, not five-file shortcut
The mature per-asset package and its machine/human trace objects remain materialized. Host shortcuts may not replace the compiler/export path with only `design_card + prompt CN/EN + visible copy + notes` while silently dropping manifest, strategy, visual spec, photography/layout contracts, source trace, strategy trace, prompt contract and other mature package objects.

### REQ-038 — Provider → Result → Review → Local Revision → hash lineage
Production continuity must carry the selected final prompt/reference/visible copy into the real Provider Job; preserve Provider Result; create Review Item; apply the smallest responsible local revision; and retain lineage/hash/provenance. A prompt file is not a produced asset.

### REQ-039 — Actual-output QA
QA is performed on real generated/shot/composited output and checks product identity/geometry/packaging, copy accuracy/readability, first-scan answer, composition/crop/safe-zone, material physics, hands/body/skin, scene/props, evidence/claim truth, artifacts, motion/audio/subtitles, platform readiness and portfolio redundancy. Planned QA text is not evidence of passed output QA.

### REQ-040 — Smallest repair route is per actual defect
Text errors, product geometry, hand/anatomy, skin exposure, material reflection, crop/safe-zone, motion continuity and provider limitations route to the smallest responsible layer (typography/local edit/mask/prompt/reference/product regen/provider change/full regen) rather than blindly regenerating everything.

### REQ-041 — Measurement / learning closes the loop
Review/measurement/feedback can update the responsible Listing/Asset/Offer/Strategy layer when evidence supports it. Learning may not overwrite immutable truth or claim evidence and may not pretend correlation is causation.

---

## H. Human Workspace / information architecture

### REQ-042 — Preserve mature routed interaction
Keep the mature routed workspace interaction floor: one primary work surface at a time, real project-object routes, local subviews/lenses, independent `asset/<id>` details, search, copy, back/hash, responsive behavior and print/PDF projection.

### REQ-043 — No permanent capability-menu shell
Product / Market / Listing / Strategy / Visual / Assets or any other capability taxonomy may not become a permanent global menu merely because the Runtime has those modules. The information architecture is authored from the current project objects. Runtime may provide project identity/home/searchable object switching as a fallback, not dictate the whole workspace.

### REQ-044 — Operations view is additive, never a replacement
Current priority / next action / operator execution may be useful routed objects, but may not replace full strategy, Listing, Visual/Video, Economics, Ads, Review/Evidence or per-asset detail.

### REQ-045 — FULL business objects remain deep
Economics, Ads, Review/Evidence, Listing, Product Truth, Content, Video/Creator/LIVE and other currently relevant objects retain their professional depth in Human HTML. A thin summary under Strategy or Assets does not count as preservation.

---

## I. Release / source continuity

### REQ-046 — Re-read cumulative user requirements before every relevant release
Before modifying the project, read this ledger plus the current source contracts. New long-form user requirements must be merged into this ledger or an explicitly referenced successor in the same release. The latest turn is never assumed to replace earlier requirements unless the user says so.

### REQ-047 — GitHub main is the ongoing source of truth
Project updates are applied to `seekpura/cbcc` rather than living only in conversation ZIPs. Release/plugin artifacts are built from and reconciled back to the repository authority.

### REQ-048 — Installed-plugin parity is real evidence
After updating the plugin, re-read the actual installed release: manifests, current Skill, deep Skill/resources authority, VERSION and the Runtime files changed by the release. Source intent or local ZIP contents alone are not proof.

### REQ-049 — Real FULL regression fixture required
A release that claims to fix FULL behavior must run at least one representative real FULL project through the actual public path and inspect its final package/workspace/prompts/output state. Synthetic/unit tests prove local logic only; they do not prove Host authoring/materialization/provider behavior.

### REQ-050 — The 2026-10-30 K01 package is a negative regression fixture
The uploaded `KIYUU_K01_Malaysia_TikTok_CBCC` package demonstrates prohibited regressions: simplified five-file assets, globally composite/no-text behavior, product on every asset, repeated visual mechanisms, fixed capability navigation, incomplete structured Art Direction, shallow FULL domains and no real Provider/Review/QA/Revision result. Future releases must not accept an equivalent output as FULL-complete.

---

## Mandatory companion authorities
- `references/MASTER_CONSTRUCTION_CONTRACT.md`
- `references/PROMPT_ART_DIRECTION_MASTER_CONTRACT.md`
- `references/BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md`
- `references/HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md`
- `references/ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md`
- `references/SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md`
- `references/AUTHORITY_SOURCE_PARITY_LOCK.md`
- current canonical Skill and current loading map

## Acceptance principle
A requirement is not satisfied because its sentence appears in a document. For the layer it governs, require evidence in the actual authored object, compiled object, Human Workspace, Provider Job/Result, Review/Revision or installed plugin as appropriate. **Rules without consumed output evidence are only intent, not completion.**
