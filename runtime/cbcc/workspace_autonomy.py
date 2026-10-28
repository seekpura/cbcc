from __future__ import annotations

from typing import Any, Mapping

VERSION = '0.6.22-dynamic-commerce-workspace'

ROUTE_META = {
    'overview': {'icon':'⌂','label':'工作台','action':'查看当前项目'},
    'product': {'icon':'▣','label':'产品事实','action':'核对产品事实与证据'},
    'market': {'icon':'◎','label':'市场 / 人群','action':'处理市场、人群与文化判断'},
    'listing': {'icon':'≡','label':'上架中心','action':'处理上架资料'},
    'strategy': {'icon':'◇','label':'策略中心','action':'查看或调整关键策略决策'},
    'content': {'icon':'▤','label':'内容系统','action':'规划当前需要的内容对象'},
    'visual': {'icon':'◐','label':'视觉 / 摄影','action':'处理创意、视觉或摄影决策'},
    'assets': {'icon':'▦','label':'资产中心','action':'进入资产生产工作区'},
    'prompts': {'icon':'⌘','label':'提示词工作台','action':'执行当前已就绪的生产提示词'},
    'risk': {'icon':'!','label':'风险 / 合规','action':'解决风险、合规或待查证问题'},
    'sources': {'icon':'◉','label':'来源 / 真源','action':'查看来源与证据'},
    'archive': {'icon':'⋯','label':'归档','action':'查看结构化机器归档'},
}

FRONTIER_ROUTE = {
    'RESEARCH_OR_EVIDENCE_RESOLUTION':'sources',
    'REPLAN_ASSET_ARCHITECTURE':'assets',
    'AUTHOR_OR_SELECT_CREATIVE_DIRECTION':'visual',
    'RESOLVE_COMPLIANCE_BOUNDARY':'risk',
    'PRODUCE_RESUME_OR_REPAIR':'assets',
}


def _bool(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(_bool(v) for v in value.values())
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_bool(v) for v in value)
    return value not in (None, '', False, 0)


def build_workspace_route_plan(
    *,
    availability: Mapping[str, Any],
    agent_next_action: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build primary navigation from the business objects that actually exist in this project.

    This function does not decide which commerce capabilities a project should have. It only projects the
    already-compiled project into a human workspace. Empty capabilities are not promoted into primary nav.
    Machine archive is intentionally secondary because it is a trace surface, not a normal human workflow.
    """
    available = {str(k): _bool(v) for k, v in dict(availability or {}).items()}
    primary_order = ['overview','product','market','listing','strategy','content','visual','assets','prompts','risk','sources']
    routes=[]
    for route in primary_order:
        if route != 'overview' and not available.get(route, False):
            continue
        routes.append({'route':route, **ROUTE_META[route]})

    secondary=[]
    if available.get('archive'):
        secondary.append({'route':'archive', **ROUTE_META['archive']})

    frontier = list((agent_next_action or {}).get('frontier') or [])
    commands=[]
    seen=set()
    for item in frontier:
        action=str(item.get('action') or '')
        route=FRONTIER_ROUTE.get(action)
        if not route or not available.get(route, False) or route in seen:
            continue
        commands.append({
            'route':route,
            'name':item.get('label') or ROUTE_META[route]['action'],
            'description':item.get('reason') or '这是当前 Agent 识别到的下一项高价值工作。',
            'source':'AGENT_FRONTIER',
            'action':action,
        })
        seen.add(route)

    # Add available business objects not already promoted by the Agent frontier. No fixed action quota.
    for route in ['listing','assets','content','visual','prompts','risk','sources','market','strategy','product']:
        if not available.get(route, False) or route in seen:
            continue
        commands.append({
            'route':route,
            'name':ROUTE_META[route]['action'],
            'description':f"当前项目已生成“{ROUTE_META[route]['label']}”对象，可直接进入处理。",
            'source':'AVAILABLE_BUSINESS_OBJECT',
        })
        seen.add(route)

    return {
        'version':VERSION,
        'primary_routes':routes,
        'secondary_routes':secondary,
        'commands':commands,
        'default_route':'overview',
        'fixed_route_count':None,
        'fixed_command_count':None,
        'principle':'Show the business objects and next actions that actually exist. Navigation is a projection of the current project, not a fixed report table of contents.',
    }


def relevant_asset_view_keys(asset: Mapping[str, Any]) -> list[str]:
    """Return asset workspace views as independent lenses, not mandatory sequential phases."""
    raw=[]
    for view in asset.get('views') or []:
        if not isinstance(view, Mapping):
            continue
        key=str(view.get('key') or '')
        body=str(view.get('html') or '').strip()
        if key and body and '暂无已确认内容' not in body:
            raw.append(key)
    if asset.get('prompt_cn') or asset.get('prompt_en'):
        raw.append('prompt')
    if asset.get('source_files'):
        raw.append('qa')
    explicit=asset.get('agent_view_order') or asset.get('workspace_view_order')
    if isinstance(explicit, (list, tuple)):
        ordered=[str(k) for k in explicit if str(k) in raw]
        ordered += [k for k in raw if k not in ordered]
        return list(dict.fromkeys(ordered))
    return list(dict.fromkeys(raw))
