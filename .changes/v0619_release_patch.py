from pathlib import Path

ROOT = Path('.')

version = ROOT / 'VERSION'
version.write_text('0.6.19\n', encoding='utf-8')

skill = ROOT / 'SKILL.md'
text = skill.read_text(encoding='utf-8')
text = text.replace('version: 0.6.18-transport-descriptor-parity', 'version: 0.6.19-plugin-http-host')
section = """## v0.6.19 Plugin/OpenAPI HTTP Host
- 新增真正可启动的 `PluginHTTPApplication` / WSGI host；HTTP action route 全部来自 v0.6.18 generated OpenAPI descriptor，不手写第二套路由表。
- 唯一调用链保持 `HTTP request → operationId → PluginActionTransportAdapter → ProviderActionDispatcher`；`plugin_http.py` 不 import `ProviderExecutionSurface / ProviderExecutorBridge / ProviderExecutor`。
- 提供 `/health`、`/openapi.json`、`/actions.json`（含 schema aliases）；checked-in descriptor bundle 仍保持 descriptor-only，因此其 `plugin_http_server_included=false` 不等于仓库没有 host runtime。
- POST action 强制 `application/json`、`Content-Length`、JSON object 与可配置 request-size limit；transport error 使用稳定 HTTP/code 映射。
- `ActionAuthorization` 由宿主 hook 注入；`CBCC_ACTION_AUTH_MODULE` 只指定 auth module 名，不把 API key/token/credential 放进 action body 或 CLI 参数。
- 默认授权 DENY；authorization resolver 异常按 403 fail-closed 且不回显宿主异常文本。
- canonical `PENDING` 映射 HTTP 202，并返回 `Retry-After`、`X-CBCC-Operation-Id`、`X-CBCC-Operation-State`；status/resume 继续复用 v0.6.17 operation/state lineage。
- 新增 `cbcc.plugin_http_cli` composition root，可用标准库 `wsgiref.simple_server` 启动 reference host；生产宿主也可直接挂载标准 WSGI application。

"""
marker = '## v0.6.18 Transport Descriptor Parity\n'
if section not in text:
    if marker not in text:
        raise SystemExit('SKILL v0.6.18 marker missing')
    text = text.replace(marker, section + marker)
skill.write_text(text, encoding='utf-8')

handoff = ROOT / 'CURRENT_HANDOFF.md'
text = handoff.read_text(encoding='utf-8')
text = text.replace('# CBCC v0.6.18 CURRENT HANDOFF', '# CBCC v0.6.19 CURRENT HANDOFF')
text = text.replace('当前版本：`0.6.18-transport-descriptor-parity`。', '当前版本：`0.6.19-plugin-http-host`。')
old_next = """## 下一步唯一主任务
**在 v0.6.18 descriptors 之上实现一个真正可启动但仍然薄的 transport host：优先实现 Plugin/OpenAPI HTTP host（与当前 ChatGPT/Plugin 使用面最接近），只负责 HTTP request → operationId → `PluginActionTransportAdapter` → `ProviderActionDispatcher`，并把 `ActionAuthorization` 作为宿主注入而不是请求体 credential。补 health/schema endpoints、request size/JSON validation、authorization hook、pending/resume/status HTTP semantics 与 transport-level error mapping；禁止 transport host 直接调用 ProviderExecutionSurface / Bridge / Executor。MCP server 后续复用同一 canonical descriptors/dispatcher。**"""
new_tail = """## v0.6.19 已完成
1. 新增真正可启动的 Plugin/OpenAPI WSGI host；action path 全部从 v0.6.18 generated OpenAPI descriptor 派生。
2. HTTP host 唯一调用链为 request → operationId → `PluginActionTransportAdapter` → `ProviderActionDispatcher`；transport module 不直接 import/call ProviderExecutionSurface、Bridge 或 Executor。
3. `/health`、`/openapi.json`、`/actions.json` 可直接读取运行状态与 canonical schema；descriptor bundle 自身仍保持 descriptor-only 语义。
4. action POST 强制 JSON media type、Content-Length、JSON object 与 request-size 上限；400/403/404/405/409/411/413/415/422/500 由 transport 统一映射。
5. `CBCC_ACTION_AUTH_MODULE` 只指定宿主 auth module；ActionAuthorization 由 host hook 瞬时注入，不进入 action payload / project state / provider runtime state。
6. 默认 DENY；auth resolver 自身异常按 403 fail-closed，且宿主异常文本不返回客户端。
7. PENDING → HTTP 202 + Retry-After + operation headers；status/resume 继续使用 v0.6.17 稳定 operation ID 与现有 provider persisted state，没有第二套 async DB。
8. 新增 `cbcc.plugin_http_cli` composition root；默认 reference server 仅使用 Python 标准库，WSGI application 可被其他宿主 server 挂载。
9. v0.6.13–v0.6.19 provider continuity + transport HTTP 定向联测：48 passed。
10. 全量回归与 v0.6.18 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`；HTTP transport 发布保持 canonical descriptor/dispatcher authority。

## 下一步唯一主任务
**在 v0.6.19 HTTP host 完成后，为 v0.6.18 已生成的 MCP tool descriptors 实现同样薄的真实 MCP transport host。实施前先核对当前 MCP 官方 transport/SDK 规范，再选择宿主最合适的 stdio / Streamable HTTP 入口；无论 transport 形式如何，都必须复用 canonical `mcp_tools.json` / Action Catalog / `ProviderActionDispatcher` / `ActionAuthorization`，不得复制 ProviderExecutionSurface、Bridge、Executor 或另建 completion/state authority。补 MCP initialize/list-tools/call-tool、authorization 注入、pending/status/resume 语义、schema parity 与 transport-level error mapping。**"""
if old_next in text:
    text = text.replace(old_next, new_tail)
elif '## v0.6.19 已完成' not in text:
    raise SystemExit('CURRENT_HANDOFF next-task marker missing')
handoff.write_text(text, encoding='utf-8')

changelog = ROOT / 'CHANGELOG.md'
text = changelog.read_text(encoding='utf-8')
entry = """## 0.6.19 — Plugin/OpenAPI HTTP Host
- Added a real startable WSGI Plugin/OpenAPI host over generated action routes.
- Kept the only runtime chain through PluginActionTransportAdapter → ProviderActionDispatcher.
- Added health/schema endpoints, JSON/media-type/request-size validation and stable transport-level HTTP mapping.
- Added host-injected default-deny ActionAuthorization with fail-closed redacted resolver failures.
- Added HTTP 202 pending semantics with operation/resume headers and a standard-library startup entrypoint.
- See `CHANGELOG_V0619.md`.

"""
if not text.startswith('## 0.6.19 — Plugin/OpenAPI HTTP Host'):
    text = entry + text
changelog.write_text(text, encoding='utf-8')

(ROOT / 'CHANGELOG_V0619.md').write_text("""# CBCC v0.6.19 — Plugin/OpenAPI HTTP Host

## Goal
Turn the v0.6.18 generated Plugin/OpenAPI descriptor into a real, startable transport without creating another provider runtime or another completion/state authority.

## Runtime
- `runtime/cbcc/plugin_http.py` provides a standard WSGI application and reference `wsgiref.simple_server` host.
- `runtime/cbcc/plugin_http_cli.py` is the composition root that wires the existing ProviderExecutionSurface into ProviderActionDispatcher and then into the thin HTTP transport.
- The transport runtime itself only owns HTTP parsing, route/operation mapping, authorization injection, response/error mapping and request limits.

## HTTP contract
- GET `/health` / `/healthz`.
- GET `/openapi.json` or `/schema/openapi.json`.
- GET `/actions.json` or `/schema/actions.json`.
- POST action routes are derived from the generated OpenAPI descriptor.
- Canonical SUCCEEDED/PENDING/DENIED/INVALID_INPUT/HOLD/FAILED statuses map to transport-level HTTP codes.
- PENDING returns 202 plus Retry-After and stable operation headers.

## Authorization and secrets
- Default authorization is DENY.
- `CBCC_ACTION_AUTH_MODULE` contains only the module name; the module returns ActionAuthorization from host-owned request context.
- Credential-bearing action body fields remain forbidden by the canonical dispatcher.
- Authorization resolver failures are fail-closed and do not echo host exception text.

## Validation
- v0.6.13–v0.6.19 targeted provider/action/transport continuity: 48 passed.
- Full regression is compared against v0.6.18 main by failing pytest node-id set; release requires `NEW_FAILURE_COUNT=0`.
""", encoding='utf-8')
