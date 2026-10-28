from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
import importlib
import json
import os

from .provider_bridge import (
    ExecutionPolicy,
    ProviderAdapterRegistry,
    ProviderExecutorBridge,
    bridge_contract,
    build_default_adapter_registry,
)
from .production import ingest_provider_job_results
from .review import materialize_review_workspace
from .state import ProjectState

VERSION = '0.6.16-provider-host-execution-surface'
HOST_MODULE_ENV = 'CBCC_PROVIDER_HOST_MODULE'
REFERENCE_ADAPTER_ENV = 'CBCC_PROVIDER_ENABLE_REFERENCE'

RuntimeContextResolver = Callable[[str, Path, dict[str, Any]], dict[str, Any] | None]


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return {} if default is None else default


def _write_json(path: Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def host_execution_contract() -> dict[str, Any]:
    return {
        'version': VERSION,
        'commands': ['adapter-list', 'provider-execute', 'provider-cancel', 'provider-reconcile'],
        'single_execution_chain': bridge_contract()['single_execution_chain'],
        'runtime_context': {
            'persistence': 'FORBIDDEN',
            'cli_secret_arguments': 'FORBIDDEN',
            'host_module_environment_variable': HOST_MODULE_ENV,
            'host_module_value_is_module_name_not_credentials': True,
            'credential_ownership': 'HOST',
        },
        'completion_authority': 'Existing ingest_provider_job_results + ProjectState PRODUCTION gate',
    }


class ProviderExecutionSurface:
    """Host-safe operational surface over ProviderAdapterRegistry + ProviderExecutorBridge.

    Runtime credentials/clients/callbacks are obtained lazily through context_resolver and are never
    written to project artifacts or returned in command payloads.
    """

    def __init__(
        self,
        registry: ProviderAdapterRegistry,
        *,
        context_resolver: RuntimeContextResolver | None = None,
        bridge: ProviderExecutorBridge | None = None,
    ) -> None:
        self.registry = registry
        self.context_resolver = context_resolver
        self.bridge = bridge or ProviderExecutorBridge(registry)

    def list_adapters(
        self,
        *,
        provider: str | None = None,
        production_mode: str | None = None,
        required_capabilities: list[str] | None = None,
    ) -> dict[str, Any]:
        rows = self.registry.discover(
            provider=provider,
            production_mode=production_mode,
            required_capabilities=required_capabilities,
        )
        return {
            'status': 'ADAPTERS_DISCOVERED',
            'count': len(rows),
            'adapters': rows,
            'host_execution_contract': host_execution_contract(),
        }

    def _context_for(self, adapter: dict[str, Any], job_dir: Path, job: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
        metadata = adapter.get('metadata') or {}
        required = bool(metadata.get('runtime_context_required'))
        if self.context_resolver is None:
            return ({}, None) if not required else (None, 'RUNTIME_CONTEXT_RESOLVER_NOT_CONFIGURED')
        context = self.context_resolver(str(adapter.get('adapter_id') or ''), Path(job_dir), job)
        if context is None:
            return (None, 'RUNTIME_CONTEXT_UNAVAILABLE') if required else ({}, None)
        if not isinstance(context, dict):
            return None, 'RUNTIME_CONTEXT_INVALID'
        return context, None

    def _project_paths(self, project_dir: Path) -> tuple[Path, Path, Path]:
        project = Path(project_dir)
        return project, project / 'artifacts/provider_jobs', project / 'artifacts/production_run.json'

    def _job_index(self, jobs_root: Path) -> dict[str, Any]:
        index = _read_json(jobs_root / 'PROVIDER_JOB_INDEX.json', {})
        if not index:
            raise FileNotFoundError(f'No provider job index found: {jobs_root / "PROVIDER_JOB_INDEX.json"}')
        return index

    def _execute_one(
        self,
        job_dir: Path,
        *,
        adapter_id: str | None,
        policy: ExecutionPolicy,
    ) -> dict[str, Any]:
        job = _read_json(job_dir / 'job.json', {})
        if not job:
            return {'status': 'FAILED_PERMANENT', 'error_code': 'JOB_JSON_MISSING'}
        resolution = self.bridge.resolve_adapter(job_dir, adapter_id=adapter_id)
        if resolution.get('status') != 'READY':
            return {'status': resolution.get('status'), 'resolution': resolution}
        selected = resolution['selected']
        context, issue = self._context_for(selected, job_dir, job)
        if issue:
            return {
                'status': 'HOLD_RUNTIME_CONTEXT',
                'error_code': issue,
                'adapter_id': selected.get('adapter_id'),
            }
        return self.bridge.execute(
            job_dir,
            runtime_context=context,
            adapter_id=str(selected.get('adapter_id')),
            policy=policy,
        )

    def execute_project(
        self,
        project_dir: Path,
        *,
        asset_ids: list[str] | None = None,
        adapter_id: str | None = None,
        policy: ExecutionPolicy | None = None,
        ingest_when_complete: bool = True,
    ) -> dict[str, Any]:
        project, jobs_root, run_path = self._project_paths(Path(project_dir))
        index = self._job_index(jobs_root)
        selected_ids = set(asset_ids or [])
        policy = policy or ExecutionPolicy()
        rows = []
        for row in index.get('jobs') or []:
            aid = str(row.get('asset_id') or '')
            if selected_ids and aid not in selected_ids:
                continue
            outcome = self._execute_one(jobs_root / aid, adapter_id=adapter_id, policy=policy)
            rows.append({'asset_id': aid, 'provider': row.get('provider'), **outcome})

        counts: dict[str, int] = {}
        for row in rows:
            status = str(row.get('status') or 'UNKNOWN')
            counts[status] = counts.get(status, 0) + 1
        all_selected_complete = bool(rows) and all(x.get('status') == 'COMPLETE' for x in rows)
        indexed_jobs = list(index.get('jobs') or [])
        all_results_present = bool(indexed_jobs) and all(
            bool(x.get('result_path')) and Path(str(x['result_path'])).exists()
            for x in indexed_jobs
        )

        ingest = None
        if ingest_when_complete and all_selected_complete and all_results_present and run_path.exists():
            run = _read_json(run_path, {})
            ingest = ingest_provider_job_results(run, jobs_root)
            _write_json(run_path, ingest)
            try:
                state = ProjectState.load(project)
                state.set_gate(
                    'PRODUCTION',
                    'READY_REVIEW' if ingest.get('status') == 'COMPLETE' else 'PENDING',
                    [str(run_path), str(jobs_root / 'PROVIDER_JOB_INDEX.json')],
                    ingest,
                )
                state.checkpoint('PROVIDER_EXECUTION_SURFACE', ingest.get('status'))
                materialize_review_workspace(project, state.data)
            except FileNotFoundError:
                pass

        return {
            'status': 'PROVIDER_EXECUTION_COMPLETE' if all_selected_complete else ('NO_PROVIDER_JOBS_SELECTED' if not rows else 'PROVIDER_EXECUTION_INCOMPLETE'),
            'jobs': rows,
            'counts': counts,
            'ingest': ingest,
            'ingest_status': (ingest or {}).get('status') if ingest else ('DEFERRED_UNTIL_ALL_RESULTS_PRESENT' if ingest_when_complete else 'SKIPPED'),
            'host_execution_contract': host_execution_contract(),
        }

    def request_cancel(self, project_dir: Path, asset_id: str, *, reason: str | None = None) -> dict[str, Any]:
        _, jobs_root, _ = self._project_paths(Path(project_dir))
        return self.bridge.request_cancel(jobs_root / str(asset_id), reason=reason)

    def cancel_project_job(
        self,
        project_dir: Path,
        asset_id: str,
        *,
        adapter_id: str | None = None,
    ) -> dict[str, Any]:
        _, jobs_root, _ = self._project_paths(Path(project_dir))
        job_dir = jobs_root / str(asset_id)
        job = _read_json(job_dir / 'job.json', {})
        resolution = self.bridge.resolve_adapter(job_dir, adapter_id=adapter_id)
        if resolution.get('status') != 'READY':
            return {'status': resolution.get('status'), 'resolution': resolution}
        context, issue = self._context_for(resolution['selected'], job_dir, job)
        if issue:
            return {'status': 'HOLD_RUNTIME_CONTEXT', 'error_code': issue, 'adapter_id': resolution['selected'].get('adapter_id')}
        return self.bridge.cancel(job_dir, runtime_context=context, adapter_id=str(resolution['selected'].get('adapter_id')))

    def reconcile_project_job(
        self,
        project_dir: Path,
        asset_id: str,
        *,
        adapter_id: str | None = None,
    ) -> dict[str, Any]:
        _, jobs_root, _ = self._project_paths(Path(project_dir))
        job_dir = jobs_root / str(asset_id)
        job = _read_json(job_dir / 'job.json', {})
        resolution = self.bridge.resolve_adapter(job_dir, adapter_id=adapter_id)
        if resolution.get('status') != 'READY':
            return {'status': resolution.get('status'), 'resolution': resolution}
        context, issue = self._context_for(resolution['selected'], job_dir, job)
        if issue:
            return {'status': 'HOLD_RUNTIME_CONTEXT', 'error_code': issue, 'adapter_id': resolution['selected'].get('adapter_id')}
        return self.bridge.reconcile(job_dir, runtime_context=context, adapter_id=str(resolution['selected'].get('adapter_id')))


def _load_host_module(module_name: str, registry: ProviderAdapterRegistry) -> RuntimeContextResolver | None:
    module = importlib.import_module(module_name)
    register = getattr(module, 'register_adapters', None)
    if callable(register):
        register(registry)
    resolver = getattr(module, 'create_runtime_context', None)
    if resolver is None:
        return None
    if not callable(resolver):
        raise TypeError('host module create_runtime_context must be callable')

    def _resolve(adapter_id: str, job_dir: Path, job: dict[str, Any]) -> dict[str, Any] | None:
        return resolver(adapter_id=adapter_id, job_dir=job_dir, job=job)

    return _resolve


def provider_execution_surface_from_environment(*, env: dict[str, str] | None = None) -> ProviderExecutionSurface:
    values = os.environ if env is None else env
    include_reference = str(values.get(REFERENCE_ADAPTER_ENV) or '').strip().lower() in {'1', 'true', 'yes'}
    registry = build_default_adapter_registry(include_reference=include_reference)
    module_name = str(values.get(HOST_MODULE_ENV) or '').strip()
    resolver = _load_host_module(module_name, registry) if module_name else None
    return ProviderExecutionSurface(registry, context_resolver=resolver)
