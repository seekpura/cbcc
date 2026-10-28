from pathlib import Path

VERSION='0.6.28-agent-frontier-scope'
Path('VERSION').write_text(VERSION+'\n',encoding='utf-8')

p=Path('SKILL.md'); s=p.read_text(encoding='utf-8')
s=s.replace('version: 0.6.27-current-scope-completion','version: '+VERSION,1)
block="""## v0.6.28 Blocking vs Advisory Agent Frontier — 当前主权威
- **还有可研究 ≠ 当前任务必须继续循环。** Agent frontier 现在显式拆成 `blocking_frontier` 与 `advisory_frontier`；只有前者阻止 `STOP_CURRENT_SCOPE_SATISFIED`。
- 未解决 Research 保留原 action identity `RESEARCH_OR_EVIDENCE_RESOLUTION`，通过 `blocking=false + advisory_frontier` 表达“可选后续研究”；不通过重命名破坏旧宿主/调用方兼容。
- Research 是否 blocking 由当前 `gate_scope` 路由决定；只影响非阻断/非当前 scope Gate 的研究不会强迫 Agent 再跑一轮。
- Compliance / Creative / Asset Architecture / Production frontier 同样按 current-scope Gate requiredness / blockingness 分类，不再因为能力或对象存在就自动变成硬下一步。
- 显式 Agent Stop 可以在仅剩 advisory frontier 时成立；不能越过真正的 current-scope hard blocker。
- 修复生产意图语义：`production_run: {}` 表示“明确请求生产、使用默认配置”，不再因空映射 `bool({}) == False` 被误判成未请求；Compiler / Gate Scope / Decision Scope / Agent Frontier 共用 presence-based intent。
- Human Project Hub 分开显示“当前范围必须先解决”与“可选后续优化 / 研究（不阻断当前完成）”。
- v0.6.28 targeted + continuity：`45 passed`；全量相对 frozen v0.6.27 main：12 vs 12，`NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。
- 详细变更见 `CHANGELOG_V0628.md`。

"""
marker='## v0.6.27 Current-Scope Completion Authority — 当前主权威\n'
if block not in s:
    if marker not in s: raise SystemExit('SKILL v0.6.27 marker missing')
    s=s.replace(marker,block+marker,1)
p.write_text(s,encoding='utf-8')

p=Path('CURRENT_HANDOFF.md'); h=p.read_text(encoding='utf-8')
h=h.replace('# CBCC v0.6.27 CURRENT HANDOFF','# CBCC v0.6.28 CURRENT HANDOFF',1)
h=h.replace('当前版本：`0.6.27-current-scope-completion`。','当前版本：`0.6.28-agent-frontier-scope`。',1)
marker='## 下一步唯一主任务\n'
if marker not in h: raise SystemExit('handoff next-task marker missing')
prefix=h.split(marker,1)[0].rstrip()
completion="""

## v0.6.28 已完成 — Blocking vs Advisory Agent Frontier
1. `compile_agent_next_action()` 消费 v0.6.26 `gate_scope` / `content_requiredness`，Frontier 拆成 blocking 与 advisory 两层。
2. Advisory Research 保留可见与可执行，但不再把 Agent 状态强制保持 `ACTION_FRONTIER_OPEN`；无 hard blocker 时真正返回 `STOP_CURRENT_SCOPE_SATISFIED`。
3. Research action identity 保持 `RESEARCH_OR_EVIDENCE_RESOLUTION`；兼容由 `blocking=false` 与 frontier 分类表达，不破坏旧宿主 action routing。
4. Compliance / Asset coverage / Creative direction / Production blocker 都按当前 required/blocking scope 路由；支持性对象或未来优化不制造硬循环。
5. 显式 Agent Stop 不能覆盖 current-scope hard blocker；若仅剩 advisory frontier，则 Stop 可成立。
6. 修复 `production_run:{}` 的真实生产意图断链：presence-based `request_intent_present()` 贯穿 Scope / Decision / Agent / Compiler，空配置表示使用默认值而不是未请求。
7. Human Project Hub 将 blocking next actions 与 optional research 分区展示。
8. targeted + continuity：`45 passed`。
9. 全量回归：frozen v0.6.27 main `12 failures` / v0.6.28 branch `12 failures` / `NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。

## 下一步唯一主任务
**进入 baseline real-defect remediation，不再把剩余 12 项统一叫“历史失败”。优先审并修真实业务断链：① Final Copy 数值型 Claim 的字段授权是否能正确允许已批准数字，同时继续阻断无授权数字；② Compliance issue shape / unapproved-claim asset routing 是否稳定且可被调用方可靠消费；③ Canonical Prompt 是否仍显式保留 Product Truth 与 Consumer Decision Question 的执行绑定，而不是只剩隐式语义。对于仅断言旧 0.5.x version/status/英文标题的测试，只在确认当前语义更强时升级测试，不倒退当前中文优先、prelight、runtime version 与更强合同。目标是让 `FIXED_FAILURE_COUNT>0`，同时继续保证 `NEW_FAILURE_COUNT=0`。**
"""
p.write_text(prefix+completion+'\n',encoding='utf-8')

Path('CHANGELOG_V0628.md').write_text("""# CBCC v0.6.28 — Blocking vs Advisory Agent Frontier

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
""",encoding='utf-8')
print('v0.6.28 release docs materialized')
