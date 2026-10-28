from pathlib import Path

path = Path('runtime/cbcc/provider_bridge.py')
text = path.read_text(encoding='utf-8')
old = """            except ProviderRateLimitError as exc:\n                delay = float(exc.retry_after_seconds) if exc.retry_after_seconds is not None else policy.backoff_for(attempt_number)\n                error_code = exc.code\n            except ProviderTransientError as exc:\n                delay = policy.backoff_for(attempt_number)\n                error_code = exc.code\n            except Exception as exc:\n"""
new = """            except ProviderRateLimitError as exc:\n                delay = float(exc.retry_after_seconds) if exc.retry_after_seconds is not None else policy.backoff_for(attempt_number)\n                error_code = exc.code\n                error_message = str(exc)\n            except ProviderTransientError as exc:\n                delay = policy.backoff_for(attempt_number)\n                error_code = exc.code\n                error_message = str(exc)\n            except Exception as exc:\n"""
if old not in text:
    raise SystemExit('retry except block not found')
text = text.replace(old, new, 1)
text = text.replace("'error': str(exc),\n                'retry_after_seconds': delay,", "'error': error_message,\n                'retry_after_seconds': delay,", 1)

append = r'''

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
'''
if 'class HostCallbackExecutor:' not in text:
    text += append
path.write_text(text, encoding='utf-8')
