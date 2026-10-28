from pathlib import Path

VERSION='0.6.29-final-stabilization'

Path('VERSION').write_text(VERSION+'\n', encoding='utf-8')

compiler=Path('runtime/cbcc/compiler.py')
text=compiler.read_text(encoding='utf-8')
old="st.data['runtime_version']='0.6.28-agent-frontier-scope'"
new=f"st.data['runtime_version']='{VERSION}'"
if old not in text:
    raise SystemExit('compiler runtime version anchor not found')
compiler.write_text(text.replace(old,new,1), encoding='utf-8')

skill=Path('SKILL.md')
s=skill.read_text(encoding='utf-8')
if 'version: 0.6.28-agent-frontier-scope' not in s:
    raise SystemExit('SKILL version anchor not found')
s=s.replace('version: 0.6.28-agent-frontier-scope',f'version: {VERSION}',1)
anchor='## v0.6.28 Blocking vs Advisory Agent Frontier — 当前主权威\n'
section='''## v0.6.29 Final Stabilization — 当前主权威
- 本版不新增架构，专门清理 baseline 中确认存在的真实业务断链；Commerce Agent 自主权、动态 Scope、Completion 与 blocking/advisory frontier 保持不变。
- Final Copy 数字等价审计现在把“字段显式绑定的已批准 Claim 数字”视为字段级 numeric authority；未绑定数字继续阻断。Claim 的真实证据等级与发布资格仍由 Claim Authority 单独决定，不能用 `APPROVED` 标签绕过证据边界。
- Compliance issue 统一稳定 shape：`scope / asset_id / code / claim_ids / severity`；asset-routing issue 与 claim-ledger issue 分流，调用方可以可靠定位哪个资产引用了未批准 Claim。
- Canonical Prompt 在 Render Objective 显式保留 `Consumer Decision Question + Product Truth binding`，同时继续禁止 Product Name、Asset ID、RACE/KPI 等内部元数据泄漏到生成模型 Prompt。
- v0.6.29 的发布门槛不是“再加能力”，而是 baseline 实际修复：`FIXED_FAILURE_COUNT > 0` 且 `NEW_FAILURE_COUNT = 0`。
- 这一版之后停止版本号驱动的连续扩张；只有真实电商任务/案例暴露新的业务缺口时，才从当前 `main` 派生下一次修改。
- 详细变更见 `CHANGELOG_V0629.md`。

'''
if anchor not in s:
    raise SystemExit('SKILL v0.6.28 anchor not found')
s=s.replace(anchor,section+anchor,1)
skill.write_text(s,encoding='utf-8')

handoff=Path('CURRENT_HANDOFF.md')
h=handoff.read_text(encoding='utf-8')
h=h.replace('# CBCC v0.6.28 CURRENT HANDOFF','# CBCC v0.6.29 CURRENT HANDOFF',1)
h=h.replace('当前版本：`0.6.28-agent-frontier-scope`。',f'当前版本：`{VERSION}`。',1)
next_anchor='## 下一步唯一主任务\n'
section='''## v0.6.29 已完成 — Baseline Real-Defect Remediation / Final Stabilization
1. Final Copy 数字审计区分 Claim 证据权威与字段级数字授权：只有显式绑定到当前字段的已批准/已验证/有效 Claim 数字才能作为额外 numeric token 通过；未绑定数字仍保持 BLOCK/REVIEW。
2. Compliance issue 统一为稳定可消费 shape，并拆分 `asset_issues / claim_issues`；资产引用未批准 Claim 时，asset-routing issue 优先返回，且 `claim_ids` / `asset_id` 始终可读。
3. Canonical Prompt 在生成目标层显式写入 Consumer Decision Question 与 Product Truth source-bound 执行合同；不再只依赖 Design Card 的隐式上下文。
4. Prompt 继续保持内部元数据隔离：不把产品名、Asset ID、Source Asset ID、RACE/KPI 等泄漏给图像/视频模型。
5. 本版不新增研究框架、固定资产数、固定创意方向或摄影配额；v0.6.21–v0.6.28 建立的 Agent 自主权与 current-scope completion 继续是主线。
6. 发布判断要求 `FIXED_FAILURE_COUNT > 0` 且 `NEW_FAILURE_COUNT = 0`；不再用固定“12 个失败”作为合理化基线。

'''
if next_anchor not in h:
    raise SystemExit('CURRENT_HANDOFF next-task anchor not found')
h=h.replace(next_anchor,section+'## 后续开发原则\n',1)
# The old next-task prose is intentionally replaced: stabilization is now complete.
marker='**进入 baseline real-defect remediation'
pos=h.find(marker)
if pos!=-1:
    h=h[:pos] + '''**停止版本号驱动的连续施工。** `main` 现在作为稳定 Commerce Agent 基线。后续只在真实商品/平台/市场/生产案例暴露可复现业务缺口时修改；先修业务能力，再考虑宿主集成。MCP / HTTP / Plugin / Provider Host 继续保持可选基础设施，不再成为主动开发主线。\n'''
handoff.write_text(h,encoding='utf-8')

Path('CHANGELOG_V0629.md').write_text('''# CBCC v0.6.29 — Final Stabilization

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
''',encoding='utf-8')

print('v0.6.29 release metadata prepared')
