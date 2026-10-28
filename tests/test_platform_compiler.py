from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.platform import PlatformCompiler

def test_unknown_site_yields_research_action(tmp_path):
    c=PlatformCompiler(tmp_path)
    out=c.compile({'platform_family':'unknown','site':'XX'},['CURRENT_RULE'])
    assert out['status']=='RESEARCH_REQUIRED' and out['research_actions']

def test_synthetic_fixture_is_explicit():
    p=ROOT/'tests/fixtures/kiyuu_my_tiktok'; c=PlatformCompiler(p)
    out=c.compile({'platform_family':'tiktok_shop','site':'MY','program':'cross_border'},['TEST-LANGUAGE-CONTRACT'])
    assert out['status']=='VERIFIED_FOR_REQUEST' and out['synthetic_for_test'] is True
