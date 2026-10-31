from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping
import json


def _meaningful(value: Any) -> bool:
    if value in (None, '', [], {}):
        return False
    if isinstance(value, Mapping):
        return any(_meaningful(v) for v in value.values())
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_meaningful(v) for v in value)
    return True


def _asset_art_directions(request: Mapping[str, Any]) -> list[dict[str, Any]]:
    plan = request.get('agent_plan') if isinstance(request.get('agent_plan'), Mapping) else {}
    creative = plan.get('creative_exploration') if isinstance(plan.get('creative_exploration'), Mapping) else {}
    candidates = creative.get('asset_art_directions') or plan.get('asset_art_directions') or request.get('asset_art_directions') or []
    return [dict(row) for row in candidates if isinstance(row, Mapping)]


def _dedupe(values: list[Any]) -> list[Any]:
    out: list[Any] = []
    seen: set[str] = set()
    for value in values:
        if not _meaningful(value):
            continue
        try:
            key = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
        except Exception:
            key = repr(value)
        if key in seen:
            continue
        seen.add(key)
        out.append(deepcopy(value))
    return out


def project_authored_asset_world_to_visual_strategy(request: Mapping[str, Any]) -> dict[str, Any]:
    """Project already-authored per-asset worlds into missing project Visual Master slots.

    This is a lossless aggregation only. It never invents a scene or prop and never overrides an
    explicit project-level visual_strategy / photography_contract decision.
    """
    out = deepcopy(dict(request))
    rows = _asset_art_directions(out)
    if not rows:
        return out

    vs = deepcopy(out.get('visual_strategy') if isinstance(out.get('visual_strategy'), Mapping) else {})
    photo = out.get('photography_contract') if isinstance(out.get('photography_contract'), Mapping) else {}

    if not _meaningful(vs.get('scene')) and not _meaningful(photo.get('scene')):
        environments = _dedupe([
            row.get('environment') if _meaningful(row.get('environment')) else row.get('scene')
            for row in rows
        ])
        if environments:
            bindings = [
                {
                    'asset': row.get('asset_id') or row.get('asset_name') or f'asset-{idx+1}',
                    'environment': deepcopy(row.get('environment') if _meaningful(row.get('environment')) else row.get('scene')),
                }
                for idx, row in enumerate(rows)
                if _meaningful(row.get('environment')) or _meaningful(row.get('scene'))
            ]
            vs['scene'] = {
                'source': 'AUTHORED_ASSET_ART_DIRECTIONS',
                'environment_system': environments,
                'asset_bindings': bindings,
                'principle': 'Lossless portfolio summary of already-authored asset environments; no new scene fact is invented.',
            }

    if not _meaningful(vs.get('props')) and not _meaningful(photo.get('props')):
        all_props: list[Any] = []
        bindings = []
        for idx, row in enumerate(rows):
            value = row.get('props')
            values = list(value) if isinstance(value, (list, tuple)) else ([value] if _meaningful(value) else [])
            if values:
                bindings.append({
                    'asset': row.get('asset_id') or row.get('asset_name') or f'asset-{idx+1}',
                    'props': deepcopy(values),
                })
                all_props.extend(values)
        props = _dedupe(all_props)
        if props:
            vs['props'] = {
                'source': 'AUTHORED_ASSET_ART_DIRECTIONS',
                'prop_system': props,
                'asset_bindings': bindings,
                'principle': 'Lossless portfolio summary of already-authored asset props; no prop is synthesized.',
            }

    if vs:
        out['visual_strategy'] = vs
    return out


def wrap_build_visual_depth(fn: Callable[..., dict[str, Any]]):
    if getattr(fn, '_cbcc_v0672_visual_master_projection', False):
        return fn

    def built(request: dict[str, Any], *args, **kwargs):
        return fn(project_authored_asset_world_to_visual_strategy(request), *args, **kwargs)

    setattr(built, '_cbcc_v0672_visual_master_projection', True)
    return built
