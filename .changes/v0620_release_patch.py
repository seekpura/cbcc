from pathlib import Path

# SKILL.md
skill = Path('SKILL.md')
text = skill.read_text(encoding='utf-8')
text = text.replace('version: 0.6.19-plugin-http-host', 'version: 0.6.20-mcp-stdio-host')
section = """## v0.6.20 MCP stdio Host
- 新增真正可启动的 MCP stdio transport：`runtime/cbcc/mcp_stdio.py` + `python -m cbcc.mcp_stdio_cli`；stdout 只输出 newline-delimited UTF-8 JSON-RPC MCP message。
- 开发前按当前 MCP 官方规范重核协议：现代主版本为 `2026-07-28`，采用每请求 `_meta` + `server/discover`；`initialize / notifications/initialized` 只保留给 `2025-11-25` legacy 兼容路径。
- `server/discover`、`tools/list`、`tools/call` 直接消费 v0.6.18 `mcp_tool_descriptors()` / canonical Action Catalog；不维护第二套 MCP tool schema。
- 现代 `tools/list` deterministic 且按 `ActionAuthorization` scope 过滤；现代 cacheable results 带保守 `ttlMs: 0 / cacheScope: private`。
- `tools/call` 只映射 `MCP tool → canonical action → ProviderActionDispatcher`；返回 `structuredContent` 并同步 text JSON 兼容内容，PENDING 继续暴露既有 operation/status/resume 状态，不创建 MCP 侧任务库。
- unsupported modern protocol 使用 `-32022 UnsupportedProtocolVersion`；缺失现代 clientCapabilities、未知 tool、非法 arguments 使用稳定 JSON-RPC/MCP error。
- `CBCC_MCP_AUTH_MODULE` 只保存 host module 名；默认 DENY，authorization resolver 异常 fail closed 且不回显宿主异常详情。
- transport runtime 不 import/call `ProviderExecutionSurface / ProviderExecutorBridge / ProviderExecutor`；composition root 才组装既有 Surface → Dispatcher。
- legacy initialize/list/call 与 modern discover/list/call 共用同一 tool descriptor、authorization 和 dispatcher authority。
- v0.6.13–v0.6.20 provider/action/Plugin/MCP continuity 定向联测：62 passed。
- 全量回归与 v0.6.19 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`。

"""
marker = '## v0.6.19 Plugin/OpenAPI HTTP Host\n'
if '## v0.6.20 MCP stdio Host' not in text:
    if marker not in text:
        raise SystemExit('SKILL v0.6.19 marker missing')
    text = text.replace(marker, section + marker, 1)
skill.write_text(text, encoding='utf-8')

# CURRENT_HANDOFF.md
handoff = Path('CURRENT_HANDOFF.md')
text = handoff.read_text(encoding='utf-8')
text = text.replace('# CBCC v0.6.19 CURRENT HANDOFF', '# CBCC v0.6.20 CURRENT HANDOFF')
text = text.replace('当前版本：`0.6.19-plugin-http-host`。', '当前版本：`0.6.20-mcp-stdio-host`。')
old_next = """## 下一步唯一主任务
**在 v0.6.19 HTTP host 完成后，为 v0.6.18 已生成的 MCP tool descriptors 实现同样薄的真实 MCP transport host。实施前先核对当前 MCP 官方 transport/SDK 规范，再选择宿主最合适的 stdio / Streamable HTTP 入口；无论 transport 形式如何，都必须复用 canonical `mcp_tools.json` / Action Catalog / `ProviderActionDispatcher` / `ActionAuthorization`，不得复制 ProviderExecutionSurface、Bridge、Executor 或另建 completion/state authority。补 MCP initialize/list-tools/call-tool、authorization 注入、pending/status/resume 语义、schema parity 与 transport-level error mapping。**"""
new_tail = """## v0.6.20 已完成
1. 开发前重核 MCP 当前官方 GA：现代协议 `2026-07-28` 已从 initialize/session 模式转为每请求 metadata；`server/discover` 是服务器必须实现的 discovery RPC，legacy `2025-11-25` 才使用 initialize/initialized。
2. 新增 dual-era stdio host：现代 `server/discover / tools/list / tools/call` + legacy `initialize / notifications/initialized / tools/list / tools/call`。
3. stdio wire 为 UTF-8 newline-delimited JSON-RPC；stdout 仅输出 MCP message，notification 不制造无效 response。
4. MCP tools 直接来自 v0.6.18 generated `mcp_tool_descriptors()`，modern tools/list 与 checked-in canonical descriptor exact parity 且 deterministic。
5. modern request 强制 `_meta.io.modelcontextprotocol/protocolVersion=2026-07-28` 与 clientCapabilities；unsupported version 返回 `-32022` + supported versions。
6. modern `server/discover` / `tools/list` 带 `resultType=complete`、serverInfo 与保守 cache hints `ttlMs=0 / cacheScope=private`。
7. tools/list 按 canonical permission scope 过滤；默认 DENY 的调用者看不到未授权工具。
8. tools/call 只进入 `ProviderActionDispatcher`；structuredContent 保留 canonical envelope，PENDING operation/status/resume 继续使用既有 provider state，无第二套 MCP async DB。
9. `CBCC_MCP_AUTH_MODULE` 只指定宿主授权 module；resolver 异常 fail closed 且不回显异常文本；canonical secret-field 拒绝继续生效。
10. MCP transport module 不直接 import/call ProviderExecutionSurface / Bridge / Executor；`mcp_stdio_cli` 仅作为 composition root。
11. v0.6.13–v0.6.20 provider/action/Plugin/MCP continuity 定向联测：62 passed。
12. 全量回归与 v0.6.19 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`。

## 下一步唯一主任务
**在 v0.6.20 stdio host 的 MCP message semantics 之上实现当前 `2026-07-28` Streamable HTTP binding，但禁止复制一套 `server/discover / tools/list / tools/call`。先抽取/复用 transport-neutral MCP protocol processor，再实现单 `/mcp` HTTP POST binding：校验 Origin、`MCP-Protocol-Version`、`Mcp-Method`、`Mcp-Name` 与 body metadata 一致性，支持 JSON response 与必要的 request-scoped SSE 扩展边界；现代路径不得重新引入旧 HTTP+SSE GET endpoint、Mcp-Session-Id 或隐藏 session state。授权必须由 HTTP host 注入 `ActionAuthorization`，Provider runtime / completion authority 继续只在 Dispatcher 后方。**"""
if old_next in text:
    text = text.replace(old_next, new_tail)
elif '## v0.6.20 已完成' not in text:
    raise SystemExit('CURRENT_HANDOFF v0.6.19 next task marker missing')
handoff.write_text(text, encoding='utf-8')

# CHANGELOG.md
changelog = Path('CHANGELOG.md')
text = changelog.read_text(encoding='utf-8')
entry = """## 0.6.20 — MCP stdio Host
- Added a real dual-era MCP stdio host over canonical generated tool descriptors and ProviderActionDispatcher.
- Aligned modern protocol behavior to MCP 2026-07-28: server/discover, per-request metadata, resultType and cache hints.
- Retained explicit 2025-11-25 initialize/initialized compatibility without treating modern MCP as a session protocol.
- Added authorization-scoped deterministic tools/list, structured tools/call results, unsupported-version errors and fail-closed host authorization.
- Preserved one provider execution/completion authority and no direct provider-runtime imports in the MCP transport.
- See `CHANGELOG_V0620.md`.

"""
if not text.startswith('## 0.6.20 — MCP stdio Host'):
    text = entry + text
changelog.write_text(text, encoding='utf-8')
