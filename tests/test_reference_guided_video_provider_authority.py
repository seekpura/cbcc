from cbcc.providers import provider_contract
from cbcc.production import _REAL_PRODUCT_MODES
from cbcc.video_creator import build_video_creator_plan, enrich_video_plan_with_strategy
from cbcc.tools.seven_agent import product_video_tool


def _strategy():
    return {'sections':{'05_visual_photography_strategy':{'camera':{},'lighting_framework':{},'cmf':{},'material_lighting_profile':{},'asset_parameter_reasoning':[],'inclusive_photography':{}}}}


def test_generic_video_does_not_imply_real_product_master_or_photography_contract():
    c=provider_contract('VIDEO_PROVIDER','VIDEO',{'product_fidelity':'REFERENCE_GUIDED'})
    assert c['status']=='READY'
    assert c['source_binding_contract']['required'] is False
    assert 'source_product_assets' not in c['required_inputs']
    assert 'photography_contract' not in c['required_inputs']
    assert 'VIDEO' not in _REAL_PRODUCT_MODES


def test_video_render_contract_is_reference_guided_by_default():
    plan=build_video_creator_plan('P',[{'family':'VIDEO','surface':'PDP_VIDEO','curation_job':'show use'}],['How is it used?'],{'primary_locale':'en-US','visible_copy_locales':['en-US']})
    out=enrich_video_plan_with_strategy(plan,_strategy(),source_product_assets=[{'asset_id':'SRC','pixel_lock':False,'fidelity_mode':'REFERENCE_GUIDED'}])
    v=out['assets'][0]
    assert v['visual_render_contract']['product_identity']['mode']=='REFERENCE_GUIDED'
    assert 'redraw' in v['visual_render_contract']['product_identity']['rule'].lower()
    assert 'sole visual identity authority' not in v['canonical_video_prompt_en']
    assert '[PRODUCT REFERENCE / FIDELITY]' in v['canonical_video_prompt_en']


def test_standalone_video_without_strategy_is_advisory_not_hold():
    out=product_video_tool(project_id='P',content_objects=[],shopper_questions=[],language_contract={'primary_locale':'en-US'},video_jobs=[])
    assert out['result']['strategy_visual_binding']=='ADVISORY_STRATEGY_AUTHORITY_NOT_SUPPLIED'
