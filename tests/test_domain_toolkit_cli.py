from pathlib import Path
import sys,json,runpy,io,contextlib
ROOT=Path(__file__).resolve().parents[1]

def run(script,payload,tmp_path):
    p=tmp_path/'in.json'; p.write_text(json.dumps(payload),encoding='utf-8')
    old=sys.argv[:]; out=io.StringIO(); err=io.StringIO()
    sys.argv=[str(ROOT/script),str(p)]
    try:
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                runpy.run_path(str(ROOT/script),run_name='__main__')
        except SystemExit as e:
            assert e.code in (0,None),(script,e.code,out.getvalue(),err.getvalue())
    finally:
        sys.argv=old
    return json.loads(out.getvalue())

def test_market_cli(tmp_path):
    o=run('toolkits/01_market/market_metrics.py',{'rows':[{'seller':'A','price':10,'units':2,'revenue':20,'configuration':'x'}]},tmp_path); assert o['row_count']==1

def test_econ_cli(tmp_path):
    o=run('toolkits/02_pricing_economics/unit_economics.py',{'price':100,'costs':{'landed_cost':20,'platform_fee':10,'fulfillment':5,'affiliate_commission':0,'ad_cost':10,'tax':0,'refund_allowance':2}},tmp_path); assert o['contribution']==53

def test_ads_feedback_experiment_cli(tmp_path):
    a=run('toolkits/06_ads/ad_economics.py',{'ad_data':{'impressions':100,'clicks':5,'orders':1,'spend':5,'revenue':20}},tmp_path); assert a['metrics']['ctr']==0.05
    f=run('toolkits/07_feedback/feedback_stats.py',{'rows':[{'category':'MISUNDERSTANDING'}]},tmp_path); assert f['issues'][0]['category']=='MISUNDERSTANDING'
    e=run('toolkits/08_experiment/experiment_metrics.py',{'control_success':10,'control_total':100,'test_success':20,'test_total':100},tmp_path); assert 'p_value_two_sided' in e
