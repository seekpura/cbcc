from __future__ import annotations
import json
from copy import deepcopy

from cbcc.creative import compile_inclusive_photography, apply_inclusive_photography_to_assets
from cbcc.product_visual_intelligence import compile_product_visual_intelligence
from cbcc.reference_guided_native_authority import apply_reference_guided_native_authority

culture={
    'status':'COMPILED_FROM_SUPPLIED_EVIDENCE',
    'statements':[{'statement':'Evidence-bounded local representation only.','status':'VERIFIED','source_ids':['SRC-CULTURE-01'],'implications':['casting review']}],
    'intersectionality':{'representation':['non-tokenistic, task-led representation']},
    'race_ethnicity':{'groups':[],'source_ids':['SRC-CULTURE-01'],'status':'PENDING','relevance':['context only'],'behavior_inference_allowed':False},
    'casting_constraints':{},
    'principle':'Identity dimensions are context signals, not automatic behavior predictions.',
}
complete={
    'casting_role':'adult shopper demonstrating the real routine task',
    'age_context':'adult; exact age not inferred',
    'skin_tone':'deep skin tone is an authored scene choice, not a behavior proxy',
    'hair_texture_style':'coily natural texture preserved with truthful edge separation',
    'grooming_makeup':'natural skin texture; no whitening or youthifying retouch',
    'wardrobe_accessories':'task-led neutral everyday wardrobe; no ethnicity-as-costume styling',
    'body_age_disability_representation':'natural adult representation; preserve visible aids/age markers if present',
    'religious_cultural_presentation':'neutral unless supported by explicit evidence; no invented signifiers',
    'pose':'body slightly turned while one hand reaches for the product',
    'expression':'calm attentive expression appropriate to the routine',
    'gaze':'gaze follows the real product interaction',
    'hands':'five-finger anatomy checked; grip preserves label visibility',
    'product_interaction':'real product held upright in the source-supported routine relationship',
    'stereotype_guard':'identity does not imply need, income, skin condition, willingness to pay, or purchase intent',
    'ai_bias_review':['no whitening','no slimming','no hair homogenization','check hands and body proportions'],
    'exposure_lighting_handling':{'skin_product_metering':'meter skin and label separately','highlight_policy':'protect skin/package highlights','fill_policy':'broad neutral fill plus negative fill'},
}

def human(context):
    return {'asset_id':'AST-HUMAN','asset_type':'IMAGE','surface':'GALLERY','decision_intent':'USAGE','creative_direction':{'route':'HUMAN_CONTEXT_ACTION'},'asset_art_direction':{'subject_system':{'subject_type':'PERSON','primary_subject':'adult shopper performing the routine task','living_subject_required':True},'human_context':deepcopy(context),'scene':'real morning bathroom vanity routine','composition_grammar':'hand-to-product routine relationship','camera_or_view':'eye-level environmental close view','lighting':{'key':{'direction':'window-side broad key'}},'cmf':{'color':'neutral warm field','material':'real glass and skin','finish':'truthful soft specular response'},'product_presence':{'planning_state':'REQUIRED','product_role':'ACTIVE_OBJECT_IN_USE'}},'visual_production_signature':{'context_role':'human routine use context','visual_job':'show real product handling in routine','camera_or_view':'eye-level human use context'}}

nonhuman={'asset_id':'AST-MACRO','asset_type':'IMAGE','surface':'GALLERY','decision_intent':'MATERIAL_SENSORY','creative_direction':{'route':'MATERIAL_SENSORY_OBJECT'},'asset_art_direction':{'subject_system':{'subject_type':'PRODUCT_OR_OBJECT','primary_subject':'real product bottle'},'scene':'controlled macro material study','camera_or_view':'100mm macro product detail','lighting':{'key':{'direction':'rear-side grazing'}},'cmf':{'color':'neutral','material':'real glass','finish':'controlled edge highlight'},'product_presence':{'planning_state':'REQUIRED','product_role':'HERO_DETAIL'}},'visual_production_signature':{'context_role':'material detail evidence','visual_job':'show truthful material response','camera_or_view':'100mm macro'}}

ready=compile_inclusive_photography(culture,{},[human(complete),nonhuman])
assert len(ready['asset_execution'])==1
row=ready['asset_execution'][0]
assert row['asset_id']=='AST-HUMAN' and row['status']=='READY'
assert row['authority']=='INCLUSIVE_PHOTOGRAPHY_AUTHORITY'
assert row['human_context']==complete
assert row['behavior_inference_allowed'] is False
assert row['runtime_may_invent_missing_identity_or_culture'] is False
assert row['source_refs']==['SRC-CULTURE-01']
assert 'No automatic whitening' in row['skin_tone_exposure']['post']
assert 'no disability erasure' in row['ai_bias_controls']

projected=apply_inclusive_photography_to_assets({'assets':[human(complete),nonhuman]},ready)
by_id={x['asset_id']:x for x in projected['assets']}
assert by_id['AST-HUMAN']['inclusive_photography']['authority']=='INCLUSIVE_PHOTOGRAPHY_AUTHORITY'
assert by_id['AST-HUMAN']['asset_art_direction']['inclusive_photography']==by_id['AST-HUMAN']['inclusive_photography']
assert 'inclusive_photography' not in by_id['AST-MACRO']
assert projected['inclusive_photography_execution']['ready_count']==1

incomplete={'casting_role':'adult shopper','pose':'hand reaches toward product','product_interaction':'holds real product upright','stereotype_guard':'do not infer behavior from identity'}
verify=compile_inclusive_photography(culture,{},[human(incomplete)])['asset_execution'][0]
assert verify['status']=='TO_VERIFY'
assert {'skin_tone','hair_texture_style','religious_cultural_presentation','hands'} <= set(verify['missing_authored_decisions'])
assert 'skin_tone' not in verify['human_context'] and 'hair_texture_style' not in verify['human_context']

pvi=compile_product_visual_intelligence({'name':'Demo product'},[],[],None,None)
assert pvi['status']=='PLANNING_ONLY_SOURCE_MASTER_REQUIRED'
assert {'geometry','material','finish','label_or_pack_copy'} <= set(pvi['missing_visual_facts'])

bundle={'design_card':{'product_presence':{'planning_state':'ABSENT','production_state':'ABSENT'},'product_identity':{'product_fidelity':'REFERENCE_GUIDED'}},'model_prompt_cn':'环境信息设计。','model_prompt_en':'Environment-led information design.','production_parameter_closure':{'status':'READY','missing_required_parameters':[]},'renderer_recipe':{'source_product_bindings':[]}}
ref=apply_reference_guided_native_authority(bundle,{'product_fidelity':'REFERENCE_GUIDED'},[])
assert ref['production_assembly_notes']['reference_input_required'] is False
assert ref['production_assembly_notes']['product_reference_generation_mode']=='TRUTH_REFERENCE_ONLY'

print(json.dumps({
    'ready_asset':row['asset_id'],
    'ready_status':row['status'],
    'authority':row['authority'],
    'source_refs':row['source_refs'],
    'nonhuman_inclusion_attached':'inclusive_photography' in by_id['AST-MACRO'],
    'incomplete_status':verify['status'],
    'incomplete_missing':verify['missing_authored_decisions'],
    'runtime_may_invent_missing_identity_or_culture':verify['runtime_may_invent_missing_identity_or_culture'],
    'pvi_status_without_source':pvi['status'],
    'product_absent_reference_required':ref['production_assembly_notes']['reference_input_required'],
},ensure_ascii=False,indent=2))
