# CBCC v0.6.24 — Task-Scoped Strategy + Asset Authority

## 主线
v0.6.24 把 v0.6.21–v0.6.23 的 Agent autonomy 继续推进到 Strategy Authority 与 Asset Architecture：机器层保留稳定 schema / lineage，人类层和当前执行层按真实任务投影。

## 主要变更
- 机器 Strategy 九段继续保留；人类 Strategy 取消固定九段展示配额。
- 框架改为显式选择；RACE 未选时不再生成执行表或给内容机械标 `COMMUNICATION`。
- P0/P1/P2、A/B、下一动作只来自真实 HOLD / research gap / evaluation signal；允许当前范围停止。
- 无资产 Surface 时不制造 GALLERY/VISUAL；shopper question 留在 Strategy/Listing 等正确对象。
- Asset handoff 改为 explicit-only，不再按列表顺序自动串链。
- legacy Strategy/asset-package 兼容测试升级为“机器完整、人类动态”，不为旧编号标题倒退当前合同。

## 验证
- targeted + continuity：28 passed。
- frozen v0.6.23 main：12 failures。
- v0.6.24 branch：12 failures。
- `NEW_FAILURE_COUNT=0`；`FIXED_FAILURE_COUNT=0`。

## Baseline 审计原则
baseline node-id 逐项判断：真实能力断链修实现；旧英文标题、旧版本前缀、旧状态字符串或已被更强证据/合规合同取代的断言更新测试。固定失败数量不拥有发布权威。

## 下一主线
继续 Compiler / Decision Trace / default shopper questions 的静态权威审计，去除“无输入也自动制造问题/框架”的残留，同时保持 Product Truth、Evidence、Compliance、Asset/Provider lineage。
