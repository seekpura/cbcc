# CBCC v0.6.7 CURRENT HANDOFF

## 唯一当前基线
GitHub 私有仓库：`seekpura/cbcc`，目标主线版本 `0.6.7-semantic-workspaces`。

源码恢复真源来自项目文件：`cross-border-commerce-creative-v0.6.6-human-workspace-zh-first.zip`。此前 GitHub 仅存在 9 个残缺 `.bootstrap/chunk-*`，并未真正 materialize v0.6.6 源码；本轮已识别并纠正该同步事实。不要再把残缺 bootstrap 树当成源码完成态。

## 当前主线
Product Truth → Research → Action → Communication → Evaluation → Product Visual Intelligence → Creative Opportunity / Council → Dynamic Surface / Asset → Design Card → CN/EN Canonical Prompt → Production / Review / Learning → Chinese-first Semantic Workspace.

## v0.6.7 已完成
1. Content 成为一级路由；`CONTENT_SYSTEM` 等内容文档与主策略第 6/7 章进入 Content，不再挤在 Strategy。
2. Strategy / Content / Visual / Listing / Prompt / Evidence 各自拥有不同信息架构，不再复用“左侧 tabs + 右侧白卡正文”。
3. 页面与视图数量完全由真实内容动态产生，没有固定方向数、内容数或资产数。
4. 新增 v0.6.7 IA 回归测试；定向测试 9 passed。
5. 全量测试 93 passed / 12 baseline failures，本轮没有新增失败。
6. KIYUU fixture 已完成真实 HTML 编译验证。

## 明确边界
1. 当前 ChatGPT Plugin 仍是 Skills-only，七大 Python Runtime 未 MCP 化。
2. 当前平台精确类目/规则/费率必须来自实时官方数据或用户资料；离线 Runtime 不猜。
3. Product / Market / Risk 与单资产内部页仍保留通用 `module-shell`，这是下一阶段人类交互债务，不影响本轮六个核心语义工作区完成态。
4. 历史 12 个 pytest 失败是恢复基线已有兼容性债务，不能伪称全绿，也不要为了“绿测试”倒退当前能力。

## 下一步唯一主任务
**重构单资产工作区：让 Design Card / Visual Execution / Photography / Copy / Prompt / QA 按资产生产决策形成专用生产台，而不是继续使用通用 `module-shell`。随后用真实 KIYUU SKU 检查每个资产从策划参数 → Canonical Prompt → 人类工作区是否完全一致。**
