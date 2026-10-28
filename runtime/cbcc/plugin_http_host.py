from __future__ import annotations

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Mapping
import json

from .action_transports import PluginActionTransportAdapter
from .host_actions import ActionAuthorization

VERSION = '0.6.19-plugin-http-host'
DEFAULT_MAX_BODY_BYTES = 1_048_576
DEFAULT_PENDING_RETRY_AFTER_SECONDS = 2


@dataclass(frozen=True)
class HTTPRequestContext:
    method: str
    path: str
    client_host: str | None
    headers: Mapping[str, str]


AuthorizationResolver = Callable[[HTTPRequestContext, str, str], ActionAuthorization | None]


def deny_all_authorization(
    request: HTTPRequestContext,
    operation_id: str,
    required_scope: str,
) -> ActionAuthorization:
    del request, operation_id, required_scope
    return ActionAuthorization()


def plugin_http_host_contract() -> dict[str, Any]:
    return {
        'version': VERSION,
        'transport': 'PLUGIN_OPENAPI_HTTP',
        'runtime_authority': 'PluginActionTransportAdapter -> ProviderActionDispatcher',
        'provider_runtime_direct_access': 'FORBIDDEN',
        'authorization': {
            'source': 'HOST_INJECTED_AUTHORIZATION_RESOLVER',
            'request_body_credentials': 'FORBIDDEN',
            'default': 'DENY',
        },
        'request': {
            'content_type': 'application/json',
            'content_length_required': True,
            'chunked_transfer_encoding': 'UNSUPPORTED',
            'max_body_bytes_default': DEFAULT_MAX_BODY_BYTES,
            'top_level_json_type': 'object',
        },
        'endpoints': {
            'health': '/healthz',
            'openapi_schema': '/schema/openapi.json',
            'host_contract': '/schema/host.json',
        },
        'pending_semantics': {
            'http_status': 202,
            'background_job_database': False,
            'model': 'STATUS_READ + EXPLICIT_RESUME_EXISTING_PROVIDER_STATE',
        },
    }


def _json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def _content_type_is_json(value: str | None) -> bool:
    if not value:
        return False
    media_type = value.split(';', 1)[0].strip().lower()
    return media_type == 'application/json' or media_type.endswith('+json')


def _normalize_path(path: str) -> str:
    raw = str(path or '/').split('?', 1)[0]
    if not raw.startswith('/'):
        raw = '/' + raw
    if len(raw) > 1:
        raw = raw.rstrip('/')
    return raw


class PluginHTTPApplication:
    """Pure HTTP transport over PluginActionTransportAdapter.

    This class never imports or calls ProviderExecutionSurface, ProviderExecutorBridge or
    ProviderExecutor. Provider execution authority stays behind ProviderActionDispatcher.
    """

    def __init__(
        self,
        adapter: PluginActionTransportAdapter,
        *,
        authorization_resolver: AuthorizationResolver | None = None,
        max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
        server_url: str = '/',
        pending_retry_after_seconds: int = DEFAULT_PENDING_RETRY_AFTER_SECONDS,
    ) -> None:
        self.adapter = adapter
        self.authorization_resolver = authorization_resolver or deny_all_authorization
        self.max_body_bytes = max(1, int(max_body_bytes))
        self.server_url = str(server_url or '/')
        self.pending_retry_after_seconds = max(0, int(pending_retry_after_seconds))
        self._openapi = self.adapter.descriptor(server_url=self.server_url)
        self._routes: dict[str, dict[str, Any]] = {}
        self._action_paths: dict[str, str] = {}
        for path, path_item in (self._openapi.get('paths') or {}).items():
            post = (path_item or {}).get('post') if isinstance(path_item, dict) else None
            if not isinstance(post, dict):
                continue
            normalized = _normalize_path(str(path))
            self._routes[normalized] = post
            action_id = str(post.get('x-cbcc-action-id') or '')
            if action_id:
                self._action_paths[action_id] = normalized

    def openapi_descriptor(self) -> dict[str, Any]:
        return json.loads(json.dumps(self._openapi, ensure_ascii=False))

    def health_payload(self) -> dict[str, Any]:
        return {
            'status': 'ok',
            'version': VERSION,
            'transport': 'PLUGIN_OPENAPI_HTTP',
            'runtime_authority': 'PluginActionTransportAdapter -> ProviderActionDispatcher',
            'provider_runtime_direct_access': False,
        }

    def _base_headers(self) -> dict[str, str]:
        return {
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-store',
            'X-Content-Type-Options': 'nosniff',
        }

    def _error(
        self,
        http_status: int,
        code: str,
        *,
        message: str | None = None,
        operation_id: str | None = None,
    ) -> tuple[int, dict[str, str], dict[str, Any]]:
        error: dict[str, Any] = {'code': code}
        if message:
            error['message'] = message
        payload = {
            'version': VERSION,
            'status': 'TRANSPORT_ERROR',
            'operation_id': operation_id,
            'errors': [error],
        }
        return http_status, self._base_headers(), payload

    def handle_get(self, path: str) -> tuple[int, dict[str, str], dict[str, Any]]:
        normalized = _normalize_path(path)
        if normalized == '/healthz':
            return 200, self._base_headers(), self.health_payload()
        if normalized == '/schema/openapi.json':
            return 200, self._base_headers(), self.openapi_descriptor()
        if normalized == '/schema/host.json':
            payload = plugin_http_host_contract()
            payload['max_body_bytes'] = self.max_body_bytes
            payload['pending_retry_after_seconds'] = self.pending_retry_after_seconds
            return 200, self._base_headers(), payload
        return self._error(404, 'HTTP_ROUTE_NOT_FOUND')

    def _resolve_authorization(
        self,
        *,
        operation_id: str,
        required_scope: str,
        path: str,
        headers: Mapping[str, str],
        client_host: str | None,
    ) -> tuple[ActionAuthorization | None, tuple[int, dict[str, str], dict[str, Any]] | None]:
        context = HTTPRequestContext(
            method='POST',
            path=path,
            client_host=client_host,
            headers=dict(headers),
        )
        try:
            authorization = self.authorization_resolver(context, operation_id, required_scope)
        except Exception:
            return None, self._error(403, 'AUTHORIZATION_RESOLUTION_FAILED', operation_id=operation_id)
        if authorization is None:
            authorization = ActionAuthorization()
        if not isinstance(authorization, ActionAuthorization):
            return None, self._error(500, 'AUTHORIZATION_RESOLVER_INVALID_RESULT', operation_id=operation_id)
        return authorization, None

    def _http_status_for_envelope(self, envelope: Mapping[str, Any]) -> int:
        status = str(envelope.get('status') or '').upper()
        return {
            'SUCCEEDED': 200,
            'PENDING': 202,
            'HOLD': 409,
            'DENIED': 403,
            'INVALID_INPUT': 400,
            'INVALID_OPERATION': 404,
            'FAILED': 502,
        }.get(status, 500)

    def _decorate_transport(
        self,
        envelope: dict[str, Any],
        *,
        http_status: int,
        plugin_operation_id: str,
        required_scope: str,
    ) -> dict[str, Any]:
        output = dict(envelope)
        transport: dict[str, Any] = {
            'version': VERSION,
            'http_status': http_status,
            'plugin_operation_id': plugin_operation_id,
            'required_scope': required_scope,
        }
        if http_status == 202:
            status_path = self._action_paths.get('cbcc.provider.status')
            resume_path = self._action_paths.get('cbcc.provider.resume')
            transport.update({
                'pending': True,
                'retry_after_seconds': self.pending_retry_after_seconds,
                'status_path': status_path,
                'resume_path': resume_path,
                'model': 'STATUS_READ + EXPLICIT_RESUME_EXISTING_PROVIDER_STATE',
            })
        output['transport'] = transport
        return output

    def handle_post(
        self,
        path: str,
        *,
        headers: Mapping[str, str],
        body: bytes,
        client_host: str | None = None,
    ) -> tuple[int, dict[str, str], dict[str, Any]]:
        normalized = _normalize_path(path)
        operation = self._routes.get(normalized)
        if operation is None:
            return self._error(404, 'HTTP_ROUTE_NOT_FOUND')

        operation_id = str(operation.get('operationId') or '')
        required_scope = str(operation.get('x-cbcc-permission-scope') or '')
        if not _content_type_is_json(headers.get('Content-Type') or headers.get('content-type')):
            return self._error(415, 'CONTENT_TYPE_MUST_BE_JSON', operation_id=operation_id)
        if len(body) > self.max_body_bytes:
            return self._error(413, 'REQUEST_BODY_TOO_LARGE', operation_id=operation_id)
        try:
            decoded = body.decode('utf-8')
            payload = json.loads(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return self._error(400, 'INVALID_JSON', operation_id=operation_id)
        if not isinstance(payload, dict):
            return self._error(400, 'JSON_BODY_MUST_BE_OBJECT', operation_id=operation_id)

        authorization, auth_error = self._resolve_authorization(
            operation_id=operation_id,
            required_scope=required_scope,
            path=normalized,
            headers=headers,
            client_host=client_host,
        )
        if auth_error is not None:
            return auth_error

        try:
            envelope = self.adapter.invoke(operation_id, payload, authorization)
        except Exception:
            return self._error(500, 'TRANSPORT_ADAPTER_FAILURE', operation_id=operation_id)
        if not isinstance(envelope, dict):
            return self._error(500, 'TRANSPORT_ADAPTER_INVALID_RESULT', operation_id=operation_id)
        http_status = self._http_status_for_envelope(envelope)
        output = self._decorate_transport(
            envelope,
            http_status=http_status,
            plugin_operation_id=operation_id,
            required_scope=required_scope,
        )
        response_headers = self._base_headers()
        if http_status == 202 and self.pending_retry_after_seconds:
            response_headers['Retry-After'] = str(self.pending_retry_after_seconds)
        return http_status, response_headers, output


def make_plugin_http_server(
    application: PluginHTTPApplication,
    *,
    bind: str = '127.0.0.1',
    port: int = 8787,
) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def log_message(self, format: str, *args: Any) -> None:
            # Deliberately suppress BaseHTTPRequestHandler request logging. Authorization headers and
            # payloads belong to the host boundary and must never be emitted by the transport.
            del format, args

        def _write(self, status: int, headers: Mapping[str, str], payload: Any) -> None:
            raw = _json_bytes(payload)
            self.send_response(status)
            for key, value in headers.items():
                self.send_header(str(key), str(value))
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:  # noqa: N802
            status, headers, payload = application.handle_get(self.path)
            self._write(status, headers, payload)

        def do_POST(self) -> None:  # noqa: N802
            transfer_encoding = str(self.headers.get('Transfer-Encoding') or '').strip().lower()
            if transfer_encoding:
                status, headers, payload = application._error(400, 'TRANSFER_ENCODING_UNSUPPORTED')
                self._write(status, headers, payload)
                return
            raw_length = self.headers.get('Content-Length')
            if raw_length is None:
                status, headers, payload = application._error(411, 'CONTENT_LENGTH_REQUIRED')
                self._write(status, headers, payload)
                return
            try:
                length = int(raw_length)
            except ValueError:
                status, headers, payload = application._error(400, 'CONTENT_LENGTH_INVALID')
                self._write(status, headers, payload)
                return
            if length < 0:
                status, headers, payload = application._error(400, 'CONTENT_LENGTH_INVALID')
                self._write(status, headers, payload)
                return
            if length > application.max_body_bytes:
                status, headers, payload = application._error(413, 'REQUEST_BODY_TOO_LARGE')
                self._write(status, headers, payload)
                return
            body = self.rfile.read(length)
            headers_map = {str(key): str(value) for key, value in self.headers.items()}
            client_host = self.client_address[0] if self.client_address else None
            status, headers, payload = application.handle_post(
                self.path,
                headers=headers_map,
                body=body,
                client_host=client_host,
            )
            self._write(status, headers, payload)

        def do_PUT(self) -> None:  # noqa: N802
            status, headers, payload = application._error(405, 'HTTP_METHOD_NOT_ALLOWED')
            headers = dict(headers)
            headers['Allow'] = 'GET, POST'
            self._write(status, headers, payload)

        do_PATCH = do_PUT
        do_DELETE = do_PUT

    return ThreadingHTTPServer((bind, int(port)), Handler)


def serve_plugin_http(
    application: PluginHTTPApplication,
    *,
    bind: str = '127.0.0.1',
    port: int = 8787,
) -> None:
    server = make_plugin_http_server(application, bind=bind, port=port)
    try:
        server.serve_forever()
    finally:
        server.server_close()
