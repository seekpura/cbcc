# Cross-Border Commerce Creative — v0.6.10

CBCC 是跨境电商 Product Truth、市场/竞品/人群、产品/SKU/Offer、Listing/Search、文化本地化、视觉/摄影、动态图片/视频、广告、评论闭环、生产与学习系统。

## 当前权威能力
- RACE = **Research → Action → Communication → Evaluation**；与购物漏斗/行为阶段分离。
- A/B/C Claim Authority：A=检测/认证/可复现实测；B=供应链/规格/配方/机理；C=主观体验/假设/待验证，C 不得硬宣称。
- FULL 策略强制九段输出、交叉性/文化适配、P0/P1/P2、平台执行/归因、输出前自检。
- Product Visual Intelligence → Creative Opportunity Universe → Direction Council → Dynamic Surface/Assets；不固定 9 图/12 图。
- 摄影/CMF/构图/材质/包容性摄影不仅写在策略里，还通过 Parameter Trace 进入每个图片/视频 Render Contract 与 Canonical Prompt。
- Render Prompt 不包含内部 Asset/Project/Direction ID、RACE、KPI 等工程元数据；精确文字后期 deterministic composition。
- 七大本地 Runtime 工具：Market / Product Strategy / Listing / Image / Video / Ads / Review。
- Human Delivery 的 `index.html` 是完整**离线 SaaS Workspace**，而不是 Markdown 索引或长篇流水报告；完整内容仍全部内嵌。
- v0.6.7 开始，Strategy / Content / Visual / Listing / Prompt / Evidence 使用不同的信息架构与交互语法；Content 是一级工作区，主策略第 6/7 章不再塞回 Strategy。
- v0.6.8 将单资产详情升级为独立生产台：Design Card / 购买决策、画面执行、摄影 / CMF、文案、Prompt、QA / 来源按真实内容动态出现，不再复用通用模块页。
- v0.6.9 将显式 Photography Contract 的拍摄/合成模式、完整构图执行字典（含商品占画、负空间与未来扩展字段）、输出色彩管理贯穿到 Design Card、CN/EN Canonical Prompt、Parameter Trace、Machine Visual Contract 与单资产生产台。
- v0.6.10 将 Approved Visual Elements、Precision Boundaries、Editable/Frozen Layers 与 Product Fidelity 贯穿到 Render Prompt 和人类 Visual 工作台；锁定可见文案只保留在 deterministic overlay / Copy 工作台，不再通过 Surface / Copy Budget JSON 泄漏给图像模型。

## 主要入口
- `SKILL.md`
- `runtime/cbcc/compiler.py`
- `runtime/cbcc/claim_authority.py`
- `runtime/cbcc/prompt_compiler.py`
- `runtime/cbcc/video_creator.py`
- `runtime/cbcc/delivery_html.py`
- `runtime/cbcc/tools/seven_agent.py`
- `builders/project_delivery_builder.py`
- `references/FINAL_OUTPUT_CONTRACT.md`
- `references/PLUGIN_RUNTIME_BOUNDARY.md`

## 重要边界
ChatGPT 私有插件当前仍是 **Skills-only**；本地 Python 七大工具尚未通过 MCP Server 暴露给聊天插件。实时平台类目/规则/法规也必须通过当前 Web/API/官方信息获取，离线包缺失时标 `待查证`。
