from pathlib import Path

P = Path('runtime/cbcc/prompt_compiler.py')
text = P.read_text(encoding='utf-8')

needle = """def _asset_reasoning(strategy_authority: dict[str, Any] | None, asset_id: str | None) -> dict[str, Any]:
    sections = (strategy_authority or {}).get('sections') or {}
    visual = sections.get('05_visual_photography_strategy') or {}
    return next((r for r in (visual.get('asset_parameter_reasoning') or []) if r.get('asset_id') == asset_id), {})


"""
insert = needle + """def _asset_human_applicable(asset: dict[str, Any]) -> bool:
    brief = asset.get('creative_brief') or {}
    sig = asset.get('visual_production_signature') or {}
    candidates = [
        brief.get('human'), brief.get('person'), brief.get('model'), brief.get('casting'), brief.get('subject'),
        asset.get('human_context'), asset.get('casting'), sig.get('context_role'), sig.get('visual_job'),
    ]
    blob = json.dumps([x for x in candidates if x not in (None, '', [], {})], ensure_ascii=False).casefold()
    terms = ['human','person','model','portrait','face','hand','body','hair','skin close','人物','人像','模特','面部','脸部','手部','人体','发质']
    return any(term in blob for term in terms)


def _inclusive_human_defaults() -> dict[str, Any]:
    return {
        'skin_tone_exposure': {
            'metering_priority': 'meter for the face/skin rather than the background; preserve real skin tone and deep-skin shadow detail',
            'exposure_compensation': 'prelight/metering-dependent; bias exposure only as needed to preserve deep-skin midtone/shadow detail, never apply a fixed whitening lift',
            'reflector_diffusion': 'use large soft diffusion plus a neutral/white reflector or bounce when needed to open shadows; keep natural facial contrast and avoid grey/ashy skin',
            'highlight_protection': 'protect forehead/cheek/specular highlights without solving highlights by underexposing the skin',
        },
        'hair_and_styling': 'Preserve real straight/wavy/curly/coily/protective hair texture; use lighting/edge separation rather than changing hair texture. Wardrobe/makeup follow the real task and locale, not ethnicity-as-costume.',
        'body_age_disability': 'Represent body type, age and disability naturally when relevant to the target/use case; do not erase mobility aids, age markers or body diversity in generation/retouching.',
        'ai_bias_controls': 'No default whitening, skin smoothing, youthifying, slimming, hair-texture homogenization or tokenistic/inspirational framing. Keep real pores, tone and task-relevant variation.',
        'representation_principle': 'People exist to perform the real shopper/use task. Identity changes representation and execution choices only when supported; it is not a shortcut to behavior.',
    }


"""
if '_asset_human_applicable' not in text:
    if needle not in text:
        raise SystemExit('asset reasoning anchor not found')
    text = text.replace(needle, insert, 1)

old = """    capture_mode=str(explicit.get('capture_mode') or reasoning.get('capture_mode') or asset.get('capture_mode') or '').upper() or None
    inherit_global=bool(explicit.get('inherit_strategy_photography') or reasoning.get('inherit_strategy_photography') or bool(reasoning) or capture_mode=='REAL_PHOTO')

    camera={}
"""
new = """    capture_mode=str(explicit.get('capture_mode') or reasoning.get('capture_mode') or asset.get('capture_mode') or '').upper() or None
    human_applicable=_asset_human_applicable(asset)
    inherit_global=bool(explicit.get('inherit_strategy_photography') or reasoning.get('inherit_strategy_photography') or bool(reasoning) or capture_mode=='REAL_PHOTO' or human_applicable)

    camera={}
"""
if old in text:
    text = text.replace(old, new, 1)
elif 'human_applicable=_asset_human_applicable(asset)' not in text:
    raise SystemExit('inherit_global anchor not found')

old = """    if isinstance(reasoning.get('camera_choice'),dict): camera.update(reasoning.get('camera_choice') or {})
    if isinstance(explicit.get('camera'),dict): camera.update(explicit.get('camera') or {})

    material=reasoning.get('material_lighting_profile') or {}
"""
new = """    if isinstance(reasoning.get('camera_choice'),dict): camera.update(reasoning.get('camera_choice') or {})
    if isinstance(explicit.get('camera'),dict): camera.update(explicit.get('camera') or {})
    # A human/context lens selected upstream is an execution decision, not disposable global prose.
    # Project it only for human-applicable assets; graphic/evidence assets remain compact.
    if human_applicable and not camera.get('focal_length_mm'):
        lens_spec=visual.get('lens') or {}
        focal_jobs=lens_spec.get('focal_length_by_job') if isinstance(lens_spec,dict) else None
        if isinstance(focal_jobs,dict):
            chosen=focal_jobs.get('context_or_use') or focal_jobs.get('human') or focal_jobs.get('portrait')
            if chosen not in (None,'',[],{}): camera['focal_length_mm']=chosen

    material=reasoning.get('material_lighting_profile') or {}
"""
if old in text:
    text = text.replace(old, new, 1)
elif "focal_jobs=lens_spec.get('focal_length_by_job')" not in text:
    raise SystemExit('camera fallback anchor not found')

old = """    inclusive=explicit.get('inclusive_photography') or reasoning.get('inclusive_photography') or {}
    if inherit_global and not inclusive: inclusive=visual.get('inclusive_photography') or {}
    repeatable=bool(explicit.get('repeatable_capture') or reasoning.get('repeatable_capture'))
"""
new = """    inclusive=explicit.get('inclusive_photography') or reasoning.get('inclusive_photography') or {}
    if inherit_global and not inclusive: inclusive=visual.get('inclusive_photography') or {}
    if human_applicable:
        # Human representation/exposure is P0 when people appear. Missing per-asset wiring must not
        # make the final Prompt silently lose skin-tone, reflector/diffusion or AI-bias execution.
        inclusive=_merge(_inclusive_human_defaults(), inclusive if isinstance(inclusive,dict) else {'representation_principle':inclusive})
    repeatable=bool(explicit.get('repeatable_capture') or reasoning.get('repeatable_capture'))
"""
if old in text:
    text = text.replace(old, new, 1)
elif '_inclusive_human_defaults()' not in text:
    raise SystemExit('inclusive anchor not found')

anchor = """def compile_asset_prompt(asset: dict[str, Any], product: dict[str, Any], target: dict[str, Any], culture: dict[str, Any], language_contract: dict[str, Any], locale_profiles: dict[str, Any] | None = None, photography: dict[str, Any] | None = None, strategy_authority: dict[str, Any] | None = None, source_product_assets: list[dict[str, Any]] | None = None) -> dict[str, Any]:
"""
helper = """def _prompt_consumption_audit(card:dict[str,Any], prompt_cn:str, prompt_en:str)->dict[str,Any]:
    relevance=_prompt_section_relevance(card)
    checks=[]
    def add(name:str, required:bool, cn_token:str, en_token:str, value:Any=None):
        if not required: return
        ok=(cn_token in prompt_cn) and (en_token in prompt_en)
        if value not in (None,'',[],{}):
            raw=str(value)
            # Exact selected values should survive at least the execution-language Prompt when serializable.
            ok=ok and (raw in prompt_en or raw in prompt_cn)
        checks.append({'decision':name,'required':True,'projected':bool(ok),'value':value})
    add('composition_camera',relevance['composition'],'【构图与摄影机】','[COMPOSITION / CAMERA]')
    add('lighting_material_cmf',relevance['lighting'],'【灯光 / 材质 / CMF】','[LIGHTING / MATERIAL / CMF]')
    add('inclusive_human_photography',relevance['inclusive'],'【包容性人物摄影】','[INCLUSIVE HUMAN PHOTOGRAPHY]')
    add('surface_information_design',relevance['surface'],'【Surface / 信息设计】','[SURFACE / INFORMATION DESIGN]')
    add('visual_boundaries_editability',relevance['boundaries'],'【视觉执行边界 / 可编辑性】','[VISUAL EXECUTION BOUNDARIES / EDITABILITY]')
    focal=(card.get('composition_camera') or {}).get('focal_length_mm')
    if focal not in (None,'',[],{}):
        checks.append({'decision':'selected_focal_length','required':True,'projected':str(focal) in prompt_en or str(focal) in prompt_cn,'value':focal})
    capture=(card.get('photography_execution') or {}).get('capture_mode')
    if capture not in (None,'',[],{}):
        checks.append({'decision':'capture_mode','required':True,'projected':str(capture) in prompt_en or str(capture) in prompt_cn,'value':capture})
    color=(card.get('photography_execution') or {}).get('color_management')
    if isinstance(color,dict) and color.get('output_space'):
        checks.append({'decision':'output_color_space','required':True,'projected':str(color.get('output_space')) in prompt_en or str(color.get('output_space')) in prompt_cn,'value':color.get('output_space')})
    checks.append({'decision':'real_product_identity','required':True,'projected':'【真实商品身份】' in prompt_cn and '[REAL PRODUCT IDENTITY]' in prompt_en})
    missing=[x['decision'] for x in checks if x.get('required') and not x.get('projected')]
    return {'status':'PASS' if not missing else 'INCOMPLETE','principle':'Semantic compression may remove repetition and irrelevant toolbox fields, but never an already-selected pixel/capture/composite-affecting execution decision.','checks':checks,'missing_decisions':missing}


"""
if '_prompt_consumption_audit' not in text:
    if anchor not in text:
        raise SystemExit('compile anchor not found')
    text = text.replace(anchor, helper + anchor, 1)

old = """    qa = {
        'decision_answer_visible': asset.get('incremental_information') or asset.get('belief_target'),
        'product_identity': card['product_identity']['rule'],
        'relevant_parameter_trace_complete': True,
"""
new = """    prompt_cn='\\n'.join(_render_lines(card, 'CN')).strip() + '\\n'
    prompt_en='\\n'.join(_render_lines(card, 'EN')).strip() + '\\n'
    consumption_audit=_prompt_consumption_audit(card,prompt_cn,prompt_en)
    qa = {
        'decision_answer_visible': asset.get('incremental_information') or asset.get('belief_target'),
        'product_identity': card['product_identity']['rule'],
        'relevant_parameter_trace_complete': consumption_audit.get('status')=='PASS',
"""
if old in text:
    text = text.replace(old, new, 1)
elif 'consumption_audit=_prompt_consumption_audit' not in text:
    raise SystemExit('qa anchor not found')

old = """    return {
        'status': 'CANONICAL_PROMPT_COMPILED_V0622_RELEVANCE_DRIVEN', 'design_card': card,
        'prompt_cn': '\\n'.join(_render_lines(card, 'CN')).strip() + '\\n',
        'prompt_en': '\\n'.join(_render_lines(card, 'EN')).strip() + '\\n',
        'deterministic_copy_overlay': locked_copy,
        'parameter_trace': _parameter_trace(card),
        'machine_visual_contract': machine, 'renderer_recipe': renderer, 'qa_target_contract': qa
    }
"""
new = """    return {
        'status': 'CANONICAL_PROMPT_COMPILED_EXECUTION_PRESERVING', 'design_card': card,
        'prompt_cn': prompt_cn,
        'prompt_en': prompt_en,
        'deterministic_copy_overlay': locked_copy,
        'parameter_trace': _parameter_trace(card),
        'prompt_consumption_audit': consumption_audit,
        'machine_visual_contract': machine, 'renderer_recipe': renderer, 'qa_target_contract': qa
    }
"""
if old in text:
    text = text.replace(old, new, 1)
elif "'prompt_consumption_audit': consumption_audit" not in text:
    raise SystemExit('return anchor not found')

P.write_text(text, encoding='utf-8')
print('prompt execution continuity repair applied')
