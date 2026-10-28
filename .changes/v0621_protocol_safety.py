from pathlib import Path

core_path = Path('runtime/cbcc/mcp_protocol.py')
core = core_path.read_text(encoding='utf-8')
old = """        if not isinstance(params, dict):\n            return _jsonrpc_error(request_id, JSONRPC_INVALID_PARAMS, 'params must be an object')\n\n        if method == 'server/discover':\n"""
new = """        if not isinstance(params, dict):\n            return _jsonrpc_error(request_id, JSONRPC_INVALID_PARAMS, 'params must be an object')\n\n        # MCP request methods are not valid JSON-RPC notifications. In particular, tools/call\n        # may trigger external side effects and must never execute without a correlatable request id.\n        if request_id is None and method in {'server/discover', 'initialize', 'tools/list', 'tools/call'}:\n            return _jsonrpc_error(None, JSONRPC_INVALID_REQUEST, f'{method} requires a JSON-RPC request id')\n\n        if method == 'server/discover':\n"""
if old in core:
    core = core.replace(old, new, 1)
elif new not in core:
    raise SystemExit('request-id guard insertion target missing')
core_path.write_text(core, encoding='utf-8')

http_path = Path('runtime/cbcc/mcp_streamable_http.py')
http = http_path.read_text(encoding='utf-8')
old = """    try:\n        text.encode('ascii')\n    except UnicodeEncodeError as exc:\n        raise ValueError('non-ASCII MCP header must use Base64 sentinel encoding') from exc\n    if any(ord(char) < 0x20 and char not in {'\\t'} for char in text) or '\\x7f' in text:\n        raise ValueError('invalid control character in MCP header')\n    return text\n"""
new = """    try:\n        text.encode('ascii')\n    except UnicodeEncodeError as exc:\n        raise ValueError('non-ASCII MCP header must use Base64 sentinel encoding') from exc\n    if text != text.strip(' \\t'):\n        raise ValueError('MCP header values with leading/trailing whitespace must use Base64 sentinel encoding')\n    if any(ord(char) < 0x20 and char not in {'\\t'} for char in text) or '\\x7f' in text:\n        raise ValueError('invalid control character in MCP header')\n    return text\n"""
if old in http:
    http = http.replace(old, new, 1)
elif new not in http:
    raise SystemExit('mirrored-header whitespace target missing')
old = """        if str(message.get('method') or '') == 'notifications/cancelled':\n            return self._protocol_error(start_response, 400, message.get('id'), JSONRPC_METHOD_NOT_FOUND, 'notifications/cancelled is stdio-only in MCP 2026')\n\n        processor = self._processor_for_request(headers=headers, environ=environ)\n"""
new = """        processor = self._processor_for_request(headers=headers, environ=environ)\n"""
if old in http:
    http = http.replace(old, new, 1)
elif old not in http and new not in http:
    raise SystemExit('notifications/cancelled transport target missing')
http_path.write_text(http, encoding='utf-8')

test_path = Path('tests/test_v0621_mcp_streamable_http.py')
test = test_path.read_text(encoding='utf-8')
old = """def test_notifications_cancelled_is_rejected_on_modern_http():\n    server, thread, _ = run_server()\n    try:\n        message = modern_message(None, 'notifications/cancelled', {'requestId': 1})\n        status, _, raw = http_request(server, 'POST', message=message, headers=request_headers(message))\n        assert status == 400\n        assert decode_json(raw)['error']['code'] == -32601\n    finally:\n        close_server(server, thread)\n\n\n"""
new = """def test_notifications_cancelled_is_dropped_with_202_on_modern_http():\n    server, thread, dispatcher = run_server()\n    try:\n        message = modern_message(None, 'notifications/cancelled', {'requestId': 1})\n        status, headers, raw = http_request(server, 'POST', message=message, headers=request_headers(message))\n        assert status == 202\n        assert raw == b''\n        assert headers.get('content-length') == '0'\n        assert dispatcher.calls == []\n    finally:\n        close_server(server, thread)\n\n\ndef test_request_only_methods_without_id_never_execute_dispatcher():\n    server, thread, dispatcher = run_server()\n    try:\n        message = modern_message(None, 'tools/call', {\n            'name': 'cbcc_provider_execute',\n            'arguments': {'project_dir': '/tmp/side-effect-must-not-run'},\n        })\n        status, _, raw = http_request(server, 'POST', message=message, headers=request_headers(message))\n        payload = decode_json(raw)\n        assert status == 400\n        assert payload['error']['code'] == -32600\n        assert dispatcher.calls == []\n    finally:\n        close_server(server, thread)\n\n\n"""
if old in test:
    test = test.replace(old, new, 1)
elif new not in test:
    raise SystemExit('notifications/cancelled test target missing')
append = """\n\ndef test_stdio_tools_call_without_id_is_invalid_request_and_side_effect_free():\n    dispatcher = FakeDispatcher()\n    server = MCPStdioServer(dispatcher, authorization_resolver=allow_all)\n    message = modern_message(None, 'tools/call', {\n        'name': 'cbcc_provider_execute',\n        'arguments': {'project_dir': '/tmp/stdio-side-effect-must-not-run'},\n    })\n    response = server.handle_message(message)\n    assert response['error']['code'] == -32600\n    assert dispatcher.calls == []\n\n\ndef test_plain_mirrored_header_whitespace_requires_base64_sentinel():\n    from cbcc.mcp_streamable_http import _decode_mirrored_header\n    import pytest\n    with pytest.raises(ValueError):\n        _decode_mirrored_header(' padded ')\n    encoded = base64.b64encode(b' padded ').decode()\n    assert _decode_mirrored_header(f'=?base64?{encoded}?=') == ' padded '\n"""
if 'test_stdio_tools_call_without_id_is_invalid_request_and_side_effect_free' not in test:
    test = test.rstrip() + append + '\n'
test_path.write_text(test, encoding='utf-8')
