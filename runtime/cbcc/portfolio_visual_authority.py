from __future__ import annotations

import json
import re
from copy import deepcopy
from typing import Any, Mapping

_VISUAL_SURFACES={
    'SEARCH_RESULTS','LISTING_PRIMARY','PDP_HERO','GALLERY','PDP','LONGFORM','A_PLUS','PDP_VIDEO',
    'SHORT_VIDEO','CREATOR','LIVE','PAID_AD','SOCIAL_CONTENT','STORE_BANNER','LANDING_PAGE_HERO',
    'COMPARISON','SPECIFICATION','UGC_BRIEF'
}


def _meaningful(v: Any) -> bool:
    if v in (None,'',[],{}): return False
    if isinstance(v, Mapping): return any(_meaningful(x) for x in v.values())
    if isinstance(v,(list,tuple,set,frozenset)): return any(_meaningful(x) for x in v)
    return True


def _strings(v: Any) -> list[str]:
    if v is None: return []
    if not isinstance(v,(list,tuple,set,frozenset)): v=[v]
    return [str(x) for x in v if str(x or '').strip()]


def _visual_scope(request: Mapping[str,Any]) -> bool:
    if request.get('compile_assets') or request.get('asset_jobs') or request.get('source_product_assets'):
        return True
    target=request.get('target') if isinstance(request.get('target'),Mapping) else {}
    return bool(set(_strings(target.get('surfaces'))) & _VISUAL_SURFACES)


def _agent_authority(plan: Mapping[str,Any]) -> bool:
    authority=plan.get('authority_model') if isinstance(plan.get('authority_model'),Mapping) else {}
    creative=plan.get('creative_exploration') if isinstance(plan.get('creative_exploration'),Mapping) else {}
    return str(authority.get('creative_authority') or creative.get('art_direction_authority') or '').upper()=='HOST_AGENT'


def _raw_agent_plan(request: Mapping[str,Any]) -> dict[str,Any]:
    raw=request.get('agent_plan') or request.get('agent_decisions') or {}
    return dict(raw) if isinstance(raw,Mapping) else {}


def _program_missing(program: Mapping[str,Any] | None) -> list[str]:
    p=program if isinstance(program,Mapping) else {}
    aliases={
        'visual_territory':('visual_territory','perception_territory','creative_territory'),
        'carrier_mix':('carrier_mix','visual_carrier_mix','representation_mix'),
        'product_presence_rhythm':('product_presence_rhythm','presence_rhythm'),
        'scale_density_rhythm':('scale_density_rhythm','scale_rhythm','density_rhythm'),
        'composition_rhythm':('composition_rhythm','spatial_rhythm','composition_grammar_map'),
        'continuity_tokens':('continuity_tokens','continuity_system','shared_tokens'),
        'deliberate_breaks':('deliberate_breaks','rhythm_breaks','breaks'),
        'delete_merge_logic':('delete_merge_logic','asset_omission_logic','merge_delete_decisions'),
        'mechanism_bindings':('mechanism_bindings','technique_bindings','reference_mechanisms'),
    }
    missing=[]
    for label,keys in aliases.items():
        if not any(_meaningful(p.get(k)) for k in keys): missing.append(label)
    return missing


def _review_missing(review: Mapping[str,Any] | None) -> list[str]:
    r=review if isinstance(review,Mapping) else {}
    missing=[]
    if not _meaningful(r.get('status') or r.get('decision')): missing.append('status_or_decision')
    if not _meaningful(r.get('adjacent_asset_review') or r.get('pair_reviews') or r.get('cluster_reviews') or r.get('asset_reviews')):
        missing.append('adjacent_or_cluster_review')
    if not _meaningful(r.get('keep_reauthor_merge_delete') or r.get('actions') or r.get('decisions')):
        missing.append('keep_reauthor_merge_delete_actions')
    return missing


def wrap_compile_agent_autonomy_plan(previous_fn):
    def compiled(request: Mapping[str,Any]) -> dict[str,Any]:
        out=deepcopy(previous_fn(request))
        if not (_visual_scope(request) and _agent_authority(out)):
            return out
        raw=_raw_agent_plan(request)
        creative=dict(out.get('creative_exploration') or {})
        if not creative.get('portfolio_visual_program') and raw.get('portfolio_visual_program'):
            creative['portfolio_visual_program']=deepcopy(raw.get('portfolio_visual_program'))
        if not creative.get('portfolio_differentiation_review') and raw.get('portfolio_differentiation_review'):
            creative['portfolio_differentiation_review']=deepcopy(raw.get('portfolio_differentiation_review'))
        creative['require_portfolio_visual_program']=True
        creative['require_portfolio_differentiation_review']=True
        creative['require_production_parameter_closure']=True
        creative['portfolio_visual_authority']='HOST_AGENT'
        creative['runtime_portfolio_role']='VALIDATE_AND_RETURN_TO_AGENT_ONLY'
        creative['portfolio_visual_program_missing']=_program_missing(creative.get('portfolio_visual_program'))
        creative['portfolio_differentiation_review_missing']=_review_missing(creative.get('portfolio_differentiation_review'))
        out['creative_exploration']=creative

        authority=dict(out.get('authority_model') or {})
        decisions=list(authority.get('agent_decisions') or [])
        for item in (
            'PORTFOLIO_VISUAL_PROGRAM_AND_RHYTHM',
            'PORTFOLIO_VISUAL_DIFFERENTIATION_REVIEW',
            'PRODUCTION_PARAMETER_CLOSURE',
        ):
            if item not in decisions: decisions.append(item)
        authority['agent_decisions']=decisions
        out['authority_model']=authority
        return out
    return compiled


def wrap_agent_creative_directions(previous_fn):
    def compiled(plan: Mapping[str,Any]) -> list[dict[str,Any]]:
        rows=previous_fn(plan)
        creative=plan.get('creative_exploration') if isinstance(plan.get('creative_exploration'),Mapping) else {}
        if not creative.get('require_portfolio_visual_program'):
            return rows
        out=[]
        for raw in rows:
            row=deepcopy(raw)
            row['require_portfolio_visual_program']=True
            row['require_portfolio_differentiation_review']=True
            row['require_production_parameter_closure']=True
            if creative.get('portfolio_visual_program'):
                row['portfolio_visual_program']=deepcopy(creative.get('portfolio_visual_program'))
            if creative.get('portfolio_differentiation_review'):
                row['portfolio_differentiation_review']=deepcopy(creative.get('portfolio_differentiation_review'))
            out.append(row)
        return out
    return compiled


def _norm(v: Any) -> str:
    if not _meaningful(v): return ''
    if isinstance(v, Mapping):
        # Prefer English only to avoid treating the same bilingual content as two different signatures.
        for k in ('en','EN','en-US','cn','zh-CN','zh'):
            if _meaningful(v.get(k)): return _norm(v.get(k))
        v=json.dumps(v,ensure_ascii=False,sort_keys=True)
    elif isinstance(v,(list,tuple,set,frozenset)):
        v=' | '.join(_norm(x) for x in v if _meaningful(x))
    text=str(v).casefold()
    text=re.sub(r'\s+',' ',text).strip()
    return text


def _art(asset: Mapping[str,Any]) -> dict[str,Any]:
    a=asset.get('asset_art_direction')
    return dict(a) if isinstance(a,Mapping) else {}


def _pick(art: Mapping[str,Any], *keys: str) -> Any:
    for k in keys:
        if _meaningful(art.get(k)): return art.get(k)
    return None


def _signature(asset: Mapping[str,Any]) -> tuple[str,...]:
    art=_art(asset)
    presence=art.get('product_presence') if isinstance(art.get('product_presence'),Mapping) else asset.get('product_presence') or {}
    return tuple(_norm(x) for x in (
        _pick(art,'visual_carrier','semantic_carrier'),
        (presence or {}).get('planning_state'),
        (presence or {}).get('product_role') or art.get('product_role'),
        _pick(art,'composition_grammar','spatial_grammar','composition'),
        _pick(art,'layout_geometry','relative_placement','placement_relationships'),
        _pick(art,'scale_depth','scale_relationships','depth_program'),
        _pick(art,'negative_space','copy_negative_space'),
        _pick(art,'camera_or_view','preferred_view'),
        _pick(art,'material_response','surface_behavior'),
    ))


def _delta(asset: Mapping[str,Any]) -> Any:
    art=_art(asset)
    return _pick(art,'deliberate_difference','adjacent_asset_delta','differentiation_axis','portfolio_delta','why_different_from_adjacent')


def validate_portfolio_differentiation(architecture: Mapping[str,Any], selected_direction: Mapping[str,Any] | None=None) -> dict[str,Any]:
    direction=selected_direction if isinstance(selected_direction,Mapping) else {}
    if not direction.get('require_portfolio_differentiation_review'):
        return {'status':'NOT_APPLICABLE','authority':'COMPATIBILITY_MODE'}
    assets=[a for a in (architecture.get('assets') or []) if str(a.get('asset_type') or '').upper() in {'IMAGE','VIDEO'} and str(a.get('art_direction_status') or '').upper()=='AUTHORED']
    issues=[]
    duplicate_groups=[]
    by_sig={}
    for a in assets:
        sig=_signature(a)
        if any(sig): by_sig.setdefault(sig,[]).append(str(a.get('asset_id') or 'UNKNOWN'))
    for ids in by_sig.values():
        if len(ids)>1:
            duplicate_groups.append(ids)
            issues.append({'type':'DUPLICATE_VISUAL_SIGNATURE','asset_ids':ids,'action':'REAUTHOR_OR_JUSTIFY_KEEP'})
    for i,a in enumerate(assets):
        if i==0: continue
        if not _meaningful(_delta(a)):
            issues.append({'type':'MISSING_ADJACENT_ASSET_DELTA','asset_ids':[str(assets[i-1].get('asset_id')),str(a.get('asset_id'))],'action':'AUTHOR_DELTA_OR_REAUTHOR'})
    review=direction.get('portfolio_differentiation_review') if isinstance(direction.get('portfolio_differentiation_review'),Mapping) else {}
    review_missing=_review_missing(review)
    if review_missing:
        issues.append({'type':'MISSING_AGENT_DIFFERENTIATION_REVIEW','missing':review_missing,'action':'AUTHOR_PORTFOLIO_DIFFERENTIATION_REVIEW'})
    return {
        'status':'PASS' if not issues else 'RETURN_TO_AGENT',
        'authority':'RUNTIME_VALIDATION_OF_AGENT_AUTHORED_PORTFOLIO',
        'runtime_may_redesign':False,
        'asset_count_reviewed':len(assets),
        'duplicate_signature_groups':duplicate_groups,
        'issues':issues,
        'principle':'Runtime detects obvious repetition or missing deliberate-difference reasoning; the host Agent decides whether to keep, justify, merge, delete or redesign.',
    }


def wrap_apply_creative_system_to_assets(previous_fn):
    def compiled(architecture: dict[str,Any], council: dict[str,Any], cmf: dict[str,Any] | None=None, photography: dict[str,Any] | None=None) -> dict[str,Any]:
        out=deepcopy(previous_fn(architecture,council,cmf,photography))
        selected=(council or {}).get('selected_direction') or {}
        validation=validate_portfolio_differentiation(out,selected)
        assignment=dict(out.get('creative_system_assignment') or {})
        assignment['portfolio_visual_program']=deepcopy(selected.get('portfolio_visual_program') or {})
        assignment['portfolio_differentiation_review']=deepcopy(selected.get('portfolio_differentiation_review') or {})
        assignment['portfolio_differentiation_validation']=validation
        out['creative_system_assignment']=assignment
        return out
    return compiled


def _add_blocker(result: dict[str,Any], item: dict[str,Any]) -> None:
    blocking=list(result.get('blocking_frontier') or [])
    if not any(x.get('action')==item.get('action') for x in blocking): blocking.insert(0,item)
    result['blocking_frontier']=blocking
    result['advisory_frontier']=[x for x in (result.get('advisory_frontier') or []) if x.get('action')!=item.get('action')]
    result['frontier']=blocking+list(result.get('advisory_frontier') or [])
    result['blocking_frontier_count']=len(blocking)
    result['advisory_frontier_count']=len(result.get('advisory_frontier') or [])
    result['status']='ACTION_FRONTIER_OPEN'
    result['recommended_next_action']=blocking[0].get('action')


def wrap_compile_agent_next_action(previous_fn):
    def compiled(plan: Mapping[str,Any], **kwargs) -> dict[str,Any]:
        result=deepcopy(previous_fn(plan,**kwargs))
        creative=plan.get('creative_exploration') if isinstance(plan.get('creative_exploration'),Mapping) else {}
        if not creative.get('require_portfolio_visual_program'):
            return result
        program_missing=_program_missing(creative.get('portfolio_visual_program'))
        review_missing=_review_missing(creative.get('portfolio_differentiation_review'))
        if program_missing:
            _add_blocker(result,{
                'action':'AUTHOR_PORTFOLIO_VISUAL_PROGRAM',
                'reason':'Agent-authority visual work requires a portfolio-level carrier/presence/scale/composition rhythm and deliberate breaks before per-asset production.',
                'missing':program_missing,'blocking':True,
            })
        if review_missing:
            _add_blocker(result,{
                'action':'REVIEW_PORTFOLIO_VISUAL_DIFFERENTIATION',
                'reason':'The portfolio requires an explicit adjacent/cluster review with keep/re-author/merge/delete decisions; platform capacity is not an asset quota.',
                'missing':review_missing,'blocking':True,
            })
        architecture=kwargs.get('asset_architecture') if isinstance(kwargs.get('asset_architecture'),Mapping) else {}
        validation=((architecture.get('creative_system_assignment') or {}).get('portfolio_differentiation_validation') or {}) if isinstance(architecture,Mapping) else {}
        if str(validation.get('status') or '').upper()=='RETURN_TO_AGENT':
            _add_blocker(result,{
                'action':'REAUTHOR_PORTFOLIO_VISUAL_DIFFERENTIATION',
                'reason':'Runtime validation found repeated visual signatures or missing adjacent-asset delta. Runtime may not redesign; return the flagged assets to the Agent.',
                'issues':deepcopy(validation.get('issues') or []),'blocking':True,
            })
        result['portfolio_visual_authority']='HOST_AGENT'
        return result
    return compiled
