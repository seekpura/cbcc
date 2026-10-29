from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))

from cbcc.tools.listing import localized_copy_audit
from cbcc.compliance import compile_compliance
from cbcc.prompt_compiler import compile_asset_prompt


def test_field_bound_approved_claim_authorizes_only_its_numeric_tokens():
    fields={'highlights':['20,000mAh capacity','Up to 200W total output']}
    localized={'en-US':{'highlights':['20,000mAh capacity','Up to 200W total output','Two USB-C ports support up to 100W each under supported conditions.']}}
    claims=[{'claim_id':'C2','text':'Two USB-C ports support up to 100W each under supported conditions.','status':'APPROVED'}]
    blocked=localized_copy_audit(fields,{'primary_locale':'en-US'},localized,claims,{})
    assert blocked['issues'] and '100W' in blocked['issues'][0]['extra_target_numbers']
    allowed=localized_copy_audit(fields,{'primary_locale':'en-US'},localized,claims,{'highlights':['C2']})
    assert allowed['issues']==[]
    assert allowed['reviewed'][0]['numeric_equivalence']=='PASS_WITH_FIELD_CLAIM_AUTHORITY'
    assert '100W' in allowed['reviewed'][0]['authorized_extra_numbers']


def test_compliance_issue_shape_is_stable_and_asset_routing_is_actionable_first():
    out=compile_compliance(
        {'product':{'name':'x'}},
        [{'claim_id':'C1','status':'APPROVED'}],
        {'status':'PASS'},
        [{'asset_id':'A','claim_ids':['C1']},{'asset_id':'B','claim_ids':['C2']}],
        {'status':'VERIFIED_FOR_REQUEST'},
        {'pending':[]},
    )
    assert out['status']=='HOLD'
    assert out['issues'][0]['code']=='UNAPPROVED_CLAIM_REFERENCE'
    assert out['issues'][0]['asset_id']=='B'
    assert out['issues'][0]['claim_ids']==['C2']
    required=set(out['issue_contract']['required_keys'])
    assert all(required.issubset(row) for row in out['issues'])
    assert out['asset_checks'][1]['unapproved_claim_ids']==['C2']


def test_canonical_prompt_explicitly_binds_consumer_question_and_product_truth_without_ids_or_product_name():
    asset={
        'asset_id':'AST-SECRET','surface':'GALLERY','family':'VISUAL','asset_type':'IMAGE',
        'decision_intent':'PROOF','consumer_question':'Why should I trust this product?',
        'belief_target':'credible proof','strategic_job':'Show verified proof','product_fidelity':'LOCKED_PIXEL',
        'product_presence':{'planning_state':'REQUIRED'},
    }
    bundle=compile_asset_prompt(
        asset, {'name':'SECRET PRODUCT NAME'}, {'platform_family':'TIKTOK_SHOP','market':'MY'},
        {}, {'primary_locale':'en-MY','visible_copy_locales':['en-MY']},
        source_product_assets=[{'asset_id':'REAL-SECRET','pixel_lock':True}],
    )
    cn=bundle['prompt_cn']; en=bundle['prompt_en']; en_lower=en.lower()
    # Product Truth remains explicit, while the exact phrase “真实产品” is not a semantic requirement.
    # This fixture explicitly selects LOCKED_PIXEL, so source-lock semantics must still be preserved.
    assert '消费者问题' in cn and 'Product Truth' in cn and 'LOCKED_PIXEL' in cn
    assert 'Consumer decision question' in en and 'Product Truth binding' in en and 'LOCKED_PIXEL' in en
    assert bundle['design_card']['product_identity']['product_fidelity']=='LOCKED_PIXEL'
    assert bundle['machine_visual_contract']['fidelity']['real_product_master_required'] is True
    assert bundle['machine_visual_contract']['fidelity']['real_product_master_substitution_allowed'] is False
    assert 'why should i trust this product?' in en_lower
    for forbidden in ['ast-secret','real-secret','secret product name']:
        assert forbidden not in en_lower
    assert any(row.get('strategy_parameter')=='consumer decision question / Product Truth execution binding' for row in bundle['parameter_trace'])
