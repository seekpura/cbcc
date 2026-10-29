#!/usr/bin/env python3
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'tests/test_v0632_production_parameter_closure.py'
s=p.read_text(encoding='utf-8')
old="""    out=_compile(asset)\n    assert out['model_prompt_status']=='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'\n    closure=out['production_parameter_closure']\n    assert closure['route']['photographic'] is False\n"""
new="""    out=_compile(asset)\n    closure=out['production_parameter_closure']\n    assert out['model_prompt_status']=='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED', closure\n    assert closure['route']['photographic'] is False\n"""
if old not in s:
    raise SystemExit('graphic assertion anchor not found')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('graphic diagnostic assertion enabled')
