#!/usr/bin/env python3
from pathlib import Path

p=Path(__file__).resolve().parents[1]/'tests/test_v0631_model_native_prompt_contract.py'
s=p.read_text(encoding='utf-8')
old="""            'camera_or_view':'eye-level front / subtle 5-degree three-quarter view','focal_length_mm':'85mm full-frame equivalent',\n            'focus_dof':'label plane sharp; moderate depth of field',\n            'lighting':{'key':'large soft key 45 degrees front-side-above','fill':'white bounce','negative_fill':'narrow negative fill','cct':'5000K','exposure_ratio_plan':'2:1'},\n"""
new="""            'camera_or_view':'eye-level front / subtle 5-degree three-quarter view','focal_length_mm':'85mm full-frame equivalent',\n            'lens_family':'short telephoto product lens','working_distance':'1.0 m','camera_height':'8 cm above product-center height',\n            'yaw_pitch_roll':{'yaw':'5 degrees','pitch':'-2 degrees','roll':'0 degrees'},'shot_size':'tight product portrait',\n            'focus_plane':'front label plane','focus_dof':'f/8-equivalent label-sharp moderate depth of field',\n            'lighting':{'key':'large 100 cm soft key 45 degrees front-side-above at 1.0 m','fill':'white bounce at half-key intensity','negative_fill':'narrow negative fill camera-right','cct':'5000K','white_balance':'5000K neutral WB','exposure_ratio_plan':'2:1','shadow_policy':'soft restrained contact shadow','highlight_policy':'protect white-pack highlights below clipping'},\n            'prelight':'test frame to tune label highlight and pump reflection','color_management':'sRGB with neutral product-white match',\n"""
if old not in s:
    raise SystemExit('fixture anchor not found')
s=s.replace(old,new,1)
s=s.replace("assert out['model_prompt_status']=='MODEL_NATIVE_PROMPT_READY'","assert out['model_prompt_status']=='MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'",1)
p.write_text(s,encoding='utf-8')
print('upgraded v0.6.31 fixture for v0.6.32 closure')
