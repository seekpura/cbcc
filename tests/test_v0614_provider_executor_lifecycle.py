from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.asset_compiler import compile_asset_packages
from cbcc.production import build_production_run, materialize_provider_jobs, ingest_provider_job_results
from cbcc.provider_executor import (
    ReferenceMemoryExecutor,
    execute_provider_job_directory,
    execute_materialized_provider_jobs,
)
from cbcc.providers import provider_contract


def _asset(asset_id='AST-V0614'):
    return {
        'asset_id': asset_id,
        'asset_name': 'Provider executor lifecycle proof',
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


def _compile_local_master(root: Path, master: Path, asset_id='AST-V0614'):
    data = b'v0614-local-product-master'
    master.write_bytes(data)
    sha = hashlib.sha256(data).hexdigest()
    compile_asset_packages(
        root,
        [_asset(asset_id)],
        {'name': 'P'},
        {'platform_family': 'x', 'site': 'MY', 'market': 'Malaysia'},
        {'visual_implications': []},
        {'visible_copy_locales': ['en-MY']},
        {'profiles': []},
        source_product_assets=[{
            'asset_id': 'MASTER-V0614',
            'role': 'FRONT_MASTER',
            'path': str(master),
            'sha256': sha,
            'ingest_status': 'HASH_VERIFIED_LOCAL',
            'pixel_lock': True,
            'allowed_transforms': ['PROPORTIONAL_SCALE', 'PLACEMENT', 'MASK_OR_CROP', 'COMPOSITE'],
            'identity_features': ['logo', 'packaging_print', 'color', 'geometry', 'proportions'],
        }],
    )
    return sha


def _materialize(tmp_path: Path, *, asset_id='AST-V0614'):
    packs = tmp_path / 'packs'
    master = tmp_path / 'master.bin'
    source_sha = _compile_local_master(packs, master, asset_id=asset_id)
    run = build_production_run(packs, provider_preferences={'REAL_PRODUCT_COMPOSITE': 'EPV_ADAPTER'})
    assert run['assets'][0]['provider'] == 'EPV_ADAPTER'
    jobs = tmp_path / 'jobs'
    index = materialize_provider_jobs(packs, run, jobs)
    assert index['job_count'] == 1
    return packs, run, jobs, source_sha


def test_external_provider_contract_exposes_executor_lifecycle():
    contract = provider_contract('EPV_ADAPTER', 'REAL_PRODUCT_COMPOSITE', _asset())
    assert contract['status'] == 'READY'
    assert contract['adapter'] == 'EXTERNAL_ADAPTER'
    lifecycle = contract['executor_contract']['lifecycle']
    assert lifecycle[0] == 'PREPARE_SOURCE_ASSETS'
    assert 'SUBMIT' in lifecycle
    assert 'POLL_OR_RESUME' in lifecycle
    assert lifecycle[-1] == 'INGEST_EXISTING_RUNTIME'
    assert 'credentials' in contract['executor_contract']['adapter_owns']


def test_executor_upload_submit_resume_download_receipt_and_existing_ingest(tmp_path):
    _, run, jobs, source_sha = _materialize(tmp_path)
    job_dir = jobs / 'AST-V0614'
    original_job = json.loads((job_dir / 'job.json').read_text(encoding='utf-8'))
    original_binding_hash = original_job['source_binding_hash']

    executor = ReferenceMemoryExecutor(poll_sequence=('RUNNING', 'RUNNING', 'COMPLETED'))
    first = execute_provider_job_directory(job_dir, executor, max_polls=1)
    assert first['status'] == 'PENDING'
    assert executor.submit_calls == 1
    assert executor.ensure_asset_calls == 1
    state = json.loads((job_dir / 'executor_state.json').read_text(encoding='utf-8'))
    assert state['phase'] == 'RUNNING'
    assert state['adapter_result']['external_job_id']
    assert state['transmission']['idempotency_key']

    second = execute_provider_job_directory(job_dir, executor, max_polls=5)
    assert second['status'] == 'COMPLETE'
    assert executor.submit_calls == 1, 'resume must not submit a second provider job'
    result = json.loads((job_dir / 'result.json').read_text(encoding='utf-8'))
    assert Path(result['output_path']).read_bytes() == executor.default_output
    assert result['production_receipt']['output_artifacts'][0]['path_or_uri'] == 'outputs/final.bin'
    assert result['production_receipt']['output_artifacts'][0]['sha256'] == hashlib.sha256(executor.default_output).hexdigest()
    assert result['production_receipt']['layer_manifest'][0]['source_sha256'] == source_sha
    assert result['source_binding_hash'] == original_binding_hash
    assert result['production_receipt']['source_binding_hash'] == original_binding_hash
    assert result['adapter_result']['idempotency_key'] == state['transmission']['idempotency_key']

    ingested = ingest_provider_job_results(run, jobs)
    assert ingested['status'] == 'COMPLETE'
    assert ingested['provider_results_ingested'] == 1
    assert ingested['issues'] == []


def test_batch_executor_consumes_materialized_job_index_and_writes_ingestable_result(tmp_path):
    _, run, jobs, _ = _materialize(tmp_path)
    executor = ReferenceMemoryExecutor(poll_sequence=('COMPLETED',))
    execution = execute_materialized_provider_jobs(jobs, {'EPV_ADAPTER': executor})
    assert execution['status'] == 'EXECUTION_COMPLETE'
    assert execution['counts']['COMPLETE'] == 1
    assert execution['jobs'][0]['status'] == 'COMPLETE'
    assert (jobs / 'AST-V0614' / 'executor_state.json').exists()
    assert (jobs / 'AST-V0614' / 'result.json').exists()
    ingested = ingest_provider_job_results(run, jobs)
    assert ingested['status'] == 'COMPLETE'


def test_expired_provider_handle_is_refreshed_with_lineage_before_submit(tmp_path):
    packs = tmp_path / 'packs'
    now = datetime.now(timezone.utc)
    sha = 'a' * 64
    compile_asset_packages(
        packs,
        [_asset('AST-REFRESH')],
        {'name': 'P'},
        {'platform_family': 'x', 'site': 'MY', 'market': 'Malaysia'},
        {'visual_implications': []},
        {'visible_copy_locales': ['en-MY']},
        {'profiles': []},
        source_product_assets=[{
            'asset_id': 'MASTER-REMOTE',
            'role': 'FRONT_MASTER',
            'provider_asset_handle': {
                'handle_id': 'OLD-HANDLE',
                'provider': 'EPV_ADAPTER',
                'state': 'READY',
                'sha256': sha,
                'issued_at': (now - timedelta(days=10)).isoformat(),
                'verified_at': (now - timedelta(days=10)).isoformat(),
                'expires_at': (now - timedelta(days=1)).isoformat(),
                'generation': 4,
            },
            'sha256': sha,
            'ingest_status': 'EXTERNAL_HANDLE_HASH_DECLARED',
            'pixel_lock': True,
            'allowed_transforms': ['PLACEMENT', 'COMPOSITE'],
            'identity_features': ['logo', 'packaging_print', 'geometry'],
        }],
    )
    run = build_production_run(packs, provider_preferences={'REAL_PRODUCT_COMPOSITE': 'EPV_ADAPTER'})
    # Expired structured handles are correctly held at the upstream handoff boundary.
    assert run['assets'][0]['status'] == 'HOLD_REAL_PRODUCT_PREFLIGHT'

    # Build a portable fixture from an otherwise-valid handle, then expire it after materialization
    # to prove the executor refresh boundary without weakening upstream preflight.
    valid_packs = tmp_path / 'valid-packs'
    future = (now + timedelta(days=10)).isoformat()
    compile_asset_packages(
        valid_packs,
        [_asset('AST-REFRESH')],
        {'name': 'P'},
        {'platform_family': 'x', 'site': 'MY', 'market': 'Malaysia'},
        {'visual_implications': []},
        {'visible_copy_locales': ['en-MY']},
        {'profiles': []},
        source_product_assets=[{
            'asset_id': 'MASTER-REMOTE',
            'role': 'FRONT_MASTER',
            'provider_asset_handle': {
                'handle_id': 'OLD-HANDLE',
                'provider': 'EPV_ADAPTER',
                'state': 'READY',
                'sha256': sha,
                'issued_at': now.isoformat(),
                'verified_at': now.isoformat(),
                'expires_at': future,
                'generation': 4,
            },
            'sha256': sha,
            'ingest_status': 'EXTERNAL_HANDLE_HASH_DECLARED',
            'pixel_lock': True,
            'allowed_transforms': ['PLACEMENT', 'COMPOSITE'],
            'identity_features': ['logo', 'packaging_print', 'geometry'],
        }],
    )
    valid_run = build_production_run(valid_packs, provider_preferences={'REAL_PRODUCT_COMPOSITE': 'EPV_ADAPTER'})
    jobs = tmp_path / 'refresh-jobs'
    materialize_provider_jobs(valid_packs, valid_run, jobs)
    job_dir = jobs / 'AST-REFRESH'
    job = json.loads((job_dir / 'job.json').read_text(encoding='utf-8'))
    source = job['source_product_bindings'][0]
    source['provider_asset_lifecycle']['expires_at'] = (now - timedelta(seconds=1)).isoformat()
    (job_dir / 'job.json').write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding='utf-8')

    executor = ReferenceMemoryExecutor(poll_sequence=('COMPLETED',))
    outcome = execute_provider_job_directory(job_dir, executor, max_polls=1)
    assert outcome['status'] == 'COMPLETE'
    state = json.loads((job_dir / 'executor_state.json').read_text(encoding='utf-8'))
    refreshed = state['provider_source_bindings'][0]
    assert refreshed['locator']['value'] != 'OLD-HANDLE'
    assert refreshed['provider_asset_lifecycle']['supersedes_handle'] == 'OLD-HANDLE'
    assert refreshed['provider_asset_lifecycle']['generation'] == 5
    assert refreshed['sha256'] == sha
    assert executor.ensure_asset_calls == 1
