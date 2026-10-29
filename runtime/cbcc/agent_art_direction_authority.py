from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def _rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, Mapping):
        rows=[]
        for key,val in value.items():
            if isinstance(val, Mapping):
                row=dict(val)
                row.setdefault('asset_id', str(key))
                rows.append(row)
        return rows
    return [dict(row) for row in (value or []) if isinstance(row, Mapping)]


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple, set, frozenset)):
        value=[value]
    return [str(x) for x in value if str(x or '').strip()]


def _visual_scope(request: Mapping[str, Any]) -> bool:
    if request.get('compile_assets') or request.get('asset_jobs') or request.get('source_product_assets'):
        return True
    target=request.get('target') if isinstance(request.get('target'), Mapping) else {}
    visual_surfaces={
        'SEARCH_RESULTS','LISTING_PRIMARY','PDP_HERO','GALLERY','PDP','LONGFORM','A_PLUS','PDP_VIDEO',
        'SHORT_VIDEO','CREATOR','LIVE','PAID_AD','SOCIAL_CONTENT','STORE_BANNER','LANDING_PAGE_HERO',
        'COMPARISON','SPECIFICATION','UGC_BRIEF'
    }
    return bool(set(_strings(target.get('surfaces'))) & visual_surfaces)


def wrap_compile_agent_autonomy_plan(legacy_fn):
    def compiled(request: Mapping[str, Any]) -> dict[str, Any]:
        plan=legacy_fn(request)
        out=deepcopy(plan)
        authority=dict(out.get('authority_model') or {})
        decisions=list(authority.get('agent_decisions') or [])
        for item in [
            'PORTFOLIO_CURATION_AND_ASSET_OMISSION',
            'PER_ASSET_ART_DIRECTION',
            'PRODUCT_PRESENCE_AND_PRODUCT_ROLE',
            'VISUAL_CARRIER_AND_INFORMATION_REPRESENTATION',
            'SUBJECT_ACTION_ENVIRONMENT_PROPS',
            'SPATIAL_GRAMMAR_SCALE_FOCAL_PATH',
            'EVIDENCE_HIERARCHY_AND_NEGATIVE_SPACE',
        ]:
            if item not in decisions:
                decisions.append(item)
        authority['agent_decisions']=decisions
        authority['creative_authority']='HOST_AGENT'
        authority['runtime_creative_role']='VALIDATE_SERIALIZE_COMPILE_EXECUTE_ONLY'
        authority['missing_decision_behavior']='RETURN_TO_AGENT; DO_NOT INVENT PRODUCT PRESENCE, SUBJECT, COMPOSITION, CAMERA, LIGHTING, CMF OR LAYOUT'
        out['authority_model']=authority

        creative=dict(out.get('creative_exploration') or {})
        agent_authored=str(out.get('status') or '').upper()=='AGENT_AUTHORED'
        if agent_authored and _visual_scope(request):
            creative.setdefault('require_per_asset_art_direction', True)
        creative.setdefault('art_direction_authority', 'HOST_AGENT' if agent_authored else 'COMPATIBILITY_FALLBACK_ALLOWED')
        creative.setdefault('runtime_may_originate_art_direction', False if agent_authored else True)
        creative.setdefault('product_presence_authority', 'HOST_AGENT' if agent_authored else 'COMPATIBILITY_FALLBACK_ALLOWED')
        out['creative_exploration']=creative
        out['principle']='Freeze facts and hard boundaries; the Agent authors portfolio curation, product presence and per-asset Art Direction. Runtime may validate, serialize, compile and execute but must not originate creative decisions when Agent authority is active.'
        return out
    return compiled


def wrap_agent_creative_directions(legacy_fn):
    def compiled(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
        creative=plan.get('creative_exploration') if isinstance(plan.get('creative_exploration'), Mapping) else {}
        rows=legacy_fn(plan)
        art_rows=_rows(creative.get('asset_art_directions') or creative.get('per_asset_art_directions'))
        required=bool(creative.get('require_per_asset_art_direction'))
        if rows:
            out=[]
            for raw in rows:
                row=deepcopy(raw)
                if art_rows and not row.get('asset_art_directions'):
                    row['asset_art_directions']=deepcopy(art_rows)
                row.setdefault('require_per_asset_art_direction', required)
                if str(creative.get('art_direction_authority') or '').upper()=='HOST_AGENT':
                    row.setdefault('source','HOST_AGENT_AUTHORED')
                out.append(row)
            return out
        if art_rows:
            return [{
                'direction_id':'DIR-AGENT-ASSET-AUTHORITY',
                'direction_name':'Agent-authored per-asset art direction system',
                'decision':'SELECT',
                'source':'HOST_AGENT_AUTHORED',
                'route':'AGENT_AUTHORED',
                'creative_thesis':'Per-asset Art Direction is authoritative; portfolio coherence must not collapse assets into one repeated composition.',
                'product_role':'Decided independently per asset by the Agent.',
                'image_language':'Decided independently per asset by the Agent within shared truth and continuity constraints.',
                'proof_mechanism':'Decided independently per asset from the evidence job.',
                'composition_grammar':'No direction-level fallback composition. Each asset carries its own authored spatial grammar.',
                'require_per_asset_art_direction':True,
                'asset_art_directions':deepcopy(art_rows),
                'product_fit':1.0,'audience_fit':1.0,'platform_fit':1.0,'culture_fit':1.0,
                'differentiation':1.0,'production_feasibility':1.0,'decision_coverage':1.0,'opportunity_fit':1.0,
            }]
        return rows
    return compiled


def _direction_art_rows(direction: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _rows(direction.get('asset_art_directions') or direction.get('per_asset_art_directions'))


def _match_art_direction(asset: Mapping[str, Any], direction: Mapping[str, Any]) -> dict[str, Any] | None:
    existing=asset.get('asset_art_direction')
    if isinstance(existing, Mapping):
        return deepcopy(dict(existing))
    rows=_direction_art_rows(direction)
    aid=str(asset.get('asset_id') or '')
    q=str(asset.get('consumer_question') or '').strip()
    name=str(asset.get('asset_name') or '').strip()
    by_id=[r for r in rows if str(r.get('asset_id') or '')==aid and aid]
    if by_id:
        return deepcopy(by_id[0])
    by_q=[r for r in rows if str(r.get('consumer_question') or '').strip()==q and q]
    if len(by_q)==1:
        return deepcopy(by_q[0])
    by_name=[r for r in rows if str(r.get('asset_name') or '').strip()==name and name]
    if len(by_name)==1:
        return deepcopy(by_name[0])
    return None


def _presence_from_art(art: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(art, Mapping):
        return None
    p=art.get('product_presence')
    if isinstance(p, Mapping):
        return deepcopy(dict(p))
    state=art.get('product_presence_state')
    if state:
        return {
            'planning_state':str(state).upper(),
            'product_role':art.get('product_role'),
            'presence_why':art.get('presence_why'),
            'scale_relationship':art.get('scale_relationship'),
            'identity_requirement':art.get('identity_requirement'),
            'source_reference_role':art.get('source_reference_role'),
        }
    return None


def _unresolved_presence() -> dict[str, Any]:
    return {
        'planning_state':'UNRESOLVED_AGENT_DECISION',
        'production_state':'UNRESOLVED',
        'source_reference_role':'TRUTH_REFERENCE_ONLY',
        'authority':'AGENT_DECISION_REQUIRED',
        'principle':'Runtime must return this asset to the Agent. Missing product presence is not permission to insert a packshot or product layer.',
    }


def _art_value(art: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        value=art.get(key)
        if value not in (None,'',[],{}):
            return value
    return None


def wrap_apply_creative_system_to_assets(legacy_module):
    legacy_expression=legacy_module._expression_variant

    def compiled(architecture: dict[str, Any], council: dict[str, Any], cmf: dict[str, Any] | None = None, photography: dict[str, Any] | None = None) -> dict[str, Any]:
        del photography
        selected=(council or {}).get('selected_direction') or {}
        alternatives=(council or {}).get('alternative_directions') or []
        direction_source=str((council or {}).get('direction_source') or '').upper()
        assets=[]
        authored_count=0
        missing_count=0
        for i,raw in enumerate(architecture.get('assets') or []):
            a=deepcopy(raw)
            direction=selected
            # Runtime may route among legacy alternatives only when per-asset Agent Art Direction is not required.
            required=bool(direction.get('require_per_asset_art_direction'))
            art=_match_art_direction(a,direction)
            if not required and not art and alternatives:
                intent=str(a.get('decision_intent') or '').upper()
                preferred={'PROOF':'EVIDENCE_MECHANISM','PERFORMANCE_PROOF':'EVIDENCE_MECHANISM','MATERIAL_SENSORY':'MATERIAL_SENSORY_OBJECT','USAGE':'HUMAN_CONTEXT_ACTION','FIT_WEAR':'HUMAN_CONTEXT_ACTION','RELEVANCE':'HUMAN_CONTEXT_ACTION'}.get(intent)
                direction=next((d for d in [selected]+alternatives if d.get('route')==preferred),selected)
                art=_match_art_direction(a,direction)
                required=bool(direction.get('require_per_asset_art_direction'))

            a['creative_direction']=deepcopy(direction)
            a['art_direction_required']=required
            if art:
                authored_count+=1
                a['asset_art_direction']=deepcopy(art)
                a['art_direction_status']='AUTHORED'
                presence=_presence_from_art(art)
                if presence:
                    a['product_presence']=presence
                elif required:
                    a['product_presence']=_unresolved_presence()
                if isinstance(art.get('information_assetization'), Mapping):
                    a['information_assetization']=deepcopy(dict(art.get('information_assetization') or {}))
                elif art.get('visual_carrier'):
                    a['information_assetization']={
                        'representation':art.get('visual_carrier'),
                        'authority':'HOST_AGENT_ART_DIRECTION',
                        'reason':art.get('visual_carrier_why') or art.get('why'),
                    }
                expression={
                    'variant_id':art.get('variant_id') or f"ART-{str(a.get('asset_id') or i)}",
                    'spatial_rhythm':_art_value(art,'spatial_rhythm','space_rhythm'),
                    'composition_grammar':_art_value(art,'composition_grammar','composition','spatial_grammar'),
                    'preferred_view':_art_value(art,'camera_or_view','preferred_view','view'),
                    'context_role':_art_value(art,'context_role','environment_role'),
                    'direction_id':direction.get('direction_id'),
                    'direction_route':direction.get('route'),
                    'direction_thesis':direction.get('creative_thesis'),
                    'authority':'AGENT_AUTHORED_ASSET_ART_DIRECTION',
                    'same_layout_guard':'Do not inherit the previous asset composition. Execute this asset Art Direction exactly, while preserving only the authored continuity tokens.',
                }
                a['visual_expression_variant']={k:v for k,v in expression.items() if v not in (None,'',[],{})}

                # Agent Art Direction is authoritative. Direction-level values only fill shared system context;
                # they never overwrite authored per-asset design choices.
                brief=dict(a.get('creative_brief') or {})
                direction_defaults={
                    'creative_thesis':direction.get('creative_thesis'),
                    'lighting':direction.get('photography'),
                    'color':(cmf or {}).get('color') or direction.get('color_world'),
                    'typography':direction.get('typography'),
                    'image_language':direction.get('image_language'),
                    'proof_mechanism':direction.get('proof_mechanism'),
                    'verbal_thesis':direction.get('verbal_thesis'),
                }
                for k,v in direction_defaults.items():
                    if v not in (None,'',[],{}) and k not in brief:
                        brief[k]=deepcopy(v)
                authored_map={
                    'subject':_art_value(art,'subject'),
                    'action':_art_value(art,'action','decisive_action'),
                    'environment':_art_value(art,'environment'),
                    'props':_art_value(art,'props','scene_props'),
                    'human':_art_value(art,'human_context','people','casting'),
                    'composition':_art_value(art,'composition_grammar','composition','spatial_grammar'),
                    'camera_or_view':_art_value(art,'camera_or_view','preferred_view','view'),
                    'lighting':_art_value(art,'lighting'),
                    'color':_art_value(art,'cmf','color','color_world'),
                    'typography':_art_value(art,'typography'),
                    'scene_props':_art_value(art,'scene_props','props'),
                    'image_language':_art_value(art,'image_language','visual_language'),
                    'proof_mechanism':_art_value(art,'proof_mechanism','evidence_hierarchy','evidence_plane'),
                    'verbal_thesis':_art_value(art,'verbal_thesis'),
                    'negative_space':_art_value(art,'negative_space','copy_negative_space'),
                    'focal_path':_art_value(art,'focal_path'),
                }
                for k,v in authored_map.items():
                    if v not in (None,'',[],{}):
                        brief[k]=deepcopy(v)
                a['creative_brief']=brief

                sig={
                    'creative_direction_id':direction.get('direction_id'),
                    'creative_direction_route':direction.get('route'),
                    'expression_variant':a.get('visual_expression_variant'),
                    'visual_job':_art_value(art,'visual_job','decisive_moment','objective') or a.get('strategic_job'),
                    'composition_grammar':authored_map.get('composition'),
                    'camera_or_view':authored_map.get('camera_or_view'),
                    'context_role':_art_value(art,'context_role','environment_role'),
                    'evidence_plane':_art_value(art,'evidence_plane','evidence_hierarchy'),
                    'differentiation_axis':_art_value(art,'differentiation_axis','deliberate_difference'),
                    'authority':'HOST_AGENT_ART_DIRECTION',
                }
                a['visual_production_signature']={k:v for k,v in sig.items() if v not in (None,'',[],{})}
            else:
                if required:
                    missing_count+=1
                    a['art_direction_status']='MISSING_AGENT_DECISION'
                    a['product_presence']=_unresolved_presence()
                    a['visual_expression_variant']={
                        'authority':'AGENT_DECISION_REQUIRED',
                        'same_layout_guard':'No deterministic composition fallback is allowed. Return to the Agent for per-asset Art Direction.',
                    }
                    a['visual_production_signature']={
                        'authority':'AGENT_DECISION_REQUIRED',
                        'visual_job':a.get('strategic_job'),
                    }
                else:
                    # Legacy compatibility path only. Preserve existing asset-level brief rather than
                    # overwriting it with direction-level defaults.
                    expression=legacy_expression(a,direction,i)
                    a['visual_expression_variant']=expression
                    sig=dict(a.get('visual_production_signature') or {})
                    sig.update({
                        'creative_direction_id':direction.get('direction_id'),
                        'creative_direction_route':direction.get('route'),
                        'expression_variant':expression,
                    })
                    if expression.get('composition_grammar'):
                        sig['composition_grammar']=expression.get('composition_grammar')
                    if expression.get('preferred_view'):
                        sig['camera_or_view']=expression.get('preferred_view')
                    if expression.get('context_role'):
                        sig['context_role']=expression.get('context_role')
                    a['visual_production_signature']=sig
                    brief=dict(a.get('creative_brief') or {})
                    defaults={
                        'creative_thesis':direction.get('creative_thesis'),
                        'composition':expression.get('composition_grammar'),
                        'camera_or_view':expression.get('preferred_view'),
                        'lighting':direction.get('photography'),
                        'color':(cmf or {}).get('color') or direction.get('color_world'),
                        'typography':direction.get('typography'),
                        'scene_props':direction.get('scene_props'),
                        'image_language':direction.get('image_language'),
                        'proof_mechanism':direction.get('proof_mechanism'),
                        'verbal_thesis':direction.get('verbal_thesis'),
                    }
                    for k,v in defaults.items():
                        if v not in (None,'',[],{}) and k not in brief:
                            brief[k]=deepcopy(v)
                    a['creative_brief']=brief
                    a.setdefault('art_direction_status','LEGACY_COMPATIBILITY_FALLBACK')

            # Keep the surface contract synchronized with the final Agent authority decision.
            surface_contract=dict(a.get('surface_native_contract') or {})
            if a.get('product_presence'):
                surface_contract['product_presence']=(a.get('product_presence') or {}).get('planning_state')
            if a.get('information_assetization'):
                surface_contract['representation']=(a.get('information_assetization') or {}).get('representation')
            if surface_contract:
                a['surface_native_contract']=surface_contract
            assets.append(a)

        out=deepcopy(architecture)
        out['assets']=assets
        out['creative_system_assignment']={
            'selected_direction_id':selected.get('direction_id'),
            'selected_direction':deepcopy(selected),
            'direction_source':direction_source,
            'direction_count':len((council or {}).get('directions') or []),
            'asset_expression_count':len(assets),
            'agent_authored_art_direction_count':authored_count,
            'missing_agent_art_direction_count':missing_count,
            'creative_authority':'HOST_AGENT' if bool(selected.get('require_per_asset_art_direction')) else 'COMPATIBILITY_MODE',
            'runtime_creative_role':'VALIDATE_SERIALIZE_COMPILE_EXECUTE_ONLY' if bool(selected.get('require_per_asset_art_direction')) else 'LEGACY_COMPATIBILITY_FALLBACK_ALLOWED',
            'same_layout_guard':'Coherence comes from shared truth and authored continuity tokens. Per-asset composition, product role, subject, evidence plane and visual carrier remain Agent decisions.',
        }
        return out
    return compiled


def wrap_compile_agent_next_action(legacy_fn):
    def compiled(plan: Mapping[str, Any], **kwargs) -> dict[str, Any]:
        result=deepcopy(legacy_fn(plan, **kwargs))
        creative=plan.get('creative_exploration') if isinstance(plan.get('creative_exploration'), Mapping) else {}
        if not creative.get('require_per_asset_art_direction'):
            return result
        architecture=kwargs.get('asset_architecture') if isinstance(kwargs.get('asset_architecture'), Mapping) else {}
        missing=[]
        for asset in architecture.get('assets') or []:
            if str(asset.get('asset_type') or '').upper() in {'IMAGE','VIDEO'} and str(asset.get('art_direction_status') or '').upper()!='AUTHORED':
                missing.append(asset.get('asset_id'))
        if not missing:
            return result
        item={
            'action':'AUTHOR_PER_ASSET_ART_DIRECTION',
            'reason':'Visual production is in Agent-authority mode and one or more visual assets still lack authored Art Direction. Runtime may not invent product presence, composition or visual carrier.',
            'items':missing,
            'blocking':True,
        }
        blocking=list(result.get('blocking_frontier') or [])
        if not any(x.get('action')=='AUTHOR_PER_ASSET_ART_DIRECTION' for x in blocking):
            blocking.insert(0,item)
        advisory=[x for x in (result.get('advisory_frontier') or []) if x.get('action')!='AUTHOR_PER_ASSET_ART_DIRECTION']
        result['blocking_frontier']=blocking
        result['advisory_frontier']=advisory
        result['frontier']=blocking+advisory
        result['blocking_frontier_count']=len(blocking)
        result['advisory_frontier_count']=len(advisory)
        result['status']='ACTION_FRONTIER_OPEN'
        result['recommended_next_action']='AUTHOR_PER_ASSET_ART_DIRECTION'
        result['agent_stop_overridden_by_hard_blocker']=bool(result.get('agent_stop_requested'))
        result['creative_authority']='HOST_AGENT'
        return result
    return compiled
