from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project
from cbcc.state import ProjectState

def test_kiyuu_my_tiktok_planning_e2e(tmp_path):
    fx=ROOT/'tests/fixtures/kiyuu_my_tiktok'; req=json.loads((fx/'request.json').read_text(encoding='utf-8'))
    out=build_project(tmp_path/'proj',req,fx)
    assert out['gates']['PRODUCT_TRUTH']['status']=='READY_REVIEW'
    assert out['gates']['PLATFORM_COMPILE']['status']=='READY_REVIEW'
    cg=json.loads((tmp_path/'proj/artifacts/content_graph.json').read_text(encoding='utf-8'))
    families={o['family'] for o in cg['objects']}
    assert {'LISTING','VISUAL','VIDEO','CREATOR_AFFILIATE','PAID','CX'}.issubset(families)
    target=json.loads((tmp_path/'proj/artifacts/target_context.json').read_text(encoding='utf-8'))
    assert target['language']['primary_locale']=='en-MY' and 'ms-MY' in target['language']['support_locales']
    assert target['language']['prompt_instruction_locale']=='zh-CN'
    # Build never silently locks authority.
    assert all(v['status']!='LOCKED' for v in out['gates'].values())
    # revision is dependency-exact
    st=ProjectState.load(tmp_path/'proj'); affected=st.revise(['PRODUCT_TRUTH'])
    assert 'PRODUCT_TRUTH' in affected and 'COMMERCE_ENTITY' in affected and 'TARGET_CONTEXT' in affected
