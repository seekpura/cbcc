# CBCC v0.6.21 — MCP Protocol Core + Streamable HTTP

## Goal
Reuse one MCP protocol authority across stdio and HTTP, then implement the current MCP `2026-07-28` Streamable HTTP binding without reintroducing legacy session/SSE architecture or duplicating Provider runtime.

## Shared protocol core
- Extracted `runtime/cbcc/mcp_protocol.py` as the single authority for MCP lifecycle, modern metadata validation, `server/discover`, `tools/list`, `tools/call`, authorization-scoped tool visibility and canonical dispatcher execution.
- `runtime/cbcc/mcp_stdio.py` is now a thin newline framing layer over `MCPProtocolProcessor` and preserves the v0.6.20 public API/behavior.
- Both stdio and HTTP consume the same generated MCP tool descriptors and `ProviderActionDispatcher`.

## Streamable HTTP 2026-07-28
- Added `runtime/cbcc/mcp_streamable_http.py` and `runtime/cbcc/mcp_streamable_http_cli.py`.
- The modern server exposes one configurable MCP endpoint, default `/mcp`, and accepts POST only.
- Every request validates `Accept` support for both `application/json` and `text/event-stream`.
- Every modern request validates `MCP-Protocol-Version`, `Mcp-Method`, and `Mcp-Name` where applicable against the JSON-RPC body.
- Header/body failures return HTTP 400 with JSON-RPC `HeaderMismatch` (`-32020`).
- Matching but unsupported protocol versions return HTTP 400 with `UnsupportedProtocolVersion` (`-32022`).
- `Mcp-Name` and `Mcp-Param-*` support the MCP Base64 sentinel encoding.
- Schema-declared `x-mcp-header` tool parameters are mirrored/validated when present; annotations are checked for case-insensitive uniqueness and HTTP token syntax.

## Security
- Origin is validated whenever it is present; an unapproved Origin returns HTTP 403.
- `CBCC_MCP_ALLOWED_ORIGINS` holds the explicit Origin allowlist; absence of Origin remains valid for non-browser MCP clients.
- `CBCC_MCP_HTTP_AUTH_MODULE` contains only a host module name. The host resolver receives the request context and injects `ActionAuthorization` into the shared protocol processor.
- Authorization exceptions fail closed and host exception text is not returned.
- The HTTP transport module does not import/call ProviderExecutionSurface, ProviderExecutorBridge or ProviderExecutor directly.

## Stateless modern transport
- No `Mcp-Session-Id` is created or echoed.
- `Last-Event-ID` is ignored; resumable streams are not implemented.
- GET/DELETE to the modern MCP endpoint return 405.
- Accepted JSON-RPC notifications can return HTTP 202 with an empty body.
- `notifications/cancelled` is rejected on modern Streamable HTTP because request-stream closure is the cancellation signal in the 2026 revision.

## Responses
- Normal request responses use `application/json`.
- The binding also supports request-scoped SSE responses through an injectable response selector; SSE carries only request-related output and terminates after the final JSON-RPC response.
- SSE responses send `X-Accel-Buffering: no` and do not create a standalone GET stream or hidden session.

## Validation
- Real localhost HTTP tests cover JSON success, required headers, version/method/name mismatch, unsupported version, missing client capabilities, Origin allow/deny, Accept negotiation, GET/DELETE rejection, ignored legacy session headers, method-not-found HTTP mapping, 202 notification behavior, stdio-only cancellation rejection, Base64 names, `Mcp-Param-*`, request-scoped SSE, authorization redaction and no direct provider-runtime imports.
- v0.6.13–v0.6.21 targeted provider/action/Plugin/MCP continuity: 81 passed.
- Release requires full pytest failed-node-id comparison against v0.6.20 main with `NEW_FAILURE_COUNT=0`.

## Next
Make CBCC a real installable host distribution. Add Python project metadata, package discovery and stable console entrypoints for the main CBCC CLI, Plugin/OpenAPI HTTP host, MCP stdio host and MCP Streamable HTTP host. Verify wheel/sdist content and run clean-venv installation/E2E so users no longer need repository-relative `PYTHONPATH` execution.
