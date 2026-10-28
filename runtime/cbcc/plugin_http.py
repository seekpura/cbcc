from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Iterable
from urllib.parse import urlsplit
from wsgiref.simple_server import WSGIServer, make_server
import json
import os

from .action_transports import PluginActionTransportAdapter, plugin_openapi_descriptor
from .host_actions import ActionAuthorization, ProviderActionDispatcher, action_catalog

VERSION = '0.6.19-plugin-http-host'
ACTION_AUTH_MODULE_ENV = 'CBCC_ACTION_AUTH_MODULE'
DEFAULT_MAX_REQUEST_BYTES = 1024 * 1024
DEFAULT_RETRY_AFTER_SECONDS = 1


@dataclass(frozen=True)
class HTTPAuthorizationContext:
    method: str
    path: str
    operation_id: str | None
    headers: dict[str, str]
    remote_addr: str | None


AuthorizationResolver = Callable[[HTTPAuthorizationContext], ActionAuthorization | None]


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
        409: 'Conflict',
        411: 'Length Required',
        413: 'Payload Too Large',
        415: 'Unsupported Media Type',
        422: 'Unprocessable Entity',
        500: 'Internal Server Error',
    }
    return f'{code} {labels.get(code, "Error")}'


def _http_code_for_envelope(envelope: dict[str, Any]) -> int:
    status = str(envelope.get('status') or '').upper()
    if status == 'SUCCEEDED':
        return 200
    if status == 'PENDING':
        return 202
    if status == 'DENIED':
        return 403
    if status == 'INVALID_OPERATION':
        return 404
    if status == 'INVALID_INPUT':
        return 422
    if status == 'HOLD':
        return 409
    return 500


def _headers_from_environ(environ: dict[str, Any]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for key, value in environ.items():
        if key.startswith('HTTP_'):
            name = key[5:].replace('_', '-').title()
            headers[name] = str(value)
    if environ.get('CONTENT_TYPE'):
        headers['Content-Type'] = str(environ['CONTENT_TYPE'])
    if environ.get('CONTENT_LENGTH'):
        headers['Content-Length'] = str(environ['CONTENT_LENGTH'])
    return headers


def deny_by_default_authorization(context: HTTPAuthorizationContext) -> ActionAuthorization:
    return ActionAuthorization(actor_id='http-anonymous', scopes=frozenset())


def _coerce_authorization(value: Any) -> ActionAuthorization | None:
    if value is None or isinstance(value, ActionAuthorization):
        return value
    if isinstance(value, dict):
        scopes = value.get('scopes') or []
        return ActionAuthorization.from_scopes(scopes, actor_id=str(value.get('actor_id') or 'http-host'))
    raise TypeError('authorization resolver must return ActionAuthorization, dict, or None')


def authorization_resolver_from_environment(*, env: dict[str, str] | None = None) -> AuthorizationResolver:
    values = os.environ if env is None else env
    module_name = str(values.get(ACTION_AUTH_MODULE_ENV) or '').strip()
    if not module_name:
        return deny_by_default_authorization
    module = import_module(module_name)
    resolver = getattr(module, 'resolve_action_authorization', None)
    if not callable(resolver):
        raise TypeError(f'{ACTION_AUTH_MODULE_ENV} module must expose resolve_action_authorization(...)')

    def _resolve(context: HTTPAuthorizationContext) -> ActionAuthorization | None:
        value = resolver(
            method=context.method,
            path=context.path,
            operation_id=context.operation_id,
            headers=dict(context.headers),
            remote_addr=context.remote_addr,
        )
        return _coerce_authorization(value)

    return _resolve


class PluginHTTPApplication:
    """Thin WSGI host over PluginActionTransportAdapter.

    The host owns HTTP parsing, size limits, transport status mapping and host authorization injection.
    It never instantiates or calls ProviderExecutionSurface, ProviderExecutorBridge or ProviderExecutor.
    """

    def __init__(
        self,
        adapter: PluginActionTransportAdapter,
        *,
        authorization_resolver: AuthorizationResolver | None = None,
        max_request_bytes: int = DEFAULT_MAX_REQUEST_BYTES,
        retry_after_seconds: int = DEFAULT_RETRY_AFTER_SECONDS,
        server_url: str = '/',
    ) -> None:
        self.adapter = adapter
        self.authorization_resolver = authorization_resolver or deny_by_default_authorization
        self.max_request_bytes = max(1, int(max_request_bytes))
        self.retry_after_seconds = max(0, int(retry_after_seconds))
        self.server_url = server_url
        descriptor = self.adapter.descriptor(server_url=server_url)
        self._descriptor = descriptor
        self._path_to_operation: dict[str, str] = {}
        for path, item in (descriptor.get('paths') or {}).items():
            operation = (item or {}).get('post') if isinstance(item, dict) else None
            if isinstance(operation, dict) and operation.get('operationId'):
                self._path_to_operation[str(path)] = str(operation['operationId'])

    def _respond(self, start_response: Callable[..., Any], code: int, payload: Any, headers: Iterable[tuple[str, str]] = ()) -> list[bytes]:
        body = _json_bytes(payload)
        response_headers = [
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Content-Length', str(len(body))),
            ('Cache-Control', 'no-store'),
            ('X-Content-Type-Options', 'nosniff'),
        ]
        response_headers.extend(list(headers))
        start_response(_status_line(code), response_headers)
        return [body]

    def _transport_error(self, start_response: Callable[..., Any], code: int, error_code: str, message: str | None = None) -> list[bytes]:
        error: dict[str, Any] = {'code': error_code}
        if message:
            error['message'] = message
        return self._respond(start_response, code, {
            'version': VERSION,
            'status': 'TRANSPORT_ERROR',
            'errors': [error],
        })

    def _read_json_body(self, environ: dict[str, Any], start_response: Callable[..., Any]) -> tuple[dict[str, Any] | None, list[bytes] | None]:
        content_type = str(environ.get('CONTENT_TYPE') or '').split(';', 1)[0].strip().lower()
        if content_type != 'application/json':
            return None, self._transport_error(start_response, 415, 'CONTENT_TYPE_JSON_REQUIRED')
        raw_length = str(environ.get('CONTENT_LENGTH') or '').strip()
        if not raw_length:
            return None, self._transport_error(start_response, 411, 'CONTENT_LENGTH_REQUIRED')
        try:
            content_length = int(raw_length)
        except ValueError:
            return None, self._transport_error(start_response, 400, 'CONTENT_LENGTH_INVALID')
        if content_length < 0:
            return None, self._transport_error(start_response, 400, 'CONTENT_LENGTH_INVALID')
        if content_length > self.max_request_bytes:
            return None, self._transport_error(start_response, 413, 'REQUEST_BODY_TOO_LARGE')
        raw = environ['wsgi.input'].read(content_length)
        if len(raw) != content_length:
            return None, self._transport_error(start_response, 400, 'REQUEST_BODY_TRUNCATED')
        try:
            payload = json.loads(raw.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, self._transport_error(start_response, 400, 'JSON_INVALID', str(exc))
        if not isinstance(payload, dict):
            return None, self._transport_error(start_response, 422, 'JSON_OBJECT_REQUIRED')
        return payload, None

    def __call__(self, environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
        method = str(environ.get('REQUEST_METHOD') or 'GET').upper()
        path = urlsplit(str(environ.get('PATH_INFO') or '/')).path

        if method == 'GET' and path in {'/health', '/healthz'}:
            return self._respond(start_response, 200, {
                'version': VERSION,
                'status': 'OK',
                'runtime_authority': 'ProviderActionDispatcher',
                'transport': 'WSGI_PLUGIN_OPENAPI',
            })
        if method == 'GET' and path in {'/openapi.json', '/schema/openapi.json'}:
            return self._respond(start_response, 200, self._descriptor)
        if method == 'GET' and path in {'/actions.json', '/schema/actions.json'}:
            return self._respond(start_response, 200, action_catalog())
        if method == 'GET':
            return self._transport_error(start_response, 404, 'ROUTE_NOT_FOUND')
        if method != 'POST':
            return self._transport_error(start_response, 405, 'METHOD_NOT_ALLOWED')

        operation_id = self._path_to_operation.get(path)
        if operation_id is None:
            return self._transport_error(start_response, 404, 'ACTION_ROUTE_NOT_FOUND')
        body, error_response = self._read_json_body(environ, start_response)
        if error_response is not None:
            return error_response

        context = HTTPAuthorizationContext(
            method=method,
            path=path,
            operation_id=operation_id,
            headers=_headers_from_environ(environ),
            remote_addr=str(environ.get('REMOTE_ADDR')) if environ.get('REMOTE_ADDR') else None,
        )
        try:
            authorization = _coerce_authorization(self.authorization_resolver(context))
        except Exception as exc:
            return self._transport_error(start_response, 500, 'AUTHORIZATION_RESOLVER_FAILED', str(exc))

        envelope = self.adapter.invoke(operation_id, body or {}, authorization)
        code = _http_code_for_envelope(envelope)
        response_headers: list[tuple[str, str]] = []
        operation = envelope.get('operation') if isinstance(envelope, dict) else None
        if isinstance(operation, dict) and operation.get('operation_id'):
            response_headers.append(('X-CBCC-Operation-Id', str(operation['operation_id'])))
        if code == 202:
            response_headers.append(('Retry-After', str(self.retry_after_seconds)))
            response_headers.append(('X-CBCC-Operation-State', 'PENDING'))
        return self._respond(start_response, code, envelope, response_headers)


def create_plugin_http_application(
    dispatcher: ProviderActionDispatcher,
    *,
    authorization_resolver: AuthorizationResolver | None = None,
    max_request_bytes: int = DEFAULT_MAX_REQUEST_BYTES,
    retry_after_seconds: int = DEFAULT_RETRY_AFTER_SECONDS,
    server_url: str = '/',
) -> PluginHTTPApplication:
    return PluginHTTPApplication(
        PluginActionTransportAdapter(dispatcher),
        authorization_resolver=authorization_resolver,
        max_request_bytes=max_request_bytes,
        retry_after_seconds=retry_after_seconds,
        server_url=server_url,
    )


def make_plugin_http_server(
    dispatcher: ProviderActionDispatcher,
    *,
    host: str = '127.0.0.1',
    port: int = 0,
    authorization_resolver: AuthorizationResolver | None = None,
    max_request_bytes: int = DEFAULT_MAX_REQUEST_BYTES,
    retry_after_seconds: int = DEFAULT_RETRY_AFTER_SECONDS,
    server_url: str = '/',
) -> WSGIServer:
    application = create_plugin_http_application(
        dispatcher,
        authorization_resolver=authorization_resolver,
        max_request_bytes=max_request_bytes,
        retry_after_seconds=retry_after_seconds,
        server_url=server_url,
    )
    return make_server(host, int(port), application)


def serve_plugin_http_host(
    dispatcher: ProviderActionDispatcher,
    *,
    host: str = '127.0.0.1',
    port: int = 8787,
    authorization_resolver: AuthorizationResolver | None = None,
    max_request_bytes: int = DEFAULT_MAX_REQUEST_BYTES,
    retry_after_seconds: int = DEFAULT_RETRY_AFTER_SECONDS,
    server_url: str = '/',
) -> None:
    server = make_plugin_http_server(
        dispatcher,
        host=host,
        port=port,
        authorization_resolver=authorization_resolver,
        max_request_bytes=max_request_bytes,
        retry_after_seconds=retry_after_seconds,
        server_url=server_url,
    )
    try:
        server.serve_forever()
    finally:
        server.server_close()


def plugin_http_contract() -> dict[str, Any]:
    return {
        'version': VERSION,
        'transport': 'WSGI_PLUGIN_OPENAPI',
        'runtime_authority': 'ProviderActionDispatcher',
        'adapter': 'PluginActionTransportAdapter',
        'provider_runtime_imports': 'FORBIDDEN',
        'authorization': {
            'source': 'HOST_HOOK',
            'environment_module': ACTION_AUTH_MODULE_ENV,
            'request_body_credentials': 'FORBIDDEN',
            'default': 'DENY',
        },
        'limits': {
            'default_max_request_bytes': DEFAULT_MAX_REQUEST_BYTES,
            'json_object_required': True,
            'content_type': 'application/json',
        },
        'endpoints': ['/health', '/openapi.json', '/actions.json'],
        'action_routes_source': 'GENERATED_PLUGIN_OPENAPI_DESCRIPTOR',
        'pending_http_status': 202,
    }
