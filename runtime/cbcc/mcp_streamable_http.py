from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Iterable, Mapping
from wsgiref.simple_server import WSGIServer, make_server
import base64
import binascii
import json
import os
import re

from .action_transports import mcp_tool_descriptors
from .host_actions import ActionAuthorization, ProviderActionDispatcher
from .mcp_protocol import (
    JSONRPC_INVALID_PARAMS,
    JSONRPC_INVALID_PARAMS,
    JSONRPC_INVALID_PARAMS,
    JSONRPC_INVALID_REQUEST,
    JSONRPC_METHOD_NOT_FOUND,
    MCPAuthorizationContext,
    MCPProtocolProcessor,
    MCP_AUTHORIZATION_ERROR,
    MCP_UNSUPPORTED_PROTOCOL_VERSION,
    MODERN_PROTOCOL_VERSION,
)

VERSION = '0.6.21-mcp-streamable-http'
HEADER_MISMATCH = -32020
MCP_HTTP_AUTH_MODULE_ENV = 'CBCC_MCP_HTTP_AUTH_MODULE'
MCP_ALLOWED_ORIGINS_ENV = 'CBCC_MCP_ALLOWED_ORIGINS'
DEFAULT_MAX_REQUEST_BYTES = 1024 * 1024


@dataclass(frozen=True)
class MCPHTTPAuthorizationContext:
    method: str
    path: str
    headers: Mapping[str, str]
    remote_addr: str | None
    origin: str | None
    protocol_version: str | None
    tool_name: str | None
    action_id: str | None
    required_scope: str | None
    request_meta: Mapping[str, Any]
    client_info: Mapping[str, Any]


HTTPAuthorizationResolver = Callable[[MCPHTTPAuthorizationContext], ActionAuthorization | None]
StreamResponseSelector = Callable[[dict[str, Any], dict[str, Any]], bool]


def deny_by_default_http_authorization(context: MCPHTTPAuthorizationContext) -> ActionAuthorization:
    del context
    return ActionAuthorization(actor_id='mcp-http-anonymous', scopes=frozenset())


def _coerce_authorization(value: Any) -> ActionAuthorization | None:
    if value is None or isinstance(value, ActionAuthorization):
        return value
    if isinstance(value, dict):
        scopes = value.get('scopes') or []
        if not isinstance(scopes, (list, tuple, set, frozenset)):
            raise TypeError('authorization scopes must be a sequence')
        return ActionAuthorization.from_scopes(
            [str(item) for item in scopes],
            actor_id=str(value.get('actor_id') or 'mcp-http-host'),
        )
    raise TypeError('authorization resolver must return ActionAuthorization, dict, or None')


def http_authorization_resolver_from_environment(
    *, env: dict[str, str] | None = None,
) -> HTTPAuthorizationResolver:
    values = os.environ if env is None else env
    module_name = str(values.get(MCP_HTTP_AUTH_MODULE_ENV) or '').strip()
    if not module_name:
        return deny_by_default_http_authorization
    module = import_module(module_name)
    resolver = getattr(module, 'resolve_action_authorization', None)
    if not callable(resolver):
        raise TypeError(f'{MCP_HTTP_AUTH_MODULE_ENV} module must expose resolve_action_authorization(...)')

    def _resolve(context: MCPHTTPAuthorizationContext) -> ActionAuthorization | None:
        value = resolver(
            transport='MCP_STREAMABLE_HTTP',
            method=context.method,
            path=context.path,
            headers=dict(context.headers),
            remote_addr=context.remote_addr,
            origin=context.origin,
            protocol_version=context.protocol_version,
            tool_name=context.tool_name,
            action_id=context.action_id,
            required_scope=context.required_scope,
            request_meta=dict(context.request_meta),
            client_info=dict(context.client_info),
        )
        return _coerce_authorization(value)

    return _resolve


def allowed_origins_from_environment(*, env: dict[str, str] | None = None) -> frozenset[str]:
    values = os.environ if env is None else env
    raw = str(values.get(MCP_ALLOWED_ORIGINS_ENV) or '')
    return frozenset(item.strip() for item in raw.split(',') if item.strip())


def _json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def _status_line(code: int) -> str:
    labels = {
        200: 'OK',
        202: 'Accepted',
        400: 'Bad Request',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        411: 'Length Required',
        413: 'Payload Too Large',
        415: 'Unsupported Media Type',
        500: 'Internal Server Error',
    }
    return f'{code} {labels.get(code, "Error")}'


def _headers_from_environ(environ: Mapping[str, Any]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for key, value in environ.items():
        if str(key).startswith('HTTP_'):
            name = str(key)[5:].replace('_', '-').lower()
            headers[name] = str(value)
    if environ.get('CONTENT_TYPE'):
        headers['content-type'] = str(environ['CONTENT_TYPE'])
    if environ.get('CONTENT_LENGTH'):
        headers['content-length'] = str(environ['CONTENT_LENGTH'])
    return headers


def _jsonrpc_error(request_id: Any, code: int, message: str, *, data: dict[str, Any] | None = None) -> dict[str, Any]:
    error: dict[str, Any] = {'code': int(code), 'message': str(message)}
    if data is not None:
        error['data'] = data
    return {'jsonrpc': '2.0', 'id': request_id, 'error': error}


def _body_protocol_version(message: Mapping[str, Any]) -> str | None:
    params = message.get('params')
    if not isinstance(params, dict):
        return None
    meta = params.get('_meta')
    if not isinstance(meta, dict):
        return None
    value = meta.get('io.modelcontextprotocol/protocolVersion')
    return str(value) if value is not None else None


def _body_name(message: Mapping[str, Any]) -> Any:
    params = message.get('params')
    if not isinstance(params, dict):
        return None
    if 'name' in params:
        return params.get('name')
    if 'uri' in params:
        return params.get('uri')
    return None


def _decode_mirrored_header(value: str) -> str:
    text = str(value)
    if text.startswith('=?base64?') and text.endswith('?='):
        encoded = text[len('=?base64?'):-2]
        try:
            return base64.b64decode(encoded, validate=True).decode('utf-8')
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise ValueError('malformed MCP Base64 sentinel header') from exc
    try:
        text.encode('ascii')
    except UnicodeEncodeError as exc:
        raise ValueError('non-ASCII MCP header must use Base64 sentinel encoding') from exc
    if any(ord(char) < 0x20 and char not in {'\t'} for char in text) or '\x7f' in text:
        raise ValueError('invalid control character in MCP header')
    return text


def _reachable_header_annotations(schema: Mapping[str, Any], path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], str, str]]:
    rows: list[tuple[tuple[str, ...], str, str]] = []
    properties = schema.get('properties')
    if not isinstance(properties, dict):
        return rows
    for property_name, raw_property in properties.items():
        if not isinstance(raw_property, dict):
            continue
        current = (*path, str(property_name))
        annotation = raw_property.get('x-mcp-header')
        if annotation is not None:
            rows.append((current, str(annotation), str(raw_property.get('type') or '')))
        rows.extend(_reachable_header_annotations(raw_property, current))
    return rows


def _value_at_path(payload: Mapping[str, Any], path: tuple[str, ...]) -> tuple[bool, Any]:
    current: Any = payload
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _primitive_header_value(value: Any, type_name: str) -> str:
    if type_name == 'boolean':
        if not isinstance(value, bool):
            raise ValueError('boolean mirrored parameter type mismatch')
        return 'true' if value else 'false'
    if type_name == 'integer':
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError('integer mirrored parameter type mismatch')
        if value < -(2**53) + 1 or value > (2**53) - 1:
            raise ValueError('integer mirrored parameter outside JavaScript safe range')
        return str(value)
    if type_name == 'string':
        if not isinstance(value, str):
            raise ValueError('string mirrored parameter type mismatch')
        return value
    raise ValueError('x-mcp-header is only valid on string/integer/boolean properties')


def _accept_supports_required_types(value: str | None) -> bool:
    if not value:
        return False
    media = {item.split(';', 1)[0].strip().lower() for item in value.split(',') if item.strip()}
    return 'application/json' in media and 'text/event-stream' in media


def _content_type_is_json(value: str | None) -> bool:
    if not value:
        return False
    media = value.split(';', 1)[0].strip().lower()
    return media == 'application/json' or media.endswith('+json')


class MCPStreamableHTTPApplication:
    """MCP 2026-07-28 Streamable HTTP binding over the shared MCPProtocolProcessor."""

    def __init__(
        self,
        dispatcher: ProviderActionDispatcher,
        *,
        authorization_resolver: HTTPAuthorizationResolver | None = None,
        allowed_origins: Iterable[str] = (),
        max_request_bytes: int = DEFAULT_MAX_REQUEST_BYTES,
        endpoint_path: str = '/mcp',
        stream_response_selector: StreamResponseSelector | None = None,
    ) -> None:
        self.dispatcher = dispatcher
        self.authorization_resolver = authorization_resolver or deny_by_default_http_authorization
        self.allowed_origins = frozenset(str(item) for item in allowed_origins)
        self.max_request_bytes = max(1, int(max_request_bytes))
        self.endpoint_path = '/' + str(endpoint_path or '/mcp').strip('/')
        self.stream_response_selector = stream_response_selector or (lambda _request, _response: False)
        self._tools = {str(tool.get('name') or ''): tool for tool in mcp_tool_descriptors()}

    def _respond(self, start_response, status: int, payload: Any | None, *, headers: list[tuple[str, str]] | None = None):
        response_headers = list(headers or [])
        if payload is None:
            start_response(_status_line(status), response_headers + [('Content-Length', '0')])
            return [b'']
        raw = _json_bytes(payload)
        response_headers.extend([
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Content-Length', str(len(raw))),
            ('Cache-Control', 'no-store'),
            ('X-Content-Type-Options', 'nosniff'),
        ])
        start_response(_status_line(status), response_headers)
        return [raw]

    def _protocol_error(self, start_response, status: int, request_id: Any, code: int, message: str, *, data: dict[str, Any] | None = None):
        return self._respond(start_response, status, _jsonrpc_error(request_id, code, message, data=data))

    def _validate_origin(self, origin: str | None) -> bool:
        if origin is None or origin == '':
            return True
        return origin in self.allowed_origins

    def _validate_headers(self, message: dict[str, Any], headers: Mapping[str, str]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        request_id = message.get('id')
        header_version = headers.get('mcp-protocol-version')
        body_version = _body_protocol_version(message)
        if not header_version or not body_version or header_version != body_version:
            return None, _jsonrpc_error(request_id, HEADER_MISMATCH, 'Header mismatch: MCP-Protocol-Version must match request metadata')
        if header_version != MODERN_PROTOCOL_VERSION:
            return None, _jsonrpc_error(
                request_id,
                MCP_UNSUPPORTED_PROTOCOL_VERSION,
                'Unsupported protocol version',
                data={'supported': [MODERN_PROTOCOL_VERSION], 'requested': header_version},
            )
        method = message.get('method')
        header_method = headers.get('mcp-method')
        if not isinstance(method, str) or not header_method or header_method != method:
            return None, _jsonrpc_error(request_id, HEADER_MISMATCH, 'Header mismatch: Mcp-Method must match request method')
        name_value = _body_name(message)
        if method in {'tools/call', 'resources/read', 'prompts/get'}:
            raw_name = headers.get('mcp-name')
            if raw_name is None or name_value is None:
                return None, _jsonrpc_error(request_id, HEADER_MISMATCH, 'Header mismatch: Mcp-Name is required')
            try:
                decoded = _decode_mirrored_header(raw_name)
            except ValueError:
                return None, _jsonrpc_error(request_id, HEADER_MISMATCH, 'Header mismatch: malformed Mcp-Name')
            if decoded != str(name_value):
                return None, _jsonrpc_error(request_id, HEADER_MISMATCH, 'Header mismatch: Mcp-Name does not match request body')
        if method == 'tools/call' and isinstance(name_value, str):
            tool = self._tools.get(name_value)
            params = message.get('params') if isinstance(message.get('params'), dict) else {}
            arguments = params.get('arguments') if isinstance(params.get('arguments'), dict) else {}
            if tool is not None:
                schema = tool.get('inputSchema') if isinstance(tool.get('inputSchema'), dict) else {}
                seen_headers: set[str] = set()
                for path, annotation, type_name in _reachable_header_annotations(schema):
                    normalized = annotation.lower()
                    if (
                        not annotation
                        or normalized in seen_headers
                        or re.fullmatch(r"[!#$%&'*+\-.^_`|~0-9A-Za-z]+", annotation) is None
                    ):
                        return None, _jsonrpc_error(request_id, HEADER_MISMATCH, 'Header mismatch: invalid x-mcp-header annotation')
                    seen_headers.add(normalized)
                    present, value = _value_at_path(arguments, path)
                    header_key = f'mcp-param-{normalized}'
                    if not present or value is None:
                        if header_key in headers:
                            return None, _jsonrpc_error(request_id, HEADER_MISMATCH, f'Header mismatch: unexpected Mcp-Param-{annotation}')
                        continue
                    raw = headers.get(header_key)
                    if raw is None:
                        return None, _jsonrpc_error(request_id, HEADER_MISMATCH, f'Header mismatch: missing Mcp-Param-{annotation}')
                    try:
                        decoded = _decode_mirrored_header(raw)
                        expected = _primitive_header_value(value, type_name)
                    except ValueError:
                        return None, _jsonrpc_error(request_id, HEADER_MISMATCH, f'Header mismatch: malformed Mcp-Param-{annotation}')
                    if decoded != expected:
                        return None, _jsonrpc_error(request_id, HEADER_MISMATCH, f'Header mismatch: Mcp-Param-{annotation} does not match request body')
        return message, None

    def _processor_for_request(self, *, headers: Mapping[str, str], environ: Mapping[str, Any]) -> MCPProtocolProcessor:
        origin = headers.get('origin')
        remote_addr = str(environ.get('REMOTE_ADDR')) if environ.get('REMOTE_ADDR') else None

        def resolve(core_context: MCPAuthorizationContext) -> ActionAuthorization | None:
            context = MCPHTTPAuthorizationContext(
                method=core_context.method,
                path=self.endpoint_path,
                headers=dict(headers),
                remote_addr=remote_addr,
                origin=origin,
                protocol_version=core_context.protocol_version,
                tool_name=core_context.tool_name,
                action_id=core_context.action_id,
                required_scope=core_context.required_scope,
                request_meta=dict(core_context.request_meta),
                client_info=dict(core_context.client_info),
            )
            return _coerce_authorization(self.authorization_resolver(context))

        return MCPProtocolProcessor(
            self.dispatcher,
            authorization_resolver=resolve,
            transport_name='MCP_STREAMABLE_HTTP',
        )

    def _http_status_for_protocol_response(self, response: dict[str, Any]) -> int:
        error = response.get('error') if isinstance(response, dict) else None
        code = error.get('code') if isinstance(error, dict) else None
        if code in {HEADER_MISMATCH, MCP_UNSUPPORTED_PROTOCOL_VERSION, JSONRPC_INVALID_REQUEST, JSONRPC_INVALID_PARAMS}:
            return 400
        if code == JSONRPC_METHOD_NOT_FOUND:
            return 404
        if code == MCP_AUTHORIZATION_ERROR:
            return 403
        return 200

    def _sse_response(self, start_response, response: dict[str, Any]):
        data = _json_bytes(response).decode('utf-8')
        raw = f'event: message\ndata: {data}\n\n'.encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'text/event-stream; charset=utf-8'),
            ('Cache-Control', 'no-cache'),
            ('X-Accel-Buffering', 'no'),
            ('Content-Length', str(len(raw))),
        ])
        return [raw]

    def __call__(self, environ, start_response):
        path = str(environ.get('PATH_INFO') or '/')
        method = str(environ.get('REQUEST_METHOD') or 'GET').upper()
        if path != self.endpoint_path:
            return self._protocol_error(start_response, 404, None, JSONRPC_METHOD_NOT_FOUND, 'MCP endpoint not found')
        if method != 'POST':
            return self._protocol_error(start_response, 405, None, JSONRPC_INVALID_REQUEST, 'MCP 2026 Streamable HTTP endpoint accepts POST only')

        headers = _headers_from_environ(environ)
        if not self._validate_origin(headers.get('origin')):
            return self._protocol_error(start_response, 403, None, MCP_AUTHORIZATION_ERROR, 'Invalid Origin')
        if not _accept_supports_required_types(headers.get('accept')):
            return self._protocol_error(start_response, 406, None, JSONRPC_INVALID_REQUEST, 'Accept must include application/json and text/event-stream')
        if not _content_type_is_json(headers.get('content-type')):
            return self._protocol_error(start_response, 415, None, JSONRPC_INVALID_REQUEST, 'Content-Type must be application/json')

        raw_length = headers.get('content-length')
        if raw_length is None:
            return self._protocol_error(start_response, 411, None, JSONRPC_INVALID_REQUEST, 'Content-Length required')
        try:
            length = int(raw_length)
        except ValueError:
            return self._protocol_error(start_response, 400, None, JSONRPC_INVALID_REQUEST, 'Invalid Content-Length')
        if length < 0:
            return self._protocol_error(start_response, 400, None, JSONRPC_INVALID_REQUEST, 'Invalid Content-Length')
        if length > self.max_request_bytes:
            return self._protocol_error(start_response, 413, None, JSONRPC_INVALID_REQUEST, 'Request body too large')
        try:
            raw = environ['wsgi.input'].read(length)
            message = json.loads(raw.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return self._protocol_error(start_response, 400, None, -32700, 'Parse error')
        if not isinstance(message, dict):
            return self._protocol_error(start_response, 400, None, JSONRPC_INVALID_REQUEST, 'JSON-RPC message must be an object')
        if 'method' not in message:
            return self._protocol_error(start_response, 400, message.get('id'), HEADER_MISMATCH, 'Header mismatch: request body must contain method')

        _validated, header_error = self._validate_headers(message, headers)
        if header_error is not None:
            return self._respond(start_response, 400, header_error)
        if str(message.get('method') or '') == 'notifications/cancelled':
            return self._protocol_error(start_response, 400, message.get('id'), JSONRPC_METHOD_NOT_FOUND, 'notifications/cancelled is stdio-only in MCP 2026')

        processor = self._processor_for_request(headers=headers, environ=environ)
        response = processor.handle_message(message)
        if message.get('id') is None:
            if response is None or 'error' not in response:
                return self._respond(start_response, 202, None)
            return self._respond(start_response, self._http_status_for_protocol_response(response), response)
        if response is None:
            return self._protocol_error(start_response, 500, message.get('id'), -32603, 'Protocol processor returned no response')
        status = self._http_status_for_protocol_response(response)
        if status == 200 and self.stream_response_selector(message, response):
            return self._sse_response(start_response, response)
        return self._respond(start_response, status, response)


def make_mcp_streamable_http_server(
    dispatcher: ProviderActionDispatcher,
    *,
    host: str = '127.0.0.1',
    port: int = 8788,
    authorization_resolver: HTTPAuthorizationResolver | None = None,
    allowed_origins: Iterable[str] = (),
    max_request_bytes: int = DEFAULT_MAX_REQUEST_BYTES,
    endpoint_path: str = '/mcp',
    stream_response_selector: StreamResponseSelector | None = None,
) -> WSGIServer:
    application = MCPStreamableHTTPApplication(
        dispatcher,
        authorization_resolver=authorization_resolver,
        allowed_origins=allowed_origins,
        max_request_bytes=max_request_bytes,
        endpoint_path=endpoint_path,
        stream_response_selector=stream_response_selector,
    )
    return make_server(host, int(port), application)


def mcp_streamable_http_contract() -> dict[str, Any]:
    return {
        'version': VERSION,
        'protocol_version': MODERN_PROTOCOL_VERSION,
        'transport': 'MCP_STREAMABLE_HTTP',
        'endpoint': '/mcp',
        'methods': ['POST'],
        'request_headers': ['MCP-Protocol-Version', 'Mcp-Method', 'Mcp-Name when applicable'],
        'accept_required': ['application/json', 'text/event-stream'],
        'origin_validation': 'REQUIRED_WHEN_ORIGIN_PRESENT',
        'sessions': 'NONE',
        'get_stream_endpoint': 'NONE',
        'last_event_id_resume': 'UNSUPPORTED',
        'response_modes': ['application/json', 'request-scoped text/event-stream'],
        'protocol_processor': 'MCPProtocolProcessor',
        'runtime_authority': 'ProviderActionDispatcher',
        'provider_runtime_direct_access': 'FORBIDDEN',
    }
