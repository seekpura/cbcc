from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.asset_compiler import compile_asset_packages
from cbcc.production import build_production_run, materialize_provider_jobs, ingest_provider_job_results
from cbcc.provider_transport import (
    normalize_provider_asset_handle,
    validate_provider_asset_binding,
    validate_provider_asset_refresh,
    build_adapter_transmission,
    validate_adapter_result,
    verify_artifact_reference,
    recover_remote_artifact,
)


def _binding(handle_id='hdl-1', *, state='READY', expires_at=None, supersedes=None, sha='a' * 64):
    lifecycle = normalize_provider_asset_handle({
        'handle_id': handle_id,
        'provider': 'EPV_ADAPTER',
        'state': state,
        'expires_at': expires_at,
        'supersedes_handle': supersedes,
        'sha256': sha,
    }, source_sha256=sha)
    return {
        'asset_id': 'MASTER-1',
        'locator': {'kind': 'PROVIDER_ASSET_HANDLE', 'value': handle_id},
        'sha256': sha,
        'handoff_sha256': sha,
        'provider_asset_lifecycle': lifecycle,
    }


def test_provider_asset_handle_lifecycle_expiry_and_refresh_lineage():
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    ready = _binding(expires_at=(now + timedelta(hours=1)).isoformat())
    assert validate_provider_asset_binding(ready, now=now) == []

    expired = _binding(expires_at=(now - timedelta(seconds=1)).isoformat())
    assert 'PROVIDER_ASSET_HANDLE_EXPIRED' in validate_provider_asset_binding(expired, now=now)

    refreshed = _binding(
        'hdl-2',
        state='REFRESHED',
        expires_at=(now + timedelta(days=1)).isoformat(),
        supersedes='hdl-1',
    )
    assert validate_provider_asset_refresh(ready, refreshed, now=now) == []

    broken = _binding(
        'hdl-3',
        state='REFRESHED',
        expires_at=(now + timedelta(days=1)).isoformat(),
        supersedes='other-handle',
    )
    assert 'PROVIDER_ASSET_REFRESH_LINEAGE_MISSING' in validate_provider_asset_refresh(ready, broken, now=now)


def test_remote_artifact_hash_requires_resolver_and_supports_verified_recovery(tmp_path):
    data = b'v0613-remote-provider-output'
    sha = hashlib.sha256(data).hexdigest()
    artifact = {'path_or_uri': 'https://provider.example/jobs/123/final.png', 'sha256': sha}

    unresolved = verify_artifact_reference(artifact, require_remote_verification=True)
    assert unresolved['status'] == 'UNVERIFIED_REMOTE'
    assert 'PRODUCTION_RECEIPT_REMOTE_ARTIFACT_UNVERIFIED' in unresolved['issues']

    verified = verify_artifact_reference(
        artifact,
        resolver=lambda uri: data,
        require_remote_verification=True,
    )
    assert verified['status'] == 'VERIFIED_REMOTE'
    assert verified['sha256'] == sha

    recovered = recover_remote_artifact(artifact, lambda uri: data, tmp_path / 'recovered')
    assert recovered['status'] == 'RECOVERED_VERIFIED'
    assert Path(recovered['path']).read_bytes() == data

    mismatch = verify_artifact_reference(
        artifact,
        resolver=lambda uri: b'wrong-output',
        require_remote_verification=True,
    )
    assert 'PRODUCTION_RECEIPT_REMOTE_ARTIFACT_HASH_MISMATCH' in mismatch['issues']


def test_external_adapter_transmission_maps_fields_and_binds_external_job():
    job = {
        'job_id': 'JOB-1',
        'asset_id': 'AST-1',
        'provider': 'EPV_ADAPTER',
        'adapter': 'EXTERNAL_ADAPTER',
        'production_mode': 'REAL_PRODUCT_COMPOSITE',
        'package_hash': 'p' * 64,
        'package_ref': {'kind': 'PACKAGE_RELATIVE_PATH', 'value': 'inputs/asset_package'},
        'source_product_bindings': [_binding()],
        'source_binding_hash': 's' * 64,
        'execution_brief': {'canonical_prompt_contract': {'id': 'prompt'}},
        'result_contract': {'required': ['output_path']},
        'production_receipt_contract': {'required': ['output_artifacts']},
    }
    tx = build_adapter_transmission(job)
    assert tx['status'] == 'READY'
    assert tx['vendor_request']['client_job_id'] == 'JOB-1'
    assert tx['vendor_request']['source_assets'] == job['source_product_bindings']
    assert tx['request_hash'] and tx['idempotency_key']

    row = {
        'provider': 'EPV_ADAPTER',
        'provider_contract': {'adapter': 'EXTERNAL_ADAPTER'},
        'provider_adapter_transmission': tx,
    }
    result = {
        'adapter_result': {
            'transmission_id': tx['transmission_id'],
            'request_hash': tx['request_hash'],
            'idempotency_key': tx['idempotency_key'],
            'external_job_id': 'EXT-7788',
            'status': 'COMPLETED',
        }
    }
    assert validate_adapter_result(row, result) == []

    tampered = json.loads(json.dumps(result))
    tampered['adapter_result']['request_hash'] = 'wrong'
    assert 'ADAPTER_RESULT_BINDING_MISMATCH:request_hash' in validate_adapter_result(row, tampered)


def _asset():
    return {
        'asset_id': 'AST-V0613-REMOTE', 'asset_name': 'Remote provider transport proof', 'asset_type': 'IMAGE',
        'status': 'ACTIVATE', 'surface': 'GALLERY', 'family': 'VISUAL',
        'consumer_question': 'What is this product?', 'strategic_job': 'Identify exact product',
        'production_mode': 'REAL_PRODUCT_COMPOSITE', 'product_fidelity': 'LOCKED_PIXEL', 'priority': 'P0',
        'dependencies': [], 'source_ids': ['SRC-1'], 'claim_ids': [], 'listing_reference': [],
        'success_metric': 'identity clarity',
    }


def _compile(root: Path, master: Path):
    data = b'v0613-real-product-master'
    master.write_bytes(data)
    sha = hashlib.sha256(data).hexdigest()
    compile_asset_packages(
        root, [_asset()], {'name': 'P'}, {'platform_family': 'x', 'site': 'MY', 'market': 'Malaysia'},
        {'visual_implications': []}, {'visible_copy_locales': ['en-MY']}, {'profiles': []},
        source_product_assets=[{
            'asset_id': 'MASTER-V0613', 'role': 'FRONT_MASTER', 'path': str(master), 'sha256': sha,
            'ingest_status': 'HASH_VERIFIED_LOCAL', 'pixel_lock': True,
            'allowed_transforms': ['PROPORTIONAL_SCALE', 'PLACEMENT', 'MASK_OR_CROP', 'COMPOSITE'],
            'identity_features': ['logo', 'packaging_print', 'color', 'geometry', 'proportions'],
        }],
    )
    return sha


def _quality(job):
    hashes = {x['asset_id']: x['sha256'] for x in job['source_product_bindings']}
    out = {}
    for key in job['result_contract']['quality_observations_required']:
        if key == 'source_product_asset_ids_used':
            out[key] = list(hashes)
        elif key == 'source_product_hashes_used':
            out[key] = hashes
        elif key == 'product_layer_operation':
            out[key] = 'COMPOSITE_LOCKED'
        else:
            out[key] = {'status': 'PASS', 'evidence': 'provider evidence for ' + key}
    return out


def _write_remote_result(job_dir: Path, job: dict, source_sha: str, output_data: bytes):
    remote_uri = 'https://provider.example/jobs/' + job['job_id'] + '/final.png'
    output_sha = hashlib.sha256(output_data).hexdigest()
    result = {
        'asset_id': job['asset_id'], 'provider': job['provider'], 'package_hash': job['package_hash'],
        'output_path': remote_uri,
        'changed_fields': [], 'changed_layers': [],
        'qa': {'product': True, 'fact': True, 'claim': True, 'visual': True, 'culture': True, 'platform': True},
        'production_contract_ack': True,
        'source_binding_hash': job['source_binding_hash'],
        'quality_observations': _quality(job),
        'production_receipt': {
            'job_id': job['job_id'], 'asset_id': job['asset_id'], 'provider': job['provider'],
            'package_hash': job['package_hash'],
            'portable_manifest_hash': job['portable_package']['portable_manifest_hash'],
            'source_binding_hash': job['source_binding_hash'],
            'output_artifacts': [{'path_or_uri': remote_uri, 'sha256': output_sha, 'role': 'FINAL'}],
            'layer_manifest': [{
                'layer_id': 'product-master', 'role': 'PRODUCT_MASTER',
                'source_asset_id': 'MASTER-V0613', 'source_sha256': source_sha,
                'operation': 'COMPOSITE_LOCKED', 'frozen': True,
            }],
            'capture_metadata': {},
        },
    }
    (job_dir / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return remote_uri


def test_ingested_remote_result_is_reviewed_without_resolver_and_passes_with_verified_bytes(tmp_path):
    packs = tmp_path / 'packs'
    master = tmp_path / 'master.png'
    source_sha = _compile(packs, master)
    run = build_production_run(packs)
    jobs = tmp_path / 'jobs'
    materialize_provider_jobs(packs, run, jobs)
    job_dir = jobs / _asset()['asset_id']
    job = json.loads((job_dir / 'job.json').read_text(encoding='utf-8'))
    output_data = b'remote-provider-output-v0613'
    remote_uri = _write_remote_result(job_dir, job, source_sha, output_data)

    unresolved = ingest_provider_job_results(run, jobs)
    assert any(x['code'] == 'PRODUCTION_RECEIPT_REMOTE_ARTIFACT_UNVERIFIED' for x in unresolved['issues'])

    resolved = ingest_provider_job_results(run, jobs, remote_artifact_resolver=lambda uri: output_data if uri == remote_uri else b'')
    assert resolved['status'] == 'COMPLETE'


def test_epv_adapter_job_contains_transmission_and_requires_bound_external_job_ack(tmp_path):
    packs = tmp_path / 'packs'
    master = tmp_path / 'master.png'
    source_sha = _compile(packs, master)
    run = build_production_run(packs, provider_preferences={'REAL_PRODUCT_COMPOSITE': 'EPV_ADAPTER'})
    assert run['assets'][0]['provider'] == 'EPV_ADAPTER'
    jobs = tmp_path / 'jobs'
    materialize_provider_jobs(packs, run, jobs)
    job_dir = jobs / _asset()['asset_id']
    job = json.loads((job_dir / 'job.json').read_text(encoding='utf-8'))
    tx = job['adapter_transmission']
    assert tx['status'] == 'READY'
    assert tx['vendor_request']['client_job_id'] == job['job_id']
    assert 'adapter_result' in job['result_contract']['required']

    output_data = b'external-adapter-output-v0613'
    remote_uri = _write_remote_result(job_dir, job, source_sha, output_data)
    result_path = job_dir / 'result.json'
    result = json.loads(result_path.read_text(encoding='utf-8'))
    result['adapter_result'] = {
        'transmission_id': tx['transmission_id'],
        'request_hash': tx['request_hash'],
        'idempotency_key': tx['idempotency_key'],
        'external_job_id': 'EPV-JOB-123',
        'status': 'COMPLETED',
    }
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    passed = ingest_provider_job_results(run, jobs, remote_artifact_resolver=lambda uri: output_data if uri == remote_uri else b'')
    assert passed['status'] == 'COMPLETE'

    result['adapter_result']['external_job_id'] = ''
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    reviewed = ingest_provider_job_results(run, jobs, remote_artifact_resolver=lambda uri: output_data)
    assert any(x['code'] == 'ADAPTER_EXTERNAL_JOB_ID_MISSING' for x in reviewed['issues'])
