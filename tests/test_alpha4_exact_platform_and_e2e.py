from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.platform import PlatformCompiler
from cbcc.compiler import build_project


def test_tiktok_shop_my_exact_current_pack():
    out=PlatformCompiler(ROOT/'platform_packs').compile({'platform_family':'tiktok_shop','site':'MY','program':'cross_border','category':'beauty','surfaces':['PDP','GALLERY','PDP_VIDEO'],'primary_locale':'en-MY'},['TTS-MY-IMAGE-MIN-600','TTS-MY-PRIMARY-IMAGE','TTS-MY-PDP-VIDEO'])
    assert out['resolution']=='EXACT' and out['status']=='VERIFIED_FOR_REQUEST'
    assert out['submission_readiness']=='ASSESSED' and out['synthetic_for_test'] is False
    ids={r['rule_id'] for r in out['rules']}
    assert {'TTS-MY-IMAGE-MIN-600','TTS-MY-PRIMARY-IMAGE','TTS-MY-PDP-VIDEO'} <= ids


def test_alpha4_full_creative_to_production_contract(tmp_path):
    fx=ROOT/'tests/fixtures/kiyuu_my_tiktok'; req=json.loads((fx/'request.json').read_text(encoding='utf-8'))
    req['creative_references']=[{'reference_id':'REF-1','role':'VISUAL_REFERENCE','source':'user reference','usable_for':['composition'],'not_truth_for':['product appearance']}]
    req['competitor_visual_patterns']=[{'pattern':'generic splash','pattern_status':'CLICHE'},{'pattern':'warm editorial clinical','pattern_status':'WHITESPACE'}]
    req['creative_directions']=[{'direction_id':'TROPICAL_CLINICAL','product_fit':5,'audience_fit':5,'platform_fit':4,'culture_fit':5,'differentiation':5,'production_feasibility':4,'decision':'SELECT'}]
    req['persuasion_frameworks']=['AIDA','FABE','4P']
    req['audience_culture']['race_ethnicity']={'groups':['Malaysia multi-ethnic audience'],'status':'VERIFIED','source_ids':['SRC-TEST'],'relevance':['casting and representation review']}
    req['video_jobs']=[{'family':'VIDEO','surface':'PDP_VIDEO','objective':'Explain daily routine','shopper_question':'How does it fit into a daily routine?','duration_seconds':18}]
    req['production_run']={'asset_ids':[]}
    out=build_project(tmp_path/'proj',req,fx)
    creative=json.loads((tmp_path/'proj/artifacts/creative_contract.json').read_text(encoding='utf-8'))
    assert creative['creative_council']['selected_direction']['direction_id']=='TROPICAL_CLINICAL'
    assert creative['cmf']['status']=='EXECUTION_READY'
    decision=json.loads((tmp_path/'proj/artifacts/decision_trace.json').read_text(encoding='utf-8'))
    assert 'AIDA' in decision['persuasion']['frameworks'] and decision['race_ethnicity']['behavior_inference_allowed'] is False
    video=json.loads((tmp_path/'proj/artifacts/video_creator_plan.json').read_text(encoding='utf-8'))
    assert video['assets'][0]['duration_seconds']==18
    prod=json.loads((tmp_path/'proj/artifacts/production_run.json').read_text(encoding='utf-8'))
    assert prod['replanning_allowed'] is False and prod['asset_count']==3
    assert out['gates']['EXECUTION']['status']=='READY_REVIEW'
