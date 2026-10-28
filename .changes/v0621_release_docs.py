from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'missing release-doc target: {label}')
    return text.replace(old, new, 1)


# VERSION
Path('VERSION').write_text('0.6.21-commerce-agent-autonomy\n', encoding='utf-8')

# SKILL: put commerce-agent authority ahead of transport history.
p = Path('SKILL.md')
text = p.read_text(encoding='utf-8')
text = text.replace('version: 0.6.20-mcp-stdio-host', 'version: 0.6.21-commerce-agent-autonomy', 1)
text = text.replace(
    'description: Positive-first cross-border commerce strategy authority with product truth, market/SKU/economics, positioning, culture, listing, visual/photography, dynamic assets, production handoff and learning.',
    'description: Autonomous cross-border commerce agent for product truth, decision-driven research, market/SKU/economics, strategy, listing, content, visual/photography, dynamic assets, production, review and learning.',
    1,
)
purpose = "Create a professional cross-border ecommerce plan **before** governance machinery becomes visible. The user-facing mainline is positive commercial design: understand the product, market and shopper; decide positioning and message architecture; design platform-native content, visual and photography; compile dynamic assets; then use evidence/platform/compliance/review as background guardrails.\n"
insert = purpose + """

## v0.6.21 Commerce Agent Autonomy — 当前主权威
- **冻结事实与硬边界，Agent 自主决定完成路径。** Product Truth、用户明确锁定、平台/法规硬约束、Claim 证据、真实商品身份/LOCKED PIXEL、目标输出技术规格属于不可擅自改写的边界；研究范围、策略路径、内容范围、资产数量、创意机制、方向数量、构图/摄影/CMF、生产路线和迭代深度属于 Agent 决策。
- 宿主 Agent 应优先自行形成 `agent_plan` / `agent_decisions`，而不是让 Runtime 的兼容 heuristics 代替智能判断。Plan 可以按当前任务只声明真正需要的 research/content/creative/framework/iteration 决策，不要求填写固定表单。
- Research 以**信息增益是否仍会改变重要商业决策**作为继续/停止条件；禁止为了固定来源数、竞品数、关键词数、页面数或“研究完整度”机械扩写。
- Content/Asset 由真实消费者问题、目标 Surface、商业任务、证据与生产需求派生；不存在默认 7 图/9 图、固定 Hero/Proof/How-to 套餐、固定内容家族配额。
- Creative exploration 不规定 6–12 mechanisms、3–5 directions 或固定差异数量。Agent 可以只形成一个明显正确的方向，也可以在不确定性较高时扩展更多 materially distinct 方向；数量必须来自任务需要，而不是系统配额。
- AIDA / FABE / 4P / STP / JTBD / Funnel / RACE 都是**可选思考工具**。只有它们能改善当前决策时才启用；不得因为框架存在就强制生成对应阶段、页面、资产或叙事。
- Asset expression 必须从该资产自身的 buyer decision / evidence plane / Surface / production mode 推导；禁止固定 intent→layout 映射和轮换式空间节奏伪装“多样性”。
- Photography / composition / lighting / CMF 参数是执行工具，不是必填专业字段。只有相关时才进入策划；一旦 Agent 决定某个参数会影响结果，该参数必须继续贯穿 Design Card → CN/EN Canonical Prompt → Parameter Trace → Machine Contract → Production，不得在执行链丢失。
- `agent_next_action.json` 是当前轮的动态 action frontier：Agent 根据真实未解决问题决定继续研究、重规划、生产/修复、复核，或停止。**不存在固定下一步流水线。**
- MCP / Plugin / HTTP / Provider Host 属于**可选宿主/生产接入基础设施**。它们服务电商能力，但不拥有研究、策略、设计或产品路线权威，也不应成为主迭代目标。
- 详细变更见 `CHANGELOG_V0621.md`。
"""
text = replace_once(text, purpose, insert, 'SKILL autonomy section')
p.write_text(text, encoding='utf-8')

# CHANGELOG index
p = Path('CHANGELOG.md')
text = p.read_text(encoding='utf-8')
entry = """## 0.6.21 — Commerce Agent Autonomy
- Re-centered CBCC on autonomous ecommerce decision-making rather than transport/protocol expansion.
- Added agent-owned research scope and stopping rules, dynamic content scope, arbitrary creative mechanisms/direction counts, and a replan/stop action frontier.
- Removed default all-family content expansion, fixed creative quotas/layout rotations, mandatory marketing-framework bundles, and generic script/RACE sequencing.
- Made photography precision relevance-driven: execution parameters are required only when they materially control the asset or preserve verified product truth.
- Kept MCP/Plugin/HTTP as optional integration infrastructure, not product-strategy authority.
- Targeted autonomy suite: 20 passed. See `CHANGELOG_V0621.md`.

"""
if not text.startswith('## 0.6.21 — Commerce Agent Autonomy'):
    text = entry + text
p.write_text(text, encoding='utf-8')

# CURRENT_HANDOFF
p = Path('CURRENT_HANDOFF.md')
text = p.read_text(encoding='utf-8')
text = text.replace('# CBCC v0.6.20 CURRENT HANDOFF', '# CBCC v0.6.21 CURRENT HANDOFF', 1)
text = text.replace('当前版本：`0.6.20-mcp-stdio-host`。', '当前版本：`0.6.21-commerce-agent-autonomy`。', 1)
old_mainline = 'Product Truth → Research → Action → Communication → Evaluation → Product Visual Intelligence → Creative Opportunity / Council → Dynamic Surface / Asset → Design Card → CN/EN Canonical Prompt → Production / Review / Learning → Chinese-first Semantic Workspace.'
new_mainline = 'Commerce Goal → Product Truth / Hard Boundaries → Agent Evidence-Gap Discovery → Agent Strategy & Surface Decisions → Dynamic Content / Asset Architecture → Dynamic Creative / Photography / CMF → CN/EN Canonical Prompt / Production Contract → Production / Review / Learning → Agent Replan or Stop → Chinese-first Semantic Workspace.'
text = text.replace(old_mainline, new_mainline, 1)
text = text.replace(
    '1. 当前 ChatGPT Plugin 仍是 Skills-only，七大 Python Runtime 未 MCP 化。',
    '1. MCP / Plugin / HTTP / Provider Host 已作为可选宿主与生产接入能力存在；它们不是电商研究、策略、内容或设计权威，后续主线不得为了 transport 完整度挤占 Commerce Agent 能力。',
    1,
)
section = """

## v0.6.21 已完成 — Commerce Agent Autonomy
1. 新增 `agent_autonomy.py`，明确 Hard Constraints 与 Agent Decisions：事实/合规/平台硬边界/真实商品身份被冻结，研究、策略、内容、资产、创意、摄影/CMF、生产路线、迭代深度由 Agent 决定。
2. 编译物化 `agent_autonomy_plan.json`；宿主可直接提供 `agent_plan / agent_decisions`，其决定优先于 Runtime fallback heuristic。
3. Research 从“调用方先写固定研究清单”升级为 Agent 自主 gap discovery；fallback 也只产生能改变当前商业决策的缺口。研究没有固定来源数/竞品数/query 数，停止条件是信息增益不再改变重要决策。
4. Content Graph 不再默认展开全部 `DEFAULT_FAMILIES`；只从目标 Surface、明确任务和真实项目能力信号派生，Agent 显式 scope 不被 Runtime 扩写。
5. Creative Opportunity 支持任意 Agent-authored mechanisms/domain/count；原 12 机制仅是无 Agent 决策时的兼容 fallback，fallback 也取消固定 12 上限。
6. Creative Direction 取消 6–12 mechanism、3–5 direction、固定差异数等配额；方向数量按当前相关度/不确定性动态决定。
7. 删除固定 decision-intent → layout/view/context 模板和 5 种 spatial rhythm 轮换；资产表达优先消费自身 `visual_production_signature` / `agent_visual_expression`。
8. AIDA / FABE / 4P / STP / JTBD / Funnel / RACE 改为可选工具；不再每个项目自动注入框架，也不再把所有资产强制标为 RACE=COMMUNICATION。
9. 平台内容矩阵移除固定“钩子→价值/证据→异议→CTA”叙事权威；脚本/叙事由当前消费者问题、证据关系、Surface 和交互任务决定。
10. 新增 `agent_next_action.json`：动态暴露 Research / Asset Replan / Creative / Compliance / Production 等 frontier；Agent 有最终路由权并可在当前目标满足时停止，不存在固定步骤序列。
11. Photography Contract 改为 relevance-driven precision：COMPOSITE/CG/AI 不为过校验虚构真实摄影参数；语义 perspective 可代替死焦段；numeric occupancy 只在锁定时要求；LOCKED_PIXEL/精确商品色仍保留严格 color fidelity。
12. 定向自主权测试：20 passed。发布仍需与最新 main 做全量失败 node-id 差分，`NEW_FAILURE_COUNT=0` 才能进入 main。
13. v0.6.17–v0.6.20 的 Provider/Plugin/MCP 基础设施继续保留，但从 v0.6.21 起明确降为可选 integration layer，不再作为 Commerce 产品主路线。
"""
if '## v0.6.21 已完成 — Commerce Agent Autonomy' not in text:
    marker = '\n## 下一步唯一主任务\n'
    if marker not in text:
        raise SystemExit('CURRENT_HANDOFF next-task marker missing')
    text = text.replace(marker, section + marker, 1)
old_next = "**在 v0.6.20 stdio host 的 MCP message semantics 之上实现当前 `2026-07-28` Streamable HTTP binding，但禁止复制一套 `server/discover / tools/list / tools/call`。先抽取/复用 transport-neutral MCP protocol processor，再实现单 `/mcp` HTTP POST binding：校验 Origin、`MCP-Protocol-Version`、`Mcp-Method`、`Mcp-Name` 与 body metadata 一致性，支持 JSON response 与必要的 request-scoped SSE 扩展边界；现代路径不得重新引入旧 HTTP+SSE GET endpoint、Mcp-Session-Id 或隐藏 session state。授权必须由 HTTP host 注入 `ActionAuthorization`，Provider runtime / completion authority 继续只在 Dispatcher 后方。**"
new_next = "**继续 Commerce Agent 自主权深审与真实电商验证。重点检查 Workspace / Strategy / Listing / Prompt / Asset / Production 是否仍存在固定页面、固定模块、固定方向/资产/研究数量、固定叙事或‘为了字段完整而填参数’的隐藏静态权威；以真实商品任务验证 Agent 能自主发现缺口、选择研究与框架、设计动态资产体系、让相关摄影/构图/灯光/CMF参数真实进入下游 Prompt/Production，并根据结果自主 replan 或 stop。MCP/HTTP 仅在实际宿主接入需求出现时维护，不作为下一主任务。**"
text = replace_once(text, old_next, new_next, 'CURRENT_HANDOFF next task')
p.write_text(text, encoding='utf-8')
