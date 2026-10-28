# CBCC v0.6.7 — Semantic Workspaces

## 目标
把 v0.6.6 已经完成的“离线 SaaS 壳”继续从通用页面模板推进到**业务语义级工作区**。这不是增加固定页面数量，而是让不同任务使用不同信息架构，同时保留完整内容和动态输入规模。

## 本轮变更
- `CONTENT_SYSTEM / CONTENT_MATRIX / CONTENT_PLAN / CREATOR_CONTENT / SOCIAL_CONTENT` 成为一级 `content` 路由，不再归入 Strategy。
- `MASTER_STRATEGY_CN` 第 6 章平台内容矩阵与第 7 章 RACE 传播执行进入 Content 工作区。
- Strategy：改为动态决策地图 / 可展开决策单元，不再使用通用左侧 tabs。
- Content：改为动态内容泳道 / 内容矩阵；不预设内容方向、平台或资产数量。
- Visual：改为视觉方向接触表 + 单方向 Inspector。
- Listing：改为横向上架任务栏 + 字段工作台；目标语言与中文释义规则保持不变。
- Prompt：改为资产选择器 + CN/EN 双执行面板，不再复用通用 `module-shell`。
- Evidence：媒体、证据文档、来源文件账本同页组织，不再使用通用 tabs。
- 新增统一 `workspace-switch / workspace-panel` 交互协议，仅负责状态切换，不规定页面结构。
- 新增 `tests/test_v067_workspace_information_architecture.py`，锁定不同工作区不能退化为同一骨架，并验证动态数量。

## 验证
- v0.6.7 定向工作区测试：9 passed。
- 全量测试：93 passed / 12 failed；12 个失败与恢复的 v0.6.6 基线完全相同，没有本轮新增失败。
- `python -m compileall -q runtime builders` 通过。
- KIYUU 真实 fixture 已生成完整离线 HTML：Content 3 个动态泳道、Visual 7 个动态视图、Prompt 3 个资产选择器；通用 `module-shell` 仅保留在尚未语义重构的 Product / Market / Risk 与单资产内部页。

## 已知基线债务
全量测试现有 12 个历史失败集中在旧版本断言、inclusive photography 状态字符串、compliance issue 结构、numeric localization authorization 与旧策略文案兼容，不属于本轮 IA 改造。
