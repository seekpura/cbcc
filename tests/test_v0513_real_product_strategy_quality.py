from pathlib import Path
import copy, json, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))

from cbcc.asset_architecture import build_asset_architecture
from cbcc.compiler import build_project


def test_v0513_compound_questions_are_atomic_and_traceable_without_fixed_asset_count():
    target={'target_id':'T1','surfaces':['GALLERY','PDP_VIDEO']}
    content=[
        {'family':'VISUAL','surface':'GALLERY','curation_job':'Resolve visual purchase question'},
        {'family':'VIDEO','surface':'PDP_VIDEO','curation_job':'Resolve operation question'},
    ]
    arch=build_asset_architecture(
        'V0513-Q',target,
        ['What exactly is this essence and where does it fit in a routine?'],
        content,
        category_family='BEAUTY_PERSONAL_CARE',
    )
    assert arch['source_shopper_question_count']==1
    assert arch['atomic_decision_job_count']==2
    assert arch['decision_coverage_summary']['uncovered_atomic_jobs']==0
    intents={x['decision_intent'] for x in arch['decision_question_audit']}
    assert intents=={'IDENTIFY','USAGE'}
    assert arch['asset_count']==2


def test_v0513_host_strategy_request_and_protected_authority_boundary(tmp_path):
    req=json.loads((ROOT/'tests/fixtures/v058_multicategory/beauty_kiyuu.json').read_text(encoding='utf-8'))
    req=copy.deepcopy(req); req['project_id']='V0513-HOST-STRATEGY'
    req['strategy_annotations']={
        'value_ladder':{
            # This must be rejected: Host/model cannot replace deterministic claim ledger.
            'claim_value_ladder':[{'claim_id':'FAKE','claim':'invented'}],
            'host_value_translation':[{'fact':'verified formula fact','perceived_benefit':'Make the decision meaning explicit without creating a new claim.'}],
        },
        'product_strategy':{
            # This must be rejected: Host/model cannot create unit economics.
            'economics_status':'PROFITABLE_BY_HOST_GUESS',
        },
        'positioning':{
            'primary_conversion_proposition':'A decision-specific proposition authored from the verified fact set.',
            'positioning_statement':'A product-specific commercial synthesis that remains bounded by Product Truth.',
        },
    }
    p=tmp_path/'project'; build_project(p,req,ROOT/'platform_packs')
    host=json.loads((p/'artifacts/strategy_host_authoring_request.json').read_text(encoding='utf-8'))
    strategy=json.loads((p/'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
    assert host['status']=='HOST_STRATEGY_AUTHORING_RESPONSE_SUPPLIED'
    assert host['required_output_key']=='strategy_annotations'
    assert host['quality_flags']['host_annotations_supplied'] is True
    app=strategy['strategy_annotation_application']
    assert 'value_ladder.claim_value_ladder' in app['rejected_protected_paths']
    assert 'product_strategy.economics_status' in app['rejected_protected_paths']
    assert strategy['sections']['02_product_truth_value_ladder']['claim_value_ladder'][0].get('claim_id')!='FAKE'
    assert strategy['sections']['04_marketing_core_strategy']['product_strategy']['economics_status']!='PROFITABLE_BY_HOST_GUESS'
    assert strategy['sections']['04_marketing_core_strategy']['positioning']['primary_conversion_proposition'].startswith('A decision-specific')
    assert strategy['sections']['02_product_truth_value_ladder']['host_value_translation']
    assert (p/'artifacts/strategy_host_authoring_request.json').exists()


def test_v0513_missing_economics_never_becomes_false_offer_readiness(tmp_path):
    req=json.loads((ROOT/'tests/fixtures/v058_multicategory/beauty_kiyuu.json').read_text(encoding='utf-8'))
    req=copy.deepcopy(req); req['project_id']='V0513-NO-ECON'
    req.pop('offer_economics',None)
    p=tmp_path/'project'; build_project(p,req,ROOT/'platform_packs')
    strategy=json.loads((p/'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
    sku=strategy['sections']['04_marketing_core_strategy']['product_strategy']
    assert sku['economics_status']=='INSUFFICIENT_DATA'
    assert sku['category_offer_architecture']['economics_validation_status']=='ECONOMICS_NOT_SUPPLIED_DO_NOT_LOCK_OFFER'


def test_v0513_final_copy_allows_extra_number_only_when_field_claim_ref_authorizes_it():
    from cbcc.tools.listing import localized_copy_audit
    fields={'highlights':['20,000mAh capacity','Up to 200W total output']}
    localized={'en-US':{'highlights':['20,000mAh capacity','Up to 200W total output','Two USB-C ports support up to 100W each under supported conditions.']}}
    claims=[{'claim_id':'C2','text':'Two USB-C ports support up to 100W each under supported conditions.','status':'APPROVED'}]
    blocked=localized_copy_audit(fields,{'primary_locale':'en-US'},localized,claims,{})
    assert blocked['issues'] and '100W' in blocked['issues'][0]['extra_target_numbers']
    allowed=localized_copy_audit(fields,{'primary_locale':'en-US'},localized,claims,{'highlights':['C2']})
    assert allowed['issues']==[]
    row=allowed['reviewed'][0]
    assert row['numeric_equivalence']=='PASS_WITH_FIELD_CLAIM_AUTHORITY'
    assert '100W' in row['authorized_extra_numbers']
