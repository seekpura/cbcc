# CBCC v0.5.11 — Integration Audit

## 审计结论

本审计回答的不是“仓库里有没有这个文件”，而是：**能力结果有没有真正改变或约束 Strategy Authority、Dynamic Asset、Final Copy、单资产生产合同、Provider Job 或 Measurement / Revision Routing。**

- v0.5.10 不能诚实地称为“全部核心能力已完成接线”：市场证据质量没有真正进入 reconciliation 权重，Ads/Feedback 缺显式 Strategy Revision Routing，Market Search/Review/Competitor → Dynamic Asset 仍依赖手工 `market_theme_fit`。
- v0.5.11 已补完上述三条数据流，并增加 Runtime `capability_integration_map.json`。
- 综合压力项目中，当前定义的核心 Runtime 能力没有 `INTEGRATION_GAP`。这不等于“所有外部系统都内置”：Host 文案生成与 Provider 执行仍是外部执行边界，Runtime 负责合同、版本、审校、冻结与结果回收。
- QA / lint / validator 不计作战略能力；它们仍作为后台护栏。

## 核心能力接线矩阵

| Capability | Stress project status | Actual consumers |
|---|---|---|
| `PRODUCT_TRUTH` | `INTEGRATED_ACTIVE` | Strategy §2 Value Ladder; Compliance; Listing/Asset/Final Copy truth boundary |
| `MARKET_COMPETITOR_CUSTOMER` | `INTEGRATED_ACTIVE` | Strategy §3 Market; Strategy §4 Quality-weighted Evidence Reconciliation; Market Evidence Fit Contract → Asset Architecture after explicit fit |
| `SOURCE_ADAPTER_RESEARCH_QUALITY` | `INTEGRATED_ACTIVE` | Market analysis; Evidence-quality weighting; Research refresh/risk register |
| `PRODUCT_SKU_OFFER_ECONOMICS` | `INTEGRATED_ACTIVE` | Strategy §4 Product/SKU/Offer; Ads economic guardrails; Strategy §9 portfolio/incrementality |
| `POSITIONING_MESSAGE` | `INTEGRATED_ACTIVE` | Strategy §4 Positioning/Message; Listing Strategy; Platform Content Matrix; Asset Portfolio |
| `LISTING_SEARCH` | `INTEGRATED_ACTIVE` | Strategy §4 Listing; Dynamic Asset objection inputs; Claim/source trace |
| `FINAL_COPY_WORKFLOW` | `INTEGRATED_ACTIVE` | Final Copy packages; Author/Revision/Review tasks; Delivery Builder |
| `HOST_COPY_AUTHORING` | `INTEGRATED_INACTIVE_NO_PROJECT_INPUT` | Copy version creation; Hard-check rerun; Version-bound re-review |
| `ADS` | `INTEGRATED_ACTIVE` | Strategy §9 diagnostics; Strategy Revision Routing |
| `FEEDBACK` | `INTEGRATED_ACTIVE` | Dynamic Asset communication issues; Strategy §9 local revision routing |
| `EXPERIMENT_CAUSAL` | `INTEGRATED_ACTIVE` | Strategy §9 causal design; Measurement architecture |
| `CULTURE_INTERSECTIONALITY` | `INTEGRATED_ACTIVE` | Strategy §3/8; Casting/visual/copy implications |
| `VISUAL_PHOTOGRAPHY_CMF` | `INTEGRATED_ACTIVE` | Strategy §5; Asset 02/03 contracts; Provider production contracts |
| `DYNAMIC_ASSET_CURATION` | `INTEGRATED_ACTIVE` | Strategy §5 portfolio; 00–11 per-asset packages; Provider jobs when production requested |
| `KNOWLEDGE_ONTOLOGY_PROMPTS` | `INTEGRATED_ACTIVE` | Section authority bindings across 01–09 |
| `COMPLIANCE` | `INTEGRATED_ACTIVE` | Strategy §9 risk; Claim/source publication boundary; Execution readiness |
| `ASSET_COMPILER` | `INTEGRATED_ACTIVE` | Per-asset 00–11 production packages; Package validation |
| `PROVIDER_PRODUCTION` | `INTEGRATED_ACTIVE` | Frozen Provider Jobs; Provider Result ingestion; Review workspace |
| `REVIEW_LOCAL_REVISION_PACKAGE_HASH` | `INTEGRATED_ACTIVE` | Asset package hash binding; Review workspace; Local revision scope; Provider result/package-hash validation |
| `MEASUREMENT_REVISION_INTEGRATION` | `INTEGRATED_ACTIVE` | Strategy §9; Decision Index; Local revision candidates |

## 三个 v0.5.10 真实接线缺口及修复

### 1. Evidence Quality → Strategy Reconciliation

- **旧状态**：freshness / coverage / representativeness / scope metadata 已存在，但 Strategy reconciliation 主要按 signal pressure 解释。
- **v0.5.11**：EvidencePriority 现在显式消费 source-id traceability、freshness、representativeness metadata、scope match、caller-declared source quality，以及跨来源 agreement / conflict。
- **边界**：不根据品牌知名度或“看起来权威”自动创造 source prestige。
- **验证**：保持同一 `brew preparation × 100` 评论信号不变，仅改变证据质量；弱/旧/错范围 evidence 的 weighted evidence 为 **6.0**，Category Prior 仍以 `DIETARY_FIT` 排第一；强/新/范围匹配 evidence 为 **108.0**，`TASTE_PREP` 可以上升到第一。

### 2. Market Evidence → Product Truth Fit → Dynamic Asset

- **旧状态**：需要调用方手工提供 `market_theme_fit`。
- **v0.5.11**：Search / Review / Competitor evidence 自动形成 `MarketEvidenceFitContract` 候选，但在 Host 明确确认 Product Truth fit 之前 **不会**创建资产。
- 综合项目：确认前 market-fit assets = **0**；确认 1 个候选后 approved jobs = **1**，market-fit assets = **1**。

### 3. Ads / Feedback → Strategy Revision Routing

- **旧状态**：诊断主要停留在 Measurement/Section 9 或 Feedback 分析。
- **v0.5.11**：统一输出 `strategy_revision_routing.json`，明确 `edit_layers` 与 `freeze_layers`，避免一次低 CTR / 低 CVR / CS 问题触发全案重写。
- 综合项目生成 **4** 条局部 revision routes，来源为 **ADS, FEEDBACK**。

## Knowledge / Ontology / Prompt 的真实消费

- 新增 `PROMPT-EVIDENCE-QUALITY-WEIGHTING` / `KNOW-EVIDENCE-QUALITY-WEIGHTING`。
- 修复 Adapter-only Market 输入的 domain 派生顺序：通过 `research_source_adapters` 激活的 Market 现在同样选择 Evidence Quality / Category Reconciliation Authority，不再出现“数据进了 Market、专业 Authority 没激活”的半接线。
- 新增 `PROMPT-REVISION-INTEGRATION` / `KNOW-REVISION-INTEGRATION`。
- 新增 `EvidenceQualityWeight`、`MarketEvidenceFitContract`、`StrategyRevisionRoute`、`CapabilityIntegrationMap` ontology 对象。
- 五个历史 strategy-depth knowledge documents 已补稳定 ID；`selected_knowledge` 不再出现 `null` Authority ID。

## 旧 Calculators / Toolkits 的定位

### Canonical strategic/runtime engines

`runtime/cbcc/tools/market.py`、`economics.py`、`listing.py`、`ads.py`、`feedback.py`、`experiment.py`、`source_adapters.py` 等是 Runtime 的计算/分析真源，由 `compiler.py` 直接调用。

### Compatibility CLI — 已统一到底层 Runtime

- `toolkits/01_market/market_metrics.py` / `tabular_ingest.py` → canonical market engine。
- `toolkits/02_pricing_economics/unit_economics.py` → canonical economics engine。
- `toolkits/03_listing/listing_compile.py` / title/spec tools → canonical listing engine。
- `toolkits/06_ads`、`07_feedback`、`08_experiment` → canonical runtime engines。
- v0.5.11 又把根目录 `calculators/market_metrics.py`、`unit_economics.py`、`ad_economics.py`、`experiment_metrics.py` 改为兼容入口并委托 canonical runtime；不再维护第二套业务公式真源。

### QA-only guardrails — 故意不进入战略推理主线

`validate_cross_module.py`、`validate_visual_semantics.py`、`validate_asset_map.py`、platform registry validators 等用于发布前一致性检查。它们的价值是阻止坏交付，不应该被包装成 Market / Positioning / Creative Strategy 能力。

## External execution boundaries — 不是“未集成”，也不能伪称内置

- **Host Final Copy**：Runtime materialize author/revise/re-review tasks、版本和术语合同；真正的语言生成/母语审校由 Host/专业模型返回。没有响应时保持 `TO_AUTHOR` / `DRAFT_REVIEW_REQUIRED`。
- **Provider execution**：Runtime materialize frozen Provider Jobs + package/contract hashes；外部 Provider 是否执行必须通过显式 result ingestion。综合项目 materialized 8 jobs，但 `execution_authorized=false`。
- **Live data acquisition**：Source Adapter family 已进入 Runtime，但 ZIP 本身不是平台私有 API 客户端；它消费 Host/Connector/API 提供的 scoped evidence，并保留 source/cursor/checkpoint/quality lineage。

## 结论

在 **当前定义的 CBCC 核心 Runtime 范围** 内，v0.5.11 已把此前发现的主接线缺口补齐；综合项目 `integration_gaps=[]`。以后新增任何工具/知识文件，如果没有明确消费者和下游产物，就不能宣称“已集成”。

这不是 RC 结论。RC 仍需要多真实商品、真实当前数据、Host Copy 循环和 Provider Result 回收的端到端业务验证。
