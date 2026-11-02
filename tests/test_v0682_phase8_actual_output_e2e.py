from __future__ import annotations

from pathlib import Path
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.asset_compiler import compile_asset_packages
from cbcc.full_package_semantic_closure_v0681 import audit_actual_output_boundary
from cbcc.learning_loop import (
    compile_local_revision_jobs,
    ingest_local_revision_results,
    sync_local_revision_review_state,
)
from cbcc.production import build_production_run, materialize_provider_jobs
from cbcc.provider_bridge import ExecutionPolicy, build_default_adapter_registry
from cbcc.provider_executor import ReferenceMemoryExecutor
from cbcc.provider_surface import ProviderExecutionSurface
from cbcc.review import materialize_review_workspace
from cbcc.state import ProjectState


ASSET_ID = 'AST-PHASE8-E2E'


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def _asset() -> dict:
    return {
        'asset_id': ASSET_ID,
        'asset_name': 'Phase 8 actual-output E2E',
        'asset_type': 'IMAGE',
        'status': 'ACTIVATE',
        'surface': 'GALLERY',
        'family': 'VISUAL',
        'consumer_question': 'What is this product?',
        'strategic_job': 'Preserve product identity while proving actual-output lifecycle',
        'production_mode': 'REAL_PRODUCT_COMPOSITE',
        'product_fidelity': 'LOCKED_PIXEL',
        'priority': 'P0',
        'dependencies': [],
        'source_ids': ['SRC-PHASE8'],
        'claim_ids': [],
        'listing_reference': [],
        'success_metric': 'actual output lineage',
    }


def _callbacks(executor: ReferenceMemoryExecutor) -> dict:
    return {
        'ensure_asset': executor.ensure_asset,
        'submit': executor.submit,
        'poll': executor.poll,
        'collect': executor.collect,
        'resolve': executor.resolve,
    }


def _build_project(tmp_path: Path) -> tuple[Path, ProviderExecutionSurface, ReferenceMemoryExecutor]:
    project = tmp_path / 'project'
    state = ProjectState.init(project, 'PHASE8-E2E')
    packages = project / 'artifacts/asset_packages'
    master = tmp_path / 'product-master.bin'
    master_bytes = b'phase8-real-product-master-bytes'
    master.write_bytes(master_bytes)

    compile_asset_packages(
        packages,
        [_asset()],
        {'name': 'Phase8 Product'},
        {'platform_family': 'tiktok', 'site': 'MY', 'market': 'Malaysia'},
        {'visual_implications': []},
        {'visible_copy_locales': ['en-MY']},
        {'profiles': []},
        source_product_assets=[{
            'asset_id': 'MASTER-PHASE8-E2E',
            'role': 'FRONT_MASTER',
            'path': str(master),
            'sha256': _sha(master_bytes),
            'ingest_status': 'HASH_VERIFIED_LOCAL',
            'pixel_lock': True,
            'allowed_transforms': ['PROPORTIONAL_SCALE', 'PLACEMENT', 'MASK_OR_CROP', 'COMPOSITE'],
            'identity_features': ['logo', 'packaging_print', 'color', 'geometry', 'proportions'],
        }],
    )

    provider_preferences = {'REAL_PRODUCT_COMPOSITE': 'EPV_ADAPTER'}
    run = build_production_run(packages, provider_preferences, [ASSET_ID])
    jobs = materialize_provider_jobs(packages, run, project / 'artifacts/provider_jobs')
    run['provider_jobs'] = jobs
    _write_json(project / 'artifacts/production_run.json', run)

    executor = ReferenceMemoryExecutor(
        poll_sequence=('COMPLETED',),
        default_output=b'phase8-provider-actual-output-v1',
    )
    registry = build_default_adapter_registry()

    def resolver(adapter_id, job_dir, job):
        assert adapter_id == 'EPV_HOST_CALLBACK_V1'
        return {'callbacks': _callbacks(executor), 'api_key': 'phase8-ci-runtime-only'}

    surface = ProviderExecutionSurface(registry, context_resolver=resolver)
    state.save()
    return project, surface, executor


def _copy_actual_output_boundary(project: Path, package: Path) -> None:
    package.mkdir(parents=True, exist_ok=True)
    shutil.copytree(project / 'artifacts/provider_jobs', package / 'provider_jobs')
    shutil.copytree(project / 'artifacts/local_revisions', package / 'local_revisions')
    shutil.copytree(project / '.cbcc/review', package / 'review_workspace')
    (package / 'supporting_analysis').mkdir(parents=True, exist_ok=True)
    shutil.copy2(project / 'artifacts/production_run.json', package / 'supporting_analysis/production_run.json')


def test_provider_result_review_local_revision_review_hash_lineage_reaches_e2e_proven(tmp_path: Path):
    project, surface, executor = _build_project(tmp_path)
    policy = ExecutionPolicy(max_attempts=2, max_polls_per_attempt=2)

    # 1) Main provider execution must create actual output bytes through the real adapter/executor bridge.
    executed = surface.execute_project(
        project,
        adapter_id='EPV_HOST_CALLBACK_V1',
        policy=policy,
    )
    assert executed['status'] == 'PROVIDER_EXECUTION_COMPLETE'
    # Provider result ingest is intentionally fail-honest: actual output exists, but it remains
    # REVIEW_REQUIRED until a human explicitly accepts the addressable output review item.
    assert executed['ingest_status'] == 'REVIEW_REQUIRED'

    result_path = project / 'artifacts/provider_jobs' / ASSET_ID / 'result.json'
    result = json.loads(result_path.read_text(encoding='utf-8'))
    receipt = result['production_receipt']
    artifact = receipt['output_artifacts'][0]
    output_path = result_path.parent / artifact['path_or_uri']
    assert output_path.read_bytes() == b'phase8-provider-actual-output-v1'
    assert _sha(output_path.read_bytes()) == artifact['sha256']

    # 2) Human review accepts the provider output and requests a bounded editable-layer revision.
    state = ProjectState.load(project)
    state.apply_review_decision({
        'project_id': 'PHASE8-E2E',
        'revision': state.data['revision'],
        'accept_items': [f'OUTPUT-{ASSET_ID}'],
        'revise_items': [{
            'item_id': f'ASSET-{ASSET_ID}',
            'requested_change': 'Tighten the headline only; preserve the product pixels.',
            'allowed_fields': ['headline'],
        }],
    })
    materialize_review_workspace(project, state.data)
    state.save()
    assert state.data['item_reviews'][f'OUTPUT-{ASSET_ID}']['status'] == 'ACCEPTED'

    # 3) Compile and execute the local revision through the same host provider surface.
    compiled = compile_local_revision_jobs(
        project,
        state.data,
        {'REAL_PRODUCT_COMPOSITE': 'EPV_ADAPTER'},
    )
    state.save()
    assert compiled['status'] == 'LOCAL_REVISION_JOBS_COMPILED'
    assert compiled['count'] == 1
    revision_id = compiled['compiled'][0]['revision_id']

    executor.default_output = b'phase8-provider-revised-output-v2'
    revision_execution = surface.execute_local_revision(
        project,
        revision_id,
        adapter_id='EPV_HOST_CALLBACK_V1',
        policy=policy,
    )
    assert revision_execution['status'] == 'LOCAL_REVISION_PROVIDER_EXECUTION_COMPLETE'

    ingested = ingest_local_revision_results(project, state.data, [revision_id])
    state.save()
    assert ingested['status'] == 'LOCAL_REVISION_RESULTS_INGESTED'
    # A revised provider result is also gated for explicit review; ingest does not self-accept it.
    assert ingested['revisions'][0]['provider_result_status'] == 'REVIEW_REQUIRED'
    revised_path = Path(ingested['revisions'][0]['output_path'])
    assert revised_path.read_bytes() == b'phase8-provider-revised-output-v2'
    assert ingested['revisions'][0]['output_hash'] == _sha(revised_path.read_bytes())

    # 4) The revised actual output becomes an addressable review item and must be explicitly accepted.
    materialize_review_workspace(project, state.data)
    state.save()
    state.apply_review_decision({
        'project_id': 'PHASE8-E2E',
        'revision': state.data['revision'],
        'accept_items': [f'REVISION-OUTPUT-{revision_id}'],
    })
    synced = sync_local_revision_review_state(project, state.data)
    assert revision_id in synced['revision_ids']
    state.save()
    materialize_review_workspace(project, state.data)
    state.save()

    revision_index = json.loads((project / 'artifacts/local_revisions/LOCAL_REVISION_INDEX.json').read_text(encoding='utf-8'))
    revision_row = next(row for row in revision_index['revisions'] if row['revision_id'] == revision_id)
    assert revision_row['status'] == 'ACCEPTED'
    assert revision_row['review_status'] == 'ACCEPTED'
    assert revision_row['revised_output_hash'] == _sha(revised_path.read_bytes())
    assert revision_row['parent_package_hash']

    # 5) Audit the exact package-side boundary that Phase 7 deliberately left E2E_PENDING.
    package = tmp_path / 'actual-output-boundary-package'
    _copy_actual_output_boundary(project, package)
    audit = audit_actual_output_boundary(package)

    assert audit['status'] == 'E2E_PROVEN'
    assert audit['provider_job_count'] == 1
    row = audit['assets'][0]
    assert row['provider_result'] == 'PASS'
    assert row['review'] == 'PASS'
    assert row['local_revision'] == 'PASS'
    assert row['lineage_hash'] == 'PASS'
    assert row['provider_output_sha256'] == [artifact['sha256']]
    assert row['revised_output_sha256'] == [_sha(revised_path.read_bytes())]
    assert row['production_receipt_hash']
