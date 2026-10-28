# Cross-Border Commerce Creative — v0.6.29

CBCC 是面向跨境电商的 Commerce Agent：从 Product Truth、证据与平台约束出发，动态完成市场/竞品/人群研究、SKU/Offer、策略、Listing/Search、内容、视觉/摄影/CMF、图片/视频资产、生产、Review 与学习闭环。

## 当前状态

- **唯一源码真源**：`main`
- **当前稳定版本**：`0.6.29-final-stabilization`
- **发行语义版本**：`v0.6.29`
- **开发状态**：主线能力已收口；停止为了版本号继续扩张，只在真实商品/平台/生产案例暴露可复现业务缺口时修改。
- **稳定化证据**：v0.6.29 已通过 targeted real-defect tests、近期 Agent autonomy continuity 与 full-regression node-id diff；发布门槛是 `NEW_FAILURE_COUNT = 0` 且 `FIXED_FAILURE_COUNT > 0`。

详细变更见 `CHANGELOG_V0629.md`，当前交接状态见 `CURRENT_HANDOFF.md`。

## 核心主线

`Commerce Goal → Product Truth / Hard Boundaries → Agent Evidence-Gap Discovery → Agent Strategy & Surface Decisions → Dynamic Content / Asset Architecture → Dynamic Creative / Photography / CMF → CN/EN Canonical Prompt / Production Contract → Production / Review / Learning → Agent Replan or Stop → Chinese-first Semantic Workspace`

关键原则：

- Agent 根据当前商品、市场、平台、证据与任务范围决定研究、策略、内容、Surface、资产与创意方向；不以固定 9 图/12 图、固定方向数、固定 RACE/AIDA/4P 流程或摄影字段配额替代判断。
- Product Truth、Claim Authority、Compliance、平台当前证据与 Review 作为后台约束；未知项保持 UNKNOWN / 待查证，不由 Runtime 猜测。
- 中文优先做人类交付；目标市场可见文案保持目标语言并提供中文释义/说明。
- 摄影、CMF、构图、材质、色彩管理、真实商品锁定、可编辑/冻结层与 Product Fidelity 进入真实执行合同与 Canonical Prompt，而不是只停留在策略文字。
- Render Prompt 隔离 Product Name、Asset/Project/Direction ID、RACE、KPI 等内部工程元数据；精确可见文案由 deterministic composition / Copy 权威负责。
- Completion 以 current scope 的真实 blocker、required review、revision 与 Agent frontier 派生；“还有可研究”不等于“当前任务不能完成”。

## 三种使用/安装方式

### 1. ChatGPT 私人 Plugin / Skill

正式 Release 会生成：

- `cross-border-commerce-creative-plugin-v0.6.29.zip`
- `cross-border-commerce-creative-skill-v0.6.29.zip`

Plugin 包保持 Agent Plugins 1.0 清单，并把当前 GitHub 源码完整快照放入 Skill resources。私人 ChatGPT Plugin 默认使用 Skill 能力；**本地 Python Runtime 不会因为被打包进 Plugin 就自动变成云端工具**。如需直接调用 Provider/MCP/HTTP Runtime，必须使用已验证的宿主或 MCP/HTTP 部署。

### 2. 本地 Runtime

CBCC 当前按“完整仓库 Runtime”运行，不把资源拆成一个不完整的 `pip install cbcc` 包：

```bash
python bin/cbcc.py --help
bash tests/run_smoke.sh
python bin/cbcc.py audit --root .
```

CLI 主入口：`bin/cbcc.py`；实现位于 `runtime/cbcc/`。完整安装与验证见 `INSTALL.md`。

### 3. Provider / Plugin HTTP / MCP Host

Plugin/OpenAPI HTTP Host：

```bash
PYTHONPATH=runtime python -m cbcc.plugin_http_cli --bind 127.0.0.1 --port 8787
```

MCP stdio Host：

```bash
PYTHONPATH=runtime python -m cbcc.mcp_stdio_cli
```

Provider credentials、SDK/client 与 authorization 由宿主瞬时注入，不写入项目状态、descriptor 或命令行参数。

## 发行产物

源码内提供两层构建：

```bash
python scripts/build_plugin_dist.py --output-dir dist
python scripts/build_dist.py dist/cross-border-commerce-creative-runtime-v0.6.29.zip
```

GitHub release workflow 会在构建前执行 smoke + v0.6.29 定向/连续性验证，随后生成 Plugin / Skill / Runtime ZIP、SHA256 校验文件并发布到 `v0.6.29` Release。

## 主要入口

- `SKILL.md` — 当前 Agent/Skill 主权威
- `runtime/cbcc/compiler.py` — 项目编译主线
- `runtime/cbcc/decision_authority.py` — 当前任务/决策问题权威
- `runtime/cbcc/completion.py` — current-scope completion
- `runtime/cbcc/claim_authority.py` / `compliance.py` — Claim / Compliance
- `runtime/cbcc/prompt_compiler.py` — CN/EN Canonical Prompt
- `runtime/cbcc/provider_surface.py` — Provider Execution Surface
- `runtime/cbcc/plugin_http.py` / `plugin_http_cli.py` — Plugin/OpenAPI HTTP Host
- `runtime/cbcc/mcp_stdio.py` / `mcp_stdio_cli.py` — MCP stdio Host
- `transport/plugin_openapi.json` / `transport/mcp_tools.json` — canonical transport descriptors
- `CURRENT_HANDOFF.md` — 当前唯一交接说明

## 重要边界

1. 精确平台类目、规则、费率、法规与时效信息必须来自当前官方数据、用户资料或实时研究。
2. MCP / HTTP / Plugin / Provider Host 是接入与执行层，不取代 Commerce Agent 的研究、策略、内容和设计权威。
3. GitHub `main` 是源码真源；ChatGPT 私人 Plugin、Skill ZIP 与 Runtime ZIP 都是从 `main` 派生的发行物。
4. 发布包不得重新引入固定研究清单、固定资产数、固定创意方向、固定页面模板或流水线 Workspace。
