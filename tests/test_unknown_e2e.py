from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project

def test_unknown_platform_holds_submission_but_strategy_continues(tmp_path):
    req={'project_id':'UNKNOWN-E2E','product':{'name':'Test Product'},'sources':[{'source_id':'S1','kind':'USER_PROVIDED_FACT'}],
         'target':{'market':'Unknown','platform_family':'nonexistent_platform','site':'ZZ','primary_locale':'en-US','currency':'USD'},
         'content_families':['LISTING','VISUAL']}
    out=build_project(tmp_path/'p',req,ROOT/'platform_packs')
    assert out['gates']['PLATFORM_COMPILE']['status']=='HOLD'
    assert out['gates']['CONTENT_GRAPH']['status']=='READY_REVIEW'
    assert out['gates']['STRATEGY_AUTHORITY']['status']=='READY_REVIEW'
    assert out['pending_actions'] and out['pending_actions'][0]['status']=='PENDING'
