from pathlib import Path

source_path = Path('runtime/cbcc/mcp_stdio.py')
source = source_path.read_text(encoding='utf-8')
if Path('runtime/cbcc/mcp_protocol.py').exists():
    raise SystemExit(0)

# Split the transport-neutral processor from stdio-only line framing at the first framing method.
marker = '    def handle_line(self, line: str) -> dict[str, Any] | None:\n'
if marker not in source:
    raise SystemExit('mcp stdio framing marker missing')
core, tail = source.split(marker, 1)

# Make the extracted class and auth resolver explicitly transport-neutral.
core = core.replace("VERSION = '0.6.20-mcp-stdio-host'", "VERSION = '0.6.21-mcp-protocol-core'")
core = core.replace('class MCPStdioServer:', 'class MCPProtocolProcessor:')
core = core.replace(
    "    def __init__(\n        self,\n        dispatcher: ProviderActionDispatcher,\n        *,\n        authorization_resolver: AuthorizationResolver | None = None,\n    ) -> None:\n        self.dispatcher = dispatcher\n        self.authorization_resolver = authorization_resolver or deny_by_default_authorization\n",
    "    def __init__(\n        self,\n        dispatcher: ProviderActionDispatcher,\n        *,\n        authorization_resolver: AuthorizationResolver | None = None,\n        transport_name: str = 'MCP',\n    ) -> None:\n        self.dispatcher = dispatcher\n        self.authorization_resolver = authorization_resolver or deny_by_default_authorization\n        self.transport_name = str(transport_name or 'MCP')\n",
)
core = core.replace(
    "class MCPAuthorizationContext:\n    method: str\n",
    "class MCPAuthorizationContext:\n    transport: str\n    method: str\n",
)
core = core.replace(
    "        context = MCPAuthorizationContext(\n            method=method,\n",
    "        context = MCPAuthorizationContext(\n            transport=self.transport_name,\n            method=method,\n",
)
core = core.replace(
    "            'transport': 'MCP_STDIO',\n            'wire': 'UTF8_NEWLINE_DELIMITED_JSONRPC_2_0',\n",
    "            'transport': self.transport_name,\n",
)
# The environment resolver should relay the processor's transport name instead of hard-coding stdio.
core = core.replace(
    "            transport='MCP_STDIO',\n",
    "            transport=context.transport,\n",
)
# Trim imports that belong only to stdio framing.
core = core.replace('from typing import Any, Callable, IO, Mapping\n', 'from typing import Any, Callable, Mapping\n')
core = core.replace('import sys\n', '')
core += "\n\ndef mcp_protocol_contract() -> dict[str, Any]:\n    return {\n        'version': VERSION,\n        'protocol': 'MCP',\n        'supported_protocol_versions': list(SUPPORTED_PROTOCOL_VERSIONS),\n        'modern_protocol': MODERN_PROTOCOL_VERSION,\n        'modern_discovery': 'server/discover',\n        'legacy_protocol': LEGACY_PROTOCOL_VERSION,\n        'legacy_initialize': True,\n        'tools': [str(tool.get('name') or '') for tool in mcp_tool_descriptors()],\n        'tool_schema_source': 'mcp_tool_descriptors()',\n        'runtime_authority': 'ProviderActionDispatcher',\n        'provider_runtime_direct_access': 'FORBIDDEN',\n        'authorization_default': 'DENY',\n    }\n"
Path('runtime/cbcc/mcp_protocol.py').write_text(core, encoding='utf-8')

stdio = '''from __future__ import annotations

from typing import Any, IO
import json
import sys

from .host_actions import ProviderActionDispatcher
from .mcp_protocol import (
    AuthorizationResolver,
    JSONRPC_INTERNAL_ERROR,
    JSONRPC_INVALID_PARAMS,
    JSONRPC_INVALID_REQUEST,
    JSONRPC_METHOD_NOT_FOUND,
    JSONRPC_PARSE_ERROR,
    LEGACY_PROTOCOL_VERSION,
    MCPAuthorizationContext,
    MCP_AUTHORIZATION_ERROR,
    MCP_AUTH_MODULE_ENV,
    MCP_NOT_INITIALIZED,
    MCP_UNSUPPORTED_PROTOCOL_VERSION,
    MODERN_PROTOCOL_VERSION,
    SUPPORTED_PROTOCOL_VERSIONS,
    MCPProtocolProcessor,
    authorization_resolver_from_environment,
    deny_by_default_authorization,
    mcp_protocol_contract,
)

VERSION = '0.6.21-mcp-stdio-binding'


class MCPStdioServer(MCPProtocolProcessor):
    """Newline framing for the shared transport-neutral MCP protocol processor."""

    def __init__(self, dispatcher: ProviderActionDispatcher, *, authorization_resolver: AuthorizationResolver | None = None) -> None:
        super().__init__(dispatcher, authorization_resolver=authorization_resolver, transport_name='MCP_STDIO')

    def handle_line(self, line: str) -> dict[str, Any] | None:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            return {'jsonrpc': '2.0', 'id': None, 'error': {'code': JSONRPC_PARSE_ERROR, 'message': 'Parse error'}}
        return self.handle_message(message)

    def run(self, stdin: IO[str], stdout: IO[str]) -> None:
        for raw_line in stdin:
            line = raw_line.rstrip('\\r\\n')
            if not line:
                continue
            response = self.handle_line(line)
            if response is None:
                continue
            stdout.write(json.dumps(response, ensure_ascii=False, separators=(',', ':')) + '\\n')
            stdout.flush()


def run_stdio_server(
    dispatcher: ProviderActionDispatcher,
    *,
    authorization_resolver: AuthorizationResolver | None = None,
    stdin: IO[str] | None = None,
    stdout: IO[str] | None = None,
) -> None:
    server = MCPStdioServer(dispatcher, authorization_resolver=authorization_resolver)
    server.run(stdin or sys.stdin, stdout or sys.stdout)


def mcp_stdio_contract() -> dict[str, Any]:
    return {
        **mcp_protocol_contract(),
        'version': VERSION,
        'transport': 'MCP_STDIO',
        'wire': 'UTF8_NEWLINE_DELIMITED_JSONRPC_2_0',
        'authorization': {
            'environment_module': MCP_AUTH_MODULE_ENV,
            'default': 'DENY',
            'request_json_credentials': 'FORBIDDEN_BY_CANONICAL_ACTION_DISPATCH',
        },
    }
'''
source_path.write_text(stdio, encoding='utf-8')
