from pathlib import Path

# Shared presence semantics: an explicitly supplied empty mapping means "use defaults", not "not requested".
p=Path('runtime/cbcc/scope_readiness.py')
s=p.read_text(encoding='utf-8')
anchor="""ASSET_FAMILIES={'VISUAL','RICH_CONTENT','VIDEO','CREATOR_AFFILIATE','LIVE','PAID','SOCIAL','STORE','CX','LIFECYCLE'}


def _strings(value: Any) -> list[str]:
"""
insert="""ASSET_FAMILIES={'VISUAL','RICH_CONTENT','VIDEO','CREATOR_AFFILIATE','LIVE','PAID','SOCIAL','STORE','CX','LIFECYCLE'}


def request_intent_present(request: Mapping[str,Any], key: str) -> bool:
    \"\"\"Presence-based request intent; an empty dict/list may intentionally mean 'use defaults'.\"\"\"
    return key in request and request.get(key) is not None and request.get(key) is not False


def _strings(value: Any) -> list[str]:
"""
if anchor not in s: raise SystemExit('scope readiness helper anchor missing')
s=s.replace(anchor,insert,1)
s=s.replace("production_intent=bool(request.get('compile_assets') or request.get('production_run'))","production_intent=bool(request.get('compile_assets')) or request_intent_present(request,'production_run')",1)
s=s.replace("production=bool(request.get('production_run'))","production=request_intent_present(request,'production_run')",1)
p.write_text(s,encoding='utf-8')

p=Path('runtime/cbcc/decision_authority.py')
s=p.read_text(encoding='utf-8')
if 'from .scope_readiness import request_intent_present' not in s:
    s=s.replace('from typing import Any, Mapping\n','from typing import Any, Mapping\n\nfrom .scope_readiness import request_intent_present\n',1)
s=s.replace("or request.get('production_run')\n    )","or request_intent_present(request,'production_run')\n    )",1)
s=s.replace("if (request.get('compile_assets') or request.get('production_run')) and authored_questions:","if (request.get('compile_assets') or request_intent_present(request,'production_run')) and authored_questions:",1)
p.write_text(s,encoding='utf-8')

p=Path('runtime/cbcc/agent_autonomy.py')
s=p.read_text(encoding='utf-8')
if 'from .scope_readiness import request_intent_present' not in s:
    s=s.replace('from .models import stable_hash\n','from .models import stable_hash\nfrom .scope_readiness import request_intent_present\n',1)
# The v0.6.28 override is the last occurrence and is what callers resolve.
s=s.replace("requested_production=bool(request.get('production_run'))\n    production_status=str(production_run.get('status') or 'NOT_REQUESTED').upper()","requested_production=request_intent_present(request,'production_run')\n    production_status=str(production_run.get('status') or 'NOT_REQUESTED').upper()",1)
p.write_text(s,encoding='utf-8')

p=Path('runtime/cbcc/compiler.py')
s=p.read_text(encoding='utf-8')
s=s.replace('from .scope_readiness import compile_required_content_families, compile_gate_scope','from .scope_readiness import compile_required_content_families, compile_gate_scope, request_intent_present',1)
s=s.replace("if request.get('production_run') and request.get('compile_assets') and asset_compile.get('status')=='COMPILED':","if request_intent_present(request,'production_run') and request.get('compile_assets') and asset_compile.get('status')=='COMPILED':",1)
s=s.replace("_capability_row('PROVIDER_PRODUCTION',bool(request.get('production_run')),production_run.get('status')","_capability_row('PROVIDER_PRODUCTION',request_intent_present(request,'production_run'),production_run.get('status')",1)
s=s.replace("(not request.get('production_run')) or bool(production_run.get('provider_jobs'))","(not request_intent_present(request,'production_run')) or bool(production_run.get('provider_jobs'))",1)
p.write_text(s,encoding='utf-8')

# Lock this boundary in the v0.6.28 tests.
p=Path('tests/test_v0628_agent_frontier_scope.py')
s=p.read_text(encoding='utf-8')
if 'test_empty_production_config_still_counts_as_explicit_production_intent' not in s:
    s += """

def test_empty_production_config_still_counts_as_explicit_production_intent():
    out=compile_agent_next_action({},request={'production_run':{}},production_run={'status':'PENDING'},gate_scope=_gate_scope('PRODUCTION'),content_requiredness={})
    assert out['status']=='ACTION_FRONTIER_OPEN'
    assert out['blocking_frontier'][0]['action']=='PRODUCE_RESUME_OR_REPAIR'
"""
p.write_text(s,encoding='utf-8')
print('v0.6.28 explicit empty production intent repaired')
