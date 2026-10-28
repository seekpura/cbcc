from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.asset_compiler import compile_asset_packages
from cbcc.production import build_production_run, materialize_provider_jobs, ingest_provider_job_results


def _asset(mode='REAL_PRODUCT_COMPOSITE'):
    return {
        'asset_id': 'AST-V0612-PORTABLE', 'asset_name': 'Portable provider proof', 'asset_type': 'IMAGE', 'status': 'ACTIVATE',
        'surface': 'GALLERY', 'family': 'VISUAL', 'consumer_question': 'What is this product?', 'strategic_job': 'Identify exact product',
        'production_mode': mode, 'product_fidelity': 'LOCKED_PIXEL', 'priority': 'P0', 'dependencies': [],
        'source_ids': ['SRC-1'], 'claim_ids': [], 'listing_reference': [], 'success_metric': 'identity clarity',
    }


def _compile(root: Path, master: Path, mode='REAL_PRODUCT_COMPOSITE'):
    data = b'v0612-portable-real-product-master'
    master.write_bytes(data)
    sources = [{
        'asset_id': 'MASTER-V0612', 'role': 'FRONT_MASTER', 'path': str(master),
        'sha256': hashlib.sha256(data).hexdigest(), 'ingest_status': 'HASH_VERIFIED_LOCAL', 'pixel_lock': True,
        'allowed_transforms': ['PROPORTIONAL_SCALE', 'PLACEMENT', 'MASK_OR_CROP', 'COMPOSITE'],
        'identity_features': ['logo', 'packaging_print', 'color', 'geometry', 'proportions'],
    }]
    compile_asset_packages(
        root, [_asset(mode)], {'name': 'P'}, {'platform_family': 'x', 'site': 'MY', 'market': 'Malaysia'},
        {'visual_implications': []}, {'visible_copy_locales': ['en-MY']}, {'profiles': []}, source_product_assets=sources,
    )
    return hashlib.sha256(data).hexdigest()


def _quality(job: dict):
    hashes = {x['asset_id']: x['sha256'] for x in job['source_product_bindings']}
    out = {}
    for key in job['result_contract']['quality_observations_required']:
        if key == 'source_product_asset_ids_used': out[key] = list(hashes)
        elif key == 'source_product_hashes_used': out[key] = hashes
        elif key == 'product_layer_operation': out[key] = 'COMPOSITE_LOCKED'
        else: out[key] = {'status': 'PASS', 'evidence': 'provider evidence for ' + key}
    return out


def _write_external_result(job_dir: Path, job: dict, source_sha: str, *, capture=False, tamper_output_hash=False, omit_receipt=False):
    outputs = job_dir / 'outputs'
    outputs.mkdir(exist_ok=True)
    final = outputs / 'final.png'
    final.write_bytes(b'provider-output-v0612')
    output_sha = hashlib.sha256(final.read_bytes()).hexdigest()
    if tamper_output_hash:
        output_sha = '0' * 64
    result = {
        'asset_id': job['asset_id'], 'provider': job['provider'], 'package_hash': job['package_hash'], 'output_path': 'outputs/final.png',
        'changed_fields': [], 'changed_layers': [],
        'qa': {'product': True, 'fact': True, 'claim': True, 'visual': True, 'culture': True, 'platform': True},
        'production_contract_ack': True, 'source_binding_hash': job['source_binding_hash'],
        'quality_observations': _quality(job),
    }
    if not omit_receipt:
        result['production_receipt'] = {
            'job_id': job['job_id'], 'asset_id': job['asset_id'], 'provider': job['provider'],
            'package_hash': job['package_hash'], 'portable_manifest_hash': job['portable_package']['portable_manifest_hash'],
            'source_binding_hash': job['source_binding_hash'],
            'output_artifacts': [{'path_or_uri': 'outputs/final.png', 'sha256': output_sha, 'role': 'FINAL'}],
            'layer_manifest': [{
                'layer_id': 'product-master', 'role': 'PRODUCT_MASTER', 'source_asset_id': 'MASTER-V0612',
                'source_sha256': source_sha, 'operation': 'COMPOSITE_LOCKED', 'frozen': True,
            }],
            'capture_metadata': {'capture_type': 'CAMERA_CAPTURE'} if capture else {},
        }
    (job_dir / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')


def test_materialized_job_is_self_contained_after_original_master_disappears(tmp_path):
    packs = tmp_path / 'packs'; master = tmp_path / 'master.png'; source_sha = _compile(packs, master)
    run = build_production_run(packs)
    jobs = tmp_path / 'jobs'; index = materialize_provider_jobs(packs, run, jobs)
    assert index['job_count'] == 1
    job_dir = jobs / _asset()['asset_id']
    job = json.loads((job_dir / 'job.json').read_text(encoding='utf-8'))
    binding = job['source_product_bindings'][0]
    assert binding['locator']['kind'] == 'PACKAGE_RELATIVE_PATH'
    portable_master = job_dir / binding['locator']['value']
    assert portable_master.exists()
    assert hashlib.sha256(portable_master.read_bytes()).hexdigest() == source_sha
    assert job['package_ref'] == {'kind': 'PACKAGE_RELATIVE_PATH', 'value': 'inputs/asset_package'}
    assert str(master) not in (job_dir / 'job.json').read_text(encoding='utf-8')
    master.unlink()
    assert portable_master.exists()


def test_external_result_receipt_binds_job_source_layer_and_output_hash(tmp_path):
    packs = tmp_path / 'packs'; master = tmp_path / 'master.png'; source_sha = _compile(packs, master)
    run = build_production_run(packs)
    jobs = tmp_path / 'jobs'; materialize_provider_jobs(packs, run, jobs)
    job_dir = jobs / _asset()['asset_id']
    job = json.loads((job_dir / 'job.json').read_text(encoding='utf-8'))
    master.unlink()
    _write_external_result(job_dir, job, source_sha)
    applied = ingest_provider_job_results(run, jobs)
    assert applied['status'] == 'COMPLETE'
    row = applied['assets'][0]
    assert row['production_receipt_hash']
    assert row['production_receipt']['job_id'] == job['job_id']


def test_external_provider_receipt_missing_or_tampered_is_reviewed(tmp_path):
    packs = tmp_path / 'packs'; master = tmp_path / 'master.png'; source_sha = _compile(packs, master)
    run = build_production_run(packs)
    jobs = tmp_path / 'jobs'; materialize_provider_jobs(packs, run, jobs)
    job_dir = jobs / _asset()['asset_id']
    job = json.loads((job_dir / 'job.json').read_text(encoding='utf-8'))

    _write_external_result(job_dir, job, source_sha, omit_receipt=True)
    missing = ingest_provider_job_results(run, jobs)
    assert any(x['code'] == 'PRODUCTION_RECEIPT_MISSING' for x in missing['issues'])

    _write_external_result(job_dir, job, source_sha, tamper_output_hash=True)
    tampered = ingest_provider_job_results(run, jobs)
    assert any(x['code'] == 'PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_HASH_MISMATCH' for x in tampered['issues'])


def test_real_capture_mode_requires_capture_metadata_in_receipt(tmp_path):
    packs = tmp_path / 'packs'; master = tmp_path / 'master.png'; source_sha = _compile(packs, master, mode='REAL_PHOTO')
    run = build_production_run(packs)
    jobs = tmp_path / 'jobs'; materialize_provider_jobs(packs, run, jobs)
    job_dir = jobs / _asset('REAL_PHOTO')['asset_id']
    job = json.loads((job_dir / 'job.json').read_text(encoding='utf-8'))
    _write_external_result(job_dir, job, source_sha, capture=False)
    reviewed = ingest_provider_job_results(run, jobs)
    assert any(x['code'] == 'PRODUCTION_RECEIPT_CAPTURE_METADATA_MISSING' for x in reviewed['issues'])
    _write_external_result(job_dir, job, source_sha, capture=True)
    passed = ingest_provider_job_results(run, jobs)
    assert passed['status'] == 'COMPLETE'
