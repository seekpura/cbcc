from pathlib import Path

path = Path('runtime/cbcc/mcp_streamable_http.py')
text = path.read_text(encoding='utf-8')
if 'import re\n' not in text:
    text = text.replace('import os\n', 'import os\nimport re\n')
text = text.replace(
    '    JSONRPC_INVALID_REQUEST,\n    JSONRPC_METHOD_NOT_FOUND,\n',
    '    JSONRPC_INVALID_PARAMS,\n    JSONRPC_INVALID_REQUEST,\n    JSONRPC_METHOD_NOT_FOUND,\n',
)
old = """                    if not annotation or normalized in seen_headers:\n                        return None, _jsonrpc_error(request_id, HEADER_MISMATCH, 'Header mismatch: invalid x-mcp-header annotation')\n"""
new = """                    if (\n                        not annotation\n                        or normalized in seen_headers\n                        or re.fullmatch(r\"[!#$%&'*+\\-.^_`|~0-9A-Za-z]+\", annotation) is None\n                    ):\n                        return None, _jsonrpc_error(request_id, HEADER_MISMATCH, 'Header mismatch: invalid x-mcp-header annotation')\n"""
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit('x-mcp-header validation target missing')
old = """        if code in {HEADER_MISMATCH, MCP_UNSUPPORTED_PROTOCOL_VERSION, JSONRPC_INVALID_REQUEST}:\n            return 400\n"""
new = """        if code in {HEADER_MISMATCH, MCP_UNSUPPORTED_PROTOCOL_VERSION, JSONRPC_INVALID_REQUEST, JSONRPC_INVALID_PARAMS}:\n            return 400\n"""
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit('HTTP protocol error mapping target missing')
path.write_text(text, encoding='utf-8')
