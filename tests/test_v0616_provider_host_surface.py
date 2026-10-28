from pathlib import Path
import hashlib
import json
import sys
import types

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.asset_compiler import compile_asset_packages
from cbcc.cli import main as cli_main
from cbcc.production import build_production_run, materialize_provider_jobs
from cbcc.provider_bridge import ExecutionPolicy
from cbcc.provider_executor import ReferenceMemoryExecutor
from cbcc.provider_surface import (
    HOST_MODULE_ENV,
    ProviderExecutionSurface,
    host_execution_contract,
    provider_execution_surface_from_environment,
)
from cbcc.provider_bridge import build_default_adapter_registry
from cbcc.state import ProjectState


def _asset(asset_id='AST-V0616'):
    return {
        'asset_id': asset_id,
        'asset_name': 'Provider host execution surface proof',
        'asset_type': 'IMAGE',
        'status': 'ACTIVATE',
        'surface': 'GALLERY',
        'family': 'VISUAL',
        'consumer_question': 'What is this product?',
        'strategic_job': 'Preserve exact product identity through host execution',
        'production_mode': 'REAL_PRODUCT_COMPOSITE',
        'product_fidelity': 'LOCKED_PIXEL',
        'priority': 'P0',
        'dependencies': [],
        'source_ids': ['SRC-1'],
        'claim_ids': [],
        'listing_reference': [],
        'success_metric': 'identity clarity',
    }


def _materialize_project(tmp_path: Path, asset_id='AST-V0616'):
    project = tmp_path / 'project'
    packs = project / 'artifacts/asset_packages'
    master = tmp_path / 'master.bin'
    data = b'v0616-real-product-master'
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
            'asset_id': 'MASTER-V0616',
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
    # Match the real compiler: provider job materialization mutates run with the receipt/binding
    # contracts that existing ingest must validate, then production_run.json is persisted.
    run['provider_jobs'] = index
    run_path = project / 'artifacts/production_run.json'
    run_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding='utf-8')
    ProjectState.init(project, 'V0616-HOST-SURFACE', version='0.6.16-provider-host-execution-surface')
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


def _install_host_module(monkeypatch, name: str, callbacks: dict, secret: str):
    module = types.ModuleType(name)

    def create_runtime_context(*, adapter_id, job_dir, job):
        assert adapter_id == 'EPV_HOST_CALLBACK_V1'
        return {'callbacks': callbacks, 'api_key': secret, 'sdk_client': object()}

    module.create_runtime_context = create_runtime_context
    monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setenv(HOST_MODULE_ENV, name)
    return module


def test_host_execution_contract_forbids_secret_cli_arguments_and_persistence():
    contract = host_execution_contract()
    assert contract['runtime_context']['persistence'] == 'FORBIDDEN'
    assert contract['runtime_context']['cli_secret_arguments'] == 'FORBIDDEN'
    assert contract['runtime_context']['host_module_value_is_module_name_not_credentials'] is True
    assert contract['single_execution_chain'].endswith('Production Receipt → Ingest')
    assert set(contract['commands']) == {'adapter-list', 'provider-execute', 'provider-cancel', 'provider-reconcile'}


def test_adapter_listing_is_available_without_runtime_credentials():
    surface = provider_execution_surface_from_environment(env={})
    out = surface.list_adapters(provider='EPV_ADAPTER', production_mode='REAL_PRODUCT_COMPOSITE')
    assert out['status'] == 'ADAPTERS_DISCOVERED'
    assert out['count'] == 1
    assert out['adapters'][0]['adapter_id'] == 'EPV_HOST_CALLBACK_V1'
    serialized_adapters = json.dumps(out['adapters'])
    assert 'api_key' not in serialized_adapters
    assert 'credential_value' not in serialized_adapters


def test_programmatic_surface_executes_ingests_updates_state_and_never_persists_secret(tmp_path):
    project, jobs = _materialize_project(tmp_path)
    secret = 'DO-NOT-PERSIST-V0616-SECRET'
    reference = ReferenceMemoryExecutor(poll_sequence=('COMPLETED',))
    registry = build_default_adapter_registry()

    def resolver(adapter_id, job_dir, job):
        return {'callbacks': _callbacks(reference), 'api_key': secret}

    surface = ProviderExecutionSurface(registry, context_resolver=resolver)
    out = surface.execute_project(
        project,
        adapter_id='EPV_HOST_CALLBACK_V1',
        policy=ExecutionPolicy(max_attempts=2, max_polls_per_attempt=2),
    )
    assert out['status'] == 'PROVIDER_EXECUTION_COMPLETE'
    assert out['ingest_status'] == 'COMPLETE'
    production = json.loads((project / 'artifacts/production_run.json').read_text(encoding='utf-8'))
    assert production['status'] == 'COMPLETE'
    state = ProjectState.load(project)
    assert state.data['gates']['PRODUCTION']['status'] == 'READY_REVIEW'
    assert state.data['current_stage'] == 'PROVIDER_EXECUTION_SURFACE'

    persisted = '\n'.join(
        p.read_text(encoding='utf-8')
        for p in [
            jobs / 'AST-V0616/bridge_state.json',
            jobs / 'AST-V0616/executor_state.json',
            jobs / 'AST-V0616/result.json',
            project / 'artifacts/production_run.json',
            project / '.cbcc/project_state.json',
        ]
    )
    assert secret not in persisted


def test_environment_host_module_contains_only_module_name_and_executes_real_callbacks(tmp_path, monkeypatch):
    project, _ = _materialize_project(tmp_path)
    secret = 'HOST-ONLY-V0616-KEY'
    reference = ReferenceMemoryExecutor(poll_sequence=('COMPLETED',))
    module_name = 'cbcc_v0616_test_host'
    _install_host_module(monkeypatch, module_name, _callbacks(reference), secret)
    assert sys.modules[module_name] is not None
    assert secret not in module_name

    surface = provider_execution_surface_from_environment()
    out = surface.execute_project(project, adapter_id='EPV_HOST_CALLBACK_V1')
    assert out['status'] == 'PROVIDER_EXECUTION_COMPLETE'
    assert out['ingest_status'] == 'COMPLETE'
    assert secret not in (project / 'artifacts/provider_jobs/AST-V0616/bridge_state.json').read_text(encoding='utf-8')


def test_cli_adapter_list_and_provider_execute_reuse_host_surface(tmp_path, monkeypatch, capsys):
    project, _ = _materialize_project(tmp_path)
    secret = 'CLI-HOST-ONLY-KEY'
    reference = ReferenceMemoryExecutor(poll_sequence=('COMPLETED',))
    module_name = 'cbcc_v0616_cli_host'
    _install_host_module(monkeypatch, module_name, _callbacks(reference), secret)

    assert cli_main(['adapter-list', '--provider', 'EPV_ADAPTER', '--production-mode', 'REAL_PRODUCT_COMPOSITE']) == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed['adapters'][0]['adapter_id'] == 'EPV_HOST_CALLBACK_V1'

    assert cli_main([
        'provider-execute', '--project-dir', str(project),
        '--adapter-id', 'EPV_HOST_CALLBACK_V1', '--max-attempts', '2', '--max-polls', '2',
    ]) == 0
    executed = json.loads(capsys.readouterr().out)
    assert executed['status'] == 'PROVIDER_EXECUTION_COMPLETE'
    assert executed['ingest_status'] == 'COMPLETE'
    assert secret not in json.dumps(executed)
    assert ProjectState.load(project).data['gates']['PRODUCTION']['status'] == 'READY_REVIEW'


def test_cli_rejects_secret_argument_surface(tmp_path):
    with pytest.raises(SystemExit):
        cli_main(['provider-execute', '--project-dir', str(tmp_path), '--api-key', 'must-not-be-accepted'])


def test_cli_cancel_and_reconcile_share_existing_external_job_lineage(tmp_path, monkeypatch, capsys):
    project, jobs = _materialize_project(tmp_path)
    reference = ReferenceMemoryExecutor(poll_sequence=('RUNNING', 'RUNNING', 'RUNNING'))
    cancelled = []

    def cancel(external_job_id, *, job):
        cancelled.append(external_job_id)
        return {'status': 'CANCELLED'}

    def reconcile(external_job_id, *, job, local_state):
        return {'status': local_state.get('provider_status') or 'RUNNING', 'external_job_id': external_job_id}

    module_name = 'cbcc_v0616_control_host'
    _install_host_module(monkeypatch, module_name, _callbacks(reference, cancel=cancel, reconcile=reconcile), 'CONTROL-SECRET')

    assert cli_main([
        'provider-execute', '--project-dir', str(project), '--adapter-id', 'EPV_HOST_CALLBACK_V1', '--max-polls', '1',
    ]) == 0
    pending = json.loads(capsys.readouterr().out)
    assert pending['jobs'][0]['status'] == 'PENDING'

    assert cli_main([
        'provider-reconcile', '--project-dir', str(project), '--asset-id', 'AST-V0616', '--adapter-id', 'EPV_HOST_CALLBACK_V1',
    ]) == 0
    reconciled = json.loads(capsys.readouterr().out)
    assert reconciled['status'] == 'RECONCILED'

    assert cli_main([
        'provider-cancel', '--project-dir', str(project), '--asset-id', 'AST-V0616', '--adapter-id', 'EPV_HOST_CALLBACK_V1', '--reason', 'operator stop',
    ]) == 0
    stopped = json.loads(capsys.readouterr().out)
    assert stopped['status'] == 'CANCELLED'
    assert len(cancelled) == 1
    executor_state = json.loads((jobs / 'AST-V0616/executor_state.json').read_text(encoding='utf-8'))
    assert executor_state['adapter_result']['external_job_id'] == cancelled[0]
