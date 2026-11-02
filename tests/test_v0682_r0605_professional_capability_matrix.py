from copy import deepcopy

from runtime.cbcc.ads_optimization_authority import materialize_ads_optimization_authority
from runtime.cbcc.culture import compile_culture_context
from runtime.cbcc.economics_offer_authority import materialize_economics_offer_authority
from runtime.cbcc.measurement_authority import materialize_measurement_authority
from runtime.cbcc.review_analysis_authority import materialize_review_analysis_authority
from runtime.cbcc.strategy_depth import (
    build_content_matrix_depth, build_culture_depth, build_listing_depth,
    build_market_depth, build_performance_learning_depth, build_positioning_depth,
    build_sku_depth, build_value_depth, build_visual_depth,
)
from runtime.cbcc.tools.experiment import compile_experiment_analysis
from runtime.cbcc.tools.listing import compile_listing
from runtime.cbcc.tools.visual import validate_photography_contract
from runtime.cbcc.video_creator import build_video_creator_plan, project_dynamic_art_direction_to_assets

BASE={'delivery_mode':'FULL_PROJECT','product':{'name':'Demo Gel','category':'beauty'},'target':{'market':'Malaysia','platform_family':'tiktok_shop','site':'MY','category':'beauty'},'shopper_questions':['Why?']}


def _positioning(request=BASE):
    value=build_value_depth(request,{'product':request['product']},request['shopper_questions'])
    return build_positioning_depth(request,value,{},build_sku_depth(request,{},{}),{},request['shopper_questions'])


def test_B_market_customer_voice_changes_positioning_tension():
    market={'customer_voice':{'theme_summary':[{'theme':'sticky feel','weighted_mentions':18,'dominant_sentiment':'NEGATIVE','source_ids':['M1']}]}}
    value=build_value_depth(BASE,{'product':BASE['product']},BASE['shopper_questions'])
    yes=build_positioning_depth(BASE,value,build_market_depth(market,BASE),build_sku_depth(BASE,build_market_depth(market,BASE),{}),{},BASE['shopper_questions'])
    no=build_positioning_depth(BASE,value,build_market_depth(None,BASE),build_sku_depth(BASE,build_market_depth(None,BASE),{}),{},BASE['shopper_questions'])
    assert yes['market_tension_candidates'][0]['theme']=='sticky feel' and not no['market_tension_candidates']


def test_C_economics_missing_is_explicit_unknown_and_real_input_changes_sku_decision():
    missing=materialize_economics_offer_authority({'status':'NOT_SUPPLIED','currency':'MYR'},{'delivery_mode':'FULL_PROJECT'}, {})
    full={'status':'READY','scenarios':[{'scenario_id':'S1','price':59}]}
    assert missing['status']=='TO_VERIFY' and 'price' in missing['missing_inputs']
    assert build_sku_depth(BASE,{},missing)['economics_status']=='TO_VERIFY'
    assert build_sku_depth(BASE,{},full)['economics_scenarios'][0]['price']==59


def test_D_positioning_changes_listing_and_content_message():
    a=deepcopy(BASE); b=deepcopy(BASE)
    a['positioning']={'primary_conversion_proposition':'Oil-balance clarity'}; b['positioning']={'primary_conversion_proposition':'Simple daily hydration'}
    pa=_positioning(a); pb=_positioning(b)
    assert build_listing_depth(a,None,pa,a['target'])['title_job'] != build_listing_depth(b,None,pb,b['target'])['title_job']
    asset=[{'asset_id':'A1','family':'VISUAL','surface':'GALLERY','consumer_question':'Why?','strategic_job':'Resolve relevance','decision_intent':'RELEVANCE'}]
    assert build_content_matrix_depth([a['target']],{},asset,pa)[0]['hook']=='Oil-balance clarity'
    assert build_content_matrix_depth([b['target']],{},asset,pb)[0]['hook']=='Simple daily hydration'


def test_E_search_keywords_change_listing_search_architecture():
    lc={'primary_locale':'en-MY','visible_copy_locales':['en-MY'],'delivery_locale':'zh-CN'}; fields={'title':'Demo Gel'}
    one=compile_listing(fields,BASE['product'],[],{},lc,[{'term':'oil control gel','cluster':'CORE','priority':10}],BASE['target'])
    two=compile_listing(fields,BASE['product'],[],{},lc,[{'term':'daily moisturiser','cluster':'CORE','priority':10}],BASE['target'])
    assert one['keyword_priority'] != two['keyword_priority']
    assert build_listing_depth(BASE,{'compiled':one},_positioning(),BASE['target'])['search_intent_architecture'] != build_listing_depth(BASE,{'compiled':two},_positioning(),BASE['target'])['search_intent_architecture']


def test_F_culture_input_changes_localization_rows():
    supplied=compile_culture_context({'statements':[{'statement':'Use Malaysia-localized language hierarchy','status':'VERIFIED','confidence':1,'source_ids':['C1']}],'intersectionality':{'ethnicity':['multi-ethnic']}})
    missing=compile_culture_context(None)
    assert build_culture_depth([BASE['target']],supplied)['platform_audience_culture_rows'] != build_culture_depth([BASE['target']],missing)['platform_audience_culture_rows']


def test_G_photography_and_cmf_change_visual_execution():
    culture=compile_culture_context(None); p=_positioning()
    p1={'camera':{'focal_length_mm':85},'lighting':{'cct':5200},'cmf':{'material':'tube','finish':'semi-gloss'}}
    p2={'camera':{'focal_length_mm':50},'lighting':{'cct':4300},'cmf':{'material':'tube','finish':'matte'}}
    v1=build_visual_depth({**BASE,'photography_contract':p1},{'cmf':p1['cmf']},culture,p,[],validate_photography_contract(p1))
    v2=build_visual_depth({**BASE,'photography_contract':p2},{'cmf':p2['cmf']},culture,p,[],validate_photography_contract(p2))
    assert v1['camera']!=v2['camera'] and v1['material_lighting_profile']!=v2['material_lighting_profile']


def test_H_explicit_dynamic_job_controls_motion_timing_audio_projection():
    asset={'asset_id':'A1','family':'VIDEO','surface':'PDP_VIDEO','asset_type':'VIDEO','consumer_question':'How?','decision_intent':'USAGE','asset_art_direction':{}}
    job={'family':'VIDEO','surface':'PDP_VIDEO','source_asset':asset,'duration_seconds':12,'shots':[{'shot':'OPEN','seconds':4},{'shot':'PROOF','seconds':8}],'camera_motion':'slow push','audio':{'voice_locale':'en-MY'}}
    plan=build_video_creator_plan('P',[{'family':'VIDEO','surface':'PDP_VIDEO'}],['How?'],{'primary_locale':'en-MY'},[job],assets=[asset])
    art=project_dynamic_art_direction_to_assets({'assets':[asset]},plan)['assets'][0]['asset_art_direction']
    assert art['timing']['duration_seconds']==12 and art['motion']['camera_motion']=='slow push' and art['audio']['voice_locale']=='en-MY'


def _density(label,source):
    return {'what':label,'why':'why','evidence':[source],'tradeoff':'hold unrelated layers','execution':'one variable','measurement':'declared metrics','source_refs':[source],'source_type':'ADS_PERFORMANCE','recency':'2026-11-01','exact_fact':'fact','interpretation':'directional evidence only','confidence':'HIGH','downstream_use':['creative'],'conflict_status':'NO_DECLARED_CONFLICT'}


def test_I_ads_optimization_consumes_performance_offer_and_economics():
    row={'optimization_id':'A1','objective':'qualified traffic','funnel_state':'CLICK_TO_PDP','audience_state':'qualified','consumer_tension':'needs proof','creative_hypothesis':'proof-first','creative_mechanism':'tension-to-proof','proof':['C1'],'offer':'No automatic launch discount','landing_handoff':'PDP','spend_boundary':'CPA boundary','economics_boundary_ref':'phase2_economics_offer_authority.break_even','attribution':'directional only','test_structure':'A/B','test_variable':'hook','hold_constant':['audience','price'],'success_rule':'CTR up/CVR stable','failure_rule':'stop if CVR down','failure_diagnosis':'message mismatch','repair_route':'FIRST_IMPRESSION_CREATIVE_ONLY','learning_handoff':['creative'],**_density('change hook','ADS')}
    req={'delivery_mode':'FULL_PROJECT','sources':[{'source_id':'ADS','source_type':'ADS_PERFORMANCE','as_of':'2026-11-01'}],'advertising_optimization':{'rows':[row]}}
    perf={'status':'PORTFOLIO_CALCULATED','aggregate':{'metrics':{'cpa':12,'roas':4.9}},'rows':[],'diagnosis_required':[],'scale_candidates':[]}
    phase2={'status':'READY','break_even':{'cpa':{'status':'AVAILABLE','value':17},'cpc':{'status':'AVAILABLE','value':0.68},'roas':{'status':'AVAILABLE','value':3.47}},'pricing_decision':{'density_status':'READY','decision':'MYR 59'},'offer_decision':{'density_status':'READY','decision':'No automatic launch discount'}}
    out=materialize_ads_optimization_authority(perf,req,{'phase2_business_status':'READY','phase2_economics_offer_authority':phase2})
    assert out['status']=='READY' and out['optimization_rows'][0]['economics_binding_status']=='READY' and out['performance_analysis']['aggregate']['metrics']['cpa']==12


def test_J_feedback_routes_smallest_repair_and_freezes_product_truth():
    legacy={'status':'AGGREGATED_FROM_CLASSIFIED_INPUT','revision_actions':[{'category':'EXPECTATION_GAP','routes':['LISTING','FAQ'],'frozen_layers':['PRODUCT_TRUTH']}], 'issues':[],'summary':{},'defect_vs_communication':{}}
    route=build_performance_learning_depth(None,legacy,None)['strategy_revision_routing']['routes'][0]
    assert route['edit_layers']==['LISTING','FAQ'] and route['freeze_layers']==['PRODUCT_TRUTH']
    row={'issue_class':'EXPECTATION_GAP','issue_signal':'mismatch','root_cause_hypothesis':'listing unclear','root_cause_layer':'LISTING','root_cause_status':'WORKING_HYPOTHESIS','responsible_layer':'LISTING','repair_action':'clarify FAQ','repair_scope':['LISTING.FAQ'],'frozen_layers':['PRODUCT_TRUTH'],'why_not_broader_rework':'no defect evidence','verification_metric':'GAP_RATE','success_rule':'down','failure_rule':'reclassify','learning_handoff':['LISTING'],**{**_density('clarify','REV'),'source_type':'CUSTOMER_REVIEW_EXPORT'}}
    req={'delivery_mode':'FULL_PROJECT','sources':[{'source_id':'REV','source_type':'CUSTOMER_REVIEW_EXPORT','as_of':'2026-11-01'}],'review_analysis':{'rows':[row]}}
    assert materialize_review_analysis_authority(legacy,req)['repair_rows'][0]['repair_scope']==['LISTING.FAQ']


def test_K_experiment_remains_evidence_while_measurement_plan_owns_next_decision():
    exp=compile_experiment_analysis({'control_success':50,'control_total':1000,'test_success':80,'test_total':1000})
    common={'what':'test hero','why':'uncertainty','evidence':['M'],'tradeoff':'hold price','execution':'A/B','measurement':'progression','source_refs':['M'],'source_type':'MEASUREMENT_BASELINE','recency':'2026-11-01','exact_fact':'baseline','interpretation':'baseline','confidence':'HIGH','downstream_use':['LISTING'],'conflict_status':'NO_DECLARED_CONFLICT'}
    row={'measurement_id':'M1','business_question':'hero?','decision_object':'LISTING.HERO','hypothesis':'hero helps','primary_metric':'PROGRESSION','metric_definition':'x/y','desired_direction':'UP','baseline':0.05,'target_or_mde':0.02,'metric_source_ref':'M','attribution_method':'SESSION_AB','observation_window':'WINDOW','analysis_unit':'SESSION','guardrails':['CVR'],'test_type':'A_B','changed_variable':'HERO','held_constants':['PRICE'],'variants':['C','T'],'deployment_pool':'PDP','randomization_unit':'SESSION','sequential_monitoring_policy':'NO_PEEKING','learning_handoff':['LISTING'],'sample_size_rule':'predeclared','duration_or_stop_rule':'sample reached','success_rule':'MDE met','failure_rule':'not met','next_decision':'promote locally or keep baseline',**common}
    def priority(p): return {'priority':p,'status':'ACTIVE','action':p,'decision_ref':'M1','next_decision':'next',**common}
    nxt={'input_id':'N1','status':'PLANNED_COLLECTION','decision_ref':'M1','exact_missing_input':'post-test metric','source_or_owner':'analytics','downstream_unblock':'M1','decision_trigger':'after stop',**common}
    req={'delivery_mode':'FULL_PROJECT','sources':[{'source_id':'M','source_type':'MEASUREMENT_BASELINE','as_of':'2026-11-01'}],'measurement_plan':{'rows':[row],'priorities':[priority('P0'),priority('P1'),priority('P2')],'next_inputs':[nxt]}}
    legacy={'status':'STRATEGY_AUTHORITY_COMPILED','delivery_mode':'FULL_PROJECT','sections':{'09_risk_measurement_priority_next_steps':{}}}
    out=materialize_measurement_authority(legacy,req,exp)['measurement_authority_v0676']
    assert out['status']=='READY' and out['experiment_evidence']==exp and out['measurement_rows'][0]['next_decision']=='promote locally or keep baseline'
