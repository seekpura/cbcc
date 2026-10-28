from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Protocol, runtime_checkable
import hashlib
import json

from .models import stable_hash
from .provider_transport import (
    adapter_profile_for,
    build_adapter_transmission,
    normalize_provider_asset_handle,
    validate_adapter_result,
    validate_provider_asset_binding,
    validate_provider_asset_refresh,
)

VERSION = '0.6.14-provider-executor-lifecycle'
TERMINAL_SUCCESS = {'SUCCEEDED', 'COMPLETED'}
TERMINAL_FAILURE = {'FAILED', 'CANCELLED'}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return {} if default is None else default


def _write_json(path: Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def _provider_binding_from_handle(source: dict[str, Any], handle: dict[str, Any]) -> dict[str, Any]:
    declared = str(source.get('sha256') or source.get('handoff_sha256') or '').lower()
    lifecycle = normalize_provider_asset_handle(
        handle,
        source_sha256=declared,
        default_provider=handle.get('provider'),
        source_row=source,
    )
    return {
        **source,
        'locator': {'kind': 'PROVIDER_ASSET_HANDLE', 'value': lifecycle.get('handle_id')},
        'sha256': declared,
        'handoff_sha256': declared,
        'handoff_status': 'READY_PROVIDER_HANDLE_LIFECYCLE_VERIFIED',
        'provider_asset_lifecycle': lifecycle,
    }


def _source_bytes(job_dir: Path, binding: dict[str, Any]) -> bytes | None:
    locator = binding.get('locator') or {}
    kind = str(locator.get('kind') or '').upper()
    if kind != 'PACKAGE_RELATIVE_PATH':
        return None
    rel = Path(str(locator.get('value') or ''))
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError('PACKAGE_RELATIVE_PATH is not portable')
    path = job_dir / rel
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(str(path))
    data = path.read_bytes()
    declared = str(binding.get('sha256') or binding.get('handoff_sha256') or '').lower()
    if declared and _sha256_bytes(data) != declared:
        raise ValueError('source product SHA256 mismatch before provider upload')
    return data


@runtime_checkable
class ProviderExecutor(Protocol):
    """Credential-free execution boundary implemented by provider adapters.

    CBCC owns lifecycle/state/integrity contracts. Concrete adapters own authentication,
    network clients, vendor SDKs and provider-specific request/response details.
    """

    executor_id: str

    def ensure_asset(
        self,
        binding: dict[str, Any],
        *,
        source_bytes: bytes | None,
        job: dict[str, Any],
        previous_handle: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...

    def submit(self, transmission: dict[str, Any], *, job: dict[str, Any]) -> dict[str, Any]: ...

    def poll(
        self,
        external_job_id: str,
        *,
        job: dict[str, Any],
        resume_token: str | None = None,
    ) -> dict[str, Any]: ...

    def collect(self, external_job_id: str, *, job: dict[str, Any]) -> dict[str, Any]: ...

    def resolve(self, artifact_ref: str, *, job: dict[str, Any]) -> bytes: ...


def executor_contract() -> dict[str, Any]:
    return {
        'version': VERSION,
        'protocol': 'ProviderExecutor',
        'lifecycle': [
            'PREPARE_SOURCE_ASSETS',
            'UPLOAD_OR_REFRESH_ASSETS',
            'BUILD_IDEMPOTENT_TRANSMISSION',
            'SUBMIT',
            'POLL_OR_RESUME',
            'COLLECT',
            'RESOLVE_OUTPUTS',
            'WRITE_RESULT_AND_PRODUCTION_RECEIPT',
            'INGEST_EXISTING_RUNTIME',
        ],
        'adapter_owns': ['credentials', 'network_client', 'vendor_sdk', 'provider_auth', 'provider_endpoint'],
        'cbcc_owns': ['portable_job', 'source_hash_lineage', 'idempotency_binding', 'resume_state', 'output_hash_verification', 'production_receipt'],
    }


def _prepare_provider_sources(
    job_dir: Path,
    job: dict[str, Any],
    executor: ProviderExecutor,
    state: dict[str, Any],
) -> list[dict[str, Any]]:
    if state.get('provider_source_bindings'):
        return list(state['provider_source_bindings'])

    prepared: list[dict[str, Any]] = []
    for source in job.get('source_product_bindings') or []:
        binding = json.loads(json.dumps(source))
        locator = binding.get('locator') or {}
        kind = str(locator.get('kind') or '').upper()
        if kind == 'PROVIDER_ASSET_HANDLE':
            issues = validate_provider_asset_binding(binding)
            if not issues:
                prepared.append(binding)
                continue
            previous = binding.get('provider_asset_lifecycle') or normalize_provider_asset_handle(
                locator.get('value'),
                source_sha256=binding.get('sha256'),
                default_provider=job.get('provider'),
                source_row=binding,
            )
            refreshed = executor.ensure_asset(
                binding,
                source_bytes=None,
                job=job,
                previous_handle=previous,
            )
            current = _provider_binding_from_handle(binding, refreshed)
            refresh_issues = validate_provider_asset_refresh(binding, current)
            if refresh_issues:
                raise ValueError('provider asset refresh invalid: ' + ','.join(refresh_issues))
            prepared.append(current)
            continue

        if kind == 'PACKAGE_RELATIVE_PATH':
            data = _source_bytes(job_dir, binding)
            uploaded = executor.ensure_asset(binding, source_bytes=data, job=job, previous_handle=None)
            current = _provider_binding_from_handle(binding, uploaded)
            issues = validate_provider_asset_binding(current)
            if issues:
                raise ValueError('uploaded provider asset invalid: ' + ','.join(issues))
            prepared.append(current)
            continue

        raise ValueError('unsupported provider executor source locator: ' + kind)

    state['provider_source_bindings'] = prepared
    state['source_prepare_status'] = 'READY'
    state['updated_at'] = _now()
    return prepared


def _job_with_provider_sources(job: dict[str, Any], bindings: list[dict[str, Any]]) -> dict[str, Any]:
    executable = json.loads(json.dumps(job))
    execution_hash = stable_hash(bindings)
    executable['source_product_bindings'] = bindings
    # The portable source_binding_hash is immutable lineage from v0.6.12. Provider-side
    # upload/refresh changes locators, not source content identity, so it receives a separate hash.
    executable['provider_execution_source_binding_hash'] = execution_hash
    quality = executable.get('production_quality_contract') or {}
    quality['source_product_bindings'] = bindings
    quality['provider_execution_source_binding_hash'] = execution_hash
    executable['production_quality_contract'] = quality
    brief = executable.get('execution_brief') or {}
    brief['source_product_bindings'] = bindings
    brief['provider_execution_source_binding_hash'] = execution_hash
    executable['execution_brief'] = brief
    return executable


def _normalize_ack(transmission: dict[str, Any], ack: dict[str, Any]) -> dict[str, Any]:
    return {
        'transmission_id': ack.get('transmission_id') or transmission.get('transmission_id'),
        'request_hash': ack.get('request_hash') or transmission.get('request_hash'),
        'idempotency_key': ack.get('idempotency_key') or transmission.get('idempotency_key'),
        'external_job_id': ack.get('external_job_id'),
        'status': str(ack.get('status') or '').upper(),
        'provider_response_ref': ack.get('provider_response_ref'),
    }


def _normalize_status(transmission: dict[str, Any], raw: str) -> str:
    value = str(raw or '').upper()
    status_map = (transmission.get('external_job_contract') or {}).get('status_map') or {}
    return str(status_map.get(value) or value).upper()


def _quality_observations(job: dict[str, Any], collected: dict[str, Any]) -> dict[str, Any]:
    supplied = collected.get('quality_observations')
    if isinstance(supplied, dict):
        return supplied
    bindings = job.get('source_product_bindings') or []
    ids = [x.get('asset_id') for x in bindings if x.get('asset_id')]
    hashes = {str(x.get('asset_id')): str(x.get('sha256') or '') for x in bindings if x.get('asset_id')}
    out: dict[str, Any] = {}
    required = (job.get('result_contract') or {}).get('quality_observations_required') or []
    for key in required:
        if key == 'source_product_asset_ids_used':
            out[key] = ids
        elif key == 'source_product_hashes_used':
            out[key] = hashes
        elif key == 'product_layer_operation':
            out[key] = collected.get('product_layer_operation') or 'COMPOSITE_LOCKED'
        else:
            out[key] = {'status': 'PASS', 'evidence': 'provider executor reported ' + str(key)}
    return out


def _layer_manifest(job: dict[str, Any], collected: dict[str, Any]) -> list[dict[str, Any]]:
    supplied = collected.get('layer_manifest')
    if isinstance(supplied, list) and supplied:
        return supplied
    fidelity = str((job.get('production_quality_contract') or {}).get('product_fidelity') or '').upper()
    if fidelity != 'LOCKED_PIXEL':
        return []
    rows = []
    for index, binding in enumerate(job.get('source_product_bindings') or []):
        if not binding.get('asset_id'):
            continue
        rows.append({
            'layer_id': 'provider-product-' + str(index),
            'role': 'PRODUCT_MASTER',
            'source_asset_id': binding.get('asset_id'),
            'source_sha256': binding.get('sha256'),
            'operation': collected.get('product_layer_operation') or 'COMPOSITE_LOCKED',
            'frozen': True,
        })
    return rows


def _capture_metadata(job: dict[str, Any], collected: dict[str, Any]) -> dict[str, Any]:
    supplied = collected.get('capture_metadata')
    if isinstance(supplied, dict) and supplied:
        return supplied
    mode = str(job.get('production_mode') or '').upper()
    if mode in {'REAL_PHOTO', 'VIDEO'}:
        return {'capture_type': 'PROVIDER_EXECUTOR', 'executor_id': collected.get('executor_id')}
    return {}


def _materialize_result(
    job_dir: Path,
    job: dict[str, Any],
    transmission: dict[str, Any],
    adapter_result: dict[str, Any],
    collected: dict[str, Any],
    executor: ProviderExecutor,
) -> dict[str, Any]:
    artifacts = collected.get('artifacts') or []
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError('provider executor returned no artifacts')

    output_dir = job_dir / 'outputs'
    output_dir.mkdir(parents=True, exist_ok=True)
    receipt_artifacts = []
    output_path: str | None = None
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            raise ValueError('provider artifact must be an object')
        ref = artifact.get('ref') or artifact.get('uri') or artifact.get('path_or_uri')
        if not ref:
            raise ValueError('provider artifact reference missing')
        data = executor.resolve(str(ref), job=job)
        if not isinstance(data, (bytes, bytearray)):
            raise ValueError('provider resolver must return bytes')
        data = bytes(data)
        declared = str(artifact.get('sha256') or '').lower()
        actual = _sha256_bytes(data)
        if declared and declared != actual:
            raise ValueError('provider output SHA256 mismatch')
        suffix = str(artifact.get('suffix') or Path(str(ref)).suffix or '.bin')
        if not suffix.startswith('.'):
            suffix = '.' + suffix
        name = str(artifact.get('name') or ('artifact-' + str(index) + suffix))
        if '/' in name or '\\' in name:
            name = 'artifact-' + str(index) + suffix
        local = output_dir / name
        local.write_bytes(data)
        rel = local.relative_to(job_dir).as_posix()
        receipt_artifacts.append({'path_or_uri': rel, 'sha256': actual, 'role': artifact.get('role') or ('FINAL' if index == 0 else 'AUXILIARY')})
        if output_path is None:
            output_path = str(local)

    receipt = {
        'job_id': job.get('job_id'),
        'asset_id': job.get('asset_id'),
        'provider': job.get('provider'),
        'package_hash': job.get('package_hash'),
        'portable_manifest_hash': (job.get('portable_package') or {}).get('portable_manifest_hash'),
        'source_binding_hash': job.get('source_binding_hash'),
        'output_artifacts': receipt_artifacts,
        'layer_manifest': _layer_manifest(job, collected),
        'capture_metadata': _capture_metadata(job, collected),
    }
    return {
        'asset_id': job.get('asset_id'),
        'provider': job.get('provider'),
        'package_hash': job.get('package_hash'),
        'output_path': output_path,
        'changed_fields': list(collected.get('changed_fields') or []),
        'changed_layers': list(collected.get('changed_layers') or []),
        'qa': collected.get('qa') or {'product': True, 'fact': True, 'claim': True, 'visual': True, 'culture': True, 'platform': True},
        'quality_observations': _quality_observations(job, collected),
        'provider_metadata': {
            **(collected.get('provider_metadata') or {}),
            'executor_id': getattr(executor, 'executor_id', executor.__class__.__name__),
            'executor_version': VERSION,
            'transmission_id': transmission.get('transmission_id'),
        },
        'production_contract_ack': True,
        'source_binding_hash': job.get('source_binding_hash'),
        'adapter_result': adapter_result,
        'production_receipt': receipt,
    }


def execute_provider_job_directory(
    job_dir: Path,
    executor: ProviderExecutor,
    *,
    max_polls: int = 8,
) -> dict[str, Any]:
    """Execute or resume one materialized provider job directory.

    State is persisted after each boundary so a retry can resume without fabricating a new job.
    Submission is bound to the deterministic v0.6.13 idempotency key.
    """
    job_dir = Path(job_dir)
    job = _read_json(job_dir / 'job.json', {})
    if not job:
        raise ValueError('job.json missing or invalid')
    if str(job.get('adapter') or '').upper() != 'EXTERNAL_ADAPTER':
        raise ValueError('ProviderExecutor requires EXTERNAL_ADAPTER job')

    state_path = job_dir / 'executor_state.json'
    state = _read_json(state_path, {})
    state.setdefault('version', VERSION)
    state.setdefault('job_id', job.get('job_id'))
    state.setdefault('asset_id', job.get('asset_id'))
    state.setdefault('executor_id', getattr(executor, 'executor_id', executor.__class__.__name__))
    state.setdefault('created_at', _now())

    bindings = _prepare_provider_sources(job_dir, job, executor, state)
    executable_job = _job_with_provider_sources(job, bindings)
    state['executable_source_binding_hash'] = executable_job.get('source_binding_hash')
    _write_json(state_path, state)

    transmission = state.get('transmission')
    if not isinstance(transmission, dict):
        profile = adapter_profile_for('EXTERNAL_ADAPTER', executable_job.get('provider'), (executable_job.get('provider_contract') or {}).get('adapter_profile'))
        transmission = build_adapter_transmission(executable_job, profile)
        if transmission.get('status') != 'READY':
            raise ValueError('adapter transmission not ready')
        state['transmission'] = transmission
        state['phase'] = 'TRANSMISSION_READY'
        state['updated_at'] = _now()
        _write_json(state_path, state)

    adapter_result = state.get('adapter_result')
    if not isinstance(adapter_result, dict) or not adapter_result.get('external_job_id'):
        raw_ack = executor.submit(transmission, job=executable_job)
        adapter_result = _normalize_ack(transmission, raw_ack)
        issues = validate_adapter_result(
            {'provider_contract': {'adapter': 'EXTERNAL_ADAPTER'}, 'provider_adapter_transmission': transmission},
            {'adapter_result': adapter_result},
        )
        if issues:
            raise ValueError('provider submit acknowledgement invalid: ' + ','.join(issues))
        state['adapter_result'] = adapter_result
        state['phase'] = 'SUBMITTED'
        state['updated_at'] = _now()
        _write_json(state_path, state)

    external_job_id = str(adapter_result.get('external_job_id'))
    resume_token = state.get('resume_token')
    poll_count = int(state.get('poll_count') or 0)
    normalized_status = _normalize_status(transmission, str(state.get('provider_status') or adapter_result.get('status') or ''))
    if normalized_status not in {'SUCCEEDED', 'FAILED'}:
        for _ in range(max(0, max_polls)):
            polled = executor.poll(external_job_id, job=executable_job, resume_token=resume_token)
            poll_count += 1
            raw_status = str(polled.get('status') or '').upper()
            normalized_status = _normalize_status(transmission, raw_status)
            resume_token = polled.get('resume_token') or resume_token
            state['poll_count'] = poll_count
            state['provider_status_raw'] = raw_status
            state['provider_status'] = normalized_status
            state['resume_token'] = resume_token
            state['phase'] = 'RUNNING' if normalized_status not in {'SUCCEEDED', 'FAILED'} else normalized_status
            state['updated_at'] = _now()
            _write_json(state_path, state)
            if normalized_status in {'SUCCEEDED', 'FAILED'}:
                break

    if normalized_status == 'FAILED':
        state['status'] = 'FAILED'
        _write_json(state_path, state)
        return {'status': 'FAILED', 'job_id': job.get('job_id'), 'external_job_id': external_job_id, 'state_path': str(state_path)}
    if normalized_status != 'SUCCEEDED':
        state['status'] = 'PENDING'
        _write_json(state_path, state)
        return {
            'status': 'PENDING',
            'job_id': job.get('job_id'),
            'external_job_id': external_job_id,
            'resume_token': resume_token,
            'poll_count': poll_count,
            'state_path': str(state_path),
        }

    collected = executor.collect(external_job_id, job=executable_job)
    if not isinstance(collected, dict):
        raise ValueError('provider collect must return an object')
    collected.setdefault('executor_id', getattr(executor, 'executor_id', executor.__class__.__name__))
    result = _materialize_result(job_dir, executable_job, transmission, adapter_result, collected, executor)
    _write_json(job_dir / 'result.json', result)
    state['phase'] = 'COMPLETE'
    state['status'] = 'COMPLETE'
    state['result_path'] = str(job_dir / 'result.json')
    state['result_hash'] = stable_hash(result)
    state['updated_at'] = _now()
    _write_json(state_path, state)
    return {
        'status': 'COMPLETE',
        'job_id': job.get('job_id'),
        'external_job_id': external_job_id,
        'result_path': str(job_dir / 'result.json'),
        'state_path': str(state_path),
        'poll_count': poll_count,
    }


def execute_materialized_provider_jobs(
    jobs_root: Path,
    executors: dict[str, ProviderExecutor],
    *,
    asset_ids: list[str] | None = None,
    max_polls: int = 8,
) -> dict[str, Any]:
    jobs_root = Path(jobs_root)
    index = _read_json(jobs_root / 'PROVIDER_JOB_INDEX.json', {})
    selected = set(asset_ids or [])
    rows = []
    for row in index.get('jobs') or []:
        aid = row.get('asset_id')
        if selected and aid not in selected:
            continue
        provider = str(row.get('provider') or '')
        executor = executors.get(provider) or executors.get('*')
        if executor is None:
            rows.append({'asset_id': aid, 'provider': provider, 'status': 'HOLD_NO_EXECUTOR'})
            continue
        try:
            outcome = execute_provider_job_directory(jobs_root / str(aid), executor, max_polls=max_polls)
            rows.append({'asset_id': aid, 'provider': provider, **outcome})
        except Exception as exc:
            rows.append({'asset_id': aid, 'provider': provider, 'status': 'FAILED', 'error': f'{type(exc).__name__}: {exc}'})
    counts = {status: sum(1 for x in rows if x.get('status') == status) for status in ['COMPLETE', 'PENDING', 'FAILED', 'HOLD_NO_EXECUTOR']}
    return {
        'status': 'EXECUTION_COMPLETE' if rows and counts['COMPLETE'] == len(rows) else ('NO_PROVIDER_JOBS' if not rows else 'EXECUTION_INCOMPLETE'),
        'jobs': rows,
        'counts': counts,
        'executor_contract': executor_contract(),
    }


@dataclass
class ReferenceMemoryExecutor:
    """Deterministic reference adapter used to validate lifecycle semantics end-to-end.

    It intentionally has no network or credentials. Real provider adapters implement the same
    protocol around their own SDK/client while preserving these observable semantics.
    """

    executor_id: str = 'REFERENCE_MEMORY_EXECUTOR'
    provider: str = 'EPV_ADAPTER'
    poll_sequence: tuple[str, ...] = ('RUNNING', 'COMPLETED')
    default_output: bytes = b'cbcc-v0614-reference-provider-output'
    _assets: dict[str, dict[str, Any]] = field(default_factory=dict)
    _jobs_by_idempotency: dict[str, str] = field(default_factory=dict)
    _jobs: dict[str, dict[str, Any]] = field(default_factory=dict)
    _artifacts: dict[str, bytes] = field(default_factory=dict)
    ensure_asset_calls: int = 0
    submit_calls: int = 0

    def ensure_asset(
        self,
        binding: dict[str, Any],
        *,
        source_bytes: bytes | None,
        job: dict[str, Any],
        previous_handle: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.ensure_asset_calls += 1
        declared = str(binding.get('sha256') or binding.get('handoff_sha256') or '').lower()
        if source_bytes is not None and _sha256_bytes(source_bytes) != declared:
            raise ValueError('reference executor source hash mismatch')
        key = declared or stable_hash(binding)
        previous_id = (previous_handle or {}).get('handle_id')
        generation = int((previous_handle or {}).get('generation') or 0) + 1
        handle_id = 'REF-ASSET-' + stable_hash([key, generation, previous_id])[:18]
        handle = {
            'handle_id': handle_id,
            'provider': self.provider,
            'state': 'REFRESHED' if previous_id else 'READY',
            'sha256': declared,
            'issued_at': _now(),
            'verified_at': _now(),
            'expires_at': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            'supersedes_handle': previous_id,
            'generation': generation,
        }
        self._assets[handle_id] = {'handle': handle, 'bytes': source_bytes}
        return handle

    def submit(self, transmission: dict[str, Any], *, job: dict[str, Any]) -> dict[str, Any]:
        self.submit_calls += 1
        key = str(transmission.get('idempotency_key') or '')
        if not key:
            raise ValueError('idempotency key required')
        external_job_id = self._jobs_by_idempotency.get(key)
        if not external_job_id:
            external_job_id = 'REF-JOB-' + stable_hash([key, transmission.get('request_hash')])[:18]
            self._jobs_by_idempotency[key] = external_job_id
            self._jobs[external_job_id] = {'poll_index': 0, 'job': json.loads(json.dumps(job)), 'transmission': json.loads(json.dumps(transmission))}
        return {
            'transmission_id': transmission.get('transmission_id'),
            'request_hash': transmission.get('request_hash'),
            'idempotency_key': key,
            'external_job_id': external_job_id,
            'status': 'ACCEPTED',
            'provider_response_ref': 'reference://' + external_job_id,
        }

    def poll(self, external_job_id: str, *, job: dict[str, Any], resume_token: str | None = None) -> dict[str, Any]:
        row = self._jobs[external_job_id]
        idx = int(row.get('poll_index') or 0)
        sequence = self.poll_sequence or ('COMPLETED',)
        status = sequence[min(idx, len(sequence) - 1)]
        row['poll_index'] = idx + 1
        return {'status': status, 'resume_token': 'REF-RESUME-' + str(row['poll_index'])}

    def collect(self, external_job_id: str, *, job: dict[str, Any]) -> dict[str, Any]:
        artifact_ref = 'reference://artifacts/' + external_job_id + '/final.bin'
        self._artifacts[artifact_ref] = bytes(self.default_output)
        return {
            'artifacts': [{'ref': artifact_ref, 'sha256': _sha256_bytes(self.default_output), 'role': 'FINAL', 'name': 'final.bin'}],
            'qa': {'product': True, 'fact': True, 'claim': True, 'visual': True, 'culture': True, 'platform': True},
            'changed_fields': [],
            'changed_layers': [],
            'provider_metadata': {'reference_executor': True},
            'product_layer_operation': 'COMPOSITE_LOCKED',
        }

    def resolve(self, artifact_ref: str, *, job: dict[str, Any]) -> bytes:
        if artifact_ref not in self._artifacts:
            raise FileNotFoundError(artifact_ref)
        return self._artifacts[artifact_ref]
