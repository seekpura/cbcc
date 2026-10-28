from __future__ import annotations

from pathlib import Path
import ast
import json

import anyio
from mcp import Client

from cbcc.action_transports import mcp_tool_descriptors
from cbcc.host_actions import ActionAuthorization, ProviderActionDispatcher
from cbcc.mcp_host import create_mcp_host, mcp_host_contract


ALL_SCOPES = sorted({str(row['x-cbcc-permission-scope']) for row in mcp_tool_descriptors()})


class FakeSurface:
    def __init__(self):
        self.execute_calls = []

    def list_adapters(self, *, provider=None, production_mode=None, required_capabilities=None):
        return {
            'status': 'ADAPTERS_DISCOVERED',
            'count': 1,
            'adapters': [{'adapter_id': 'fake.adapter', 'provider': provider or 'FAKE'}],
        }

    def execute_project(self, project_dir, *, asset_ids=None, adapter_id=None, policy=None):
        self.execute_calls.append({
            'project_dir': str(project_dir),
            'asset_ids': list(asset_ids or []),
            'adapter_id': adapter_id,
        })
        return {'status': 'PROVIDER_EXECUTION_INCOMPLETE', 'jobs': [], 'counts': {'PENDING': 1}}


def allow_all(_context):
    return ActionAuthorization.from_scopes(ALL_SCOPES, actor_id='mcp-test-host')


def _tool_map(tools):
    return {tool.name: tool for tool in tools}


def test_inprocess_client_uses_current_protocol_and_exact_canonical_tools():
    async def scenario():
        host = create_mcp_host(
            ProviderActionDispatcher(FakeSurface()),
            authorization_resolver=allow_all,
        )
        async with Client(host.server) as client:
            assert client.protocol_version == '2026-07-28'
            assert client.server_capabilities.tools is not None
            listed = await client.list_tools()
            by_name = _tool_map(listed.tools)
            canonical = {row['name']: row for row in mcp_tool_descriptors()}
            assert list(by_name) == list(canonical)
            for name, row in canonical.items():
                assert by_name[name].description == row['description']
                assert by_name[name].input_schema == row['inputSchema']

            result = await client.call_tool('cbcc_provider_adapters_list', {})
            assert result.is_error is False
            assert result.structured_content['status'] == 'SUCCEEDED'
            assert result.structured_content['authorization']['actor_id'] == 'mcp-test-host'
            assert result.structured_content['result']['count'] == 1

    anyio.run(scenario)


def test_default_deny_hides_tools_and_denies_direct_known_call():
    async def scenario():
        host = create_mcp_host(ProviderActionDispatcher(FakeSurface()))
        async with Client(host.server) as client:
            listed = await client.list_tools()
            assert listed.tools == []
            result = await client.call_tool('cbcc_provider_adapters_list', {})
            assert result.is_error is True
            assert result.structured_content['status'] == 'DENIED'
            assert result.structured_content['errors'][0]['code'] == 'ACTION_SCOPE_REQUIRED'

    anyio.run(scenario)


def test_secret_like_action_fields_remain_forbidden_through_mcp():
    async def scenario():
        host = create_mcp_host(
            ProviderActionDispatcher(FakeSurface()),
            authorization_resolver=allow_all,
        )
        async with Client(host.server) as client:
            result = await client.call_tool('cbcc_provider_adapters_list', {'provider_api_key': 'never-persist-me'})
            assert result.is_error is True
            assert result.structured_content['status'] == 'INVALID_INPUT'
            assert result.structured_content['errors'][0]['code'] == 'CREDENTIAL_FIELD_FORBIDDEN'
            serialized = json.dumps(result.structured_content, ensure_ascii=False)
            assert 'never-persist-me' not in serialized

    anyio.run(scenario)


def test_pending_execute_status_round_trip_reuses_existing_operation_state(tmp_path):
    project = tmp_path / 'project'
    jobs_root = project / 'artifacts/provider_jobs'
    job_dir = jobs_root / 'A1'
    job_dir.mkdir(parents=True)
    result_path = job_dir / 'result.json'
    (jobs_root / 'PROVIDER_JOB_INDEX.json').write_text(json.dumps({
        'jobs': [{
            'asset_id': 'A1',
            'job_id': 'J1',
            'result_path': str(result_path),
        }]
    }), encoding='utf-8')
    (job_dir / 'bridge_state.json').write_text(json.dumps({'status': 'PENDING'}), encoding='utf-8')

    surface = FakeSurface()

    async def scenario():
        host = create_mcp_host(
            ProviderActionDispatcher(surface),
            authorization_resolver=allow_all,
        )
        async with Client(host.server) as client:
            execute = await client.call_tool('cbcc_provider_execute', {
                'project_dir': str(project),
                'asset_ids': ['A1'],
                'max_polls': 0,
            })
            assert execute.is_error is False
            assert execute.structured_content['status'] == 'PENDING'
            operation = execute.structured_content['operation']
            assert operation['asset_ids'] == ['A1']
            assert operation['operation_id'].startswith('OP-')
            assert execute.structured_content['result']['status_action_id'] == 'cbcc.provider.status'
            assert execute.structured_content['result']['resume_action_id'] == 'cbcc.provider.resume'

            status = await client.call_tool('cbcc_provider_status', {
                'project_dir': str(project),
                'operation_id': operation['operation_id'],
                'asset_ids': operation['asset_ids'],
            })
            assert status.is_error is False
            assert status.structured_content['status'] == 'SUCCEEDED'
            assert status.structured_content['result']['status'] == 'PENDING'
            assert status.structured_content['result']['jobs'][0]['bridge_status'] == 'PENDING'

        assert surface.execute_calls == [{
            'project_dir': str(project),
            'asset_ids': ['A1'],
            'adapter_id': None,
        }]

    anyio.run(scenario)


def test_mcp_transport_module_does_not_import_provider_runtime_layers():
    source_path = Path(__file__).resolve().parents[1] / 'runtime/cbcc/mcp_host.py'
    tree = ast.parse(source_path.read_text(encoding='utf-8'))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert not any(name.endswith('provider_surface') for name in imported)
    assert not any(name.endswith('provider_bridge') for name in imported)
    assert not any(name.endswith('provider_executor') for name in imported)
    contract = mcp_host_contract()
    assert contract['protocol_revision_baseline'] == '2026-07-28'
    assert contract['runtime_authority'] == 'ProviderActionDispatcher'
    assert contract['authorization']['default'] == 'DENY'
