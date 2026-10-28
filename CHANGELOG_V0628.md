# CBCC v0.6.28 — Blocking vs Advisory Agent Frontier

## 主线
v0.6.28 解决 Agent autonomy 的最后一类明显循环权威：可选研究、支持性 Compliance/Creative/Production 信号不能因为“还能做”就强迫当前任务继续执行。

## 主要变更
- `agent_next_action.json` 明确输出 `blocking_frontier` / `advisory_frontier` 及数量。
- 只有 blocking frontier 产生 `ACTION_FRONTIER_OPEN`；仅剩 advisory frontier 时返回 `STOP_CURRENT_SCOPE_SATISFIED`。
- Research action identity 保持 `RESEARCH_OR_EVIDENCE_RESOLUTION`，通过 `blocking=false` 表达 advisory，保持宿主兼容。
- Research / Compliance / Creative / Asset / Production blocker 与 `gate_scope`、`content_requiredness` 对齐。
- Agent 显式 stop 不可越过 hard blocker。
- 新增 presence-based `request_intent_present()`：`production_run:{}` 仍表示明确生产请求。
- Human Project Hub 将 blocking 与 advisory next actions 分区展示。

## 验证
- targeted + continuity：45 passed。
- frozen v0.6.27 main：12 failures。
- v0.6.28 branch：12 failures。
- `NEW_FAILURE_COUNT=0`；`FIXED_FAILURE_COUNT=0`。

## 下一主线
对 baseline 12 项做 real-defect remediation，优先 Final Copy numeric Claim、Compliance issue contract、Prompt Product-Truth/Decision binding；旧版本/旧字符串断言只在当前语义更强时升级测试。
