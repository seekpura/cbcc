# CBCC v0.6.29 CURRENT HANDOFF

## 唯一当前基线
GitHub 私有仓库：`seekpura/cbcc`，`main` 是唯一源码真源。当前版本：`0.6.29-final-stabilization`。

2026-10-28 已完成一次性仓库恢复；`.bootstrap` / chunk / 源码解包 workflow 已退出。私有 ChatGPT 插件是 GitHub 源码的派生发行包，不是反向源码权威。

## 固定 GitHub 开发方式
日常修改使用 Git Database 增量链：读取 `main HEAD + tree` → changed / added / deleted 构新 tree → 一个 commit → `update_ref(expected_sha=旧 HEAD)`。大文件小改动优先使用小型 Git patch 传输，不复制完整大文件。

## 当前主线
Commerce Goal → Product Truth / Hard Boundaries → Agent Evidence-Gap Discovery → Agent Strategy & Surface Decisions → Dynamic Content / Asset Architecture → Dynamic Creative / Photography / CMF → CN/EN Canonical Prompt / Production Contract → Production / Review / Learning → Agent Replan or Stop → Chinese-first Semantic Workspace.

## v0.6.7 / v0.6.8 已完成
1. Strategy / Content / Visual / Listing / Prompt / Evidence 使用不同语义 IA；Content 成为一级路由。
2. 单资产详情进入动态 `asset-production-workspace`：决策 / Design Card、画面、摄影 / CMF、文案、Prompt、QA / 来源按真实内容出现。
3. 中文优先交付；目标市场可见语言与中文人类说明同时保留。

## v0.6.9 已完成
1. 真实 KIYUU 审计发现并修复 Photography Contract 执行断链。
2. `capture_mode`、完整 `composition`、显式 `color_management` 进入 `photography_execution`，贯穿 Design Card → CN/EN Canonical Prompt → Parameter Trace → Machine Visual Contract → Human Asset Workspace。
3. `composition` 按开放字典保留；`negative_space`、`subject_clearance` 等未来字段不会因白名单缺失而被吞掉。
4. KIYUU 三个真实资产均验证 `COMPOSITE`、68% product occupancy、`sRGB`、`locked real-product layer` 的全链连续性。
5. v0.6.7 + v0.6.8 + v0.6.9 定向联测：12 passed。
6. 全量回归：100 passed / 13 个既有 baseline failures；本轮无新增失败。

## v0.6.10 已完成
1. 修复 Approved Visual / Precision / Editability 只停留在 Design Card 的断链；CN/EN Prompt、Parameter Trace 与人类 Visual 工作台现在都消费正确执行子集。
2. 修复人类 Copy 工作台仍读取旧字段的问题；当前直接读取 `information_design.locked_visible_copy`。
3. 修复英文 Render Prompt 通过 Surface / Copy Budget JSON 泄漏精确营销文案的问题；精确文案只留在 deterministic overlay 与人类 Copy 工作台。
4. 真实 KIYUU 三资产验证：允许视觉元素、LOCKED_PIXEL、product_master_pixels 等冻结层进入执行 Prompt；锁定营销文案不进入图像模型 Prompt。
5. v0.6.7 + v0.6.8 + v0.6.9 + v0.6.10 定向联测：14 passed。
6. 全量回归：103 passed / 12 个剩余失败；v0.6.9 已通过项无回退，并有 1 个既有 Provider Quality Preflight 失败因执行追踪增强转为通过。

## 明确边界
1. MCP / Plugin / HTTP / Provider Host 已作为可选宿主与生产接入能力存在；它们不是电商研究、策略、内容或设计权威，后续主线不得为了 transport 完整度挤占 Commerce Agent 能力。
2. 当前平台精确类目 / 规则 / 费率必须来自实时官方数据或用户资料；离线 Runtime 不猜。
3. Product / Market / Risk 仍保留通用 `module-shell`，只有真实使用需求证明需要时再拆，不为页面差异机械制造模板。
4. baseline failing node-id 必须逐项审计：真实能力断链要修，旧字符串/旧版本/已被更强合同取代的断言要升级测试；不得用固定失败数量替代能力判断，也不得为了“全绿”倒退当前能力。
5. Render Prompt 继续禁止 Asset / Project / Direction ID、RACE、KPI 等内部元数据；精确可见文案继续 deterministic composition。

## v0.6.11 已完成
1. `source_product_assets` 不再只留在 QA 合同：Renderer Recipe 与 Provider Job 都有机器可读 `source_product_bindings`。
2. LOCAL_FILE_PATH 在 handoff 时重新检查存在性和 SHA256；编译后母版移动/被替换会 HOLD，不会继续发单。
3. LOCKED_PIXEL 结果必须回报母版 ID + SHA256 lineage，并回显 `source_binding_hash`；错误 hash / 错 binding 进入 Review。
4. Local Revision 结果增加 `changed_layers`；报告修改 frozen 商品身份层会触发 `FROZEN_LAYER_MUTATION_REPORTED`。
5. GRAPHIC_DESIGN 等 LOCKED_PIXEL Provider 也必须声明 source binding 输入，不再仅摄影/合成模式携带。
6. 真实 KIYUU 三资产 production run：3/3 Provider Job 绑定同一经过 handoff 校验的商品母版。
7. v0.6.7–v0.6.11 定向联测：18 passed；全量：107 passed / 12 个既有历史失败。

## v0.6.12 已完成
1. `materialize_provider_jobs()` 不再把主机 `package_dir` / LOCAL_FILE_PATH 当作外部执行路径；冻结资产包与本地商品母版进入 job 内部 `inputs/`。
2. 本地商品母版在物化时再次校验 SHA256 后复制，并重绑为 `PACKAGE_RELATIVE_PATH`；外部 Provider handle 继续保持显式 handle。
3. 新增 `PORTABLE_JOB_MANIFEST.json`，绑定冻结 package 文件 hash、upstream source binding、portable source binding 与 portable manifest hash。
4. 外部 `result.json` 必须返回 `production_receipt`；系统校验 job/package/source/output lineage，并对 job 内本地输出重新计算 SHA256。
5. LOCKED_PIXEL receipt 必须有 source-bound `layer_manifest`；REAL_PHOTO / VIDEO receipt 必须有真实 `capture_metadata`。

## v0.6.13 已完成
1. `PROVIDER_ASSET_HANDLE` 增加结构化 lifecycle：provider/state/expiry/supersedes/generation/content SHA256；失效、过期或内容 hash 不一致在 handoff HOLD。
2. 旧字符串 handle 保持兼容，但明确为 `DECLARED_ONLY`，不再伪称已远程验证。
3. `EXTERNAL_ADAPTER` 增加统一 Adapter Profile → vendor request 映射、request hash、idempotency key、transmission ID 和 external job acknowledgement。
4. 真实 provider-job ingestion 遇到远程 URI 必须由 adapter/resolver 提供实际字节并重新计算 SHA256；无 resolver / 下载失败 / hash 不匹配进入 Review。
5. 新增远程输出 recovery，只有 hash 匹配的实际字节才能落入恢复副本。

## v0.6.14 已完成
1. 新增可插拔 `ProviderExecutor` protocol；credentials / network client / vendor SDK 由 adapter 外置，CBCC 只拥有执行状态与完整性合同。
2. materialized Provider Job 进入真实生命周期：prepare / upload-or-refresh → idempotent submit → poll/resume → collect → resolve/download → `result.json + production_receipt`。
3. `executor_state.json` 持久化外部 job ID、resume token、poll count 与 transmission，宿主恢复后不重复 submit。
4. 本地商品母版上传前再次 SHA256；过期 Provider Handle refresh 必须 rotate handle，并保留 supersedes + generation + content SHA256 lineage。
5. portable `source_binding_hash` 保持不可变；Provider 侧 locator/handle 重绑定使用 `provider_execution_source_binding_hash`。
6. executor transmission 成为 v0.6.13 portable transmission 的 child；ingest 同时校验 parent binding、execution request hash、external acknowledgement。
7. `ReferenceMemoryExecutor` 已跑通 upload / refresh / submit / resume / output bytes / receipt / existing ingest 闭环。
8. v0.6.13 + v0.6.14 定向联测：9 passed。
9. 全量回归与 v0.6.13 main 基线逐 node-id 对比：`NEW_FAILURE_COUNT=0`；不以固定失败数量阈值替代回归判断。

## v0.6.15 已完成
1. 新增 credential-free Adapter Registry：按 provider / mode / capability / operation discovery；确定性选择，不在 registry 保存认证信息。
2. 新增 Executor Bridge：在 v0.6.14 executor 之上统一 retry / exponential backoff / provider retry-after / cancel / reconcile。
3. `bridge_state.json` 与 `executor_state.json` 分工明确：前者保存宿主编排策略与尝试历史，后者继续保存 Provider job lifecycle；两者都不持久化 runtime credentials。
4. 标准错误分类：只有显式 transient / rate-limit 才重试；未知错误按 permanent 处理。
5. `HostCallbackExecutor` + `EPV_HOST_CALLBACK_V1` 已打通真实宿主注入面，SDK / HTTP client / auth callback 由宿主提供。
6. Reference Memory adapter 仅 opt-in 测试使用，不进入 production default discovery。
7. cancel / reconcile 与既有 external job ID / executor state 共用同一 lineage；没有第二套完成路径。
8. `provider_contract()` 已显式暴露 executor + bridge contract。
9. v0.6.13–v0.6.15 provider continuity 定向联测：16 passed。
10. 全量回归与 v0.6.14 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`；历史失败继续作为独立兼容性债务。

## v0.6.16 已完成
1. 新增 `ProviderExecutionSurface`：宿主通过稳定程序化入口操作 adapter discovery / execute / cancel / reconcile，而不是直接碰内部 executor。
2. CLI 新增 `adapter-list / provider-execute / provider-cancel / provider-reconcile`；没有 API key / token / secret 参数。
3. 新增 `CBCC_PROVIDER_HOST_MODULE`，其值仅为 host module 名称；宿主 module 可 `register_adapters(registry)` 并用 `create_runtime_context(...)` 返回瞬时 callbacks / SDK client / auth objects。
4. runtime context 不写入 adapter declaration、bridge state、executor state、result、production run 或 ProjectState。
5. `provider-execute` 继续复用 Registry → Bridge → Executor → Receipt → existing ingest；全部 materialized jobs 结果齐全后才自动 ingest。
6. 自动 ingest 成功继续更新 ProjectState `PRODUCTION=READY_REVIEW` 并物化 Review Workspace，没有第二套 completion authority。
7. 局部/分批执行结果不齐时 ingest 明确 DEFER，不会误把全项目 COMPLETE。
8. CLI cancel / reconcile 使用现有 external job ID / executor state / bridge state lineage。
9. v0.6.13–v0.6.16 provider continuity + host-surface 定向联测：23 passed。
10. 全量回归与 v0.6.15 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`；发布判断继续以新增失败集合为准。

## v0.6.17 已完成
1. 仓库审计确认当前没有 MCP server / Plugin action runtime，因此没有伪造“已接 MCP”；先建立 host-neutral canonical Action Contract + Dispatcher。
2. 六个 canonical actions：adapter list、execute、status、resume、cancel、reconcile；每个 action 有明确 input schema / output status / permission scope。
3. authorization 默认 DENY；`PROVIDER_ADAPTER_READ / PROVIDER_STATUS_READ / PROVIDER_EXECUTE / PROVIDER_CANCEL / PROVIDER_RECONCILE` 权限独立。
4. Action Dispatcher 只调用现有 `ProviderExecutionSurface`，不直接 instantiate executor，不复制 Provider runtime。
5. execute → PENDING → status(read-only) → resume 已跑通；resume 复用同一 external job，Reference Executor submit count 保持 1。
6. operation ID 绑定 project + materialized job scope；scope 被改动时 status/resume 拒绝继续。
7. 不建立第二套 async job DB；状态继续来自 `bridge_state.json / executor_state.json / result.json / production_run.json`。
8. action payload 禁止 credential-like 字段，包含 namespaced key；runtime context 继续只由 v0.6.16 Host Surface resolver 注入。
9. 提供 MCP tool name / Plugin operationId 的 declarative thin mapping，但 manifest 明确 `claims_mcp_server_exists=false / claims_plugin_server_exists=false`。
10. v0.6.13–v0.6.17 provider continuity + host-action 定向联测：33 passed。
11. 全量回归与 v0.6.16 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`；Action transport 发布不以固定失败数量阈值放行。

## v0.6.18 已完成
1. MCP tools 与 Plugin/OpenAPI descriptors 全部由 v0.6.17 canonical Action Catalog 生成，不再手写两套 schema。
2. 6 个 canonical actions 在 MCP / Plugin 两种 transport 下保持 exact input-schema parity。
3. descriptor parity 同时校验 tool/operation naming、permission scope、authorization source 与 credential-like field lint。
4. checked-in `descriptor_manifest.json` 保存 canonical/MCP/Plugin schema hashes；当前 6 个 action 三方 hash 全部一致，issues=[]。
5. checked-in `mcp_tools.json / plugin_openapi.json / descriptor_manifest.json` 与 runtime generator 输出完全一致。
6. OpenAPI 使用同源相对 `/`；没有把 credential schema、API key 字段或假 provider runtime 放进 descriptor。
7. `PluginActionTransportAdapter` 只做 operationId → canonical action → Dispatcher 转发，不持有 surface / bridge / executor。
8. descriptor manifest 明确没有 MCP server / Plugin HTTP server；网络 host 仍是下一层薄适配器责任。
9. v0.6.13–v0.6.18 provider continuity + transport parity 定向联测：40 passed。
10. 全量回归与 v0.6.17 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`；descriptor 发布必须保持 canonical schema parity。

## v0.6.19 已完成
1. 新增真正可启动的 Plugin/OpenAPI WSGI host；action path 全部从 v0.6.18 generated OpenAPI descriptor 派生。
2. HTTP host 唯一调用链为 request → operationId → `PluginActionTransportAdapter` → `ProviderActionDispatcher`；transport module 不直接 import/call ProviderExecutionSurface、Bridge 或 Executor。
3. `/health`、`/openapi.json`、`/actions.json` 可直接读取运行状态与 canonical schema；descriptor bundle 自身仍保持 descriptor-only 语义。
4. action POST 强制 JSON media type、Content-Length、JSON object 与 request-size 上限；400/403/404/405/409/411/413/415/422/500 由 transport 统一映射。
5. `CBCC_ACTION_AUTH_MODULE` 只指定宿主 auth module；ActionAuthorization 由 host hook 瞬时注入，不进入 action payload / project state / provider runtime state。
6. 默认 DENY；auth resolver 自身异常按 403 fail-closed，且宿主异常文本不返回客户端。
7. PENDING → HTTP 202 + Retry-After + operation headers；status/resume 继续使用 v0.6.17 稳定 operation ID 与现有 provider persisted state，没有第二套 async DB。
8. 新增 `cbcc.plugin_http_cli` composition root；默认 reference server 仅使用 Python 标准库，WSGI application 可被其他宿主 server 挂载。
9. v0.6.13–v0.6.19 provider continuity + transport HTTP 定向联测：48 passed。
10. 全量回归与 v0.6.18 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`；HTTP transport 发布保持 canonical descriptor/dispatcher authority。

## v0.6.20 已完成
1. 开发前重核 MCP 当前官方 GA：现代协议 `2026-07-28` 已从 initialize/session 模式转为每请求 metadata；`server/discover` 是服务器必须实现的 discovery RPC，legacy `2025-11-25` 才使用 initialize/initialized。
2. 新增 dual-era stdio host：现代 `server/discover / tools/list / tools/call` + legacy `initialize / notifications/initialized / tools/list / tools/call`。
3. stdio wire 为 UTF-8 newline-delimited JSON-RPC；stdout 仅输出 MCP message，notification 不制造无效 response。
4. MCP tools 直接来自 v0.6.18 generated `mcp_tool_descriptors()`，modern tools/list 与 checked-in canonical descriptor exact parity 且 deterministic。
5. modern request 强制 `_meta.io.modelcontextprotocol/protocolVersion=2026-07-28` 与 clientCapabilities；unsupported version 返回 `-32022` + supported versions。
6. modern `server/discover` / `tools/list` 带 `resultType=complete`、serverInfo 与保守 cache hints `ttlMs=0 / cacheScope=private`。
7. tools/list 按 canonical permission scope 过滤；默认 DENY 的调用者看不到未授权工具。
8. tools/call 只进入 `ProviderActionDispatcher`；structuredContent 保留 canonical envelope，PENDING operation/status/resume 继续使用既有 provider state，无第二套 MCP async DB。
9. `CBCC_MCP_AUTH_MODULE` 只指定宿主授权 module；resolver 异常 fail closed 且不回显异常文本；canonical secret-field 拒绝继续生效。
10. MCP transport module 不直接 import/call ProviderExecutionSurface / Bridge / Executor；`mcp_stdio_cli` 仅作为 composition root。
11. v0.6.13–v0.6.20 provider/action/Plugin/MCP continuity 定向联测：62 passed。
12. 全量回归与 v0.6.19 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`。


## v0.6.21 已完成 — Commerce Agent Autonomy
1. 新增 `agent_autonomy.py`，明确 Hard Constraints 与 Agent Decisions：事实/合规/平台硬边界/真实商品身份被冻结，研究、策略、内容、资产、创意、摄影/CMF、生产路线、迭代深度由 Agent 决定。
2. 编译物化 `agent_autonomy_plan.json`；宿主可直接提供 `agent_plan / agent_decisions`，其决定优先于 Runtime fallback heuristic。
3. Research 从“调用方先写固定研究清单”升级为 Agent 自主 gap discovery；fallback 也只产生能改变当前商业决策的缺口。研究没有固定来源数/竞品数/query 数，停止条件是信息增益不再改变重要决策。
4. Content Graph 不再默认展开全部 `DEFAULT_FAMILIES`；只从目标 Surface、明确任务和真实项目能力信号派生，Agent 显式 scope 不被 Runtime 扩写。
5. Creative Opportunity 支持任意 Agent-authored mechanisms/domain/count；原 12 机制仅是无 Agent 决策时的兼容 fallback，fallback 也取消固定 12 上限。
6. Creative Direction 取消 6–12 mechanism、3–5 direction、固定差异数等配额；方向数量按当前相关度/不确定性动态决定。
7. 删除固定 decision-intent → layout/view/context 模板和 5 种 spatial rhythm 轮换；资产表达优先消费自身 `visual_production_signature` / `agent_visual_expression`。
8. AIDA / FABE / 4P / STP / JTBD / Funnel / RACE 改为可选工具；不再每个项目自动注入框架，也不再把所有资产强制标为 RACE=COMMUNICATION。
9. 平台内容矩阵移除固定“钩子→价值/证据→异议→CTA”叙事权威；脚本/叙事由当前消费者问题、证据关系、Surface 和交互任务决定。
10. 新增 `agent_next_action.json`：动态暴露 Research / Asset Replan / Creative / Compliance / Production 等 frontier；Agent 有最终路由权并可在当前目标满足时停止，不存在固定步骤序列。
11. Photography Contract 改为 relevance-driven precision：COMPOSITE/CG/AI 不为过校验虚构真实摄影参数；语义 perspective 可代替死焦段；numeric occupancy 只在锁定时要求；LOCKED_PIXEL/精确商品色仍保留严格 color fidelity。
12. 定向自主权测试：20 passed。发布仍需与最新 main 做全量失败 node-id 差分，`NEW_FAILURE_COUNT=0` 才能进入 main。
13. v0.6.17–v0.6.20 的 Provider/Plugin/MCP 基础设施继续保留，但从 v0.6.21 起明确降为可选 integration layer，不再作为 Commerce 产品主路线。

## v0.6.22 已完成 — Dynamic Workspace + Relevance-driven Prompt Projection
1. 新增 `workspace_autonomy.py`：一级 Workspace 路由按当前项目真实业务对象动态出现，不再固定展示 12 个模块；首页动作同时消费 `agent_next_action.json`，不固定成上架 / 做图 / 内容 / Prompt 四按钮。
2. 单资产工作台改为独立相关视图，而不是固定生产流水线。Design Card/购买判断聚合为“决策”，Visual / Photography-CMF / Copy / Production / Prompt 仅在相关时出现；Agent 显式 view order 优先，默认 UI 顺序仅用于阅读，不拥有规划/执行权威。
3. `trace + source files + unknown legacy views` 聚合到 `QA / 来源`，因此取消固定阶段后仍保持参数、源文件和历史资产内容完整可追溯。
4. Canonical Prompt 改为 relevance-driven projection：非真实摄影资产不再为了字段完整强塞焦段、快门、ISO、主辅光、CCT、偏振、Prelight 或人物摄影段落；空/不相关 section 不进入 renderer prompt。
5. 已经被 Agent/策略选定且确实绑定到当前资产的摄影参数不会被“相关性裁剪”误删。存在 asset-specific photography reasoning 时，策略层已决定的镜头 / CCT / 光圈等可继续贯穿 Design Card → Prompt → Trace → Production。
6. Parameter Trace、QA photography checks 与 Renderer layer plan 同步改为任务相关；不存在“上游取消必填、下游 QA 又逼着补字段”的反向静态化。
7. Human Workspace 继续中文优先；目标市场可见文案保留目标语言并提供中文释义。Content 工作区移除固定 Hook / CTA / 传播阶段的默认权威表述。
8. 新增 v0.6.22 动态 Workspace / Prompt relevance 回归，并升级 v0.6.8 资产工作区兼容测试的旧“动态阶段”措辞；能力保护项（决策聚合、QA/来源、legacy recoverability）继续保留。
9. 发布验证：targeted + compatibility `20 passed`；branch 与冻结 main 全量各 `12` 个既有失败，失败 node-id 差分 `NEW_FAILURE_COUNT=0`。发布判断仍以新增失败集合为准，不为追求全绿倒退能力。
10. MCP / Plugin / HTTP / Provider Host 继续保留为可选 integration layer；v0.6.22 没有把 transport 重新提升为 Commerce 主线。

## v0.6.23 已完成 — Task-Scoped Human Delivery + Listing Authority
1. `human_delivery.py` 不再无条件构造固定 25 个上架字段并用其支配全项目 readiness；当前 request、Agent content scope、Content Graph 与 `agent_next_action` 共同决定 Listing 是否属于当前工作范围。
2. 非 Listing 当前任务明确为 `NOT_IN_CURRENT_SCOPE`：`copy_center` 不制造价格 / 物流 / 售后 / 卖家信息缺口；已有商品与 Listing 数据继续保存在 `preserved_listing_fields` / 结构化真源。
3. Listing 当前任务只投影 supplied + platform-required + 真正 submission-sensitive 字段；可选缺口与阻断缺口分离，只有当前 required 字段可以进入 `READY_WITH_HOLDS`。
4. 精确平台类目只有在真实上架 / 发布任务需要时才成为 submission-sensitive；规划 category 继续可以服务策略，但不伪装成 Seller Center 最终类目。
5. 上架字段按实际内容动态形成语义组，而不是固定 canonical 字段表；中文项目交付与目标市场文案 / 中文释义继续并存。
6. `listing_conversion_architecture()` 的 click / post-purchase fields 改为当前字段投影；不存在固定 field quota，也不再为了“完整”制造 price / variant / FAQ / usage / package 等槽位。
7. 项目总控台改为当前 Commerce scope + Agent frontier + Assets + real risk，而不是固定“先看四件事 / 正常使用四步”。
8. `compiler.py` runtime version 更新为 `0.6.23-task-scoped-delivery`；v0.6.21–v0.6.22 Agent/Workspace/Prompt 自主权继续保留。
9. v0.6.23 targeted + compatibility：`23 passed`。
10. 全量回归相对 frozen v0.6.22 main：main 12 failures / branch 12 failures / `NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。

## v0.6.24 已完成 — Task-Scoped Strategy + Asset Authority
1. `strategy_authority.json` 继续保留九段 canonical machine schema；人类 `MASTER_STRATEGY_CN.md` 改为 task-scoped projection，只显示当前商业目标真正需要的决策域。
2. 历史全框架注入退出权威：STP/JTBD/4P/Funnel/AIDA/FABE/Fogg/Means-End/Signaling/FIRST/Cognitive Budget/Belief Sequence/Commerce Response Ladder/RACE 只在 Agent/用户选择时进入当前策略。
3. RACE 未启用时 section 07 保持兼容键但为空，Content Matrix 不再机械写 `COMMUNICATION`；显式 RACE 仍完整保留。
4. `build_risk_priority_depth()` 不再强制填满 P0/P1/P2，也不默认制造 A/B；真实 Compliance HOLD、Research gap、Evaluation/Experiment 才生成动作。无实质缺口时 `CURRENT_SCOPE_CAN_STOP`。
5. Asset Architecture 在无实际资产 Surface 时不再把 shopper question 变成 GALLERY/VISUAL；保留为 `unrouted_questions`，等待真实 Surface/任务激活。
6. 取消资产 A→B→C 自动 handoff；关系模式为 `EXPLICIT_ONLY`，显式 handoff 原样保留。
7. 机器九段、Product Truth、Claim/Evidence、Foundation、Photography/CMF、00–13 资产包、Provider/Review/Revision/Hash lineage 均保留。
8. v0.5 Strategy 兼容测试同步升级：继续严查机器九段和 legacy asset package preservation，但不再要求未显式启用的 RACE 出现在人类 Markdown。
9. targeted + continuity：`28 passed`。
10. 全量回归：frozen v0.6.23 main `12 failures` / v0.6.24 branch `12 failures` / `NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。
11. 本轮额外审计 12 个 baseline node-id，确认其中多项是旧英文标题、旧版本前缀、旧状态字符串或被更强 Claim/Compliance 合同取代的断言；以后继续逐项分类，不能把“12”本身当发布标准。

## v0.6.25 已完成 — Decision Question + Framework Authority
1. 新增 `decision_authority.py`，把 Shopper Question、Decision Trace、Framework Selection、Content-family activation 的当前任务权威从 Compiler 静态默认中拆出。
2. 删除 Compiler 无输入时自动制造的四个 shopper questions；问题可以为空，空本身不是错误。
3. 问题来源只接受用户/调用方、Agent authored scope/trace、显式 Asset/Video job、以及当前 Listing/CX 的真实异议；物化 `decision_question_authority.json` 记录来源与 lineage。
4. 删除问题数组位置 → RACE/Funnel stage 的静态映射；没有显式 RACE 与 stage 时 `race_stage=None`。
5. 删除 Compiler 默认 decision framework 列表；只有用户/Agent 明确选择的框架进入 Decision Trace / persuasion compiler。
6. Target Surface 单独存在不再制造 Content family；平台/Surface 是约束，不是“系统能做什么就都做什么”的配额。
7. 保留真实生产兼容：已有 shopper question + `compile_assets/production_run` 时，Surface 可以把这些已有问题路由到 VISUAL / VIDEO / CREATOR / CX 等资产 family；不会凭空添加 Listing/Search/Offer 工作。
8. 请求资产/生产但没有问题/Asset job 时，`agent_next_action.json` 暴露 `AUTHOR_DECISION_OR_ASSET_SCOPE`；Agent 先定义真正决策任务，Runtime 不用默认问题填空。
9. v0.6.21 的静态源码字符串测试同步升级为当前更强合同；真实 v0.5.10 / v0.5.8 多品类生产兼容保持通过。
10. targeted + continuity：`46 passed`。
11. 全量回归：frozen v0.6.24 main `12 failures` / v0.6.25 branch `12 failures` / `NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。

## v0.6.26 已完成 — Task-Scoped Content + Gate Readiness
1. 新增 `scope_readiness.py` 与 `content_requiredness.json`：Content family active/preserved 与 current deliverable requiredness 分离。
2. ContentObject 的 `required` 不再全量 `True`；显式 deliverable / current production scope 才升级为 required。
3. 新增 `gate_scope.json`；18 个 canonical Gate 继续保留机器审计与 dependency lineage，但每个 Gate 有独立 `required_for_current_scope / blocking_for_current_scope / scope_status / scope_reason`。
4. ProjectState Gate record 持久化 scope 元数据；动态化不删除 gate。
5. Review Manifest 取消“除 ASSET_COMPILE/PRODUCTION 外所有 gate required”的硬编码；只有当前 scope 的 blocking gate 才形成 `required_missing`。
6. Supporting ContentObject 保留但不自动进入 `review_pending`；Human workspace 可以看到数据，而不会把支持资料变成待办。
7. Planning-only Platform Compile required/context 与 blocking 拆分，当前规则待研究不阻断可以继续完成的策略范围。
8. Review HTML / checklist 明示 Runtime Status / Current Scope / Blocking，减少流水线错觉。
9. targeted + continuity：`34 passed`。
10. 全量回归：frozen v0.6.25 main `12 failures` / v0.6.26 branch `12 failures` / `NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。

## v0.6.27 已完成 — Current-Scope Completion Authority
1. 新增 `completion.py`，用 current scope blockers / required review / blocking actions / open revisions / hard Agent frontier 派生 READY。
2. `final_ready` 从静态 flag 变为可重复计算结果；Target-only / Strategy-only scope 在没有真实阻断时可以完成。
3. Asset/Content/Production 当前 required item 仍必须完成 item review；未审阅不会误报 READY。
4. Supporting / advisory Gate、ContentObject、Research、Agent frontier 可以保留，不自动制造“永远做不完”的状态。
5. Review Manifest、ProjectState、Review Workspace、CLI Export 统一消费同一 completion authority。
6. `build / review-apply / provider-ingest / revision-compile / revision-ingest / learning-apply / revise / export` 均刷新并持久化 completion。
7. Revision 继续通过 dependency graph 精确 INVALIDATE；若影响当前 required/blocking scope，READY 会重新打开。
8. targeted + continuity：`40 passed`。
9. 全量回归：frozen v0.6.26 main `12 failures` / v0.6.27 branch `12 failures` / `NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。

## v0.6.28 已完成 — Blocking vs Advisory Agent Frontier
1. `compile_agent_next_action()` 消费 v0.6.26 `gate_scope` / `content_requiredness`，Frontier 拆成 blocking 与 advisory 两层。
2. Advisory Research 保留可见与可执行，但不再把 Agent 状态强制保持 `ACTION_FRONTIER_OPEN`；无 hard blocker 时真正返回 `STOP_CURRENT_SCOPE_SATISFIED`。
3. Research action identity 保持 `RESEARCH_OR_EVIDENCE_RESOLUTION`；兼容由 `blocking=false` 与 frontier 分类表达，不破坏旧宿主 action routing。
4. Compliance / Asset coverage / Creative direction / Production blocker 都按当前 required/blocking scope 路由；支持性对象或未来优化不制造硬循环。
5. 显式 Agent Stop 不能覆盖 current-scope hard blocker；若仅剩 advisory frontier，则 Stop 可成立。
6. 修复 `production_run:{}` 的真实生产意图断链：presence-based `request_intent_present()` 贯穿 Scope / Decision / Agent / Compiler，空配置表示使用默认值而不是未请求。
7. Human Project Hub 将 blocking next actions 与 optional research 分区展示。
8. targeted + continuity：`45 passed`。
9. 全量回归：frozen v0.6.27 main `12 failures` / v0.6.28 branch `12 failures` / `NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。

## v0.6.29 已完成 — Baseline Real-Defect Remediation / Final Stabilization
1. Final Copy 数字审计区分 Claim 证据权威与字段级数字授权：只有显式绑定到当前字段的已批准/已验证/有效 Claim 数字才能作为额外 numeric token 通过；未绑定数字仍保持 BLOCK/REVIEW。
2. Compliance issue 统一为稳定可消费 shape，并拆分 `asset_issues / claim_issues`；资产引用未批准 Claim 时，asset-routing issue 优先返回，且 `claim_ids` / `asset_id` 始终可读。
3. Canonical Prompt 在生成目标层显式写入 Consumer Decision Question 与 Product Truth source-bound 执行合同；不再只依赖 Design Card 的隐式上下文。
4. Prompt 继续保持内部元数据隔离：不把产品名、Asset ID、Source Asset ID、RACE/KPI 等泄漏给图像/视频模型。
5. 本版不新增研究框架、固定资产数、固定创意方向或摄影配额；v0.6.21–v0.6.28 建立的 Agent 自主权与 current-scope completion 继续是主线。
6. 发布判断要求 `FIXED_FAILURE_COUNT > 0` 且 `NEW_FAILURE_COUNT = 0`；不再用固定“12 个失败”作为合理化基线。

## 后续开发原则
**停止版本号驱动的连续施工。** `main` 现在作为稳定 Commerce Agent 基线。后续只在真实商品/平台/市场/生产案例暴露可复现业务缺口时修改；先修业务能力，再考虑宿主集成。MCP / HTTP / Plugin / Provider Host 继续保持可选基础设施，不再成为主动开发主线。
