# CBCC v0.6.16 — Provider Host Execution Surface

## Gap closed
v0.6.15 made provider adapters discoverable and executable through a shared Bridge, but operators and host harnesses still lacked a stable operational surface. The only existing CLI action was `provider-ingest`, so real execution/cancel/reconcile still required direct Python calls.

## Implementation
1. Added `ProviderExecutionSurface` as the programmatic host surface over the existing Adapter Registry and Executor Bridge.
2. Added host operations: adapter discovery, provider execution, cancellation and reconciliation. No alternate production runtime or completion path was introduced.
3. Added CLI commands:
   - `adapter-list`
   - `provider-execute`
   - `provider-cancel`
   - `provider-reconcile`
4. CLI deliberately exposes no API-key/token/secret arguments. Runtime credentials remain host-owned.
5. Added `CBCC_PROVIDER_HOST_MODULE`. Its value is a Python module name, not credential material. The host module may register adapters and return ephemeral runtime context through `create_runtime_context(...)`.
6. Runtime context (callbacks, SDK clients, auth objects, API keys) is resolved lazily and is never serialized into project artifacts, bridge state, executor state or CLI output.
7. `provider-execute` reuses `Adapter Registry → Executor Bridge → ProviderExecutor → Production Receipt → existing ingest`; when every materialized result is present, the surface runs the existing ingest authority and updates the ProjectState `PRODUCTION` gate.
8. Automatic ingest now requires a complete result set for every row in `PROVIDER_JOB_INDEX`; partial selected execution cannot accidentally mark the project complete.
9. Cancel/reconcile CLI operations reuse the same persisted external job ID and existing executor/bridge lineage.
10. Host-surface tests verify that secret values do not persist to `bridge_state.json`, `executor_state.json`, `result.json`, `production_run.json` or ProjectState.
11. Provider continuity tests from v0.6.13 through v0.6.16 pass together.

## Security boundary
- Secret CLI flags are unsupported by design.
- Registry declarations remain credential-free.
- Environment configuration points only to a host module; credential acquisition remains inside the host/SDK/keyring/credential-chain implementation.
- CBCC records execution lineage and integrity evidence, not credential material.

- Release regression rule: compare full-suite failure node IDs with current main and ship only when `NEW_FAILURE_COUNT=0`.
