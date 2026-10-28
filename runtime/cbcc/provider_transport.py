from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse
import hashlib
import re

from .models import stable_hash

VERSION = '0.6.13-provider-transport-integrity'
_EXECUTABLE_HANDLE_STATES = {'READY', 'ACTIVE', 'REFRESHED', 'DECLARED'}
_TERMINAL_HANDLE_STATES = {'EXPIRED', 'REVOKED', 'DELETED', 'INVALID'}
_REMOTE_SCHEMES = {'http', 'https', 's3', 'gs', 'azure', 'az', 'fixture', 'provider'}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _valid_sha(value: Any) -> bool:
    return bool(re.fullmatch(r'[0-9a-f]{64}', str(value or '').lower()))


def _parse_time(value: Any) -> datetime | None:
    if value in (None, ''):
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        if text.endswith('Z'):
            text = text[:-1] + '+00:00'
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _now(value: Any = None) -> datetime:
    return _parse_time(value) or datetime.now(timezone.utc)


def normalize_provider_asset_handle(
    raw: Any,
    *,
    source_sha256: str | None = None,
    default_provider: str | None = None,
    source_row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize legacy string handles and structured handle lifecycle metadata.

    A legacy string stays usable for backwards compatibility, but is labelled DECLARED rather than
    pretending that CBCC remotely verified provider existence or expiry.
    """
    source_row = source_row or {}
    if isinstance(raw, dict):
        handle_id = raw.get('handle_id') or raw.get('handle') or raw.get('id') or raw.get('value')
        provider = raw.get('provider') or source_row.get('provider_asset_provider') or default_provider
        state = str(raw.get('state') or source_row.get('provider_asset_state') or 'READY').upper()
        lifecycle = {
            'handle_id': handle_id,
            'provider': provider,
            'state': state,
            'content_sha256': str(raw.get('sha256') or source_sha256 or '').lower() or None,
            'issued_at': raw.get('issued_at') or source_row.get('provider_asset_issued_at'),
            'verified_at': raw.get('verified_at') or source_row.get('provider_asset_verified_at'),
            'expires_at': raw.get('expires_at') or source_row.get('provider_asset_expires_at'),
            'supersedes_handle': raw.get('supersedes_handle') or raw.get('previous_handle') or source_row.get('provider_asset_supersedes_handle'),
            'generation': raw.get('generation') or source_row.get('provider_asset_generation'),
            'legacy_declared': False,
        }
    else:
        handle_id = raw
        lifecycle = {
            'handle_id': handle_id,
            'provider': source_row.get('provider_asset_provider') or default_provider,
            'state': str(source_row.get('provider_asset_state') or 'DECLARED').upper(),
            'content_sha256': str(source_sha256 or '').lower() or None,
            'issued_at': source_row.get('provider_asset_issued_at'),
            'verified_at': source_row.get('provider_asset_verified_at'),
            'expires_at': source_row.get('provider_asset_expires_at'),
            'supersedes_handle': source_row.get('provider_asset_supersedes_handle'),
            'generation': source_row.get('provider_asset_generation'),
            'legacy_declared': True,
        }
    return lifecycle


def validate_provider_asset_binding(binding: dict[str, Any], now: Any = None) -> list[str]:
    locator = binding.get('locator') or {}
    if str(locator.get('kind') or '').upper() != 'PROVIDER_ASSET_HANDLE':
        return []
    issues: list[str] = []
    handle_id = locator.get('value')
    declared = str(binding.get('sha256') or binding.get('handoff_sha256') or '').lower()
    if not handle_id:
        issues.append('PROVIDER_ASSET_HANDLE_MISSING')
    if not _valid_sha(declared):
        issues.append('PROVIDER_ASSET_HANDLE_HASH_MISSING_OR_INVALID')

    lifecycle = binding.get('provider_asset_lifecycle') or {}
    if not isinstance(lifecycle, dict):
        lifecycle = {}
    lifecycle_handle = lifecycle.get('handle_id')
    if lifecycle_handle and str(lifecycle_handle) != str(handle_id):
        issues.append('PROVIDER_ASSET_HANDLE_ID_MISMATCH')
    lifecycle_sha = str(lifecycle.get('content_sha256') or '').lower()
    if lifecycle_sha and declared and lifecycle_sha != declared:
        issues.append('PROVIDER_ASSET_HANDLE_CONTENT_HASH_MISMATCH')

    state = str(lifecycle.get('state') or 'DECLARED').upper()
    if state in _TERMINAL_HANDLE_STATES:
        issues.append('PROVIDER_ASSET_HANDLE_' + state)
    elif state not in _EXECUTABLE_HANDLE_STATES:
        issues.append('PROVIDER_ASSET_HANDLE_STATE_NOT_EXECUTABLE')

    expires_raw = lifecycle.get('expires_at')
    if expires_raw not in (None, ''):
        expires = _parse_time(expires_raw)
        if expires is None:
            issues.append('PROVIDER_ASSET_HANDLE_EXPIRY_INVALID')
        elif expires <= _now(now):
            issues.append('PROVIDER_ASSET_HANDLE_EXPIRED')

    supersedes = lifecycle.get('supersedes_handle')
    if supersedes and str(supersedes) == str(handle_id):
        issues.append('PROVIDER_ASSET_HANDLE_REFRESH_SELF_REFERENCE')
    return list(dict.fromkeys(issues))


def validate_provider_asset_refresh(previous: dict[str, Any], current: dict[str, Any], now: Any = None) -> list[str]:
    """Validate a refresh/re-upload without requiring the predecessor to still be unexpired."""
    issues = validate_provider_asset_binding(current, now=now)
    prev_locator = previous.get('locator') or {}
    cur_locator = current.get('locator') or {}
    if str(prev_locator.get('kind') or '').upper() != 'PROVIDER_ASSET_HANDLE' or str(cur_locator.get('kind') or '').upper() != 'PROVIDER_ASSET_HANDLE':
        issues.append('PROVIDER_ASSET_REFRESH_LOCATOR_KIND_INVALID')
        return list(dict.fromkeys(issues))
    prev_handle = str(prev_locator.get('value') or '')
    cur_handle = str(cur_locator.get('value') or '')
    if not prev_handle or not cur_handle or prev_handle == cur_handle:
        issues.append('PROVIDER_ASSET_REFRESH_HANDLE_NOT_ROTATED')
    if previous.get('asset_id') and current.get('asset_id') and previous.get('asset_id') != current.get('asset_id'):
        issues.append('PROVIDER_ASSET_REFRESH_ASSET_ID_MISMATCH')
    prev_sha = str(previous.get('sha256') or previous.get('handoff_sha256') or '').lower()
    cur_sha = str(current.get('sha256') or current.get('handoff_sha256') or '').lower()
    if prev_sha != cur_sha:
        issues.append('PROVIDER_ASSET_REFRESH_CONTENT_HASH_CHANGED')
    prev_lifecycle = previous.get('provider_asset_lifecycle') or {}
    cur_lifecycle = current.get('provider_asset_lifecycle') or {}
    prev_provider = prev_lifecycle.get('provider')
    cur_provider = cur_lifecycle.get('provider')
    if prev_provider and cur_provider and prev_provider != cur_provider:
        issues.append('PROVIDER_ASSET_REFRESH_PROVIDER_MISMATCH')
    if str(cur_lifecycle.get('supersedes_handle') or '') != prev_handle:
        issues.append('PROVIDER_ASSET_REFRESH_LINEAGE_MISSING')
    return list(dict.fromkeys(issues))


def adapter_profile_for(adapter: str | None, provider: str | None = None, override: dict[str, Any] | None = None) -> dict[str, Any]:
    if override:
        return dict(override)
    adapter_name = str(adapter or 'FILE_HANDOFF').upper()
    if adapter_name == 'EXTERNAL_ADAPTER':
        return {
            'profile_id': 'CBCC_EXTERNAL_PROVIDER_V1',
            'adapter': 'EXTERNAL_ADAPTER',
            'provider': provider,
            'operation': 'SUBMIT_PROVIDER_JOB',
            'field_map': {
                'client_job_id': 'job_id',
                'asset_id': 'asset_id',
                'production_mode': 'production_mode',
                'input_package': 'package_ref',
                'source_assets': 'source_product_bindings',
                'instructions': 'execution_brief',
                'result_contract': 'result_contract',
                'receipt_contract': 'production_receipt_contract',
            },
            'required_vendor_response_fields': ['external_job_id', 'status'],
            'status_map': {
                'QUEUED': 'ACCEPTED', 'PENDING': 'ACCEPTED', 'ACCEPTED': 'ACCEPTED',
                'RUNNING': 'RUNNING', 'IN_PROGRESS': 'RUNNING',
                'SUCCEEDED': 'SUCCEEDED', 'COMPLETED': 'SUCCEEDED',
                'FAILED': 'FAILED', 'CANCELLED': 'FAILED',
            },
        }
    return {
        'profile_id': 'CBCC_FILE_HANDOFF_V1',
        'adapter': 'FILE_HANDOFF',
        'provider': provider,
        'operation': 'FILE_JOB_EXCHANGE',
        'field_map': {
            'job_id': 'job_id',
            'asset_id': 'asset_id',
            'package_ref': 'package_ref',
            'source_assets': 'source_product_bindings',
            'result_contract': 'result_contract',
        },
        'required_vendor_response_fields': [],
        'status_map': {},
    }


def _get_path(value: Any, dotted_path: str) -> Any:
    node = value
    for part in str(dotted_path or '').split('.'):
        if not part:
            continue
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def build_adapter_transmission(job: dict[str, Any], adapter_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    profile = adapter_profile_for(job.get('adapter'), job.get('provider'), adapter_profile)
    field_map = profile.get('field_map') or {}
    mapped = {vendor_field: _get_path(job, source_path) for vendor_field, source_path in field_map.items()}
    missing = [field for field, value in mapped.items() if value is None]
    request_hash = stable_hash(mapped)
    idempotency_key = 'IDEMP-' + stable_hash([
        job.get('job_id'), job.get('provider'), job.get('package_hash'), job.get('source_binding_hash'),
        profile.get('profile_id'), request_hash,
    ])[:24]
    transmission_id = 'TX-' + stable_hash([idempotency_key, request_hash])[:20]
    return {
        'version': VERSION,
        'status': 'READY' if not missing else 'HOLD',
        'transmission_id': transmission_id,
        'adapter': profile.get('adapter'),
        'provider': job.get('provider'),
        'profile_id': profile.get('profile_id'),
        'operation': profile.get('operation'),
        'idempotency_key': idempotency_key,
        'request_hash': request_hash,
        'vendor_request': mapped,
        'field_map': field_map,
        'mapping_errors': [{'field': field, 'code': 'ADAPTER_SOURCE_FIELD_MISSING'} for field in missing],
        'external_job_contract': {
            'required': list(profile.get('required_vendor_response_fields') or []),
            'status_map': dict(profile.get('status_map') or {}),
            'binding_fields': ['transmission_id', 'request_hash', 'idempotency_key'],
        },
        'authority_rule': 'This envelope maps frozen CBCC job fields to an adapter request. It does not claim that an external API call occurred.',
    }


def adapter_result_template(transmission: dict[str, Any]) -> dict[str, Any]:
    return {
        'transmission_id': transmission.get('transmission_id'),
        'request_hash': transmission.get('request_hash'),
        'idempotency_key': transmission.get('idempotency_key'),
        'external_job_id': '',
        'status': '',
        'provider_response_ref': None,
    }


def validate_adapter_result(row: dict[str, Any], result: dict[str, Any]) -> list[str]:
    contract = row.get('provider_contract') or {}
    adapter = str(contract.get('adapter') or '').upper()
    portable_transmission = row.get('provider_adapter_transmission') or {}
    execution_transmission = result.get('provider_execution_transmission')
    transmission = execution_transmission if isinstance(execution_transmission, dict) else portable_transmission
    if adapter != 'EXTERNAL_ADAPTER' and str(portable_transmission.get('adapter') or '').upper() != 'EXTERNAL_ADAPTER':
        return []
    issues: list[str] = []
    if not portable_transmission:
        return ['ADAPTER_TRANSMISSION_CONTRACT_MISSING']
    if portable_transmission.get('status') != 'READY':
        issues.append('ADAPTER_TRANSMISSION_NOT_READY')

    if isinstance(execution_transmission, dict):
        parent = execution_transmission.get('parent_transmission_binding') or {}
        for key in ['transmission_id', 'request_hash', 'idempotency_key']:
            if parent.get(key) != portable_transmission.get(key):
                issues.append('ADAPTER_EXECUTION_PARENT_BINDING_MISMATCH:' + key)
        vendor_request = execution_transmission.get('vendor_request') or {}
        if stable_hash(vendor_request) != execution_transmission.get('request_hash'):
            issues.append('ADAPTER_EXECUTION_REQUEST_HASH_MISMATCH')
        if execution_transmission.get('portable_source_binding_hash') and row.get('provider_job_source_binding_hash') and execution_transmission.get('portable_source_binding_hash') != row.get('provider_job_source_binding_hash'):
            issues.append('ADAPTER_EXECUTION_PORTABLE_SOURCE_BINDING_MISMATCH')
        if execution_transmission.get('status') != 'READY':
            issues.append('ADAPTER_EXECUTION_TRANSMISSION_NOT_READY')

    ack = result.get('adapter_result')
    if not isinstance(ack, dict):
        return list(dict.fromkeys(issues + ['ADAPTER_RESULT_MISSING']))
    for key in ['transmission_id', 'request_hash', 'idempotency_key']:
        if ack.get(key) != transmission.get(key):
            issues.append('ADAPTER_RESULT_BINDING_MISMATCH:' + key)
    if not ack.get('external_job_id'):
        issues.append('ADAPTER_EXTERNAL_JOB_ID_MISSING')
    raw_status = str(ack.get('status') or '').upper()
    if not raw_status:
        issues.append('ADAPTER_EXTERNAL_STATUS_MISSING')
    else:
        status_map = (transmission.get('external_job_contract') or {}).get('status_map') or {}
        normalized = status_map.get(raw_status)
        if not normalized:
            issues.append('ADAPTER_EXTERNAL_STATUS_UNMAPPED')
        elif normalized == 'FAILED':
            issues.append('ADAPTER_EXTERNAL_JOB_FAILED')
    return list(dict.fromkeys(issues))


def _resolve_remote_bytes(locator: str, resolver: Callable[..., Any]) -> bytes:
    try:
        value = resolver(locator)
    except TypeError:
        value = resolver(locator, None)
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, Path):
        return value.read_bytes()
    if isinstance(value, str):
        path = Path(value)
        if path.exists() and path.is_file():
            return path.read_bytes()
        raise ValueError('resolver returned a non-file string')
    if isinstance(value, dict):
        if isinstance(value.get('bytes'), (bytes, bytearray)):
            return bytes(value['bytes'])
        if value.get('path'):
            return Path(str(value['path'])).read_bytes()
    raise ValueError('resolver did not return bytes or a readable local path')


def verify_artifact_reference(
    artifact: dict[str, Any],
    *,
    base_dir: Path | None = None,
    resolver: Callable[..., Any] | None = None,
    require_remote_verification: bool = False,
) -> dict[str, Any]:
    locator = artifact.get('path_or_uri') or artifact.get('path') or artifact.get('uri')
    declared = str(artifact.get('sha256') or '').lower()
    if not locator or not _valid_sha(declared):
        return {'status': 'INVALID', 'issues': ['PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_INVALID']}
    text = str(locator)
    parsed = urlparse(text)
    is_remote = bool(parsed.scheme and parsed.scheme.lower() in _REMOTE_SCHEMES) or '://' in text
    if not is_remote:
        rel = Path(text)
        if rel.is_absolute():
            return {'status': 'INVALID', 'issues': ['PRODUCTION_RECEIPT_OUTPUT_PATH_NOT_PORTABLE']}
        if base_dir is None:
            return {'status': 'DECLARED_LOCAL_HASH', 'sha256': declared, 'issues': []}
        target = Path(base_dir) / rel
        if not target.exists() or not target.is_file():
            return {'status': 'MISSING', 'issues': ['PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_MISSING']}
        actual = _sha256_file(target)
        if actual != declared:
            return {'status': 'HASH_MISMATCH', 'sha256': actual, 'issues': ['PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_HASH_MISMATCH']}
        return {'status': 'VERIFIED_LOCAL', 'sha256': actual, 'issues': []}

    if not require_remote_verification:
        return {'status': 'DECLARED_REMOTE_HASH', 'sha256': declared, 'issues': []}
    if resolver is None:
        return {'status': 'UNVERIFIED_REMOTE', 'issues': ['PRODUCTION_RECEIPT_REMOTE_ARTIFACT_UNVERIFIED']}
    try:
        data = _resolve_remote_bytes(text, resolver)
    except Exception:
        return {'status': 'RESOLVE_FAILED', 'issues': ['PRODUCTION_RECEIPT_REMOTE_ARTIFACT_RESOLVE_FAILED']}
    actual = _sha256_bytes(data)
    if actual != declared:
        return {'status': 'HASH_MISMATCH', 'sha256': actual, 'issues': ['PRODUCTION_RECEIPT_REMOTE_ARTIFACT_HASH_MISMATCH']}
    return {'status': 'VERIFIED_REMOTE', 'sha256': actual, 'bytes': len(data), 'issues': []}


def recover_remote_artifact(
    artifact: dict[str, Any],
    resolver: Callable[..., Any],
    recovery_dir: Path,
) -> dict[str, Any]:
    """Resolve remote bytes, verify declared SHA256, and persist a deterministic recovery copy."""
    check = verify_artifact_reference(artifact, resolver=resolver, require_remote_verification=True)
    if check.get('status') != 'VERIFIED_REMOTE':
        return check
    locator = str(artifact.get('path_or_uri') or artifact.get('uri') or '')
    data = _resolve_remote_bytes(locator, resolver)
    declared = str(artifact.get('sha256')).lower()
    suffix = Path(urlparse(locator).path).suffix or '.bin'
    target_dir = Path(recovery_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f'recovered-{declared[:16]}{suffix}'
    if not target.exists():
        target.write_bytes(data)
    actual = _sha256_file(target)
    if actual != declared:
        return {'status': 'RECOVERY_HASH_MISMATCH', 'issues': ['PRODUCTION_RECEIPT_REMOTE_ARTIFACT_RECOVERY_HASH_MISMATCH']}
    return {
        'status': 'RECOVERED_VERIFIED',
        'path': str(target),
        'sha256': actual,
        'recovered_from_uri': locator,
        'issues': [],
    }
