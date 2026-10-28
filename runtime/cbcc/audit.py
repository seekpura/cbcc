from __future__ import annotations
from pathlib import Path
import subprocess, sys, re, yaml, json, os, io, contextlib

NEG=re.compile(r"\b(?:do not|don't|never|must not|forbid|prohibit|banned?)\b|禁止|不要|不得|严禁",re.I)
POS=re.compile(r"\b(?:create|build|use|prefer|define|select|express|show|preserve|deliver|recommend|focus|support|prioritize|design)\b|优先|采用|使用|表达|呈现|建立|输出|保留",re.I)

def _capability_check(root:Path):
    ledger=yaml.safe_load((root/'references/capability_ledger.yaml').read_text(encoding='utf-8'))
    errors=[]; counts={}
    for cap in ledger.get('capabilities',[]):
        if not cap.get('required'): continue
        cid=cap.get('id'); maturity=cap.get('maturity','UNKNOWN'); counts[maturity]=counts.get(maturity,0)+1
        for field in ['implementation_paths','trigger_examples','runtime_consumers','behavior_test','e2e_evidence','maturity']:
            if not cap.get(field): errors.append(f'{cid}: missing {field}')
        for rel in (cap.get('implementation_paths') or [])+(cap.get('runtime_consumers') or []):
            if not (root/rel).exists(): errors.append(f'{cid}: missing path {rel}')
        for rel in [cap.get('behavior_test'),cap.get('e2e_evidence')]:
            if rel and not (root/rel).exists(): errors.append(f'{cid}: missing evidence {rel}')
    return {'name':'capability_ledger','pass':not errors,'required_count':sum(counts.values()),'maturity_counts':counts,'errors':errors}

def _platform_check(root:Path):
    d=yaml.safe_load((root/'references/platforms/platform_registry.yaml').read_text(encoding='utf-8')); errors=[]; exact=[]
    for k,v in d.get('platforms',{}).items():
        if not v.get('capabilities'): errors.append(f'{k}: no capabilities')
        if v.get('rules_status') not in {'VERIFIED','VERIFIED_SITE_GENERIC','REVERIFY_REQUIRED'}: errors.append(f'{k}: bad rules_status')
    for p in sorted((root/'platform_packs').glob('*.yaml')):
        x=yaml.safe_load(p.read_text(encoding='utf-8')) or {}
        if x.get('site') in {None,'*'} or x.get('synthetic_for_test'): continue
        exact.append(x.get('pack_id'))
        if not x.get('source_records'): errors.append(f'{p.name}: exact pack missing source_records')
        atoms=x.get('rule_atoms',[]) or []
        if not atoms: errors.append(f'{p.name}: exact pack missing rule_atoms')
        for a in atoms:
            if a.get('authority')!='OFFICIAL': errors.append(f"{p.name}:{a.get('rule_id')}: exact rule not OFFICIAL")
            if not a.get('source_url') or not a.get('verified_at') or not a.get('expires_at'): errors.append(f"{p.name}:{a.get('rule_id')}: incomplete freshness/source")
    return {'name':'platform_registry','pass':not errors,'errors':errors,'exact_packs':exact}

def _positive_first_check(root:Path):
    findings=[]
    for p in sorted((root/'skills').glob('*/SKILL.md')):
        t=p.read_text(encoding='utf-8'); n=len(NEG.findall(t)); q=len(POS.findall(t)); ratio=n/max(q,1)
        if n>=6 and ratio>0.60: findings.append({'file':str(p.relative_to(root)),'negative':n,'positive':q,'ratio':round(ratio,3)})
    return {'name':'positive_first','pass':not findings,'findings':findings,'policy':'positive-first; necessary precision boundaries remain allowed'}

def _pytest_check(root:Path, timeout=120):
    # Run pytest in-process in the fresh audit CLI process. This avoids platform-specific
    # subprocess pipe/process-tree hangs while still executing the real behavior suite.
    try:
        import pytest
        out=io.StringIO(); err=io.StringIO(); old=os.getcwd(); old_plugins=os.environ.get('PYTEST_DISABLE_PLUGIN_AUTOLOAD')
        os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
        os.chdir(root)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code=pytest.main(['-q'])
        finally:
            os.chdir(old)
            if old_plugins is None: os.environ.pop('PYTEST_DISABLE_PLUGIN_AUTOLOAD',None)
            else: os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']=old_plugins
        return {'name':'pytest','pass':code==0,'code':int(code),'stdout':out.getvalue()[-12000:],'stderr':err.getvalue()[-12000:],'runner':'in_process_pytest'}
    except Exception as e:
        return {'name':'pytest','pass':False,'code':2,'stdout':'','stderr':f'{type(e).__name__}: {e}','runner':'in_process_pytest'}

def machine_audit(root:Path,include_pytest=True):
    root=Path(root).resolve()
    checks=[_capability_check(root),_platform_check(root),_positive_first_check(root)]
    if include_pytest: checks.append(_pytest_check(root))
    ok=all(c.get('pass') for c in checks)
    return {
        'pass':ok,
        'checks':checks,
        'audit_semantics':'in-process structural gates + executable behavioral pytest',
        'toolkit_cli_coverage':'pytest includes tests/test_domain_toolkit_cli.py and tests/test_toolkits_cli.py; release certification also runs tests/run_toolkit_smoke.py separately',
        'note':'PASS proves configured code/tests passed in this package. It does not prove marketplace approval, legal approval, native-language editorial quality, visual taste, or conversion lift.'
    }
