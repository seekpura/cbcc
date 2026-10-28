from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
import json

from .host_actions import (
    VERSION as ACTION_VERSION,
    ActionAuthorization,
    ProviderActionDispatcher,
    action_catalog,
    action_transport_manifest,
    forbidden_secret_fields,
)
from .models import stable_hash

VERSION = '0.6.18-transport-descriptor-parity'


def _action_index() -> dict[str, dict[str, Any]]:
    return {str(row['action_id']): row for row in action_catalog()['actions']}


def _mapping_index() -> dict[str, dict[str, Any]]:
    return {str(row['action_id']): row for row in action_transport_manifest()['mappings']}


def mcp_tool_descriptors() -> list[dict[str, Any]]:
    """Generate MCP-style tool descriptors from the canonical v0.6.17 action catalog.

    This is a descriptor generator only. It does not claim or start an MCP server.
    """
    actions = _action_index()
    mappings = _mapping_index()
    tools = []
    for action_id in sorted(actions):
        action = actions[action_id]
        mapping = mappings[action_id]
        tools.append({
            'name': mapping['mcp_tool_name'],
            'description': action['title'],
            'inputSchema': deepcopy(action['input_schema']),
            'x-cbcc-action-id': action_id,
            'x-cbcc-permission-scope': action['permission_scope'],
            'x-cbcc-long-running': bool(action['long_running']),
            'x-cbcc-mutation': bool(action['mutation']),
        })
    return tools


def _plugin_path(action_id: str) -> str:
    slug = action_id.replace('cbcc.provider.', '').replace('.', '-')
    return '/actions/provider/' + slug


def plugin_openapi_descriptor(*, title: str = 'CBCC Provider Actions', server_url: str = '/') -> dict[str, Any]:
    """Generate an OpenAPI 3.1 descriptor suitable for a thin Plugin/Actions transport.

    `server_url` is a transport deployment placeholder. The document deliberately defines no
    credential-bearing request fields or embedded authentication secret schema. Authorization is
    injected by the host as ActionAuthorization outside the canonical action payload.
    """
    actions = _action_index()
    mappings = _mapping_index()
    paths: dict[str, Any] = {}
    for action_id in sorted(actions):
        action = actions[action_id]
        mapping = mappings[action_id]
        paths[_plugin_path(action_id)] = {
            'post': {
                'operationId': mapping['plugin_operation_id'],
                'summary': action['title'],
                'x-cbcc-action-id': action_id,
                'x-cbcc-permission-scope': action['permission_scope'],
                'x-cbcc-long-running': bool(action['long_running']),
                'x-cbcc-mutation': bool(action['mutation']),
                'x-cbcc-authorization-source': 'HOST_OUT_OF_BAND_ACTION_AUTHORIZATION',
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': deepcopy(action['input_schema']),
                        }
                    },
                },
                'responses': {
                    '200': {
                        'description': 'Canonical CBCC ProviderActionDispatcher envelope.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'required': ['version', 'action_id', 'status', 'errors', 'authorization'],
                                    'properties': {
                                        'version': {'type': 'string'},
                                        'action_id': {'type': 'string'},
                                        'status': {'type': 'string'},
                                        'result': {},
                                        'errors': {'type': 'array', 'items': {'type': 'object'}},
                                        'authorization': {
                                            'type': 'object',
                                            'properties': {
                                                'actor_id': {'type': ['string', 'null']},
                                                'decision': {'type': 'string'},
                                            },
                                        },
                                        'operation': {'type': 'object'},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        }
    return {
        'openapi': '3.1.0',
        'info': {
            'title': title,
            'version': VERSION,
            'description': 'Generated thin transport descriptor over the canonical CBCC provider action catalog.',
        },
        'servers': [{'url': server_url}],
        'paths': paths,
        'x-cbcc-canonical-action-version': ACTION_VERSION,
        'x-cbcc-runtime': 'ProviderActionDispatcher',
        'x-cbcc-credential-payload-fields': 'FORBIDDEN',
        'x-cbcc-transport-owns-provider-runtime': False,
    }


def _openapi_operations(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path, path_item in (document.get('paths') or {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if str(method).lower() not in {'get', 'post', 'put', 'patch', 'delete'} or not isinstance(operation, dict):
                continue
            action_id = operation.get('x-cbcc-action-id')
            if action_id:
                rows[str(action_id)] = {'path': path, 'method': str(method).upper(), **operation}
    return rows


def descriptor_parity_report(
    *,
    mcp_tools: list[dict[str, Any]] | None = None,
    plugin_openapi: dict[str, Any] | None = None,
) -> dict[str, Any]:
    canonical = _action_index()
    mappings = _mapping_index()
    mcp_tools = deepcopy(mcp_tools) if mcp_tools is not None else mcp_tool_descriptors()
    plugin_openapi = deepcopy(plugin_openapi) if plugin_openapi is not None else plugin_openapi_descriptor()
    mcp_by_action = {str(row.get('x-cbcc-action-id')): row for row in mcp_tools if row.get('x-cbcc-action-id')}
    plugin_by_action = _openapi_operations(plugin_openapi)
    issues: list[dict[str, Any]] = []
    rows = []

    for action_id in sorted(canonical):
        action = canonical[action_id]
        mapping = mappings[action_id]
        canonical_schema = action['input_schema']
        canonical_hash = stable_hash(canonical_schema)
        mcp = mcp_by_action.get(action_id)
        plugin = plugin_by_action.get(action_id)
        if mcp is None:
            issues.append({'action_id': action_id, 'code': 'MCP_DESCRIPTOR_MISSING'})
        if plugin is None:
            issues.append({'action_id': action_id, 'code': 'PLUGIN_DESCRIPTOR_MISSING'})
        mcp_schema = (mcp or {}).get('inputSchema')
        plugin_schema = (((plugin or {}).get('requestBody') or {}).get('content') or {}).get('application/json', {}).get('schema')
        if mcp is not None:
            if mcp.get('name') != mapping['mcp_tool_name']:
                issues.append({'action_id': action_id, 'code': 'MCP_NAME_DRIFT'})
            if mcp_schema != canonical_schema:
                issues.append({'action_id': action_id, 'code': 'MCP_SCHEMA_DRIFT'})
            if mcp.get('x-cbcc-permission-scope') != action['permission_scope']:
                issues.append({'action_id': action_id, 'code': 'MCP_AUTH_SCOPE_DRIFT'})
            secret_fields = forbidden_secret_fields(mcp_schema or {})
            if secret_fields:
                issues.append({'action_id': action_id, 'code': 'MCP_CREDENTIAL_FIELD_PRESENT', 'fields': secret_fields})
        if plugin is not None:
            if plugin.get('operationId') != mapping['plugin_operation_id']:
                issues.append({'action_id': action_id, 'code': 'PLUGIN_OPERATION_ID_DRIFT'})
            if plugin_schema != canonical_schema:
                issues.append({'action_id': action_id, 'code': 'PLUGIN_SCHEMA_DRIFT'})
            if plugin.get('x-cbcc-permission-scope') != action['permission_scope']:
                issues.append({'action_id': action_id, 'code': 'PLUGIN_AUTH_SCOPE_DRIFT'})
            if plugin.get('x-cbcc-authorization-source') != 'HOST_OUT_OF_BAND_ACTION_AUTHORIZATION':
                issues.append({'action_id': action_id, 'code': 'PLUGIN_AUTH_SOURCE_DRIFT'})
            secret_fields = forbidden_secret_fields(plugin_schema or {})
            if secret_fields:
                issues.append({'action_id': action_id, 'code': 'PLUGIN_CREDENTIAL_FIELD_PRESENT', 'fields': secret_fields})
        rows.append({
            'action_id': action_id,
            'canonical_schema_hash': canonical_hash,
            'mcp_schema_hash': stable_hash(mcp_schema) if mcp_schema is not None else None,
            'plugin_schema_hash': stable_hash(plugin_schema) if plugin_schema is not None else None,
            'permission_scope': action['permission_scope'],
        })

    extra_mcp = sorted(set(mcp_by_action) - set(canonical))
    extra_plugin = sorted(set(plugin_by_action) - set(canonical))
    for action_id in extra_mcp:
        issues.append({'action_id': action_id, 'code': 'MCP_UNKNOWN_ACTION'})
    for action_id in extra_plugin:
        issues.append({'action_id': action_id, 'code': 'PLUGIN_UNKNOWN_ACTION'})

    return {
        'version': VERSION,
        'status': 'PASS' if not issues else 'FAIL',
        'canonical_action_count': len(canonical),
        'mcp_tool_count': len(mcp_by_action),
        'plugin_operation_count': len(plugin_by_action),
        'rows': rows,
        'issues': issues,
        'rules': [
            'MCP and Plugin input schemas are generated from and must equal the canonical action schema.',
            'Permission scope must remain identical across transports.',
            'Credential-like payload fields are forbidden in every generated transport schema.',
            'Transport descriptors do not own provider execution runtime.',
        ],
    }


def transport_descriptor_bundle(*, server_url: str = '/') -> dict[str, Any]:
    mcp = mcp_tool_descriptors()
    plugin = plugin_openapi_descriptor(server_url=server_url)
    parity = descriptor_parity_report(mcp_tools=mcp, plugin_openapi=plugin)
    return {
        'version': VERSION,
        'mcp_tools': mcp,
        'plugin_openapi': plugin,
        'parity': parity,
        'runtime_authority': 'ProviderActionDispatcher',
        'mcp_server_included': False,
        'plugin_http_server_included': False,
    }


def materialize_transport_descriptors(output_dir: Path, *, server_url: str = '/') -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    bundle = transport_descriptor_bundle(server_url=server_url)
    if bundle['parity']['status'] != 'PASS':
        raise ValueError('transport descriptor parity failed')
    paths = {
        'mcp_tools': output / 'mcp_tools.json',
        'plugin_openapi': output / 'plugin_openapi.json',
        'manifest': output / 'descriptor_manifest.json',
    }
    paths['mcp_tools'].write_text(json.dumps(bundle['mcp_tools'], ensure_ascii=False, indent=2), encoding='utf-8')
    paths['plugin_openapi'].write_text(json.dumps(bundle['plugin_openapi'], ensure_ascii=False, indent=2), encoding='utf-8')
    manifest = {
        'version': VERSION,
        'canonical_action_version': ACTION_VERSION,
        'runtime_authority': 'ProviderActionDispatcher',
        'mcp_server_included': False,
        'plugin_http_server_included': False,
        'parity': bundle['parity'],
        'files': {
            'mcp_tools': paths['mcp_tools'].name,
            'plugin_openapi': paths['plugin_openapi'].name,
        },
    }
    paths['manifest'].write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'status': 'MATERIALIZED', 'paths': {k: str(v) for k, v in paths.items()}, 'manifest': manifest}


class PluginActionTransportAdapter:
    """Thin in-process Plugin/OpenAPI operation adapter over ProviderActionDispatcher.

    Authentication/authorization is supplied out-of-band as ActionAuthorization. The request body is
    always the canonical action payload and can never carry runtime credentials.
    """

    def __init__(self, dispatcher: ProviderActionDispatcher) -> None:
        self.dispatcher = dispatcher
        self._operation_to_action = {
            str(row['plugin_operation_id']): str(row['action_id'])
            for row in action_transport_manifest()['mappings']
        }

    def invoke(self, operation_id: str, body: dict[str, Any] | None, authorization: ActionAuthorization | None = None) -> dict[str, Any]:
        action_id = self._operation_to_action.get(str(operation_id))
        if action_id is None:
            return {
                'version': VERSION,
                'operation_id': operation_id,
                'status': 'INVALID_OPERATION',
                'result': None,
                'errors': [{'code': 'PLUGIN_OPERATION_NOT_MAPPED'}],
            }
        return self.dispatcher.dispatch(action_id, body or {}, authorization)

    def descriptor(self, *, server_url: str = '/') -> dict[str, Any]:
        return plugin_openapi_descriptor(server_url=server_url)
