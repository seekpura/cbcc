from pathlib import Path
import sys,random
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.tools.ads import analyze_ads
from cbcc.tools.feedback import analyze_feedback
from cbcc.tools.listing import compile_listing, keyword_architecture


def test_listing_keyword_stress_5000_rows_is_deterministic():
    rows=[{'term':f'keyword-{i}','cluster':['CORE','FEATURE','SCENE','AUDIENCE','RISK'][i%5],'volume':10000-i,'competition':i%37,'source_id':f'S{i%11}'} for i in range(5000)]
    a=keyword_architecture(rows); b=keyword_architecture(rows)
    assert a==b and sum(len(v) for v in a['clusters'].values())==5000 and a['unclassified_count']==0
    fields={'title':'Verified Product 500 ml','bullets':['500 ml verified capacity'],'_source_refs':{'title':['SRC-1'],'bullets':['SRC-1']}}
    out=compile_listing(fields,{'capacity':'500 ml'},[],{'title':{'required':True,'max_chars':75}}, {'visible_copy_locales':['en-US']}, rows)
    assert out['pass'] and sum(len(v) for v in out['keywords']['clusters'].values())==5000


def test_feedback_stress_10000_classified_rows_routes_without_semantic_reclassification():
    cats=['MISUNDERSTANDING','PRODUCT_DEFECT','PACKAGE_CONFUSION','USAGE_DIFFICULTY','LOGISTICS']
    rows=[{'category':cats[i%len(cats)],'severity':['LOW','MEDIUM','HIGH'][i%3],'text':f'feedback {i}'} for i in range(10000)]
    out=analyze_feedback(rows)
    assert out['summary']['total']==10000 and out['unclassified_count']==0 and len(out['issues'])==5
    mis=next(x for x in out['issues'] if x['category']=='MISUNDERSTANDING')
    assert 'LISTING' in mis['routes'] and len(mis['examples'])==3


def test_ads_portfolio_like_stress_2000_campaigns_has_no_hidden_benchmark():
    # Each row is independently diagnosed from caller thresholds/economics; no industry CTR/CVR is invented.
    for i in range(2000):
        imp=1000+i; clicks=10+(i%30); orders=1+(i%8); spend=20+(i%40); revenue=80+(i%150)
        out=analyze_ads({'impressions':imp,'clicks':clicks,'orders':orders,'spend':spend,'revenue':revenue},price=50,costs={'landed_cost':10,'platform_fee':5,'fulfillment':5,'affiliate_commission':0,'tax':0,'refund_allowance':2},thresholds={'min_ctr':0.005})
        assert out['status']=='CALCULATED_FROM_INPUTS' and out['thresholds_used']['min_ctr']==0.005
        assert out['economics']['break_even_roas'] is not None
