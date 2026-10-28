from pathlib import Path

# SKILL.md
p=Path('SKILL.md'); s=p.read_text(encoding='utf-8')
s=s.replace('version: 0.6.23-task-scoped-delivery','version: 0.6.24-task-scoped-strategy-asset',1)
section='''## v0.6.24 Task-Scoped Strategy + Asset Authority — 当前主权威
- **机器兼容结构与人类当前任务分层。** `strategy_authority.json` 继续保留九段 canonical section、证据、追溯和资产包绑定；`MASTER_STRATEGY_CN.md` 只投影当前 Commerce 目标真正相关的决策域，不再把九段目录当成人类配额。
- STP / JTBD / 4P / Funnel / AIDA / FABE / Fogg / Means-End / Signaling / FIRST / Cognitive Budget / Belief Sequence / Commerce Response Ladder / RACE 均为可选决策镜头。只有 Agent / 用户显式选择时才进入当前 Strategy Authority；默认不再全量注入。
- RACE 未显式启用时，机器 section 07 保持兼容键但内容为空；Content Matrix 不再机械写 `race_stage=COMMUNICATION`。显式选择 RACE 时完整保留。
- P0/P1/P2 与 A/B 不再为了“策略完整”自动制造未来工作。只有真实 Compliance HOLD、未解决 Research、明确 Evaluation/Experiment 信号才形成当前动作；没有实质未解决项时允许 `CURRENT_SCOPE_CAN_STOP`。
- Asset Architecture 不再在没有视觉/视频/Creator/Paid Surface 时把 shopper question 强制变成 GALLERY 图片。问题可继续留在 Strategy / Listing，直到真实资产 Surface 被激活。
- Asset 列表顺序只用于展示；没有显式 `handoff` 时不再自动生成 A→B→C 链。资产关系为 `EXPLICIT_ONLY`，显式关系继续保留。
- Foundation roles、Product Truth、Claim/Evidence、Photography/CMF、00–13 资产包、Provider / Review / Revision / Hash lineage 全部继续保留；动态化不是删能力。
- v0.6.24 targeted + continuity：`28 passed`；全量相对 frozen v0.6.23 main：12 vs 12，`NEW_FAILURE_COUNT=0`。
- baseline failing node-id 必须逐项判断真实断链还是旧语义断言；禁止用固定失败数量替代能力审计，也禁止为旧字符串测试倒退当前合同。
- 详细变更见 `CHANGELOG_V0624.md`。

'''
marker='## v0.6.23 Task-Scoped Human Delivery + Listing Authority — 当前主权威\n'
if '## v0.6.24 Task-Scoped Strategy + Asset Authority' not in s:
    s=s.replace(marker,section+marker,1)
p.write_text(s,encoding='utf-8')

# CURRENT_HANDOFF.md
p=Path('CURRENT_HANDOFF.md'); h=p.read_text(encoding='utf-8')
h=h.replace('# CBCC v0.6.23 CURRENT HANDOFF','# CBCC v0.6.24 CURRENT HANDOFF',1)
h=h.replace('当前版本：`0.6.23-task-scoped-delivery`。','当前版本：`0.6.24-task-scoped-strategy-asset`。',1)
h=h.replace('4. 12 个历史 pytest 失败属于既有兼容性债务，不能为了“全绿”倒退当前能力。','4. baseline failing node-id 必须逐项审计：真实能力断链要修，旧字符串/旧版本/已被更强合同取代的断言要升级测试；不得用固定失败数量替代能力判断，也不得为了“全绿”倒退当前能力。',1)
v24='''## v0.6.24 已完成 — Task-Scoped Strategy + Asset Authority
1. `strategy_authority.json` 继续保留九段 canonical machine schema；人类 `MASTER_STRATEGY_CN.md` 改为 task-scoped projection，只显示当前商业目标真正需要的决策域。
2. 历史全框架注入退出权威：STP/JTBD/4P/Funnel/AIDA/FABE/Fogg/Means-End/Signaling/FIRST/Cognitive Budget/Belief Sequence/Commerce Response Ladder/RACE 只在 Agent/用户选择时进入当前策略。
3. RACE 未启用时 section 07 保持兼容键但为空，Content Matrix 不再机械写 `COMMUNICATION`；显式 RACE 仍完整保留。
4. `build_risk_priority_depth()` 不再强制填满 P0/P1/P2，也不默认制造 A/B；真实 Compliance HOLD、Research gap、Evaluation/Experiment 才生成动作。无实质缺口时 `CURRENT_SCOPE_CAN_STOP`。
5. Asset Architecture 在无实际资产 Surface 时不再把 shopper question 变成 GALLERY/VISUAL；保留为 `unrouted_questions`，等待真实 Surface/任务激活。
6. 取消资产 A→B→C 自动 handoff；关系模式为 `EXPLICIT_ONLY`，显式 handoff 原样保留。
7. 机器九段、Product Truth、Claim/Evidence、Foundation、Photography/CMF、00–13 资产包、Provider/Review/Revision/Hash lineage 均保留。
8. v0.5 Strategy 兼容测试同步升级：继续严查机器九段和 legacy asset package preservation，但不再要求未显式启用的 RACE 出现在人类 Markdown。
9. targeted + continuity：`28 passed`。
10. 全量回归：frozen v0.6.23 main `12 failures` / v0.6.24 branch `12 failures` / `NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。
11. 本轮额外审计 12 个 baseline node-id，确认其中多项是旧英文标题、旧版本前缀、旧状态字符串或被更强 Claim/Compliance 合同取代的断言；以后继续逐项分类，不能把“12”本身当发布标准。

'''
next_marker='## 下一步唯一主任务\n'
if '## v0.6.24 已完成 — Task-Scoped Strategy + Asset Authority' not in h:
    h=h.replace(next_marker,v24+next_marker,1)
idx=h.find(next_marker)
if idx!=-1:
    h=h[:idx]+'''## 下一步唯一主任务
**继续 Commerce Agent 静态权威深审，下一轮优先处理 Compiler / Decision Trace / default shopper questions：当前 `compiler.py` 仍存在无输入时自动生成四个 shopper questions、默认 decision framework 列表，以及部分兼容层可能把“系统会什么”误当成“本项目必须研究/回答什么”。目标是让问题发现、Decision Trace、Framework selection、Content/Asset scope 全部由当前 Commerce goal、Product Truth、证据缺口、Surface 与 Agent plan 派生，同时保留机器兼容、证据、合规与生产 lineage。继续用真实跨境商品验证 Research → Strategy → Content/Asset → Prompt → Production → Replan/Stop，检查是否仍有为完整度制造的问题、页面、字段、实验或资产。MCP/HTTP 继续只作为可选 integration layer。**
'''
p.write_text(h,encoding='utf-8')

# Changelog
Path('CHANGELOG_V0624.md').write_text('''# CBCC v0.6.24 — Task-Scoped Strategy + Asset Authority

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
''',encoding='utf-8')
print('v0.6.24 release authorities updated')
