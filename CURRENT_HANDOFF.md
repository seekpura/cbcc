# CBCC v0.6.20 CURRENT HANDOFF

## 唯一当前基线
GitHub 私有仓库：`seekpura/cbcc`，`main` 是唯一源码真源。当前版本：`0.6.20-mcp-host`。

2026-10-28 已完成一次性仓库恢复；`.bootstrap` / chunk / 源码解包 workflow 已退出。私有 ChatGPT 插件是 GitHub 源码的派生发行包，不是反向源码权威。

## 固定 GitHub 开发方式
日常修改使用 Git Database 增量链：读取 `main HEAD + tree` → changed / added / deleted 构新 tree → 一个 commit → `update_ref(expected_sha=旧 HEAD)`。大文件小改动优先使用小型 Git patch 传输，不复制完整大文件。

## 当前主线
Product Truth → Research → Action → Communication → Evaluation → Product Visual Intelligence → Creative Opportunity / Council → Dynamic Surface / Asset → Design Card → CN/EN Canonical Prompt → Production / Review / Learning → Chinese-first Semantic Workspace.

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
1. 当前 ChatGPT Plugin 仍是 Skills-only，七大 Python Runtime 未 MCP 化。
2. 当前平台精确类目 / 规则 / 费率必须来自实时官方数据或用户资料；离线 Runtime 不猜。
3. Product / Market / Risk 仍保留通用 `module-shell`，只有真实使用需求证明需要时再拆，不为页面差异机械制造模板。
4. 13 个历史 pytest 失败属于既有兼容性债务，不能为了“全绿”倒退当前能力。
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
1. 先核对 MCP 2026-07-28 官方规范和 Python SDK v2，再实现 transport；本轮实际 CI 使用 `mcp 2.3.0`。
2. 新增真实 `MCPActionTransportAdapter + CBCCMCPHost`；low-level Server 直接消费 canonical MCP descriptors/input schemas，避免 decorator/signature 重新派生 schema。
3. 官方 SDK 负责 `server/discover`、协议协商与旧 initialize fallback；CBCC 不复制 MCP wire protocol。
4. 真实 in-process Client、Streamable HTTP Client、stdio subprocess 三条 E2E 均使用官方 MCP Client 跑通；协议协商结果为 `2026-07-28`。
5. `tools/list` 根据宿主 `ActionAuthorization` scope 暴露工具；默认无 scope 时工具列表为空；直接调用已知工具仍由 Dispatcher 返回 DENIED。
6. `tools/call` 只进入 `ProviderActionDispatcher`；secret-like arguments、required fields、operation scope、PENDING/status/resume 继续复用 canonical Action contract。
7. `CBCC_MCP_AUTH_MODULE` 只保存模块名；HTTP headers / request meta 不被 CBCC 视为可信身份，只传给宿主 resolver 做实际验证。
8. Streamable HTTP 保留官方 DNS-rebinding protection；CLI 对 loopback 生成精确端口 Host/Origin allowlist，公网必须显式 allowlist 或显式 trusted-proxy ownership，拒绝 `:*` wildcard。
9. v0.6.13–v0.6.20 provider/action/Plugin/MCP continuity + transport security 定向联测：61 passed。
10. 全量回归与 v0.6.19 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`；发布判断仍只看新增失败集合。

## 下一步唯一主任务
**把 v0.6.20 MCP transport 从“宿主授权 resolver”推进到生产部署授权合同：先重新核对 MCP 2026-07-28 当前 Authorization / Protected Resource Metadata / OAuth 规范与 Python SDK v2 `AuthSettings / TokenVerifier` 接口，再为 Streamable HTTP 增加可选的原生 Bearer/OAuth gate，并把验证后的 principal/scopes 映射为现有 `ActionAuthorization`。必须保持 stdio 本地模式独立、tool arguments 无 credential 字段、ProviderActionDispatcher 继续是唯一 action authority；禁止把 access token 写入 project state / bridge / executor / result / logs。补 unauthorized/insufficient-scope/metadata discovery/token-verifier failure/secret-redaction E2E。**
