# CBCC v0.6.13 — Provider Transport Integrity

## Real breaks fixed
1. Provider asset handles previously had no executable lifecycle semantics beyond a declared handle + SHA256.
2. Remote receipt URIs could carry a declared hash without CBCC observing and hashing the returned bytes.
3. `EXTERNAL_ADAPTER` existed as a registry label without a normalized request/idempotency/external-job acknowledgement contract.

## Implementation
- `runtime/cbcc/provider_transport.py` owns handle lifecycle, adapter mapping/transmission binding, remote artifact verification and recovery.
- Structured handles may declare provider, state, issued/verified/expiry time, predecessor and generation. Refreshes rotate handles while preserving source content SHA256 lineage. Legacy string handles remain compatible but explicitly declared-only.
- External adapter transmissions map the portable job contract to a vendor-neutral request envelope and bind it with request hash + idempotency key + transmission ID. This is a transport contract, not a claim that an API call occurred.
- Real provider-job ingestion requires remote output bytes to be resolved and SHA256-verified. The core runtime accepts an injected resolver instead of embedding credentials or a network client.
- Remote recovery writes only verified bytes and rechecks the local recovered copy.

## Boundary
Provider-specific credentials, upload APIs, polling clients and download authentication remain adapter/executor responsibilities. v0.6.13 defines the executable transport contract they must satisfy.

## Compatibility
- Materialized provider results keep legacy `fixture://` receipt semantics for deterministic local/test handoff. Strict byte resolution remains mandatory for real remote schemes (`http(s)`, `s3`, `gs`, Azure and provider URIs), preserving v0.6.13 remote-integrity guarantees without regressing the existing FILE_HANDOFF lifecycle.
