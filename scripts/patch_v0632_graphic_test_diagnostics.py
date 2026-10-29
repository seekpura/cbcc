#!/usr/bin/env python3
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'tests/test_v0632_production_parameter_closure.py'
s=p.read_text(encoding='utf-8')
old="""    out=_compile(asset)\n    assert out['model_prompt_status']=='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'\n    closure=out['production_parameter_closure']\n    assert closure['route']['photographic'] is False\n"""
new="""    out=_compile(asset)\n    closure=out['production_parameter_closure']\n    diag=(closure['route'], closure['required_groups'], closure['missing_required_parameters'], closure['english_render_semantics_missing_for'])\n    assert out['model_prompt_status']=='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED', diag\n    assert closure['route']['photographic'] is False\n"""
if old in s:
    s=s.replace(old,new,1)
else:
    old2="""    out=_compile(asset)\n    closure=out['production_parameter_closure']\n    assert out['model_prompt_status']=='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED', closure\n    assert closure['route']['photographic'] is False\n"""
    if old2 not in s:
        raise SystemExit('graphic assertion anchor not found')
    s=s.replace(old2,new,1)
p.write_text(s,encoding='utf-8')
print('concise graphic diagnostic assertion enabled')
