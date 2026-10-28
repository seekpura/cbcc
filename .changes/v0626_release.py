from pathlib import Path

VERSION='0.6.26-scope-readiness'
Path('VERSION').write_text(VERSION+'\n',encoding='utf-8')

p=Path('SKILL.md'); s=p.read_text(encoding='utf-8')
s=s.replace('version: 0.6.25-decision-question-authority','version: '+VERSION,1)
block="""## v0.6.26 Task-Scoped Content + Gate Readiness — 当前主权威
- **对象存在 ≠ 当前任务必须完成。** 新增 `content_requiredness.json`，把 active/preserved family 与 `required_for_current_scope` 明确拆开；Listing/Compliance 等可以继续作为支持权威存在，而不自动变成人类当前交付债务。
- ContentObject 不再统一写 `required=True`。显式 content scope、Asset/Video/Paid/Measurement/Compliance deliverable，以及“已有决策问题 + 明确资产生产意图”才会把对应 family 升级为当前 required deliverable。
- 新增 `gate_scope.json`：18 个 canonical gate 全部继续保留，但每个 Gate 增加 `required_for_current_scope / blocking_for_current_scope / scope_status / scope_reason`。
- ProjectState 继续保存 canonical Gate 与 dependency lineage；`NOT_IN_CURRENT_SCOPE` Gate 可以维持机器状态/工件，不再反向制造 readiness debt。
- Planning-only 的 Platform Compile 可以是当前需要的证据上下文，但不因动态规则待研究而阻断 Strategy；required 与 blocking 明确分离。
- Review Manifest 不再硬编码“除 ASSET_COMPILE / PRODUCTION 外全部 Gate required”；只让当前 scope 的 blocking Gate 进入 `required_missing`。
- Supporting ContentObject 仍可审阅、追溯、被 Strategy/Asset 消费，但默认不会进入 `review_pending` 阻断当前交付。
- Review HTML / checklist 同时显示 Runtime Status、Current Scope 与 Blocking，避免把机器流水线状态误读成用户工作流。
- canonical gates、Product Truth、Decision Authority、Strategy、Asset/Photography/Prompt、00–13 包、Provider/Review/Revision/Hash lineage 均继续保留。
- v0.6.26 targeted + continuity：`34 passed`；全量相对 frozen v0.6.25 main：12 vs 12，`NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。
- 详细变更见 `CHANGELOG_V0626.md`。

"""
marker='## v0.6.25 Decision Question Authority — 当前主权威\n'
if block not in s:
    if marker not in s: raise SystemExit('SKILL marker missing')
    s=s.replace(marker,block+marker,1)
p.write_text(s,encoding='utf-8')

p=Path('CURRENT_HANDOFF.md'); h=p.read_text(encoding='utf-8')
h=h.replace('# CBCC v0.6.25 CURRENT HANDOFF','# CBCC v0.6.26 CURRENT HANDOFF',1)
h=h.replace('当前版本：`0.6.25-decision-question-authority`。','当前版本：`0.6.26-scope-readiness`。',1)
marker='## 下一步唯一主任务\n'
if marker not in h: raise SystemExit('handoff next marker missing')
prefix=h.split(marker,1)[0].rstrip()
completion="""

## v0.6.26 已完成 — Task-Scoped Content + Gate Readiness
1. 新增 `scope_readiness.py` 与 `content_requiredness.json`：Content family active/preserved 与 current deliverable requiredness 分离。
2. ContentObject 的 `required` 不再全量 `True`；显式 deliverable / current production scope 才升级为 required。
3. 新增 `gate_scope.json`；18 个 canonical Gate 继续保留机器审计与 dependency lineage，但每个 Gate 有独立 `required_for_current_scope / blocking_for_current_scope / scope_status / scope_reason`。
4. ProjectState Gate record 持久化 scope 元数据；动态化不删除 gate。
5. Review Manifest 取消“除 ASSET_COMPILE/PRODUCTION 外所有 gate required”的硬编码；只有当前 scope 的 blocking gate 才形成 `required_missing`。
6. Supporting ContentObject 保留但不自动进入 `review_pending`；Human workspace 可以看到数据，而不会把支持资料变成待办。
7. Planning-only Platform Compile required/context 与 blocking 拆分，当前规则待研究不阻断可以继续完成的策略范围。
8. Review HTML / checklist 明示 Runtime Status / Current Scope / Blocking，减少流水线错觉。
9. targeted + continuity：`34 passed`。
10. 全量回归：frozen v0.6.25 main `12 failures` / v0.6.26 branch `12 failures` / `NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。

## 下一步唯一主任务
**继续 final completion / review lifecycle 深审。当前 `ProjectState.final_ready` 初始化为 False，Compiler 完成后仍无条件写回 False；需要确认 Review Accept / required scope closure / Agent stop 是否能形成真实、可解释的最终完成态。目标不是“所有 canonical gate 都 LOCKED”，而是：当前 scope required + blocking 项闭环、required review items 完成、无 unresolved blocking action 时，项目才可进入 READY；支持性 Gate/对象不阻断。必须保持局部 Revision / dependency invalidation 能把 readiness 精确打回受影响层，并继续与 Agent `STOP_CURRENT_SCOPE` / replan frontier 对齐。**
"""
h=prefix+completion+'\n'; p.write_text(h,encoding='utf-8')

Path('CHANGELOG_V0626.md').write_text("""# CBCC v0.6.26 — Task-Scoped Content + Gate Readiness

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
""",encoding='utf-8')
print('v0.6.26 release docs materialized')
