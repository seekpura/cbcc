# CBCC v0.6.29 — Final Stabilization

## 目的
本版是收口版，不增加新的系统层。目标是把 v0.6.28 handoff 已确认的 baseline 真实缺陷修掉，同时保持 Agent 自主权和当前 scope completion 不回退。

## 修复
1. **Final Copy numeric Claim field authorization**：字段显式绑定的已批准/已验证 Claim 可以授权其中的额外数字；没有字段绑定的额外数字继续被 numeric-equivalence audit 拦截。Claim evidence/publication authority 仍由 Claim Authority 负责。
2. **Stable Compliance issue contract**：每个 issue 统一包含 `scope / asset_id / code / claim_ids / severity`；`asset_issues` 与 `claim_issues` 独立暴露，资产路由问题优先，方便宿主和 Human Workspace 精确定位。
3. **Canonical Prompt execution binding**：CN/EN Prompt 都显式携带 Consumer Decision Question 与 Product Truth source-bound 约束；Parameter Trace 同步记录该绑定。

## 保留边界
- 不新增固定研究清单、方向数、资产数、RACE/AIDA/4P 强制流程或摄影字段配额。
- 不恢复流水线 Workspace。
- 不把 Product Name、Asset ID、Source Asset ID、RACE/KPI 等内部元数据注入生成模型 Prompt。
- MCP / HTTP / Plugin / Provider Host 继续是可选接入层。

## 发布门槛
- Targeted real-defect tests 必须通过。
- Full pytest 与 frozen v0.6.28 main 按失败 node-id 比较。
- `NEW_FAILURE_COUNT = 0`。
- `FIXED_FAILURE_COUNT > 0`。
