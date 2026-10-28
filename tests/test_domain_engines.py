from pathlib import Path
import sys,math
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.tools.market import analyze_market
from cbcc.tools.economics import unit_economics,allowable_cpa,allowable_cpc,scenario_matrix
from cbcc.tools.listing import keyword_architecture,compile_listing
from cbcc.tools.ads import analyze_ads
from cbcc.tools.feedback import analyze_feedback
from cbcc.tools.experiment import evaluate_binary_experiment

ROWS=[
 {'seller':'A','price':10,'units':100,'revenue':1000,'configuration':'30ml'},
 {'seller':'A','price':12,'units':80,'revenue':960,'configuration':'30ml'},
 {'seller':'B','price':20,'units':40,'revenue':800,'configuration':'50ml'},
 {'seller':'C','price':30,'units':30,'revenue':900,'configuration':'50ml'},
 {'seller':'D','price':32,'units':25,'revenue':800,'configuration':'100ml'},
]
def test_market_engine_real_metrics():
    o=analyze_market(ROWS,10)
    assert o['market_capacity']['units']==275
    assert o['concentration']['cr3']>80
    assert o['concentration']['hhi']>0
    assert len(o['price_bands'])>=3
    assert o['configuration'][0]['units_per_item']>0
    assert o['data_quality']['note']

def test_economics_waterfall_and_headroom():
    costs={'landed_cost':20,'platform_fee':{'type':'rate','value':0.1},'fulfillment':5,'affiliate_commission':0,'ad_cost':10,'tax':0,'refund_allowance':2}
    o=unit_economics(100,costs)
    assert o['status']=='CALCULATED_FROM_INPUTS' and o['contribution']==53
    assert allowable_cpa(100,costs)==63
    assert math.isclose(allowable_cpc(100,costs,0.05),3.15)
    m=scenario_matrix([{'scenario_id':'hero','sku':'A','price':100,'costs':costs}])
    assert m[0]['break_even_roas']>1

def test_listing_engine_trace_and_keyword_aggregation():
    kw=keyword_architecture([{'term':'oil control gel','cluster':'CORE','volume':100,'source_id':'K1'},{'term':'blemish gel','cluster':'PROBLEM','volume':50,'source_id':'K2'}])
    assert kw['clusters']['CORE'][0]['term']=='oil control gel'
    fields={'title':'KIYUU Oil Control Gel 30g','bullets':['Daily gel moisturiser'],'_source_refs':{'title':['S1']}}
    o=compile_listing(fields,{'net_weight':'30g'},[],{'title':{'max_chars':80,'required_terms':['KIYUU']}})
    assert o['pass'] and o['traceability'][0]['source_ids']==['S1']
    bad=compile_listing({'title':'Product 24H 30g'}, {'net_weight':'30g'}, [], {'title':{'max_chars':80}})
    assert not bad['checks']['numeric_trace']['pass']

def test_ads_diagnosis_uses_economics_and_caller_thresholds():
    costs={'landed_cost':20,'platform_fee':10,'fulfillment':5,'affiliate_commission':0,'ad_cost':0,'tax':0,'refund_allowance':2}
    o=analyze_ads({'impressions':1000,'clicks':10,'orders':1,'spend':20,'revenue':100},100,costs,{'min_ctr':0.02})
    assert o['metrics']['ctr']==0.01
    assert any(x['symptom']=='LOW_CTR' for x in o['diagnosis'])
    assert o['economics']['break_even_roas'] is not None

def test_feedback_aggregates_semantic_labels_without_reclassifying():
    o=analyze_feedback([{'category':'MISUNDERSTANDING','severity':'HIGH','text':'I thought it included X'},{'category':'PRODUCT_DEFECT','severity':'CRITICAL','text':'pump broken'}])
    assert o['summary']['total']==2
    mi=[x for x in o['issues'] if x['category']=='MISUNDERSTANDING'][0]
    assert 'LISTING' in mi['routes']

def test_experiment_has_uncertainty_not_just_lift():
    o=evaluate_binary_experiment(50,1000,80,1000)
    assert 'p_value_two_sided' in o and o['control_ci95']['lower'] < o['control_rate'] < o['control_ci95']['upper']
    assert o['decision'] in {'EVIDENCE_SUPPORTS_TEST','NO_CLEAR_WINNER'}
