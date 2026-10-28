from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import re

from .models import stable_hash
from .provider_bridge import ExecutionPolicy
from .provider_surface import ProviderExecutionSurface, host_execution_contract

VERSION = '0.6.17-host-action-mapping'

ACTION_ADAPTER_LIST = 'cbcc.provider.adapters.list'
ACTION_EXECUTE = 'cbcc.provider.execute'
ACTION_STATUS = 'cbcc.provider.status'
ACTION_RESUME = 'cbcc.provider.resume'
ACTION_CANCEL = 'cbcc.provider.cancel'
ACTION_RECONCILE = 'cbcc.provider.reconcile'

SCOPE_ADAPTER_READ = 'PROVIDER_ADAPTER_READ'
SCOPE_STATUS_READ = 'PROVIDER_STATUS_READ'
SCOPE_EXECUTE = 'PROVIDER_EXECUTE'
SCOPE_CANCEL = 'PROVIDER_CANCEL'
SCOPE_RECONCILE = 'PROVIDER_RECONCILE'

_FORBIDDEN_SECRET_KEYS = {
    'api_key', 'apikey', 'api_token', 'token', 'access_token', 'refresh_token',
    'secret', 'client_secret', 'password', 'passwd', 'credentials', 'credential',
    'authorization', 'auth_header', 'authorization_header', 'bearer', 'private_key',
    'access_key', 'secret_key', 'aws_secret_access_key', 'session_token',
}


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return {} if default is None else default


def _normalize_key(value: Any) -> str:
    text = str(value or '').strip()
    text = re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text


def forbidden_secret_fields(payload: Any, prefix: str = '') -> list[str]:
    """Return forbidden credential-bearing field paths from an action payload.

    The policy is intentionally field based. Credential values belong to the v0.6.16 runtime-context
    resolver, never to host action/MCP/plugin JSON payloads.
    """
    found: list[str] = []
    if isinstance(payload, dict):
        for raw_key, value in payload.items():
            key = _normalize_key(raw_key)
            path = f'{prefix}.{raw_key}' if prefix else str(raw_key)
            if key in _FORBIDDEN_SECRET_KEYS:
                found.append(path)
            found.extend(forbidden_secret_fields(value, path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            path = f'{prefix}[{index}]' if prefix else f'[{index}]'
            found.extend(forbidden_secret_fields(value, path))
    return list(dict.fromkeys(found))


@dataclass(frozen=True)
class ActionAuthorization:
    actor_id: str = 'anonymous'
    scopes: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def from_scopes(cls, scopes: list[str] | tuple[str, ...] | set[str] | frozenset[str], *, actor_id: str = 'host') -> 'ActionAuthorization':
        return cls(actor_id=actor_id, scopes=frozenset(str(x).upper() for x in scopes))

    def allows(self, scope: str) -> bool:
        return str(scope).upper() in self.scopes


@dataclass(frozen=True)
class ActionDefinition:
    action_id: str
    title: str
    permission_scope: str
    mutation: bool
    long_running: bool
    input_schema: dict[str, Any]
    output_statuses: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            'version': VERSION,
            'action_id': self.action_id,
            'title': self.title,
            'permission_scope': self.permission_scope,
            'mutation': self.mutation,
            'long_running': self.long_running,
            'input_schema': self.input_schema,
            'output_statuses': list(self.output_statuses),
        }


def _string_prop(description: str) -> dict[str, Any]:
    return {'type': 'string', 'description': description}


def _array_string_prop(description: str) -> dict[str, Any]:
    return {'type': 'array', 'items': {'type': 'string'}, 'description': description}


def _object_schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        'type': 'object',
        'additionalProperties': False,
        'properties': properties,
        'required': list(required or []),
    }


_ACTIONS: dict[str, ActionDefinition] = {
    ACTION_ADAPTER_LIST: ActionDefinition(
        ACTION_ADAPTER_LIST,
        'List compatible provider adapters',
        SCOPE_ADAPTER_READ,
        False,
        False,
        _object_schema({
            'provider': _string_prop('Provider registry identifier.'),
            'production_mode': _string_prop('Production mode filter.'),
            'required_capabilities': _array_string_prop('Required adapter capabilities.'),
        }),
        ('SUCCEEDED', 'DENIED', 'INVALID_INPUT'),
    ),
    ACTION_EXECUTE: ActionDefinition(
        ACTION_EXECUTE,
        'Execute materialized provider jobs',
        SCOPE_EXECUTE,
        True,
        True,
        _object_schema({
            'project_dir': _string_prop('CBCC project directory already available to the host.'),
            'asset_ids': _array_string_prop('Optional asset subset; empty means all materialized provider jobs.'),
            'adapter_id': _string_prop('Optional explicit compatible adapter ID.'),
            'max_attempts': {'type': 'integer', 'minimum': 1, 'maximum': 20},
            'max_polls': {'type': 'integer', 'minimum': 0, 'maximum': 100},
        }, ['project_dir']),
        ('SUCCEEDED', 'PENDING', 'HOLD', 'FAILED', 'DENIED', 'INVALID_INPUT'),
    ),
    ACTION_STATUS: ActionDefinition(
        ACTION_STATUS,
        'Read provider operation status',
        SCOPE_STATUS_READ,
        False,
        False,
        _object_schema({
            'project_dir': _string_prop('CBCC project directory.'),
            'operation_id': _string_prop('Stable non-secret operation ID returned by execute/resume.'),
            'asset_ids': _array_string_prop('Operation asset scope returned by execute/resume.'),
        }, ['project_dir', 'operation_id', 'asset_ids']),
        ('SUCCEEDED', 'DENIED', 'INVALID_INPUT'),
    ),
    ACTION_RESUME: ActionDefinition(
        ACTION_RESUME,
        'Resume a pending provider operation',
        SCOPE_EXECUTE,
        True,
        True,
        _object_schema({
            'project_dir': _string_prop('CBCC project directory.'),
            'operation_id': _string_prop('Stable operation ID returned by execute.'),
            'asset_ids': _array_string_prop('Original operation asset scope.'),
            'adapter_id': _string_prop('Optional explicit compatible adapter ID.'),
            'max_attempts': {'type': 'integer', 'minimum': 1, 'maximum': 20},
            'max_polls': {'type': 'integer', 'minimum': 0, 'maximum': 100},
        }, ['project_dir', 'operation_id', 'asset_ids']),
        ('SUCCEEDED', 'PENDING', 'HOLD', 'FAILED', 'DENIED', 'INVALID_INPUT'),
    ),
    ACTION_CANCEL: ActionDefinition(
        ACTION_CANCEL,
        'Cancel an existing provider job',
        SCOPE_CANCEL,
        True,
        False,
        _object_schema({
            'project_dir': _string_prop('CBCC project directory.'),
            'asset_id': _string_prop('Asset ID whose existing external job should be cancelled.'),
            'adapter_id': _string_prop('Optional explicit compatible adapter ID.'),
            'reason': _string_prop('Operator-visible cancellation reason; never credential material.'),
        }, ['project_dir', 'asset_id']),
        ('SUCCEEDED', 'PENDING', 'HOLD', 'FAILED', 'DENIED', 'INVALID_INPUT'),
    ),
    ACTION_RECONCILE: ActionDefinition(
        ACTION_RECONCILE,
        'Reconcile persisted provider state with provider state',
        SCOPE_RECONCILE,
        True,
        False,
        _object_schema({
            'project_dir': _string_prop('CBCC project directory.'),
            'asset_id': _string_prop('Asset ID whose provider state should be reconciled.'),
            'adapter_id': _string_prop('Optional explicit compatible adapter ID.'),
        }, ['project_dir', 'asset_id']),
        ('SUCCEEDED', 'HOLD', 'FAILED', 'DENIED', 'INVALID_INPUT'),
    ),
}


def action_catalog() -> dict[str, Any]:
    actions = [definition.as_dict() for definition in _ACTIONS.values()]
    forbidden = sorted(_FORBIDDEN_SECRET_KEYS)
    return {
        'version': VERSION,
        'status': 'HOST_ACTION_CATALOG',
        'canonical_authority': 'ProviderExecutionSurface',
        'actions': actions,
        'authorization': {
            'default': 'DENY',
            'scopes': [SCOPE_ADAPTER_READ, SCOPE_STATUS_READ, SCOPE_EXECUTE, SCOPE_CANCEL, SCOPE_RECONCILE],
            'mutating_actions_require_explicit_scope': True,
        },
        'secret_boundary': {
            'credential_fields_forbidden': forbidden,
            'runtime_context_source': 'ProviderExecutionSurface runtime-context resolver only',
            'action_payload_credentials': 'FORBIDDEN',
        },
        'long_running': {
            'model': 'RESUME_EXISTING_PROVIDER_STATE',
            'separate_async_job_database': False,
            'state_authority': ['bridge_state.json', 'executor_state.json', 'result.json', 'production_run.json'],
        },
    }


def action_transport_manifest() -> dict[str, Any]:
    """Thin transport mappings. This declares names only; it does not claim an MCP/plugin server exists."""
    mappings = {
        ACTION_ADAPTER_LIST: {'mcp_tool_name': 'cbcc_provider_adapters_list', 'plugin_operation_id': 'cbccProviderAdaptersList'},
        ACTION_EXECUTE: {'mcp_tool_name': 'cbcc_provider_execute', 'plugin_operation_id': 'cbccProviderExecute'},
        ACTION_STATUS: {'mcp_tool_name': 'cbcc_provider_status', 'plugin_operation_id': 'cbccProviderStatus'},
        ACTION_RESUME: {'mcp_tool_name': 'cbcc_provider_resume', 'plugin_operation_id': 'cbccProviderResume'},
        ACTION_CANCEL: {'mcp_tool_name': 'cbcc_provider_cancel', 'plugin_operation_id': 'cbccProviderCancel'},
        ACTION_RECONCILE: {'mcp_tool_name': 'cbcc_provider_reconcile', 'plugin_operation_id': 'cbccProviderReconcile'},
    }
    return {
        'version': VERSION,
        'status': 'DECLARATIVE_THIN_MAPPING',
        'canonical_schema_source': 'action_catalog()',
        'runtime_implementation': 'ProviderActionDispatcher → ProviderExecutionSurface',
        'claims_mcp_server_exists': False,
        'claims_plugin_server_exists': False,
        'mappings': [{'action_id': action_id, **mapping} for action_id, mapping in mappings.items()],
    }


def _project_identity(project_dir: Path) -> str:
    state = _read_json(Path(project_dir) / '.cbcc/project_state.json', {})
    return str(state.get('project_id') or Path(project_dir).name)


def _selected_job_rows(project_dir: Path, asset_ids: list[str] | None = None) -> list[dict[str, Any]]:
    project = Path(project_dir)
    index = _read_json(project / 'artifacts/provider_jobs/PROVIDER_JOB_INDEX.json', {})
    selected = {str(x) for x in (asset_ids or []) if str(x)}
    rows = []
    for row in index.get('jobs') or []:
        aid = str(row.get('asset_id') or '')
        if selected and aid not in selected:
            continue
        rows.append(row)
    return rows


def operation_descriptor(project_dir: Path, asset_ids: list[str] | None = None) -> dict[str, Any]:
    rows = _selected_job_rows(Path(project_dir), asset_ids)
    scope = [
        {'asset_id': str(row.get('asset_id') or ''), 'job_id': str(row.get('job_id') or '')}
        for row in rows
    ]
    scope = sorted(scope, key=lambda row: (row['asset_id'], row['job_id']))
    project_id = _project_identity(Path(project_dir))
    operation_id = 'OP-' + stable_hash([VERSION, project_id, scope])[:24]
    return {
        'operation_id': operation_id,
        'project_id': project_id,
        'asset_ids': [row['asset_id'] for row in scope],
        'job_ids': [row['job_id'] for row in scope],
        'state_source': 'EXISTING_PROVIDER_JOB_STATE',
    }


def _classify_job_state(job_dir: Path, index_row: dict[str, Any]) -> dict[str, Any]:
    result_path = Path(str(index_row.get('result_path') or job_dir / 'result.json'))
    bridge = _read_json(job_dir / 'bridge_state.json', {})
    executor = _read_json(job_dir / 'executor_state.json', {})
    bridge_status = str(bridge.get('status') or '').upper()
    executor_status = str(executor.get('status') or executor.get('provider_status') or executor.get('phase') or '').upper()
    external_job_id = str(((executor.get('adapter_result') or {}).get('external_job_id')) or '') or None
    if result_path.exists():
        status = 'COMPLETE'
    elif bridge_status.startswith('CANCEL') or executor_status.startswith('CANCEL'):
        status = 'CANCELLED'
    elif bridge_status in {'FAILED_PERMANENT', 'RETRY_EXHAUSTED'} or executor_status in {'FAILED'}:
        status = 'FAILED'
    elif bridge_status in {'PENDING', 'RETRY_SCHEDULED', 'RUNNING'} or executor_status in {'PENDING', 'RUNNING', 'ACCEPTED', 'SUBMITTED'}:
        status = 'PENDING'
    elif bridge_status.startswith('HOLD'):
        status = 'HOLD'
    else:
        status = 'NOT_STARTED'
    return {
        'asset_id': str(index_row.get('asset_id') or ''),
        'job_id': str(index_row.get('job_id') or ''),
        'status': status,
        'bridge_status': bridge_status or None,
        'executor_status': executor_status or None,
        'external_job_id': external_job_id,
        'result_present': result_path.exists(),
    }


def read_operation_status(project_dir: Path, asset_ids: list[str], operation_id: str) -> dict[str, Any]:
    descriptor = operation_descriptor(Path(project_dir), asset_ids)
    if str(operation_id) != descriptor['operation_id']:
        return {
            'status': 'OPERATION_SCOPE_MISMATCH',
            'operation': descriptor,
            'jobs': [],
        }
    rows = _selected_job_rows(Path(project_dir), descriptor['asset_ids'])
    jobs_root = Path(project_dir) / 'artifacts/provider_jobs'
    jobs = [_classify_job_state(jobs_root / str(row.get('asset_id')), row) for row in rows]
    statuses = {row['status'] for row in jobs}
    if jobs and statuses == {'COMPLETE'}:
        overall = 'COMPLETE'
    elif 'FAILED' in statuses:
        overall = 'FAILED'
    elif 'HOLD' in statuses:
        overall = 'HOLD'
    elif 'CANCELLED' in statuses and statuses.issubset({'CANCELLED', 'COMPLETE'}):
        overall = 'CANCELLED'
    elif jobs and statuses.issubset({'COMPLETE', 'PENDING', 'NOT_STARTED'}):
        overall = 'PENDING'
    else:
        overall = 'PENDING' if jobs else 'EMPTY'
    production = _read_json(Path(project_dir) / 'artifacts/production_run.json', {})
    return {
        'status': overall,
        'operation': descriptor,
        'jobs': jobs,
        'production_status': production.get('status'),
        'read_only': True,
    }


def _validate_required_fields(definition: ActionDefinition, payload: dict[str, Any]) -> list[str]:
    missing = []
    for key in definition.input_schema.get('required') or []:
        if key not in payload or payload.get(key) in (None, ''):
            missing.append(str(key))
    extra = [str(key) for key in payload if key not in (definition.input_schema.get('properties') or {})]
    return [f'MISSING_REQUIRED:{key}' for key in missing] + [f'UNKNOWN_FIELD:{key}' for key in extra]


def _action_envelope(action_id: str, status: str, *, result: Any = None, errors: list[dict[str, Any]] | None = None, authorization: ActionAuthorization | None = None, operation: dict[str, Any] | None = None) -> dict[str, Any]:
    out = {
        'version': VERSION,
        'action_id': action_id,
        'status': status,
        'result': result,
        'errors': list(errors or []),
        'authorization': {
            'actor_id': (authorization.actor_id if authorization else None),
            'decision': 'ALLOW' if status != 'DENIED' else 'DENY',
        },
    }
    if operation is not None:
        out['operation'] = operation
    return out


class ProviderActionDispatcher:
    """Host-neutral dispatcher. It never instantiates executors or resolves credentials directly."""

    def __init__(self, surface: ProviderExecutionSurface) -> None:
        self.surface = surface

    def dispatch(self, action_id: str, payload: dict[str, Any] | None, authorization: ActionAuthorization | None = None) -> dict[str, Any]:
        definition = _ACTIONS.get(str(action_id))
        if definition is None:
            return _action_envelope(str(action_id), 'INVALID_INPUT', errors=[{'code': 'ACTION_NOT_REGISTERED'}], authorization=authorization)
        body = dict(payload or {})
        secret_fields = forbidden_secret_fields(body)
        if secret_fields:
            return _action_envelope(
                definition.action_id,
                'INVALID_INPUT',
                errors=[{'code': 'CREDENTIAL_FIELD_FORBIDDEN', 'fields': secret_fields}],
                authorization=authorization,
            )
        issues = _validate_required_fields(definition, body)
        if issues:
            return _action_envelope(
                definition.action_id,
                'INVALID_INPUT',
                errors=[{'code': issue} for issue in issues],
                authorization=authorization,
            )
        auth = authorization or ActionAuthorization()
        if not auth.allows(definition.permission_scope):
            return _action_envelope(
                definition.action_id,
                'DENIED',
                errors=[{'code': 'ACTION_SCOPE_REQUIRED', 'required_scope': definition.permission_scope}],
                authorization=auth,
            )
        try:
            return self._dispatch_authorized(definition, body, auth)
        except (FileNotFoundError, ValueError, KeyError, TypeError) as exc:
            return _action_envelope(
                definition.action_id,
                'FAILED',
                errors=[{'code': type(exc).__name__, 'message': str(exc)}],
                authorization=auth,
            )

    def _dispatch_authorized(self, definition: ActionDefinition, body: dict[str, Any], auth: ActionAuthorization) -> dict[str, Any]:
        action_id = definition.action_id
        if action_id == ACTION_ADAPTER_LIST:
            result = self.surface.list_adapters(
                provider=body.get('provider'),
                production_mode=body.get('production_mode'),
                required_capabilities=body.get('required_capabilities'),
            )
            return _action_envelope(action_id, 'SUCCEEDED', result=result, authorization=auth)

        if action_id == ACTION_STATUS:
            result = read_operation_status(Path(body['project_dir']), list(body.get('asset_ids') or []), str(body['operation_id']))
            status = 'SUCCEEDED' if result.get('status') != 'OPERATION_SCOPE_MISMATCH' else 'INVALID_INPUT'
            errors = [] if status == 'SUCCEEDED' else [{'code': 'OPERATION_SCOPE_MISMATCH'}]
            return _action_envelope(action_id, status, result=result, errors=errors, authorization=auth, operation=result.get('operation'))

        if action_id in {ACTION_EXECUTE, ACTION_RESUME}:
            project_dir = Path(body['project_dir'])
            asset_ids = list(body.get('asset_ids') or [])
            operation = operation_descriptor(project_dir, asset_ids)
            if action_id == ACTION_RESUME and str(body.get('operation_id')) != operation['operation_id']:
                return _action_envelope(action_id, 'INVALID_INPUT', errors=[{'code': 'OPERATION_SCOPE_MISMATCH'}], authorization=auth, operation=operation)
            policy = ExecutionPolicy(
                max_attempts=max(1, int(body.get('max_attempts') or 1)),
                max_polls_per_attempt=max(0, int(body.get('max_polls') if body.get('max_polls') is not None else 1)),
            )
            result = self.surface.execute_project(
                project_dir,
                asset_ids=operation['asset_ids'],
                adapter_id=body.get('adapter_id'),
                policy=policy,
            )
            status_read = read_operation_status(project_dir, operation['asset_ids'], operation['operation_id'])
            underlying = status_read.get('status')
            if underlying == 'COMPLETE':
                status = 'SUCCEEDED'
            elif underlying in {'PENDING', 'NOT_STARTED'}:
                status = 'PENDING'
            elif underlying == 'HOLD':
                status = 'HOLD'
            else:
                status = 'FAILED'
            result_payload = {
                'execution': result,
                'operation_status': status_read,
                'resume_action_id': ACTION_RESUME if status == 'PENDING' else None,
                'status_action_id': ACTION_STATUS,
            }
            return _action_envelope(action_id, status, result=result_payload, authorization=auth, operation=operation)

        if action_id == ACTION_CANCEL:
            project_dir = Path(body['project_dir'])
            asset_id = str(body['asset_id'])
            requested = self.surface.request_cancel(project_dir, asset_id, reason=body.get('reason'))
            cancelled = self.surface.cancel_project_job(project_dir, asset_id, adapter_id=body.get('adapter_id'))
            raw = str(cancelled.get('status') or '')
            if raw in {'CANCELLED', 'CANCELLED_BEFORE_SUBMIT', 'CANCEL_TOO_LATE_COMPLETED'}:
                status = 'SUCCEEDED'
            elif raw in {'CANCEL_PENDING', 'CANCEL_REQUESTED'}:
                status = 'PENDING'
            elif raw.startswith('CANCEL_HOLD') or raw == 'CANCEL_UNSUPPORTED':
                status = 'HOLD'
            else:
                status = 'FAILED'
            return _action_envelope(action_id, status, result={'request': requested, 'cancel': cancelled}, authorization=auth)

        if action_id == ACTION_RECONCILE:
            result = self.surface.reconcile_project_job(Path(body['project_dir']), str(body['asset_id']), adapter_id=body.get('adapter_id'))
            raw = str(result.get('status') or '')
            if raw == 'RECONCILED':
                status = 'SUCCEEDED'
            elif raw.startswith('RECONCILE_HOLD') or raw in {'RECONCILIATION_REQUIRED', 'RECONCILE_NO_EXTERNAL_JOB'}:
                status = 'HOLD'
            else:
                status = 'FAILED'
            return _action_envelope(action_id, status, result=result, authorization=auth)

        return _action_envelope(action_id, 'FAILED', errors=[{'code': 'ACTION_DISPATCH_UNREACHABLE'}], authorization=auth)


def host_action_contract() -> dict[str, Any]:
    return {
        'version': VERSION,
        'host_execution_surface': host_execution_contract(),
        'action_catalog': action_catalog(),
        'transport_manifest': action_transport_manifest(),
        'authority_rule': 'All provider action transports are thin wrappers over ProviderActionDispatcher → ProviderExecutionSurface. They must not instantiate a second provider runtime.',
    }
