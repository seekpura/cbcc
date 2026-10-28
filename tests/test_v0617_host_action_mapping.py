from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.asset_compiler import compile_asset_packages
from cbcc.host_actions import (
    ACTION_ADAPTER_LIST,
    ACTION_CANCEL,
    ACTION_EXECUTE,
    ACTION_RECONCILE,
    ACTION_RESUME,
    ACTION_STATUS,
    SCOPE_ADAPTER_READ,
    SCOPE_CANCEL,
    SCOPE_EXECUTE,
    SCOPE_RECONCILE,
    SCOPE_STATUS_READ,
    ActionAuthorization,
    ProviderActionDispatcher,
    action_catalog,
    action_transport_manifest,
    forbidden_secret_fields,
)
from cbcc.production import build_production_run, materialize_provider_jobs
from cbcc.provider_bridge import build_default_adapter_registry
from cbcc.provider_executor import ReferenceMemoryExecutor
from cbcc.provider_surface import ProviderExecutionSurface
from cbcc.state import ProjectState


def _asset(asset_id='AST-V0617'):
    return {
        'asset_id': asset_id,
        'asset_name': 'Host action mapping proof',
        'asset_type': 'IMAGE',
        'status': 'ACTIVATE',
        'surface': 'GALLERY',
        'family': 'VISUAL',
        'consumer_question': 'What is this product?',
        'strategic_job': 'Preserve exact product identity through action mapping',
        'production_mode': 'REAL_PRODUCT_COMPOSITE',
        'product_fidelity': 'LOCKED_PIXEL',
        'priority': 'P0',
        'dependencies': [],
        'source_ids': ['SRC-1'],
        'claim_ids': [],
        'listing_reference': [],
        'success_metric': 'identity clarity',
    }


def _materialize_project(tmp_path: Path, asset_id='AST-V0617'):
    project = tmp_path / 'project'
    packs = project / 'artifacts/asset_packages'
    master = tmp_path / 'master.bin'
    data = b'v0617-real-product-master'
    master.write_bytes(data)
    sha = hashlib.sha256(data).hexdigest()
    compile_asset_packages(
        packs,
        [_asset(asset_id)],
        {'name': 'P'},
        {'platform_family': 'x', 'site': 'MY', 'market': 'Malaysia'},
        {'visual_implications': []},
        {'visible_copy_locales': ['en-MY']},
        {'profiles': []},
        source_product_assets=[{
            'asset_id': 'MASTER-V0617',
            'role': 'FRONT_MASTER',
            'path': str(master),
            'sha256': sha,
            'ingest_status': 'HASH_VERIFIED_LOCAL',
            'pixel_lock': True,
            'allowed_transforms': ['PROPORTIONAL_SCALE', 'PLACEMENT', 'MASK_OR_CROP', 'COMPOSITE'],
            'identity_features': ['logo', 'packaging_print', 'color', 'geometry', 'proportions'],
        }],
    )
    run = build_production_run(packs, provider_preferences={'REAL_PRODUCT_COMPOSITE': 'EPV_ADAPTER'})
    jobs = project / 'artifacts/provider_jobs'
    index = materialize_provider_jobs(packs, run, jobs)
    assert index['job_count'] == 1
    run['provider_jobs'] = index
    run_path = project / 'artifacts/production_run.json'
    run_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding='utf-8')
    ProjectState.init(project, 'V0617-ACTION-PROJECT', version='0.6.17-host-action-mapping')
    return project, jobs


def _callbacks(reference: ReferenceMemoryExecutor, *, cancel=None, reconcile=None):
    rows = {
        'ensure_asset': reference.ensure_asset,
        'submit': reference.submit,
        'poll': reference.poll,
        'collect': reference.collect,
        'resolve': reference.resolve,
    }
    if cancel is not None:
        rows['cancel'] = cancel
    if reconcile is not None:
        rows['reconcile'] = reconcile
    return rows


def _dispatcher(reference: ReferenceMemoryExecutor, *, cancel=None, reconcile=None):
    registry = build_default_adapter_registry()
    callbacks = _callbacks(reference, cancel=cancel, reconcile=reconcile)

    def resolver(adapter_id, job_dir, job):
        return {'callbacks': callbacks, 'api_key': 'RUNTIME-ONLY-SECRET-V0617'}

    surface = ProviderExecutionSurface(registry, context_resolver=resolver)
    return ProviderActionDispatcher(surface)


def _auth(*scopes):
    return ActionAuthorization.from_scopes(scopes, actor_id='TEST-HOST')


def test_action_catalog_has_canonical_schemas_without_credential_input_fields():
    catalog = action_catalog()
    assert catalog['canonical_authority'] == 'ProviderExecutionSurface'
    assert catalog['authorization']['default'] == 'DENY'
    assert catalog['long_running']['separate_async_job_database'] is False
    assert len(catalog['actions']) == 6
    for action in catalog['actions']:
        properties = (action['input_schema'].get('properties') or {})
        assert forbidden_secret_fields(properties) == []
    assert 'api_key' in catalog['secret_boundary']['credential_fields_forbidden']
    assert 'token' in catalog['secret_boundary']['credential_fields_forbidden']


def test_transport_manifest_is_thin_mapping_and_does_not_claim_servers_exist():
    manifest = action_transport_manifest()
    assert manifest['status'] == 'DECLARATIVE_THIN_MAPPING'
    assert manifest['runtime_implementation'].endswith('ProviderExecutionSurface')
    assert manifest['claims_mcp_server_exists'] is False
    assert manifest['claims_plugin_server_exists'] is False
    assert len(manifest['mappings']) == 6
    assert all(row['mcp_tool_name'].startswith('cbcc_provider_') for row in manifest['mappings'])
    assert all(row['plugin_operation_id'].startswith('cbccProvider') for row in manifest['mappings'])


def test_secret_bearing_action_payload_is_rejected_before_dispatch(tmp_path):
    reference = ReferenceMemoryExecutor()
    dispatcher = _dispatcher(reference)
    out = dispatcher.dispatch(
        ACTION_EXECUTE,
        {'project_dir': str(tmp_path), 'api_key': 'SHOULD-NEVER-ENTER-ACTION'},
        _auth(SCOPE_EXECUTE),
    )
    assert out['status'] == 'INVALID_INPUT'
    assert out['errors'][0]['code'] == 'CREDENTIAL_FIELD_FORBIDDEN'
    assert out['errors'][0]['fields'] == ['api_key']
    assert reference.submit_calls == 0


def test_mutating_action_is_default_deny_without_explicit_scope(tmp_path):
    project, _ = _materialize_project(tmp_path)
    reference = ReferenceMemoryExecutor(poll_sequence=('COMPLETED',))
    dispatcher = _dispatcher(reference)
    denied = dispatcher.dispatch(ACTION_EXECUTE, {'project_dir': str(project)}, ActionAuthorization())
    assert denied['status'] == 'DENIED'
    assert denied['errors'][0]['required_scope'] == SCOPE_EXECUTE
    assert reference.submit_calls == 0


def test_adapter_list_requires_read_scope_and_maps_to_existing_surface(tmp_path):
    reference = ReferenceMemoryExecutor()
    dispatcher = _dispatcher(reference)
    denied = dispatcher.dispatch(ACTION_ADAPTER_LIST, {'provider': 'EPV_ADAPTER'}, ActionAuthorization())
    assert denied['status'] == 'DENIED'
    allowed = dispatcher.dispatch(
        ACTION_ADAPTER_LIST,
        {'provider': 'EPV_ADAPTER', 'production_mode': 'REAL_PRODUCT_COMPOSITE'},
        _auth(SCOPE_ADAPTER_READ),
    )
    assert allowed['status'] == 'SUCCEEDED'
    assert allowed['result']['adapters'][0]['adapter_id'] == 'EPV_HOST_CALLBACK_V1'


def test_execute_pending_status_read_only_and_resume_same_external_job_without_duplicate_submit(tmp_path):
    project, jobs = _materialize_project(tmp_path)
    reference = ReferenceMemoryExecutor(poll_sequence=('RUNNING', 'COMPLETED'))
    dispatcher = _dispatcher(reference)

    execute = dispatcher.dispatch(
        ACTION_EXECUTE,
        {
            'project_dir': str(project),
            'asset_ids': ['AST-V0617'],
            'adapter_id': 'EPV_HOST_CALLBACK_V1',
            'max_attempts': 2,
            'max_polls': 1,
        },
        _auth(SCOPE_EXECUTE),
    )
    assert execute['status'] == 'PENDING'
    operation = execute['operation']
    assert operation['operation_id'].startswith('OP-')
    assert operation['asset_ids'] == ['AST-V0617']
    assert execute['result']['resume_action_id'] == ACTION_RESUME
    assert execute['result']['status_action_id'] == ACTION_STATUS
    assert reference.submit_calls == 1

    bridge_state_path = jobs / 'AST-V0617/bridge_state.json'
    before = bridge_state_path.read_text(encoding='utf-8')
    status = dispatcher.dispatch(
        ACTION_STATUS,
        {
            'project_dir': str(project),
            'operation_id': operation['operation_id'],
            'asset_ids': operation['asset_ids'],
        },
        _auth(SCOPE_STATUS_READ),
    )
    after = bridge_state_path.read_text(encoding='utf-8')
    assert status['status'] == 'SUCCEEDED'
    assert status['result']['status'] == 'PENDING'
    assert status['result']['read_only'] is True
    assert before == after

    resumed = dispatcher.dispatch(
        ACTION_RESUME,
        {
            'project_dir': str(project),
            'operation_id': operation['operation_id'],
            'asset_ids': operation['asset_ids'],
            'adapter_id': 'EPV_HOST_CALLBACK_V1',
            'max_attempts': 2,
            'max_polls': 2,
        },
        _auth(SCOPE_EXECUTE),
    )
    assert resumed['status'] == 'SUCCEEDED'
    assert resumed['operation']['operation_id'] == operation['operation_id']
    assert reference.submit_calls == 1, 'resume must reuse the accepted external provider job'
    assert resumed['result']['operation_status']['status'] == 'COMPLETE'
    assert resumed['result']['execution']['ingest_status'] == 'COMPLETE'
    assert ProjectState.load(project).data['gates']['PRODUCTION']['status'] == 'READY_REVIEW'
    persisted = '\n'.join(
        p.read_text(encoding='utf-8')
        for p in [
            jobs / 'AST-V0617/bridge_state.json',
            jobs / 'AST-V0617/executor_state.json',
            jobs / 'AST-V0617/result.json',
            project / 'artifacts/production_run.json',
        ]
    )
    assert 'RUNTIME-ONLY-SECRET-V0617' not in persisted


def test_status_and_resume_reject_operation_scope_tampering(tmp_path):
    project, _ = _materialize_project(tmp_path)
    reference = ReferenceMemoryExecutor(poll_sequence=('RUNNING',))
    dispatcher = _dispatcher(reference)
    execute = dispatcher.dispatch(
        ACTION_EXECUTE,
        {'project_dir': str(project), 'asset_ids': ['AST-V0617'], 'max_polls': 1},
        _auth(SCOPE_EXECUTE),
    )
    operation = execute['operation']
    status = dispatcher.dispatch(
        ACTION_STATUS,
        {'project_dir': str(project), 'operation_id': operation['operation_id'], 'asset_ids': ['OTHER-ASSET']},
        _auth(SCOPE_STATUS_READ),
    )
    assert status['status'] == 'INVALID_INPUT'
    resume = dispatcher.dispatch(
        ACTION_RESUME,
        {'project_dir': str(project), 'operation_id': operation['operation_id'], 'asset_ids': ['OTHER-ASSET']},
        _auth(SCOPE_EXECUTE),
    )
    assert resume['status'] == 'INVALID_INPUT'


def test_cancel_and_reconcile_action_scopes_map_to_same_external_job_lineage(tmp_path):
    project, jobs = _materialize_project(tmp_path)
    reference = ReferenceMemoryExecutor(poll_sequence=('RUNNING', 'RUNNING', 'RUNNING'))
    cancelled = []

    def cancel(external_job_id, *, job):
        cancelled.append(external_job_id)
        return {'status': 'CANCELLED'}

    def reconcile(external_job_id, *, job, local_state):
        return {'status': local_state.get('provider_status') or 'RUNNING', 'external_job_id': external_job_id}

    dispatcher = _dispatcher(reference, cancel=cancel, reconcile=reconcile)
    execute = dispatcher.dispatch(
        ACTION_EXECUTE,
        {'project_dir': str(project), 'asset_ids': ['AST-V0617'], 'max_polls': 1},
        _auth(SCOPE_EXECUTE),
    )
    assert execute['status'] == 'PENDING'

    denied_reconcile = dispatcher.dispatch(
        ACTION_RECONCILE,
        {'project_dir': str(project), 'asset_id': 'AST-V0617'},
        _auth(SCOPE_STATUS_READ),
    )
    assert denied_reconcile['status'] == 'DENIED'

    reconciled = dispatcher.dispatch(
        ACTION_RECONCILE,
        {'project_dir': str(project), 'asset_id': 'AST-V0617'},
        _auth(SCOPE_RECONCILE),
    )
    assert reconciled['status'] == 'SUCCEEDED'
    assert reconciled['result']['status'] == 'RECONCILED'

    denied_cancel = dispatcher.dispatch(
        ACTION_CANCEL,
        {'project_dir': str(project), 'asset_id': 'AST-V0617'},
        _auth(SCOPE_EXECUTE),
    )
    assert denied_cancel['status'] == 'DENIED'

    cancelled_action = dispatcher.dispatch(
        ACTION_CANCEL,
        {'project_dir': str(project), 'asset_id': 'AST-V0617', 'reason': 'operator stop'},
        _auth(SCOPE_CANCEL),
    )
    assert cancelled_action['status'] == 'SUCCEEDED'
    assert cancelled_action['result']['cancel']['status'] == 'CANCELLED'
    assert len(cancelled) == 1
    executor_state = json.loads((jobs / 'AST-V0617/executor_state.json').read_text(encoding='utf-8'))
    assert executor_state['adapter_result']['external_job_id'] == cancelled[0]


def test_action_outputs_do_not_echo_authorization_scopes_or_runtime_context(tmp_path):
    project, _ = _materialize_project(tmp_path)
    reference = ReferenceMemoryExecutor(poll_sequence=('COMPLETED',))
    dispatcher = _dispatcher(reference)
    out = dispatcher.dispatch(
        ACTION_EXECUTE,
        {'project_dir': str(project), 'max_polls': 2},
        _auth(SCOPE_EXECUTE, SCOPE_CANCEL, SCOPE_RECONCILE),
    )
    serialized = json.dumps(out)
    assert 'RUNTIME-ONLY-SECRET-V0617' not in serialized
    assert 'api_key' not in serialized
    assert out['authorization'] == {'actor_id': 'TEST-HOST', 'decision': 'ALLOW'}
    assert 'scopes' not in out['authorization']
