# CBCC v0.6.19 — Plugin/OpenAPI HTTP Host

## Summary
v0.6.19 turns the v0.6.18 generated Plugin/OpenAPI descriptor into a real, startable thin HTTP transport while preserving the existing canonical action and provider execution authorities.

## Completed
1. Added `runtime/cbcc/plugin_http.py`, a WSGI transport host over `PluginActionTransportAdapter -> ProviderActionDispatcher`.
2. Added `runtime/cbcc/plugin_http_cli.py`; the host starts with `python -m cbcc.plugin_http_cli` and exposes bind/port/request-size/retry/server-url transport options only.
3. Added health and schema surfaces: `/health` + `/healthz`, `/openapi.json` + `/schema/openapi.json`, and `/actions.json` + `/schema/actions.json`.
4. Added transport validation for JSON content type, required content length, request byte limit, UTF-8 JSON parsing, top-level object shape, method routing and action-route mapping.
5. Added host-injected authorization through `CBCC_ACTION_AUTH_MODULE`; the module exports `resolve_action_authorization(...)`. Authorization remains outside the action body and defaults to DENY.
6. Authorization resolver failures fail closed with HTTP 403 and a fixed error code; host exception detail is not returned to the client.
7. Added transport status mapping including HTTP 202 for pending provider operations, `Retry-After`, `X-CBCC-Operation-Id`, and `X-CBCC-Operation-State` headers.
8. Pending/status/resume continue to use the canonical v0.6.17 action model and existing provider state. No second async job database or completion authority is introduced.
9. The transport module does not import or call ProviderExecutionSurface, ProviderExecutorBridge or ProviderExecutor directly.
10. Added live HTTP/WSGI tests covering health/schema, default deny, authorization allow, malformed/oversized payloads, pending semantics, operation headers and fail-closed authorization.

## Runtime authority
`HTTP request -> generated OpenAPI route -> PluginActionTransportAdapter -> ProviderActionDispatcher -> existing ProviderExecutionSurface chain`

## Security boundary
- Provider/action credentials are never accepted as canonical JSON fields.
- Authorization may inspect host HTTP headers, but those values are not written into project state by the transport.
- Authorization resolver exceptions are redacted from the client response.
- CLI options do not contain API-key/token/secret/password credential parameters.

## Next
Implement a real MCP transport host from the same v0.6.18 canonical MCP descriptors and `ProviderActionDispatcher`, keeping the Plugin and MCP transports schema-equivalent and provider-runtime-neutral.
