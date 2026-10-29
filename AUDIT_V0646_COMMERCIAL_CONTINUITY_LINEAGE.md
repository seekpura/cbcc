# v0.6.46 商业连续性 / 决策血缘审计

## 结论
当前 v0.6.45 的主要问题不是单个 Prompt 变短，而是 **Authority → Analysis → Decision → Curation → Asset → Prompt → Human HTML** 的连续性被分段实现，且安装包发生 Canonical 缩减。结果是代码能力仍存在，但 Agent 作者化深度、跨工具消费和人类交付投影不稳定。

## P0-1｜安装包 Canonical 被缩减
- GitHub main 根 `SKILL.md` 当前约 91,944 bytes，是项目完整 Canonical。
- 已安装 v0.6.45 的 Host Skill 与 `resources/SKILL.md` 均约 27,658 bytes。
- 正式 builder 原本会把 repo root `SKILL.md` 复制为 `resources/SKILL.md`；当前安装包是历史 overlay 路径，导致 compact wrapper 覆盖/替代了完整 Canonical。
- 直接影响：Agent 在规划阶段不能稳定获得完整 Production Parameter Closure、七工具、市场/价格/区域/人群/RACE、Design Card、摄影灯光 CMF 等权威要求。

### 修复
1. v0.6.46 正式包必须以 repo root `SKILL.md` 作为 Canonical 真源。
2. Host Skill 不得成为一份更薄的平行业务规范；Host 与 Canonical 使用同一完整权威正文或经过 hash 验证的同源版本。
3. package guard 校验 Canonical SHA/size，禁止 silent shrink。

## P0-2｜七工具真实结果被压成 status/count 摘要
`compile_seven_agent_synthesis().asset_inputs` 当前主要保留：
- Market: status + approved-fit count
- Economics: status + currency
- Listing: status + objection count
- Ads: status + diagnostic routes
- Review: status + issue count

真实运营决策载荷没有继续下传：Price Bands / Price Valleys / Price×Configuration / SKU role / contribution / break-even / offer boundary / market segment / audience / culture / search intent / objections / review themes / RACE / measurement 等。

### 修复
新增 `Commerce Decision Context`：保留真实决策值、证据/来源、状态、适用 Surface/Intent 和下游消费者。摘要可以保留，但不得替代 payload。

## P0-3｜asset.commerce_context 到 Prompt Compiler 断链
`compiler.py` 会给资产写入 `commerce_context`，但当前 `prompt_compiler.py` 不读取该字段。因此分析即使进入资产对象，也不会进入 Design Card / Model Prompt / Assembly / QA。

### 修复
- 每个资产生成 `decision_lineage`：只绑定与当前购买问题/Surface/Intent 相关的市场、人群、价格/Offer、Listing、RACE、Ads、Review、Evidence 决策。
- Design Card 显示“上游商业决策与依据”。
- Model Prompt 只消费会改变生成结果的商业决策；追踪/经济公式/后台状态进入 Assembly/Inspector，不污染模型 Prompt。
- continuity audit 检查“有上游绑定但没有真实下游消费者”的断链。

## P0-4｜摄影生产深度代码存在，但作者化输入不稳定
当前 `prompt_compiler.py` 已支持：焦段/镜头族、工作距离、机位高度、yaw/pitch/roll、对焦/景深、快门/ISO、key/fill/negative/rim、CCT、光比、反射/偏振、Prelight、CMF、色彩管理等；但只有上游已有具体决策时才会输出。

由于安装 Skill 变薄，加上资产级 `asset_parameter_reasoning` / `asset_art_direction` 并不总被作者化，Runtime 为避免瞎编参数会留空，因此最终 Prompt 变薄。

### 修复
- 摄影/摄影式生成资产必须在 Agent Art Direction 阶段完成适用参数闭合；未知实拍量标 `PRELIGHT_DEPENDENT`，而不是删除字段。
- 非摄影 Graphic / Illustration / Native Text / Diagram 不强制伪摄影参数。
- 新增 generation-parameter lineage：Art Direction 选定值 → Design Card → Prompt CN/EN → Provider/QA。

## P0-5｜关键运营数据在人类 HTML 中降级到 Machine Archive
当前 HTML 主工作面主要读取 Strategy Markdown、Listing Human Delivery、Asset human files；大量结构化工具输出进入 JSON archive。即使数据文件存在，运营视角仍表现为“丢了”。

### 修复
在 `cbcc-commercial-v1` 内新增项目存在时才出现的商业工作面/局部视图：
- 市场 / 区域 / 人群 / 文化
- SKU / Pricing / Economics / Offer
- Search / Listing / Objection
- RACE / Journey / Content
- Ads / Measurement
- Reviews / Customer Voice
- Decision Lineage / Evidence
这些对象直接消费结构化权威数据；Machine Archive 仅保留底层审计。

## P1｜平台未指定只在 Delivery 层修复，上游 Compiler 仍假设 target
v0.6.45 修复了最终交付的 silent default，但 `build_project()` 仍要求 `request['target']` 和 market/platform/site 等字段。后续需要继续把“推荐平台”和“已选择平台”从上游拆开，避免 Host 为满足 schema 被迫填历史默认值。

## 新的不可回退连续性合同
1. **Source truth continuity**：事实/市场/价格/人群数据必须保留来源。
2. **Decision continuity**：分析结果只有转化成明确决策/边界/假设才进入下游。
3. **Curation continuity**：资产存在理由必须引用相关决策，而不是只引用通用风格。
4. **Production continuity**：选中的 generation-relevant 参数必须进入 Prompt/Provider。
5. **Human-delivery continuity**：关键商业对象必须在人类 HTML 一等可见，不能只存在 JSON。
6. **Revision continuity**：Ads/Review/Experiment 的新证据应回流到最小责任层，并保留未受影响对象。
7. **Package continuity**：升级只能加法；正式安装包必须证明完整 Canonical + Runtime + human delivery consumer 同时存在。
