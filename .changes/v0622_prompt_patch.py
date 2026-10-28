from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'missing prompt patch target: {label}')
    return text.replace(old, new, 1)

p=Path('runtime/cbcc/prompt_compiler.py')
text=p.read_text(encoding='utf-8')

# Generic relevance helpers: preserve numeric zero/False when they are actual values; drop only absent containers/text.
anchor="""def _merge(base: dict[str, Any] | None, override: dict[str, Any] | None) -> dict[str, Any]:
    out = dict(base or {})
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        elif v not in (None, '', [], {}):
            out[k] = v
    return out
"""
insert=anchor+"""

def _meaningful(value: Any) -> bool:
    if value in (None, ''):
        return False
    if isinstance(value, dict):
        return any(_meaningful(v) for v in value.values())
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_meaningful(v) for v in value)
    return True


def _compact(value: Any) -> Any:
    if isinstance(value, dict):
        out={}
        for k,v in value.items():
            cv=_compact(v)
            if _meaningful(cv): out[k]=cv
        return out
    if isinstance(value, list):
        return [cv for item in value if _meaningful(cv:=_compact(item))]
    return value
"""
text=replace_once(text,anchor,insert,'relevance helpers')

# Replace global photography inheritance with asset-relevance inheritance.
start=text.index('def _derived_photo_contract(')
end=text.index('\ndef _design_card(',start)
new_func='''def _derived_photo_contract(asset: dict[str, Any], strategy_authority: dict[str, Any] | None, explicit: dict[str, Any] | None) -> dict[str, Any]:
    """Project only photography/CMF decisions that are actually relevant to this asset.

    Global strategy can contain a photography toolbox, but that does not make every camera/light field mandatory
    for every asset. Asset reasoning and explicit execution contracts are authoritative; global defaults are
    inherited only for real repeatable photography or when the asset explicitly opts in.
    """
    explicit=dict(explicit or {})
    sections=(strategy_authority or {}).get('sections') or {}
    visual=sections.get('05_visual_photography_strategy') or {}
    reasoning=_asset_reasoning(strategy_authority,asset.get('asset_id'))
    capture_mode=str(explicit.get('capture_mode') or reasoning.get('capture_mode') or asset.get('capture_mode') or '').upper() or None
    inherit_global=bool(explicit.get('inherit_strategy_photography') or reasoning.get('inherit_strategy_photography') or capture_mode=='REAL_PHOTO')

    camera={}
    if inherit_global and isinstance(visual.get('camera'),dict): camera.update(visual.get('camera') or {})
    if inherit_global and isinstance(visual.get('lens'),dict):
        for k,v in (visual.get('lens') or {}).items(): camera.setdefault(k,v)
    if isinstance(reasoning.get('camera_choice'),dict): camera.update(reasoning.get('camera_choice') or {})
    if isinstance(explicit.get('camera'),dict): camera.update(explicit.get('camera') or {})

    material=reasoning.get('material_lighting_profile') or {}
    lighting={}
    if inherit_global and isinstance(visual.get('lighting_framework'),dict): lighting.update(visual.get('lighting_framework') or {})
    if isinstance(reasoning.get('lighting_choice'),dict): lighting.update(reasoning.get('lighting_choice') or {})
    if isinstance(explicit.get('lighting'),dict): lighting.update(explicit.get('lighting') or {})
    shot=reasoning.get('shot_lighting_reasoning') or {}
    if material and (inherit_global or reasoning):
        for k in ['prelight_plan','lighting_diagram','exposure_ratio_plan','polarization_plan','color_consistency_plan']:
            if material.get(k) not in (None,'',[],{}): lighting.setdefault(k,material.get(k))
    if shot:
        if shot.get('material_response_to_show') not in (None,'',[],{}): lighting.setdefault('material_response_to_show',shot.get('material_response_to_show'))
        if shot.get('highlight_reflection_why') not in (None,'',[],{}): lighting.setdefault('reflection_reasoning',shot.get('highlight_reflection_why'))
        if shot.get('color_management_why') not in (None,'',[],{}): lighting.setdefault('color_management_reasoning',shot.get('color_management_why'))

    cmf=reasoning.get('cmf_choice') or explicit.get('cmf') or {}
    if inherit_global and not cmf:
        cmf=visual.get('cmf') or visual.get('palette_hex') or {}
    if isinstance(cmf,list): cmf={'palette_hex':cmf}
    if cmf and not isinstance(cmf,dict): cmf={'description':cmf}
    if isinstance(cmf,dict) and cmf:
        cmf=_merge({
            'material':material.get('material'),'finish':material.get('finish'),'surface_behavior':material.get('surface_behavior'),
            'optical_risks':material.get('optical_risks'),
        },cmf)

    color_management=explicit.get('color_management')
    if not color_management and reasoning.get('color_management'):
        color_management=reasoning.get('color_management')
    if not color_management and inherit_global:
        color_management=visual.get('color_management') or material.get('color_consistency_plan')

    inclusive=explicit.get('inclusive_photography') or reasoning.get('inclusive_photography') or {}
    if inherit_global and not inclusive: inclusive=visual.get('inclusive_photography') or {}
    repeatable=bool(explicit.get('repeatable_capture') or reasoning.get('repeatable_capture'))
    prelight_required=bool(explicit.get('prelight_required')) if 'prelight_required' in explicit else bool(capture_mode=='REAL_PHOTO' and (repeatable or lighting.get('prelight_plan')))

    base={
        'status':'ASSET_RELEVANCE_DERIVED_EXECUTION_CONTRACT',
        'capture_mode':capture_mode,
        'camera':camera,
        'composition':explicit.get('composition') or reasoning.get('composition_execution') or {},
        'lighting':lighting,
        'cmf':cmf,
        'color_management':color_management,
        'inclusive_photography':inclusive,
        'asset_reasoning':reasoning,
        'prelight_required':prelight_required,
        'repeatable_capture':repeatable,
    }
    # Remaining explicit keys are allowed to extend the asset contract; absent global toolbox fields are not invented.
    return _compact(_merge(base,explicit))
'''
text=text[:start]+new_func+text[end:]

# Compact Design Card so absent camera/light fields do not become fake downstream obligations.
needle="""    return {
        'asset_id': asset.get('asset_id'), 'asset_name': asset.get('asset_name'), 'asset_type': asset.get('asset_type'),
"""
replacement="""    return _compact({
        'asset_id': asset.get('asset_id'), 'asset_name': asset.get('asset_name'), 'asset_type': asset.get('asset_type'),
"""
text=replace_once(text,needle,replacement,'compact design card start')
text=replace_once(text,"""        'editable_layer_contract': asset.get('editable_layer_contract') or {},
    }


def _render_safe_text""","""        'editable_layer_contract': asset.get('editable_layer_contract') or {},
    })


def _render_safe_text""",'compact design card end')

# Section-level relevance filter. Static explanatory prose cannot keep an irrelevant photography section alive.
clean_anchor="""def _clean_render_lines(lines:list[str])->list[str]:
    out=[]
    for x in lines:
        if x is None: continue
        text=str(x)
        stripped=text.strip()
        if not stripped: out.append(''); continue
        # Remove parameter rows that contain no actual value (e.g. \"Shutter / ISO: / \ ").
        for sep in (':','：'):
            if sep in text and not stripped.startswith('[') and not stripped.startswith('【'):
                tail=text.split(sep,1)[1].replace('/','').strip()
                if not tail:
                    text=''; break
        if text: out.append(text)
    # collapse duplicate blank lines
    compact=[]
    for x in out:
        if x=='' and compact and compact[-1]=='': continue
        compact.append(x)
    return compact
"""
filter_code=clean_anchor+"""

def _prompt_section_relevance(card:dict[str,Any])->dict[str,bool]:
    cam=card.get('composition_camera') or {}; photo=card.get('photography_execution') or {}
    lm=dict(card.get('lighting_material_cmf') or {}); lm.pop('material_truth_rule',None)
    inc=card.get('inclusive_photography') or {}; surface=card.get('surface_contract') or {}; info=card.get('information_design') or {}
    boundaries=bool(card.get('approved_visual_elements') or card.get('precision_boundaries') or card.get('editable_layer_contract'))
    return {
        'composition':_meaningful(cam) or _meaningful(photo.get('composition')) or _meaningful(photo.get('capture_mode')),
        'lighting':_meaningful(lm) or _meaningful(photo.get('color_management')),
        'inclusive':_meaningful(inc),
        'surface':_meaningful(surface) or _meaningful(info.get('copy_budget')) or _meaningful(info.get('typography')),
        'boundaries':boundaries,
    }


def _filter_relevant_prompt_sections(lines:list[str],card:dict[str,Any],cn:bool)->list[str]:
    relevance=_prompt_section_relevance(card)
    active_titles={
        ('【构图与摄影机】' if cn else '[COMPOSITION / CAMERA]'):relevance['composition'],
        ('【灯光 / 材质 / CMF】' if cn else '[LIGHTING / MATERIAL / CMF]'):relevance['lighting'],
        ('【包容性人物摄影】' if cn else '[INCLUSIVE HUMAN PHOTOGRAPHY]'):relevance['inclusive'],
        ('【Surface / 信息设计】' if cn else '[SURFACE / INFORMATION DESIGN]'):relevance['surface'],
        ('【视觉执行边界 / 可编辑性】' if cn else '[VISUAL EXECUTION BOUNDARIES / EDITABILITY]'):relevance['boundaries'],
    }
    out=[]; keep=True
    for row in lines:
        s=str(row or '').strip()
        if s in active_titles:
            keep=active_titles[s]
            if keep: out.append(row)
            continue
        if (cn and s.startswith('【') and s.endswith('】')) or ((not cn) and s.startswith('[') and s.endswith(']')):
            keep=True
        if keep: out.append(row)
    return out
"""
text=replace_once(text,clean_anchor,filter_code,'section relevance filter')

# Do not invent human/casting constraints when no people are part of this asset.
text=text.replace("f\"人物与选角：{_txt(_cn_phrase(sae.get('human_context')),'仅在画面任务需要时出现人物；人物服务真实使用/决策任务，不把族裔、性别、年龄等身份直接推断为行为。')}\"", "f\"人物与选角：{_txt(_cn_phrase(sae.get('human_context')))}\"")
text=text.replace("f\"Human / casting: {_txt(sae.get('human_context'),'Include people only when the visual task requires them.')}\"", "f\"Human / casting: {_txt(sae.get('human_context'))}\"")

# Replace universal CN photography boilerplate with actual asset execution values.
text=text.replace("f\"光比：{_txt(_cn_phrase(lm.get('exposure_ratio_plan')))}\", f\"反射与偏振：{polarization}\",\n            f\"Prelight：{prelight}\",", "f\"光比：{_txt(_cn_phrase(lm.get('exposure_ratio_plan')))}\", f\"反射与偏振：{_txt(_cn_phrase(lm.get('reflection')))} / {_txt(_cn_phrase(lm.get('polarization_plan')))}\",\n            f\"Prelight：{_txt(_cn_phrase(lm.get('prelight_plan')))}\",")
text=text.replace("f\"颜色一致性：{color_consistency}\", '材质真实性边界", "f\"颜色一致性：{_txt(_cn_phrase(lm.get('color_consistency_plan')))}\", '材质真实性边界")

# Section filter applies after language-specific construction and before empty-row cleanup.
text=replace_once(
    text,
    "    return _clean_render_lines([x for x in lines if x is not None and str(x).strip() != 'None'])\n\n\ndef _parameter_trace",
    "    lines=_filter_relevant_prompt_sections(lines,card,cn)\n    return _clean_render_lines([x for x in lines if x is not None and str(x).strip() != 'None'])\n\n\ndef _parameter_trace",
    'apply relevant section filter',
)

# Parameter trace only contains dimensions that actually exist.
trace_start=text.index('def _parameter_trace(card: dict[str, Any]) -> list[dict[str, Any]]:\n')
trace_end=text.index('\ndef compile_asset_prompt(',trace_start)
new_trace='''def _parameter_trace(card: dict[str, Any]) -> list[dict[str, Any]]:
    rows=[
        {'strategy_parameter':'creative thesis / image language / creative anchor','render_location':'RENDER OBJECTIVE','value':card.get('creative_system')},
        {'strategy_parameter':'composition / camera / lens / focus / exposure settings','render_location':'COMPOSITION / CAMERA','value':card.get('composition_camera')},
        {'strategy_parameter':'capture mode / product occupancy / negative space / output color management','render_location':'PHOTOGRAPHY EXECUTION CONTRACT','value':card.get('photography_execution')},
        {'strategy_parameter':'lighting / CCT / ratio / prelight / polarization / CMF / material response / color management','render_location':'LIGHTING / MATERIAL / CMF','value':{k:v for k,v in (card.get('lighting_material_cmf') or {}).items() if k!='material_truth_rule'}},
        {'strategy_parameter':'skin-tone exposure / hair / wardrobe / intersectionality','render_location':'INCLUSIVE HUMAN PHOTOGRAPHY','value':card.get('inclusive_photography')},
        {'strategy_parameter':'surface / safe zone / copy budget / typography','render_location':'SURFACE / INFORMATION DESIGN','value':{'surface':card.get('surface_contract'),'information_design':card.get('information_design')}},
        {'strategy_parameter':'approved visual elements / precision boundaries / editable & frozen layers','render_location':'VISUAL EXECUTION BOUNDARIES / EDITABILITY','value':{'approved_visual_elements':card.get('approved_visual_elements'),'precision_boundaries':card.get('precision_boundaries'),'editable_layer_contract':card.get('editable_layer_contract')}},
        {'strategy_parameter':'product fidelity / real masters','render_location':'REAL PRODUCT IDENTITY','value':card.get('product_identity')},
    ]
    return [_compact(row) for row in rows if _meaningful(row.get('value'))]


def _renderer_layer_plan(card:dict[str,Any],locked_copy:dict[str,Any])->list[str]:
    layers=[]
    subject=card.get('subject_action_environment_props') or {}
    presence=card.get('product_presence') or {}
    if _meaningful(subject.get('environment')): layers.append('background_environment')
    if _meaningful(subject.get('human_context')): layers.append('human_or_context_if_required')
    if str(presence.get('planning_state') or '').upper()!='FORBIDDEN' or _meaningful(card.get('product_identity')): layers.append('product_master_or_verified_product')
    if _meaningful((card.get('information_design') or {}).get('proof_plane')): layers.append('evidence_graphics')
    if locked_copy: layers.append('locked_typography')
    if _meaningful((card.get('photography_execution') or {}).get('color_management')) or _meaningful((card.get('lighting_material_cmf') or {}).get('post_implications')): layers.append('final_color_grade')
    return list(dict.fromkeys(layers))


def _dynamic_photography_checks(card:dict[str,Any])->list[str]:
    relevance=_prompt_section_relevance(card); checks=[]
    if relevance['composition']: checks.append('selected composition/perspective contract is visible')
    if relevance['lighting']: checks.append('selected lighting/material/CMF and color-management decisions match the asset contract')
    if relevance['inclusive']: checks.append('human exposure/representation constraints are applied when people appear')
    if _meaningful((card.get('lighting_material_cmf') or {}).get('material_truth_rule')): checks.append('no unsupported physical/material effects')
    return checks
'''
text=text[:trace_start]+new_trace+text[trace_end:]

# Compact machine contract, make renderer layers and QA checks task-derived.
text=replace_once(text,"""    machine = {
        'asset_id': card['asset_id'], 'surface': card['surface'], 'production_mode': asset.get('production_mode'),
""","""    machine = _compact({
        'asset_id': card.get('asset_id'), 'surface': card.get('surface'), 'production_mode': asset.get('production_mode'),
""",'machine compact start')
text=replace_once(text,"""        'approved_visual_elements': card.get('approved_visual_elements')
    }
""","""        'approved_visual_elements': card.get('approved_visual_elements')
    })
""",'machine compact end')
text=replace_once(text,"""        'layer_plan': ['background_environment', 'human_or_context_if_required', 'product_master_or_verified_product', 'evidence_graphics', 'locked_typography', 'final_color_grade'],
""","""        'layer_plan': _renderer_layer_plan(card,locked_copy),
""",'dynamic layer plan')
text=replace_once(text,"""        'parameter_trace_complete': True,
""","""        'relevant_parameter_trace_complete': True,
""",'relevant trace flag')
text=replace_once(text,"""        'photography_checks': ['camera/lens intent visible', 'lighting/material response matches contract', 'CCT/color consistency preserved', 'skin-tone exposure applied when people appear', 'no unsupported physical effects']
""","""        'photography_checks': _dynamic_photography_checks(card)
""",'dynamic QA checks')
text=text.replace("'status': 'CANONICAL_PROMPT_COMPILED_V066'","'status': 'CANONICAL_PROMPT_COMPILED_V0622_RELEVANCE_DRIVEN'")

p.write_text(text,encoding='utf-8')
