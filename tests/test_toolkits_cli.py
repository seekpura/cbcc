from pathlib import Path
import sys,json,runpy,io,contextlib
ROOT=Path(__file__).resolve().parents[1]

def run_cli(script,payload,tmp_path):
    f=tmp_path/'d.json'; f.write_text(json.dumps(payload),encoding='utf-8')
    old=sys.argv[:]; out=io.StringIO(); err=io.StringIO(); sys.argv=[str(ROOT/script),str(f)]
    try:
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                runpy.run_path(str(ROOT/script),run_name='__main__')
        except SystemExit as e:
            assert e.code in (0,None),(script,e.code,out.getvalue(),err.getvalue())
    finally:
        sys.argv=old
    return out.getvalue()

def test_truth_toolkit_standalone(tmp_path):
    payload={'sources':[{'source_id':'S1','kind':'USER_PROVIDED_FACT'}],'claims':[{'claim_id':'C1','status':'APPROVED','evidence_source_ids':['S1']}]}
    for script in ['toolkits/00_truth_claim/validate_sources.py','toolkits/00_truth_claim/validate_claims.py']:
        out=run_cli(script,payload,tmp_path)
        assert '"pass": true' in out.lower()
