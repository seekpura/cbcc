# CBCC v0.6.14 CURRENT HANDOFF

## 唯一当前基线
GitHub 私有仓库：`seekpura/cbcc`，`main` 是唯一源码真源。当前版本：`0.6.14-provider-executor-lifecycle`。

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

## 下一步唯一主任务
**把 ProviderExecutor 从 reference protocol 推进到宿主可调用的 Adapter Registry / Executor Bridge：定义 provider adapter discovery、capability declaration、retry/backoff/rate-limit/cancel/reconcile 语义，并接一个真实 Provider profile 时保持凭证外置。与此同时继续以现有 `Provider Job → Executor → Production Receipt → Ingest` 为唯一执行链，不建立旁路。**
