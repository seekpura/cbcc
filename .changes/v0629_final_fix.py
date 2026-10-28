from pathlib import Path
import re

# 1) Final Copy numeric claim authorization: field-bound approved claims may authorize
# numeric tokens, while upstream Claim Authority still owns evidence/publication validity.
listing = Path('runtime/cbcc/tools/listing.py')
text = listing.read_text(encoding='utf-8')
old = """    approved_by_id={}\n    for c in claims:\n        cid=str(c.get('claim_id') or c.get('id') or '')\n        status=str(c.get('evidence_grade') or c.get('evidence_level') or '').upper()\n        if cid and status in {'A','B'} and str(c.get('publication_status') or '').upper()!='BLOCKED':\n            approved_by_id[cid]=c\n"""
new = """    numeric_authority_by_id={}\n    for c in claims:\n        cid=str(c.get('claim_id') or c.get('id') or '')\n        grade=str(c.get('evidence_grade') or c.get('evidence_level') or '').upper()\n        declared_status=str(c.get('status') or '').upper()\n        publication=str(c.get('publication_status') or '').upper()\n        blocked=(publication in {'BLOCKED','SOFT_ONLY_NO_HARD_CLAIM'} or declared_status in {'BLOCKED','PROHIBITED','REJECTED','INVALID'})\n        numeric_authorized=(\n            grade in {'A','B'}\n            or declared_status in {'APPROVED','VERIFIED','ACTIVE'}\n            or publication in {'HARD_CLAIM_ALLOWED_WITH_SCOPE','BOUNDED_SUPPORTED_CLAIM'}\n        )\n        if cid and numeric_authorized and not blocked:\n            numeric_authority_by_id[cid]=c\n"""
if old not in text:
    raise SystemExit('listing numeric authority block not found')
text = text.replace(old, new, 1)
text = text.replace("c=approved_by_id.get(str(cid))", "c=numeric_authority_by_id.get(str(cid))")
listing.write_text(text, encoding='utf-8')

# 2) Compliance issues get a stable common shape; actionable asset-routing issues come first.
compliance = Path('runtime/cbcc/compliance.py')
ctext = compliance.read_text(encoding='utf-8')
pattern = re.compile(r"def compile_compliance\(.*", re.S)
replacement = '''def compile_compliance(product_truth:dict[str,Any], claims:list[dict[str,Any]], listing:dict[str,Any]|None, assets:list[dict[str,Any]]|None, platform_compile:dict[str,Any], research_gate:dict[str,Any]|None=None)->dict[str,Any]:
    claims=claims or []; assets=assets or []
    approved={
        c.get('claim_id') for c in claims
        if c.get('claim_id')
        and str(c.get('evidence_grade') or c.get('evidence_level') or '').upper() in {'A','B'}
        and str(c.get('publication_status') or '').upper() not in {'BLOCKED','SOFT_ONLY_NO_HARD_CLAIM'}
    }
    claim_issues=[]; asset_issues=[]; checks=[]

    def issue(*, scope, code, claim_ids=None, asset_id=None, severity='HOLD', details=None):
        row={
            'scope':scope,
            'asset_id':asset_id,
            'code':code,
            'claim_ids':list(claim_ids or []),
            'severity':severity,
        }
        if details:
            row['details']=details
        return row

    for c in claims:
        cid=c.get('claim_id')
        grade=str(c.get('evidence_grade') or c.get('evidence_level') or '').upper()
        declared_status=str(c.get('status') or '').upper()
        if cid and grade not in {'A','B','C'}:
            claim_issues.append(issue(scope=cid, code='CLAIM_EVIDENCE_GRADE_MISSING', claim_ids=[cid]))
        if cid and grade=='C' and declared_status in {'APPROVED','VERIFIED','ACTIVE'}:
            claim_issues.append(issue(scope=cid, code='C_GRADE_CANNOT_BE_HARD_APPROVED', claim_ids=[cid]))

    for a in assets:
        asset_id=a.get('asset_id')
        unknown=[x for x in a.get('claim_ids',[]) if x not in approved]
        if unknown:
            asset_issues.append(issue(scope=asset_id, asset_id=asset_id, code='UNAPPROVED_CLAIM_REFERENCE', claim_ids=unknown))
        checks.append({
            'asset_id':asset_id,
            'claim_ids':a.get('claim_ids',[]),
            'unapproved_claim_ids':unknown,
            'status':'PASS' if not unknown else 'HOLD',
        })

    # Asset-routing problems are first because they are directly actionable by callers.
    issues=asset_issues+claim_issues
    listing_status=(listing or {}).get('status') or ((listing or {}).get('compiled') or {}).get('status')
    research_rows=list((research_gate or {}).get('pending') or [])
    research_pending=bool(research_rows)
    research_blocking_pending=any(bool(row.get('blocking', True)) for row in research_rows)
    platform_ready=platform_compile.get('status') in {'VERIFIED_FOR_REQUEST','FAMILY_PLANNING_ONLY','PLANNING_ONLY_RESEARCH_PENDING'}
    return {
        'status':'HOLD' if issues or research_blocking_pending or not platform_ready else 'READY_REVIEW',
        'issues':issues,
        'claim_issues':claim_issues,
        'asset_issues':asset_issues,
        'asset_checks':checks,
        'listing_status':listing_status,
        'platform_status':platform_compile.get('status'),
        'research_pending':research_pending,
        'research_blocking_pending':research_blocking_pending,
        'issue_contract':{
            'required_keys':['scope','asset_id','code','claim_ids','severity'],
            'ordering':'ASSET_ROUTING_FIRST_THEN_CLAIM_LEDGER',
        },
        'layers':{'product':'SOURCE_BOUND','claim':'LEDGER_BOUND','creative':'ASSET_BOUND','platform':'CURRENT_EVIDENCE_BOUND'},
        'principle':'Compliance compiles evidence and current platform scope; it does not manufacture legal or regulatory approval.'
    }
'''
if not pattern.search(ctext):
    raise SystemExit('compile_compliance function not found')
ctext = pattern.sub(replacement, ctext, count=1)
compliance.write_text(ctext, encoding='utf-8')

# 3) Canonical Prompt explicitly binds the consumer decision question and Product Truth.
prompt = Path('runtime/cbcc/prompt_compiler.py')
ptext = prompt.read_text(encoding='utf-8')
cn_anchor = """            '【生成目标】',\n            f\"视觉任务：{_txt(_cn_phrase(card.get('visual_objective')))}\",\n"""
cn_new = """            '【生成目标】',\n            f\"视觉任务：{_txt(_cn_phrase(card.get('visual_objective')))}\",\n            f\"消费者问题：{_txt(_cn_phrase((card.get('commerce_task') or {}).get('consumer_question')))}\",\n            '真实产品 / Product Truth 绑定：商品身份、包装、材质、颜色、结构与可见事实只允许来自已验证商品真源及随任务提供的真实商品母版 / 参考图。',\n"""
if cn_anchor not in ptext:
    raise SystemExit('CN prompt objective anchor not found')
ptext = ptext.replace(cn_anchor, cn_new, 1)
en_anchor = """            '[RENDER OBJECTIVE]',\n            f\"Visual task: {_txt(card.get('visual_objective'))}\",\n"""
en_new = """            '[RENDER OBJECTIVE]',\n            f\"Visual task: {_txt(card.get('visual_objective'))}\",\n            f\"Consumer decision question: {_txt((card.get('commerce_task') or {}).get('consumer_question'))}\",\n            'Product Truth binding: product identity, packaging, material, color, geometry and visible facts must remain source-bound to verified Product Truth and the real-product references supplied with the task.',\n"""
if en_anchor not in ptext:
    raise SystemExit('EN prompt objective anchor not found')
ptext = ptext.replace(en_anchor, en_new, 1)
trace_anchor = """        {'strategy_parameter':'creative thesis / image language / creative anchor','render_location':'RENDER OBJECTIVE','value':card.get('creative_system')},\n"""
trace_new = trace_anchor + """        {'strategy_parameter':'consumer decision question / Product Truth execution binding','render_location':'RENDER OBJECTIVE / REAL PRODUCT IDENTITY','value':{'consumer_question':(card.get('commerce_task') or {}).get('consumer_question'),'product_truth_binding':'SOURCE_BOUND'}},\n"""
if trace_anchor not in ptext:
    raise SystemExit('parameter trace anchor not found')
ptext = ptext.replace(trace_anchor, trace_new, 1)
prompt.write_text(ptext, encoding='utf-8')

# Focused regression tests for the three real defects.
test = Path('tests/test_v0629_final_stabilization.py')
test.write_text("""from pathlib import Path
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
    assert '消费者问题' in cn and '真实产品' in cn and 'Product Truth' in cn
    assert 'Consumer decision question' in en and 'Product Truth binding' in en
    assert 'why should i trust this product?' in en_lower
    for forbidden in ['ast-secret','real-secret','secret product name']:
        assert forbidden not in en_lower
    assert any(row.get('strategy_parameter')=='consumer decision question / Product Truth execution binding' for row in bundle['parameter_trace'])
""", encoding='utf-8')

print('v0.6.29 final stabilization patch applied')
