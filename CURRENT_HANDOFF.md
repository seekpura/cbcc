# CBCC v0.6.8 CURRENT HANDOFF

## 唯一当前基线
GitHub 私有仓库：`seekpura/cbcc`，`main` 是唯一源码真源。当前版本：`0.6.8-asset-production-workspace`。

2026-10-28 已完成一次性仓库恢复：此前残缺 `.bootstrap` 中间态已被完整 canonical source tree 替换；恢复 workflow 与 bootstrap 文件已经随恢复提交退出仓库。后续禁止重新引入 chunk / Actions 解包源码作为日常开发方式。

## 固定 GitHub 开发方式
日常修改使用 Git Database 增量链：读取 `main HEAD + tree` → 对 changed / added / deleted 文件构建新 tree → 一个 commit → `update_ref(expected_sha=旧 HEAD)`。小文本可直接 Contents API；大文件的小改动优先传递 Git patch，而不是复制整个大文件或重新上传全仓。

私有 ChatGPT 插件是 GitHub 源码的派生发行包，不是反向源码权威。

## 当前主线
Product Truth → Research → Action → Communication → Evaluation → Product Visual Intelligence → Creative Opportunity / Council → Dynamic Surface / Asset → Design Card → CN/EN Canonical Prompt → Production / Review / Learning → Chinese-first Semantic Workspace.

## v0.6.7 已完成
1. Content 成为一级路由；Strategy / Content / Visual / Listing / Prompt / Evidence 使用不同 IA。
2. 页面 / 方向 / 内容 / 资产数量由真实输入动态产生。
3. 中文优先人类交付与目标市场语言并存。

## v0.6.8 已完成
1. 单资产详情退出通用 `module-shell`，进入独立 `asset-production-workspace`。
2. Design Card / 购买决策、画面执行、摄影 / CMF、文案、Prompt 执行、QA / 来源按当前资产真实内容动态出现。
3. 中文与英文 / 目标模型 Prompt 合并到同一个执行台；生产备注跟随 Prompt，Parameter Trace / 合同 / 源文件进入 QA。
4. Legacy 未分类内容不会丢失，自动进入 QA / 来源。
5. 移动端与打印态已经适配新的资产生产台。
6. v0.6.7 + v0.6.8 定向联测：10 passed。
7. 同源全量复测：98 passed / 13 baseline failures；本轮没有新增失败。此前 `93 passed / 12 failures` 记录已纠正。
8. KIYUU Malaysia TikTok fixture 已完成真实 HTML 编译：3 个动态资产生产台，单资产页无 `module-shell`。

## 明确边界
1. 当前 ChatGPT Plugin 仍是 Skills-only，七大 Python Runtime 未 MCP 化。
2. 当前平台精确类目 / 规则 / 费率必须来自实时官方数据或用户资料；离线 Runtime 不猜。
3. Product / Market / Risk 仍保留通用 `module-shell`，属于下一阶段人类交互债务。
4. 13 个历史 pytest 失败是恢复基线已有兼容性债务，不能为了“全绿”倒退当前能力。

## 下一步唯一主任务
**用真实 KIYUU SKU 对每个资产做“策划参数 → Design Card → CN/EN Canonical Prompt → 单资产生产台”一致性审计，发现参数被策划但没有进入执行 Prompt / 人类工作区时，只修最小责任层；同时按真实使用需要逐步拆 Product / Market / Risk 的通用页面，不机械制造新模板。**
