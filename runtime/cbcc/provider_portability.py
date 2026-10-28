from __future__ import annotations
from pathlib import Path
from typing import Any
import hashlib, json, re, shutil

from .models import stable_hash

VERSION = '0.6.12-portable-provider-package-production-receipt'
_CAPTURE_METADATA_MODES = {'REAL_PHOTO', 'VIDEO?}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _safe_name(value: Any) -> str:
    return re.sub(r'[^A-Za-z0-9._-]+', '-', str(value or 'source')).strip('-') or 'source'


def _file_manifest(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(p for p in Path(root).rglob('*') if p.is_file()):
        rows.append({
            'path': path.relative_to(root).as_posix(),
            'sha256': _sha256_file(path),
            'bytes': path.stat().st_size,
        })
    return rows


def materialize_portable_job_inputs(package_dir: Path, job_dir: Path, source_bindings: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Create a self-contained provider input envelope.

    The frozen asset package is copied unchanged for package-hash lineage. Local source masters are
    copied into the job and rebound to PACKAGE_RELATIVE_PATH. Provider handles remain handles.
    No execution binding in job.json needs the CBCC host's absolute filesystem path.
    """
    package_dir = Path(package_dir)
    job_dir = Path(job_dir)
    inputs = job_dir / 'inputs'
    frozen = inputs / 'asset_package'
    masters = inputs / 'product_masters'
    if frozen.exists():
        shutil.rmtree(frozen)
    frozen.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(package_dir, frozen)
    masters.mkdir(parents=True, exist_ok=True)

    portable = []
    errors = []
    upstream = list(source_bindings or [])
    for row in upstream:
        if not isinstance(row, dict):
            continue
        binding = json.loads(json.dumps(row))
        locator = binding.get('locator') or {}
        kind = str(locator.get('kind') or '').upper()
        value = locator.get('value')
        declared = str(binding.get('sha256') or binding.get('handoff_sha256') or '').lower()
        aid = binding.get('asset_id')
        if kind == 'LOCAL_FILE_PATH':
            src = Path(str(value or '')).expanduser()
            if not src.exists() or not src.is_file():
                errors.append({'asset_id': aid, 'code': 'PORTABLE_SOURCE_PATH_MISSING'})
                continue
            actual = _sha256_file(src)
            if not declared or actual != declared:
                errors.append({'asset_id': aid, 'code': 'PORTABLE_SOURCE_HASH_MISMATCH' if declared else 'PORTABLE_SOURCE_HASH_MISSING'})
                continue
            suffix = src.suffix if src.suffix else '.bin'
            dest = masters / f"{_safe_name(aid)}-{actual[:10]}{suffix}"
            if not dest.exists():
                shutil.copy2(src, dest)
            copied = _sha256_file(dest)
            if copied != actual:
                errors.append({'asset_id': aid, 'code': 'PORTABLE_SOURCE_COPY_HASH_MISMATCH'})
                continue
            binding['upstream_locator_kind'] = 'LOCAL_FILE_PATH'
            binding['locator'] = {'kind': 'PACKAGE_RELATIVE_PATH', 'value': dest.relative_to(job_dir).as_posix()}
            binding['handoff_status'] = 'READY_PACKAGE_VERIFIED'
            binding['handoff_sha256'] = copied
        elif kind == 'PROVIDER_ASSET_HANDLE':
            if not value or not declared:
                errors.append({'asset_id': aid, 'code': 'PORTABLE_PROVIDER_HANDLE_INCOMPLETE'})
                continue
            binding['handoff_status'] = 'READY_PROVIDER_HANDLE_VERIFIED'
            binding['handoff_sha256'] = declared
        elif kind == 'PACKAGE_RELATIVE_PATH':
            rel = Path(str(value or ''))
            src = job_dir / rel
            if rel.is_absolute() or not src.exists() or not src.is_file():
                errors.append({'asset_id': aid, 'code': 'PORTABLE_RELATIVE_SOURCE_UNRESOLVED'})
                continue
            actual = _sha256_file(src)
            if declared and actual != declared:
                errors.append({'asset_id': aid, 'code': 'PORTABLE_SOURCE_HASH_MISMATCH'})
                continue
            binding['handoff_status'] = 'READY_PACKAGE_VERIFIED'
            binding['handoff_sha256'] = actual
        else:
            errors.append({'asset_id': aid, 'code': 'PORTABLE_SOURCE_UNRESOLVED'})
            continue
        portable.append(binding)

    payload = {
        'version': VERSION,
        'status': 'READY' if not errors else 'HOLD',
        'asset_package': {
            'locator': {'kind': 'PACKAGE_RELATIVE_PATH', 'value': 'inputs/asset_package'},
            'files': _file_manifest(frozen),
        },
        'source_product_bindings': portable,
        'upstream_source_binding_hash': stable_hash(upstream),
        'portable_source_binding_hash': stable_hash(portable),
        'errors': errors,
        'portability_rule': 'Execution resources are resolved from this job directory or an explicit provider asset handle; host absolute paths are not execution locators.',
    }
    manifest_hash = stable_hash(payload)
    payload['portable_manifest_hash'] = manifest_hash
    (job_dir / 'PORTABLE_JOB_MANIFEST.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return payload


def build_production_receipt_contract(job_id: str, asset_id: str, provider: str, package_hash: str, source_binding_hash: str | None, production_mode: str, product_fidelity: str, portable_manifest_hash: str) -> dict[str, Any]:
    mode = str(production_mode or '').upper()
    fidelity = str(product_fidelity or '').upper()
    required = ['job_id', 'asset_id', 'provider', 'package_hash', 'portable_manifest_hash', 'output_artifacts']
    if fidelity == 'LOCKED_PIXEL':
        required += ['source_binding_hash', 'layer_manifest']
    if mode in _CAPTURE_METADATA_MODES:
        required += ['capture_metadata']
    return {
        'version': VERSION,
        'required': required,
        'expected': {
            'job_id': job_id,
            'asset_id': asset_id,
            'provider': provider,
            'package_hash': package_hash,
            'portable_manifest_hash': portable_manifest_hash,
            'source_binding_hash': source_binding_hash,
        },
        'output_artifact_contract': {'required_fields': ['path_or_uri', 'sha256'], 'local_paths_must_be_job_relative': True},
        'layer_manifest_contract': {
            'required': fidelity == 'LOCKED_PIXEL',
            'product_layer_required_fields': ['source_asset_id', 'source_sha256', 'operation', 'frozen'],
            'rule': 'Every reported locked product layer must resolve to a bound source master and preserve its SHA256 lineage.',
        },
        'capture_metadata_contract': {
            'required': mode in _CAPTURE_METADATA_MODES,
            'required_fields': ['capture_type'],
            'rule': 'Describe actual capture/render provenance without inventing EXIF or camera metadata that was not produced.',
        },
    }


def production_receipt_template(contract: dict[str, Any]) -> dict[str, Any]:
    expected = contract.get('expected') or {}
    receipt = {
        'job_id': expected.get('job_id'),
        'asset_id': expected.get('asset_id'),
        'provider': expected.get('provider'),
        'package_hash': expected.get('package_hash'),
        'portable_manifest_hash': expected.get('portable_manifest_hash'),
        'source_binding_hash': expected.get('source_binding_hash'),
        'output_artifacts': [],
        'layer_manifest': [],
        'capture_metadata': {},
    }
    return receipt


def validate_production_receipt(row: dict[str, Any], result: dict[str, Any]) -> list[str]:
    """Validate portable external-provider receipt lineage.

    Inline/internal results remain backward-compatible. Results ingested from materialized provider
    jobs are marked `_provider_job_ingest` and must carry a receipt.
    """
    external = bool(result.get('_provider_job_ingest'))
    receipt = result.get('production_receipt')
    if not receipt:
        return ['PRODUCTION_RECEIPT_MISSING'] if external else []
    if not isinstance(receipt, dict):
        return ['PRODUCTION_RECEIPT_INVALID']

    issues = []
    expected = {
        'job_id': row.get('provider_job_id'),
        'asset_id': row.get('asset_id'),
        'provider': row.get('provider'),
        'package_hash': row.get('package_hash'),
        'portable_manifest_hash': row.get('portable_job_manifest_hash'),
    }
    qc = row.get('production_quality_contract') or {}
    if str(qc.get('product_fidelity') or '').upper() == 'LOCKED_PIXEL':
        expected['source_binding_hash'] = qc.get('source_binding_hash')
    for key, value in expected.items():
        if value is not None and receipt.get(key) != value:
            issues.append('PRODUCTION_RECEIPT_BINDING_MISMATCH:' + key)

    artifacts = receipt.get('output_artifacts')
    if not isinstance(artifacts, list) or not artifacts:
        issues.append('PRODUCTION_RECEIPT_OUTPUT_ARTIFACTS_MISSING')
    else:
        base_raw = result.get('_provider_job_dir')
        base = Path(str(base_raw)) if base_raw else None
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                issues.append('PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_INVALID')
                continue
            locator = artifact.get('path_or_uri') or artifact.get('path') or artifact.get('uri')
            declared = str(artifact.get('sha256') or '').lower()
            if not locator or not re.fullmatch(r'[0-9a-f]{64}', declared):
                issues.append('PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_INVALID')
                continue
            if base and artifact.get('uri') is None and '://' not in str(locator):
                rel = Path(str(locator))
                if rel.is_absolute():
                    issues.append('PRODUCTION_RECEIPT_OUTPUT_PATH_NOT_PORTABLE')
                    continue
                target = base / rel
                if not target.exists() or not target.is_file():
                    issues.append('PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_MISSING')
                elif _sha256_file(target) != declared:
                    issues.append('PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_HASH_MISMATCH')

    fidelity = str(qc.get('product_fidelity') or '').upper()
    if fidelity == 'LOCKED_PIXEL':
        layers = receipt.get('layer_manifest')
        if not isinstance(layers, list) or not layers:
            issues.append('PRODUCTION_RECEIPT_LAYER_MANIFEST_MISSING')
        else:
            expected_hashes = {str(x.get('asset_id')): str(x.get('sha256') or '') for x in qc.get('source_product_bindings') or [] if x.get('asset_id')}
            used = set((result.get('quality_observations') or {}).get('source_product_asset_ids_used') or [])
            matched = set()
            for layer in layers:
                if not isinstance(layer, dict) or not layer.get('source_asset_id'):
                    continue
                aid = str(layer.get('source_asset_id'))
                if aid in expected_hashes:
                    matched.add(aid)
                    if str(layer.get('source_sha256') or '') != expected_hashes[aid]:
                        issues.append('PRODUCTION_RECEIPT_PRODUCT_LAYER_HASH_MISMATCH')
                    if layer.get('frozen') is not True:
                        issues.append('PRODUCTION_RECEIPT_PRODUCT_LAYER_NOT_FROZEN')
                    if not layer.get('operation'):
                        issues.append('PRODUCTION_RECEIPT_PRODUCT_LAYER_OPERATION_MISSING')
            if used and not used.issubset(matched):
                issues.append('PRODUCTION_RECEIPT_PRODUCT_LAYER_LINEAGE_MISSING')

    mode = str(row.get('production_mode') or '').upper()
    if mode in _CAPTURE_METADATA_MODES:
        metadata = receipt.get('capture_metadata')
        if not isinstance(metadata, dict) or not metadata.get('capture_type'):
            issues.append('PRODUCTION_RECEIPT_CAPTURE_METADATA_MISSING')

    return list(dict.fromkeys(issues))
