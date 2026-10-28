from __future__ import annotations

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
            line = raw_line.rstrip('\r\n')
            if not line:
                continue
            response = self.handle_line(line)
            if response is None:
                continue
            stdout.write(json.dumps(response, ensure_ascii=False, separators=(',', ':')) + '\n')
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
