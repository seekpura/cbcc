from __future__ import annotations

from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import ast
import json
import sys
import types

from cbcc.action_transports import plugin_openapi_descriptor
from cbcc.host_actions import (
    ACTION_ADAPTER_LIST,
    ActionAuthorization,
    ProviderActionDispatcher,
    SCOPE_ADAPTER_READ,
)
from cbcc.plugin_http import (
    ACTION_AUTH_MODULE_ENV,
    HTTPAuthorizationContext,
    authorization_resolver_from_environment,
    create_plugin_http_application,
    make_plugin_http_server,
    plugin_http_contract,
)


class FakeSurface:
    def __init__(self):
        self.calls = []

    def list_adapters(self, *, provider=None, production_mode=None, required_capabilities=None):
        self.calls.append((provider, production_mode, required_capabilities))
        return {'status': 'ADAPTERS_DISCOVERED', 'count': 0, 'adapters': []}


class PendingDispatcher:
    def dispatch(self, action_id, payload, authorization=None):
        return {
            'version': 'stub',
            'action_id': action_id,
            'status': 'PENDING',
            'result': {'status_action_id': 'cbcc.provider.status', 'resume_action_id': 'cbcc.provider.resume'},
            'errors': [],
            'authorization': {'actor_id': getattr(authorization, 'actor_id', None), 'decision': 'ALLOW'},
            'operation': {'operation_id': 'OP-live-123'},
        }


def _path_for(action_id: str) -> str:
    descriptor = plugin_openapi_descriptor()
    for path, item in descriptor['paths'].items():
        post = item.get('post') or {}
        if post.get('x-cbcc-action-id') == action_id:
            return path
    raise AssertionError(action_id)


def _request(base: str, path: str, *, method='GET', body=None, headers=None):
    data = None if body is None else json.dumps(body).encode('utf-8')
    req_headers = dict(headers or {})
    if data is not None:
        req_headers.setdefault('Content-Type', 'application/json')
    request = Request(base + path, data=data, headers=req_headers, method=method)
    try:
        response = urlopen(request, timeout=5)
        payload = json.loads(response.read().decode('utf-8'))
        return response.status, {k.lower(): v for k, v in response.headers.items()}, payload
    except HTTPError as exc:
        payload = json.loads(exc.read().decode('utf-8'))
        return exc.code, {k.lower(): v for k, v in exc.headers.items()}, payload


def _run_server(server):
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread, f'http://127.0.0.1:{server.server_port}'


def test_health_and_schema_endpoints_are_live():
    surface = FakeSurface()
    dispatcher = ProviderActionDispatcher(surface)
    server = make_plugin_http_server(dispatcher, host='127.0.0.1', port=0)
    thread, base = _run_server(server)
    try:
        code, _, health = _request(base, '/health')
        assert code == 200
        assert health['status'] == 'OK'
        assert health['runtime_authority'] == 'ProviderActionDispatcher'

        code, _, schema = _request(base, '/openapi.json')
        assert code == 200
        assert schema['openapi'] == '3.1.0'
        assert schema['x-cbcc-runtime'] == 'ProviderActionDispatcher'

        code, _, actions = _request(base, '/actions.json')
        assert code == 200
        assert actions['actions']
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_default_authorization_is_deny_and_host_hook_can_allow():
    path = _path_for(ACTION_ADAPTER_LIST)

    denied_surface = FakeSurface()
    denied_server = make_plugin_http_server(ProviderActionDispatcher(denied_surface), host='127.0.0.1', port=0)
    thread, base = _run_server(denied_server)
    try:
        code, _, payload = _request(base, path, method='POST', body={})
        assert code == 403
        assert payload['status'] == 'DENIED'
        assert denied_surface.calls == []
    finally:
        denied_server.shutdown(); denied_server.server_close(); thread.join(timeout=5)

    allowed_surface = FakeSurface()
    seen = []

    def resolver(context: HTTPAuthorizationContext):
        seen.append(context)
        assert context.headers.get('X-Host-Identity') == 'operator-7'
        return ActionAuthorization.from_scopes([SCOPE_ADAPTER_READ], actor_id='operator-7')

    allowed_server = make_plugin_http_server(
        ProviderActionDispatcher(allowed_surface),
        host='127.0.0.1',
        port=0,
        authorization_resolver=resolver,
    )
    thread, base = _run_server(allowed_server)
    try:
        code, _, payload = _request(
            base,
            path,
            method='POST',
            body={},
            headers={'X-Host-Identity': 'operator-7'},
        )
        assert code == 200
        assert payload['status'] == 'SUCCEEDED'
        assert payload['authorization']['actor_id'] == 'operator-7'
        assert allowed_surface.calls == [(None, None, None)]
        assert len(seen) == 1
    finally:
        allowed_server.shutdown(); allowed_server.server_close(); thread.join(timeout=5)


def test_pending_dispatch_maps_to_202_and_operation_headers():
    path = _path_for(ACTION_ADAPTER_LIST)
    server = make_plugin_http_server(
        PendingDispatcher(),
        host='127.0.0.1',
        port=0,
        authorization_resolver=lambda context: ActionAuthorization.from_scopes([SCOPE_ADAPTER_READ], actor_id='host'),
        retry_after_seconds=3,
    )
    thread, base = _run_server(server)
    try:
        code, headers, payload = _request(base, path, method='POST', body={})
        assert code == 202
        assert payload['status'] == 'PENDING'
        assert headers['retry-after'] == '3'
        assert headers['x-cbcc-operation-id'] == 'OP-live-123'
        assert headers['x-cbcc-operation-state'] == 'PENDING'
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)


def test_transport_validates_json_media_type_object_and_size():
    surface = FakeSurface()
    dispatcher = ProviderActionDispatcher(surface)
    path = _path_for(ACTION_ADAPTER_LIST)
    app = create_plugin_http_application(dispatcher, max_request_bytes=8)

    from io import BytesIO

    def call(raw: bytes, *, content_type='application/json', content_length=None):
        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': path,
            'CONTENT_TYPE': content_type,
            'CONTENT_LENGTH': str(len(raw) if content_length is None else content_length),
            'wsgi.input': BytesIO(raw),
        }
        captured = {}
        def start_response(status, headers):
            captured['status'] = status
            captured['headers'] = headers
        body = b''.join(app(environ, start_response))
        return int(captured['status'].split()[0]), json.loads(body.decode('utf-8'))

    code, payload = call(b'{bad}')
    assert code == 400 and payload['errors'][0]['code'] == 'JSON_INVALID'
    code, payload = call(b'[]')
    assert code == 422 and payload['errors'][0]['code'] == 'JSON_OBJECT_REQUIRED'
    code, payload = call(b'{}', content_type='text/plain')
    assert code == 415 and payload['errors'][0]['code'] == 'CONTENT_TYPE_JSON_REQUIRED'
    code, payload = call(b'{"x":123456789}')
    assert code == 413 and payload['errors'][0]['code'] == 'REQUEST_BODY_TOO_LARGE'


def test_authorization_module_is_host_injected_and_not_payload_driven(monkeypatch):
    module_name = 'cbcc_test_auth_module_v0619'
    module = types.ModuleType(module_name)

    def resolve_action_authorization(**kwargs):
        assert kwargs['headers']['Authorization'] == 'Bearer opaque-host-token'
        return {'actor_id': 'host-user', 'scopes': [SCOPE_ADAPTER_READ]}

    module.resolve_action_authorization = resolve_action_authorization
    monkeypatch.setitem(sys.modules, module_name, module)
    resolver = authorization_resolver_from_environment(env={ACTION_AUTH_MODULE_ENV: module_name})
    authorization = resolver(HTTPAuthorizationContext(
        method='POST',
        path='/actions/provider/adapters-list',
        operation_id='listProviderAdapters',
        headers={'Authorization': 'Bearer opaque-host-token'},
        remote_addr='127.0.0.1',
    ))
    assert authorization.actor_id == 'host-user'
    assert authorization.allows(SCOPE_ADAPTER_READ)


def test_transport_module_does_not_import_provider_runtime_layers():
    source_path = Path(__file__).resolve().parents[1] / 'runtime/cbcc/plugin_http.py'
    tree = ast.parse(source_path.read_text(encoding='utf-8'))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert not any(name.endswith('provider_surface') for name in imported)
    assert not any(name.endswith('provider_bridge') for name in imported)
    assert not any(name.endswith('provider_executor') for name in imported)
    contract = plugin_http_contract()
    assert contract['runtime_authority'] == 'ProviderActionDispatcher'
    assert contract['authorization']['default'] == 'DENY'
