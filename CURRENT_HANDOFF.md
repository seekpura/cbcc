# CBCC v0.6.10 CURRENT HANDOFF

## 唯一当前基线
GitHub 私有仓库：`seekpura/cbcc`，`main` 是唯一源码真源。当前版本：`0.6.10-visual-execution-copy-continuity`。

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

## 下一步唯一主任务
**继续用真实 KIYUU SKU 审计 Product Fidelity / Source Product Master → Provider Job → Renderer Recipe → QA / Local Revision 的生产交付链，重点确认 LOCKED_PIXEL 冻结合同在实际 Provider handoff 与局部修订时不会被降级成文字提醒。只修真实断链。**
