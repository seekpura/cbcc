# CBCC v0.6.20 — MCP stdio Host

## Goal
Provide a real MCP transport over the canonical CBCC action layer without creating another provider runtime, and align with the current MCP 2026-07-28 protocol while retaining the necessary 2025-era compatibility path.

## Current protocol alignment
- Modern MCP revision: `2026-07-28`.
- Modern lifecycle: per-request `_meta` + `server/discover`; there is no mandatory initialize/initialized session handshake.
- Legacy compatibility revision: `2025-11-25`, using `initialize` + `notifications/initialized`.
- stdio framing is UTF-8 newline-delimited JSON-RPC 2.0; stdout is reserved for protocol messages.

## Runtime
- Added `runtime/cbcc/mcp_stdio.py`.
- Added `runtime/cbcc/mcp_stdio_cli.py`; launch with `python -m cbcc.mcp_stdio_cli`.
- Tool definitions are consumed from `mcp_tool_descriptors()` generated from the v0.6.17 canonical Action Catalog; no second tool schema is maintained.
- Tool calls map only to `ProviderActionDispatcher`.
- The transport runtime does not import or call ProviderExecutionSurface, ProviderExecutorBridge or ProviderExecutor directly.

## Modern 2026-07-28 behavior
- Implements `server/discover` with tools capability and server identity.
- Requires modern per-request protocol metadata and client capabilities.
- Implements deterministic, authorization-scoped `tools/list`.
- Implements `tools/call` with structuredContent plus text serialization for compatibility.
- Modern cacheable results include conservative `ttlMs: 0` and `cacheScope: private`.
- Unsupported protocol versions return MCP `UnsupportedProtocolVersionError` code `-32022` with supported versions.

## Legacy behavior
- Implements `initialize` and `notifications/initialized` for the 2025-era path.
- Legacy `tools/list` / `tools/call` reuse the same canonical descriptors, authorization and dispatcher.
- A 2026 modern version sent to the legacy initialize path is explicitly redirected via protocol-version error rather than pretending to initialize a modern session.

## Authorization and secrets
- Default authorization is DENY.
- `CBCC_MCP_AUTH_MODULE` contains only a host module name.
- Host authorization is resolved out-of-band into `ActionAuthorization`; canonical action payload secret-field rejection remains active.
- Authorization resolver exceptions fail closed with a fixed JSON-RPC error and do not echo host exception text.
- `tools/list` hides tools for which the caller lacks the required canonical action scope.

## Validation
- Modern discover, modern tools/list/call, legacy initialize/list/call, unsupported-version handling, default-deny filtering, authorization failure redaction, newline framing, descriptor parity, pending operation output and no-direct-provider-import boundaries are covered.
- v0.6.13–v0.6.20 targeted provider/action/Plugin/MCP continuity: 62 passed.
- Full release regression is compared to v0.6.19 main by failing pytest node-id set; release requires `NEW_FAILURE_COUNT=0`.

## Next
Extract/reuse the MCP message processor as the single protocol authority and add the current `2026-07-28` Streamable HTTP binding on top of it. The HTTP binding must use one `/mcp` endpoint, validate Origin, carry current protocol/method/name headers, preserve canonical authorization, and avoid reintroducing legacy HTTP+SSE/session semantics into the modern path.
