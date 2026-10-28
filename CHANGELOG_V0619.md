# CBCC v0.6.19 — Plugin/OpenAPI HTTP Host

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
