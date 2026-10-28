from pathlib import Path

ROOT = Path('.')

(ROOT / 'VERSION').write_text('0.6.20\n', encoding='utf-8')

skill = ROOT / 'SKILL.md'
text = skill.read_text(encoding='utf-8')
text = text.replace('version: 0.6.19-plugin-http-host', 'version: 0.6.20-mcp-host')
section = """## v0.6.20 Real MCP Host
- 新增真正可运行的 MCP host，基于官方 Model Context Protocol Python SDK v2；本轮 CI 实际验证 `mcp 2.3.0`，协议基线为 `2026-07-28`。
- 使用 low-level `Server` 的 `on_list_tools / on_call_tool / get_tool_input_schema`，工具名、描述和 `inputSchema` 原样消费 v0.6.18 `mcp_tool_descriptors()`；不由 Python 函数签名重新生成第二套 schema。
- 官方 SDK 负责 `server/discover`、当前协议协商与旧客户端 initialize fallback；CBCC 不手写协议兼容层。
- 真正跑通两种 transport：本地 `stdio` 与部署型 `Streamable HTTP`；没有新增 legacy SSE transport。
- MCP transport 唯一执行链仍是 `MCP tool → ProviderActionDispatcher → ProviderExecutionSurface`；`mcp_host.py` 不 import/call Surface、Bridge 或 Executor。
- `CBCC_MCP_AUTH_MODULE` 只指定宿主授权模块；request headers / `_meta` 只作为宿主验证输入，CBCC 不把客户端 header 直接当身份；默认 DENY。
- `tools/list` 按 ActionAuthorization scope 过滤；`tools/call` 继续经过 canonical Dispatcher，credential-like tool arguments 仍在执行前拒绝。
- PENDING / status / resume 复用 v0.6.17 稳定 operation ID 与既有 provider persisted state；没有第二套 MCP async database。
- Streamable HTTP CLI 默认使用精确端口 Host/Origin allowlist；公网 bind 必须显式 allowlist 或明确交给可信反向代理做 Host 校验；拒绝当前 SDK 已知存在匹配边界的 `:*` wildcard 模式。
- `claims_mcp_server_exists=false / mcp_server_included=false` 继续只描述 v0.6.17/18 mapping/descriptor 层本身不内嵌 server；仓库从 v0.6.20 起已真实包含 MCP runtime。

"""
marker = '## v0.6.19 Plugin/OpenAPI HTTP Host\n'
if section not in text:
    if marker not in text:
        raise SystemExit('SKILL v0.6.19 marker missing')
    text = text.replace(marker, section + marker)
skill.write_text(text, encoding='utf-8')

handoff = ROOT / 'CURRENT_HANDOFF.md'
text = handoff.read_text(encoding='utf-8')
text = text.replace('# CBCC v0.6.19 CURRENT HANDOFF', '# CBCC v0.6.20 CURRENT HANDOFF')
text = text.replace('当前版本：`0.6.19-plugin-http-host`。', '当前版本：`0.6.20-mcp-host`。')
old_next = """## 下一步唯一主任务
**在 v0.6.19 HTTP host 完成后，为 v0.6.18 已生成的 MCP tool descriptors 实现同样薄的真实 MCP transport host。实施前先核对当前 MCP 官方 transport/SDK 规范，再选择宿主最合适的 stdio / Streamable HTTP 入口；无论 transport 形式如何，都必须复用 canonical `mcp_tools.json` / Action Catalog / `ProviderActionDispatcher` / `ActionAuthorization`，不得复制 ProviderExecutionSurface、Bridge、Executor 或另建 completion/state authority。补 MCP initialize/list-tools/call-tool、authorization 注入、pending/status/resume 语义、schema parity 与 transport-level error mapping。**"""
new_tail = """## v0.6.20 已完成
1. 先核对 MCP 2026-07-28 官方规范和 Python SDK v2，再实现 transport；本轮实际 CI 使用 `mcp 2.3.0`。
2. 新增真实 `MCPActionTransportAdapter + CBCCMCPHost`；low-level Server 直接消费 canonical MCP descriptors/input schemas，避免 decorator/signature 重新派生 schema。
3. 官方 SDK 负责 `server/discover`、协议协商与旧 initialize fallback；CBCC 不复制 MCP wire protocol。
4. 真实 in-process Client、Streamable HTTP Client、stdio subprocess 三条 E2E 均使用官方 MCP Client 跑通；协议协商结果为 `2026-07-28`。
5. `tools/list` 根据宿主 `ActionAuthorization` scope 暴露工具；默认无 scope 时工具列表为空；直接调用已知工具仍由 Dispatcher 返回 DENIED。
6. `tools/call` 只进入 `ProviderActionDispatcher`；secret-like arguments、required fields、operation scope、PENDING/status/resume 继续复用 canonical Action contract。
7. `CBCC_MCP_AUTH_MODULE` 只保存模块名；HTTP headers / request meta 不被 CBCC 视为可信身份，只传给宿主 resolver 做实际验证。
8. Streamable HTTP 保留官方 DNS-rebinding protection；CLI 对 loopback 生成精确端口 Host/Origin allowlist，公网必须显式 allowlist 或显式 trusted-proxy ownership，拒绝 `:*` wildcard。
9. v0.6.13–v0.6.20 provider/action/Plugin/MCP continuity + transport security 定向联测：61 passed。
10. 全量回归与 v0.6.19 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`；发布判断仍只看新增失败集合。

## 下一步唯一主任务
**把 v0.6.20 MCP transport 从“宿主授权 resolver”推进到生产部署授权合同：先重新核对 MCP 2026-07-28 当前 Authorization / Protected Resource Metadata / OAuth 规范与 Python SDK v2 `AuthSettings / TokenVerifier` 接口，再为 Streamable HTTP 增加可选的原生 Bearer/OAuth gate，并把验证后的 principal/scopes 映射为现有 `ActionAuthorization`。必须保持 stdio 本地模式独立、tool arguments 无 credential 字段、ProviderActionDispatcher 继续是唯一 action authority；禁止把 access token 写入 project state / bridge / executor / result / logs。补 unauthorized/insufficient-scope/metadata discovery/token-verifier failure/secret-redaction E2E。**"""
if old_next in text:
    text = text.replace(old_next, new_tail)
elif '## v0.6.20 已完成' not in text:
    raise SystemExit('CURRENT_HANDOFF next-task marker missing')
handoff.write_text(text, encoding='utf-8')

changelog = ROOT / 'CHANGELOG.md'
text = changelog.read_text(encoding='utf-8')
entry = """## 0.6.20 — Real MCP Host
- Added a real official-SDK MCP server over the canonical provider action dispatcher.
- Preserved exact v0.6.18 generated tool schemas through the low-level MCP Server API.
- Added real stdio, in-process and Streamable HTTP MCP client E2E on protocol 2026-07-28 / SDK 2.3.0.
- Added default-deny host authorization, scope-filtered tool discovery and canonical secret-field rejection.
- Hardened Streamable HTTP deployment with exact Host/Origin allowlists and explicit public-bind policy.
- See `CHANGELOG_V0620.md`.

"""
if not text.startswith('## 0.6.20 — Real MCP Host'):
    text = entry + text
changelog.write_text(text, encoding='utf-8')

(ROOT / 'CHANGELOG_V0620.md').write_text("""# CBCC v0.6.20 — Real MCP Host

## Goal
Expose the v0.6.18 canonical MCP tool descriptors through a real MCP server without creating a second provider runtime, schema authority or async completion store.

## Protocol and SDK
- Protocol baseline: MCP `2026-07-28`.
- Official Python SDK major: v2; release verification used `mcp 2.3.0`.
- Low-level `Server` is used so canonical `inputSchema` is preserved exactly.
- SDK owns `server/discover`, protocol negotiation and compatibility fallback.

## Runtime
- `runtime/cbcc/mcp_host.py`: thin MCP mapping + authorization injection + Dispatcher call.
- `runtime/cbcc/mcp_host_cli.py`: composition root for stdio / Streamable HTTP.
- `requirements-mcp.txt`: optional MCP hosting dependency (`mcp[cli]>=2.3,<3`).
- ProviderExecutionSurface / Bridge / Executor are not imported by the transport adapter.

## Authorization and transport security
- Default ActionAuthorization is DENY.
- `CBCC_MCP_AUTH_MODULE` contains only a module name; host code verifies request context and returns principal/scopes.
- HTTP headers and MCP `_meta` are untrusted inputs, never identity by themselves.
- Streamable HTTP retains DNS-rebinding protection; CLI uses exact-port loopback allowlists and requires explicit policy for public binds.
- `:*` wildcard-port patterns are rejected at the CLI boundary.

## Long-running operations
- Canonical PENDING remains a successful MCP tool response with structured status/resume metadata.
- status/resume reuse the same stable operation ID and existing bridge/executor/result state.
- No MCP-specific async database or completion authority is introduced.

## Validation
- v0.6.13–v0.6.20 targeted continuity and transport-security suite: 61 passed.
- Full regression is compared with v0.6.19 main by failing pytest node-id set; release requires `NEW_FAILURE_COUNT=0`.
""", encoding='utf-8')
