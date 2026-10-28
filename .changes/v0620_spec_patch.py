from pathlib import Path

runtime = Path('runtime/cbcc/mcp_stdio.py')
text = runtime.read_text(encoding='utf-8')
old = """            'instructions': 'CBCC provider tools use host authorization and canonical action schemas.',\n            'cacheScope': 'private',\n"""
new = """            'instructions': 'CBCC provider tools use host authorization and canonical action schemas.',\n            'ttlMs': 0,\n            'cacheScope': 'private',\n"""
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit('discover cache hint target missing')
old = """            result = _with_modern_meta({'resultType': 'complete', **result, 'cacheScope': 'private'})\n"""
new = """            result = _with_modern_meta({'resultType': 'complete', **result, 'ttlMs': 0, 'cacheScope': 'private'})\n"""
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit('tools/list cache hint target missing')
runtime.write_text(text, encoding='utf-8')

test = Path('tests/test_v0620_mcp_stdio_host.py')
text = test.read_text(encoding='utf-8')
old = """    assert result['capabilities'] == {'tools': {}}\n    assert result['_meta']['io.modelcontextprotocol/serverInfo']['name'] == 'cbcc'\n"""
new = """    assert result['capabilities'] == {'tools': {}}\n    assert result['ttlMs'] == 0\n    assert result['cacheScope'] == 'private'\n    assert result['_meta']['io.modelcontextprotocol/serverInfo']['name'] == 'cbcc'\n"""
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit('discover test target missing')
old = """    assert response['result']['tools'] == mcp_tool_descriptors()\n    assert response['result']['_meta']['io.modelcontextprotocol/serverInfo']['name'] == 'cbcc'\n"""
new = """    assert response['result']['tools'] == mcp_tool_descriptors()\n    assert response['result']['ttlMs'] == 0\n    assert response['result']['cacheScope'] == 'private'\n    assert response['result']['_meta']['io.modelcontextprotocol/serverInfo']['name'] == 'cbcc'\n"""
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit('tools/list test target missing')
test.write_text(text, encoding='utf-8')
