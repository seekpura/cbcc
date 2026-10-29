from pathlib import Path
import json

from cbcc.compiler import _normalize_source_product_assets
from cbcc.prompt_compiler import _derived_photo_contract
from cbcc.production import _production_quality_contract, materialize_provider_jobs


def test_nonphotographic_human_asset_keeps_representation_without_camera_defaults():
    asset={'asset_id':'A','production_mode':'THREE_D','creative_brief':{'human':'stylized person'}}
    p=_derived_photo_contract(asset, {'sections':{'05_visual_photography_strategy':{'camera':{'focal_length_mm':'85mm'},'lighting_framework':{'cct':'5200K'}}}}, None)
    assert p.get('camera') in ({},None)
    inc=p.get('inclusive_photography') or {}
    assert 'ai_bias_controls' in inc
    assert 'skin_tone_exposure' not in inc
    assert p.get('prelight_required') is False


def test_provider_job_allows_reference_substitution_when_real_master_not_required(tmp_path):
    root=tmp_path/'assets'; d=root/'A'; d.mkdir(parents=True)
    (root/'ASSET_PACKAGE_INDEX.json').write_text(json.dumps({'assets':[{'asset_id':'A'}]}),encoding='utf-8')
    # minimal package files used for hashing/contract reads
    (d/'00_asset_manifest.yaml').write_text('asset_id: A\nstatus: ACTIVATE\nproduction_mode: GRAPHIC_DESIGN\nproduct_fidelity: REFERENCE_GUIDED\nsource_product_assets: []\n',encoding='utf-8')
    for fn in ['03_photography_contract.json','04_layout_contract.json','13_prompt_contract.json']:
        (d/fn).write_text('{}',encoding='utf-8')
    qc=_production_quality_contract(d, {'asset_id':'A','production_mode':'GRAPHIC_DESIGN','product_fidelity':'REFERENCE_GUIDED','source_product_assets':[]})
    assert qc['real_product_master_required'] is False
    run={'assets':[{'asset_id':'A','status':'READY_TO_HANDOFF','package_hash':'x','provider':'HUMAN_OR_DESIGN_PROVIDER','provider_contract':{'adapter':'FILE_HANDOFF'},'production_mode':'GRAPHIC_DESIGN','production_quality_contract':qc,'production_contract_binding':{}}]}
    out=materialize_provider_jobs(root,run,tmp_path/'jobs')
    assert out['job_count']==1
    job=json.loads((tmp_path/'jobs/A/job.json').read_text(encoding='utf-8'))
    assert job['execution_policy']['real_product_master_substitution_allowed'] is True


def test_host_wrapper_does_not_reintroduce_prompt_zero_missing_gate():
    source=Path('scripts/build_plugin_dist.py').read_text(encoding='utf-8')
    assert 'Prompt Consumption Audit 的 `missing decisions = 0`' not in source
    assert 'missing decisions` 形成 `NEEDS_PROMPT_WORK`' in source
