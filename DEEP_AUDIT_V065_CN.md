# CBCC v0.6.5 全链路深度审计

审计对象：`cross-border-commerce-creative-v0.6.5-saas-prompt-integrity`

审计目标不是“测试数量”，而是确认 **Strategy 写下来的决定是否真的改变 Listing / Image / Video / Delivery / Compliance / Revision 的生产行为**，并找出重复权威、假接入、默认批准、内部元数据泄漏和人类交付缺陷。

---

## 0. 总结

### 已修 P0
1. **RACE 双语义污染**：旧 `Reach / Act / Convert / Engage` 与本项目 `Research / Action / Communication / Evaluation` 曾并存。当前 RACE 执行表和内容矩阵已统一；购物漏斗/行动状态与 RACE 分离。
2. **Claim Authority 前后不一致**：旧链路曾可能信任 `APPROVED / VERIFIED / A / B` 标签；当前 A/B/C 由证据来源编译，无 A/B 支持的 `APPROVED` 仍降为 C，不能硬宣称，也不能进入 Primary Value。
3. **Product Truth 假谱系**：旧 Value Depth 曾把项目所有 source ID 挂到每条事实；当前改为字段级 source mapping，未映射事实明确为 `USER_SUPPLIED_UNMAPPED`。
4. **摄影策划未完整进入 Render Prompt**：旧链路把深层 camera/light/CMF 参数留在 `asset_reasoning`，Prompt 只读顶层合同。当前建立 Master → Asset/Video Override → Shot Override，Parameter Trace 可追踪。
5. **视频同类断链**：旧视频主要有 Hook/Proof/CTA/Shot，但摄影/CMF/人物连续性不足。当前每个 Video / Shot 均有 Visual Render Contract 和 CN/EN Canonical Video Prompt。
6. **Prompt 工程元数据污染**：移除 `asset for KIYUU K01`、Asset/Video/Direction/Project ID、RACE、KPI、内部评分/状态；Render Prompt 只保留会改变生成结果的生产语言。
7. **包容性摄影适用性错误**：旧逻辑主要依赖显式 casting/human input，Human Use / Fit / Relevance 资产可能漏掉 P0。当前由最终资产任务激活；深肤色曝光、柔光/反光、发质、体型/年龄/残障、AI bias 进入 Render Contract。
8. **局部摄影 override 覆盖整个 Master**：视频实测发现只覆盖角度时会丢掉 85mm/ISO/快门等 master 参数。当前改为深合并。
9. **精确文字交给生成模型**：当前包装文字/最终营销 copy 明确走 deterministic composition after render；生成模型只预留安全区。

### 已修 P1
10. **HTML 仍是长报告/文件目录思维**：当前改为单文件离线 SaaS Workspace，多路由页面 + 独立资产详情页 + Prompt Lab；不是纵向“流水席”。
11. **完整资产由多文件组成、用户被迫拼图**：`asset_packages/<asset>/` 中 00–13 文件现在聚合到同一个 HTML 资产页面，源文件继续独立保留。
12. **旧 `asset_compiler` Prompt 路径残留**：已删除旧 `Create ecommerce visual asset A01` 生产路径，避免未来误切回模板逻辑。
13. **旧 `ACT` 内部标签容易与 RACE 混淆**：购买决策链里的内部状态改为 `NEXT_ACTION`；广告中的 reach/convert 若出现，仅作为普通漏斗/指标词，不作为 RACE stage。
14. **版本元数据不一致**：当前 active runtime / state / strategy source / production / seven-agent contract / human delivery 元数据统一到 v0.6.5；兼容性检查仍允许历史包。

---

## 1. Product Truth / Evidence / Claim

| 检查项 | 旧风险 | v0.6.5 状态 | 结论 |
|---|---|---|---|
| A/B/C 权威 | 声明 A/B 或 APPROVED 可能被过度信任 | `claim_authority.py` 先归一化，再进入策略/Listing/Compliance | 已修 P0 |
| C 硬宣称 | 后置报告可降级，但上游可能已吃入 | C 从源头不得进入硬宣称/Primary Value | 已修 P0 |
| 事实来源 | 所有项目来源挂到每条事实 | 字段级 mapping；无 mapping 明确标记 | 已修 P0 |
| 市场来源污染产品真源 | 市场/语境 source 可能被当 Product Truth source | Product Truth 只绑定明确 product/formula/spec/label 等来源 | 已修 |
| 证据等级与事实类型 | 配方/规格曾可能被当 A | 无检测/认证/实测来源时默认 B | 已修 |

反例实测：Claim 写 `status=APPROVED, evidence_level=A`，但没有任何证据来源 → 最终为 **C / SOFT_ONLY_NO_HARD_CLAIM**，且 `primary_value_candidates=[]`。

---

## 2. RACE / Strategy Framework

权威 RACE：**Research → Action → Communication → Evaluation**。

当前 fresh FULL build：
- `07_race_execution_table = [RESEARCH, ACTION, COMMUNICATION, EVALUATION]`
- 平台内容矩阵 `race_stage = COMMUNICATION`
- Render Prompt 不携带 RACE stage。

购物漏斗仍可使用“Discover / Identify / Believe / Next Action / Retain”等用户状态；这不是 RACE。广告中的 reach/click/convert 也只是性能诊断术语，不得重新解释成 RACE。

---

## 3. Photography / CMF → Image Prompt

### 旧断点
Strategy §5 已经计算过焦段、机位、灯光、CMF、材质、曝光/偏振等，但 Prompt Compiler 主要只读取顶层 `photography_contract`；没有显式合同的项目会出现“策划写了、Prompt 没吃全”。

### 当前链路
`Strategy §5 → asset_parameter_reasoning → Design Card → Render Contract → CN/EN Prompt → Provider Job / QA`

没有真实测光数据时也不交空合同，而是给**策略起始推荐值**，并把现场锁定项标为 prelight：
- 例如产品/证据：约 85mm eq 起点；人物/使用/相关性：约 65mm eq 起点；
- f/8 或场景化 f/5.6–8；
- 1/125s、ISO 100 作为受控棚拍起点；
- 5200K 起点 + 灰卡/产品色参考；
- 大柔光 45°、中性填充、必要时 negative fill；
- 1.5:1–2:1 起始光比，证据/材质任务可按细节需求调整；
- prelight、polarization、material response、color consistency 全部进入 Prompt。

这些是**摄影策划建议**，不是伪造“现场实测值”。灯位精确距离/功率、最终 EV、最终 WB 等仍由真实 prelight 冻结。

Fresh build 图片 Prompt 已确认出现：焦段、f-stop、快门、ISO、CCT、光比、Prelight、偏振、CMF、材质、深肤色/反光/柔光、Body/Age/Disability、AI bias；同时不出现 AST/DIR/RACE/KPI/project ID。

---

## 4. Video Prompt

### 旧断点
视频计划有 Hook / Shot / Proof / CTA，但深层摄影语言没有像图片一样完整继承；局部 override 还会把 master camera 整块抹掉。

### 当前
- Master Photography → Video decision override → Shot override 深合并；
- USAGE / RELEVANCE / FIT 默认偏 65mm contextual human/product 起点；
- Proof/Material 偏 85–100mm 证据视角；
- 每 shot 带 camera/light/CMF/material/inclusive continuity；
- Canonical Video Prompt 带 CCT/ISO/shutter/prelight/material/culture/inclusive constraints；
- 不带 AST/VID/DIR、`For KIYUU...`、RACE、KPI。

Fresh build 3 条视频逐条检查通过。

---

## 5. Creative Direction / Dynamic Assets

- 保留 Product Visual Intelligence → Creative Opportunity Universe → Direction Synthesis / Council → Creative Anchors → Dynamic Surface → Asset Architecture。
- 不固定 9 图、12 图、Packshot→Hero→Proof→Human 顺序。
- `Creative Thesis / Image Language / Creative Anchor` 现在不仅存在 Design Card，也转成生成模型可执行的空间节奏、构图语法、场景角色、光线/材质连续性语言。
- Direction ID / variant ID 只留机器合同，不进入 Render Prompt。

仍需关注：当前视觉机会/方向综合能力依赖 Strategy Authority 与输入研究深度；输入没有真实市场/竞品/参考时，不应伪装成“已经验证的市场视觉白区”。

---

## 6. Inclusive Photography / Culture

旧缺陷：是否启用包容性摄影主要看显式 `human.present/casting`，最终 Human Use 资产可能漏掉。

当前：只要资产任务涉及人物、手部、身体比例、穿戴/使用/相关性，即 `APPLICABLE_P0`，包括：
- 深肤色独立测光；
- +0.3/+0.7 EV 仅作为 bracket 起始比较，不作为固定补偿；
- neutral white/soft fill；
- large diffusion；
- negative fill 替代“故意压暗深肤色”；
- 发质/造型保真；
- 体型/年龄/残障自然呈现；
- no whitening / slimming / youthifying / hair homogenization / disability erasure；
- hands / assistive devices / hair edges / body proportions QA。

文化身份仍只影响表达/代表性/语言/场景，不允许从族裔自动推购买行为。

---

## 7. Listing / Upload Ready

已完成：标题、产品名、品牌、平台类目、类目 ID/路径、Highlights/Bullets、描述、属性、搜索词、成分/材质、使用、Warning、FAQ、SKU/Variant、价格/Offer、物流/售后、责任方、合规 HOLD、媒体槽位集中到 HTML Copy Center / `01_LISTING_UPLOAD_READY.md`。

### 保留边界
精确平台类目树、提交字段、费率、算法、法规等若没有当前官方/Web/API证据，必须 `待查证`。离线 Runtime 不能凭静态 pack 保证“今天最新”。这是数据边界，不应通过猜测“修复”。

---

## 8. Human Delivery HTML

### v0.6.4 问题
虽然完整，但仍是“长报告/章节目录”思路；内容密度大、滚动疲劳、像流水席。

### v0.6.5
一个离线 HTML，内部是产品型 Workspace：
- Overview
- Product Truth
- Market & Audience
- Listing
- Strategy
- Visual & Photography
- Asset Library
- Prompt Lab
- Risk & Compliance
- Sources
- Complete Archive
- `asset/<asset_id>` 独立资产详情页

Asset 详情把 00–13 包聚合到一页；Prompt Lab 可直接复制；人类内容与结构化附录直接内嵌。图片/视频/音频媒体可直接嵌入，MD/JSON/TXT 不再是阅读前置条件。

Fresh demo HTML 约 5.7MB、4 个资产 route，未出现“打开源文件”式导航。

### 验证边界
当前执行环境禁止通过本地浏览器导航到生成的 `file://` 页面，因此本轮没有声称“浏览器截图视觉验收通过”；已做 DOM/route/content/响应式代码层检查。真实视觉接受仍应由实际打开 HTML 的用户判断。

---

## 9. 七大工具

本地 Runtime 的 7 个一级合同仍在：
1. Market Research
2. Product Strategy
3. Listing Creative
4. Product Image
5. Product Video
6. Advertising Optimization
7. Review Analysis

薄 `toolkits/11_seven_agent_contracts/*.py` 是 dispatcher wrapper；真正深逻辑集中在 `runtime/cbcc/tools/seven_agent.py` 及 Market/Economics/Listing/PVI/Creative/Video/Ads/Feedback 模块。**文件小不等于能力薄，但必须看它调用的 Runtime。**

### 仍未完成的架构项：ChatGPT MCP 化
当前私人插件没有 `mcp.json`。因此：
- Local Runtime/CLI：七大 Python 合同是真执行；
- ChatGPT Skills-only plugin：按 Skill 和宿主工具遵循同一合同，但不是直接调用七大 Python 函数。

如果目标是让 ChatGPT 中直接出现 `CBCC.market_research(...)` / `CBCC.product_image(...)` 等工具调用，需要另建并部署 MCP Server。这项 **本版明确未完成**，不得继续说“插件已经直接调用七大工具”。

---

## 10. Ads / Review / Learning

- Ads 诊断顺序保持：资格/有效流量 → 点击包 → PDP/流量质量 → Economics → Incrementality；`reach/convert` 在此只作为普通广告/漏斗术语，不是 RACE。
- Review 保留八类归因、misunderstanding、defect-vs-communication、fixability、positive selling-point ranking、exact reconciliation 与局部回流。
- Revision / Learning 仍按 smallest responsible layer 路由，不因单一问题重做整套策略。

未发现本版修改导致这些能力被删除。

---

## 11. 结构性剩余风险

### P1 — Strategy overlay / duplicate authority
AST 扫描确认：
- `strategy_depth.py` 有 9 个顶层函数名重复定义；
- `strategy_authority.py` 有 2 个顶层函数名重复定义。

这是历史“保留旧实现 + 后置 wrapper 深化”的 overlay 结构。当前 active path 是后定义 wrapper，fresh FULL build 行为正确；但它有两个风险：
1. 旧语义可能隐藏在 earlier implementation，未来重构/导入方式变化时重新冒出；
2. 维护者难以判断哪个函数是权威。

本版只修了高风险语义，不进行 200KB+ 文件的大爆炸重构，以免在用户还在真实验证前制造更大回归。后续应做 **Authority Consolidation**：把 legacy implementations 移到明确 `legacy/compat`，主文件只保留一个 canonical implementation。

### P1 — Live platform intelligence
Platform packs 是计划/提交辅助，不是实时平台数据库。当前类目树、算法、费率、禁限售和法规仍需要 live source adapter/Web/API。

### P1 — MCP execution surface
见七大工具章节。若用户需要插件直接执行本地/远程 Python 工具，这是下一个独立架构任务。

---

## 12. 本轮 targeted regression

只做与修复直接相关的回归，不把测试数量当成熟度：
- `tests/test_v065_saas_prompt_integrity.py`
- `tests/test_v060_capability_complete_rebase.py`
- 结果：**6 passed**。
- Fresh FULL build：Strategy / Listing / Assets / Video / Prompt / Provider contract / Human Delivery / HTML 全链生成成功。

检查结果：
- RACE = Research / Action / Communication / Evaluation；
- Image Render Prompt：摄影/CMF/包容性参数存在，内部 IDs/RACE/KPI 不存在；
- Video Render Prompt：USAGE/RELEVANCE 使用 65mm 起始方案，证据任务保持 85mm 级别；内部 IDs/项目 lead-in/RACE/KPI 不存在；
- unsupported `APPROVED + A` 无证据 Claim → C，不能进入 Primary Value；
- HTML 为多 route SaaS Workspace，资产详情和 Prompt Lab 均在同一文件。

---

## 13. 结论

v0.6.5 解决了本轮用户点名问题背后的**生产链断点**，而不只是修文字：
- 页面从“报告”变成“工作区”；
- 摄影/CMF/人物/Surface 参数从“策划资料”变成“Render Contract”；
- Prompt 从“项目日志 + 视觉说明”变成“纯生产指令”；
- Claim、Product Truth、RACE、Inclusive Photography 统一成前置权威；
- 明确区分已经实现的 Local Runtime 与尚未 MCP 化的 ChatGPT Plugin。

仍然保留的主要结构风险只有：**legacy overlay consolidation、live platform/current-data integration、MCP execution surface**。这些不能靠继续往 Skill 里写规则解决。
