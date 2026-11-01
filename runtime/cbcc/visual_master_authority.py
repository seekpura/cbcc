from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping

from .models import stable_hash
from .visual_route_scope import is_visual_production_asset


def _target_context(request: Mapping[str, Any] | None) -> dict[str, Any]:
    request = request if isinstance(request, Mapping) else {}
    target = request.get('target') if isinstance(request.get('target'), Mapping) else request
    target = target if isinstance(target, Mapping) else {}
    return {
        'target_id': target.get('target_id'),
        'market': target.get('market'),
        'platform_family': target.get('platform_family'),
        'site': target.get('site'),
        'category': target.get('category'),
        'surfaces': deepcopy(target.get('surfaces') or []),
    }


def compile_visual_master(
    portfolio_visual_program: Mapping[str, Any] | None,
    *,
    target: Mapping[str, Any] | None = None,
    missing: list[str] | None = None,
) -> dict[str, Any]:
    """Materialize the existing Agent-authored Portfolio Visual Program as one canonical authority.

    This function does not create visual ideas, scenes, camera settings or layouts. The authored
    Portfolio Visual Program remains the content source; Visual Master only gives that same program
    a stable pre-asset identity/lineage so architecture and per-asset Art Direction can reference it.
    """
    program = deepcopy(dict(portfolio_visual_program or {}))
    missing = list(missing or [])
    context = _target_context(target)
    authority_hash = stable_hash({
        'source_authority': 'PORTFOLIO_VISUAL_PROGRAM',
        'portfolio_visual_program': program,
        'target_context': context,
    })
    return {
        'schema_version': 'cbcc-visual-master-v0.6.76',
        'status': 'READY' if program and not missing else 'TO_VERIFY',
        'authority': 'HOST_AGENT',
        'authority_stage': 'PRE_ASSET_ARCHITECTURE',
        'source_authority': 'PORTFOLIO_VISUAL_PROGRAM',
        'visual_master_id': 'VM-' + authority_hash[:12].upper(),
        'authority_hash': authority_hash,
        'portfolio_visual_program': program,
        'missing': missing,
        'target_context': context,
        'runtime_may_invent_visual_strategy': False,
        'per_asset_art_direction_must_adapt_not_copy': True,
        'fixed_visual_template': False,
        'principle': 'Visual Master is the stable authority identity of the existing Agent-authored Portfolio Visual Program. Assets reference it and author route-specific Art Direction; runtime does not synthesize a second visual system.',
    }


def visual_master_ref(master: Mapping[str, Any] | None) -> dict[str, Any]:
    master = master if isinstance(master, Mapping) else {}
    if not master.get('visual_master_id') or not master.get('authority_hash'):
        return {}
    return {
        'visual_master_id': master.get('visual_master_id'),
        'authority_hash': master.get('authority_hash'),
        'authority_stage': master.get('authority_stage') or 'PRE_ASSET_ARCHITECTURE',
    }


def wrap_compile_agent_autonomy_plan(previous_fn: Callable[..., dict[str, Any]]):
    if getattr(previous_fn, '_cbcc_v0676_visual_master_plan', False):
        return previous_fn

    def compiled(request: Mapping[str, Any]) -> dict[str, Any]:
        out = deepcopy(previous_fn(request))
        creative = dict(out.get('creative_exploration') or {})
        if not creative.get('require_portfolio_visual_program'):
            return out
        creative['visual_master'] = compile_visual_master(
            creative.get('portfolio_visual_program') if isinstance(creative.get('portfolio_visual_program'), Mapping) else {},
            target=request,
            missing=list(creative.get('portfolio_visual_program_missing') or []),
        )
        creative['visual_master_authority'] = 'CANONICAL_MATERIALIZATION_OF_PORTFOLIO_VISUAL_PROGRAM'
        out['creative_exploration'] = creative
        return out

    setattr(compiled, '_cbcc_v0676_visual_master_plan', True)
    return compiled


def wrap_agent_creative_directions(previous_fn: Callable[..., list[dict[str, Any]]]):
    if getattr(previous_fn, '_cbcc_v0676_visual_master_directions', False):
        return previous_fn

    def compiled(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
        rows = previous_fn(plan)
        creative = plan.get('creative_exploration') if isinstance(plan.get('creative_exploration'), Mapping) else {}
        ref = visual_master_ref(creative.get('visual_master'))
        if not ref:
            return rows
        out = []
        for raw in rows:
            row = deepcopy(raw)
            row['visual_master_ref'] = deepcopy(ref)
            out.append(row)
        return out

    setattr(compiled, '_cbcc_v0676_visual_master_directions', True)
    return compiled


def wrap_build_asset_architecture(previous_fn: Callable[..., dict[str, Any]]):
    if getattr(previous_fn, '_cbcc_v0676_visual_master_architecture', False):
        return previous_fn

    def built(
        project_id: str,
        target: dict[str, Any],
        questions: list[str],
        content_objects: list[dict[str, Any]],
        asset_jobs: list[dict[str, Any]] | None = None,
        decision_context: dict[str, Any] | None = None,
        category_family: str = 'GENERAL_COMMERCE',
    ) -> dict[str, Any]:
        target_for_build = deepcopy(dict(target or {}))
        master = target_for_build.get('phase4_visual_master')
        out = deepcopy(previous_fn(project_id, target_for_build, questions, content_objects, asset_jobs, decision_context, category_family))
        if not isinstance(master, Mapping):
            return out
        master = deepcopy(dict(master))
        ref = visual_master_ref(master)
        out['phase4_visual_master'] = master
        if ref:
            for asset in out.get('assets') or []:
                if isinstance(asset, dict) and is_visual_production_asset(asset):
                    asset['visual_master_ref'] = deepcopy(ref)
        return out

    setattr(built, '_cbcc_v0676_visual_master_architecture', True)
    return built


def wrap_apply_creative_system_to_assets(previous_fn: Callable[..., dict[str, Any]]):
    if getattr(previous_fn, '_cbcc_v0676_visual_master_assignment', False):
        return previous_fn

    def compiled(
        architecture: dict[str, Any],
        council: dict[str, Any],
        cmf: dict[str, Any] | None = None,
        photography: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        out = deepcopy(previous_fn(architecture, council, cmf, photography))
        master = out.get('phase4_visual_master') or architecture.get('phase4_visual_master')
        ref = visual_master_ref(master if isinstance(master, Mapping) else {})
        if not ref:
            return out
        out['phase4_visual_master'] = deepcopy(dict(master))
        assignment = dict(out.get('creative_system_assignment') or {})
        assignment['visual_master_ref'] = deepcopy(ref)
        out['creative_system_assignment'] = assignment
        for asset in out.get('assets') or []:
            if isinstance(asset, dict) and is_visual_production_asset(asset):
                asset['visual_master_ref'] = deepcopy(ref)
        return out

    setattr(compiled, '_cbcc_v0676_visual_master_assignment', True)
    return compiled
