from __future__ import annotations

from copy import deepcopy
from http.client import HTTPConnection
from pathlib import Path
import ast
import base64
import json
import threading

from cbcc.action_transports import mcp_tool_descriptors
from cbcc.host_actions import ActionAuthorization
from cbcc.mcp_protocol import (
    JSONRPC_INVALID_PARAMS,
    MCPProtocolProcessor,
    MCP_AUTHORIZATION_ERROR,
    MCP_UNSUPPORTED_PROTOCOL_VERSION,
    MODERN_PROTOCOL_VERSION,
)
from cbcc.mcp_stdio import MCPStdioServer
from cbcc.mcp_streamable_http import (
    HEADER_MISMATCH,
    MCPStreamableHTTPApplication,
    make_mcp_streamable_http_server,
    mcp_streamable_http_contract,
)
from cbcc.mcp_streamable_http_cli import build_arg_parser


ALL_SCOPES = [
    'PROVIDER_ADAPTER_READ',
    'PROVIDER_STATUS_READ',
    'PROVIDER_EXECUTE',
    'PROVIDER_CANCEL',
    'PROVIDER_RECONCILE',
]


class FakeDispatcher:
    def __init__(self):
        self.calls = []

    def dispatch(self, action_id, payload, authorization=None):
        self.calls.append((action_id, payload, authorization))
        return {
            'version': 'test',
            'action_id': action_id,
            'status': 'SUCCEEDED',
            'result': {'echo': payload},
            'errors': [],
            'authorization': {
                'actor_id': getattr(authorization, 'actor_id', None),
                'decision': 'ALLOW' if getattr(authorization, 'scopes', None) else 'DENY',
            },
        }


def allow_all(context):
    return ActionAuthorization.from_scopes(ALL_SCOPES, actor_id='mcp-http-test')


def modern_meta(version=MODERN_PROTOCOL_VERSION, *, include_capabilities=True):
    meta = {
        'io.modelcontextprotocol/protocolVersion': version,
        'io.modelcontextprotocol/clientInfo': {'name': 'http-test', 'version': '1'},
    }
    if include_capabilities:
        meta['io.modelcontextprotocol/clientCapabilities'] = {}
    return meta


def modern_message(request_id, method, params=None, *, version=MODERN_PROTOCOL_VERSION, include_capabilities=True):
    body = dict(params or {})
    body['_meta'] = modern_meta(version, include_capabilities=include_capabilities)
    message = {'jsonrpc': '2.0', 'method': method, 'params': body}
    if request_id is not None:
        message['id'] = request_id
    return message


def request_headers(message, *, origin=None, version=None, name=None, accept='application/json, text/event-stream', extra=None):
    headers = {
        'Content-Type': 'application/json',
        'Accept': accept,
        'MCP-Protocol-Version': version or message['params']['_meta']['io.modelcontextprotocol/protocolVersion'],
        'Mcp-Method': message['method'],
    }
    body_name = message.get('params', {}).get('name') or message.get('params', {}).get('uri')
    if name is not None:
        headers['Mcp-Name'] = name
    elif body_name is not None:
        headers['Mcp-Name'] = str(body_name)
    if origin is not None:
        headers['Origin'] = origin
    headers.update(extra or {})
    return headers


def run_server(*, authorize=allow_all, allowed_origins=(), stream_selector=None, app_mutator=None):
    dispatcher = FakeDispatcher()
    server = make_mcp_streamable_http_server(
        dispatcher,
        host='127.0.0.1',
        port=0,
        authorization_resolver=authorize,
        allowed_origins=allowed_origins,
        stream_response_selector=stream_selector,
    )
    if app_mutator:
        app_mutator(server.get_app())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, dispatcher


def http_request(server, method, path='/mcp', *, message=None, headers=None, raw_body=None):
    host, port = server.server_address
    connection = HTTPConnection(host, port, timeout=5)
    body = raw_body
    if message is not None:
        body = json.dumps(message, separators=(',', ':')).encode('utf-8')
    connection.request(method, path, body=body, headers=headers or {})
    response = connection.getresponse()
    raw = response.read()
    response_headers = {key.lower(): value for key, value in response.getheaders()}
    connection.close()
    return response.status, response_headers, raw


def decode_json(raw):
    return json.loads(raw.decode('utf-8'))


def close_server(server, thread):
    server.shutdown(); server.server_close(); thread.join(timeout=5)


def test_protocol_core_is_shared_by_stdio_and_http():
    assert issubclass(MCPStdioServer, MCPProtocolProcessor)
    source = Path('runtime/cbcc/mcp_streamable_http.py').read_text(encoding='utf-8')
    assert 'MCPProtocolProcessor' in source
    assert 'def _list_tools' not in source
    assert 'def _call_tool' not in source


def test_modern_tools_list_over_single_mcp_post_returns_json():
    server, thread, dispatcher = run_server()
    try:
        message = modern_message(1, 'tools/list')
        status, headers, raw = http_request(server, 'POST', message=message, headers=request_headers(message))
        payload = decode_json(raw)
        assert status == 200
        assert headers['content-type'].startswith('application/json')
        assert payload['result']['tools'] == mcp_tool_descriptors()
        assert payload['result']['ttlMs'] == 0
        assert payload['result']['cacheScope'] == 'private'
        assert dispatcher.calls == []
    finally:
        close_server(server, thread)


def test_header_body_protocol_method_and_name_mismatch_are_400_header_mismatch():
    server, thread, _ = run_server()
    try:
        message = modern_message(2, 'tools/call', {'name': 'cbcc_provider_adapters_list', 'arguments': {}})
        variants = [
            {**request_headers(message), 'MCP-Protocol-Version': '2025-11-25'},
            {**request_headers(message), 'Mcp-Method': 'tools/list'},
            {**request_headers(message), 'Mcp-Name': 'cbcc_provider_execute'},
        ]
        for headers in variants:
            status, _, raw = http_request(server, 'POST', message=message, headers=headers)
            assert status == 400
            assert decode_json(raw)['error']['code'] == HEADER_MISMATCH
    finally:
        close_server(server, thread)


def test_missing_required_headers_are_400_header_mismatch():
    server, thread, _ = run_server()
    try:
        message = modern_message(3, 'tools/call', {'name': 'cbcc_provider_adapters_list', 'arguments': {}})
        base = request_headers(message)
        for missing in ['MCP-Protocol-Version', 'Mcp-Method', 'Mcp-Name']:
            headers = dict(base); headers.pop(missing)
            status, _, raw = http_request(server, 'POST', message=message, headers=headers)
            assert status == 400
            assert decode_json(raw)['error']['code'] == HEADER_MISMATCH
    finally:
        close_server(server, thread)


def test_unsupported_version_with_matching_body_and_header_returns_32022():
    server, thread, _ = run_server()
    try:
        message = modern_message(4, 'tools/list', version='2099-01-01')
        status, _, raw = http_request(server, 'POST', message=message, headers=request_headers(message))
        payload = decode_json(raw)
        assert status == 400
        assert payload['error']['code'] == MCP_UNSUPPORTED_PROTOCOL_VERSION
        assert payload['error']['data']['supported'] == [MODERN_PROTOCOL_VERSION]
    finally:
        close_server(server, thread)


def test_missing_client_capabilities_is_http_400_invalid_params():
    server, thread, _ = run_server()
    try:
        message = modern_message(5, 'tools/list', include_capabilities=False)
        status, _, raw = http_request(server, 'POST', message=message, headers=request_headers(message))
        assert status == 400
        assert decode_json(raw)['error']['code'] == JSONRPC_INVALID_PARAMS
    finally:
        close_server(server, thread)


def test_origin_is_fail_closed_when_present_and_allowlist_controls_access():
    server, thread, _ = run_server(allowed_origins={'https://allowed.example'})
    try:
        message = modern_message(6, 'tools/list')
        status, _, raw = http_request(server, 'POST', message=message, headers=request_headers(message, origin='https://evil.example'))
        assert status == 403
        assert decode_json(raw)['error']['code'] == MCP_AUTHORIZATION_ERROR
        status, _, raw = http_request(server, 'POST', message=message, headers=request_headers(message, origin='https://allowed.example'))
        assert status == 200
    finally:
        close_server(server, thread)


def test_origin_absent_is_allowed_for_non_browser_clients():
    server, thread, _ = run_server()
    try:
        message = modern_message(7, 'tools/list')
        status, _, _ = http_request(server, 'POST', message=message, headers=request_headers(message))
        assert status == 200
    finally:
        close_server(server, thread)


def test_accept_must_advertise_json_and_event_stream():
    server, thread, _ = run_server()
    try:
        message = modern_message(8, 'tools/list')
        for accept in ['application/json', 'text/event-stream', '*/*', '']:
            status, _, _ = http_request(server, 'POST', message=message, headers=request_headers(message, accept=accept))
            assert status == 406
    finally:
        close_server(server, thread)


def test_get_delete_are_405_and_legacy_session_headers_are_ignored_not_echoed():
    server, thread, _ = run_server()
    try:
        for method in ['GET', 'DELETE']:
            status, _, _ = http_request(server, method, headers={})
            assert status == 405
        message = modern_message(9, 'tools/list')
        headers = request_headers(message, extra={'Mcp-Session-Id': 'legacy-session', 'Last-Event-ID': 'legacy-event'})
        status, response_headers, _ = http_request(server, 'POST', message=message, headers=headers)
        assert status == 200
        assert 'mcp-session-id' not in response_headers
        assert 'last-event-id' not in response_headers
    finally:
        close_server(server, thread)


def test_unknown_method_returns_http_404_with_jsonrpc_method_not_found():
    server, thread, _ = run_server()
    try:
        message = modern_message(10, 'unknown/method')
        status, _, raw = http_request(server, 'POST', message=message, headers=request_headers(message))
        assert status == 404
        assert decode_json(raw)['error']['code'] == -32601
    finally:
        close_server(server, thread)


def test_notification_post_can_be_accepted_as_202_empty_body():
    server, thread, _ = run_server()
    try:
        message = modern_message(None, 'example/notification')
        status, headers, raw = http_request(server, 'POST', message=message, headers=request_headers(message))
        assert status == 202
        assert raw == b''
        assert headers.get('content-length') == '0'
    finally:
        close_server(server, thread)


def test_notifications_cancelled_is_dropped_with_202_on_modern_http():
    server, thread, dispatcher = run_server()
    try:
        message = modern_message(None, 'notifications/cancelled', {'requestId': 1})
        status, headers, raw = http_request(server, 'POST', message=message, headers=request_headers(message))
        assert status == 202
        assert raw == b''
        assert headers.get('content-length') == '0'
        assert dispatcher.calls == []
    finally:
        close_server(server, thread)


def test_request_only_methods_without_id_never_execute_dispatcher():
    server, thread, dispatcher = run_server()
    try:
        message = modern_message(None, 'tools/call', {
            'name': 'cbcc_provider_execute',
            'arguments': {'project_dir': '/tmp/side-effect-must-not-run'},
        })
        status, _, raw = http_request(server, 'POST', message=message, headers=request_headers(message))
        payload = decode_json(raw)
        assert status == 400
        assert payload['error']['code'] == -32600
        assert dispatcher.calls == []
    finally:
        close_server(server, thread)


def test_mcp_name_supports_base64_sentinel_encoding():
    server, thread, dispatcher = run_server()
    try:
        name = 'cbcc_provider_adapters_list'
        message = modern_message(11, 'tools/call', {'name': name, 'arguments': {}})
        encoded = base64.b64encode(name.encode()).decode()
        headers = request_headers(message, name=f'=?base64?{encoded}?=')
        status, _, raw = http_request(server, 'POST', message=message, headers=headers)
        assert status == 200
        assert decode_json(raw)['result']['isError'] is False
        assert dispatcher.calls[0][0] == 'cbcc.provider.adapters.list'
    finally:
        close_server(server, thread)


def test_x_mcp_header_parameter_is_required_and_validated_when_schema_marks_it():
    def mutate(app: MCPStreamableHTTPApplication):
        tool = deepcopy(app._tools['cbcc_provider_execute'])
        schema = tool['inputSchema']
        schema['properties']['adapter_id']['x-mcp-header'] = 'Adapter'
        app._tools['cbcc_provider_execute'] = tool

    server, thread, _ = run_server(app_mutator=mutate)
    try:
        message = modern_message(12, 'tools/call', {
            'name': 'cbcc_provider_execute',
            'arguments': {'project_dir': '/tmp/project', 'adapter_id': 'demo-adapter'},
        })
        status, _, raw = http_request(server, 'POST', message=message, headers=request_headers(message))
        assert status == 400
        assert decode_json(raw)['error']['code'] == HEADER_MISMATCH

        headers = request_headers(message, extra={'Mcp-Param-Adapter': 'demo-adapter'})
        status, _, raw = http_request(server, 'POST', message=message, headers=headers)
        assert status == 200
    finally:
        close_server(server, thread)


def test_request_scoped_sse_can_carry_final_jsonrpc_response_and_disables_proxy_buffering():
    server, thread, _ = run_server(stream_selector=lambda request, response: True)
    try:
        message = modern_message(13, 'tools/list')
        status, headers, raw = http_request(server, 'POST', message=message, headers=request_headers(message))
        assert status == 200
        assert headers['content-type'].startswith('text/event-stream')
        assert headers['x-accel-buffering'] == 'no'
        text = raw.decode('utf-8')
        assert text.startswith('event: message\ndata: ')
        data_line = next(line for line in text.splitlines() if line.startswith('data: '))
        payload = json.loads(data_line[len('data: '):])
        assert payload['result']['tools'] == mcp_tool_descriptors()
    finally:
        close_server(server, thread)


def test_authorization_exception_fails_closed_and_does_not_leak_host_detail():
    def broken(context):
        raise RuntimeError('private-http-auth-detail')

    server, thread, dispatcher = run_server(authorize=broken)
    try:
        message = modern_message(14, 'tools/list')
        status, _, raw = http_request(server, 'POST', message=message, headers=request_headers(message))
        payload = decode_json(raw)
        assert status == 403
        assert payload['error']['code'] == MCP_AUTHORIZATION_ERROR
        assert 'private-http-auth-detail' not in raw.decode('utf-8')
        assert dispatcher.calls == []
    finally:
        close_server(server, thread)


def test_http_module_has_no_direct_provider_runtime_imports_and_contract_is_sessionless():
    source = Path('runtime/cbcc/mcp_streamable_http.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert not any(name.endswith('provider_surface') for name in imported)
    assert not any(name.endswith('provider_bridge') for name in imported)
    assert not any(name.endswith('provider_executor') for name in imported)
    contract = mcp_streamable_http_contract()
    assert contract['endpoint'] == '/mcp'
    assert contract['methods'] == ['POST']
    assert contract['sessions'] == 'NONE'
    assert contract['get_stream_endpoint'] == 'NONE'
    assert contract['last_event_id_resume'] == 'UNSUPPORTED'


def test_http_cli_has_no_credential_or_session_arguments():
    help_text = build_arg_parser().format_help().lower()
    for forbidden in ['api-key', 'api_key', '--token', '--secret', '--password', '--credential', 'session-id']:
        assert forbidden not in help_text

def test_stdio_tools_call_without_id_is_invalid_request_and_side_effect_free():
    dispatcher = FakeDispatcher()
    server = MCPStdioServer(dispatcher, authorization_resolver=allow_all)
    message = modern_message(None, 'tools/call', {
        'name': 'cbcc_provider_execute',
        'arguments': {'project_dir': '/tmp/stdio-side-effect-must-not-run'},
    })
    response = server.handle_message(message)
    assert response['error']['code'] == -32600
    assert dispatcher.calls == []


def test_plain_mirrored_header_whitespace_requires_base64_sentinel():
    from cbcc.mcp_streamable_http import _decode_mirrored_header
    import pytest
    with pytest.raises(ValueError):
        _decode_mirrored_header(' padded ')
    encoded = base64.b64encode(b' padded ').decode()
    assert _decode_mirrored_header(f'=?base64?{encoded}?=') == ' padded '

