---
name: cross-border-commerce-creative
description: Positive-first cross-border commerce strategy authority with product truth, market/SKU/economics, positioning, culture, listing, visual/photography, dynamic assets, production handoff and learning.
version: 0.6.12-portable-provider-package-production-receipt
---

# Cross-Border Commerce Creative — Hard Contract Strategy → Creative → Production Build

## Purpose
Create a professional cross-border ecommerce plan **before** governance machinery becomes visible. The user-facing mainline is positive commercial design: understand the product, market and shopper; decide positioning and message architecture; design platform-native content, visual and photography; compile dynamic assets; then use evidence/platform/compliance/review as background guardrails.

## v0.6.12 可携带 Provider Package + Production Receipt
- 外部 Provider Job 必须自包含执行资源：LOCAL_FILE_PATH 商品母版在 handoff 时复制到 job `inputs/product_masters/` 并重绑为 `PACKAGE_RELATIVE_PATH`；Provider handle 保持显式 handle。
- 冻结资产包复制到 `inputs/asset_package/`，原 package hash 继续作为策略/设计合同 lineage；job.json 不再依赖 CBCC 主机绝对路径执行。
- 外部 `result.json` 必须带 `production_receipt`，绑定 job_id、asset_id、provider、package_hash、portable_manifest_hash、source_binding_hash 与输出文件 SHA256。
- LOCKED_PIXEL receipt 必须带 `layer_manifest` 证明真实商品层来自正确 source asset/hash 且保持 frozen；REAL_PHOTO / VIDEO receipt 必须带真实 `capture_metadata`，不得虚构 EXIF。

## v0.6.11 商品母版绑定 + 冻结层修订执行
- LOCKED_PIXEL 的真实商品母版必须以机器可执行 `source_product_bindings` 进入 Renderer Recipe 与 Provider Job；每个 binding 至少包含 asset_id、resolver/locator、SHA256、pixel_lock、allowed_transforms 与 identity_features。
- Provider handoff 不得只信 compile-time ingest 状态：LOCAL_FILE_PATH 在发单时重新检查文件存在与 SHA256；PROVIDER_ASSET_HANDLE 必须带已声明 SHA256。不可解析的真实商品母版使真实商品生产进入 HOLD。
- LOCKED_PIXEL Provider Result 必须回报 `source_product_asset_ids_used`、`source_product_hashes_used`、`product_layer_operation`、`product_identity_preserved`，并回显 `source_binding_hash`；ID/hash lineage 不一致进入 Review。
- Local Revision 除 `changed_fields` 外还必须回报 `changed_layers`；任何 frozen product-identity layer 被报告修改都触发 `FROZEN_LAYER_MUTATION_REPORTED`。
- Provider contract 对所有 LOCKED_PIXEL 模式（包括 GRAPHIC_DESIGN）要求 source-product binding，不再只对摄影/合成模式声明输入。

## v0.6.10 视觉执行边界 + 锁定文案隔离
- `approved_visual_elements`、`precision_boundaries`、`editable_layer_contract` 与 `product_fidelity` 是逐资产生产执行合同；不能只停留在 Design Card / JSON，必须在 Render Prompt 与人类 Visual 工作台出现正确的可执行子集。
- Render Prompt 必须明确允许视觉元素、精确边界、可编辑层、冻结层和商品 Fidelity；局部修改只能动明确可编辑层，LOCKED_PIXEL 商品身份层保持冻结。
- `information_design.locked_visible_copy` 是确定性文字合成权威。精确目标市场文案必须留在 `deterministic_copy_overlay` 与人类 Copy 工作台；Surface / Copy Budget 进入图像模型前必须移除 `locked_copy` / `visible_copy` 等精确文案字段。
- 人类单资产工作台的 Copy 阶段直接读取 `information_design.locked_visible_copy`，不再依赖旧 `copy_language` / `copy` 字段或旁路 Markdown 才能看到锁定文案。
- Parameter Trace 新增 `VISUAL EXECUTION BOUNDARIES / EDITABILITY`，用于证明视觉允许项、精确边界和编辑冻结合同真正进入执行层。

## v0.6.9 摄影执行合同连续性
- 显式 `Photography Contract` 是生产执行权威之一。`capture_mode`、完整 `composition` 字典与显式 `color_management` 必须原样进入 Design Card 的 `photography_execution`；不得只抽取旧白名单中的镜头、机位和灯光字段。
- `photography_execution` 必须继续进入 CN/EN Canonical Prompt、Parameter Trace、Machine Visual Contract 与人类单资产「摄影 / CMF」工作区。策划里用于出图的参数，最终必须能在执行层找到。
- Composition 使用开放字典语义：`product_occupancy`、`negative_space`、`subject_clearance` 或未来新增的执行字段均不得因编译器未预登记字段名而丢失。
- 显式输出色彩管理（例如 `output_space=sRGB`、真实商品颜色锁定）优先作为执行合同保留；策略派生的颜色一致性计划可以补充解释，但不能覆盖或吞掉显式合同。
- 仍然禁止把 Asset / Project / Direction ID、RACE、KPI 等内部元数据塞进 Render Prompt；摄影合同连续性只传递真正影响画面生成/拍摄/合成的参数。

## v0.6.8 单资产生产工作区
- 单资产详情页不再复用通用 `module-shell`。每张资产按当前真实内容动态形成 **决策 / Design Card → 画面执行 → 摄影 / CMF → 文案 → Prompt 执行 → QA / 来源** 的生产工作区；缺失阶段不占位，不预设固定阶段数。
- Design Card 概览与购买决策合并为同一个决策对象；Visual Execution 只回答消费者可见关系；Photography / CMF 承接镜头、机位、曝光、灯光、材质与颜色执行。
- 中文 Canonical Prompt 与英文 / 目标模型 Prompt 在同一个执行台核对与复制；Prompt 明确是前序策划参数的执行合同，不是独立创意来源。
- 合同、Parameter Trace、源文件与未知旧版资产内容进入 QA / 来源区，确保追溯完整但不污染最终 Render Prompt。
- 单资产生产阶段数量由真实资产内容动态决定；legacy 资产仍可回收进入 QA，不因新 UI 丢内容。

## v0.6.7 语义工作区 + 中文优先交付
- **默认交付语言是中文（zh-CN）**，除非用户明确要求其他语言。不要因为目标市场是英语、马来语、阿拉伯语等，就把策略、解释、风险、摄影策划或 HTML UI 变成大段外语。
- 区分 `delivery_locale` 与 `target-visible locale`：前者服务项目使用者，后者服务目标消费者。目标市场标题/描述/CTA/搜索词/资产可见文案可按策划使用本地语言，但人类交付必须在同一界面提供中文释义、用途或搜索意图说明。
- CN/EN Canonical Prompt 都要保留：中文 Prompt 是人类生产说明与审阅权威；英文/目标模型 Prompt 是渲染执行载体。任何英文 Prompt 不得成为唯一可读交付。
- `index.html` 不再使用报告式连续章节或“左侧锚点 + 长页面”。它是 **语义化 SaaS Workspace**，不同业务对象不能复用同一套页面骨架：Strategy 使用决策板，Content 使用内容泳道 / 矩阵，Visual 使用方向接触表 + Inspector，Listing 使用横向上架任务工作台，Prompt 使用资产选择器 + 中英双执行面板，Evidence 使用媒体证据墙 + 文档 / 文件账本。页面数量由真实输入动态决定，不固定方向数、内容数或资产数。
- 所有内容仍完整嵌入 HTML；“分页面”只是交互状态，不是把用户赶回 MD。MD/JSON/TXT 继续作为编辑与机器真源。
- 内部英文术语如 Product Truth / Prompt / Surface 可作为小号次级标签，中文名称必须是主要信息层。



## v0.6.5 SaaS delivery + prompt integrity rule
The product is **capability-first, not validation-first**. The runtime must finish the commercial reasoning and production language needed for the user to execute real work; automated checks are maintenance guardrails, never the main user-facing product or a substitute for strategy/creative capability.

The authoritative creative-production chain is now:
`Information Audit → Product Truth / Offer / Evidence → Research (Market / Platform / Audience / Race-Ethnicity-Culture / Competitor) → Action (STP / JTBD / Positioning / Message / 4P / Funnel / Visual / Budget) → Communication (Listing / Creator / UGC / Paid / CRM / Localization) → Evaluation (Metrics / Attribution / A-B / Feedback / Economics / Revision) → Product Visual Intelligence → Creative Opportunity Universe (6–12 mechanisms) → Direction Synthesis / Council → Creative Anchors → Dynamic Surface Architecture → Information Assetization → per-asset Visual Expression → Design Card → Canonical CN/EN Prompt Contract → Provider Job → Review / Local Revision → Learning`.

Required behavior:
- **RACE authority for this Skill is Research / Action / Communication / Evaluation.** Research covers product/market/platform/audience/race-ethnicity-culture/competitor truth; Action converts research into strategy, hierarchy, content, shoot and budget; Communication executes platform-native creator/UGC/paid/owned/localized distribution; Evaluation covers metrics, attribution, A/B, feedback and iterative revision. Do not substitute Reach/Act/Convert/Engage in this project.
- If no creative directions are supplied, first compile a **Creative Opportunity Universe** of 6–12 current-product mechanisms from Product Visual Intelligence, decision intents, Surface needs, reference whitespace/cliches, scale/use/material/risk/system evidence and remote-domain spatial logic. Only then synthesize 3–5 materially different directions. Stable route IDs are compatibility tags, not a fixed style library. Candidate directions must differ in buyer entry, creative thesis, composition grammar, product role, image language, proof mechanism, verbal thesis and/or color world; coherence must not collapse into repeated layout.
- Compile Product Visual Intelligence before downstream production: geometry, structure, materials/finish, transparency/reflectivity, label/identity faces, canonical views, source masters, visual risks and permitted reconstruction. Unknown product facts stay unknown.
- Foundation assets answer **who the product is**; Creative Anchors answer **how the chosen visual system behaves**. Anchors create continuity without forcing identical composition.
- Surface planning is dynamic. Decide whether information belongs in IMAGE / NATIVE_TEXT / HYBRID / SOURCE_VIEW / NOT_NEEDED / OFF_DOMAIN_HANDOFF before turning every useful fact into another image. Product presence is deliberate, not mandatory on every asset.
- Every activated asset receives a materially specific Visual Expression Variant and a full Design Card: shopper question, belief transition, RACE stage, decisive moment, subject/action/environment/props, composition/camera/crop, lighting/CMF/material behavior, information hierarchy, copy/language budget, Surface semantics, source masters, editable/frozen layers and measurement hypothesis.
- `05_prompt_CN.txt` and `06_prompt_EN.txt` are complete canonical production prompts, not thin summaries. They inherit the Design Card, Product Visual Intelligence, Creative Direction/Anchor, Surface contract, Copy contract, Photography/CMF, locale and Product Fidelity boundaries.
- Paid advertising is its own Campaign Architecture with objective, audience state, tension, offer, proof, landing handoff, materially different concepts and test hypotheses. It is not a resized PDP asset. Creator/Video/Live likewise use native hook/demo/proof/objection/CTA logic and rights/usage contracts.
- Exact approved visible copy should use deterministic text composition when precision matters. Image/video generation must not rewrite, translate or invent locked packaging or market copy.
- Preserve existing Market/Competitor, SKU/Economics, Listing, Platform, Culture/Localization, Evidence, Provider, Review, Local Revision and Learning capabilities. This rebase is additive and replaces thin creative/prompt handoff behavior, not those systems.


### Hard business / culture / execution contract
- Evidence grade is authoritative: **A = test report / official certification / reproducible measurement; B = supply-chain specification / formula or ingredient-mechanism support; C = subjective experience / creative hypothesis / pending validation. C must never become a hard claim.**
- Every major strategy decision answers **why this platform, this region, this audience, and—when relevant—this race/ethnicity/cultural context**. Unsupported identity-to-behavior inference is prohibited.
- Claims/compliance are P0. Efficacy, ingredient, certification, price, sales rank/volume and regulated categories (medical/beauty/food/finance and similar) require a separate evidence/compliance boundary; unknown current rules are `待查证`.
- Intersectionality evaluates relevant combinations such as ethnicity × gender × age × income × geography plus language/religion/lifestyle only when they affect representation, access, scene or purchase friction.
- Inclusive photography is P0 where people appear: skin-tone metering, deep-skin exposure/reflector/diffusion, hair texture, body/age/disability representation and AI-bias checks must be executable, not a generic diversity sentence.
- Platform execution includes dimensions/aspect, duration, cover/first-frame, subtitles, music/usage rights, traffic/discovery mechanism, CTA, landing handoff, UTM or equivalent attribution IDs. Unknown current platform mechanisms/rules are `待查证`.
- Localization includes native-language review/back-translation, holiday calendar when relevant, payment/logistics promise, religion/taboo review and local regulation. Unknowns remain `待查证`.
- Resource constraints force tradeoffs: **P0 = failure/claim/identity/compliance risk; P1 = material performance impact; P2 = enhancement.** Cut duplicate/decorative/low-information assets before P0/P1.
- Strategy rows prefer tables and contain **依据 + 取舍 + 可执行动作 + metric** rather than adjectives.
- Before delivery, self-check fabrication, WHY coverage, culture/intersectionality, compliance, metrics/attribution and explicit assumptions.
- Information lock: audit first → at most 10 clarification questions → explicit assumptions → continue under assumptions; ordinary missing information may not stop the whole strategy.
- FULL delivery is not complete unless all nine required sections, the RACE execution table, culture adaptation checklist, platform execution fields, P0/P1/P2 priorities and output self-check are materialized.
- Every delivery package includes a **self-contained offline SaaS-style `index.html` workspace** with task pages (Overview / Product Truth / Market & Audience / Listing / Strategy / Content / Visual & Photography / Asset Library / Prompt Lab / Risk & Compliance / Sources / Archive) plus independent in-HTML asset routes. The HTML contains the full human-facing delivery; Markdown/JSON/TXT remain editable/machine authorities, not required reading.

### Seven first-class commerce tool contracts
The reference seven-agent capabilities are first-class orchestrated tools rather than filename presence:
1. **Market Research** — cleaning/profile, concentration, price bands/valleys, configuration, competitor, keywords, customer voice and source-quality context.
2. **Product Strategy** — product truth/value ladder + SKU roles + pricing/economics + positioning/offer decisions and tradeoffs.
3. **Listing Creative** — keyword architecture → field authoring/decision map → Claim trace → platform/locale transcreation/back-translation → final-copy release contract.
4. **Product Image** — Product Visual Intelligence → creative opportunity/council → dynamic asset architecture → per-asset Design Card / canonical prompts / visual production contracts. Never regress to a fixed nine-image quota.
5. **Product Video** — native hook/script/storyboard/shot plan → video prompt → VO/subtitle/cover/music-rights/CTA/landing handoff with platform timing.
6. **Advertising Optimization** — funnel diagnosis + economics/break-even + creative/audience/placement analysis + P0/P1/P2 actions + attribution/UTM + incrementality boundary.
7. **Review Analysis** — eight commerce feedback classes + misunderstanding detector + defect-vs-communication + fixability + praise/issue ranking + exact reconciliation + local routing back to Listing/Image/Offer/Product.
Tools 6 and 7 feed the smallest responsible layer back into tools 2/3/4; they must not trigger indiscriminate full-plan rewrites.


### v0.6.5 production-parameter integrity
- Strategy-derived photography is executable planning, not decorative prose. When no measured shoot contract exists, provide a category/decision-specific **starting recommendation** for focal length/lens family, azimuth/elevation/roll, working-distance intent, camera height, shot size, focus plane, aperture/DOF, shutter, ISO, key/fill/negative/rim geometry, CCT/WB, light ratio, shadow/highlight policy, prelight, polarization, CMF/material and color consistency. Mark measured/final values as prelight-dependent rather than inventing them.
- Merge photography as **Master → Asset/Video Override → Shot Override**. A local override must not erase unrelated master parameters.
- Every image and video production contract exposes a `parameter_trace` showing how Strategy Authority parameters enter the render contract / prompt.
- Render prompts contain only generation-relevant production language. Asset/Video/Direction/Project IDs, RACE, KPI, audit status and internal scores stay in Design Card / Machine Contract / trace. Internal lead-ins such as `asset for <project>` or `For <project>, synthesize...` are not render instructions.
- Inclusive photography applicability is determined by the **final asset task**, not only by whether the input request explicitly supplied casting. Any person/hand/body relationship activates P0 skin-tone exposure, reflector/diffusion, hair texture, body/age/disability representation and AI-bias controls.
- Claim Authority is normalized **before** positioning/listing/compliance/asset decisions. `APPROVED`, `VERIFIED` or a declared A/B label does not create evidence; only linked A/B support may enter hard/bounded claims or Primary Value.
- Product Truth provenance is field-specific. Do not attach every project source to every fact. Unmapped user facts remain `USER_SUPPLIED_UNMAPPED`.

### Plugin execution boundary
The packaged Python seven-tool runtime is a real local Runtime/CLI capability, but the current private ChatGPT plugin is Skills-only unless a verified `mcp.json` is present. Do not claim that normal ChatGPT plugin chat is directly invoking the Python seven-agent functions. In Skills-only mode, ChatGPT follows the same contracts using host tools. Direct tool invocation requires a separately deployed MCP server.

## v0.5.14 real-production quality rule
A real-product production route is not executable merely because a Provider exists. For LOCKED_PIXEL and other real-product modes, bind exact source product masters with hash lineage first. Missing or mismatched masters remain explicit holds; never silently substitute a generated/reconstructed product.

Every asset must carry a decision-specific visual production signature and semantic editable/frozen layer contract into the Provider Job. Distinct shopper decisions must remain visually distinct through composition grammar, evidence plane, context role and surface-native execution rather than collapsing into one reusable centered-product layout.

Provider completion requires evidence-bearing quality observations for the relevant dimensions (product fidelity, decision visibility, surface usability, copy-visual alignment, Photography/CMF and visual differentiation). Boolean QA remains compatibility metadata, not sufficient production evidence. Local Revision may edit only declared semantic layers and must never alter LOCKED_PIXEL product identity. Production learning should revise the smallest implicated execution layer before escalating Product Truth, Positioning or Offer.

## v0.5.11 integration rule
A capability is **not** considered integrated merely because a file, prompt, knowledge document, calculator, toolkit or test exists. It must have a runtime consumer and materially change or constrain at least one of: Strategy Authority, Dynamic Asset Architecture, Final Copy, per-asset production contracts, Provider Jobs, or Measurement / Revision Routing. QA/lint/validator wrappers remain background guardrails and are not counted as strategy capability.

Evidence-quality reconciliation must weight current market/search/review/competitor signals by declared traceability, freshness, representativeness metadata, scope match, explicit source quality and source agreement/conflict. Market observations require explicit Product Truth fit before creating own-product asset jobs. Ads and Feedback diagnostics must route to local strategy edit/freeze layers rather than trigger whole-plan rewrites.

## v0.5.13 real-product quality rule
A strategy is not professionally deep merely because every framework, asset file or runtime capability exists. Preserve every live consumer decision question through atomic decision coverage, Listing field routing and Dynamic Asset curation. Category priors may sequence questions but may not erase product-specific decisions. Proof contracts must follow the atomic decision topic (for example clinical evidence vs formula fact vs cleaning vs compatibility).

When deterministic Strategy Authority is commercially shallow, materialize `strategy_host_authoring_request.json` and return professional reasoning under `strategy_annotations`. Host/model interpretation may deepen value, Positioning, message hierarchy, Listing/Visual WHY and execution, but must not overwrite Product Truth, claim/evidence ledger, deterministic market/economics/experiment results, exact policy authority, Final Copy release state or asset hashes. Extra numeric Final Copy is allowed only through explicit field-level approved Claim authority.

## v0.5.12 executable production-learning rule
A review-requested Local Revision must be compiled as a separate scope-limited Provider Job; never rewrite the parent `00–11` package in place. Preserve parent package hash, `allowed_fields`, revised output hash and independent re-review. Post-change metrics produce descriptive learning by default; causal credit requires explicit valid causal evidence. Apply learning only to implicated edit layers and keep declared frozen layers authoritative.

Runtime CLI lifecycle: `provider-ingest → review-apply → revision-compile → revision-ingest → review-apply → learning-apply`.

## Canonical mainline
`Information Audit → Product Truth → RACE Research → RACE Action (STP/JTBD/Positioning/4P/Funnel/Visual/Budget) → RACE Communication (Listing/Creator/Paid/Owned/Localization) → RACE Evaluation (Metrics/Attribution/A-B/Feedback/Economics) → Dynamic Asset Architecture → Asset Compiler → Production → Local Revision / Learning`

## Required final strategy deliverables
Every complete strategy project must materialize the following nine sections and explain **WHY** for major decisions:
1. Information completeness, pending confirmations, assumptions and decision log.
2. Product truth audit and value ladder: real selling point / perceived benefit / emotional value / unclaimable item / A-B-C evidence grade / publication status. C-level material is soft-only and cannot be a hard claim.
3. Platform × region × audience × race/ethnicity/culture insight, including intersectionality and stereotype/taboo review.
4. Product/SKU/Offer strategy, positioning, value proposition, message hierarchy, STP, JTBD, RACE, AIDA, FABE, 4P, Funnel, Fogg, Means–End, Signaling, FIRST, Cognitive Budget, Belief Sequence and Commerce Response Ladder.
5. Visual strategy and shoot plan: style/moodboard, composition, role-based HEX + contrast, CMF, lighting direction/CCT/key-fill/soft-hard, focal length, framing, camera position, scene, props, casting/wardrobe/hair/makeup, platform dimensions, shot list, deep-skin exposure/reflector/diffusion and AI-bias controls.
6. Platform content matrix: platform / audience / topic / hook / script structure / visual form / CTA / metric / RACE / culture adaptation + taboo check / dimensions / duration / cover / subtitles / music rights / traffic mechanism / landing handoff / UTM or equivalent attribution / WHY.
7. RACE execution table: stage / objective / action / output / platform / culture check / KPI / WHY.
8. Culture adaptation checklist: adaptation / inclusive representation / stereotype or taboo concern / result / modification / WHY.
9. Compliance/cultural risk, measurement and A/B hypotheses, P0/P1/P2 action plan and next information needed.

## Decision contract
For every major strategy decision use the structure:
`WHAT → WHY → EVIDENCE → CONSUMER LOGIC → PLATFORM LOGIC → CULTURE LOGIC → BUSINESS LOGIC → EXECUTION → MEASUREMENT`.
Frameworks are decision lenses, not forms to fill mechanically.


## Professional-depth rule
A structurally complete report is not enough. Do not stop at generic statements such as “target audience”, “use suitable CTA”, “premium visual”, or “optimize conversion”. The final strategy must convert evidence into a concrete commercial decision and explain WHY. Deterministic tools calculate; the strategy/model layer interprets those results and changes SKU/positioning/listing/content/visual/measurement accordingly.

Use the specialized prompt authorities in `prompts/registry.json` when a domain requires deeper reasoning. The nine-section final report is the synthesis layer, not a substitute for Market, SKU, Listing, Creative, Culture or Measurement reasoning.

## Positive-first policy
Describe the desired commercial and creative result first. Plants, water, laboratory cues, models, props, environments, textures, graphics and motion are selectable creative devices when they serve product truth and the shopper decision. Add precision boundaries only where they prevent factual, rights, safety, product-identity, cultural or platform errors.

## Product truth and value
Keep `Fact → Advantage → Perceived Benefit → Emotional Value → Proof` distinct. A useful strategy idea can exist before final evidence is complete, but publication-sensitive hard claims retain evidence status and cannot silently become product facts.

## Market / Product / Economics tool split
Semantic interpretation and strategy belong to the strategy/model layer. Deterministic tools handle cleaning, aggregation, CR3/CR10/HHI, price/configuration matrices, contribution waterfalls, break-even ROAS/CPA/CPC, listing lint/trace, advertising metrics, feedback aggregation and experiment statistics. Tool results feed strategy; they do not replace reasoning.

## Audience, culture, race/ethnicity and intersectionality
Identity variables may affect representation, casting, language and context when supported by evidence. They are not shortcuts to consumer behavior. Evaluate relevant intersections such as ethnicity × gender × age × income × geography × lifestyle and convert them into concrete copy, casting, styling, scene, gesture, photography and CTA implications with rationale.

## Photography / CMF
When relevant, specify executable contracts for focal length/equivalent, working distance, camera height, yaw/pitch/roll, crop/product occupancy, focus plane/DOF, key/fill/negative-fill/rim, modifier geometry/distance, CCT/WB, contrast, shadows, exposure/highlight protection, reflection/material control, skin-tone metering, output color space, product color fidelity, CMF, styling and props. The plan also explains **why** those choices fit the commercial job.

## Asset package preservation — mandatory
The Strategy Authority is upstream of asset production and must never replace or collapse the established asset package workflow.
Each activated asset retains the complete package:
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

The canonical `00–11` contract remains unchanged for backward compatibility. v0.6.0 adds production-depth companions instead of replacing it:
- `12_design_card.json`
- `13_prompt_contract.json`

`12` carries the complete per-asset commercial/decision/visual/production specification. `13` carries the canonical CN/EN prompt contract, machine visual contract, renderer recipe and QA target used by Provider Jobs.

`03` and `11` stay present even when their content is not applicable/supplied; they carry an explicit status instead of disappearing. Provider Jobs, Provider Results, Review Items, Local Revision records and Package Hash continuity remain part of the workflow.

## Research and platform rules
Missing exact platform/site/category/program rules should not stop the whole strategy. Continue all evidence-supported strategic work and hold only the submission-sensitive decision that depends on the missing rule. Family planning capability never equals exact submission readiness.

## Knowledge / Ontology / Prompt layers
- `knowledge/`: reusable commercial reasoning.
- `ontology/commerce_ontology.json`: shared entities, relations, constraints and processes.
- `prompts/registry.json`: executable strategy/prompt authority references.
- `runtime/`: deterministic and stateful project execution.
These layers prevent all expertise from being buried in one giant prompt.

## Strategy reasoning context
The runtime dynamically selects relevant `knowledge/`, ontology entities/relations/constraints and registered prompts, extracts authority content, binds it to the nine Strategy Authority sections, and materializes `artifacts/strategy_reasoning_context.json`. These layers are runtime-consumed rather than passive documentation. Deterministic tools remain the authority for calculations and Product Truth remains the authority for facts.


## v0.5.10 evidence-commerce reconciliation depth
- Treat Category Commerce Profiles as strategic priors, not unquestioned winners. The runtime reconciles them against scoped Product Truth, own shopper/feedback/behavior evidence and current market/search/review/competitor evidence.
- Evidence may reorder objection, proof, message and platform-expression priorities, but may not create product facts, claims, certifications, price economics or service scope.
- Preserve the authority order: Product Truth / verified policy & evidence → own evidence → current scoped external evidence → category prior → generic fallback.
- Proof hierarchy rows declare evidence conditions and input support rather than treating a category-typical proof format as if evidence already exists.
- Promo response, bundle affinity and repeat/replacement observations are descriptive offer evidence. They may support a test candidate but do not establish causal elasticity, incrementality or a final promotion/CRM cadence.
- Platform × category intersection changes entry logic, information density, proof rule and offer role while keeping Product Truth and evidence priority stable across surfaces.
- Reconciliation decisions must remain traceable through WHAT/WHY/EVIDENCE/CONSUMER/PLATFORM/BUSINESS/EXECUTION/MEASUREMENT.

## v0.5.3+ portfolio / competitor / localization depth
- Competitor intelligence joins source-bounded Listing message/offer/proof observations with explicitly labelled review themes before positioning decisions.
- Multi-SKU strategy evaluates overlap/cannibalization hypotheses, trade-up justification and lifecycle offer roles; no forecast percentage is invented without behavioral evidence.
- Listing transcreation materializes locale × field authoring tasks and audits supplied localized numerical facts.
- Platform Content Matrix now carries locale-specific authoring tasks, beat plans and copy contracts while preserving dynamic asset count.
- Market/review themes may create new Dynamic Asset jobs only after explicit Product Truth fit confirmation.


## v0.5.4 research / behavioral validation / Final Copy depth
- Market/competitor/customer research must preserve source IDs, dates, declared freshness windows, sampling metadata and scope boundaries. Never infer representativeness from N.
- Structural SKU overlap is a hypothesis. Use cross-shopping, switching, cohort and treatment/control evidence to validate portfolio decisions while keeping descriptive behavior separate from causal incrementality.
- `_localized_copy` is an authored draft/source layer, not automatic Final Copy. `_localized_copy_reviews` must explicitly approve native fluency, claim equivalence, platform fit and culture fit before `APPROVED_FINAL`.
- TikTok Shop, Shopee, Amazon and DTC/Shopify use distinct native commerce authoring systems. Reuse Product Truth / Positioning / Message Hierarchy / evidence, not identical copy or beat sequence.
- Preserve `artifacts/listing_final_copy.json` and per-locale Final Copy files in delivery when Listing authoring is present.


## v0.5.5 evidence / incrementality / authoring / surface depth
- Research ingestion defaults to `REPORT_ONLY`; deterministic dedup is opt-in and limited to exact same-source row fingerprints. Cross-source duplicate candidates remain separate provenance evidence.
- Source version lineage records explicit `supersedes` relationships separately from merely observed chronological versions; later is not automatically more truthful.
- Directional switch rates require explicit eligible-from denominators. Shared visitors alone are not a switch or cannibalization rate.
- Holdout calculations may report arithmetic incremental orders/contribution, but do not claim statistical significance; assignment integrity, interference, power and pre-period balance remain experiment-review concerns.
- Localized copy review is version-bound. Any revised version invalidates an older approval until the current version passes hard checks plus native fluency, claim equivalence, platform fit and culture fit review.
- Authoring work is materialized as author / revise / re-review tasks rather than pretending deterministic runtime can judge native-language quality.
- Platform-native logic is compiled at the actual commerce surface, not only at platform-family level.
- Every image asset carries an asset-level photography reasoning chain into `02_visual_spec.md` and `03_photography_contract.json`; the master photography recipe is not treated as a sufficient explanation by itself.


## v0.5.6 adapter / causal / copy / production / CMF depth
- Research adapters may normalize full snapshots or incremental batches into canonical market/keyword/review/competitor datasets. Primary-key change sets and high-watermarks are provenance signals; semantic near-duplicates are review-only and never silently deleted.
- Experiment Strategy Authority reviews assignment/randomization, pre-period balance, MDE/power planning, contamination, spillover and interference before interpreting outcome lift. Arithmetic significance or lift never substitutes for design validity.
- Host/model authoring responses create new locale × field copy versions only. The current version must pass deterministic hard checks and explicit native fluency / claim equivalence / platform fit / culture fit review; old-version approval becomes stale after revision.
- Platform-native strategy must compile a surface production contract covering decision job, first frame/line, safe-zone/copy-density logic, motion/demo/audio/caption logic, product fidelity, reuse-vs-recompose, deliverable intent and measurement. Exact submission limits come from current platform authority, not generic runtime guesses.
- Supplied CMF/material signals must affect shot-level lighting reasoning. Explain key geometry, fill/negative fill, reflection/highlight handling and color management for the actual material response. When finish behavior is unknown, require a material test frame rather than inventing one.
- These additions must flow into the nine Strategy Authority sections and active asset `00–11` packages; they are not sidecar calculators or new Gate systems.


## v0.5.9 category-commerce depth

The Runtime must not stop multi-category specificity at visual style or asset type. It must use the project category family, Product Truth and actual consumer decision questions to compile a **category commerce profile** that can change:

- Listing objection priority and PDP decision order;
- proof hierarchy and proof conditions;
- offer patterns that should be tested, without locking unsupported discounts/services/bundles;
- message sequence and category-specific script structure;
- content cadence as module rotation + refresh triggers, never an invented posting-frequency rule.

Current category families include beauty/personal care, apparel fit, fashion accessory, food/beverage, electronics, home durable, high-ticket durable and general commerce fallback. Category profiles are strategy hypotheses, not Product Truth. They must never create certifications, dietary facts, compatibility, performance evidence, warranty/service scope, delivery/installation promises, returns policy, sensory facts or pricing economics.

Category decision-intent classification must use controlled word/phrase matching. Avoid substring collisions that can manufacture false intent. The generic P0/P1/P2/P3 hierarchy may remain as a cross-category compatibility reference, but category message/proof/objection architecture must be visible in the formal Strategy Authority and Platform Content Matrix.

## v0.5.8 multi-category strategy-specificity depth
- Reuse the commerce decision architecture across categories, **not** one fixed asset sequence, surface mix, visual territory or photography recipe.
- Infer a category execution profile only from supplied product/category context. The profile guides purchase-decision priorities, visual territory and provisional photography planning; it does not create Product Truth or claims.
- Auto-curated purchase questions should be classified into decision intents such as identity, fit/wear, size/capacity, leak/seal, storage/stacking, care, compatibility, material/sensory, proof, relevance and usage. Merge repeated questions only when they solve the same decision intent on the same production surface/family.
- Explicit user-authored asset jobs are authoritative and must not be silently semantically merged.
- Platform-pack capability/surface gaps mark strategy objects as research-required; they do not delete useful strategic surfaces. Submission readiness remains separate from planning eligibility.
- When no explicit photography contract is supplied, category/decision-specific camera and lighting recommendations may be created as `STRATEGY_DERIVED_PHOTOGRAPHY_PLAN`, but must remain `prelight_required` and cannot masquerade as measured execution settings.
- CMF reasoning must respond to material behavior: textile/woven, transparent/glass, glossy, metallic and matte products should not inherit one beauty-style soft-light treatment.
- Multi-category validation is a professional-quality check, not a Gate-count target. If materially different categories produce essentially identical asset portfolios or photography WHY without evidence, treat that as a strategy-homogenization defect.

## v0.6.3 historical human-first delivery note — superseded by v0.6.6
The v0.6.3 rule that HTML must contain the complete human-readable delivery remains valid, but its **Commerce Editorial long-report presentation is superseded**. v0.6.6 authority is the object/task-based offline SaaS Workspace defined at the top of this Skill and in `references/FINAL_OUTPUT_CONTRACT.md` / `references/REPORT_THEME_CONTRACT.md`. Source files remain editable authorities; exact platform categories still require current site-tree evidence and otherwise remain `待查证`.
