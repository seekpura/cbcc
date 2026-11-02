from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected one match, found {count}')
    p.write_text(text.replace(old, new), encoding='utf-8')


replace_once(
    'runtime/cbcc/agent_autonomy.py',
    """    stop_conditions = _strings(agent.get('research_stop_conditions')) or [
        'Stop when additional research is unlikely to change a material strategy, listing, asset, compliance or production decision.',
        'Stop when decision-critical claims and hard platform/compliance constraints have sufficient current evidence.',
        'Do not research for quota completion, source-count targets or cosmetic comprehensiveness.',
    ]
""",
    """    if 'research_stop_conditions' in agent:
        stop_conditions = _strings(agent.get('research_stop_conditions'))
    else:
        stop_conditions = [
            'Stop when additional research is unlikely to change a material strategy, listing, asset, compliance or production decision.',
            'Stop when decision-critical claims and hard platform/compliance constraints have sufficient current evidence.',
            'Do not research for quota completion, source-count targets or cosmetic comprehensiveness.',
        ]
""",
)

replace_once(
    'runtime/cbcc/creative_opportunity.py',
    """    if agent_opportunities:
""",
    """    if agent_opportunities is not None:
""",
)

replace_once(
    'runtime/cbcc/creative.py',
    """    supplied=bool(directions)
    source_rows=list(directions or _auto_directions(product_truth,curation,culture,platform_compile,category_family,decision_intents,opportunity_universe))
""",
    """    supplied=directions is not None
    source_rows=list(directions if directions is not None else _auto_directions(product_truth,curation,culture,platform_compile,category_family,decision_intents,opportunity_universe))
""",
)

replace_once(
    'runtime/cbcc/asset_architecture.py',
    """    jobs=list(asset_jobs or [])
    asset_scope_active=bool(jobs)
    if not jobs:
""",
    """    asset_jobs_supplied=asset_jobs is not None
    jobs=list(asset_jobs or [])
    asset_scope_active=bool(jobs)
    if not jobs and not asset_jobs_supplied:
""",
)

replace_once(
    'runtime/cbcc/compiler.py',
    """    creative_opportunity_universe=compile_creative_opportunity_universe(
        truth,product_visual_intelligence,category_family,architecture.get('assets') or [],curation,culture,tc,
        agent_opportunities=agent_creative_opportunities(agent_plan),
    )
    _write(p/'artifacts/creative_opportunity_universe.json',creative_opportunity_universe)
    council=compile_creative_council(request.get('creative_directions') or agent_creative_directions(agent_plan),curation,truth,culture,pc,category_family,[a.get('decision_intent') for a in architecture.get('assets') or []],creative_opportunity_universe)
""",
    """    creative_scope=agent_plan.get('creative_exploration') if isinstance(agent_plan.get('creative_exploration'),dict) else {}
    if 'opportunities' in creative_scope or 'mechanisms' in creative_scope:
        agent_opportunity_rows=agent_creative_opportunities(agent_plan)
    else:
        agent_opportunity_rows=None
    creative_opportunity_universe=compile_creative_opportunity_universe(
        truth,product_visual_intelligence,category_family,architecture.get('assets') or [],curation,culture,tc,
        agent_opportunities=agent_opportunity_rows,
    )
    _write(p/'artifacts/creative_opportunity_universe.json',creative_opportunity_universe)
    if 'creative_directions' in request:
        council_directions=request.get('creative_directions')
    elif 'directions' in creative_scope:
        council_directions=agent_creative_directions(agent_plan)
    else:
        council_directions=None
    council=compile_creative_council(council_directions,curation,truth,culture,pc,category_family,[a.get('decision_intent') for a in architecture.get('assets') or []],creative_opportunity_universe)
""",
)
