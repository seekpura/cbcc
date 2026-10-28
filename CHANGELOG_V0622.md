# CBCC v0.6.22 — Dynamic Workspace + Relevance-driven Prompt Projection

## Commerce 主线
v0.6.22 继续 v0.6.21 的 Agent Autonomy：静态权威不仅要从研究/策略中退出，也要从人类 Workspace、Prompt Projection、Parameter Trace、QA 和 Renderer Recipe 中退出。硬约束仍来自 Product Truth、用户锁定、平台/合规、真实商品身份与明确技术规格。

## 主要变更
- 新增 `workspace_autonomy.py`，根据真实业务对象与 `agent_next_action.json` 动态生成 Workspace 路由和首页动作。
- 单资产页面改成动态相关视图，无固定步骤序列；Agent-authored view order 优先。
- Design Card 决策、QA/来源、trace、source files 和 unknown legacy 内容保持完整可恢复。
- Prompt 只投影实际相关参数；非摄影任务不再被强迫携带焦段、快门、ISO、CCT、Prelight、偏振或人物摄影字段。
- 存在 asset-specific photography reasoning 时，已选定的策略摄影参数继续进入当前资产执行链。
- Parameter Trace、QA checks、Renderer layer plan 同步按任务相关性生成。
- 中文人类交付保持主层；目标市场可见语言保留原文并附中文释义。

## 验证
- v0.6.22 targeted + compatibility：20 passed。
- frozen main `63c696a` 与 v0.6.22 branch 全量 pytest 均为 12 个既有失败。
- 失败 node-id 差分：`NEW_FAILURE_COUNT=0`。

## 下一主线
继续深审 Listing / Human Delivery / Strategy / Asset 的隐藏静态权威，尤其是固定上架字段/readiness 对非 Listing 任务的干扰。MCP/HTTP 维持可选 integration layer，不作为下一主任务。
