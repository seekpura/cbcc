# CBCC v0.6.14 — Provider Executor Lifecycle

## Real execution gap closed
v0.6.13 defined transport integrity, but CBCC still stopped before an adapter actually uploaded/refreshed assets, submitted a provider job, resumed polling, downloaded output bytes and wrote an ingestible production receipt.

## Implementation
1. Added a credential-free `ProviderExecutor` protocol. Concrete adapters own credentials/network/vendor SDKs; CBCC owns lifecycle, lineage, idempotency, resume state and receipt integrity.
2. Added persistent `executor_state.json` with resumable `PREPARE → TRANSMISSION → SUBMIT → POLL/RESUME → COLLECT → RESOLVE → COMPLETE` semantics.
3. Local `PACKAGE_RELATIVE_PATH` product masters are hash-checked before adapter upload. Expired provider handles can be refreshed while preserving content SHA256 and predecessor/generation lineage.
4. Submission consumes deterministic request hash/idempotency semantics. A resumed execution reuses the accepted external job instead of submitting a duplicate.
5. Provider output references are resolved to actual bytes, SHA256-checked, materialized under the job, and returned through the existing production receipt contract.
6. Portable `source_binding_hash` remains immutable across provider-handle rebinding. Executor-side handle state receives a separate `provider_execution_source_binding_hash`.
7. Executor transmission is a child of the v0.6.13 portable transmission. Ingest validates parent transmission linkage, executor request hash and the external acknowledgement binding.
8. Added `ReferenceMemoryExecutor` as an executable reference adapter with deterministic upload/refresh, idempotent submit, poll/resume, collect and resolve behavior.
9. Existing `ingest_provider_job_results()` remains the final review authority; executor output is not a parallel completion path.

## Verification target
- v0.6.13 transport tests remain green.
- v0.6.14 targeted lifecycle tests cover upload, refresh lineage, idempotent resume, output-byte resolution, receipt generation, batch execution and existing ingest compatibility.
- Full regression is compared against current `main`; only newly introduced failures block release.

- Release regression rule: full-suite failure node IDs are compared with current main; v0.6.14 ships only when `NEW_FAILURE_COUNT=0`.
