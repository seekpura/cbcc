from __future__ import annotations
from typing import Any
import json
import re


def _txt(v: Any, fallback: str = '') -> str:
    if v in (None, '', [], {}):
        return fallback
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def _merge(base: dict[str, Any] | None, override: dict[str, Any] | None) -> dict[str, Any]:
    out = dict(base or {})
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        elif v not in (None, '', [], {}):
            out[k] = v
    return out


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


def _asset_reasoning(strategy_authority: dict[str, Any] | None, asset_id: str | None) -> dict[str, Any]:
    sections = (strategy_authority or {}).get('sections') or {}
    visual = sections.get('05_visual_photography_strategy') or {}
    return next((r for r in (visual.get('asset_parameter_reasoning') or []) if r.get('asset_id') == asset_id), {})


def _asset_human_applicable(asset: dict[str, Any]) -> bool:
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


def _derived_photo_contract(asset: dict[str, Any], strategy_authority: dict[str, Any] | None, explicit: dict[str, Any] | None) -> dict[str, Any]:
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
    human_applicable=_asset_human_applicable(asset)
    production_mode=str(asset.get('production_mode') or '').upper()
    photographic_route=bool(
        capture_mode=='REAL_PHOTO'
        or production_mode in {'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT'}
        or explicit.get('photographic_route')
        or reasoning.get('photographic_route')
    )
    inherit_global=bool(explicit.get('inherit_strategy_photography') or reasoning.get('inherit_strategy_photography') or bool(reasoning) or photographic_route)

    camera={}
    if inherit_global and isinstance(visual.get('camera'),dict): camera.update(visual.get('camera') or {})
    if inherit_global and isinstance(visual.get('lens'),dict):
        for k,v in (visual.get('lens') or {}).items(): camera.setdefault(k,v)
    if isinstance(reasoning.get('camera_choice'),dict): camera.update(reasoning.get('camera_choice') or {})
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
    if human_applicable and photographic_route:
        # Real / photographic routes consume metering, reflector/diffusion and exposure controls.
        inclusive=_merge(_inclusive_human_defaults(), inclusive if isinstance(inclusive,dict) else {'representation_principle':inclusive})
    elif human_applicable:
        # Illustration/3D/stylized generation keeps representation and bias controls without pretending a camera/prelight exists.
        representation_defaults={
            'body_age_disability':'Represent body type, age and disability naturally when relevant; do not erase task-relevant variation.',
            'ai_bias_controls':'No default whitening, youthifying, slimming, hair-texture homogenization or tokenistic/inspirational framing.',
            'representation_principle':'People exist to perform the real shopper/use task. Identity changes representation choices only when supported; it is not a shortcut to behavior.',
        }
        inclusive=_merge(representation_defaults, inclusive if isinstance(inclusive,dict) else {'representation_principle':inclusive})
    repeatable=bool(explicit.get('repeatable_capture') or reasoning.get('repeatable_capture')) if photographic_route else False
    prelight_required=(bool(explicit.get('prelight_required')) if 'prelight_required' in explicit else bool(capture_mode=='REAL_PHOTO' and (repeatable or lighting.get('prelight_plan')))) if photographic_route else False

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

def _design_card(asset: dict[str, Any], product: dict[str, Any], target: dict[str, Any], culture: dict[str, Any], language_contract: dict[str, Any], photography: dict[str, Any] | None, strategy_authority: dict[str, Any] | None, source_product_assets: list[dict[str, Any]] | None) -> dict[str, Any]:
    sig = asset.get('visual_production_signature') or {}
    brief = asset.get('creative_brief') or {}
    direction = asset.get('creative_direction') or {}
    expression = asset.get('visual_expression_variant') or {}
    surface = asset.get('surface_native_contract') or {}
    copy_budget = asset.get('surface_copy_budget') or {}
    presence = asset.get('product_presence') or {}
    p = _derived_photo_contract(asset, strategy_authority, photography)
    camera = p.get('camera') or {}
    composition_execution = p.get('composition') or {}
    lighting = p.get('lighting') or {}
    color_management_execution = p.get('color_management') or {}
    cmf = p.get('cmf') or {}
    reasoning = p.get('asset_reasoning') or {}
    sections = (strategy_authority or {}).get('sections') or {}
    visual_master = sections.get('05_visual_photography_strategy') or {}
    core = sections.get('04_marketing_core_strategy') or {}
    pos = (core.get('positioning') or {}) if isinstance(core, dict) else {}
    product_fidelity = asset.get('product_fidelity') or 'REFERENCE_GUIDED'
    product_masters = list(source_product_assets or [])
    locked_masters = [m for m in product_masters if m.get('pixel_lock')]

    return {
        'asset_id': asset.get('asset_id'), 'asset_name': asset.get('asset_name'), 'asset_type': asset.get('asset_type'),
        'surface': asset.get('surface'), 'family': asset.get('family'),
        'commerce_task': {
            'consumer_question': asset.get('consumer_question'), 'decision_intent': asset.get('decision_intent'),
            'purchase_barrier': asset.get('purchase_barrier'), 'entry_state': asset.get('entry_state'),
            'target_belief': asset.get('belief_target'), 'exit_state': asset.get('exit_state'),
            'race_stage': asset.get('race_stage'), 'strategic_job': asset.get('strategic_job'),
            'reason_to_exist': asset.get('reason_to_exist'), 'incremental_information': asset.get('incremental_information'),
            'business_hypothesis': asset.get('business_hypothesis'), 'success_metric': asset.get('success_metric'),
            'handoff': asset.get('handoff')
        },
        'creative_system': {
            'direction_id': direction.get('direction_id'), 'direction_name': direction.get('direction_name'),
            'route': direction.get('route'), 'creative_thesis': direction.get('creative_thesis') or brief.get('creative_thesis'),
            'image_language': direction.get('image_language') or brief.get('image_language'),
            'verbal_thesis': direction.get('verbal_thesis') or brief.get('verbal_thesis'),
            'tradeoff': direction.get('tradeoff'), 'expression_variant': expression,
            'creative_anchor_plan': asset.get('creative_anchor_plan') or {},
        },
        'visual_objective': asset.get('incremental_information') or asset.get('belief_target') or asset.get('strategic_job'),
        'visual_narrative': {
            'shopper_question': asset.get('consumer_question'),
            'entry_state': asset.get('entry_state'),
            'belief_transition': f"{asset.get('entry_state') or 'uncertain'} → {asset.get('belief_target') or asset.get('exit_state') or 'decision-ready'}",
            'decisive_moment': expression.get('variant_id') or sig.get('visual_job') or 'Make the decision-critical relationship instantly legible.',
            'what_must_be_visible': asset.get('incremental_information') or asset.get('belief_target') or asset.get('strategic_job'),
            'what_must_not_become_decorative': 'Any visual element that does not change the purchase decision, prove an approved fact, or preserve the selected creative system.',
            'handoff': asset.get('handoff'),
        },
        'decisive_moment': expression.get('variant_id') or sig.get('visual_job') or 'Make the decision-critical relationship instantly legible.',
        'subject_action_environment_props': {
            'subject': brief.get('subject') or ('Use supplied product/source files as design references for the product subject; redraw/rerender is allowed unless an explicit locked-source mode is selected' if presence.get('planning_state') != 'FORBIDDEN' else 'decision-critical context/evidence'),
            'action': brief.get('action') or sig.get('visual_job') or asset.get('strategic_job'),
            'environment': brief.get('environment') or sig.get('context_role') or direction.get('scene_props'),
            'props': brief.get('props') or brief.get('scene_props') or direction.get('scene_props'),
            'human_context': brief.get('human') or culture.get('casting_constraints') or culture.get('casting_implications')
        },
        'composition_camera': {
            'composition_grammar': brief.get('composition') or reasoning.get('composition_choice') or sig.get('composition_grammar') or visual_master.get('composition'),
            'spatial_rhythm': expression.get('spatial_rhythm'),
            'camera_or_view': brief.get('camera_or_view') or sig.get('camera_or_view') or camera.get('view') or camera.get('preferred_view') or camera.get('perspective_contract') or camera.get('viewpoint'),
            'focal_length_mm': camera.get('focal_length_mm'), 'lens_family': camera.get('lens_family'),
            'projection': camera.get('projection'), 'azimuth': camera.get('azimuth') or camera.get('yaw_deg'),
            'elevation': camera.get('elevation') or camera.get('pitch_deg'), 'roll_deg': camera.get('roll_deg'),
            'distance': camera.get('distance') or camera.get('working_distance') or camera.get('camera_distance'), 'camera_height': camera.get('camera_height'),
            'focus_plane': camera.get('focus_plane'), 'aperture_dof_intent': camera.get('aperture_dof_intent') or camera.get('dof'),
            'shutter_speed': camera.get('shutter_speed'), 'iso': camera.get('iso') or camera.get('ISO'),
            'crop': brief.get('crop'), 'product_orientation': brief.get('product_orientation'),
            'safe_zone': brief.get('safe_zone') or surface.get('safe_zone'),
            'parameter_why': reasoning.get('parameter_why') or {}
        },
        'photography_execution': {
            'capture_mode': p.get('capture_mode'),
            'camera': _compact(camera),
            'composition': composition_execution,
            'lighting': _compact(lighting),
            'cmf': _compact(cmf),
            'color_management': color_management_execution,
            'repeatable_capture': p.get('repeatable_capture'),
            'prelight_required': p.get('prelight_required'),
        },
        'lighting_material_cmf': {
            'key': lighting.get('key'), 'fill': lighting.get('fill'), 'negative_fill': lighting.get('negative_fill'),
            'rim': lighting.get('rim'), 'cct': lighting.get('cct'), 'shadow': lighting.get('shadow'),
            'reflection': lighting.get('reflection') or lighting.get('reflection_control'),
            'highlight_policy': lighting.get('highlight_policy'),
            'prelight_plan': lighting.get('prelight_plan'), 'lighting_diagram': lighting.get('lighting_diagram'),
            'exposure_ratio_plan': lighting.get('exposure_ratio_plan'), 'polarization_plan': lighting.get('polarization_plan'),
            'color_consistency_plan': lighting.get('color_consistency_plan') or p.get('color_management'),
            'cmf': cmf, 'material_response_to_show': lighting.get('material_response_to_show'),
            'capture_implications': cmf.get('capture_implications') if isinstance(cmf, dict) else None,
            'post_implications': cmf.get('post_implications') if isinstance(cmf, dict) else None,
            'material_truth_rule': 'Creative/stylized material depiction is allowed when selected by the art direction. Do not present invented material, finish, texture or physical behavior as a verified product fact.'
        },
        'inclusive_photography': p.get('inclusive_photography') or {},
        'information_design': {
            'primary_message': asset.get('belief_target') or asset.get('incremental_information'),
            'secondary_message': asset.get('strategic_job'), 'proof_plane': sig.get('evidence_plane'),
            'locked_visible_copy': asset.get('visible_copy') or {}, 'copy_budget': copy_budget,
            'typography': brief.get('typography') or direction.get('typography'), 'language_contract': language_contract,
            'copy_visual_rule': 'Reserve deliberate copy zones in generation. Exact approved copy is composed deterministically after image generation unless the selected renderer has verified exact-text capability.'
        },
        'surface_contract': surface,
        'information_assetization': asset.get('information_assetization'), 'product_presence': presence,
        'product_identity': {
            'product_fidelity': product_fidelity, 'source_product_assets': product_masters,
            'product_visual_intelligence': asset.get('product_visual_intelligence') or {},
            'creative_anchor_plan': asset.get('creative_anchor_plan') or {}, 'locked_masters': locked_masters,
            'rule': ('Explicit locked-source mode: use supplied product master pixels as an immutable layer; do not regenerate, redraw, retype, recolor or reshape that layer.' if str(product_fidelity).upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} else 'Reference-guided mode: supplied files are design/product references, not immutable pixels. The product may be redrawn, rerendered, stylized, illustrated or recomposed according to the approved creative direction. Preserve verified product facts and only the identity cues the brief actually requires; photorealism and pixel matching are not default requirements.')
        },
        'market_locale': {
            'market': target.get('market'), 'platform': target.get('platform_family'), 'site': target.get('site'),
            'category': target.get('category'), 'primary_locale': language_contract.get('primary_locale'),
            'culture_implications': culture.get('visual_implications') or culture.get('copy_implications'),
            'casting_constraints': culture.get('casting_constraints'), 'intersectionality': culture.get('intersectionality')
        },
        'positioning_context': {
            'target_user': pos.get('target_user'), 'primary_conversion_proposition': pos.get('primary_conversion_proposition'),
            'message_hierarchy': pos.get('message_hierarchy')
        },
        'precision_boundaries': asset.get('precision_boundaries') or [],
        'approved_visual_elements': asset.get('approved_visual_elements') or [],
        'editable_layer_contract': asset.get('editable_layer_contract') or {},
    }


def _render_safe_text(value:Any)->str:
    """Remove runtime identifiers and product-name lead-ins from text sent to image/video renderers."""
    text=_txt(value)
    if not text:
        return ''
    # Runtime identifiers belong in Machine/Design Card, never in generative rendering prose.
    text=re.sub(r'\b(?:AST|DIR|VID|PROJECT)[-_][A-Z0-9_-]{3,}\b','',text,flags=re.I)
    # Direction synthesis often starts with "For <product name>, synthesize ...". The product
    # identity is already bound by the real reference images; repeating its name can invite redraw/retyping.
    text=re.sub(r'^\s*For\s+[^,]{1,160},\s*(?=synthesize\b)','',text,flags=re.I)
    text=re.sub(r'\s{2,}',' ',text).strip(' ,;')
    return text


def _render_expression(cs:dict[str,Any])->dict[str,Any]:
    expr=cs.get('expression_variant') or {}
    if not isinstance(expr,dict): return {'expression':_render_safe_text(expr)}
    allowed=['spatial_rhythm','composition_grammar','preferred_view','context_role','same_layout_guard']
    out={k:expr.get(k) for k in allowed if expr.get(k) not in (None,'',[],{})}
    if expr.get('direction_thesis'):
        out['direction_thesis']=_render_safe_text(expr.get('direction_thesis'))
    return out


def _render_anchor(cs:dict[str,Any])->str:
    anchor=cs.get('creative_anchor_plan') or {}
    if not isinstance(anchor,dict): return _render_safe_text(anchor)
    behaviors=[]
    for k in ['visual_behavior','lighting_reference','material_response','scene_language','composition_behavior','continuity_rule']:
        if anchor.get(k): behaviors.append(f"{k}: {_render_safe_text(anchor.get(k))}")
    if behaviors: return '; '.join(behaviors)
    roles=set(anchor.get('roles') or [])
    if roles:
        mapped=[]
        if 'HERO_KEYFRAME_MASTER' in roles: mapped.append('preserve the selected hero identity hierarchy without copying the same layout')
        if 'LIGHTING_REFERENCE_MASTER' in roles: mapped.append('keep the approved lighting character and white-balance family coherent')
        if 'MATERIAL_RESPONSE_MASTER' in roles: mapped.append('keep material gloss/texture/reflection behavior consistent with the approved reference')
        if 'SCENE_LANGUAGE_MASTER' in roles: mapped.append('keep the approved scene/prop language coherent while rebuilding composition for this decision job')
        if mapped: return '; '.join(mapped)
    return ''


def _render_without_exact_copy(value: Any) -> Any:
    """Keep layout/copy-budget constraints while withholding exact visible copy from render prompts.

    Exact target-market text belongs to deterministic_copy_overlay and the human Copy workbench.
    Passing it back through surface/copy-budget JSON would contradict the renderer text policy.
    """
    hidden = {'locked_copy', 'locked_visible_copy', 'visible_copy', 'target_copy', 'delivery_translation'}
    if isinstance(value, dict):
        return {k: _render_without_exact_copy(v) for k, v in value.items() if str(k) not in hidden}
    if isinstance(value, list):
        return [_render_without_exact_copy(v) for v in value]
    return value


def _clean_render_lines(lines:list[str])->list[str]:
    out=[]
    for x in lines:
        if x is None: continue
        text=str(x)
        stripped=text.strip()
        if not stripped: out.append(''); continue
        # Remove parameter rows that contain no actual value (e.g. "Shutter / ISO: / ").
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

def _cn_phrase(value:Any)->Any:
    """Human/renderer-facing Chinese companion for CBCC-owned strategy phrases.

    Exact technical tokens (mm/ISO/CCT/HEX/Surface names) are preserved. We translate our own
    deterministic prose and enum semantics; arbitrary user/source text is not silently rewritten.
    """
    if value in (None,'',[],{}): return value
    if isinstance(value,list): return [_cn_phrase(v) for v in value]
    if isinstance(value,dict):
        km={
          'direction':'方向','modifier':'控光附件','objective':'目标','frames':'测试帧','acceptance':'通过条件','boundary':'边界',
          'camera_axis':'相机轴线','key':'主光','fill':'补光','negative_fill':'负补光','rim':'轮廓光','background_light':'背景光','instruction':'执行说明',
          'declared_ratio':'声明光比','target_start':'起始目标','proof_material_range':'证据/材质范围','status':'状态','measurement':'测量方式','why':'为什么','final':'最终锁定',
          'applicable':'适用性','test':'测试方法','reference':'参考基准','white_balance':'白平衡','capture_rule':'拍摄规则','output_rule':'输出规则',
          'material':'材质','finish':'表面处理','surface_behavior':'表面光学行为','optical_risks':'光学风险','capture_implications':'拍摄影响','post_implications':'后期影响','logic':'逻辑','contrast':'对比策略','color':'颜色',
          'metering_priority':'测光优先','highlight_protection':'高光保护','hair':'发质','wardrobe':'服装','makeup':'妆容','rule':'规则','casting_boundary':'选角边界',
          'message_unit_budget':'主信息单元数','text_layer_budget':'文字层级数','density_class':'信息密度','product_dominance_target':'产品主导程度','hard_character_limit':'硬字符限制','overflow_rule':'溢出处理',
          'surface':'展示位置','decision_job':'决策任务','representation':'表达方式','product_presence':'产品出现方式','mobile_scan_rule':'移动端扫描原则','reuse_rule':'复用原则',
          'intersectionality_notes':'交叉性维度','intersectionality_context':'交叉性语境','missing':'待补项',
        }
        return {km.get(str(k),str(k)):_cn_phrase(v) for k,v in value.items() if v not in (None,'',[],{})}
    raw=str(value)
    exact={
      'Human Use Decisive Moment × Information Hierarchy as Visual Form':'真实使用关键瞬间 × 信息层级视觉化',
      'Evidence Relationship / Causal Proof × Category Convention Reframing':'证据关系 / 因果证明 × 品类惯例重构',
      'Current-product mechanism synthesis: HUMAN_CONTEXT + INFORMATION_DESIGN. Coherence comes from Product Truth/CMF/type tokens; composition is rebuilt per decision job.':'当前产品机制：真实人物/使用语境 + 信息设计。用商品真源、CMF 与字体系统维持一致性；每张资产按自己的购买问题重新构图，不继承上一张版式。',
      'Use the supplied real-product master as the product subject':'以用户提供的真实商品母版作为商品主体',
        'Use supplied product/source files as design references for the product subject; redraw/rerender is allowed unless an explicit locked-source mode is selected':'使用已提供的产品/源文件作为设计参考；除非显式选择锁定源图模式，否则允许重绘与重新渲染。',
        'Reference-guided mode: supplied product/source files guide design and identity cues; redraw, rerender, stylize, illustrate or recompose as the selected direction requires. Do not present creative changes as verified product facts.':'参考设计模式：已提供的产品/源文件用于指导设计与必要的身份线索；可按已选方向重绘、重渲染、风格化、插画化或重新构图。不得把创作性变化当成已验证商品事实。',
        'Explicit locked-source mode: preserve the supplied product master as an immutable source layer; do not redraw that layer.':'显式锁定源图模式：已提供的产品母图作为不可修改的源图层保留，不得重绘该图层。',
      'decision-critical context/evidence':'与购买决策直接相关的语境 / 证据',
      'Resolve the named shopper decision with one clearly visible information relationship.':'用一个清晰可见的信息关系解决当前购买问题。',
      'Make product identity and the primary proposition recoverable at first scan.':'让消费者第一眼识别商品身份与第一购买理由。',
      'specific use context':'具体、可信的真实使用语境',
      'minimal category cue':'最小化品类语境，只保留识别所需线索',
      'hands/body/real use context':'手部 / 身体关系 / 真实使用语境',
      'Only mechanism-relevant scale/use/evidence/context objects; no decorative prop kit.':'只使用与机理、尺度、使用、证据或语境直接相关的道具；不放装饰性道具套件。',
      'product-dominant identity field':'产品主导的身份识别画面',
      'context-led relevance frame':'语境主导的相关性画面',
      'proof-led hierarchy':'证据主导的信息层级',
      'action-led use moment':'动作主导的真实使用关键瞬间',
      'front/3Q label-readable view':'正面 / 三分之四视角，保证标签可读',
      'human/object/environment relationship':'人物 / 商品 / 环境关系视角',
      'orthographic/macro/evidence plane':'正交 / 微距 / 证据平面，根据证据任务选择',
      'interaction/contact-point angle':'围绕真实交互 / 接触点选择机位',
      'LEFT_WEIGHTED':'左侧重心','RIGHT_WEIGHTED':'右侧重心','CENTERED_OBJECT_STUDY':'中心商品研究式构图','TOP_DOWN_SYSTEM':'俯视系统关系构图','DIAGONAL_ACTION':'对角动作关系构图',
      'large diffusion':'大型柔光', 'NORMALLY_NOT_REQUIRED':'通常不需要','CONDITIONAL_TEST':'条件测试','MEASURE_IN_PRELIGHT':'Prelight 实测后锁定',
      'REQUIRED':'必须','OPTIONAL':'可选','FORBIDDEN':'禁止','PRESENT':'出现','RESOLVE_PER_BLUEPRINT':'按资产蓝图决定','IMAGE':'图片','VIDEO':'视频','HYBRID':'混合表达','MEDIUM':'中等','LOW_TO_MEDIUM':'低到中等','HIGH':'高',
      'SUPPLIED_CMF_REQUIRED':'必须以已提供的 CMF / 实物材质为准',
      'ethnicity × gender × age × income × geography':'族裔 × 性别 × 年龄 × 收入 × 地域',
      'color':'颜色','material':'材质','finish':'表面处理','PARTIAL':'部分信息待补',
    }
    if raw in exact:return exact[raw]
    replacements=[
      ('full-frame equivalent starting recommendation','全画幅等效，作为起始建议'),('equivalent starting recommendation','等效，作为起始建议'),('starting recommendation','起始建议'),
      ('camera-left/front','相机左前方'),('camera-right/front','相机右前方'),('above decision plane','高于决策平面'),('neutral bounce','中性反光板'),('one stop lower','低一档'),
      ('product optical center / interaction plane','产品光学中心 / 交互决策平面'),('decision-relevant product, skin or evidence plane','与当前决策相关的产品 / 肤色 / 证据平面'),
      ('starting point; freeze final WB after prelight','起始值；Prelight 后锁定最终白平衡'),('starting point','起始值'),
      ('protect label, skin and package highlights from clipping; preserve truthful gloss','保护标签、肤色与包装高光不过曝，同时保留真实光泽'),
      ('matte flexible tube + transparent pump-style applicator','哑光软管 + 透明泵式出料结构'),('truthful matte / transparent response; preserve real highlight behavior','保持真实哑光 / 透明材质响应，并保留真实高光行为'),
      ('no default whitening','禁止默认美白'),('no slimming/body reshaping','禁止瘦身或重塑体型'),('no youthifying','禁止年轻化处理'),('no hair-texture homogenization','禁止统一/抹平发质差异'),('no disability erasure','禁止消除残障特征'),
      ('check hands/assistive devices/hair edges/body proportions','检查手部、辅助器具、发丝边缘与身体比例'),
      ('Measure key/fill or lit/shadow stop difference on the decision-relevant product plane; freeze the accepted ratio for repeat shots.','在当前决策相关的产品平面测量主光/补光或亮面/暗面的档位差；确认后锁定该光比用于同组重复拍摄。'),
      ('Numeric ratio is useful only when tied to readable label/material contrast; the runtime does not invent a premium-looking ratio.','只有当数值光比能服务标签可读性和材质分离时才有意义；系统不会为了所谓“高级感”虚构光比。'),
      ('Material-specific optical behavior is under-specified; do not invent gloss/transparency/metal behavior.','当前材质的特定光学行为信息不足；不得凭空增加高光泽、透明、金属等材质表现。'),
      ('Derive the field from verified product/brand/material cues and the selected mechanism; never apply a universal category palette.','色彩场必须从已验证的商品、品牌、材质线索和本张表达机制推导；不得套用品类通用配色模板。'),
      ('Optimize figure/ground, material separation and mobile readability for the current Surface.','针对当前展示位置优化主体/背景分离、材质区分和移动端可读性。'),
      ('meter for face/skin and protect deep-skin shadow detail','以面部/肤色为主要测光依据，保护深肤色暗部层次'),
      ('protect specular highlights without lifting skin unnaturally','保护镜面高光不过曝，同时不得不自然地提亮肤色'),
      ('Preserve real straight/wavy/curly/coily/protective style texture; use edge separation for dark hair instead of changing texture.','保留真实直发、波浪、卷发、紧卷或保护性发型的纹理；深色头发用边缘分离和控光解决，不改变真实发质。'),
      ('Choose wardrobe from product task, locale and scene; do not use ethnicity as costume.','服装应从商品任务、当地语境和真实场景推导；不得把族裔身份当作服装符号。'),
      ('Keep real skin texture/tone; makeup supports the scene and product, not whitening/youthifying.','保留真实肤质和肤色；妆容只服务场景与商品，不做默认美白或年轻化。'),
      ('Represent age/body/disability naturally when relevant to the target/use case; do not erase mobility aids, age markers or body diversity in generation/retouching.','当目标人群或使用情境相关时，自然呈现年龄、体型和残障差异；生成或修图不得消除辅助器具、年龄特征或身体多样性。'),
      ('No tokenistic or inspirational framing; the person exists to perform the real decision/use task.','避免象征性凑数或“励志化”呈现；人物存在的目的应是完成真实的购买判断或使用任务。'),
      ('Deterministic final copy composition; hierarchy and text area follow current Surface copy budget and evidence plane.','最终文案采用确定性排版合成；信息层级与文字区域遵循当前展示位置的文案预算和证据平面。'),
      ('Show the actual operation/routine relationship that reduces use uncertainty.','展示真实操作或日常使用流程关系，降低消费者对使用方式的不确定性。'),
      ('Make the approved proof object legible and attributable to the product without turning proof into decoration.','让已批准的证据对象清晰可读，并能明确归属于该商品；不能把证据做成装饰。'),
      ('verified proof artifact/data','可验证的证据物 / 数据'),
      ('Primary Proposition','第一购买理由'),
      ('RTB/Proof','可验证理由 / 证据'),
      ('first-screen comprehension','首屏理解度'),
      ('PDP progression','详情页继续浏览 / 决策推进'),
      ('claim comprehension','宣称理解度'),
    ]
    out=raw
    for a,b in replacements: out=out.replace(a,b)
    return out


def _cn_expression(cs:dict[str,Any])->str:
    e=_render_expression(cs)
    parts=[]
    label={'spatial_rhythm':'空间节奏','composition_grammar':'构图语法','preferred_view':'建议视角','context_role':'语境角色','same_layout_guard':'防同版式规则','direction_thesis':'方向母命题'}
    for k in ['spatial_rhythm','composition_grammar','preferred_view','context_role']:
        if e.get(k): parts.append(f"{label[k]}：{_txt(_cn_phrase(e[k]))}")
    if e.get('same_layout_guard'): parts.append('防同版式规则：保留设计系统一致性，但必须按本资产的购买问题重新建立层级与构图，不能继承上一张版式。')
    return '；'.join(parts)


def _cn_anchor(cs:dict[str,Any])->str:
    anchor=cs.get('creative_anchor_plan') or {}
    roles=set(anchor.get('roles') or []) if isinstance(anchor,dict) else set()
    rows=[]
    if 'HERO_KEYFRAME_MASTER' in roles: rows.append('延续已选主视觉的商品身份层级，但不复制同一版式')
    if 'LIGHTING_REFERENCE_MASTER' in roles: rows.append('保持已批准的灯光性格与白平衡家族一致')
    if 'MATERIAL_RESPONSE_MASTER' in roles: rows.append('保持材质光泽、纹理、反射行为与真实参考一致')
    if 'SCENE_LANGUAGE_MASTER' in roles: rows.append('保持场景与道具语言一致，同时按当前购买问题重建构图')
    return '；'.join(rows)


def _cn_creative_thesis(card:dict[str,Any])->str:
    cs=card.get('creative_system') or {}; task=card.get('commerce_task') or {}; route=str(cs.get('route') or '')
    route_name={'HUMAN_CONTEXT_ACTION':'真实使用关键瞬间 + 信息层级视觉化','EVIDENCE_MECHANISM':'证据关系 / 因果证明 + 品类惯例重构','PRODUCT_IDENTITY':'商品身份 / 第一购买理由','MATERIAL_OPTICS':'材质 / 光学行为证明','SYSTEM_RELATIONSHIP':'系统 / 兼容关系可视化'}.get(route)
    if not route_name: route_name=_cn_phrase(cs.get('direction_name')) or '购买问题驱动的视觉表达'
    reason=task.get('reason_to_exist') or card.get('visual_objective') or task.get('strategic_job')
    return f"采用“{route_name}”来解决本资产的购买问题。{_txt(reason)}"


def _cn_surface_summary(surface:dict[str,Any], info:dict[str,Any])->str:
    cb=(info.get('copy_budget') or surface.get('copy_budget') or {}) if isinstance(info,dict) else {}
    rows=[]
    if surface.get('surface'): rows.append(f"展示位置：{surface.get('surface')}")
    if surface.get('representation'): rows.append(f"表达方式：{_cn_phrase(surface.get('representation'))}")
    if surface.get('product_presence'): rows.append(f"产品出现：{_cn_phrase(surface.get('product_presence'))}")
    if cb:
        rows.append(f"文案预算：主信息单元 {cb.get('message_unit_budget','—')} 个，文字层级 {cb.get('text_layer_budget','—')} 层，密度 {_cn_phrase(cb.get('density_class')) or '—'}")
    rows.append('移动端第一眼只保留一个主要购买答案；次级解释移到相邻原生内容位，不靠缩小所有文字硬塞。')
    rows.append('跨 Surface 复用商品真源与证据，但版式和文案必须按当前 Surface 任务重新策展，不能机械改尺寸。')
    return '；'.join(rows)


def _render_lines(card: dict[str, Any], language: str) -> list[str]:
    cs = card['creative_system']; sae = card['subject_action_environment_props']; cam = card['composition_camera']
    photo_exec = card.get('photography_execution') or {}
    lm = card['lighting_material_cmf']; inc = card.get('inclusive_photography') or {}; info = card['information_design']
    prod = card['product_identity']; surface = card.get('surface_contract') or {}; loc = card['market_locale']
    approved_visual = card.get('approved_visual_elements') or []
    precision = card.get('precision_boundaries') or []
    editable = card.get('editable_layer_contract') or {}
    surface_render = _render_without_exact_copy(surface)
    copy_budget_render = _render_without_exact_copy(info.get('copy_budget') or {})
    cn = language.upper() == 'CN'

    if cn:
        # CN is a real Chinese production prompt, not Chinese labels wrapped around English runtime prose.
        # Internal IDs/RACE/KPI stay in Design/Machine contracts; model-facing Chinese carries only executable visual instructions.
        key=lm.get('key'); key_cn=_cn_phrase(key)
        fill_cn=_cn_phrase(lm.get('fill')); neg_cn=_cn_phrase(lm.get('negative_fill')); rim_cn=_cn_phrase(lm.get('rim'))
        prelight='先拍中性/商品颜色参考帧、正面标签可读帧、边缘/材质响应帧；通过后锁定灯位、距离、功率、白平衡和曝光参考。'
        polarization='先保留无偏振基准；仅在能去除遮挡信息的眩光、且不会抹掉真实光泽/透明度/印刷/材质线索时使用偏振。'
        color_consistency='同一镜头家族锁定白平衡与曝光参考；商品材质、光源或背景改变后重新拍参考帧，跨资产对照商品/品牌/肤色颜色一致性。'
        inc_skin=_cn_phrase(inc.get('skin_tone_exposure'))
        inc_hair=_cn_phrase(inc.get('hair_and_styling'))
        inc_body=_cn_phrase(inc.get('body_age_disability'))
        inc_bias=_cn_phrase(inc.get('ai_bias_controls'))
        lines = [
            '【生成目标】',
            f"视觉任务：{_txt(_cn_phrase(card.get('visual_objective')))}",
            f"消费者问题：{_txt(_cn_phrase((card.get('commerce_task') or {}).get('consumer_question')))}",
            'Product Truth / 参考设计绑定：已验证商品事实与 Claim 不得被创意改写；随任务提供的源文件作为产品设计参考。除非明确选择锁定源图模式，否则允许重绘、重渲染、风格化、插画化与重新构图，不要求像素级一致或摄影写实。',
            f"创意母命题：{_cn_creative_thesis(card)}",
            '图像语言：根据当前创意方向决定写实、风格化、插画、3D、合成或其他视觉语言；源文件提供设计与商品事实参考，每张资产按自己的购买问题重新建立空间层级和构图。',
            f"本张表达机制：{_cn_expression(cs)}", f"创意锚点：{_cn_anchor(cs)}",
            '', '【主体 / 动作 / 环境】',
            f"主体：{_txt(_cn_phrase(sae.get('subject')))}", f"动作：{_txt(_cn_phrase(sae.get('action')))}",
            f"环境：{_txt(_cn_phrase(sae.get('environment')))}", f"道具：{_txt(_cn_phrase(sae.get('props')))}",
            f"人物与选角：{_txt(_cn_phrase(sae.get('human_context')))}",
            '', '【构图与摄影机】',
            f"构图语法：{_txt(_cn_phrase(cam.get('composition_grammar')))}", f"空间节奏：{_txt(_cn_phrase(cam.get('spatial_rhythm')))}",
            f"机位 / 视角：{_txt(_cn_phrase(cam.get('camera_or_view')))}", f"焦段 / 镜头族：{_txt(_cn_phrase(cam.get('focal_length_mm')))} / {_txt(_cn_phrase(cam.get('lens_family')))}",
            f"方位 / 俯仰 / 滚转：{_txt(_cn_phrase(cam.get('azimuth')))} / {_txt(_cn_phrase(cam.get('elevation')))} / {_txt(_cn_phrase(cam.get('roll_deg')))}",
            f"距离 / 机位高度：{_txt(_cn_phrase(cam.get('distance')))} / {_txt(_cn_phrase(cam.get('camera_height')))}",
            f"对焦面 / 景深：{_txt(_cn_phrase(cam.get('focus_plane')))} / {_txt(_cn_phrase(cam.get('aperture_dof_intent')))}",
            f"快门 / ISO：{_txt(_cn_phrase(cam.get('shutter_speed')))} / {_txt(_cn_phrase(cam.get('iso')))}",
            f"裁切 / 产品方向 / 安全区：{_txt(_cn_phrase(cam.get('crop')))} / {_txt(_cn_phrase(cam.get('product_orientation')))} / {_txt(_cn_phrase(cam.get('safe_zone')))}",
            f"拍摄 / 合成模式：{_txt(_cn_phrase(photo_exec.get('capture_mode')))}",
            f"构图执行合同：{_txt(_cn_phrase(photo_exec.get('composition')))}",
            f"摄影机执行合同：{_txt(_cn_phrase(photo_exec.get('camera')))}",
            '', '【灯光 / 材质 / CMF】',
            f"主光 / 补光 / 负补光 / 轮廓光：{_txt(key_cn)} / {_txt(fill_cn)} / {_txt(neg_cn)} / {_txt(rim_cn)}",
            f"色温 / 阴影 / 高光：{_txt(_cn_phrase(lm.get('cct')))} / {_txt(_cn_phrase(lm.get('shadow')))} / {_txt(_cn_phrase(lm.get('highlight_policy')))}",
            f"光比：{_txt(_cn_phrase(lm.get('exposure_ratio_plan')))}", f"反射与偏振：{_txt(_cn_phrase(lm.get('reflection')))} / {_txt(_cn_phrase(lm.get('polarization_plan')))}",
            f"Prelight：{_txt(_cn_phrase(lm.get('prelight_plan')))}",
            f"CMF：{_txt(_cn_phrase(lm.get('cmf')))}", f"需要表现的材质响应：{_txt(_cn_phrase(lm.get('material_response_to_show')))}",
            f"拍摄影响：{_txt(_cn_phrase(lm.get('capture_implications')))}", f"后期影响：{_txt(_cn_phrase(lm.get('post_implications')))}",
            f"色彩管理合同：{_txt(_cn_phrase(photo_exec.get('color_management')))}",
            f"颜色一致性：{_txt(_cn_phrase(lm.get('color_consistency_plan')))}", '材质事实边界：可以按创意方向做风格化材质表达，但不得把源文件未支持的材质、表面处理或物理行为当成真实商品事实。',
            '', '【包容性人物摄影】',
            f"肤色曝光：{_txt(inc_skin)}", f"发质 / 服化道：{_txt(inc_hair)}",
            f"交叉性语境：{_txt(_cn_phrase(inc.get('intersectionality_context') or loc.get('intersectionality')))}",
            f"体型 / 年龄 / 残障：{_txt(inc_body)}", f"AI 偏见控制：{_txt(inc_bias)}",
            '代表性原则：自然呈现与真实使用任务相关的人群差异；不把身份维度当作行为结论，不做默认美白、瘦身、年轻化、发质同质化或残障消除。',
            '', '【Surface / 信息设计】',
            _cn_surface_summary(surface,info), f"字体 / 文案方向：{_txt(_cn_phrase(info.get('typography')))}",
            '生成画面时为锁定文案预留清晰版式区，但不要让图像模型重写包装文字或最终营销文案；精确文案在后期确定性合成。',
            '', '【视觉执行边界 / 可编辑性】',
            f"允许进入画面的视觉元素：{_txt(_cn_phrase(approved_visual))}",
            f"精确执行边界：{_txt(_cn_phrase(precision))}",
            f"可编辑层：{_txt(_cn_phrase(editable.get('editable_layers')))}",
            f"冻结层：{_txt(_cn_phrase(editable.get('frozen_layers')))}",
            '局部修改规则：遵守当前资产声明的冻结事实/Claim/文案边界；参考图本身只有在显式锁定源图模式下才是不可改像素层。' if editable else '',
            '', '【产品参考 / 保真策略】',
            f"商品参考模式：{_txt(prod.get('product_fidelity'))}",
            prod.get('rule'),
            '', '【禁止生成】',
            '不得生成未被产品真源 / 证据支持的成分、质地、认证、检测、疗效、人体结果、before/after、比较数字或包装文字；不得为了“高级感”添加与购买判断无关的水花、粒子、实验室符号、抽象光环或模板化卡片。'
        ]
    else:
        lines = [
            '[RENDER OBJECTIVE]',
            f"Visual task: {_txt(card.get('visual_objective'))}",
            f"Consumer decision question: {_txt((card.get('commerce_task') or {}).get('consumer_question'))}",
            'Product Truth / reference binding: verified product facts and claims must remain honest. Supplied source files are product/design references; unless locked-source mode is explicitly selected, redraw, rerender, stylization, illustration and recomposition are allowed and photorealism/pixel matching are not required.',
            f"Creative thesis: {_render_safe_text(cs.get('creative_thesis'))}", f"Image language: {_render_safe_text(cs.get('image_language'))}",
            f"Asset expression mechanism: {_txt(_render_expression(cs))}", f"Creative anchor: {_render_anchor(cs)}",
            '', '[SUBJECT / ACTION / ENVIRONMENT]',
            f"Subject: {_txt(sae.get('subject'))}", f"Action: {_txt(sae.get('action'))}",
            f"Environment: {_txt(sae.get('environment'))}", f"Props: {_txt(sae.get('props'))}",
            f"Human / casting: {_txt(sae.get('human_context'))}",
            '', '[COMPOSITION / CAMERA]',
            f"Composition grammar: {_txt(cam.get('composition_grammar'))}", f"Spatial rhythm: {_txt(cam.get('spatial_rhythm'))}",
            f"Camera / view: {_txt(cam.get('camera_or_view'))}", f"Focal length / lens family: {_txt(cam.get('focal_length_mm'))} / {_txt(cam.get('lens_family'))}",
            f"Azimuth / elevation / roll: {_txt(cam.get('azimuth'))} / {_txt(cam.get('elevation'))} / {_txt(cam.get('roll_deg'))}",
            f"Working distance / camera height: {_txt(cam.get('distance'))} / {_txt(cam.get('camera_height'))}",
            f"Focus plane / depth of field: {_txt(cam.get('focus_plane'))} / {_txt(cam.get('aperture_dof_intent'))}",
            f"Shutter / ISO: {_txt(cam.get('shutter_speed'))} / {_txt(cam.get('iso'))}",
            f"Crop / product orientation / safe zone: {_txt(cam.get('crop'))} / {_txt(cam.get('product_orientation'))} / {_txt(cam.get('safe_zone'))}",
            f"Capture / composite mode: {_txt(photo_exec.get('capture_mode'))}",
            f"Composition execution contract: {_txt(photo_exec.get('composition'))}",
            f"Camera execution contract: {_txt(photo_exec.get('camera'))}",
            '', '[LIGHTING / MATERIAL / CMF]',
            f"Key / fill / negative fill / rim: {_txt(lm.get('key'))} / {_txt(lm.get('fill'))} / {_txt(lm.get('negative_fill'))} / {_txt(lm.get('rim'))}",
            f"CCT / shadow / highlight policy: {_txt(lm.get('cct'))} / {_txt(lm.get('shadow'))} / {_txt(lm.get('highlight_policy'))}",
            f"Exposure ratio: {_txt(lm.get('exposure_ratio_plan'))}", f"Reflection / polarization: {_txt(lm.get('reflection'))} / {_txt(lm.get('polarization_plan'))}",
            f"Prelight plan: {_txt(lm.get('prelight_plan'))}", f"Lighting diagram: {_txt(lm.get('lighting_diagram'))}",
            f"CMF: {_txt(lm.get('cmf'))}", f"Material response to show: {_txt(lm.get('material_response_to_show'))}",
            f"Capture implications: {_txt(lm.get('capture_implications'))}", f"Post implications: {_txt(lm.get('post_implications'))}",
            f"Color management contract: {_txt(photo_exec.get('color_management'))}",
            f"Color consistency: {_txt(lm.get('color_consistency_plan'))}", f"Material-truth boundary: {lm.get('material_truth_rule')}",
            '', '[INCLUSIVE HUMAN PHOTOGRAPHY]',
            f"Skin-tone exposure: {_txt(inc.get('skin_tone_exposure'))}", f"Hair / wardrobe / makeup: {_txt(inc.get('hair_and_styling'))}",
            f"Intersectionality context: {_txt(inc.get('intersectionality_context') or loc.get('intersectionality'))}",
            f"Body / age / disability: {_txt(inc.get('body_age_disability'))}", f"AI bias controls: {_txt(inc.get('ai_bias_controls'))}",
            f"Representation principle: {_txt(inc.get('representation_principle'))}",
            '', '[SURFACE / INFORMATION DESIGN]',
            f"Surface visual constraints: {_txt(surface_render)}", f"Copy budget: {_txt(copy_budget_render)}", f"Typography direction: {_txt(info.get('typography'))}",
            'Reserve deliberate layout zones for locked copy, but do not ask the image model to retype packaging or final marketing copy. Exact approved text is composed deterministically after generation.',
            '', '[VISUAL EXECUTION BOUNDARIES / EDITABILITY]',
            f"Approved visual elements: {_txt(approved_visual)}",
            f"Precision boundaries: {_txt(precision)}",
            f"Editable layers: {_txt(editable.get('editable_layers'))}",
            f"Frozen layers: {_txt(editable.get('frozen_layers'))}",
            'Local edit rule: preserve declared product facts/claims/copy boundaries; source pixels are immutable only in an explicit locked-source mode.' if editable else '',
            '', '[PRODUCT REFERENCE / FIDELITY]',
            f"Product reference mode: {_txt(prod.get('product_fidelity'))}",
            prod.get('rule'),
            '', '[DO NOT GENERATE]',
            'Do not invent unsupported ingredients, textures, tests, certifications, efficacy, body outcomes, before/after, comparison numbers or package copy. Do not add arbitrary premium splashes, particles, laboratory symbolism, abstract halos or repetitive card layouts.'
        ]
    lines=_filter_relevant_prompt_sections(lines,card,cn)
    return _clean_render_lines([x for x in lines if x is not None and str(x).strip() != 'None'])


def _parameter_trace(card: dict[str, Any]) -> list[dict[str, Any]]:
    rows=[
        {'strategy_parameter':'creative thesis / image language / creative anchor','render_location':'RENDER OBJECTIVE','value':card.get('creative_system')},
        {'strategy_parameter':'consumer decision question / Product Truth execution binding','render_location':'RENDER OBJECTIVE / PRODUCT REFERENCE / FIDELITY','value':{'consumer_question':(card.get('commerce_task') or {}).get('consumer_question'),'product_truth_binding':'FACT_BOUND_REFERENCE_GUIDED'}},
        {'strategy_parameter':'composition / camera / lens / focus / exposure settings','render_location':'COMPOSITION / CAMERA','value':card.get('composition_camera')},
        {'strategy_parameter':'capture mode / product occupancy / negative space / output color management','render_location':'PHOTOGRAPHY EXECUTION CONTRACT','value':card.get('photography_execution')},
        {'strategy_parameter':'lighting / CCT / ratio / prelight / polarization / CMF / material response / color management','render_location':'LIGHTING / MATERIAL / CMF','value':{k:v for k,v in (card.get('lighting_material_cmf') or {}).items() if k!='material_truth_rule'}},
        {'strategy_parameter':'skin-tone exposure / hair / wardrobe / intersectionality','render_location':'INCLUSIVE HUMAN PHOTOGRAPHY','value':card.get('inclusive_photography')},
        {'strategy_parameter':'surface / safe zone / copy budget / typography','render_location':'SURFACE / INFORMATION DESIGN','value':{'surface':card.get('surface_contract'),'information_design':card.get('information_design')}},
        {'strategy_parameter':'approved visual elements / precision boundaries / editable & frozen layers','render_location':'VISUAL EXECUTION BOUNDARIES / EDITABILITY','value':{'approved_visual_elements':card.get('approved_visual_elements'),'precision_boundaries':card.get('precision_boundaries'),'editable_layer_contract':card.get('editable_layer_contract')}},
        {'strategy_parameter':'product reference / fidelity policy','render_location':'PRODUCT REFERENCE / FIDELITY','value':card.get('product_identity')},
    ]
    return [_compact(row) for row in rows if _meaningful(row.get('value'))]


def _renderer_layer_plan(card:dict[str,Any],locked_copy:dict[str,Any])->list[str]:
    layers=[]
    subject=card.get('subject_action_environment_props') or {}
    presence=card.get('product_presence') or {}
    if _meaningful(subject.get('environment')): layers.append('background_environment')
    if _meaningful(subject.get('human_context')): layers.append('human_or_context_if_required')
    if str(presence.get('planning_state') or '').upper()!='FORBIDDEN' or _meaningful(card.get('product_identity')): layers.append('product_reference_or_product_subject')
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

def _prompt_consumption_audit(card:dict[str,Any], prompt_cn:str, prompt_en:str)->dict[str,Any]:
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
    checks.append({'decision':'product_reference_fidelity','required':True,'projected':'【产品参考 / 保真策略】' in prompt_cn and '[PRODUCT REFERENCE / FIDELITY]' in prompt_en})
    missing=[x['decision'] for x in checks if x.get('required') and not x.get('projected')]
    return {'status':'PASS' if not missing else 'INCOMPLETE','principle':'Prompt readiness is a production-quality diagnostic, not a project-completion gate. When prompts are requested, preserve the selected execution decisions that actually matter to that production route.','checks':checks,'missing_decisions':missing}


def compile_asset_prompt(asset: dict[str, Any], product: dict[str, Any], target: dict[str, Any], culture: dict[str, Any], language_contract: dict[str, Any], locale_profiles: dict[str, Any] | None = None, photography: dict[str, Any] | None = None, strategy_authority: dict[str, Any] | None = None, source_product_assets: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    card = _design_card(asset, product, target, culture, language_contract, photography, strategy_authority, source_product_assets)
    source_assets = card.get('product_identity', {}).get('source_product_assets') or []
    locked_copy = card.get('information_design', {}).get('locked_visible_copy') or {}
    machine = _compact({
        'asset_id': card.get('asset_id'), 'surface': card.get('surface'), 'production_mode': asset.get('production_mode'),
        'product_fidelity': asset.get('product_fidelity'),
        'fidelity': {
            'mode': asset.get('product_fidelity'),
            'source_product_asset_ids': [x.get('asset_id') for x in source_assets if isinstance(x, dict) and x.get('asset_id')],
            'real_product_master_required': str(asset.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'},
            'real_product_master_substitution_allowed': str(asset.get('product_fidelity') or '').upper() not in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'},
            'immutable_identity_fields': ['logo', 'packaging_print', 'product_color_identity', 'geometry', 'proportions'] if str(asset.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} else ['verified_product_facts', 'approved_claim_facts'],
        },
        'product_presence': card.get('product_presence'), 'information_assetization': card.get('information_assetization'),
        'composition_camera': card.get('composition_camera'), 'photography_execution': card.get('photography_execution'), 'lighting_material_cmf': card.get('lighting_material_cmf'),
        'inclusive_photography': card.get('inclusive_photography'), 'information_design': card.get('information_design'),
        'surface_contract': card.get('surface_contract'), 'creative_system': card.get('creative_system'),
        'editable_layer_contract': card.get('editable_layer_contract'), 'precision_boundaries': card.get('precision_boundaries'),
        'approved_visual_elements': card.get('approved_visual_elements')
    })
    source_bindings = []
    for row in source_assets:
        if not isinstance(row, dict):
            continue
        handle = row.get('provider_asset_handle')
        path = row.get('path')
        source_bindings.append({
            'asset_id': row.get('asset_id'),
            'role': row.get('role'),
            'locator': {
                'kind': 'PROVIDER_ASSET_HANDLE' if handle else ('LOCAL_FILE_PATH' if path else 'UNRESOLVED'),
                'value': handle or path,
            },
            'sha256': row.get('sha256'),
            'ingest_status': row.get('ingest_status'),
            'pixel_lock': bool(row.get('pixel_lock')),
            'allowed_transforms': list(row.get('allowed_transforms') or []),
            'identity_features': list(row.get('identity_features') or []),
        })
    renderer = {
        'route': asset.get('production_mode'), 'single_asset_single_canvas': True, 'contact_sheet': False,
        'real_product_master_required': str(asset.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'},
        'source_product_bindings': source_bindings,
        'deterministic_text_composition': bool(locked_copy),
        'text_policy': {
            'exact_copy_mode': 'DETERMINISTIC_COMPOSITION_AFTER_RENDER',
            'image_model_may_rewrite_locked_copy': False, 'image_model_may_retype_packaging': False,
            'visible_copy_present': bool(locked_copy), 'locked_copy': locked_copy,
        },
        'layer_plan': _renderer_layer_plan(card,locked_copy),
        'local_revision_contract': asset.get('editable_layer_contract') or {}
    }
    prompt_cn='\n'.join(_render_lines(card, 'CN')).strip() + '\n'
    prompt_en='\n'.join(_render_lines(card, 'EN')).strip() + '\n'
    consumption_audit=_prompt_consumption_audit(card,prompt_cn,prompt_en)
    qa = {
        'decision_answer_visible': asset.get('incremental_information') or asset.get('belief_target'),
        'product_identity': card['product_identity']['rule'],
        'relevant_parameter_trace_complete': consumption_audit.get('status')=='PASS',
        'same_layout_guard': 'The result must visibly differ from adjacent assets when decision intent/evidence plane differs.',
        'copy_visual_alignment': card['information_design']['copy_visual_rule'], 'surface_native': card.get('surface_contract'),
        'culture_locale': card.get('market_locale'), 'material_truth': card['lighting_material_cmf']['material_truth_rule'],
        'photography_checks': _dynamic_photography_checks(card)
    }
    return {
        'status': 'CANONICAL_PROMPT_COMPILED_EXECUTION_PRESERVING', 'design_card': card,
        'prompt_cn': prompt_cn,
        'prompt_en': prompt_en,
        'deterministic_copy_overlay': locked_copy,
        'parameter_trace': _parameter_trace(card),
        'prompt_consumption_audit': consumption_audit,
        'machine_visual_contract': machine, 'renderer_recipe': renderer, 'qa_target_contract': qa
    }
