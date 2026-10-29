from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping
import re


_INTEGRATED_COPY_MODES={'MODEL_RENDER','HYBRID'}
_HARD_INPUT_STATUSES={
    'REAL_PRODUCT_REFERENCE_INPUT_REQUIRED',
    'COMPLIANCE_INPUT_REQUIRED',
    'PROVIDER_EXECUTION_UNAVAILABLE',
}


def _meaningful(value:Any)->bool:
    if value in (None,'',[],{}): return False
    if isinstance(value,Mapping): return any(_meaningful(v) for v in value.values())
    if isinstance(value,(list,tuple,set,frozenset)): return any(_meaningful(v) for v in value)
    return True


def _first(mapping:Mapping[str,Any]|None,*keys:str)->Any:
    mapping=mapping or {}
    for key in keys:
        value=mapping.get(key)
        if _meaningful(value): return value
    return None


def _text(value:Any)->str:
    if value in (None,'',[],{}): return ''
    if isinstance(value,str): return value.strip()
    if isinstance(value,Mapping):
        for key in ('target_market_copy','target_copy','copy','text','headline','primary','value'):
            if _meaningful(value.get(key)): return _text(value.get(key))
        return '; '.join(f'{k}: {_text(v)}' for k,v in value.items() if _meaningful(v))
    if isinstance(value,(list,tuple,set,frozenset)):
        return ' / '.join(_text(v) for v in value if _meaningful(v))
    return str(value).strip()


def _art(asset:Mapping[str,Any])->dict[str,Any]:
    raw=asset.get('asset_art_direction')
    return deepcopy(dict(raw)) if isinstance(raw,Mapping) else {}


def _copy_block(out:Mapping[str,Any],asset:Mapping[str,Any])->dict[str,Any]:
    raw=out.get('visible_copy_block')
    if isinstance(raw,Mapping): return deepcopy(dict(raw))
    source=asset.get('visible_copy')
    if isinstance(source,Mapping):
        return {
            'target_market_copy':_first(source,'target_market_copy','target_copy','copy','text','headline'),
            'secondary_copy':_first(source,'secondary_copy','subheadline','proof','cta'),
            'delivery_translation_zh':_first(source,'delivery_translation','zh','zh-CN','chinese'),
            'raw':deepcopy(dict(source)),
        }
    return {'target_market_copy':source} if _meaningful(source) else {}


def resolve_copy_render_mode(asset:Mapping[str,Any],out:Mapping[str,Any])->tuple[str,str]:
    """Resolve normal copy rendering autonomously; post-composite is explicit-only."""
    art=_art(asset)
    explicit=_first(art,'copy_render_mode','text_render_mode','visible_copy_render_mode')
    if not explicit:
        explicit=_first(asset,'copy_render_mode','text_render_mode','visible_copy_render_mode')
    if explicit:
        mode=str(explicit).upper()
        if mode in {'MODEL_RENDER','HYBRID','POST_COMPOSITE','NO_VISIBLE_COPY'}:
            return mode,'EXPLICIT_AGENT_OR_PROJECT_DECISION'
    block=_copy_block(out,asset)
    if _meaningful(block.get('target_market_copy')) or _meaningful(block.get('secondary_copy')):
        return 'MODEL_RENDER','AUTONOMOUS_INTEGRATED_RENDER_DEFAULT'
    return 'NO_VISIBLE_COPY','AUTONOMOUS_NO_COPY_FROM_ASSET_CONTENT'


def _strip_legacy_text_suppression(text:str)->str:
    if not text: return text
    replacements=(
        'Preserve the authored typography zone and clean negative space; generate no marketing text inside the image.',
        'Reserve deliberate layout zones for locked copy, but do not ask the image model to retype packaging or final marketing copy. Exact approved text is composed deterministically after generation.',
        '按已设计的信息层级保留清晰文字区和足够负空间；画面中不要生成营销文字。',
        '为锁定文案保留明确排版区，但不要让图像模型重新输入包装文字或最终营销文案；精确批准文案在生成后确定性合成。',
    )
    out=text
    for row in replacements: out=out.replace(row,'')
    patterns=(
        r'Exact approved text is composed deterministically after generation\.?',
        r'generate no marketing text inside the image\.?',
        r'画面中不要生成营销文字。?',
        r'精确批准文案在生成后确定性合成。?',
    )
    for pattern in patterns: out=re.sub(pattern,'',out,flags=re.I)
    return re.sub(r'\n{3,}','\n\n',out).strip()


def _integrated_copy_instruction(block:Mapping[str,Any],language:str,typography:Any=None)->str:
    primary=_text(block.get('target_market_copy'))
    secondary=_text(block.get('secondary_copy'))
    if not primary and not secondary: return ''
    if language=='CN':
        bits=['把批准的市场文案作为最终商业画面的一部分直接排版并清晰生成。']
        if primary: bits.append(f'主文案必须逐字准确出现一次："{primary}"。')
        if secondary: bits.append(f'次级文案必须准确呈现："{secondary}"。')
        if _meaningful(typography): bits.append(f'排版方向：{_text(typography)}。')
        bits.append('文字必须与商品、证据和留白共同构成同一视觉层级；移动端可读；不生成额外营销文字、水印或无关品牌。')
        return ''.join(bits)
    bits=['Render the approved market copy as an integrated part of the finished commercial image. ']
    if primary: bits.append(f'Render this exact primary copy once, verbatim: "{primary}". ')
    if secondary: bits.append(f'Render this exact secondary copy: "{secondary}". ')
    if _meaningful(typography): bits.append(f'Typography direction: {_text(typography)}. ')
    bits.append('Make the text mobile-legible and visually integrated with product, evidence and negative space; add no extra marketing copy, watermarks or unrelated brands.')
    return ''.join(bits)


def _commercial_qa_contract(asset:Mapping[str,Any],out:Mapping[str,Any],copy_mode:str)->dict[str,Any]:
    card=out.get('design_card') or {}
    presence=card.get('product_presence') or {}
    state=str(presence.get('planning_state') or presence.get('state') or '').upper()
    visible_product=state in {'HERO_REQUIRED','REQUIRED','SUPPORTING','DETAIL_ONLY'} or (state=='OPTIONAL' and str(presence.get('production_state') or '').upper()=='PRESENT')
    return {
        'authority':'COMMERCIAL_VISUAL_OUTPUT_QA_V0637',
        'requires_actual_output_inspection':True,
        'checks':[
            {'id':'COMMERCE_FIRST_SCAN','required':True,'question':'Does the first scan communicate the authored decision answer and hierarchy?'},
            {'id':'PRODUCT_IDENTITY','required':bool(visible_product),'question':'Does the rendered product preserve the verified product/package identity, geometry, color and recognizable reference details required by the route?'},
            {'id':'VISIBLE_COPY_ACCURACY','required':copy_mode in _INTEGRATED_COPY_MODES,'question':'Is every required visible-copy string exact, legible, correctly repeated and correctly hierarchical?'},
            {'id':'COMPOSITION_CROP','required':True,'question':'Are composition, scale, crop, focal path and surface safe zones correct?'},
            {'id':'MATERIAL_PHYSICS','required':True,'question':'Are contact shadows, reflections, transparency, surface finish and material behavior plausible for the authored scene?'},
            {'id':'HUMAN_OBJECT_INTEGRITY','required':bool((card.get('subject_action_environment_props') or {}).get('human_context')),'question':'Are anatomy, hands, grip, product interaction and human context believable?'},
            {'id':'EVIDENCE_TRUTH','required':True,'question':'Does the image avoid invented proof, unsupported claims, badges, tests, results or product details?'},
            {'id':'ARTIFACT_SCAN','required':True,'question':'Are there no warped labels/logos, duplicated objects, malformed geometry, stray text or generation artifacts?'},
            {'id':'PORTFOLIO_DELTA','required':True,'question':'Does this asset preserve intentional brand continuity while remaining materially distinct when its decision job differs?'},
            {'id':'PLATFORM_READY','required':True,'question':'Is the final output usable on the selected platform/surface at actual viewing size?'},
        ],
        'repair_routes':['PROMPT_REFINE','REFERENCE_STRENGTHEN','LOCAL_EDIT_OR_MASK','TYPOGRAPHY_REPAIR','CROP_OR_SURFACE_ADAPT','REGENERATE_CANDIDATE','CHANGE_PROVIDER_OR_MODEL','EXPLICIT_POST_COMPOSITE_IF_NOW_JUSTIFIED'],
        'principle':'Provider completion is not a commercial-quality pass. Inspect the actual result and repair the smallest failing layer.',
    }


def apply_commercial_operator_density_authority(bundle:Mapping[str,Any],asset:Mapping[str,Any])->dict[str,Any]:
    out=deepcopy(dict(bundle))
    copy_block=_copy_block(out,asset)
    copy_mode,mode_source=resolve_copy_render_mode(asset,out)
    art=_art(asset)
    typography=_first(art,'typography','typography_direction') or ((out.get('design_card') or {}).get('information_design') or {}).get('typography')

    raw_cn=str(out.get('model_prompt_cn') or out.get('prompt_cn') or '')
    raw_en=str(out.get('model_prompt_en') or out.get('prompt_en') or '')
    # Only integrated modes erase historical no-text instructions. An explicitly selected
    # POST_COMPOSITE route keeps its deliberate no-text/typography-zone instruction intact.
    if copy_mode in _INTEGRATED_COPY_MODES:
        cn=_strip_legacy_text_suppression(raw_cn)
        en=_strip_legacy_text_suppression(raw_en)
        cn_instruction=_integrated_copy_instruction(copy_block,'CN',typography)
        en_instruction=_integrated_copy_instruction(copy_block,'EN',typography)
        primary=_text(copy_block.get('target_market_copy'))
        if cn_instruction and (primary not in cn or '直接排版' not in cn): cn=(cn.rstrip()+'\n'+cn_instruction).strip()
        if en_instruction and (primary not in en or 'integrated part of the finished commercial image' not in en): en=(en.rstrip()+'\n'+en_instruction).strip()
    else:
        cn=raw_cn.strip()
        en=raw_en.strip()
    out['model_prompt_cn']=out['prompt_cn']=cn+'\n' if cn else ''
    out['model_prompt_en']=out['prompt_en']=en+'\n' if en else ''
    out['visible_copy_block']=copy_block

    notes=deepcopy(dict(out.get('production_assembly_notes') or {}))
    notes['copy_render_mode']=copy_mode
    notes['copy_render_mode_source']=mode_source
    notes['integrated_native_generation_default']=True
    notes['post_composite_is_default']=False
    notes['restriction_policy']='Restrictions are exception-only: explicit user lock, truth/evidence, compliance/platform rule, explicit exact-pixel/post-composite route, or material provider limitation.'
    out['production_assembly_notes']=notes

    renderer=deepcopy(dict(out.get('renderer_recipe') or {}))
    renderer.pop('deterministic_text_composition',None)
    renderer['text_policy']={
        'copy_render_mode':copy_mode,
        'selection_source':mode_source,
        'visible_copy_present':bool(_meaningful(copy_block.get('target_market_copy')) or _meaningful(copy_block.get('secondary_copy'))),
        'model_prompt_contains_exact_copy':copy_mode in _INTEGRATED_COPY_MODES,
        'post_composite_explicit_only':True,
        'copy_block_ref':'visible_copy_block',
    }
    renderer['integrated_native_generation_default']=True
    out['renderer_recipe']=renderer

    previous_status=str(out.get('model_prompt_status') or out.get('status') or '')
    if previous_status=='COPY_RENDER_MODE_REQUIRED':
        out['model_prompt_status']='MODEL_NATIVE_PROMPT_READY'
    out['commercial_visual_qa_contract']=_commercial_qa_contract(asset,out,copy_mode)

    hard_status=str(out.get('model_prompt_status') or '') in _HARD_INPUT_STATUSES
    out['operator_release']={
        'release_state':'NEEDS_HARD_INPUT' if hard_status else 'READY_FOR_PRODUCTION_OR_VISUAL_QA',
        'copy_render_mode':copy_mode,
        'copy_render_mode_source':mode_source,
        'integrated_native_generation_default':True,
        'normal_creative_choices_are_operator_gates':False,
        'next_action':'Resolve the explicit hard input before production.' if hard_status else 'Generate the integrated candidate, inspect the actual output with commercial_visual_qa_contract, then release or route the smallest repair.',
    }
    out['commercial_authority']={
        'version':'0.6.37-commercial-operator-density',
        'principle':'Agent creates the complete commercial asset by default. Restrictions are exceptions, not defaults.',
        'copy_mode':copy_mode,
        'copy_mode_source':mode_source,
        'product_presence_rule':'Per-asset Art Direction decides presence. Ecommerce does not imply product in every asset and compositing does not imply product absence.',
    }
    return out


def wrap_compile_asset_prompt(compile_fn):
    def compiled(*args,**kwargs):
        asset=args[0] if args else kwargs.get('asset') or {}
        return apply_commercial_operator_density_authority(compile_fn(*args,**kwargs),asset)
    return compiled
