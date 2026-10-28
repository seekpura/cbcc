from pathlib import Path

core_path = Path('runtime/cbcc/mcp_protocol.py')
core = core_path.read_text(encoding='utf-8')
old = """        if not isinstance(params, dict):
            return _jsonrpc_error(request_id, JSONRPC_INVALID_PARAMS, 'params must be an object')

        if method == 'server/discover':
"""
new = """        if not isinstance(params, dict):
            return _jsonrpc_error(request_id, JSONRPC_INVALID_PARAMS, 'params must be an object')

        # Request methods are not valid JSON-RPC notifications. tools/call may trigger external
        # side effects and therefore must never execute without a correlatable request id.
        if request_id is None and method in {'server/discover', 'initialize', 'tools/list', 'tools/call'}:
            return _jsonrpc_error(None, JSONRPC_INVALID_REQUEST, f'{method} requires a JSON-RPC request id')

        if method == 'server/discover':
"""
if old in core:
    core = core.replace(old, new, 1)
elif new not in core:
    raise SystemExit('request-id guard insertion target missing')
core_path.write_text(core, encoding='utf-8')

http_path = Path('runtime/cbcc/mcp_streamable_http.py')
http = http_path.read_text(encoding='utf-8')
old = """    try:
        text.encode('ascii')
    except UnicodeEncodeError as exc:
        raise ValueError('non-ASCII MCP header must use Base64 sentinel encoding') from exc
    if any(ord(char) < 0x20 and char not in {'\\t'} for char in text) or '\\x7f' in text:
        raise ValueError('invalid control character in MCP header')
    return text
"""
new = """    try:
        text.encode('ascii')
    except UnicodeEncodeError as exc:
        raise ValueError('non-ASCII MCP header must use Base64 sentinel encoding') from exc
    if text != text.strip(' \\t'):
        raise ValueError('MCP header values with leading/trailing whitespace must use Base64 sentinel encoding')
    if any(ord(char) < 0x20 and char not in {'\\t'} for char in text) or '\\x7f' in text:
        raise ValueError('invalid control character in MCP header')
    return text
"""
if old in http:
    http = http.replace(old, new, 1)
elif new not in http:
    raise SystemExit('mirrored-header whitespace target missing')
old = """        if str(message.get('method') or '') == 'notifications/cancelled':
            return self._protocol_error(start_response, 400, message.get('id'), JSONRPC_METHOD_NOT_FOUND, 'notifications/cancelled is stdio-only in MCP 2026')

        processor = self._processor_for_request(headers=headers, environ=environ)
"""
new = """        processor = self._processor_for_request(headers=headers, environ=environ)
"""
if old in http:
    http = http.replace(old, new, 1)
elif new not in http:
    raise SystemExit('notifications/cancelled transport target missing')
http_path.write_text(http, encoding='utf-8')

test_path = Path('tests/test_v0621_mcp_streamable_http.py')
test = test_path.read_text(encoding='utf-8')
old = """def test_notifications_cancelled_is_rejected_on_modern_http():
    server, thread, _ = run_server()
    try:
        message = modern_message(None, 'notifications/cancelled', {'requestId': 1})
        status, _, raw = http_request(server, 'POST', message=message, headers=request_headers(message))
        assert status == 400
        assert decode_json(raw)['error']['code'] == -32601
    finally:
        close_server(server, thread)


"""
new = """def test_notifications_cancelled_is_dropped_with_202_on_modern_http():
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


"""
if old in test:
    test = test.replace(old, new, 1)
elif new not in test:
    raise SystemExit('notifications/cancelled test target missing')
append = """

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
"""
if 'test_stdio_tools_call_without_id_is_invalid_request_and_side_effect_free' not in test:
    test = test.rstrip() + append + '\n'
test_path.write_text(test, encoding='utf-8')
