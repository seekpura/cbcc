# CBCC v0.6.21 — Commerce Agent Autonomy

## 目标
把 CBCC 的主开发权威从“固定流程 / 固定框架 / 固定创意配额 / 固定摄影字段”重新拉回跨境电商 Agent：事实与硬边界被冻结，完成目标的路径由 Agent 根据当前商品、市场、平台、证据、Surface 和实际结果动态决定。

## 核心变化
1. 新增 `runtime/cbcc/agent_autonomy.py`，把 Product Truth / 用户锁定 / 平台硬约束 / 合规 / 商品身份 / 技术规格定义为硬边界；研究范围、内容范围、资产数量、创意探索、方向数量、摄影/CMF、生产路线、迭代深度定义为 Agent 决策。
2. 编译时物化 `agent_autonomy_plan.json`；宿主 Agent 可以直接提供 `agent_plan` / `agent_decisions`，其研究、内容和创意决定优先于 Runtime fallback heuristics。
3. Research 不再要求调用方预先写完固定研究清单。没有 Agent plan 时，只从真实决策缺口推导研究任务；研究停止条件以“是否还会改变重要决策”为准，不使用固定来源数、竞品数或查询数。
4. Content Graph 不再缺省展开所有 `DEFAULT_FAMILIES`。内容家族由目标 Surface、明确资产任务、视频/广告/反馈/测量/合规/生产信号动态派生；Agent 显式选择时 Runtime 不扩写。
5. Creative Opportunity 支持 Agent 自主提供任意机制、任意数量、任意 domain；原有 12 个机制降级为无 Agent 计划时的兼容 fallback。
6. fallback Creative Opportunity 取消固定 12 个上限，改为按当前相关度阈值保留 materially relevant set。
7. Creative Direction 取消 6–12 mechanisms / 3–5 directions / 4 个差异维度等数值权威。Agent 可输出 1、2、7 或其他合理数量；fallback 也按相关度动态确定方向数。
8. Asset expression 删除固定 decision-intent → layout 模板和五种空间节奏轮换；构图、视角、上下文优先消费当前资产 `visual_production_signature` 或 Agent `agent_visual_expression`。
9. AIDA / FABE / 4P 不再默认自动注入；STP / JTBD / 4P / Funnel / RACE 也改为 Agent/用户按需调用的思考工具，不再是每个商品强制经过的流程。
10. 平台内容矩阵不再强制“钩子 → 价值/证据 → 异议 → CTA”，也不再把全部资产强制标为 RACE=COMMUNICATION；叙事结构和阶段由当前资产任务决定。
11. 新增 `agent_next_action.json`：当前编译后返回动态 decision frontier，Agent 可继续研究、重规划资产、选择/重做创意、解决合规、生产/修复，或在当前目标已满足时停止；不存在固定下一步序列。
12. Photography Contract 改为 relevance-driven precision：不再为了“显得专业”强制填写焦段、产品占比、灯位、modifier、CCT、色彩管理等字段。只有实际需要、用户/Agent 已锁定、重复拍摄要求或商品色彩/像素真实性要求时才升级为硬执行约束。
13. 语义透视/视角合同可以替代死焦段；COMPOSITE / CG / AI 场景不再机械套真实摄影字段；LOCKED_PIXEL 等真实商品身份场景继续严格保留 color/product fidelity 硬边界。
14. MCP / Plugin / HTTP 能力保留为可选宿主集成基础设施，但不再作为 CBCC 电商产品能力的主迭代路线。

## Agent 原则
- Freeze facts and boundaries; let the Agent decide the path.
- Dynamic does not mean random: 关键决定保留 Evidence → Decision → Implementation trace。
- Research for information gain, not quota completion.
- Use frameworks as tools, not as mandatory funnels.
- Any photography / composition / lighting / CMF parameter that the Agent decides is materially relevant must continue downstream into Design Card / Prompt / Machine Contract / Production; irrelevant parameters should remain absent rather than fabricated.
- Continue/replan only while another action can materially improve correctness, commercial usefulness or execution readiness.

## 定向验证
- Commerce Agent autonomy / dynamic content & creative scope: 9 tests.
- Optional frameworks + autonomous replan/stop frontier: 6 tests.
- Relevance-driven photography precision: 5 tests.
- Current targeted autonomy suite: 20 passed.

## 发布条件
- 全量 pytest 与发布时最新 `main` 使用相同环境运行。
- 以失败 node-id 集合对比；`NEW_FAILURE_COUNT` 必须为 0。
- release 前删除 `.changes` staging/diagnostics 与临时 workflow，只保留正式源码、测试和文档。
