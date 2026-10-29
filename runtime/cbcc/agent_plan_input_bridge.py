from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def wrap_compile_agent_autonomy_plan(previous_fn):
    """Accept host-authored curation/art-direction data in either canonical or convenient locations.

    The canonical runtime location remains `creative_exploration`, but host Agents should not lose
    their authored decisions merely because they placed `portfolio_curation` or
    `asset_art_directions` at the top of `agent_plan`.
    """
    def compiled(request: Mapping[str, Any]) -> dict[str, Any]:
        out=deepcopy(previous_fn(request))
        raw=request.get('agent_plan') or request.get('agent_decisions') or {}
        raw=dict(raw) if isinstance(raw, Mapping) else {}
        creative=dict(out.get('creative_exploration') or {})

        if not creative.get('asset_art_directions'):
            rows=raw.get('asset_art_directions') or raw.get('per_asset_art_directions')
            if rows:
                creative['asset_art_directions']=deepcopy(rows)
        if not creative.get('portfolio_curation') and raw.get('portfolio_curation'):
            creative['portfolio_curation']=deepcopy(raw.get('portfolio_curation'))
        if not creative.get('continuity_system') and raw.get('continuity_system'):
            creative['continuity_system']=deepcopy(raw.get('continuity_system'))
        if not creative.get('visual_carrier_strategy') and raw.get('visual_carrier_strategy'):
            creative['visual_carrier_strategy']=deepcopy(raw.get('visual_carrier_strategy'))

        if creative.get('asset_art_directions'):
            creative['require_per_asset_art_direction']=True
            creative['art_direction_authority']='HOST_AGENT'
            creative['runtime_may_originate_art_direction']=False
            creative['product_presence_authority']='HOST_AGENT'

        out['creative_exploration']=creative
        out['portfolio_curation']=deepcopy(creative.get('portfolio_curation') or {})
        out['asset_art_direction_count']=len(creative.get('asset_art_directions') or []) if isinstance(creative.get('asset_art_directions'), list) else None
        return out
    return compiled
