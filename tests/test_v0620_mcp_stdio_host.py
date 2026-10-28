from __future__ import annotations

from io import StringIO
from pathlib import Path
import ast
import json

from cbcc.action_transports import mcp_tool_descriptors
from cbcc.host_actions import ActionAuthorization
from cbcc.mcp_stdio import (
    JSONRPC_INVALID_PARAMS,
    MCP_AUTHORIZATION_ERROR,
    MCP_NOT_INITIALIZED,
    MCP_UNSUPPORTED_PROTOCOL_VERSION,
    LEGACY_PROTOCOL_VERSION,
    MODERN_PROTOCOL_VERSION,
    MCPStdioServer,
    mcp_stdio_contract,
)
from cbcc.mcp_stdio_cli import build_arg_parser


class FakeDispatcher:
    def __init__(self):
        self.calls = []
        self.status = 'SUCCEEDED'

    def dispatch(self, action_id, payload, authorization=None):
        self.calls.append((action_id, payload, authorization))
        result = {
            'version': 'test',
            'action_id': action_id,
            'status': self.status,
            'result': {'echo': payload},
            'errors': [],
            'authorization': {
                'actor_id': getattr(authorization, 'actor_id', None),
                'decision': 'ALLOW' if getattr(authorization, 'scopes', None) else 'DENY',
            },
        }
        if self.status == 'PENDING':
            result['operation'] = {'operation_id': 'OP-mcp-1', 'asset_ids': ['A1']}
            result['result'] = {
                'operation_status': {'status': 'PENDING'},
                'status_action_id': 'cbcc.provider.status',
                'resume_action_id': 'cbcc.provider.resume',
            }
        return result


def modern_meta(version=MODERN_PROTOCOL_VERSION):
    return {
        'io.modelcontextprotocol/protocolVersion': version,
        'io.modelcontextprotocol/clientInfo': {'name': 'pytest-client', 'version': '1.0'},
        'io.modelcontextprotocol/clientCapabilities': {},
    }


def modern_request(request_id, method, params=None, *, version=MODERN_PROTOCOL_VERSION):
    body = dict(params or {})
    body['_meta'] = modern_meta(version)
    return {'jsonrpc': '2.0', 'id': request_id, 'method': method, 'params': body}


def allow_all(context):
    return ActionAuthorization.from_scopes(
        [
            'PROVIDER_ADAPTER_READ',
            'PROVIDER_STATUS_READ',
            'PROVIDER_EXECUTE',
            'PROVIDER_CANCEL',
            'PROVIDER_RECONCILE',
        ],
        actor_id='mcp-test',
    )


def test_modern_server_discover_matches_2026_lifecycle():
    server = MCPStdioServer(FakeDispatcher(), authorization_resolver=allow_all)
    response = server.handle_message(modern_request('d1', 'server/discover'))
    assert response['id'] == 'd1'
    result = response['result']
    assert result['resultType'] == 'complete'
    assert result['supportedVersions'] == [MODERN_PROTOCOL_VERSION]
    assert result['capabilities'] == {'tools': {}}
    assert result['_meta']['io.modelcontextprotocol/serverInfo']['name'] == 'cbcc'


def test_modern_tools_list_is_exact_generated_descriptor_order_and_schema():
    server = MCPStdioServer(FakeDispatcher(), authorization_resolver=allow_all)
    response = server.handle_message(modern_request(1, 'tools/list'))
    assert response['result']['resultType'] == 'complete'
    assert response['result']['tools'] == mcp_tool_descriptors()
    assert response['result']['_meta']['io.modelcontextprotocol/serverInfo']['name'] == 'cbcc'


def test_default_deny_filters_tools_list_without_exposing_unauthorized_tools():
    server = MCPStdioServer(FakeDispatcher())
    response = server.handle_message(modern_request(1, 'tools/list'))
    assert response['result']['tools'] == []


def test_modern_tool_call_maps_to_canonical_action_and_structured_content():
    dispatcher = FakeDispatcher()
    server = MCPStdioServer(dispatcher, authorization_resolver=allow_all)
    tool = next(item for item in mcp_tool_descriptors() if item['name'] == 'cbcc_provider_adapters_list')
    response = server.handle_message(modern_request(
        2,
        'tools/call',
        {'name': tool['name'], 'arguments': {'provider': 'demo'}},
    ))
    result = response['result']
    assert result['resultType'] == 'complete'
    assert result['isError'] is False
    assert result['structuredContent']['action_id'] == tool['x-cbcc-action-id']
    assert json.loads(result['content'][0]['text']) == result['structuredContent']
    assert dispatcher.calls[0][0] == 'cbcc.provider.adapters.list'
    assert dispatcher.calls[0][1] == {'provider': 'demo'}
    assert dispatcher.calls[0][2].actor_id == 'mcp-test'


def test_pending_tool_result_remains_successful_explicit_operation_state():
    dispatcher = FakeDispatcher()
    dispatcher.status = 'PENDING'
    server = MCPStdioServer(dispatcher, authorization_resolver=allow_all)
    response = server.handle_message(modern_request(
        3,
        'tools/call',
        {'name': 'cbcc_provider_execute', 'arguments': {'project_dir': '/tmp/project'}},
    ))
    result = response['result']
    assert result['isError'] is False
    assert result['structuredContent']['status'] == 'PENDING'
    assert result['structuredContent']['operation']['operation_id'] == 'OP-mcp-1'
    assert result['structuredContent']['result']['status_action_id'] == 'cbcc.provider.status'
    assert result['structuredContent']['result']['resume_action_id'] == 'cbcc.provider.resume'


def test_unknown_tool_and_nonobject_arguments_are_protocol_errors():
    server = MCPStdioServer(FakeDispatcher(), authorization_resolver=allow_all)
    response = server.handle_message(modern_request(
        4,
        'tools/call',
        {'name': 'does_not_exist', 'arguments': {}},
    ))
    assert response['error']['code'] == JSONRPC_INVALID_PARAMS
    response = server.handle_message(modern_request(
        5,
        'tools/call',
        {'name': 'cbcc_provider_adapters_list', 'arguments': ['bad']},
    ))
    assert response['error']['code'] == JSONRPC_INVALID_PARAMS


def test_modern_request_requires_supported_protocol_and_client_capabilities():
    server = MCPStdioServer(FakeDispatcher(), authorization_resolver=allow_all)
    unsupported = server.handle_message(modern_request(6, 'tools/list', version='1900-01-01'))
    assert unsupported['error']['code'] == MCP_UNSUPPORTED_PROTOCOL_VERSION
    assert unsupported['error']['data']['supported'] == [MODERN_PROTOCOL_VERSION]

    missing_caps_meta = {
        'io.modelcontextprotocol/protocolVersion': MODERN_PROTOCOL_VERSION,
        'io.modelcontextprotocol/clientInfo': {'name': 'x', 'version': '1'},
    }
    response = server.handle_message({
        'jsonrpc': '2.0',
        'id': 7,
        'method': 'tools/list',
        'params': {'_meta': missing_caps_meta},
    })
    assert response['error']['code'] == JSONRPC_INVALID_PARAMS


def test_uninitialized_request_without_modern_meta_is_rejected():
    server = MCPStdioServer(FakeDispatcher(), authorization_resolver=allow_all)
    response = server.handle_message({'jsonrpc': '2.0', 'id': 8, 'method': 'tools/list', 'params': {}})
    assert response['error']['code'] == MCP_NOT_INITIALIZED


def test_legacy_initialize_initialized_then_list_and_call():
    dispatcher = FakeDispatcher()
    server = MCPStdioServer(dispatcher, authorization_resolver=allow_all)
    initialized = server.handle_message({
        'jsonrpc': '2.0',
        'id': 'init',
        'method': 'initialize',
        'params': {
            'protocolVersion': LEGACY_PROTOCOL_VERSION,
            'capabilities': {},
            'clientInfo': {'name': 'legacy-client', 'version': '1'},
        },
    })
    assert initialized['result']['protocolVersion'] == LEGACY_PROTOCOL_VERSION
    assert initialized['result']['capabilities'] == {'tools': {}}
    assert server.handle_message({
        'jsonrpc': '2.0',
        'method': 'notifications/initialized',
        'params': {},
    }) is None

    listed = server.handle_message({'jsonrpc': '2.0', 'id': 9, 'method': 'tools/list', 'params': {}})
    assert listed['result']['tools'] == mcp_tool_descriptors()
    assert 'resultType' not in listed['result']

    called = server.handle_message({
        'jsonrpc': '2.0',
        'id': 10,
        'method': 'tools/call',
        'params': {'name': 'cbcc_provider_adapters_list', 'arguments': {}},
    })
    assert called['result']['isError'] is False
    assert 'resultType' not in called['result']


def test_modern_protocol_sent_to_legacy_initialize_is_rejected_with_migration_signal():
    server = MCPStdioServer(FakeDispatcher(), authorization_resolver=allow_all)
    response = server.handle_message({
        'jsonrpc': '2.0',
        'id': 11,
        'method': 'initialize',
        'params': {'protocolVersion': MODERN_PROTOCOL_VERSION, 'capabilities': {}, 'clientInfo': {}},
    })
    assert response['error']['code'] == MCP_UNSUPPORTED_PROTOCOL_VERSION
    assert MODERN_PROTOCOL_VERSION in response['error']['data']['supported']


def test_authorization_resolver_failure_is_fail_closed_and_redacted():
    def broken(context):
        raise RuntimeError('mcp-host-secret-detail')

    server = MCPStdioServer(FakeDispatcher(), authorization_resolver=broken)
    response = server.handle_message(modern_request(12, 'tools/list'))
    assert response['error']['code'] == MCP_AUTHORIZATION_ERROR
    serialized = json.dumps(response, ensure_ascii=False)
    assert 'mcp-host-secret-detail' not in serialized


def test_stdio_framing_is_one_jsonrpc_object_per_output_line_and_notifications_are_silent():
    server = MCPStdioServer(FakeDispatcher(), authorization_resolver=allow_all)
    inputs = StringIO(
        '{bad json}\n'
        + json.dumps(modern_request('d', 'server/discover'), separators=(',', ':')) + '\n'
        + json.dumps({'jsonrpc': '2.0', 'method': 'unknown/notification', 'params': {'_meta': modern_meta()}}, separators=(',', ':')) + '\n'
    )
    outputs = StringIO()
    server.run(inputs, outputs)
    lines = outputs.getvalue().splitlines()
    assert len(lines) == 2
    parsed = [json.loads(line) for line in lines]
    assert parsed[0]['error']['code'] == -32700
    assert parsed[1]['result']['supportedVersions'] == [MODERN_PROTOCOL_VERSION]
    assert all('\n' not in line for line in lines)


def test_transport_module_has_no_direct_provider_runtime_imports():
    source = Path('runtime/cbcc/mcp_stdio.py').read_text(encoding='utf-8')
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
    contract = mcp_stdio_contract()
    assert contract['runtime_authority'] == 'ProviderActionDispatcher'
    assert contract['modern_protocol'] == MODERN_PROTOCOL_VERSION
    assert contract['legacy_protocol'] == LEGACY_PROTOCOL_VERSION


def test_stdio_cli_has_no_credential_arguments():
    help_text = build_arg_parser().format_help().lower()
    for forbidden in ['api-key', 'api_key', '--token', '--secret', '--password', '--credential']:
        assert forbidden not in help_text
