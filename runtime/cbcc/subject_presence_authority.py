from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable
import json

SUBJECT_TYPES = {
    'PERSON', 'ANIMAL', 'PLANT', 'PRODUCT_OR_OBJECT', 'ENVIRONMENT', 'MULTI_SUBJECT', 'NONE', 'UNRESOLVED'
}


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _nonempty(value: Any) -> bool:
    return value not in (None, '', [], {})


def normalize_subject_system(asset: dict[str, Any]) -> dict[str, Any]:
    """Normalize only explicit subject decisions; never infer a living subject from category/product type."""
    asset = _dict(asset)
    art = _dict(asset.get('asset_art_direction'))
    explicit = _dict(art.get('subject_system') or asset.get('subject_system'))
    if explicit:
        out = deepcopy(explicit)
        st = str(out.get('subject_type') or 'UNRESOLVED').upper()
        out['subject_type'] = st if st in SUBJECT_TYPES else 'UNRESOLVED'
        out.setdefault('authority', 'HOST_AGENT_AUTHORED')
        out.setdefault('living_subject_required', out['subject_type'] in {'PERSON', 'ANIMAL', 'MULTI_SUBJECT'})
        out.setdefault('principle', 'Subject choice is per-asset and task-led; person/animal/plant/object/environment/none are all valid when authored.')
        return out

    # Backward compatibility only. These legacy fields prove an explicit prior decision; they do not create a default.
    legacy_human = art.get('human_context') or art.get('people') or art.get('casting')
    if _nonempty(legacy_human):
        return {
            'subject_type': 'PERSON',
            'primary_subject': legacy_human,
            'living_subject_required': True,
            'authority': 'LEGACY_EXPLICIT_DECISION_MIGRATED',
            'migration_source': 'LEGACY_HUMAN_CONTEXT',
            'principle': 'Migrated from an explicit legacy human field; this does not establish PERSON as a global default.',
        }
    legacy_animal = art.get('animal_context') or art.get('pet_context') or asset.get('animal_context')
    if _nonempty(legacy_animal):
        return {
            'subject_type': 'ANIMAL', 'primary_subject': legacy_animal, 'living_subject_required': True,
            'authority': 'LEGACY_EXPLICIT_DECISION_MIGRATED', 'migration_source': 'LEGACY_ANIMAL_CONTEXT',
        }
    legacy_plant = art.get('plant_context') or art.get('botanical_context') or asset.get('plant_context')
    if _nonempty(legacy_plant):
        return {
            'subject_type': 'PLANT', 'primary_subject': legacy_plant, 'living_subject_required': False,
            'authority': 'LEGACY_EXPLICIT_DECISION_MIGRATED', 'migration_source': 'LEGACY_PLANT_CONTEXT',
        }

    # Do not infer PRODUCT_ONLY either. The Agent may deliberately choose environment-led or no-subject evidence work.
    return {
        'subject_type': 'UNRESOLVED',
        'primary_subject': None,
        'living_subject_required': False,
        'authority': 'AGENT_DECISION_REQUIRED_WHEN_SUBJECT_IS_RELEVANT',
        'principle': 'No person/animal/plant/object subject is implied. The Agent may author PERSON, ANIMAL, PLANT, PRODUCT_OR_OBJECT, ENVIRONMENT, MULTI_SUBJECT or NONE per asset.',
    }


def _prompt_lines(subject: dict[str, Any], cn: bool) -> list[str]:
    title = '【主体系统】' if cn else '[SUBJECT SYSTEM]'
    labels = {
        'type': '主体类型：' if cn else 'Subject type: ',
        'primary': '主主体：' if cn else 'Primary subject: ',
        'secondary': '次主体：' if cn else 'Secondary subjects: ',
        'action': '主体动作：' if cn else 'Subject action: ',
        'product': '主体与商品关系：' if cn else 'Subject-product relationship: ',
        'scene': '主体与场景关系：' if cn else 'Subject-scene relationship: ',
        'casting': '选角/物种/品种/形态约束：' if cn else 'Casting/species/variety/form constraints: ',
    }
    lines = [title, labels['type'] + str(subject.get('subject_type') or 'UNRESOLVED')]
    mapping = [
        ('primary_subject', 'primary'), ('secondary_subjects', 'secondary'), ('action', 'action'),
        ('subject_product_relationship', 'product'), ('subject_scene_relationship', 'scene'),
        ('subject_constraints', 'casting'),
    ]
    for key, label in mapping:
        value = subject.get(key)
        if _nonempty(value):
            rendered = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
            lines.append(labels[label] + rendered)
    if str(subject.get('subject_type') or '').upper() == 'NONE':
        lines.append('本资产明确不使用人物、动物或植物主体；由商品、证据、环境或信息关系承担视觉任务。' if cn else 'This asset explicitly uses no person, animal or plant subject; product, evidence, environment or information relationships carry the visual job.')
    elif str(subject.get('subject_type') or '').upper() == 'UNRESOLVED':
        lines.append('主体只有在当前购买任务确实需要时才补决策；不得默认加人物。' if cn else 'Resolve a subject only when the purchase task needs one; never add a person by default.')
    return lines


def wrap_compile_asset_prompt(fn: Callable[..., dict[str, Any]]):
    """Add the explicit subject decision to Design Card and prompts without replacing existing camera/light/CMF content."""
    def compiled(*args, **kwargs):
        raw_asset = kwargs.get('asset') if 'asset' in kwargs else (args[0] if args else {})
        asset = deepcopy(raw_asset or {})
        subject = normalize_subject_system(asset)
        asset['subject_system'] = deepcopy(subject)
        art = asset.get('asset_art_direction')
        if isinstance(art, dict):
            art = deepcopy(art)
            art['subject_system'] = deepcopy(subject)
            asset['asset_art_direction'] = art

        call_args = list(args)
        if call_args:
            call_args[0] = asset
            out = fn(*call_args, **kwargs)
        else:
            call_kwargs = dict(kwargs)
            call_kwargs['asset'] = asset
            out = fn(**call_kwargs)

        card = out.setdefault('design_card', {})
        card['subject_system'] = deepcopy(subject)

        cn = str(out.get('model_prompt_cn') or out.get('prompt_cn') or '').rstrip()
        en = str(out.get('model_prompt_en') or out.get('prompt_en') or '').rstrip()
        if '【主体系统】' not in cn:
            cn = (cn + '\n\n' + '\n'.join(_prompt_lines(subject, True))).strip() + '\n'
        if '[SUBJECT SYSTEM]' not in en:
            en = (en + '\n\n' + '\n'.join(_prompt_lines(subject, False))).strip() + '\n'
        out['prompt_cn'] = out['model_prompt_cn'] = cn
        out['prompt_en'] = out['model_prompt_en'] = en
        return out
    return compiled
