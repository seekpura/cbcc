# CBCC v0.6.27 — Current-Scope Completion Authority

## 主线
v0.6.27 把 v0.6.25 的问题/框架 scope 与 v0.6.26 的 content/gate requiredness 收束为一个真实可达的完成态。项目完成不再等于“所有 canonical gate 全部 LOCKED”，也不再依赖一个永远 False 的 flag。

## 主要变更
- 新增 `completion.py`：统一计算 current-scope gate blockers、required item review、blocking actions、open revisions、hard Agent frontier。
- Review Manifest `final_ready` 直接消费 completion authority。
- ProjectState 持久化 `completion` 与派生 `final_ready`。
- build/review/provider/revision/learning/revise/export 全部统一 refresh completion。
- Export 删除固定 required gate 列表，改为 scope-aware completion。
- Advisory research/frontier 可保留但不阻断；hard frontier 继续阻断当前 scope。
- Revision INVALIDATE 会重新打开真正受影响的当前 scope。

## 验证
- targeted + continuity：40 passed。
- frozen v0.6.26 main：12 failures。
- v0.6.27 branch：12 failures。
- `NEW_FAILURE_COUNT=0`；`FIXED_FAILURE_COUNT=0`。

## 下一主线
把 Agent frontier / Research / Compliance blocker 与 Gate Scope + Completion 完全对齐，并继续审 baseline 真实能力断链。
