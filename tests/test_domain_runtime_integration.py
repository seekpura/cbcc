from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project

def test_domain_engines_are_consumed_by_runtime(tmp_path):
    req={
      'project_id':'DEPTH-E2E','sku':'S1','planning_only':True,
      'product':{'name':'Synthetic Test Product','net_content':'30g'},
      'sources':[{'source_id':'SRC1','kind':'TEST_FIXTURE'}],
      'claims':[],
      'target':{'market':'Test','jurisdiction':'T','platform_family':'test_platform','site':'TEST','primary_locale':'en-US','surfaces':['PDP'],'currency':'USD'},
      'market_rows':[{'seller':'A','price':10,'units':10,'revenue':100,'configuration':'x'},{'seller':'B','price':20,'units':5,'revenue':100,'configuration':'y'}],
      'offer_economics':{'currency':'USD','price':100,'costs':{'landed_cost':20,'platform_fee':{'type':'rate','value':0.1},'fulfillment':5,'affiliate_commission':0,'ad_cost':10,'tax':0,'refund_allowance':2}},
      'listing_input':{'fields':{'title':'Synthetic Test Product 30g'},'rules':{'title':{'max_chars':80}},'keywords':[{'term':'test product','cluster':'CORE','volume':10,'source_id':'K1'}]},
      'ad_analysis':{'price':100,'costs':{'landed_cost':20,'platform_fee':10,'fulfillment':5,'affiliate_commission':0,'ad_cost':0,'tax':0,'refund_allowance':2},'ad_data':{'impressions':1000,'clicks':10,'orders':1,'spend':20,'revenue':100},'thresholds':{'min_ctr':0.02}},
      'feedback_rows':[{'category':'MISUNDERSTANDING','severity':'HIGH','text':'thought it included X'}],
      'experiment':{'control_success':50,'control_total':1000,'test_success':80,'test_total':1000},
      'foundation_needs':{'front':True,'cutout':True},
      'product_fidelity':'LOCKED_PIXEL',
      'photography_contract':{'capture_mode':'REAL_PHOTO','camera':{'focal_length_mm':85,'camera_height':'product center','focus_plane':'front label'},'composition':{'product_occupancy':{'height_pct':70}},'lighting':{'key':{'direction':'camera-left','modifier':'large diffusion'},'cct':5200,'highlight_policy':'protect label'},'color_management':{'output_space':'sRGB','product_color_fidelity':'truth-first'}}
    }
    pack=tmp_path/'packs'; pack.mkdir(); (pack/'test.yaml').write_text('''pack_id: test\nplatform_family: test_platform\nsite: "*"\nstatus: TEST_FIXTURE_VERIFIED\nsynthetic_for_test: true\ncapabilities: [LISTING, SEARCH, OFFER_PROMOTION, VISUAL, VIDEO, CREATOR_AFFILIATE, PAID, CX, MEASUREMENT, COMPLIANCE]\nsurfaces: [PDP]\nrule_atoms: []\nresearch_required_for: []\n''')
    build_project(tmp_path/'proj',req,pack)
    d=json.loads((tmp_path/'proj/artifacts/domain_analysis.json').read_text())
    assert d['market']['market_capacity']['units']==15
    assert d['economics']['contribution']==53
    assert d['listing']['compiled']['pass']
    assert any(x['symptom']=='LOW_CTR' for x in d['ads']['diagnosis'])
    assert d['feedback']['issues'][0]['routes'][0]=='LISTING'
    assert 'p_value_two_sided' in d['experiment']
    foundation=json.loads((tmp_path/'proj/artifacts/foundation_plan.json').read_text()); assert [x['role'] for x in foundation['roles']]==['PRODUCT_FRONT_MASTER','CUTOUT_MASTER']
    photo=json.loads((tmp_path/'proj/artifacts/photography_validation.json').read_text()); assert photo['pass']
    decision=json.loads((tmp_path/'proj/artifacts/decision_trace.json').read_text())
    assert decision['domain_inputs']['market']=='CALCULATED_FROM_INPUT_ROWS'
