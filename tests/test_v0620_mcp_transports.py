from __future__ import annotations

from pathlib import Path
import os
import sys

import anyio
import httpx2
from mcp import Client, StdioServerParameters
from mcp.client.streamable_http import streamable_http_client

from cbcc.action_transports import mcp_tool_descriptors
from cbcc.host_actions import ActionAuthorization, ProviderActionDispatcher, SCOPE_ADAPTER_READ
from cbcc.mcp_host import create_mcp_host


class FakeSurface:
    def list_adapters(self, *, provider=None, production_mode=None, required_capabilities=None):
        return {'status': 'ADAPTERS_DISCOVERED', 'count': 0, 'adapters': []}


def test_streamable_http_carries_headers_to_host_resolver_without_trusting_them_directly():
    seen = []

    def resolver(context):
        seen.append(context)
        normalized = {str(k).lower(): str(v) for k, v in context.headers.items()}
        assert normalized.get('x-host-identity') == 'operator-42'
        assert context.transport == 'streamable-http'
        return ActionAuthorization.from_scopes([SCOPE_ADAPTER_READ], actor_id='verified-operator-42')

    async def scenario():
        host = create_mcp_host(
            ProviderActionDispatcher(FakeSurface()),
            authorization_resolver=resolver,
        )
        app = host.streamable_http_app(
            host='127.0.0.1',
            path='/mcp',
            json_response=True,
            stateless_http=True,
        )
        url = 'http://127.0.0.1/mcp'
        transport = httpx2.ASGITransport(app=app)
        async with host.server.session_manager.run():
            async with httpx2.AsyncClient(
                transport=transport,
                base_url='http://127.0.0.1',
                headers={'X-Host-Identity': 'operator-42'},
            ) as http_client:
                async with Client(streamable_http_client(url, http_client=http_client)) as client:
                    assert client.protocol_version == '2026-07-28'
                    listed = await client.list_tools()
                    assert [tool.name for tool in listed.tools] == ['cbcc_provider_adapters_list']
                    result = await client.call_tool('cbcc_provider_adapters_list', {})
                    assert result.is_error is False
                    assert result.structured_content['authorization']['actor_id'] == 'verified-operator-42'

        assert any(context.method == 'tools/list' for context in seen)
        assert any(context.method == 'tools/call' for context in seen)

    anyio.run(scenario)


def test_stdio_cli_is_real_mcp_server_and_host_module_can_authorize(tmp_path):
    module_name = 'cbcc_test_mcp_stdio_auth'
    module_path = tmp_path / f'{module_name}.py'
    module_path.write_text(
        "def resolve_mcp_action_authorization(**kwargs):\n"
        "    return {'actor_id': 'stdio-host', 'scopes': ['PROVIDER_ADAPTER_READ']}\n",
        encoding='utf-8',
    )
    repo_root = Path(__file__).resolve().parents[1]
    runtime_dir = repo_root / 'runtime'
    env = {
        'PYTHONPATH': os.pathsep.join([str(runtime_dir), str(tmp_path)]),
        'CBCC_MCP_AUTH_MODULE': module_name,
    }

    async def scenario():
        parameters = StdioServerParameters(
            command=sys.executable,
            args=['-m', 'cbcc.mcp_host_cli', '--transport', 'stdio'],
            env=env,
        )
        async with Client(parameters) as client:
            assert client.protocol_version == '2026-07-28'
            listed = await client.list_tools()
            assert [tool.name for tool in listed.tools] == ['cbcc_provider_adapters_list']
            result = await client.call_tool('cbcc_provider_adapters_list', {})
            assert result.is_error is False
            assert result.structured_content['authorization']['actor_id'] == 'stdio-host'

    anyio.run(scenario)


def test_mcp_tool_order_matches_generated_descriptor_order():
    names = [row['name'] for row in mcp_tool_descriptors()]
    assert names == sorted(names)
