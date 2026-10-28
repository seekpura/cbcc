from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.claim_authority import compile_claim_authority
from cbcc.prompt_compiler import compile_asset_prompt
from cbcc.video_creator import enrich_video_plan_with_strategy


def _strategy():
    return {'sections':{'05_visual_photography_strategy':{
        'camera':{'focal_length_mm':'85mm','lens_family':'short telephoto macro','aperture_dof_intent':'f/8','focus_plane':'front label','shutter_speed':'1/125s','iso':'100'},
        'lighting_framework':{'key':'large softbox camera-left','fill':'white card','negative_fill':'black flag camera-right','cct':'5000K'},
        'cmf':{'primary':'#163C31','capture_implications':'preserve true green without cyan shift','post_implications':'no skin whitening'},
        'inclusive_photography':{'skin_tone_exposure':'+0.3 EV bracket where needed; reflector + large diffusion','hair_and_styling':'preserve real hair texture'},
        'asset_parameter_reasoning':[{'asset_id':'AST-TEST','composition_choice':'asymmetric editorial','camera_choice':{'azimuth':'15°','elevation':'5°'},'lighting_choice':{'exposure_ratio_plan':'2:1'},'material_lighting_profile':{'prelight_plan':'meter label and skin separately','lighting_diagram':'key 45° left, fill front-right','polarization_plan':'cross-polarize packaging only; preserve gel speculars','color_consistency_plan':'fixed WB + color target'},'cmf_choice':{'primary':'#163C31','background':'warm ivory'}}]
    }}}


def test_claim_authority_does_not_trust_labels_without_evidence():
    out=compile_claim_authority([
        {'claim_id':'C1','claim':'reduces acne','evidence_level':'A','status':'APPROVED'},
        {'claim_id':'C2','claim':'contains ingredient','source_ids':['S2']},
        {'claim_id':'C3','claim':'measured result','source_ids':['S3'],'status':'APPROVED'},
    ],[{'source_id':'S2','source_type':'FORMULA SPEC'},{'source_id':'S3','source_type':'LAB TEST REPORT'}])
    assert [x['evidence_grade'] for x in out['claims']]==['C','B','A']
    assert any(x['code']=='DECLARED_EVIDENCE_GRADE_NOT_SUPPORTED' for x in out['issues'])


def test_render_prompt_contains_production_parameters_not_internal_metadata():
    asset={'asset_id':'AST-TEST','surface':'GALLERY','family':'GALLERY','asset_type':'IMAGE','decision_intent':'PROOF','consumer_question':'Why trust this?','belief_target':'credible proof','race_stage':'COMMUNICATION','surface_copy_budget':{'max_message_units':2},'product_fidelity':'LOCKED_PIXEL','product_presence':{'planning_state':'REQUIRED'},'creative_direction':{'creative_thesis':'Material truth under controlled humid-beauty light','image_language':'editorial clinical still life'},'surface_native_contract':{'mobile_scan':'one proof in 1 second','safe_zone':'right 30%'}}
    c=compile_asset_prompt(asset,{'name':'KIYUU K01'},{'platform_family':'TIKTOK_SHOP','market':'MY'},{}, {},strategy_authority=_strategy(),source_product_assets=[{'asset_id':'REAL-1','pixel_lock':True}])
    p=c['prompt_en'].lower()
    for forbidden in ['ast-test','real-1','asset id','race','cvr','kiyuu k01']:
        assert forbidden not in p
    for required in ['85mm','5000k','2:1','cross-polarize','+0.3 ev','#163c31','f/8','1/125s']:
        assert required in p
    assert len(c['parameter_trace'])>=6


def test_video_prompt_inherits_strategy_parameters_without_ids():
    plan={'assets':[{'video_id':'VID-SECRET','source_asset_id':'AST-TEST','creative_thesis':'show material truth','hook':'Why?','shots':[{'shot':'HOOK','seconds':2,'job':'show use tension','visual':'hand + product'}]}]}
    out=enrich_video_plan_with_strategy(plan,_strategy(),source_product_assets=[{'asset_id':'REAL-1'}])
    p=out['assets'][0]['canonical_video_prompt_en'].lower()
    for forbidden in ['vid-secret','ast-test','real-1']:
        assert forbidden not in p
    for required in ['85mm','5000k','2:1','cross-polarize','+0.3 ev','#163c31']:
        assert required in p
