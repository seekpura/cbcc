from __future__ import annotations
from pathlib import Path
import importlib.util, sys

MODULE=Path(__file__).parents[1]/'runtime/cbcc/economics_offer_authority.py'
spec=importlib.util.spec_from_file_location('economics_offer_authority_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)

DENSITY=('what','why','evidence','tradeoff','execution','measurement')

def explicit_request():
    return {
      'delivery_mode':'FULL_PROJECT',
      'offer_economics':{
        'currency':'MYR','price':59.0,
        'costs':{
          'landed_cost':20.0,'platform_fee':{'type':'rate','value':0.08},'payment_fee':{'type':'rate','value':0.02},
          'fulfillment':4.0,'affiliate_commission':{'type':'rate','value':0.10},'tax':0.0,'refund_allowance':2.0,'ad_cost':6.0,
        },
        'click_to_order_cvr':0.04,'target_contribution':8.0,
        'pricing_decision':{
          'decision':'MYR 59 base price','what':'Use MYR 59 as the current base selling price.','why':'Explicit economics and offer strategy support this base.',
          'evidence':['SRC-ECON'],'tradeoff':'Do not chase the market valley with a lower price without margin evidence.',
          'execution':'Use MYR 59 in the approved listing/offer once publish scope is cleared.','measurement':'Track CVR, contribution/order and paid-media efficiency.'
        },
        'offer_decision':{
          'status':'APPLIED','decision':'No launch discount; preserve contribution headroom for affiliate/ads.',
          'what':'Launch without an automatic discount.','why':'Current contribution pool is reserved for creator/paid acquisition.',
          'evidence':['SRC-ECON'],'tradeoff':'Sacrifice discount-led click lift to protect contribution.',
          'execution':'Keep base price; test discount only as a separately authored experiment.','measurement':'Contribution/order, CVR and incremental lift.'
        }
      }
    }

def strict_payload(req):
    offer=req.get('offer_economics') or {}; costs=offer.get('costs') or {}
    missing=[k for k in ('landed_cost','platform_fee','fulfillment','affiliate_commission','tax','refund_allowance') if k not in costs]
    ready=offer.get('price') is not None and not missing
    return {
      'status':'READY' if ready else 'PARTIAL_MISSING_INPUT','currency':offer.get('currency'),
      'market_price_bands':[{'low':39,'high':69}],'market_price_valleys':[{'band':'LOW'}],'price_configuration_matrix':[],
      'scenarios':[{'scenario_id':'BASE','price':offer.get('price'),'status':'CALCULATED_FROM_EXPLICIT_INPUTS' if ready else 'MISSING_INPUT',
        'missing_inputs':missing,'resolved_components':costs,'break_even_cpa':17.0 if ready else None,
        'break_even_cpc':0.68 if ready and offer.get('click_to_order_cvr') is not None else None,
        'break_even_roas':3.47 if ready else None,'click_to_order_cvr':offer.get('click_to_order_cvr'),
        'target_contribution':offer.get('target_contribution',0.0)}],
      'pricing_decision':offer.get('pricing_decision') or {'status':'AGENT_DECISION_REQUIRED','decision':None,'why':None},
      'missing_inputs':[{'scenario_id':'BASE','input':x} for x in missing],'downstream_consumers':{},
    }

def test_fully_explicit_economics_pricing_and_offer_reaches_ready():
    req=explicit_request(); out=mod.materialize_economics_offer_authority(strict_payload(req),req)
    assert out['status']=='READY'
    assert out['input_integrity']['payment_fee']['status']=='EXPLICIT'
    assert out['pricing_decision']['density_status']=='READY'
    assert out['offer_decision']['density_status']=='READY'
    assert all(out['pricing_decision'][k] not in (None,'',[],{}) for k in DENSITY)
    assert all(out['offer_decision'][k] not in (None,'',[],{}) for k in DENSITY)
    assert out['break_even']['cpc']['status']=='AVAILABLE'
    assert mod.economics_offer_issues(out)==[]

def test_missing_payment_fee_is_missing_input_not_silent_zero():
    req=explicit_request(); req['offer_economics']['costs'].pop('payment_fee')
    out=mod.materialize_economics_offer_authority(strict_payload(req),req)
    assert out['status']=='TO_VERIFY'
    assert out['input_integrity']['payment_fee']['status']=='MISSING_INPUT'
    assert out['input_integrity']['payment_fee']['exact_fact'] is None
    assert 'payment_fee' in out['missing_inputs']

def test_explicit_zero_payment_fee_is_valid_and_distinct_from_missing():
    req=explicit_request(); req['offer_economics']['costs']['payment_fee']=0.0
    out=mod.materialize_economics_offer_authority(strict_payload(req),req)
    assert out['input_integrity']['payment_fee']['status']=='EXPLICIT'
    assert out['input_integrity']['payment_fee']['exact_fact']==0.0
    assert 'payment_fee' not in out['missing_inputs']

def test_missing_cvr_keeps_break_even_cpc_unavailable_while_cpa_roas_can_remain_available():
    req=explicit_request(); req['offer_economics'].pop('click_to_order_cvr')
    strict=strict_payload(req); strict['scenarios'][0]['break_even_cpc']=None
    out=mod.materialize_economics_offer_authority(strict,req)
    assert out['break_even']['cpc']['status']=='MISSING_INPUT'
    assert out['break_even']['cpc']['value'] is None
    assert out['break_even']['cpa']['status']=='AVAILABLE'
    assert out['break_even']['roas']['status']=='AVAILABLE'

def test_market_price_bands_do_not_become_product_price_or_pricing_decision():
    req={'delivery_mode':'FULL','offer_economics':{'currency':'MYR','costs':{}}}
    strict={'status':'NOT_SUPPLIED','market_price_bands':[{'low':39,'high':69}],'market_price_valleys':[{'price':49}],
            'price_configuration_matrix':[],'scenarios':[],'pricing_decision':{'status':'AGENT_DECISION_REQUIRED','decision':None,'why':None},'missing_inputs':[]}
    out=mod.materialize_economics_offer_authority(strict,req)
    assert out['pricing_decision']['decision'] is None
    assert out['pricing_decision']['density_status']=='TO_VERIFY'
    assert out['input_integrity']['price']['exact_fact'] is None
    assert out['status']=='TO_VERIFY'

def test_math_ready_without_explicit_pricing_or_offer_decisions_is_not_business_ready():
    req=explicit_request(); req['offer_economics'].pop('pricing_decision'); req['offer_economics'].pop('offer_decision')
    strict=strict_payload(req); strict['status']='READY'
    out=mod.materialize_economics_offer_authority(strict,req)
    assert out['pricing_decision']['density_status']=='TO_VERIFY'
    assert out['offer_decision']['density_status']=='TO_VERIFY'
    assert out['status']=='TO_VERIFY'

def test_legacy_sensitivity_defaults_cannot_substitute_for_offer_decision():
    req=explicit_request(); req['offer_economics'].pop('offer_decision')
    strict=strict_payload(req); legacy={'sensitivity':[{'variable':'coupon_discount','value':2.95},{'variable':'affiliate_rate','value':0.1}]}
    out=mod.materialize_economics_offer_authority(strict,req,legacy)
    assert out['offer_decision']['density_status']=='TO_VERIFY'
    assert out['offer_decision']['decision'] is None
    assert out['legacy_compatibility']['sensitivity_is_authority'] is False

def test_non_full_is_unchanged_and_validator_preserves_existing_issues():
    req=explicit_request(); req['delivery_mode']='TASK_SCOPED'; strict=strict_payload(req)
    assert mod.materialize_economics_offer_authority(strict,req)==strict
    full=explicit_request(); full['offer_economics']['costs'].pop('payment_fee',None)
    compiled=mod.materialize_economics_offer_authority(strict_payload(full),full)
    def base(value): return {'status':'INCOMPLETE','issues':[{'code':'EXISTING_STRATEGY_ISSUE'}]}
    result=mod.wrap_validate_economics_offer(base)(compiled,full)
    codes={x['code'] for x in result['issues']}
    assert 'EXISTING_STRATEGY_ISSUE' in codes
    assert 'FULL_ECONOMICS_REQUIRED_INPUT_MISSING_V0676' in codes

def test_compile_wrapper_embeds_phase2_authority_without_destroying_strict_payload():
    req=explicit_request()
    def base(request, market_analysis=None, legacy_economics=None): return strict_payload(request)
    out=mod.wrap_compile_pricing_economics_authority(base)(req,{'price_bands':[]},{'status':'LEGACY'})
    assert out['status']=='READY'
    assert out['phase2_business_status']=='READY'
    assert out['phase2_economics_offer_authority']['status']=='READY'
    assert out['market_price_bands']==[{'low':39,'high':69}]

def test_compile_wrapper_keeps_math_status_but_marks_business_incomplete_when_decisions_missing():
    req=explicit_request(); req['offer_economics'].pop('pricing_decision'); req['offer_economics'].pop('offer_decision')
    def base(request, market_analysis=None, legacy_economics=None): return strict_payload(request)
    out=mod.wrap_compile_pricing_economics_authority(base)(req,None,None)
    assert out['status']=='READY'
    assert out['phase2_business_status']=='TO_VERIFY'
    assert out['phase2_economics_offer_authority']['pricing_decision']['decision'] is None
