from pathlib import Path

skill = Path('SKILL.md')
text = skill.read_text(encoding='utf-8')
text = text.replace('version: 0.6.20-mcp-stdio-host', 'version: 0.6.21-mcp-streamable-http')
section = """## v0.6.21 MCP Protocol Core + Streamable HTTP
- 抽出 `runtime/cbcc/mcp_protocol.py` 作为唯一 MCP message semantics 权威；stdio 与 HTTP 共用同一 `MCPProtocolProcessor`，不复制 `server/discover / tools/list / tools/call`。
- `mcp_stdio.py` 退化为 newline framing + compatibility API；v0.6.20 行为回归保持通过。
- 新增 `runtime/cbcc/mcp_streamable_http.py` + `python -m cbcc.mcp_streamable_http_cli`，默认单 `/mcp` endpoint、POST-only，符合当前 MCP `2026-07-28` Streamable HTTP 形态。
- 每个 POST 强制 Accept 同时声明 `application/json` 与 `text/event-stream`，并校验 `MCP-Protocol-Version / Mcp-Method / Mcp-Name` 与 JSON-RPC body 一致；mismatch 返回 HTTP 400 + `-32020 HeaderMismatch`。
- matching-but-unsupported protocol version 返回 HTTP 400 + `-32022 UnsupportedProtocolVersion`；`-32602 Invalid params` 等现代请求校验错误映射为 HTTP 400，未知 method 映射 404。
- `Mcp-Name` / `Mcp-Param-*` 支持 MCP Base64 sentinel 编码；schema `x-mcp-header` 参数按 case-insensitive uniqueness / HTTP token / primitive type / body value 做边界校验。
- Origin 存在时必须命中 `CBCC_MCP_ALLOWED_ORIGINS`；非法 Origin 403。HTTP auth 通过 `CBCC_MCP_HTTP_AUTH_MODULE` 注入 `ActionAuthorization`，默认 DENY，resolver 异常 fail closed 且不泄漏宿主异常文本。
- modern transport 不创建或回显 `Mcp-Session-Id`，忽略 `Last-Event-ID`，GET/DELETE 返回 405；`notifications/cancelled` 不走 HTTP message，request-scoped SSE 连接关闭即取消。
- 支持 application/json response，也支持注入 selector 后的 request-scoped SSE final response；SSE 带 `X-Accel-Buffering: no`，不建立 standalone GET stream 或隐藏 session。
- MCP HTTP transport 不直接 import/call ProviderExecutionSurface / Bridge / Executor；composition root 才组装既有 Surface → Dispatcher。
- v0.6.13–v0.6.21 provider/action/Plugin/MCP continuity 定向联测：81 passed。
- 全量回归与 v0.6.20 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`。

"""
marker = '## v0.6.20 MCP stdio Host\n'
if '## v0.6.21 MCP Protocol Core + Streamable HTTP' not in text:
    if marker not in text:
        raise SystemExit('SKILL v0.6.20 marker missing')
    text = text.replace(marker, section + marker, 1)
skill.write_text(text, encoding='utf-8')

handoff = Path('CURRENT_HANDOFF.md')
text = handoff.read_text(encoding='utf-8')
text = text.replace('# CBCC v0.6.20 CURRENT HANDOFF', '# CBCC v0.6.21 CURRENT HANDOFF')
text = text.replace('当前版本：`0.6.20-mcp-stdio-host`。', '当前版本：`0.6.21-mcp-streamable-http`。')
old_next = """## 下一步唯一主任务
**在 v0.6.20 stdio host 的 MCP message semantics 之上实现当前 `2026-07-28` Streamable HTTP binding，但禁止复制一套 `server/discover / tools/list / tools/call`。先抽取/复用 transport-neutral MCP protocol processor，再实现单 `/mcp` HTTP POST binding：校验 Origin、`MCP-Protocol-Version`、`Mcp-Method`、`Mcp-Name` 与 body metadata 一致性，支持 JSON response 与必要的 request-scoped SSE 扩展边界；现代路径不得重新引入旧 HTTP+SSE GET endpoint、Mcp-Session-Id 或隐藏 session state。授权必须由 HTTP host 注入 `ActionAuthorization`，Provider runtime / completion authority 继续只在 Dispatcher 后方。**"""
new_tail = """## v0.6.21 已完成
1. MCP lifecycle/tool semantics 已抽为独立 `MCPProtocolProcessor`；stdio / Streamable HTTP 共用一套 protocol core。
2. stdio binding 保留 v0.6.20 public API 并继续通过 legacy + modern 全套协议回归。
3. 新增 current `2026-07-28` Streamable HTTP binding：单 MCP endpoint、POST-only、每 message 一个 HTTP request。
4. 强制 `Accept: application/json, text/event-stream`，并验证 JSON content type / Content-Length / request-size / UTF-8 JSON object。
5. `MCP-Protocol-Version / Mcp-Method / Mcp-Name / Mcp-Param-*` 与 body 不一致统一 HTTP 400 + `-32020 HeaderMismatch`；unsupported protocol 使用 `-32022`。
6. `Mcp-Name` 与 custom param headers 支持 Base64 sentinel；`x-mcp-header` 做 deterministic schema/binding 校验。
7. Origin 存在时必须通过 allowlist；HTTP authorization 由 host module 注入，默认 DENY，异常 fail closed 且 redacted。
8. modern HTTP 完全 sessionless：不 mint/echo `Mcp-Session-Id`，GET/DELETE 405，`Last-Event-ID` 不参与 resume。
9. normal response 支持 application/json；request-scoped SSE 可按宿主 selector 启用，SSE 只承载该 request 相关输出并在 final response 后结束。
10. transport 不直接碰 Provider runtime；HTTP 与 stdio 都只进入 canonical Dispatcher 后方的既有执行/完成权威。
11. v0.6.13–v0.6.21 provider/action/Plugin/MCP continuity 定向联测：81 passed。
12. 全量回归与 v0.6.20 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`。

## 下一步唯一主任务
**把 CBCC 从“仓库内可运行”升级为真正可安装的 Host Distribution。当前根 `pyproject.toml` 只有 pytest 配置，没有 `[project]`、package discovery 或 console scripts。v0.6.22 必须建立标准 Python packaging：把 `runtime/cbcc` 作为正式 package 纳入 wheel/sdist，提供稳定 console entrypoints（主 CBCC CLI、Plugin/OpenAPI HTTP、MCP stdio、MCP Streamable HTTP），明确 Python/dependency/包内静态资源边界，并在 clean venv 中完成 `pip install` → descriptor import → CLI help → stdio MCP discover → HTTP health/request E2E。禁止通过 repository-relative `PYTHONPATH` 假装安装成功，禁止把测试/临时 `.changes`/宿主凭证打进发行包。**"""
if old_next in text:
    text = text.replace(old_next, new_tail)
elif '## v0.6.21 已完成' not in text:
    raise SystemExit('CURRENT_HANDOFF v0.6.20 next task missing')
handoff.write_text(text, encoding='utf-8')

changelog = Path('CHANGELOG.md')
text = changelog.read_text(encoding='utf-8')
entry = """## 0.6.21 — MCP Protocol Core + Streamable HTTP
- Extracted one transport-neutral MCPProtocolProcessor shared by stdio and HTTP.
- Added current MCP 2026-07-28 single-endpoint POST Streamable HTTP binding with strict Origin, Accept and mirrored-header/body validation.
- Added `HeaderMismatch`/unsupported-version HTTP mapping, Base64 mirrored headers and schema-driven `Mcp-Param-*` validation.
- Kept modern HTTP sessionless and added request-scoped SSE response support without standalone GET streams or resumable session state.
- Added live localhost HTTP regression coverage while preserving canonical dispatcher/provider authority.
- See `CHANGELOG_V0621.md`.

"""
if not text.startswith('## 0.6.21 — MCP Protocol Core + Streamable HTTP'):
    text = entry + text
changelog.write_text(text, encoding='utf-8')
