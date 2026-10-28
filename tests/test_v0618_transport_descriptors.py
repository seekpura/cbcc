from pathlib import Path
from copy import deepcopy
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.action_transports import (
    PluginActionTransportAdapter,
    descriptor_parity_report,
    mcp_tool_descriptors,
    plugin_openapi_descriptor,
    transport_descriptor_bundle,
)
from cbcc.host_actions import (
    ACTION_ADAPTER_LIST,
    SCOPE_ADAPTER_READ,
    ActionAuthorization,
    action_catalog,
    action_transport_manifest,
    forbidden_secret_fields,
)


def _input_schemas_from_openapi(document):
    out = {}
    for path_item in (document.get('paths') or {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict) or not operation.get('x-cbcc-action-id'):
                continue
            schema = operation['requestBody']['content']['application/json']['schema']
            out[operation['x-cbcc-action-id']] = schema
    return out


def test_generated_mcp_and_plugin_descriptors_are_exact_canonical_schema_parity():
    report = descriptor_parity_report()
    assert report['status'] == 'PASS'
    assert report['canonical_action_count'] == 6
    assert report['mcp_tool_count'] == 6
    assert report['plugin_operation_count'] == 6
    for row in report['rows']:
        assert row['canonical_schema_hash'] == row['mcp_schema_hash'] == row['plugin_schema_hash']


def test_transport_descriptors_have_no_credential_payload_fields_and_preserve_authorization_scope():
    canonical = {x['action_id']: x for x in action_catalog()['actions']}
    mcp = {x['x-cbcc-action-id']: x for x in mcp_tool_descriptors()}
    plugin = plugin_openapi_descriptor()
    plugin_schemas = _input_schemas_from_openapi(plugin)
    for action_id, action in canonical.items():
        assert mcp[action_id]['x-cbcc-permission-scope'] == action['permission_scope']
        assert mcp[action_id]['inputSchema'] == action['input_schema']
        assert forbidden_secret_fields(mcp[action_id]['inputSchema']) == []
        assert plugin_schemas[action_id] == action['input_schema']
        assert forbidden_secret_fields(plugin_schemas[action_id]) == []
    assert plugin['x-cbcc-credential-payload-fields'] == 'FORBIDDEN'
    assert plugin['x-cbcc-transport-owns-provider-runtime'] is False
    assert 'securitySchemes' not in (plugin.get('components') or {})


def test_descriptor_parity_detects_schema_scope_and_secret_drift():
    tools = mcp_tool_descriptors()
    plugin = plugin_openapi_descriptor()
    tools[0]['inputSchema']['properties']['provider_api_key'] = {'type': 'string'}
    tools[1]['x-cbcc-permission-scope'] = 'WRONG_SCOPE'
    first_plugin = next(iter(plugin['paths'].values()))['post']
    first_plugin['requestBody']['content']['application/json']['schema']['properties']['oauth_token'] = {'type': 'string'}
    report = descriptor_parity_report(mcp_tools=tools, plugin_openapi=plugin)
    assert report['status'] == 'FAIL'
    codes = {x['code'] for x in report['issues']}
    assert 'MCP_SCHEMA_DRIFT' in codes
    assert 'MCP_CREDENTIAL_FIELD_PRESENT' in codes
    assert 'MCP_AUTH_SCOPE_DRIFT' in codes
    assert 'PLUGIN_SCHEMA_DRIFT' in codes
    assert 'PLUGIN_CREDENTIAL_FIELD_PRESENT' in codes


def test_checked_in_transport_artifacts_are_generated_from_current_canonical_catalog():
    mcp_path = ROOT / 'transport/mcp_tools.json'
    plugin_path = ROOT / 'transport/plugin_openapi.json'
    manifest_path = ROOT / 'transport/descriptor_manifest.json'
    assert mcp_path.exists() and plugin_path.exists() and manifest_path.exists()
    checked_mcp = json.loads(mcp_path.read_text(encoding='utf-8'))
    checked_plugin = json.loads(plugin_path.read_text(encoding='utf-8'))
    checked_manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert checked_mcp == mcp_tool_descriptors()
    assert checked_plugin == plugin_openapi_descriptor(server_url='/')
    assert checked_manifest['parity']['status'] == 'PASS'
    assert checked_manifest['runtime_authority'] == 'ProviderActionDispatcher'
    assert checked_manifest['mcp_server_included'] is False
    assert checked_manifest['plugin_http_server_included'] is False


def test_plugin_transport_adapter_only_delegates_to_canonical_dispatcher():
    calls = []

    class FakeDispatcher:
        def dispatch(self, action_id, body, authorization):
            calls.append((action_id, deepcopy(body), authorization))
            return {'action_id': action_id, 'status': 'SUCCEEDED', 'result': {'echo': body}}

    adapter = PluginActionTransportAdapter(FakeDispatcher())
    mapping = next(x for x in action_transport_manifest()['mappings'] if x['action_id'] == ACTION_ADAPTER_LIST)
    auth = ActionAuthorization.from_scopes([SCOPE_ADAPTER_READ], actor_id='PLUGIN-HOST')
    body = {'provider': 'EPV_ADAPTER'}
    out = adapter.invoke(mapping['plugin_operation_id'], body, auth)
    assert out['status'] == 'SUCCEEDED'
    assert calls == [(ACTION_ADAPTER_LIST, body, auth)]
    assert not hasattr(adapter, 'surface')
    assert not hasattr(adapter, 'executor')
    assert not hasattr(adapter, 'bridge')


def test_plugin_transport_adapter_rejects_unmapped_operation_without_dispatch():
    class ExplodingDispatcher:
        def dispatch(self, *args, **kwargs):
            raise AssertionError('must not dispatch unmapped operations')

    adapter = PluginActionTransportAdapter(ExplodingDispatcher())
    out = adapter.invoke('unknownOperation', {'project_dir': '/tmp/x'}, None)
    assert out['status'] == 'INVALID_OPERATION'
    assert out['errors'][0]['code'] == 'PLUGIN_OPERATION_NOT_MAPPED'


def test_transport_bundle_is_descriptor_only_not_server_runtime():
    bundle = transport_descriptor_bundle(server_url='/')
    assert bundle['parity']['status'] == 'PASS'
    assert bundle['runtime_authority'] == 'ProviderActionDispatcher'
    assert bundle['mcp_server_included'] is False
    assert bundle['plugin_http_server_included'] is False
    assert bundle['plugin_openapi']['servers'] == [{'url': '/'}]
