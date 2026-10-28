# CBCC v0.6.25 — Decision Question + Framework Authority

## 主线
v0.6.25 继续把 v0.6.21–v0.6.24 的 Agent autonomy 推进到 Compiler 的问题发现、Decision Trace 与 Framework Selection：系统能力只作为工具箱，当前项目的问题/框架/内容范围由真实任务决定。

## 主要变更
- 新增 `decision_question_authority.json`；问题允许为空，不再自动制造通用四问。
- Shopper Question 仅来自显式/当前真实信号，并保留 origin / job / family / surface / evidence trace。
- Decision Trace 不再按问题位置硬编码 RACE/Funnel 阶段。
- Framework selection 改为用户/Agent explicit-only；没有默认全框架列表。
- Target Surface 单独存在不创建 Content family。
- 已有明确 shopper question + 资产生产意图时，Surface 只负责把已有问题路由到对应资产 family，保持真实多品类生产兼容。
- 请求资产/生产但没有决策 scope 时，Agent frontier 返回 `AUTHOR_DECISION_OR_ASSET_SCOPE`，而不是用 Runtime 默认问题补齐。
- v0.6.21 静态源码断言升级为当前 authority 名称；旧能力测试继续保留业务语义而非旧实现名。

## 验证
- targeted + continuity：46 passed。
- frozen v0.6.24 main：12 failures。
- v0.6.25 branch：12 failures。
- `NEW_FAILURE_COUNT=0`；`FIXED_FAILURE_COUNT=0`。

## 发布边界
Surface 是 execution constraint，不是工作配额；Runtime capability 是工具箱，不是当前 scope。只有真实目标、显式 Agent/user 决策和当前证据/异议信号可以生成 shopper decision job。

## 下一主线
深审 Content Object requiredness 与 Gate/readiness 的静态权威，避免 `required=True` / 固定 gate status 把存在的能力重新变成必须完成的任务。
