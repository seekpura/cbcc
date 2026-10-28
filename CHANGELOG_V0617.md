# CBCC v0.6.17 — Host Action / MCP / Plugin Mapping

## Gap closed
v0.6.16 exposed a secure ProviderExecutionSurface to Python and CLI hosts, but the repository had no MCP server, Plugin action runtime, or canonical host action schema. Building a second provider runtime for those transports would have duplicated execution authority.

## Implementation
1. Added a host-neutral canonical action catalog in `runtime/cbcc/host_actions.py`.
2. Added six canonical action IDs:
   - `cbcc.provider.adapters.list`
   - `cbcc.provider.execute`
   - `cbcc.provider.status`
   - `cbcc.provider.resume`
   - `cbcc.provider.cancel`
   - `cbcc.provider.reconcile`
3. Added explicit authorization scopes. Default authorization is deny; every action requires its declared scope, and mutating actions never inherit read authority.
4. Added `ProviderActionDispatcher`. It maps actions directly to the existing `ProviderExecutionSurface`; it never creates executors, credentials, provider clients, production receipts, or a second completion state.
5. Added action-friendly long-running semantics without a new async job database. Execute returns a stable non-secret operation ID and scope. Status reads existing provider state; resume re-enters the same persisted Bridge/Executor lifecycle and therefore reuses the accepted external job/idempotency lineage.
6. Added operation-scope validation so an operation ID cannot be replayed against a different asset scope.
7. Added recursive credential-field rejection before dispatch. Exact and namespaced fields such as `api_key`, `provider_api_key`, `oauth_token`, `clientSecret`, password/credential/auth/private-key fields are rejected from action payloads.
8. Runtime context still comes only from the v0.6.16 ProviderExecutionSurface resolver; action JSON never carries credentials or SDK clients.
9. Added declarative thin transport mappings for MCP tool names and Plugin operation IDs. The manifest explicitly does not claim that an MCP or Plugin server exists.
10. Action status is read-only over existing `bridge_state.json`, `executor_state.json`, `result.json`, and `production_run.json`.
11. End-to-end tests prove pending → status → resume reaches COMPLETE without duplicate provider submit, then existing ingest/ProjectState remains final completion authority.
12. Provider continuity tests from v0.6.13 through v0.6.17 pass together.

## Boundary
v0.6.17 defines the canonical action contract and dispatch runtime. A concrete MCP server or ChatGPT Plugin transport should be a thin schema/transport wrapper over this contract, not a second provider execution implementation.
