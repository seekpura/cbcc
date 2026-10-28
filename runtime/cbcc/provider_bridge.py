from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol
import json
import time

from .models import stable_hash
from .provider_executor import ProviderExecutor, execute_provider_job_directory

VERSION = '0.6.15-provider-executor-bridge'


class ProviderBridgeError(RuntimeError):
    code = 'PROVIDER_BRIDGE_ERROR'
    retryable = False


class ProviderTransientError(ProviderBridgeError):
    code = 'PROVIDER_TRANSIENT_ERROR'
    retryable = True


class ProviderRateLimitError(ProviderTransientError):
    code = 'PROVIDER_RATE_LIMITED'

    def __init__(self, message: str = 'provider rate limited', *, retry_after_seconds: float | None = None):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


class ProviderPermanentError(ProviderBridgeError):
    code = 'PROVIDER_PERMANENT_ERROR'
    retryable = False


class ProviderCancelledError(ProviderPermanentError):
    code = 'PROVIDER_CANCELLED'


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return {} if default is None else default


def _write_json(path: Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def _now(clock: Callable[[], float]) -> float:
    return float(clock())


@dataclass(frozen=True)
class AdapterDeclaration:
    adapter_id: str
    provider: str
    production_modes: tuple[str, ...]
    capabilities: tuple[str, ...]
    operations: tuple[str, ...] = ('ensure_asset', 'submit', 'poll', 'collect', 'resolve')
    priority: int = 100
    auth_external: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            'version': VERSION,
            'adapter_id': self.adapter_id,
            'provider': self.provider,
            'production_modes': list(self.production_modes),
            'capabilities': list(self.capabilities),
            'operations': list(self.operations),
            'priority': self.priority,
            'auth_external': self.auth_external,
            'metadata': dict(self.metadata),
        }


class AdapterFactory(Protocol):
    def __call__(self, runtime_context: dict[str, Any]) -> ProviderExecutor: ...


@dataclass
class _RegistryEntry:
    declaration: AdapterDeclaration
    factory: AdapterFactory


class ProviderAdapterRegistry:
    """Host-callable provider adapter registry.

    Registry metadata is intentionally credential-free. Secrets/network clients may be supplied only
    in the runtime_context passed to instantiate(); they are never serialized into declarations.
    """

    def __init__(self) -> None:
        self._entries: dict[str, _RegistryEntry] = {}

    def register(self, declaration: AdapterDeclaration, factory: AdapterFactory, *, replace: bool = False) -> None:
        adapter_id = str(declaration.adapter_id)
        if not adapter_id:
            raise ValueError('adapter_id required')
        if adapter_id in self._entries and not replace:
            raise ValueError('adapter already registered: ' + adapter_id)
        if declaration.auth_external is not True:
            raise ValueError('adapter declaration must keep authentication external')
        self._entries[adapter_id] = _RegistryEntry(declaration=declaration, factory=factory)

    def unregister(self, adapter_id: str) -> bool:
        return self._entries.pop(str(adapter_id), None) is not None

    def declarations(self) -> list[dict[str, Any]]:
        rows = [entry.declaration.as_dict() for entry in self._entries.values()]
        return sorted(rows, key=lambda row: (int(row.get('priority') or 100), str(row.get('adapter_id'))))

    def discover(
        self,
        *,
        provider: str | None = None,
        production_mode: str | None = None,
        required_capabilities: list[str] | tuple[str, ...] | None = None,
        required_operations: list[str] | tuple[str, ...] | None = None,
    ) -> list[dict[str, Any]]:
        provider_u = str(provider or '').upper()
        mode_u = str(production_mode or '').upper()
        caps = {str(x).upper() for x in (required_capabilities or [])}
        ops = {str(x) for x in (required_operations or [])}
        matches: list[dict[str, Any]] = []
        for entry in self._entries.values():
            d = entry.declaration
            if provider_u and str(d.provider).upper() != provider_u:
                continue
            modes = {str(x).upper() for x in d.production_modes}
            if mode_u and mode_u not in modes and '*' not in modes:
                continue
            declared_caps = {str(x).upper() for x in d.capabilities}
            if not caps.issubset(declared_caps):
                continue
            declared_ops = set(d.operations)
            if not ops.issubset(declared_ops):
                continue
            matches.append(d.as_dict())
        return sorted(matches, key=lambda row: (int(row.get('priority') or 100), str(row.get('adapter_id'))))

    def resolve(
        self,
        *,
        provider: str,
        production_mode: str,
        required_capabilities: list[str] | tuple[str, ...] | None = None,
        required_operations: list[str] | tuple[str, ...] | None = None,
        adapter_id: str | None = None,
    ) -> dict[str, Any]:
        if adapter_id:
            entry = self._entries.get(str(adapter_id))
            if entry is None:
                return {'status': 'HOLD_ADAPTER_NOT_REGISTERED', 'adapter_id': adapter_id}
            candidates = self.discover(
                provider=provider,
                production_mode=production_mode,
                required_capabilities=required_capabilities,
                required_operations=required_operations,
            )
            selected = next((x for x in candidates if x.get('adapter_id') == adapter_id), None)
            if selected is None:
                return {'status': 'HOLD_ADAPTER_CAPABILITY_MISMATCH', 'adapter_id': adapter_id}
            return {'status': 'READY', 'selected': selected, 'candidate_count': len(candidates)}
        candidates = self.discover(
            provider=provider,
            production_mode=production_mode,
            required_capabilities=required_capabilities,
            required_operations=required_operations,
        )
        if not candidates:
            return {
                'status': 'HOLD_NO_COMPATIBLE_ADAPTER',
                'provider': provider,
                'production_mode': production_mode,
                'required_capabilities': list(required_capabilities or []),
                'required_operations': list(required_operations or []),
            }
        return {'status': 'READY', 'selected': candidates[0], 'candidate_count': len(candidates)}

    def instantiate(self, adapter_id: str, *, runtime_context: dict[str, Any] | None = None) -> ProviderExecutor:
        entry = self._entries.get(str(adapter_id))
        if entry is None:
            raise KeyError('adapter not registered: ' + str(adapter_id))
        context = dict(runtime_context or {})
        executor = entry.factory(context)
        if not isinstance(executor, ProviderExecutor):
            # runtime_checkable Protocol verifies the mandatory v0.6.14 surface.
            raise TypeError('adapter factory did not return ProviderExecutor-compatible instance')
        return executor


def bridge_contract() -> dict[str, Any]:
    return {
        'version': VERSION,
        'single_execution_chain': 'Provider Job → Adapter Registry → Executor Bridge → ProviderExecutor → Production Receipt → Ingest',
        'registry': {
            'credential_storage': 'FORBIDDEN',
            'discovery_keys': ['provider', 'production_mode', 'required_capabilities', 'required_operations'],
            'selection': 'lowest priority value, then adapter_id',
        },
        'bridge_semantics': ['RETRY', 'BACKOFF', 'RATE_LIMIT', 'CANCEL', 'RECONCILE'],
        'credentials_rule': 'Credentials/network clients are injected by the host in runtime_context and are never written to adapter declarations or bridge state.',
    }


@dataclass(frozen=True)
class ExecutionPolicy:
    max_attempts: int = 3
    base_backoff_seconds: float = 1.0
    max_backoff_seconds: float = 30.0
    backoff_multiplier: float = 2.0
    max_polls_per_attempt: int = 8

    def backoff_for(self, attempt_number: int) -> float:
        attempt_number = max(1, int(attempt_number))
        value = self.base_backoff_seconds * (self.backoff_multiplier ** max(0, attempt_number - 1))
        return min(float(self.max_backoff_seconds), float(value))

    def as_dict(self) -> dict[str, Any]:
        return {
            'max_attempts': self.max_attempts,
            'base_backoff_seconds': self.base_backoff_seconds,
            'max_backoff_seconds': self.max_backoff_seconds,
            'backoff_multiplier': self.backoff_multiplier,
            'max_polls_per_attempt': self.max_polls_per_attempt,
        }


class ProviderExecutorBridge:
    def __init__(
        self,
        registry: ProviderAdapterRegistry,
        *,
        sleeper: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.registry = registry
        self.sleeper = sleeper
        self.clock = clock

    def _state_path(self, job_dir: Path) -> Path:
        return Path(job_dir) / 'bridge_state.json'

    def _load_job(self, job_dir: Path) -> dict[str, Any]:
        job = _read_json(Path(job_dir) / 'job.json', {})
        if not job:
            raise ValueError('job.json missing or invalid')
        return job

    def _load_state(self, job_dir: Path, job: dict[str, Any]) -> dict[str, Any]:
        path = self._state_path(job_dir)
        state = _read_json(path, {})
        state.setdefault('version', VERSION)
        state.setdefault('job_id', job.get('job_id'))
        state.setdefault('asset_id', job.get('asset_id'))
        state.setdefault('provider', job.get('provider'))
        state.setdefault('attempts', [])
        state.setdefault('status', 'NEW')
        state.setdefault('created_at_epoch', _now(self.clock))
        return state

    def _save_state(self, job_dir: Path, state: dict[str, Any]) -> None:
        state['updated_at_epoch'] = _now(self.clock)
        _write_json(self._state_path(job_dir), state)

    def _requirements(self, job: dict[str, Any]) -> tuple[list[str], list[str]]:
        caps = ['IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE']
        operations = ['ensure_asset', 'submit', 'poll', 'collect', 'resolve']
        if job.get('source_product_bindings'):
            caps.append('ASSET_HANDLE_LIFECYCLE')
        return caps, operations

    def resolve_adapter(self, job_dir: Path, *, adapter_id: str | None = None) -> dict[str, Any]:
        job = self._load_job(job_dir)
        caps, operations = self._requirements(job)
        return self.registry.resolve(
            provider=str(job.get('provider') or ''),
            production_mode=str(job.get('production_mode') or ''),
            required_capabilities=caps,
            required_operations=operations,
            adapter_id=adapter_id,
        )

    def execute(
        self,
        job_dir: Path,
        *,
        runtime_context: dict[str, Any] | None = None,
        adapter_id: str | None = None,
        policy: ExecutionPolicy | None = None,
    ) -> dict[str, Any]:
        job_dir = Path(job_dir)
        job = self._load_job(job_dir)
        state = self._load_state(job_dir, job)
        if state.get('cancel_requested'):
            return self.cancel(job_dir, runtime_context=runtime_context, adapter_id=adapter_id)
        resolution = self.resolve_adapter(job_dir, adapter_id=adapter_id or state.get('adapter_id'))
        if resolution.get('status') != 'READY':
            state['status'] = resolution.get('status')
            state['resolution'] = resolution
            self._save_state(job_dir, state)
            return {'status': state['status'], 'resolution': resolution, 'state_path': str(self._state_path(job_dir))}

        selected = resolution['selected']
        selected_id = str(selected['adapter_id'])
        state['adapter_id'] = selected_id
        state['adapter_declaration_hash'] = stable_hash(selected)
        policy = policy or ExecutionPolicy()
        state['policy'] = policy.as_dict()
        self._save_state(job_dir, state)
        executor = self.registry.instantiate(selected_id, runtime_context=runtime_context)

        prior_attempts = len(state.get('attempts') or [])
        remaining = max(0, int(policy.max_attempts) - prior_attempts)
        if remaining == 0 and state.get('status') not in {'COMPLETE', 'PENDING'}:
            state['status'] = 'RETRY_EXHAUSTED'
            self._save_state(job_dir, state)
            return {'status': 'RETRY_EXHAUSTED', 'state_path': str(self._state_path(job_dir))}

        for offset in range(remaining):
            attempt_number = prior_attempts + offset + 1
            started = _now(self.clock)
            try:
                outcome = execute_provider_job_directory(job_dir, executor, max_polls=policy.max_polls_per_attempt)
                state['attempts'].append({
                    'attempt': attempt_number,
                    'started_at_epoch': started,
                    'finished_at_epoch': _now(self.clock),
                    'status': outcome.get('status'),
                })
                state['status'] = outcome.get('status') or 'UNKNOWN'
                state['last_outcome'] = outcome
                self._save_state(job_dir, state)
                return {**outcome, 'adapter_id': selected_id, 'bridge_state_path': str(self._state_path(job_dir))}
            except ProviderRateLimitError as exc:
                delay = float(exc.retry_after_seconds) if exc.retry_after_seconds is not None else policy.backoff_for(attempt_number)
                error_code = exc.code
                error_message = str(exc)
            except ProviderTransientError as exc:
                delay = policy.backoff_for(attempt_number)
                error_code = exc.code
                error_message = str(exc)
            except Exception as exc:
                state['attempts'].append({
                    'attempt': attempt_number,
                    'started_at_epoch': started,
                    'finished_at_epoch': _now(self.clock),
                    'status': 'FAILED_PERMANENT',
                    'error_code': getattr(exc, 'code', type(exc).__name__),
                    'error': str(exc),
                })
                state['status'] = 'FAILED_PERMANENT'
                self._save_state(job_dir, state)
                return {
                    'status': 'FAILED_PERMANENT',
                    'error_code': getattr(exc, 'code', type(exc).__name__),
                    'error': str(exc),
                    'adapter_id': selected_id,
                    'bridge_state_path': str(self._state_path(job_dir)),
                }

            state['attempts'].append({
                'attempt': attempt_number,
                'started_at_epoch': started,
                'finished_at_epoch': _now(self.clock),
                'status': 'RETRY_SCHEDULED',
                'error_code': error_code,
                'error': error_message,
                'retry_after_seconds': delay,
            })
            state['status'] = 'RETRY_SCHEDULED'
            state['next_retry_after_seconds'] = delay
            self._save_state(job_dir, state)
            if attempt_number >= int(policy.max_attempts):
                break
            self.sleeper(delay)

        state['status'] = 'RETRY_EXHAUSTED'
        self._save_state(job_dir, state)
        return {
            'status': 'RETRY_EXHAUSTED',
            'adapter_id': selected_id,
            'bridge_state_path': str(self._state_path(job_dir)),
            'attempt_count': len(state.get('attempts') or []),
        }

    def request_cancel(self, job_dir: Path, *, reason: str | None = None) -> dict[str, Any]:
        job_dir = Path(job_dir)
        job = self._load_job(job_dir)
        state = self._load_state(job_dir, job)
        state['cancel_requested'] = True
        state['cancel_reason'] = reason
        state['status'] = 'CANCEL_REQUESTED'
        self._save_state(job_dir, state)
        return {'status': 'CANCEL_REQUESTED', 'state_path': str(self._state_path(job_dir))}

    def cancel(
        self,
        job_dir: Path,
        *,
        runtime_context: dict[str, Any] | None = None,
        adapter_id: str | None = None,
    ) -> dict[str, Any]:
        job_dir = Path(job_dir)
        job = self._load_job(job_dir)
        state = self._load_state(job_dir, job)
        resolution = self.resolve_adapter(job_dir, adapter_id=adapter_id or state.get('adapter_id'))
        if resolution.get('status') != 'READY':
            state['status'] = 'CANCEL_HOLD_NO_ADAPTER'
            self._save_state(job_dir, state)
            return {'status': state['status'], 'resolution': resolution}
        selected_id = str(resolution['selected']['adapter_id'])
        executor = self.registry.instantiate(selected_id, runtime_context=runtime_context)
        executor_state = _read_json(job_dir / 'executor_state.json', {})
        external_job_id = ((executor_state.get('adapter_result') or {}).get('external_job_id'))
        if not external_job_id:
            state['status'] = 'CANCELLED_BEFORE_SUBMIT'
            state['cancel_requested'] = False
            self._save_state(job_dir, state)
            return {'status': 'CANCELLED_BEFORE_SUBMIT', 'adapter_id': selected_id}
        cancel_fn = getattr(executor, 'cancel', None)
        if not callable(cancel_fn):
            state['status'] = 'CANCEL_UNSUPPORTED'
            self._save_state(job_dir, state)
            return {'status': 'CANCEL_UNSUPPORTED', 'adapter_id': selected_id, 'external_job_id': external_job_id}
        provider_result = cancel_fn(str(external_job_id), job=job)
        provider_status = str((provider_result or {}).get('status') or '').upper()
        if provider_status not in {'CANCELLED', 'CANCELED', 'SUCCEEDED', 'COMPLETED', 'FAILED'}:
            state['status'] = 'CANCEL_PENDING'
        elif provider_status in {'SUCCEEDED', 'COMPLETED'}:
            state['status'] = 'CANCEL_TOO_LATE_COMPLETED'
        else:
            state['status'] = 'CANCELLED'
            state['cancel_requested'] = False
        state['cancel_provider_result'] = provider_result
        self._save_state(job_dir, state)
        return {'status': state['status'], 'adapter_id': selected_id, 'external_job_id': external_job_id, 'provider_result': provider_result}

    def reconcile(
        self,
        job_dir: Path,
        *,
        runtime_context: dict[str, Any] | None = None,
        adapter_id: str | None = None,
    ) -> dict[str, Any]:
        job_dir = Path(job_dir)
        job = self._load_job(job_dir)
        state = self._load_state(job_dir, job)
        resolution = self.resolve_adapter(job_dir, adapter_id=adapter_id or state.get('adapter_id'))
        if resolution.get('status') != 'READY':
            state['status'] = 'RECONCILE_HOLD_NO_ADAPTER'
            self._save_state(job_dir, state)
            return {'status': state['status'], 'resolution': resolution}
        selected_id = str(resolution['selected']['adapter_id'])
        executor = self.registry.instantiate(selected_id, runtime_context=runtime_context)
        executor_state = _read_json(job_dir / 'executor_state.json', {})
        external_job_id = ((executor_state.get('adapter_result') or {}).get('external_job_id'))
        if not external_job_id:
            state['status'] = 'RECONCILE_NO_EXTERNAL_JOB'
            self._save_state(job_dir, state)
            return {'status': state['status'], 'adapter_id': selected_id}
        reconcile_fn = getattr(executor, 'reconcile', None)
        if callable(reconcile_fn):
            provider_result = reconcile_fn(str(external_job_id), job=job, local_state=executor_state)
        else:
            provider_result = executor.poll(str(external_job_id), job=job, resume_token=executor_state.get('resume_token'))
        provider_status = str((provider_result or {}).get('status') or '').upper()
        local_status = str(executor_state.get('provider_status') or executor_state.get('status') or '').upper()
        state['reconciliation'] = {
            'external_job_id': external_job_id,
            'local_status': local_status,
            'provider_status': provider_status,
            'matches': bool(provider_status and provider_status == local_status),
            'provider_result': provider_result,
        }
        state['status'] = 'RECONCILED' if state['reconciliation']['matches'] else 'RECONCILIATION_REQUIRED'
        self._save_state(job_dir, state)
        return {'status': state['status'], 'adapter_id': selected_id, **state['reconciliation']}


def execute_jobs_via_bridge(
    jobs_root: Path,
    bridge: ProviderExecutorBridge,
    *,
    runtime_context_by_adapter: dict[str, dict[str, Any]] | None = None,
    asset_ids: list[str] | None = None,
    policy: ExecutionPolicy | None = None,
) -> dict[str, Any]:
    jobs_root = Path(jobs_root)
    index = _read_json(jobs_root / 'PROVIDER_JOB_INDEX.json', {})
    selected = set(asset_ids or [])
    rows = []
    for row in index.get('jobs') or []:
        aid = str(row.get('asset_id') or '')
        if selected and aid not in selected:
            continue
        resolution = bridge.resolve_adapter(jobs_root / aid)
        adapter_id = ((resolution.get('selected') or {}).get('adapter_id')) if resolution.get('status') == 'READY' else None
        context = (runtime_context_by_adapter or {}).get(str(adapter_id), {}) if adapter_id else {}
        outcome = bridge.execute(jobs_root / aid, runtime_context=context, adapter_id=adapter_id, policy=policy)
        rows.append({'asset_id': aid, 'provider': row.get('provider'), **outcome})
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get('status') or 'UNKNOWN')
        counts[key] = counts.get(key, 0) + 1
    complete = bool(rows) and all(x.get('status') == 'COMPLETE' for x in rows)
    return {
        'status': 'BRIDGE_EXECUTION_COMPLETE' if complete else ('NO_PROVIDER_JOBS' if not rows else 'BRIDGE_EXECUTION_INCOMPLETE'),
        'jobs': rows,
        'counts': counts,
        'bridge_contract': bridge_contract(),
    }


class HostCallbackExecutor:
    """ProviderExecutor backed by host-injected callbacks.

    The executor receives callbacks/network clients/credentials only through runtime_context at
    instantiation time. None of that context is exported to registry declarations or bridge state.
    This is the bridge profile intended for real host/provider integrations.
    """

    def __init__(self, runtime_context: dict[str, Any], *, executor_id: str, provider: str) -> None:
        self.executor_id = executor_id
        self.provider = provider
        callbacks = runtime_context.get('callbacks')
        if not isinstance(callbacks, dict):
            raise ValueError('runtime_context.callbacks is required')
        self._callbacks = callbacks
        required = ['ensure_asset', 'submit', 'poll', 'collect', 'resolve']
        missing = [name for name in required if not callable(callbacks.get(name))]
        if missing:
            raise ValueError('missing provider callbacks: ' + ','.join(missing))

    def ensure_asset(
        self,
        binding: dict[str, Any],
        *,
        source_bytes: bytes | None,
        job: dict[str, Any],
        previous_handle: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._callbacks['ensure_asset'](
            binding,
            source_bytes=source_bytes,
            job=job,
            previous_handle=previous_handle,
        )

    def submit(self, transmission: dict[str, Any], *, job: dict[str, Any]) -> dict[str, Any]:
        return self._callbacks['submit'](transmission, job=job)

    def poll(
        self,
        external_job_id: str,
        *,
        job: dict[str, Any],
        resume_token: str | None = None,
    ) -> dict[str, Any]:
        return self._callbacks['poll'](external_job_id, job=job, resume_token=resume_token)

    def collect(self, external_job_id: str, *, job: dict[str, Any]) -> dict[str, Any]:
        return self._callbacks['collect'](external_job_id, job=job)

    def resolve(self, artifact_ref: str, *, job: dict[str, Any]) -> bytes:
        return self._callbacks['resolve'](artifact_ref, job=job)

    def cancel(self, external_job_id: str, *, job: dict[str, Any]) -> dict[str, Any]:
        fn = self._callbacks.get('cancel')
        if not callable(fn):
            raise ProviderPermanentError('cancel callback not supplied')
        return fn(external_job_id, job=job)

    def reconcile(self, external_job_id: str, *, job: dict[str, Any], local_state: dict[str, Any]) -> dict[str, Any]:
        fn = self._callbacks.get('reconcile')
        if not callable(fn):
            raise ProviderPermanentError('reconcile callback not supplied')
        return fn(external_job_id, job=job, local_state=local_state)


def host_callback_adapter_declaration(
    provider: str,
    production_modes: list[str] | tuple[str, ...],
    *,
    adapter_id: str | None = None,
    priority: int = 50,
    supports_cancel: bool = False,
    supports_reconcile: bool = False,
) -> AdapterDeclaration:
    provider_id = str(provider).upper()
    operations = ['ensure_asset', 'submit', 'poll', 'collect', 'resolve']
    capabilities = ['IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE', 'ASSET_HANDLE_LIFECYCLE', 'HOST_CALLBACK_INJECTION']
    if supports_cancel:
        operations.append('cancel')
        capabilities.append('CANCEL')
    if supports_reconcile:
        operations.append('reconcile')
        capabilities.append('RECONCILE')
    return AdapterDeclaration(
        adapter_id=adapter_id or (provider_id + '_HOST_CALLBACK_V1'),
        provider=provider_id,
        production_modes=tuple(str(x).upper() for x in production_modes),
        capabilities=tuple(capabilities),
        operations=tuple(operations),
        priority=int(priority),
        auth_external=True,
        metadata={
            'profile': 'HOST_CALLBACK_PROVIDER_V1',
            'runtime_context_required': True,
            'credentials_persisted': False,
        },
    )


def register_host_callback_adapter(
    registry: ProviderAdapterRegistry,
    *,
    provider: str,
    production_modes: list[str] | tuple[str, ...],
    adapter_id: str | None = None,
    priority: int = 50,
    supports_cancel: bool = False,
    supports_reconcile: bool = False,
    replace: bool = False,
) -> AdapterDeclaration:
    declaration = host_callback_adapter_declaration(
        provider,
        production_modes,
        adapter_id=adapter_id,
        priority=priority,
        supports_cancel=supports_cancel,
        supports_reconcile=supports_reconcile,
    )
    registry.register(
        declaration,
        lambda runtime_context, d=declaration: HostCallbackExecutor(
            runtime_context,
            executor_id=d.adapter_id,
            provider=d.provider,
        ),
        replace=replace,
    )
    return declaration


def build_default_adapter_registry(*, include_reference: bool = False) -> ProviderAdapterRegistry:
    """Build the production-facing registry without embedding credentials or clients.

    EPV is registered as a host-callback profile because it already exists in the CBCC provider
    routing registry. The host decides what SDK/client/credentials implement those callbacks.
    The in-memory reference adapter is opt-in for tests/development only.
    """
    registry = ProviderAdapterRegistry()
    register_host_callback_adapter(
        registry,
        provider='EPV_ADAPTER',
        production_modes=(
            'REAL_PHOTO', 'REAL_PRODUCT_COMPOSITE', 'AI_ENVIRONMENT_REAL_PRODUCT',
            'AI_HUMAN_REAL_PRODUCT', 'AI_GENERATIVE', 'GRAPHIC_DESIGN', 'THREE_D', 'VIDEO',
        ),
        adapter_id='EPV_HOST_CALLBACK_V1',
        priority=10,
        supports_cancel=True,
        supports_reconcile=True,
    )
    if include_reference:
        from .provider_executor import ReferenceMemoryExecutor
        declaration = AdapterDeclaration(
            adapter_id='EPV_REFERENCE_MEMORY_V1',
            provider='EPV_ADAPTER',
            production_modes=(
                'REAL_PHOTO', 'REAL_PRODUCT_COMPOSITE', 'AI_ENVIRONMENT_REAL_PRODUCT',
                'AI_HUMAN_REAL_PRODUCT', 'AI_GENERATIVE', 'GRAPHIC_DESIGN', 'THREE_D', 'VIDEO',
            ),
            capabilities=('IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE', 'ASSET_HANDLE_LIFECYCLE'),
            operations=('ensure_asset', 'submit', 'poll', 'collect', 'resolve'),
            priority=1000,
            auth_external=True,
            metadata={'profile': 'REFERENCE_ONLY', 'production_default': False},
        )
        registry.register(declaration, lambda runtime_context: ReferenceMemoryExecutor())
    return registry
