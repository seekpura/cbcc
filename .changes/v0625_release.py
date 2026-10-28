from pathlib import Path

VERSION='0.6.25-decision-question-authority'

# VERSION
Path('VERSION').write_text(VERSION+'\n',encoding='utf-8')

# SKILL
p=Path('SKILL.md'); s=p.read_text(encoding='utf-8')
s=s.replace('version: 0.6.24-task-scoped-strategy-asset','version: '+VERSION,1)
block="""## v0.6.25 Decision Question Authority — 当前主权威
- **消费者问题允许为空。** Runtime 不再因为目标平台、PDP Surface 或“电商通常要回答这些问题”而自动制造 `What is it / Why relevant / What evidence / What after purchase` 四问。
- 新增 `decision_question_authority.json`：问题只来自用户/调用方、Agent content scope / decision trace、显式 Asset/Video job，以及当前 Listing/CX 中真实存在的异议；每条问题保留 origin / decision job / surface / family / evidence lineage。
- Decision Trace 不再按问题数组位置机械映射 `ACTION / COMMUNICATION / EVALUATION` 或 `IDENTIFY / RELATE / VERIFY / USE`；RACE stage 只有在 RACE 被显式选择且该问题本身有阶段信息时才出现。
- Decision Framework 不再有默认全家桶。`decision_frameworks` / Agent `strategy_frameworks` 是唯一选择权威；AIDA / FABE / 4P 的 persuasion compiler 也只消费显式选中的框架。
- Content family 继续 task-scoped：目标 Surface 单独存在只是执行约束，不会制造 Listing / Search / Offer / Visual 工作；只有真实任务信号才激活 family。
- 兼容边界：当已经存在明确 shopper question 且明确请求 `compile_assets / production_run` 时，请求 Surface 可以决定这些**已有问题**应落入 VISUAL / VIDEO / CREATOR / CX 等哪种资产 family；这是路由，不是 Surface 配额。
- 明确请求资产/生产但没有任何决策问题/Asset job 时，不再用 Runtime 默认问题补洞，而是在 `agent_next_action.json` 暴露 `AUTHOR_DECISION_OR_ASSET_SCOPE`，交还 Agent 决策。
- Product Truth、Evidence、Market/Listing、Strategy 九段机器兼容结构、动态 Asset、Photography/CMF、00–13 包、Provider / Review / Revision / Hash lineage 全部继续保留。
- v0.6.25 targeted + continuity：`46 passed`；全量相对 frozen v0.6.24 main：12 vs 12，`NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。
- 详细变更见 `CHANGELOG_V0625.md`。

"""
marker='## v0.6.24 Task-Scoped Strategy + Asset Authority — 当前主权威\n'
if block not in s:
    if marker not in s: raise SystemExit('SKILL v0.6.24 marker missing')
    s=s.replace(marker,block+marker,1)
p.write_text(s,encoding='utf-8')

# CURRENT_HANDOFF
p=Path('CURRENT_HANDOFF.md'); h=p.read_text(encoding='utf-8')
h=h.replace('# CBCC v0.6.24 CURRENT HANDOFF','# CBCC v0.6.25 CURRENT HANDOFF',1)
h=h.replace('当前版本：`0.6.24-task-scoped-strategy-asset`。','当前版本：`0.6.25-decision-question-authority`。',1)
marker='## 下一步唯一主任务\n'
if marker not in h: raise SystemExit('handoff next-task marker missing')
prefix=h.split(marker,1)[0].rstrip()
completion="""

## v0.6.25 已完成 — Decision Question + Framework Authority
1. 新增 `decision_authority.py`，把 Shopper Question、Decision Trace、Framework Selection、Content-family activation 的当前任务权威从 Compiler 静态默认中拆出。
2. 删除 Compiler 无输入时自动制造的四个 shopper questions；问题可以为空，空本身不是错误。
3. 问题来源只接受用户/调用方、Agent authored scope/trace、显式 Asset/Video job、以及当前 Listing/CX 的真实异议；物化 `decision_question_authority.json` 记录来源与 lineage。
4. 删除问题数组位置 → RACE/Funnel stage 的静态映射；没有显式 RACE 与 stage 时 `race_stage=None`。
5. 删除 Compiler 默认 decision framework 列表；只有用户/Agent 明确选择的框架进入 Decision Trace / persuasion compiler。
6. Target Surface 单独存在不再制造 Content family；平台/Surface 是约束，不是“系统能做什么就都做什么”的配额。
7. 保留真实生产兼容：已有 shopper question + `compile_assets/production_run` 时，Surface 可以把这些已有问题路由到 VISUAL / VIDEO / CREATOR / CX 等资产 family；不会凭空添加 Listing/Search/Offer 工作。
8. 请求资产/生产但没有问题/Asset job 时，`agent_next_action.json` 暴露 `AUTHOR_DECISION_OR_ASSET_SCOPE`；Agent 先定义真正决策任务，Runtime 不用默认问题填空。
9. v0.6.21 的静态源码字符串测试同步升级为当前更强合同；真实 v0.5.10 / v0.5.8 多品类生产兼容保持通过。
10. targeted + continuity：`46 passed`。
11. 全量回归：frozen v0.6.24 main `12 failures` / v0.6.25 branch `12 failures` / `NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。

## 下一步唯一主任务
**继续 Commerce Agent 静态权威深审，下一轮优先处理 Content Object / Gate / Requiredness / readiness：当前 Compiler 仍对生成出来的 ContentObject 统一写 `required=True`，多个 Gate 仍以固定 `READY_REVIEW / PENDING` 语义组织，可能继续把“对象存在”误当成“当前任务必须完成”。目标是让 Content Object requiredness、Gate/readiness、Creative/Execution readiness 与 Agent 当前 scope / real blockers / requested deliverable 对齐；机器审计与 lineage 继续保留，但不能反过来制造工作。继续用真实多品类与 KIYUU 类资产验证 Strategy → Content/Asset → Prompt → Production → Review / Stop，逐项审 baseline node-id 中的真实断链。MCP/HTTP/Provider Host 继续只作为可选 integration layer。**
"""
h=prefix+completion+'\n'
p.write_text(h,encoding='utf-8')

# CHANGELOG
Path('CHANGELOG_V0625.md').write_text("""# CBCC v0.6.25 — Decision Question + Framework Authority

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
""",encoding='utf-8')

print('v0.6.25 release docs materialized')
