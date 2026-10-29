from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any, Mapping

from . import model_native_prompt_contract as native


def _contains(text: str, value: Any) -> bool:
    if not native._meaningful(value):
        return True
    if isinstance(value, Mapping):
        return all(_contains(text, v) for v in value.values() if native._meaningful(v))
    if isinstance(value, (list, tuple)):
        return all(_contains(text, v) for v in value if native._meaningful(v))
    return str(value).strip() in text


def _check(name: str, value: Any, target: str, projected: bool, *, language: str | None = None, required: bool = True) -> dict[str, Any]:
    row={
        'decision': name,
        'selected_value': deepcopy(value),
        'projection_target': target,
        'projected': bool(projected),
        'required': bool(required),
    }
    if language:
        row['language']=language
    return row


def _corrected_audit(asset: Mapping[str, Any], out: Mapping[str, Any]) -> dict[str, Any]:
    card=out.get('design_card') or {}
    prompt_cn=str(out.get('model_prompt_cn') or out.get('prompt_cn') or '')
    prompt_en=str(out.get('model_prompt_en') or out.get('prompt_en') or '')
    copy_block=out.get('visible_copy_block') or {}
    notes=out.get('production_assembly_notes') or {}
    notes_text=json.dumps(notes,ensure_ascii=False,sort_keys=True)
    copy_text=json.dumps(copy_block,ensure_ascii=False,sort_keys=True)
    copy_mode=str(notes.get('copy_render_mode') or '')

    fields_cn, missing_cn=native._model_fields(asset,card,'CN')
    fields_en, missing_en=native._model_fields(asset,card,'EN')
    checks=[]

    # A bilingual authored decision is audited per language, not by demanding both languages in one prompt.
    all_keys=[]
    for key in list(fields_cn)+list(fields_en):
        if key not in all_keys:
            all_keys.append(key)
    for key in all_keys:
        cn=fields_cn.get(key)
        en=fields_en.get(key)
        if native._meaningful(cn):
            checks.append(_check(key,cn,'MODEL_PROMPT_CN',_contains(prompt_cn,cn),language='CN'))
        if native._meaningful(en):
            checks.append(_check(key,en,'MODEL_PROMPT_EN',_contains(prompt_en,en),language='EN'))

    presence=card.get('product_presence') or {}
    if native._meaningful(presence):
        state=str(presence.get('planning_state') or '').upper()
        note_ok=_contains(notes_text,presence)
        if state in {'FORBIDDEN','ABSENT','NOT_APPLICABLE'}:
            model_ok=('must not appear in frame' in prompt_en or 'intentionally absent' in prompt_en) and ('不出现在画面' in prompt_cn or '不出现' in prompt_cn)
        else:
            model_ok=(not state) or state in prompt_en or state in prompt_cn
        checks.append(_check('product_presence',presence,'MODEL_PROMPT+PRODUCTION_NOTES',model_ok and note_ok))

    target_copy=copy_block.get('target_market_copy')
    secondary_copy=copy_block.get('secondary_copy')
    delivery_zh=copy_block.get('delivery_translation_zh')
    if native._meaningful(target_copy):
        if copy_mode in {'MODEL_RENDER','HYBRID'}:
            checks.append(_check('visible_copy.target_market_copy',target_copy,'MODEL_PROMPT',_contains(prompt_en,target_copy) or _contains(prompt_cn,target_copy)))
        elif copy_mode=='POST_COMPOSITE':
            checks.append(_check('visible_copy.target_market_copy',target_copy,'VISIBLE_COPY_BLOCK+PRODUCTION_NOTES',_contains(copy_text,target_copy) and _contains(notes_text,target_copy)))
        elif copy_mode=='UNRESOLVED_AGENT_DECISION':
            checks.append(_check('copy_render_mode',copy_mode,'AGENT_DECISION',False))
    if native._meaningful(secondary_copy):
        target='MODEL_PROMPT' if copy_mode in {'MODEL_RENDER','HYBRID'} else 'VISIBLE_COPY_BLOCK+PRODUCTION_NOTES'
        projected=(_contains(prompt_en,secondary_copy) or _contains(prompt_cn,secondary_copy)) if target=='MODEL_PROMPT' else (_contains(copy_text,secondary_copy) and _contains(notes_text,secondary_copy))
        checks.append(_check('visible_copy.secondary_copy',secondary_copy,target,projected))
    if native._meaningful(delivery_zh):
        # Chinese delivery translation belongs to the human/copy object, never to the EN model prompt.
        checks.append(_check('visible_copy.delivery_translation_zh',delivery_zh,'VISIBLE_COPY_BLOCK',_contains(copy_text,delivery_zh) and delivery_zh not in prompt_en))
    if native._meaningful(target_copy) or native._meaningful(secondary_copy):
        checks.append(_check('copy_render_mode',copy_mode,'PRODUCTION_NOTES',copy_mode in {'MODEL_RENDER','POST_COMPOSITE','HYBRID'} and _contains(notes_text,copy_mode)))

    art=native._art(asset)
    for key in ('source_reference_role','production_route','fidelity','editable_layers','frozen_layers'):
        value=native._first(art,key)
        if native._meaningful(value):
            checks.append(_check(key,value,'PRODUCTION_NOTES',_contains(notes_text,value)))

    english_pure=not bool(native._CJK_RE.search(prompt_en))
    jargon=[term for term in native._ENGINEERING_JARGON if term in prompt_en.casefold() or term in prompt_cn.casefold()]
    checks.append(_check('english_model_prompt_language_purity','NO_CJK_IN_EN_MODEL_INSTRUCTIONS','MODEL_PROMPT_EN',english_pure))
    checks.append(_check('model_prompt_engineering_jargon_separation','NO_RUNTIME_ASSEMBLY_JARGON_IN_MODEL_PROMPT','MODEL_PROMPT_CN+EN',not jargon))
    checks[-1]['found']=jargon

    # _model_fields reports Chinese prose that cannot be safely projected to EN. Keep those as explicit
    # upstream bilingual semantic gaps, but do not treat Chinese delivery translations as such.
    language_missing=[]
    for item in missing_en:
        if item not in language_missing:
            language_missing.append(item)

    missing=[row['decision'] for row in checks if row.get('required',True) and not row.get('projected')]
    missing.extend(language_missing)
    missing=list(dict.fromkeys(missing))
    return {
        'status':'PASS' if not missing else 'INCOMPLETE',
        'authority':'MODEL_NATIVE_PROMPT_CONSUMPTION_V2',
        'principle':'Audit concrete values in their correct language and production object. Chinese delivery translation is not an English-model parameter; bilingual Art Direction is checked CN→CN prompt and EN→EN prompt.',
        'checks':checks,
        'missing_decisions':missing,
        'english_language_pure':english_pure,
        'engineering_jargon_in_model_prompt':jargon,
        'language_semantics_missing_for_en':language_missing,
    }


def _readiness(audit: Mapping[str, Any], prior: str | None) -> str:
    missing=list(audit.get('missing_decisions') or [])
    if not missing:
        return 'MODEL_NATIVE_PROMPT_READY'
    if 'copy_render_mode' in missing:
        return 'COPY_RENDER_MODE_REQUIRED'
    core=('visual_objective','subject','action','environment','composition','creative_thesis','visual_language','visual_carrier','decisive_moment')
    if any(str(item).startswith(core) for item in missing) or audit.get('language_semantics_missing_for_en'):
        return 'BILINGUAL_RENDER_SEMANTICS_REQUIRED'
    if prior=='AGENT_ART_DIRECTION_REQUIRED':
        return prior
    return 'MODEL_PROMPT_NEEDS_AGENT_DECISIONS'


def apply_corrected_audit(out: Mapping[str, Any], asset: Mapping[str, Any]) -> dict[str, Any]:
    result=deepcopy(dict(out))
    audit=_corrected_audit(asset,result)
    result['prompt_consumption_audit']=audit
    result['status']=_readiness(audit,str(result.get('status') or ''))
    return result


def wrap_compile_asset_prompt(compile_fn):
    def compiled(
        asset: dict[str, Any],
        product: dict[str, Any],
        target: dict[str, Any],
        culture: dict[str, Any],
        language_contract: dict[str, Any],
        locale_profiles: dict[str, Any] | None = None,
        photography: dict[str, Any] | None = None,
        strategy_authority: dict[str, Any] | None = None,
        source_product_assets: list[dict[str, Any]] | None = None,
    ):
        out=compile_fn(asset,product,target,culture,language_contract,locale_profiles,photography,strategy_authority,source_product_assets)
        return apply_corrected_audit(out,asset)
    return compiled
