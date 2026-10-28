# Plugin / Runtime Boundary — v0.6.6

CBCC 当前有两种执行路径，必须区分：

## 1. ChatGPT Skills-only Plugin
- 通过 `SKILL.md`、知识/Prompt/Schema/Platform Packs 指导 ChatGPT。
- 可使用宿主提供的 Web、文件、图片理解、ImageGen、文档等能力。
- 当前插件包 **没有 `mcp.json`**，因此不会在聊天中直接暴露 CBCC 的 Python 函数为可调用 MCP Tools。

## 2. Local Runtime / CLI
- `runtime/cbcc/tools/seven_agent.py` 与 `toolkits/11_seven_agent_contracts/` 提供七个一级工具合同。
- `bin/cbcc.py` 负责项目 state / build / revise / provider / learning / export 等运行时流程。
- 这些 Python 能力在本地 Runtime 中是真执行，不等同于 ChatGPT Skills-only 插件的“遵循同一合同”。

## 3. 若要真正 MCP 化
需要为七大工具与项目 Runtime 建立可部署的 MCP Server，并在插件中加入经过验证的 `mcp.json` endpoint / auth。未完成这一步前，不得宣称“ChatGPT 插件已直接调用七大 Python Tools”。
