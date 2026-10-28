# CBCC v0.6.23 — Task-Scoped Human Delivery + Listing Authority

## Commerce 主线
v0.6.23 延续 v0.6.21 Agent Autonomy 与 v0.6.22 Dynamic Workspace：系统拥有某项能力或历史字段，不等于该能力/字段拥有当前人类工作区主权。当前商业任务决定主工作面，结构化数据负责保存与追溯。

## 主要变更
- Human Delivery 新增当前任务 scope 推导：request、Agent content scope、Content Graph 与 `agent_next_action` 共同决定 Listing 是否激活。
- 非 Listing 任务不再被 `price / shipping / returns / seller_info` 缺失制造 HOLD；已有数据仍保留。
- Listing readiness 只由当前 supplied / platform-required / submission-sensitive 字段决定；可选 gap 与 blocking gap 分离。
- 精确平台类目只在真实 submission scope 中参与阻断，规划 category 不冒充 Seller Center 最终类目。
- 上架字段按当前实际内容形成语义组，不再固定展示 canonical 25 字段。
- Listing Conversion Architecture 的 click / expectation fields 改为从当前字段与 required rules 投影，不再固定槽位。
- 项目总控台改为当前 scope、Agent frontier、资产与真实风险，而不是固定四步导航。

## 验证
- targeted + compatibility：23 passed。
- frozen v0.6.22 main：12 个既有 failures。
- v0.6.23 branch：12 个既有 failures。
- `NEW_FAILURE_COUNT=0`；`FIXED_FAILURE_COUNT=0`。

## 下一主线
继续审计 Strategy Authority 与 Asset Architecture / Compiler 的隐藏静态权威：保留机器兼容、证据和 lineage，但不让历史九段结构、框架清单、Foundation/资产角色或生产 schema 自动变成人类当前任务配额。
