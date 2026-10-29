from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from .subject_presence_authority import normalize_subject_system


def wrap_compile_agent_autonomy_plan(fn: Callable[..., dict[str, Any]]):
    def compiled(request):
        out = fn(request)
        authority = dict(out.get('authority_model') or {})
        decisions = list(authority.get('agent_decisions') or [])
        if 'SUBJECT_PRESENCE_SYSTEM' not in decisions:
            decisions.append('SUBJECT_PRESENCE_SYSTEM')
        authority['agent_decisions'] = decisions
        authority['subject_presence_authority'] = 'HOST_AGENT_PER_ASSET'
        authority['subject_default'] = 'NONE; NO PERSON/ANIMAL/PLANT IS IMPLIED'
        out['authority_model'] = authority
        creative = dict(out.get('creative_exploration') or {})
        creative['subject_presence_contract'] = {
            'allowed_types': ['PERSON', 'ANIMAL', 'PLANT', 'PRODUCT_OR_OBJECT', 'ENVIRONMENT', 'MULTI_SUBJECT', 'NONE'],
            'default_type': None,
            'decision_level': 'PER_ASSET',
            'rule': 'Choose the subject only when it helps the current purchase decision. Pet products may be animal-led; plant/garden products may be plant-led; product/evidence/environment-led work may use no living subject.',
        }
        out['creative_exploration'] = creative
        return out
    return compiled


def wrap_apply_creative_system_to_assets(fn: Callable[..., dict[str, Any]]):
    def compiled(*args, **kwargs):
        out = fn(*args, **kwargs)
        unresolved = []
        for asset in out.get('assets') or []:
            if not isinstance(asset, dict):
                continue
            subject = normalize_subject_system(asset)
            asset['subject_system'] = deepcopy(subject)
            art = asset.get('asset_art_direction')
            if isinstance(art, dict):
                art.setdefault('subject_system', deepcopy(subject))
            if subject.get('subject_type') == 'UNRESOLVED':
                unresolved.append(asset.get('asset_id'))
        out['subject_presence_summary'] = {
            'status': 'SUBJECT_SYSTEM_AUTHORED_OR_EXPLICITLY_UNRESOLVED',
            'unresolved_asset_ids': [x for x in unresolved if x],
            'rule': 'UNRESOLVED does not mean add a person. It means the Agent has not yet chosen whether a subject is relevant; NONE is a valid authored outcome.',
        }
        return out
    return compiled
