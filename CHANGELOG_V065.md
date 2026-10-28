# CHANGELOG — v0.6.5 SaaS Prompt Integrity

## 目标
把 v0.6.4 暴露出的三个问题修到能力本体：
1. HTML 从“长报告/目录式阅读”升级为一个离线 SaaS 工作区；
2. Strategy Authority 的摄影 / CMF / 构图 / 包容性摄影真正进入图片与视频 Render Prompt；
3. 深审计并修掉旧 RACE、Claim Authority、Product Truth provenance、Prompt 内部元数据等跨层断点。

## 主要变更
- `index.html` 改为多页面式 Workspace：Overview / Product Truth / Market & Audience / Listing / Strategy / Visual & Photography / Asset Library / Prompt Lab / Risk & Compliance / Sources / Complete Archive；每个资产有独立内嵌详情页。
- HTML 仍是一个离线文件；完整人类可读内容、资产目录内容、CN/EN Prompt 与结构化附录直接内嵌。MD/JSON/TXT 继续作为编辑/机器真源，但不是阅读前置条件。
- 图片 Prompt 建立 `Strategy → Design Card → Render Contract → Prompt → QA` 参数链；增加 `parameter_trace`。
- 默认摄影策划不再只写“待 prelight”：给出可执行起始方案（焦段/机位/景别/光圈/快门/ISO/CCT/光比/灯位/反光/偏振/CMF/材质），并明确哪些值必须在真实 prelight 后冻结。
- 视频同样继承 Master Photography → Video/Asset Override → Shot Override；生成 `visual_render_contract`、shot render contracts、CN/EN Canonical Video Prompt 与 parameter trace。
- Render Prompt 清除 Asset/Video/Direction/Project ID、RACE、KPI、工程状态、`For <project>...` 等非视觉元数据。
- 精确包装文字/最终营销文字保持 deterministic composition after render，不让图像/视频模型擅自重排或改写。
- RACE 统一为 `Research → Action → Communication → Evaluation`；购物旅程/漏斗的“行动”状态与 RACE 分离，旧 `ACT` 内部标签改为 `NEXT_ACTION`。
- 新增统一 `claim_authority.py`：A/B/C 从证据来源编译，不能仅凭 `APPROVED` 或用户声明的 A/B 升级；C 不得硬宣称，也不能进入 Primary Value 候选。
- Product Truth provenance 改为字段级 source mapping；不再把项目所有来源挂到每条产品事实上。
- 包容性摄影适用性由最终资产任务判定：只要人物/手部/身体关系出现，即进入 P0；深肤色曝光、反光/柔光、发质、体型/年龄/残障、AI bias 控制进入 Render Contract。
- 删除旧 `asset_compiler` Render Prompt 路径，避免回退到 `Create ecommerce visual asset A01` 时代。

## 明确保留的边界
- 当前 ChatGPT 私有插件仍是 Skills-only，没有 `mcp.json`；七大 Python Runtime 在本地/CLI 可真实执行，但在普通 ChatGPT 插件聊天里并不是 MCP tools。要直接调用需另建 MCP Server。
- 精确实时平台类目树、算法、规则、费率、法规等必须来自当前 Web/API/官方来源；离线 Runtime 不凭空保证最新值，缺失时标 `待查证`。
- `strategy_depth.py` / `strategy_authority.py` 仍保留历史 overlay/重复函数结构。当前 active wrapper 已修正，但这是 P1 可维护性风险，后续应做 authority consolidation，而不是本版大规模重写导致回归。
