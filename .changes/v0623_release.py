from pathlib import Path

skill=Path('SKILL.md')
s=skill.read_text(encoding='utf-8')
s=s.replace('version: 0.6.22-dynamic-workspace-prompt','version: 0.6.23-task-scoped-delivery',1)
section='''## v0.6.23 Task-Scoped Human Delivery + Listing Authority — 当前主权威
- **人类工作区的主任务由当前 Commerce scope 决定，不再由系统拥有的全部能力反向规定。** Listing 数据可以长期保留，但视觉、内容、Prompt、生产等当前任务不因为价格、物流、退换货或卖家信息缺失而被整项目标记为 HOLD。
- `compile_upload_center()` 读取当前 request、Agent content scope、Content Graph 与 `agent_next_action.json`；只有 Listing / Search / Offer 或明确上架发布任务激活时，上架字段才进入当前主工作面。
- Listing readiness 改为 **task-scoped readiness**：只让当前平台明确 required 字段与真正 submission-sensitive 字段参与阻断；未供应的可选字段不再制造“待查证”权威。
- 非 Listing 当前任务使用 `NOT_IN_CURRENT_SCOPE`；已有 Listing / Product 数据继续保存在结构化真源和 `preserved_listing_fields`，动态化不以删除信息换简洁。
- Listing 激活时，字段按实际出现 / 平台 required / 当前提交需要动态形成，并按商品识别、类目搜索、购买决策、事实使用、Offer 履约等语义分组；不存在固定 25 字段展示配额。
- Listing Conversion Architecture 的 click / expectation fields 同样从当前存在或 required 字段投影，不再默认强塞 `price / variant / primary_image / faq / usage / package / attributes`。
- 项目总控台优先显示当前 Agent scope、动态 frontier、资产与真实风险；固定“四件事 / 四步正常使用路径”退出主权威。
- v0.6.23 发布验证：targeted + compatibility `23 passed`；相对 frozen v0.6.22 main 的全量失败 node-id `NEW_FAILURE_COUNT=0`（两侧各 12 个既有历史失败）。
- 详细变更见 `CHANGELOG_V0623.md`。

'''
marker='## v0.6.22 Dynamic Workspace + Relevant Prompt Projection — 当前主权威\n'
if '## v0.6.23 Task-Scoped Human Delivery' not in s:
    s=s.replace(marker,section+marker,1)
skill.write_text(s,encoding='utf-8')

hand=Path('CURRENT_HANDOFF.md')
h=hand.read_text(encoding='utf-8')
h=h.replace('# CBCC v0.6.22 CURRENT HANDOFF','# CBCC v0.6.23 CURRENT HANDOFF',1)
h=h.replace('当前版本：`0.6.22-dynamic-workspace-prompt`。','当前版本：`0.6.23-task-scoped-delivery`。',1)
v23='''## v0.6.23 已完成 — Task-Scoped Human Delivery + Listing Authority
1. `human_delivery.py` 不再无条件构造固定 25 个上架字段并用其支配全项目 readiness；当前 request、Agent content scope、Content Graph 与 `agent_next_action` 共同决定 Listing 是否属于当前工作范围。
2. 非 Listing 当前任务明确为 `NOT_IN_CURRENT_SCOPE`：`copy_center` 不制造价格 / 物流 / 售后 / 卖家信息缺口；已有商品与 Listing 数据继续保存在 `preserved_listing_fields` / 结构化真源。
3. Listing 当前任务只投影 supplied + platform-required + 真正 submission-sensitive 字段；可选缺口与阻断缺口分离，只有当前 required 字段可以进入 `READY_WITH_HOLDS`。
4. 精确平台类目只有在真实上架 / 发布任务需要时才成为 submission-sensitive；规划 category 继续可以服务策略，但不伪装成 Seller Center 最终类目。
5. 上架字段按实际内容动态形成语义组，而不是固定 canonical 字段表；中文项目交付与目标市场文案 / 中文释义继续并存。
6. `listing_conversion_architecture()` 的 click / post-purchase fields 改为当前字段投影；不存在固定 field quota，也不再为了“完整”制造 price / variant / FAQ / usage / package 等槽位。
7. 项目总控台改为当前 Commerce scope + Agent frontier + Assets + real risk，而不是固定“先看四件事 / 正常使用四步”。
8. `compiler.py` runtime version 更新为 `0.6.23-task-scoped-delivery`；v0.6.21–v0.6.22 Agent/Workspace/Prompt 自主权继续保留。
9. v0.6.23 targeted + compatibility：`23 passed`。
10. 全量回归相对 frozen v0.6.22 main：main 12 failures / branch 12 failures / `NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。

'''
next_marker='## 下一步唯一主任务\n'
if '## v0.6.23 已完成 — Task-Scoped Human Delivery' not in h:
    h=h.replace(next_marker,v23+next_marker,1)
start=h.find(next_marker)
if start!=-1:
    h=h[:start]+'''## 下一步唯一主任务
**继续 Commerce Agent 静态权威深审，下一主线转向 Strategy Authority 与 Asset Architecture / Compiler。重点区分“机器兼容与追溯所需的完整结构”和“人类当前任务必须看到/执行的内容”：九段 Strategy、框架清单、Foundation/资产角色、默认购买问题或 Production 合同都不得因为历史 schema 存在就成为当前任务配额。保留 Product Truth、证据、合规、真实商品身份与生产 lineage，同时让策略模块、资产角色、页面与生产深度由当前商业目标、真实证据、Surface 和 `agent_next_action` 派生。用真实跨境商品跑研究→策略→资产→Prompt→生产→replan/stop 闭环，检查是否还有“为了完整而生成”的内容。MCP/HTTP 继续只作为可选 integration layer。**
'''
hand.write_text(h,encoding='utf-8')

Path('CHANGELOG_V0623.md').write_text('''# CBCC v0.6.23 — Task-Scoped Human Delivery + Listing Authority

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
''',encoding='utf-8')
print('v0.6.23 release authorities updated')
