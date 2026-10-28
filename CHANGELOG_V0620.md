# CBCC v0.6.20 — Real MCP Host

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
