# CBCC v0.6.15 — Provider Adapter Registry / Executor Bridge

## Gap closed
v0.6.14 provided an executable ProviderExecutor lifecycle, but the host still needed to manually supply executor instances and had no contract for adapter discovery, capability selection, retry/backoff, rate limiting, cancellation or reconciliation.

## Implementation
1. Added `ProviderAdapterRegistry` with credential-free adapter declarations and discovery by provider, production mode, capabilities and operations.
2. Adapter selection is deterministic: lowest priority value, then adapter ID. Explicit adapter selection is capability-checked rather than blindly trusted.
3. Added `ProviderExecutorBridge` as the host orchestration layer over the existing v0.6.14 executor. The single execution chain remains `Provider Job → Adapter Registry → Executor Bridge → ProviderExecutor → Production Receipt → Ingest`.
4. Added standardized transient/permanent provider errors and bounded retry policy with exponential backoff.
5. `ProviderRateLimitError` supports provider-supplied `retry_after_seconds`; bridge state records the retry schedule without altering executor lineage.
6. Added durable `bridge_state.json` for attempt history, selected adapter, policy, cancel request and reconciliation evidence. Runtime context, callbacks, API keys and credentials are never persisted.
7. Added cancel semantics for pre-submit, unsupported, pending, completed-too-late and confirmed-cancelled cases.
8. Added reconciliation semantics comparing persisted executor state with provider/native reconciliation or poll fallback.
9. Added `HostCallbackExecutor` and `EPV_HOST_CALLBACK_V1`: a real host integration profile where SDK/HTTP/auth remain injected by the host at runtime rather than stored in CBCC.
10. Reference memory adapter remains opt-in and is not registered as a production default.
11. `provider_contract()` now exposes both the v0.6.14 executor contract and v0.6.15 bridge contract for external-adapter routes.
12. Provider continuity tests from v0.6.13 through v0.6.15 pass together, including existing ingest compatibility.

## Boundary
v0.6.15 does not add a provider-specific credential store or network SDK. The next host surface must invoke the bridge without serializing secrets into project files, command history or adapter declarations.
