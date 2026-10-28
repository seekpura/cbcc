from pathlib import Path

VERSION='0.6.27-current-scope-completion'
Path('VERSION').write_text(VERSION+'\n',encoding='utf-8')

p=Path('SKILL.md'); s=p.read_text(encoding='utf-8')
s=s.replace('version: 0.6.26-scope-readiness','version: '+VERSION,1)
block="""## v0.6.27 Current-Scope Completion Authority — 当前主权威
- **`final_ready` 不再是永远 False 的静态旗标。** 新增 `completion.py`，完成态由当前 scope 的真实闭环条件派生。
- READY 条件：当前 scope 的 blocking Gate 没有 PENDING/HOLD/MISSING/INVALIDATED 等阻断；required 非 Gate 交付项已到可审状态并完成必要 review；blocking research/action 已解决；open local revision 已闭环；不存在当前 scope 的 hard Agent frontier。
- Supporting / advisory Gate、ContentObject、Research Action 与 Agent frontier 可以继续存在，不再为了“还有可做的事”阻止当前交付完成。
- `RESEARCH_OR_EVIDENCE_RESOLUTION` 只有在对应 unresolved action 对当前 blocking scope 真正 blocking 时才阻止完成；planning-only 的 advisory research 可以保留并继续显示。
- `AUTHOR_DECISION_OR_ASSET_SCOPE / REPLAN_ASSET_ARCHITECTURE / AUTHOR_OR_SELECT_CREATIVE_DIRECTION / RESOLVE_COMPLIANCE_BOUNDARY / PRODUCE_RESUME_OR_REPAIR` 等 hard frontier 继续阻断对应当前 scope。
- Review Manifest 的 `final_ready` 直接来自 completion authority；`ProjectState.final_ready` 与 `completion` 会在 build/review/provider/revision/learning 后统一刷新并持久化。
- CLI `export` 删除旧的固定 Gate required 列表，不再要求一套静态流水线全部 LOCKED；Export 与 Review/State 共用同一 current-scope completion。
- Revision 仍会按 dependency graph INVALIDATE 受影响层，并立即重新计算 readiness；支持层变化不应无故推翻无关已完成 scope。
- v0.6.27 targeted + continuity：`40 passed`；全量相对 frozen v0.6.26 main：12 vs 12，`NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。
- 详细变更见 `CHANGELOG_V0627.md`。

"""
marker='## v0.6.26 Task-Scoped Content + Gate Readiness — 当前主权威\n'
if block not in s:
    if marker not in s: raise SystemExit('SKILL marker missing')
    s=s.replace(marker,block+marker,1)
p.write_text(s,encoding='utf-8')

p=Path('CURRENT_HANDOFF.md'); h=p.read_text(encoding='utf-8')
h=h.replace('# CBCC v0.6.26 CURRENT HANDOFF','# CBCC v0.6.27 CURRENT HANDOFF',1)
h=h.replace('当前版本：`0.6.26-scope-readiness`。','当前版本：`0.6.27-current-scope-completion`。',1)
marker='## 下一步唯一主任务\n'
if marker not in h: raise SystemExit('handoff marker missing')
prefix=h.split(marker,1)[0].rstrip()
completion="""

## v0.6.27 已完成 — Current-Scope Completion Authority
1. 新增 `completion.py`，用 current scope blockers / required review / blocking actions / open revisions / hard Agent frontier 派生 READY。
2. `final_ready` 从静态 flag 变为可重复计算结果；Target-only / Strategy-only scope 在没有真实阻断时可以完成。
3. Asset/Content/Production 当前 required item 仍必须完成 item review；未审阅不会误报 READY。
4. Supporting / advisory Gate、ContentObject、Research、Agent frontier 可以保留，不自动制造“永远做不完”的状态。
5. Review Manifest、ProjectState、Review Workspace、CLI Export 统一消费同一 completion authority。
6. `build / review-apply / provider-ingest / revision-compile / revision-ingest / learning-apply / revise / export` 均刷新并持久化 completion。
7. Revision 继续通过 dependency graph 精确 INVALIDATE；若影响当前 required/blocking scope，READY 会重新打开。
8. targeted + continuity：`40 passed`。
9. 全量回归：frozen v0.6.26 main `12 failures` / v0.6.27 branch `12 failures` / `NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。

## 下一步唯一主任务
**继续 Agent frontier / Research / Compliance 的 scope 对齐深审。重点核对 `compile_agent_next_action()` 仍会把所有 unresolved research 放进 frontier、Compliance/Creative/Production 的 blocker 是否完全按 v0.6.26 Gate Scope 与 v0.6.27 Completion Authority 路由，以及 Human Workspace 是否把 advisory frontier 与 blocking next action 清楚分开。目标是让 Agent 真正能 STOP / REPLAN，而不是因为任何可选研究或能力存在就持续循环。随后继续审 baseline 12 项里的真实断链，优先修业务能力，不为旧版本字符串回退。**
"""
h=prefix+completion+'\n'; p.write_text(h,encoding='utf-8')

Path('CHANGELOG_V0627.md').write_text("""# CBCC v0.6.27 — Current-Scope Completion Authority

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
""",encoding='utf-8')
print('v0.6.27 release docs materialized')
