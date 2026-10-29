from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Mapping

_NATIVE_REFERENCE_FIDELITY={
    'REFERENCE_GUIDED','REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK',
    'NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'
}
_EXACT_PIXEL_COMPOSITE={'EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'}
_VISIBLE_STATES={'HERO_REQUIRED','REQUIRED','SUPPORTING','DETAIL_ONLY'}
_ABSENT_STATES={'FORBIDDEN','ABSENT','NOT_APPLICABLE'}


def _meaningful(v:Any)->bool:
    return v not in (None,'',[],{})


def _presence(card:Mapping[str,Any])->tuple[str,bool]:
    p=card.get('product_presence') or {}
    state=str(p.get('planning_state') or p.get('state') or '').upper()
    prod=str(p.get('production_state') or '').upper()
    visible=state in _VISIBLE_STATES or (state=='OPTIONAL' and prod=='PRESENT')
    return state, visible


def _explicit_exact_pixel(asset:Mapping[str,Any], card:Mapping[str,Any])->bool:
    fidelity=str((card.get('product_identity') or {}).get('product_fidelity') or asset.get('product_fidelity') or '').upper()
    return bool(
        fidelity in _EXACT_PIXEL_COMPOSITE
        or asset.get('exact_pixel_composite') is True
        or asset.get('exact_pixel_layer') is True
        or str(asset.get('source_lock_intent') or '').upper() in _EXACT_PIXEL_COMPOSITE
    )


def normalize_native_reference_fidelity(asset:Mapping[str,Any], card:Mapping[str,Any])->str:
    raw=str((card.get('product_identity') or {}).get('product_fidelity') or asset.get('product_fidelity') or 'REFERENCE_GUIDED').upper()
    if _explicit_exact_pixel(asset,card):
        return 'EXACT_PIXEL_COMPOSITE'
    if raw in _NATIVE_REFERENCE_FIDELITY:
        return 'REFERENCE_GUIDED_NATIVE_LOCK'
    return raw or 'REFERENCE_GUIDED_NATIVE_LOCK'


def _strip_legacy_composite_instruction(text:str)->str:
    if not text:
        return text
    patterns=[
        r'以最终合成画面而不是空背景为目标生成环境底片：.*?同一个空间。',
        r'Generate the environment plate for the final composite, not as an unrelated empty background\..*?same photographed scene\.',
        r'Product is explicitly present and locked-source fidelity is selected\..*?locked layer\.',
    ]
    out=text
    for pattern in patterns:
        out=re.sub(pattern,'',out,flags=re.S)
    return re.sub(r'\n{3,}','\n\n',out).strip()+'\n'


def _native_reference_instruction(language:str, source_count:int)->str:
    if language=='CN':
        return (
            '真实商品参考规则：将提供的真实商品参考图作为当前商品主体的强参考输入，原生生成完整最终画面中的商品；'
            '商品必须真实可见并与环境、人物、道具、光影、景深和透视属于同一生成画面。严格保持商品身份：包装形状与比例、泵头/滴管/瓶盖等结构、Logo、品牌文字、标签排版与可辨识印刷、主色与材质外观不得被替换、改款、重设计或虚构。'
            '允许为了匹配已作者化的机位、透视、光线与场景而进行模型原生重建，但不得把商品变成另一个包装版本。'
            + (f'当前绑定真实商品参考源数量：{source_count}。' if source_count else '生成前必须绑定至少一个真实商品参考源。')
        )
    return (
        'Real-product reference rule: use the supplied real product image(s) as strong subject references and natively render the product inside the complete final image. '
        'The product must be visibly present and generated as part of the same scene, perspective, depth of field, lighting and material interaction as the environment or human context. '
        'Preserve product identity exactly: package geometry and proportions, pump/dropper/cap structure, logo, brand wording, label layout and recognizable print, primary colors and material appearance must not be substituted, redesigned, reformatted or invented. '
        'Native reconstruction is allowed only to match the authored camera, perspective, light and scene while keeping the same real product identity.'
        + (f' Bound real-product reference count: {source_count}.' if source_count else ' At least one real-product reference must be bound before generation.')
    )


def apply_reference_guided_native_authority(bundle:Mapping[str,Any], asset:Mapping[str,Any], source_product_assets:list[dict[str,Any]]|None=None)->dict[str,Any]:
    out=deepcopy(dict(bundle))
    card=deepcopy(dict(out.get('design_card') or {}))
    state,visible=_presence(card)
    exact=_explicit_exact_pixel(asset,card)
    normalized=normalize_native_reference_fidelity(asset,card)
    sources=list(source_product_assets or (card.get('product_identity') or {}).get('source_product_assets') or [])

    identity=deepcopy(dict(card.get('product_identity') or {}))
    identity['product_fidelity']=normalized
    identity['reference_generation_mode']='EXACT_PIXEL_COMPOSITE' if exact else 'REFERENCE_GUIDED_NATIVE_GENERATION'
    if visible and not exact:
        identity['rule']=_native_reference_instruction('EN',len(sources))
        identity['native_subject_required']=True
        identity['reference_input_required']=True
        identity['pixel_copy_required']=False
    elif exact:
        identity['native_subject_required']=False
        identity['reference_input_required']=True
        identity['pixel_copy_required']=True
    card['product_identity']=identity
    out['design_card']=card

    if visible and not exact:
        cn=_strip_legacy_composite_instruction(str(out.get('model_prompt_cn') or out.get('prompt_cn') or ''))
        en=_strip_legacy_composite_instruction(str(out.get('model_prompt_en') or out.get('prompt_en') or ''))
        cn=cn.rstrip()+'\n'+_native_reference_instruction('CN',len(sources))+'\n'
        en=en.rstrip()+'\n'+_native_reference_instruction('EN',len(sources))+'\n'
        out['model_prompt_cn']=out['prompt_cn']=cn
        out['model_prompt_en']=out['prompt_en']=en

    notes=deepcopy(dict(out.get('production_assembly_notes') or {}))
    notes['product_reference_generation_mode']='EXACT_PIXEL_COMPOSITE' if exact else ('REFERENCE_GUIDED_NATIVE_GENERATION' if visible else 'TRUTH_REFERENCE_ONLY')
    notes['reference_input_required']=bool(visible and sources) or exact
    notes['final_output_must_contain_generated_product']=bool(visible and not exact)
    notes['pixel_composite_is_default']=False
    out['production_assembly_notes']=notes

    renderer=deepcopy(dict(out.get('renderer_recipe') or {}))
    renderer['product_generation_mode']=notes['product_reference_generation_mode']
    renderer['reference_input_required']=notes['reference_input_required']
    renderer['final_output_must_contain_generated_product']=notes['final_output_must_contain_generated_product']
    renderer['pixel_composite_required']=bool(exact)
    bindings=[]
    for row in renderer.get('source_product_bindings') or []:
        r=deepcopy(dict(row))
        if visible and not exact:
            r['usage_role']='NATIVE_SUBJECT_REFERENCE'
            r['visible_subject_binding']=True
            r['reference_input_required']=True
            r['pixel_copy_required']=False
            r['native_generation_required']=True
        elif exact:
            r['usage_role']='EXACT_PIXEL_SOURCE_LAYER'
            r['pixel_copy_required']=True
            r['native_generation_required']=False
        bindings.append(r)
    renderer['source_product_bindings']=bindings
    out['renderer_recipe']=renderer

    closure=deepcopy(dict(out.get('production_parameter_closure') or {}))
    closure['product_reference_generation_mode']=notes['product_reference_generation_mode']
    closure['reference_input_count']=len(sources)
    closure['final_product_visibility_required']=bool(visible)
    closure['native_product_generation_required']=bool(visible and not exact)
    closure['exact_pixel_composite_explicit_only']=True
    if visible and not exact:
        closure['locked_source_final_composite_instruction']=False
    if visible and not exact:
        closure['locked_source_final_composite_instruction']=False
    if visible and not exact and not sources:
        missing=list(closure.get('missing_required_parameters') or [])
        if 'real_product_reference_input' not in missing:
            missing.append('real_product_reference_input')
        closure['missing_required_parameters']=missing
        closure['status']='INCOMPLETE'
        closure['model_generation_blocking']=True
        prior=str(out.get('model_prompt_status') or '')
        if prior not in {'BILINGUAL_RENDER_SEMANTICS_REQUIRED','COPY_RENDER_MODE_REQUIRED','AGENT_ART_DIRECTION_REQUIRED','ART_DIRECTION_EXECUTION_DEPTH_REQUIRED'}:
            out['model_prompt_status']='REAL_PRODUCT_REFERENCE_INPUT_REQUIRED'
    out['production_parameter_closure']=closure
    return out


def wrap_compile_asset_prompt(fn):
    def compiled(
        asset:dict[str,Any], product:dict[str,Any], target:dict[str,Any], culture:dict[str,Any],
        language_contract:dict[str,Any], locale_profiles:dict[str,Any]|None=None,
        photography:dict[str,Any]|None=None, strategy_authority:dict[str,Any]|None=None,
        source_product_assets:list[dict[str,Any]]|None=None,
    ):
        bundle=fn(asset,product,target,culture,language_contract,locale_profiles,photography,strategy_authority,source_product_assets)
        return apply_reference_guided_native_authority(bundle,asset,source_product_assets)
    return compiled
