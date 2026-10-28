from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.asset_compiler import compile_asset_packages
from cbcc.production import build_production_run, materialize_provider_jobs, ingest_provider_job_results
from cbcc.provider_executor import ReferenceMemoryExecutor
from cbcc.provider_bridge import (
    AdapterDeclaration,
    ExecutionPolicy,
    ProviderAdapterRegistry,
    ProviderExecutorBridge,
    ProviderRateLimitError,
    bridge_contract,
    build_default_adapter_registry,
    execute_jobs_via_bridge,
    register_host_callback_adapter,
)


def _asset(asset_id='AST-V0615'):
    return {
        'asset_id': asset_id,
        'asset_name': 'Provider executor bridge proof',
        'asset_type': 'IMAGE',
        'status': 'ACTIVATE',
        'surface': 'GALLERY',
        'family': 'VISUAL',
        'consumer_question': 'What is this product?',
        'strategic_job': 'Preserve exact product identity through provider execution',
        'production_mode': 'REAL_PRODUCT_COMPOSITE',
        'product_fidelity': 'LOCKED_PIXEL',
        'priority': 'P0',
        'dependencies': [],
        'source_ids': ['SRC-1'],
        'claim_ids': [],
        'listing_reference': [],
        'success_metric': 'identity clarity',
    }


def _materialize(tmp_path: Path, asset_id='AST-V0615'):
    packs = tmp_path / 'packs'
    master = tmp_path / 'master.bin'
    data = b'v0615-real-product-master'
    master.write_bytes(data)
    sha = hashlib.sha256(data).hexdigest()
    compile_asset_packages(
        packs,
        [_asset(asset_id)],
        {'name': 'P'},
        {'platform_family': 'x', 'site': 'MY', 'market': 'Malaysia'},
        {'visual_implications': []},
        {'visible_copy_locales': ['en-MY']},
        {'profiles': []},
        source_product_assets=[{
            'asset_id': 'MASTER-V0615',
            'role': 'FRONT_MASTER',
            'path': str(master),
            'sha256': sha,
            'ingest_status': 'HASH_VERIFIED_LOCAL',
            'pixel_lock': True,
            'allowed_transforms': ['PROPORTIONAL_SCALE', 'PLACEMENT', 'MASK_OR_CROP', 'COMPOSITE'],
            'identity_features': ['logo', 'packaging_print', 'color', 'geometry', 'proportions'],
        }],
    )
    run = build_production_run(packs, provider_preferences={'REAL_PRODUCT_COMPOSITE': 'EPV_ADAPTER'})
    jobs = tmp_path / 'jobs'
    index = materialize_provider_jobs(packs, run, jobs)
    assert index['job_count'] == 1
    return run, jobs


def _callbacks(reference: ReferenceMemoryExecutor, *, cancel=None, reconcile=None):
    rows = {
        'ensure_asset': reference.ensure_asset,
        'submit': reference.submit,
        'poll': reference.poll,
        'collect': reference.collect,
        'resolve': reference.resolve,
    }
    if cancel is not None:
        rows['cancel'] = cancel
    if reconcile is not None:
        rows['reconcile'] = reconcile
    return rows


def test_registry_discovery_is_capability_based_priority_ordered_and_credential_free():
    registry = ProviderAdapterRegistry()
    ref = ReferenceMemoryExecutor()
    high = AdapterDeclaration(
        adapter_id='HIGH', provider='EPV_ADAPTER', production_modes=('REAL_PRODUCT_COMPOSITE',),
        capabilities=('IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE', 'ASSET_HANDLE_LIFECYCLE'),
        priority=50,
    )
    low = AdapterDeclaration(
        adapter_id='LOW', provider='EPV_ADAPTER', production_modes=('REAL_PRODUCT_COMPOSITE',),
        capabilities=('IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE', 'ASSET_HANDLE_LIFECYCLE'),
        priority=10,
    )
    registry.register(high, lambda context: ref)
    registry.register(low, lambda context: ref)
    found = registry.discover(
        provider='EPV_ADAPTER', production_mode='REAL_PRODUCT_COMPOSITE',
        required_capabilities=['IDEMPOTENT_SUBMIT', 'OUTPUT_RESOLVE'],
    )
    assert [x['adapter_id'] for x in found] == ['LOW', 'HIGH']
    selected = registry.resolve(
        provider='EPV_ADAPTER', production_mode='REAL_PRODUCT_COMPOSITE',
        required_capabilities=['IDEMPOTENT_SUBMIT', 'OUTPUT_RESOLVE'],
    )
    assert selected['selected']['adapter_id'] == 'LOW'
    serialized = json.dumps(registry.declarations())
    assert 'secret' not in serialized.lower() and 'credential' not in serialized.lower()
    assert bridge_contract()['registry']['credential_storage'] == 'FORBIDDEN'


def test_default_registry_exposes_real_host_callback_profile_not_reference_by_default():
    registry = build_default_adapter_registry()
    rows = registry.discover(
        provider='EPV_ADAPTER',
        production_mode='REAL_PRODUCT_COMPOSITE',
        required_capabilities=['HOST_CALLBACK_INJECTION', 'IDEMPOTENT_SUBMIT', 'ASSET_HANDLE_LIFECYCLE'],
    )
    assert len(rows) == 1
    assert rows[0]['adapter_id'] == 'EPV_HOST_CALLBACK_V1'
    assert rows[0]['auth_external'] is True
    assert rows[0]['metadata']['credentials_persisted'] is False
    assert 'EPV_REFERENCE_MEMORY_V1' not in [x['adapter_id'] for x in registry.declarations()]


def test_host_callback_bridge_executes_existing_provider_chain_and_ingests(tmp_path):
    run, jobs = _materialize(tmp_path)
    reference = ReferenceMemoryExecutor(poll_sequence=('COMPLETED',))
    registry = build_default_adapter_registry()
    bridge = ProviderExecutorBridge(registry, sleeper=lambda _: None)
    secret = 'DO-NOT-PERSIST-SECRET-0615'
    context = {'callbacks': _callbacks(reference), 'api_key': secret}
    outcome = bridge.execute(
        jobs / 'AST-V0615',
        runtime_context=context,
        adapter_id='EPV_HOST_CALLBACK_V1',
        policy=ExecutionPolicy(max_attempts=2, max_polls_per_attempt=2),
    )
    assert outcome['status'] == 'COMPLETE'
    assert outcome['adapter_id'] == 'EPV_HOST_CALLBACK_V1'
    bridge_state_text = (jobs / 'AST-V0615' / 'bridge_state.json').read_text(encoding='utf-8')
    assert secret not in bridge_state_text
    assert (jobs / 'AST-V0615' / 'result.json').exists()
    ingested = ingest_provider_job_results(run, jobs)
    assert ingested['status'] == 'COMPLETE'
    assert ingested['issues'] == []


def test_rate_limit_retry_uses_provider_retry_after_and_resumes_single_chain(tmp_path):
    run, jobs = _materialize(tmp_path)
    reference = ReferenceMemoryExecutor(poll_sequence=('COMPLETED',))
    calls = {'ensure': 0}

    def ensure_asset(binding, *, source_bytes, job, previous_handle=None):
        calls['ensure'] += 1
        if calls['ensure'] == 1:
            raise ProviderRateLimitError('429 from provider', retry_after_seconds=7.5)
        return reference.ensure_asset(binding, source_bytes=source_bytes, job=job, previous_handle=previous_handle)

    callbacks = _callbacks(reference)
    callbacks['ensure_asset'] = ensure_asset
    slept = []
    registry = build_default_adapter_registry()
    bridge = ProviderExecutorBridge(registry, sleeper=lambda seconds: slept.append(seconds))
    outcome = bridge.execute(
        jobs / 'AST-V0615',
        runtime_context={'callbacks': callbacks},
        adapter_id='EPV_HOST_CALLBACK_V1',
        policy=ExecutionPolicy(max_attempts=2, base_backoff_seconds=1, max_polls_per_attempt=2),
    )
    assert outcome['status'] == 'COMPLETE'
    assert slept == [7.5]
    state = json.loads((jobs / 'AST-V0615' / 'bridge_state.json').read_text(encoding='utf-8'))
    assert state['attempts'][0]['status'] == 'RETRY_SCHEDULED'
    assert state['attempts'][0]['error_code'] == 'PROVIDER_RATE_LIMITED'
    assert state['attempts'][1]['status'] == 'COMPLETE'
    assert reference.submit_calls == 1
    assert ingest_provider_job_results(run, jobs)['status'] == 'COMPLETE'


def test_cancel_and_reconcile_use_declared_host_capabilities_without_parallel_state(tmp_path):
    _, jobs = _materialize(tmp_path)
    reference = ReferenceMemoryExecutor(poll_sequence=('RUNNING', 'RUNNING', 'RUNNING'))
    cancelled = []

    def cancel(external_job_id, *, job):
        cancelled.append(external_job_id)
        return {'status': 'CANCELLED'}

    def reconcile(external_job_id, *, job, local_state):
        return {'status': local_state.get('provider_status') or 'RUNNING', 'external_job_id': external_job_id}

    registry = ProviderAdapterRegistry()
    register_host_callback_adapter(
        registry,
        provider='EPV_ADAPTER',
        production_modes=['REAL_PRODUCT_COMPOSITE'],
        adapter_id='EPV-CONTROL',
        supports_cancel=True,
        supports_reconcile=True,
    )
    callbacks = _callbacks(reference, cancel=cancel, reconcile=reconcile)
    context = {'callbacks': callbacks}
    bridge = ProviderExecutorBridge(registry, sleeper=lambda _: None)
    pending = bridge.execute(
        jobs / 'AST-V0615', runtime_context=context, adapter_id='EPV-CONTROL',
        policy=ExecutionPolicy(max_attempts=3, max_polls_per_attempt=1),
    )
    assert pending['status'] == 'PENDING'
    reconciled = bridge.reconcile(jobs / 'AST-V0615', runtime_context=context, adapter_id='EPV-CONTROL')
    assert reconciled['status'] == 'RECONCILED'
    assert reconciled['matches'] is True
    requested = bridge.request_cancel(jobs / 'AST-V0615', reason='operator requested stop')
    assert requested['status'] == 'CANCEL_REQUESTED'
    stopped = bridge.execute(jobs / 'AST-V0615', runtime_context=context, adapter_id='EPV-CONTROL')
    assert stopped['status'] == 'CANCELLED'
    assert len(cancelled) == 1
    executor_state = json.loads((jobs / 'AST-V0615' / 'executor_state.json').read_text(encoding='utf-8'))
    bridge_state = json.loads((jobs / 'AST-V0615' / 'bridge_state.json').read_text(encoding='utf-8'))
    assert executor_state['adapter_result']['external_job_id'] == cancelled[0]
    assert bridge_state['cancel_provider_result']['status'] == 'CANCELLED'


def test_batch_bridge_consumes_provider_job_index_and_context_by_adapter(tmp_path):
    run, jobs = _materialize(tmp_path)
    reference = ReferenceMemoryExecutor(poll_sequence=('COMPLETED',))
    registry = build_default_adapter_registry()
    bridge = ProviderExecutorBridge(registry, sleeper=lambda _: None)
    batch = execute_jobs_via_bridge(
        jobs,
        bridge,
        runtime_context_by_adapter={'EPV_HOST_CALLBACK_V1': {'callbacks': _callbacks(reference)}},
        policy=ExecutionPolicy(max_attempts=2, max_polls_per_attempt=2),
    )
    assert batch['status'] == 'BRIDGE_EXECUTION_COMPLETE'
    assert batch['counts']['COMPLETE'] == 1
    assert ingest_provider_job_results(run, jobs)['status'] == 'COMPLETE'
