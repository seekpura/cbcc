from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.compiler import build_project


HISTORICAL_V0511_CAPABILITIES = {
    'PRODUCT_TRUTH',
    'MARKET_COMPETITOR_CUSTOMER',
    'SOURCE_ADAPTER_RESEARCH_QUALITY',
    'PRODUCT_SKU_OFFER_ECONOMICS',
    'POSITIONING_MESSAGE',
    'LISTING_SEARCH',
    'FINAL_COPY_WORKFLOW',
    'HOST_COPY_AUTHORING',
    'ADS',
    'FEEDBACK',
    'EXPERIMENT_CAUSAL',
    'CULTURE_INTERSECTIONALITY',
    'VISUAL_PHOTOGRAPHY_CMF',
    'DYNAMIC_ASSET_CURATION',
    'KNOWLEDGE_ONTOLOGY_PROMPTS',
    'COMPLIANCE',
    'ASSET_COMPILER',
    'PROVIDER_PRODUCTION',
    'REVIEW_LOCAL_REVISION_PACKAGE_HASH',
    'MEASUREMENT_REVISION_INTEGRATION',
}


def _pack(tmp_path: Path) -> Path:
    d = tmp_path / 'packs'
    d.mkdir(exist_ok=True)
    (d / 'test.yaml').write_text(
        '''pack_id: r0602-generic\nplatform_family: tiktok_shop\nsite: "*"\nstatus: TEST_FIXTURE_VERIFIED\nsynthetic_for_test: true\ncapabilities: [LISTING, SEARCH, OFFER_PROMOTION, VISUAL, VIDEO, CREATOR_AFFILIATE, CX, MEASUREMENT]\nsurfaces: [PDP, GALLERY, PDP_VIDEO, CREATOR, FAQ]\nrule_atoms: []\nresearch_required_for: []\n''',
        encoding='utf-8',
    )
    return d


def _generic_request() -> dict:
    req = json.loads((ROOT / 'tests/fixtures/v059_category_commerce/apparel_tshirt.json').read_text(encoding='utf-8'))
    req['project_id'] = 'R0602-CAPABILITY-CONSERVATION-GENERIC'
    req['planning_only'] = True
    return req


def _capability_rows(project: Path) -> dict[str, dict]:
    doc = json.loads((project / 'artifacts/capability_integration_map.json').read_text(encoding='utf-8'))
    return {row['capability']: row for row in doc['capabilities']}


def test_v0511_capability_baseline_is_not_silently_dropped(tmp_path):
    project = tmp_path / 'baseline'
    build_project(project, _generic_request(), _pack(tmp_path))
    rows = _capability_rows(project)
    assert HISTORICAL_V0511_CAPABILITIES.issubset(rows), sorted(HISTORICAL_V0511_CAPABILITIES - rows.keys())


def test_historical_capabilities_keep_named_runtime_consumers_not_registry_only(tmp_path):
    project = tmp_path / 'consumer-evidence'
    build_project(project, _generic_request(), _pack(tmp_path))
    rows = _capability_rows(project)

    for capability in HISTORICAL_V0511_CAPABILITIES:
        row = rows[capability]
        assert row['consumers'], capability
        assert row['runtime_wiring_status'] != 'INTEGRATION_GAP', capability
        assert row['integrated'] is True, capability


def test_no_culture_input_cannot_be_reported_as_integrated_active(tmp_path):
    req = _generic_request()
    # The container is present, but it deliberately contains no cultural,
    # intersectional, representation, locale or identity decision input.
    req['audience_culture'] = {'audience': 'general'}
    project = tmp_path / 'no-culture-input'
    build_project(project, req, _pack(tmp_path))
    row = _capability_rows(project)['CULTURE_INTERSECTIONALITY']

    assert row['input_status'] == 'NO_CULTURE_INPUT'
    assert row['project_input_active'] is False
    assert row['runtime_wiring_status'] == 'INTEGRATED_INACTIVE_NO_PROJECT_INPUT'
    assert row['integrated'] is True


def test_positioning_consumer_claims_follow_actual_build_direction(tmp_path):
    project = tmp_path / 'positioning-consumers'
    build_project(project, _generic_request(), _pack(tmp_path))
    consumers = _capability_rows(project)['POSITIONING_MESSAGE']['consumers']

    # Final Strategy Positioning is built after Listing + Asset Architecture.  Those
    # upstream objects therefore cannot be cited as downstream proof.  The real
    # downstream consumer is the per-asset package strategy/authority trace.
    assert 'Listing Strategy' not in consumers
    assert 'Asset Portfolio' not in consumers
    assert any('strategy' in x.lower() and 'asset' in x.lower() for x in consumers)


def test_provider_layer_manifest_is_explicit_exact_pixel_only():
    text = (ROOT / 'runtime/cbcc/provider_executor.py').read_text(encoding='utf-8')
    layer_fn = text.split('def _layer_manifest', 1)[1].split('def _capture_metadata', 1)[0]
    assert "if fidelity not in {'EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'}" in layer_fn
    assert "fidelity != 'LOCKED_PIXEL'" not in layer_fn
