from pathlib import Path

plugin = Path('runtime/cbcc/plugin_http.py')
text = plugin.read_text(encoding='utf-8')
old_auth = """        try:\n            authorization = _coerce_authorization(self.authorization_resolver(context))\n        except Exception as exc:\n            return self._transport_error(start_response, 500, 'AUTHORIZATION_RESOLVER_FAILED', str(exc))\n"""
new_auth = """        try:\n            authorization = _coerce_authorization(self.authorization_resolver(context))\n        except Exception:\n            return self._transport_error(start_response, 403, 'AUTHORIZATION_RESOLVER_FAILED')\n"""
if old_auth in text:
    text = text.replace(old_auth, new_auth)
elif new_auth not in text:
    raise SystemExit('authorization hardening target not found')
plugin.write_text(text, encoding='utf-8')

test = Path('tests/test_v0619_plugin_http_host.py')
text = test.read_text(encoding='utf-8')
normalized = """        normalized_headers = {str(key).lower(): value for key, value in headers.items()}\n        assert normalized_headers['retry-after'] == '3'\n        assert normalized_headers['x-cbcc-operation-id'] == 'OP-live-123'\n        assert normalized_headers['x-cbcc-operation-state'] == 'PENDING'\n"""
variants = [
    """        assert headers['Retry-After'] == '3'\n        assert headers['X-Cbcc-Operation-Id'] == 'OP-live-123'\n        assert headers['X-Cbcc-Operation-State'] == 'PENDING'\n""",
    """        assert headers['retry-after'] == '3'\n        assert headers['x-cbcc-operation-id'] == 'OP-live-123'\n        assert headers['x-cbcc-operation-state'] == 'PENDING'\n""",
]
if normalized not in text:
    for candidate in variants:
        if candidate in text:
            text = text.replace(candidate, normalized)
            break
    else:
        raise SystemExit('header normalization target not found')

marker = "\ndef test_transport_module_does_not_import_provider_runtime_layers():\n"
extra = """\ndef test_authorization_resolver_exception_fails_closed_without_detail_leak():\n    path = _path_for(ACTION_ADAPTER_LIST)\n    dispatcher = ProviderActionDispatcher(FakeSurface())\n\n    def broken_resolver(context):\n        raise RuntimeError('opaque-sensitive-auth-detail')\n\n    server = make_plugin_http_server(\n        dispatcher,\n        host='127.0.0.1',\n        port=0,\n        authorization_resolver=broken_resolver,\n    )\n    thread, base = _run_server(server)\n    try:\n        code, _, payload = _request(base, path, method='POST', body={})\n        assert code == 403\n        serialized = json.dumps(payload, ensure_ascii=False)\n        assert 'opaque-sensitive-auth-detail' not in serialized\n        assert payload['errors'][0]['code'] == 'AUTHORIZATION_RESOLVER_FAILED'\n    finally:\n        server.shutdown(); server.server_close(); thread.join(timeout=5)\n\n"""
if 'test_authorization_resolver_exception_fails_closed_without_detail_leak' not in text:
    if marker not in text:
        raise SystemExit('test insertion marker not found')
    text = text.replace(marker, extra + marker)
test.write_text(text, encoding='utf-8')
