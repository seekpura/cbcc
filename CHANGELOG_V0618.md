# CBCC v0.6.18 — Transport Descriptor Parity

## Gap closed
v0.6.17 established one canonical provider action catalog and dispatcher, but external hosts still needed machine-consumable MCP and Plugin/OpenAPI descriptors. Hand-authoring those schemas would create drift and eventually split authorization or credential boundaries across transports.

## Implementation
1. Added `runtime/cbcc/action_transports.py` as the transport descriptor generator over the v0.6.17 canonical action catalog.
2. Added generated MCP-style tool descriptors for all six canonical provider actions.
3. Added generated OpenAPI 3.1 Plugin/Actions descriptor for the same six actions, using same-origin relative server `/` by default.
4. MCP and Plugin input schemas are copied directly from the canonical action input schema; transport descriptors do not define an independent payload model.
5. Added parity verification for action count, tool/operation names, exact input schema equality, permission scope equality, authorization source, and credential-like field lint.
6. Every action records canonical/MCP/Plugin schema hashes; release requires all three hashes to match.
7. Added checked-in generated artifacts:
   - `transport/mcp_tools.json`
   - `transport/plugin_openapi.json`
   - `transport/descriptor_manifest.json`
8. The checked-in descriptor manifest records `mcp_server_included=false` and `plugin_http_server_included=false`; descriptor generation does not pretend that a network server exists.
9. Added `PluginActionTransportAdapter`, a thin in-process operationId adapter whose only execution dependency is `ProviderActionDispatcher`.
10. Plugin authorization remains out-of-band as `ActionAuthorization`; no credential-bearing request schema is generated.
11. Deliberate schema/scope/secret drift tests prove parity verification fails closed.
12. Provider continuity tests from v0.6.13 through v0.6.18 pass together.

## Boundary
v0.6.18 makes the canonical action contract transport-consumable without adding a second runtime. A future concrete HTTP/MCP host must load these descriptors and forward calls to the existing dispatcher rather than reimplementing provider execution.

- Release regression rule: compare full-suite failure node IDs with current main and ship only when `NEW_FAILURE_COUNT=0`.
