from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.decision import compile_persuasion_frameworks
from cbcc.research import compile_research_gate, apply_host_research_response
from cbcc.creative import compile_curation, compile_creative_council, compile_cmf, compile_inclusive_photography
from cbcc.culture import compile_culture_context


def test_persuasion_frameworks_are_decision_aids_not_asset_templates():
    default_out=compile_persuasion_frameworks(['What is it?','Why choose it?'],{'material':'steel'},{'status':'CALCULATED_FROM_INPUTS'})
    assert default_out['status']=='NOT_REQUESTED' and default_out['frameworks']=={}
    out=compile_persuasion_frameworks(['What is it?','Why choose it?'],{'material':'steel'},{'status':'CALCULATED_FROM_INPUTS'},requested=['AIDA','FABE','4P'])
    assert {'AIDA','FABE','4P'} <= set(out['frameworks'])
    assert 'optional reasoning tools' in out['principle'].lower()


def test_research_gate_creates_host_action_and_can_be_resolved():
    gate=compile_research_gate([{'id':'R1','topic':'current beauty claim rules','domain':'PLATFORM_RULE','required_for':['PLATFORM_COMPILE']}],[],'2026-10-27')
    assert gate['status']=='RESEARCH_REQUIRED' and gate['actions'][0]['preferred_source']=='OFFICIAL_CURRENT_SOURCE'
    out=apply_host_research_response(gate,[{'action_id':gate['actions'][0]['action_id'],'status':'RESOLVED'}])
    assert out['host_status']=='RESOLVED' and not out['unresolved_action_ids']


def test_curation_keeps_reference_role_separate_from_truth_and_council_selects():
    cur=compile_curation([{'reference_id':'R','role':'TEXTURE_REFERENCE','source':'upload','usable_for':['texture color'],'not_truth_for':['brand palette']}],[{'pattern':'generic splash','pattern_status':'CLICHE'},{'pattern':'editorial negative space','pattern_status':'WHITESPACE'}])
    assert cur['references'][0]['not_truth_for']==['brand palette'] and len(cur['category_cliches'])==1
    council=compile_creative_council([
      {'direction_id':'A','product_fit':5,'audience_fit':4,'platform_fit':4,'culture_fit':4,'differentiation':5,'production_feasibility':4},
      {'direction_id':'B','product_fit':3,'audience_fit':3,'platform_fit':3,'culture_fit':3,'differentiation':3,'production_feasibility':5}
    ],cur,{'product':{'name':'x'}},{'status':'COMPILED_FROM_SUPPLIED_EVIDENCE'},{'status':'VERIFIED_FOR_REQUEST'})
    assert council['status']=='SELECTED' and council['selected_direction']['direction_id']=='A'


def test_cmf_and_inclusive_photo_compile_from_execution_inputs():
    cmf=compile_cmf({'color':'ivory/green','material':'real tube','finish':'soft controlled highlight','surface_behavior':{'gloss':'low'}})
    assert cmf['status']=='EXECUTION_READY'
    culture=compile_culture_context({'race_ethnicity':{'groups':['multi-ethnic Malaysian audience'],'status':'VERIFIED','source_ids':['S1'],'relevance':['casting review']},'intersectionality':{'ethnicity':['multi-ethnic'],'gender':['inclusive']},'casting':{'skin_tone':'range appropriate to target market','hair':'locally plausible natural variation'}})
    inc=compile_inclusive_photography(culture,{'human':{'present':True,'skin_tone_exposure':{'metering_priority':'skin highlight preservation','highlight_protection':'protect specular highlights'}}})
    assert culture['race_ethnicity']['behavior_inference_allowed'] is False
    assert inc['status']=='APPLICABLE' and inc['review_required'] is True
