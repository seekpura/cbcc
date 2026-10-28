# CBCC v0.6.26 — Task-Scoped Content + Gate Readiness

## 主线
v0.6.26 把 Agent task scope 从问题/框架继续推进到 Content Object requiredness 与 canonical Gate readiness。机器审计结构继续完整，人类当前工作只由真正 required/blocking 项形成债务。

## 主要变更
- 新增 `content_requiredness.json`，active family 与 current deliverable requiredness 分离。
- ContentObject `required` 改为 task-scoped，不再统一 True。
- 新增 `gate_scope.json`；所有 canonical gate 保留但显式记录 required/blocking/current-scope 状态。
- ProjectState 持久化 Gate scope 元数据。
- Review Manifest 只让 current-scope blocking gate 进入 required_missing。
- Supporting ContentObject 不再自动进入 review_pending。
- Planning-only Platform Compile 可作为 required context 但 non-blocking。
- Review UI 显示 Runtime Status / Current Scope / Blocking。

## 验证
- targeted + continuity：34 passed。
- frozen v0.6.25 main：12 failures。
- v0.6.26 branch：12 failures。
- `NEW_FAILURE_COUNT=0`；`FIXED_FAILURE_COUNT=0`。

## 下一主线
修正 final completion / review lifecycle：从 current-scope blocking closure 与 required item review 推导真实 final readiness，并让 Revision / Agent Stop 与之对齐。
