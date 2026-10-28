from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Mapping
import json
import os

from .action_transports import mcp_tool_descriptors
from .host_actions import ActionAuthorization, ProviderActionDispatcher

VERSION = '0.6.21-mcp-protocol-core'
MODERN_PROTOCOL_VERSION = '2026-07-28'
LEGACY_PROTOCOL_VERSION = '2025-11-25'
SUPPORTED_PROTOCOL_VERSIONS = (MODERN_PROTOCOL_VERSION, LEGACY_PROTOCOL_VERSION)
MCP_AUTH_MODULE_ENV = 'CBCC_MCP_AUTH_MODULE'

JSONRPC_PARSE_ERROR = -32700
JSONRPC_INVALID_REQUEST = -32600
JSONRPC_METHOD_NOT_FOUND = -32601
JSONRPC_INVALID_PARAMS = -32602
JSONRPC_INTERNAL_ERROR = -32603
MCP_AUTHORIZATION_ERROR = -32001
MCP_NOT_INITIALIZED = -32002
MCP_UNSUPPORTED_PROTOCOL_VERSION = -32022


@dataclass(frozen=True)
class MCPAuthorizationContext:
    transport: str
    method: str
    tool_name: str | None
    action_id: str | None
    required_scope: str | None
    protocol_version: str | None
    request_meta: Mapping[str, Any]
    client_info: Mapping[str, Any]


AuthorizationResolver = Callable[[MCPAuthorizationContext], ActionAuthorization | None]


def deny_by_default_authorization(context: MCPAuthorizationContext) -> ActionAuthorization:
    del context
    return ActionAuthorization(actor_id='mcp-anonymous', scopes=frozenset())


def _coerce_authorization(value: Any) -> ActionAuthorization | None:
    if value is None or isinstance(value, ActionAuthorization):
        return value
    if isinstance(value, dict):
        scopes = value.get('scopes') or []
        if not isinstance(scopes, (list, tuple, set, frozenset)):
            raise TypeError('authorization scopes must be a sequence')
        return ActionAuthorization.from_scopes(
            [str(item) for item in scopes],
            actor_id=str(value.get('actor_id') or 'mcp-host'),
        )
    raise TypeError('authorization resolver must return ActionAuthorization, dict, or None')


def authorization_resolver_from_environment(*, env: dict[str, str] | None = None) -> AuthorizationResolver:
    values = os.environ if env is None else env
    module_name = str(values.get(MCP_AUTH_MODULE_ENV) or '').strip()
    if not module_name:
        return deny_by_default_authorization
    module = import_module(module_name)
    resolver = getattr(module, 'resolve_action_authorization', None)
    if not callable(resolver):
        raise TypeError(f'{MCP_AUTH_MODULE_ENV} module must expose resolve_action_authorization(...)')

    def _resolve(context: MCPAuthorizationContext) -> ActionAuthorization | None:
        value = resolver(
            transport=context.transport,
            method=context.method,
            tool_name=context.tool_name,
            action_id=context.action_id,
            required_scope=context.required_scope,
            protocol_version=context.protocol_version,
            request_meta=dict(context.request_meta),
            client_info=dict(context.client_info),
        )
        return _coerce_authorization(value)

    return _resolve


def _server_info() -> dict[str, str]:
    return {'name': 'cbcc', 'version': VERSION}


def _jsonrpc_result(request_id: Any, result: Any) -> dict[str, Any]:
    return {'jsonrpc': '2.0', 'id': request_id, 'result': result}


def _jsonrpc_error(
    request_id: Any,
    code: int,
    message: str,
    *,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {'code': int(code), 'message': str(message)}
    if data is not None:
        error['data'] = data
    return {'jsonrpc': '2.0', 'id': request_id, 'error': error}


def _meta_from_params(params: Mapping[str, Any]) -> dict[str, Any]:
    meta = params.get('_meta') or {}
    return dict(meta) if isinstance(meta, dict) else {}


def _protocol_version_from_meta(meta: Mapping[str, Any]) -> str | None:
    value = meta.get('io.modelcontextprotocol/protocolVersion')
    return str(value) if value is not None else None


def _client_info_from_meta(meta: Mapping[str, Any]) -> dict[str, Any]:
    value = meta.get('io.modelcontextprotocol/clientInfo') or {}
    return dict(value) if isinstance(value, dict) else {}


def _modern_result_meta() -> dict[str, Any]:
    return {'io.modelcontextprotocol/serverInfo': _server_info()}


def _with_modern_meta(result: dict[str, Any]) -> dict[str, Any]:
    out = dict(result)
    existing = out.get('_meta') if isinstance(out.get('_meta'), dict) else {}
    out['_meta'] = {**existing, **_modern_result_meta()}
    return out


def _safe_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), sort_keys=True)


class MCPProtocolProcessor:
    """Dual-era MCP stdio protocol host over canonical CBCC action descriptors.

    The transport owns JSON-RPC framing, MCP lifecycle negotiation, tool discovery and MCP result
    envelopes. It never imports or calls ProviderExecutionSurface, ProviderExecutorBridge or
    ProviderExecutor. Tool execution is delegated only to ProviderActionDispatcher.
    """

    def __init__(
        self,
        dispatcher: ProviderActionDispatcher,
        *,
        authorization_resolver: AuthorizationResolver | None = None,
        transport_name: str = 'MCP',
    ) -> None:
        self.dispatcher = dispatcher
        self.authorization_resolver = authorization_resolver or deny_by_default_authorization
        self.transport_name = str(transport_name or 'MCP')
        self.legacy_initialized = False
        self.legacy_client_info: dict[str, Any] = {}
        self._tools = list(mcp_tool_descriptors())
        self._tool_by_name = {str(tool.get('name') or ''): tool for tool in self._tools}

    def contract(self) -> dict[str, Any]:
        return {
            'version': VERSION,
            'transport': self.transport_name,
            'supported_protocol_versions': list(SUPPORTED_PROTOCOL_VERSIONS),
            'modern_lifecycle': 'server/discover + per-request _meta',
            'legacy_lifecycle': 'initialize + notifications/initialized',
            'tool_schema_source': 'mcp_tool_descriptors()',
            'runtime_authority': 'ProviderActionDispatcher',
            'provider_runtime_direct_access': 'FORBIDDEN',
            'authorization': {
                'source': 'HOST_INJECTED_RESOLVER',
                'environment_module': MCP_AUTH_MODULE_ENV,
                'default': 'DENY',
                'action_payload_credentials': 'FORBIDDEN',
            },
        }

    def _resolve_authorization(
        self,
        *,
        method: str,
        tool: Mapping[str, Any] | None,
        protocol_version: str | None,
        meta: Mapping[str, Any],
    ) -> tuple[ActionAuthorization | None, dict[str, Any] | None]:
        context = MCPAuthorizationContext(
            transport=self.transport_name,
            method=method,
            tool_name=str(tool.get('name')) if tool else None,
            action_id=str(tool.get('x-cbcc-action-id')) if tool else None,
            required_scope=str(tool.get('x-cbcc-permission-scope')) if tool else None,
            protocol_version=protocol_version,
            request_meta=dict(meta),
            client_info=_client_info_from_meta(meta) or dict(self.legacy_client_info),
        )
        try:
            authorization = _coerce_authorization(self.authorization_resolver(context))
        except Exception:
            return None, _jsonrpc_error(None, MCP_AUTHORIZATION_ERROR, 'Authorization resolution failed')
        return authorization or ActionAuthorization(actor_id='mcp-anonymous', scopes=frozenset()), None

    def _validate_modern_meta(
        self,
        request_id: Any,
        params: Mapping[str, Any],
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        meta = _meta_from_params(params)
        protocol_version = _protocol_version_from_meta(meta)
        if protocol_version != MODERN_PROTOCOL_VERSION:
            return None, _jsonrpc_error(
                request_id,
                MCP_UNSUPPORTED_PROTOCOL_VERSION,
                'Unsupported protocol version',
                data={
                    'supported': [MODERN_PROTOCOL_VERSION],
                    'requested': protocol_version,
                },
            )
        capabilities = meta.get('io.modelcontextprotocol/clientCapabilities')
        if not isinstance(capabilities, dict):
            return None, _jsonrpc_error(
                request_id,
                JSONRPC_INVALID_PARAMS,
                'Missing required MCP client capabilities metadata',
            )
        return meta, None

    def _request_era(
        self,
        request_id: Any,
        method: str,
        params: Mapping[str, Any],
    ) -> tuple[str | None, dict[str, Any], dict[str, Any] | None]:
        meta = _meta_from_params(params)
        if meta:
            modern_meta, error = self._validate_modern_meta(request_id, params)
            if error is not None:
                return None, {}, error
            return MODERN_PROTOCOL_VERSION, modern_meta or {}, None
        if method == 'initialize':
            return LEGACY_PROTOCOL_VERSION, {}, None
        if method == 'notifications/initialized':
            return LEGACY_PROTOCOL_VERSION, {}, None
        if self.legacy_initialized:
            return LEGACY_PROTOCOL_VERSION, {}, None
        return None, {}, _jsonrpc_error(
            request_id,
            MCP_NOT_INITIALIZED,
            'MCP request requires modern per-request metadata or legacy initialization',
        )

    def _discover(self, request_id: Any, params: Mapping[str, Any]) -> dict[str, Any]:
        meta, error = self._validate_modern_meta(request_id, params)
        if error is not None:
            return error
        result = {
            'resultType': 'complete',
            'supportedVersions': [MODERN_PROTOCOL_VERSION],
            'capabilities': {'tools': {}},
            '_meta': _modern_result_meta(),
            'instructions': 'CBCC provider tools use host authorization and canonical action schemas.',
            'ttlMs': 0,
            'cacheScope': 'private',
        }
        return _jsonrpc_result(request_id, result)

    def _initialize_legacy(self, request_id: Any, params: Mapping[str, Any]) -> dict[str, Any]:
        requested = str(params.get('protocolVersion') or '')
        self.legacy_client_info = dict(params.get('clientInfo') or {}) if isinstance(params.get('clientInfo'), dict) else {}
        # Legacy MCP negotiates during initialization. This reference host intentionally supports one
        # legacy revision and returns it even when the client proposed another legacy revision.
        result = {
            'protocolVersion': LEGACY_PROTOCOL_VERSION,
            'capabilities': {'tools': {}},
            'serverInfo': _server_info(),
            'instructions': 'CBCC provider tools are authorization-scoped and backed by canonical actions.',
        }
        if requested == MODERN_PROTOCOL_VERSION:
            return _jsonrpc_error(
                request_id,
                MCP_UNSUPPORTED_PROTOCOL_VERSION,
                'Modern MCP uses server/discover and per-request metadata',
                data={'supported': list(SUPPORTED_PROTOCOL_VERSIONS), 'requested': requested},
            )
        return _jsonrpc_result(request_id, result)

    def _tool_authorized(
        self,
        tool: Mapping[str, Any],
        *,
        method: str,
        protocol_version: str,
        meta: Mapping[str, Any],
    ) -> tuple[bool, ActionAuthorization | None, dict[str, Any] | None]:
        authorization, error = self._resolve_authorization(
            method=method,
            tool=tool,
            protocol_version=protocol_version,
            meta=meta,
        )
        if error is not None:
            return False, None, error
        required_scope = str(tool.get('x-cbcc-permission-scope') or '')
        allowed = bool(authorization and authorization.allows(required_scope))
        return allowed, authorization, None

    def _list_tools(
        self,
        request_id: Any,
        *,
        protocol_version: str,
        meta: Mapping[str, Any],
    ) -> dict[str, Any]:
        visible: list[dict[str, Any]] = []
        for tool in self._tools:
            allowed, _authorization, error = self._tool_authorized(
                tool,
                method='tools/list',
                protocol_version=protocol_version,
                meta=meta,
            )
            if error is not None:
                error['id'] = request_id
                return error
            if allowed:
                visible.append(dict(tool))
        result: dict[str, Any] = {'tools': visible}
        if protocol_version == MODERN_PROTOCOL_VERSION:
            result = _with_modern_meta({'resultType': 'complete', **result, 'ttlMs': 0, 'cacheScope': 'private'})
        return _jsonrpc_result(request_id, result)

    def _call_tool(
        self,
        request_id: Any,
        params: Mapping[str, Any],
        *,
        protocol_version: str,
        meta: Mapping[str, Any],
    ) -> dict[str, Any]:
        name = str(params.get('name') or '')
        tool = self._tool_by_name.get(name)
        if tool is None:
            return _jsonrpc_error(request_id, JSONRPC_INVALID_PARAMS, f'Unknown tool: {name}')
        arguments = params.get('arguments') or {}
        if not isinstance(arguments, dict):
            return _jsonrpc_error(request_id, JSONRPC_INVALID_PARAMS, 'Tool arguments must be an object')
        allowed, authorization, auth_error = self._tool_authorized(
            tool,
            method='tools/call',
            protocol_version=protocol_version,
            meta=meta,
        )
        if auth_error is not None:
            auth_error['id'] = request_id
            return auth_error
        action_id = str(tool.get('x-cbcc-action-id') or '')
        envelope = self.dispatcher.dispatch(action_id, arguments, authorization)
        status = str(envelope.get('status') or '').upper() if isinstance(envelope, dict) else 'FAILED'
        is_error = status in {'DENIED', 'INVALID_INPUT', 'FAILED', 'HOLD'}
        result: dict[str, Any] = {
            'content': [{'type': 'text', 'text': _safe_text(envelope)}],
            'structuredContent': envelope,
            'isError': is_error,
        }
        if protocol_version == MODERN_PROTOCOL_VERSION:
            result = _with_modern_meta({'resultType': 'complete', **result})
        return _jsonrpc_result(request_id, result)

    def handle_message(self, message: Any) -> dict[str, Any] | None:
        if not isinstance(message, dict):
            return _jsonrpc_error(None, JSONRPC_INVALID_REQUEST, 'JSON-RPC message must be an object')
        if message.get('jsonrpc') != '2.0':
            return _jsonrpc_error(message.get('id'), JSONRPC_INVALID_REQUEST, 'jsonrpc must be 2.0')
        method = message.get('method')
        if not isinstance(method, str) or not method:
            # This reference server only consumes client->server requests/notifications on stdin.
            return _jsonrpc_error(message.get('id'), JSONRPC_INVALID_REQUEST, 'method is required')
        request_id = message.get('id')
        params = message.get('params') or {}
        if not isinstance(params, dict):
            return _jsonrpc_error(request_id, JSONRPC_INVALID_PARAMS, 'params must be an object')

        if method == 'server/discover':
            return self._discover(request_id, params)
        if method == 'initialize':
            return self._initialize_legacy(request_id, params)
        if method == 'notifications/initialized':
            self.legacy_initialized = True
            return None

        protocol_version, meta, era_error = self._request_era(request_id, method, params)
        if era_error is not None:
            return era_error
        if method == 'tools/list':
            return self._list_tools(request_id, protocol_version=str(protocol_version), meta=meta)
        if method == 'tools/call':
            return self._call_tool(
                request_id,
                params,
                protocol_version=str(protocol_version),
                meta=meta,
            )
        if request_id is None:
            return None
        return _jsonrpc_error(request_id, JSONRPC_METHOD_NOT_FOUND, f'Method not found: {method}')



def mcp_protocol_contract() -> dict[str, Any]:
    return {
        'version': VERSION,
        'protocol': 'MCP',
        'supported_protocol_versions': list(SUPPORTED_PROTOCOL_VERSIONS),
        'modern_protocol': MODERN_PROTOCOL_VERSION,
        'modern_discovery': 'server/discover',
        'legacy_protocol': LEGACY_PROTOCOL_VERSION,
        'legacy_initialize': True,
        'tools': [str(tool.get('name') or '') for tool in mcp_tool_descriptors()],
        'tool_schema_source': 'mcp_tool_descriptors()',
        'runtime_authority': 'ProviderActionDispatcher',
        'provider_runtime_direct_access': 'FORBIDDEN',
        'authorization_default': 'DENY',
    }
