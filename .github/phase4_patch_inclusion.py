from pathlib import Path

creative_path = Path('runtime/cbcc/creative.py')
creative = creative_path.read_text(encoding='utf-8')
if 'from copy import deepcopy' not in creative:
    creative = creative.replace('from typing import Any\n', 'from typing import Any\nfrom copy import deepcopy\n', 1)

start = creative.index('def compile_inclusive_photography(')
replacement = r'''HUMAN_INCLUSION_EXECUTION_FIELDS = (
    'casting_role',
    'age_context',
    'skin_tone',
    'hair_texture_style',
    'grooming_makeup',
    'wardrobe_accessories',
    'body_age_disability_representation',
    'religious_cultural_presentation',
    'pose',
    'expression',
    'gaze',
    'hands',
    'product_interaction',
    'stereotype_guard',
    'ai_bias_review',
    'exposure_lighting_handling',
)


def _human_asset_activation(asset:dict[str,Any])->dict[str,Any]|None:
    art=asset.get('asset_art_direction') or {}
    subject=art.get('subject_system') or asset.get('subject_system') or {}
    subject_type=str(subject.get('subject_type') or '').upper() if isinstance(subject,dict) else ''
    human_context=art.get('human_context') or asset.get('human_context')
    if subject_type=='PERSON':
        return {'asset_id':asset.get('asset_id'),'reason':'EXPLICIT_PERSON_SUBJECT','subject_type':subject_type}
    if isinstance(human_context,dict) and human_context:
        return {'asset_id':asset.get('asset_id'),'reason':'AUTHORED_HUMAN_CONTEXT','subject_type':subject_type or None}
    if art.get('people') or art.get('casting'):
        return {'asset_id':asset.get('asset_id'),'reason':'EXPLICIT_HUMAN_ART_DIRECTION','subject_type':subject_type or None}
    intent=str(asset.get('decision_intent') or '').upper()
    route=str((asset.get('creative_direction') or {}).get('route') or '').upper()
    sig=asset.get('visual_production_signature') or {}
    context=' '.join(str(sig.get(k) or '') for k in ['context_role','visual_job','camera_or_view']).lower()
    human_intents={'RELEVANCE','USAGE','FIT_WEAR','SIZE_FIT','SENSORY_PREP'}
    if intent in human_intents or 'HUMAN_CONTEXT' in route or any(x in context for x in ['human','hand','body','wear','use context','routine']):
        return {'asset_id':asset.get('asset_id'),'reason':'HUMAN_ROUTE_OR_DECISION_JOB','intent':intent,'route':route,'context_role':sig.get('context_role')}
    return None


def _culture_source_refs(culture:dict[str,Any])->list[str]:
    refs=[]
    for row in culture.get('statements') or []:
        if isinstance(row,dict):
            refs.extend(str(x) for x in row.get('source_ids') or [] if x)
    race=culture.get('race_ethnicity') or {}
    if isinstance(race,dict):
        refs.extend(str(x) for x in race.get('source_ids') or [] if x)
    return list(dict.fromkeys(refs))


def compile_inclusive_photography(culture:dict[str,Any], photography:dict[str,Any]|None, assets:list[dict[str,Any]]|None=None)->dict[str,Any]:
    photo=photography or {}; human=photo.get('human') or {}; casting=culture.get('casting_constraints',{}) or {}; inter=culture.get('intersectionality',{}) or {}
    activation_rows=[]
    for asset in assets or []:
        activation=_human_asset_activation(asset)
        if activation:
            activation_rows.append(activation)
    human_required=bool(activation_rows)
    present=bool(human.get('present') or casting or human_required)
    skin=human.get('skin_tone_exposure') or ({
        'metering':'Meter skin and product/label separately; protect highlights and retain shadow chroma/detail.',
        'deep_skin_bracket':'Use neutral reference and test +0.3 / +0.7 EV brackets only as starting comparisons when needed; choose final exposure by truthful skin tone, highlight protection and product readability.',
        'reflector':'Use neutral white/soft fill to recover shadow detail; avoid tiny hard silver sources that create artificial hotspots unless the scene deliberately needs that texture.',
        'diffusion':'Large diffusion close enough to create broad tonal transitions; add negative fill for form rather than underexposing deep skin.',
        'post':'No automatic whitening, skin-tone homogenization or texture erasure.'
    } if present else {})
    hair={
        'hair':(casting.get('hair') if isinstance(casting,dict) else None) or ('Preserve real straight/wavy/curly/coily/protective style texture; use edge separation for dark hair instead of changing texture.' if present else None),
        'wardrobe':(casting.get('wardrobe') if isinstance(casting,dict) else None) or ('Choose wardrobe from product task, locale and scene; do not use ethnicity as costume.' if present else None),
        'makeup':(casting.get('makeup') if isinstance(casting,dict) else None) or ('Keep real skin texture/tone; makeup supports the scene and product, not whitening/youthifying.' if present else None),
    }
    body_age_disability=({'rule':'Represent age/body/disability naturally when relevant to the target/use case; do not erase mobility aids, age markers or body diversity in generation/retouching.','casting_boundary':'No tokenistic or inspirational framing; the person exists to perform the real decision/use task.'} if present else {})
    ai_bias_controls=(['no default whitening','no slimming/body reshaping','no youthifying','no hair-texture homogenization','no disability erasure','check hands/assistive devices/hair edges/body proportions'] if present else [])
    representation_principle='Represent the approved audience context without using identity dimensions as automatic behavior predictions.'
    p0_rule='If people/hands/body relation appear in any asset, inclusive photography and AI-bias QA are P0 production requirements.'
    source_refs=_culture_source_refs(culture)
    activation_by_id={row.get('asset_id'):row for row in activation_rows if row.get('asset_id')}
    asset_execution=[]
    for asset in assets or []:
        aid=asset.get('asset_id')
        activation=activation_by_id.get(aid)
        if not activation:
            continue
        art=asset.get('asset_art_direction') or {}
        raw_context=art.get('human_context') or asset.get('human_context') or {}
        human_context=deepcopy(raw_context) if isinstance(raw_context,dict) else {'authored_context':raw_context}
        missing=[key for key in HUMAN_INCLUSION_EXECUTION_FIELDS if human_context.get(key) in (None,'',[],{})]
        row={
            'asset_id':aid,
            'status':'READY' if not missing else 'TO_VERIFY',
            'authority':'INCLUSIVE_PHOTOGRAPHY_AUTHORITY',
            'activation_basis':deepcopy(activation),
            'human_context':human_context,
            'missing_authored_decisions':missing,
            'casting_constraints':deepcopy(casting),
            'intersectionality_context':deepcopy(inter),
            'skin_tone_exposure':deepcopy(skin),
            'hair_and_styling':deepcopy(hair),
            'body_age_disability':deepcopy(body_age_disability),
            'ai_bias_controls':deepcopy(ai_bias_controls),
            'representation_principle':representation_principle,
            'behavior_inference_allowed':False,
            'runtime_may_invent_missing_identity_or_culture':False,
            'source_refs':deepcopy(source_refs),
            'scene_relevance':{
                'scene':art.get('scene') or art.get('environment'),
                'subject':art.get('subject') or (art.get('subject_system') or {}).get('primary_subject') if isinstance(art.get('subject_system') or {},dict) else art.get('subject'),
                'action':art.get('action') or art.get('decisive_action') or art.get('decisive_moment'),
                'product_interaction':human_context.get('product_interaction'),
                'lighting':deepcopy(art.get('lighting')),
            },
            'review_required':True,
            'p0_rule':p0_rule,
        }
        asset_execution.append(row)
    return {
        'status':'APPLICABLE_P0' if present else 'NOT_APPLICABLE_NO_HUMAN_ASSET',
        'activation_basis':activation_rows,
        'casting':casting,
        'intersectionality_context':inter,
        'skin_tone_exposure':skin,
        'hair_and_styling':hair,
        'body_age_disability':body_age_disability,
        'ai_bias_controls':ai_bias_controls,
        'representation_principle':representation_principle,
        'behavior_inference_allowed':False,
        'runtime_may_invent_missing_identity_or_culture':False,
        'source_refs':source_refs,
        'asset_execution':asset_execution,
        'review_required':present,
        'p0_rule':p0_rule,
    }


def apply_inclusive_photography_to_assets(architecture:dict[str,Any], inclusive:dict[str,Any])->dict[str,Any]:
    """Project the already-compiled inclusion authority into relevant assets without redesigning them."""
    out=deepcopy(architecture or {})
    rows={row.get('asset_id'):row for row in inclusive.get('asset_execution') or [] if isinstance(row,dict) and row.get('asset_id')}
    assets=[]
    for asset in out.get('assets') or []:
        a=deepcopy(asset)
        row=rows.get(a.get('asset_id'))
        if row:
            a['inclusive_photography']=deepcopy(row)
            art=a.get('asset_art_direction')
            if isinstance(art,dict):
                art=deepcopy(art)
                art['inclusive_photography']=deepcopy(row)
                a['asset_art_direction']=art
        assets.append(a)
    out['assets']=assets
    out['inclusive_photography_execution']={
        'authority':'INCLUSIVE_PHOTOGRAPHY_AUTHORITY',
        'asset_ids':list(rows),
        'ready_count':sum(1 for row in rows.values() if row.get('status')=='READY'),
        'to_verify_count':sum(1 for row in rows.values() if row.get('status')=='TO_VERIFY'),
        'runtime_may_invent_missing_identity_or_culture':False,
    }
    return out
'''
creative = creative[:start] + replacement
creative_path.write_text(creative, encoding='utf-8')

compiler_path = Path('runtime/cbcc/compiler.py')
compiler = compiler_path.read_text(encoding='utf-8')
old_import = 'from .creative import compile_curation,compile_creative_council,compile_cmf,compile_inclusive_photography,apply_creative_system_to_assets'
new_import = 'from .creative import compile_curation,compile_creative_council,compile_cmf,compile_inclusive_photography,apply_creative_system_to_assets,apply_inclusive_photography_to_assets'
if old_import in compiler:
    compiler = compiler.replace(old_import, new_import, 1)
elif 'apply_inclusive_photography_to_assets' not in compiler.split('\n', 40)[0:40]:
    raise SystemExit('creative import shape changed; refusing blind patch')
needle = "inclusive=compile_inclusive_photography(culture,request.get('photography_contract'),architecture.get('assets') or [])"
pos = compiler.rfind(needle)
if pos < 0:
    raise SystemExit('second inclusive compile call not found')
insert_at = pos + len(needle)
projection = "\n    architecture=apply_inclusive_photography_to_assets(architecture,inclusive)"
if projection.strip() not in compiler[pos:pos+len(needle)+300]:
    compiler = compiler[:insert_at] + projection + compiler[insert_at:]
compiler_path.write_text(compiler, encoding='utf-8')
