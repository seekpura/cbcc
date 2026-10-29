from pathlib import Path

P=Path('runtime/cbcc/delivery_html.py')
text=P.read_text(encoding='utf-8')

anchor="""    risk_ws=_module_workspace(risk_views,'risk','本项目没有风险内容。')
    listing_ws=_listing_workspace(center)
"""
insert="""    risk_ws=_module_workspace(risk_views,'risk','本项目没有风险内容。')
    overview_ws=_module_workspace(master_views['overview'],'overview-decision','本项目没有信息完整度 / 假设 / 决策日志。')
    listing_ws=_listing_workspace(center)
"""
if 'overview_ws=_module_workspace(master_views[\'overview\']' not in text:
    if anchor not in text:
        raise SystemExit('overview workspace anchor not found')
    text=text.replace(anchor,insert,1)

parts_anchor="""    page_parts=[]
    page_parts.append(f'''<section class=\"page\" data-route=\"overview\""""
parts_insert="""    overview_decision_html=(
        '<div class=\"panel full-overview-domain\"><div class=\"kicker\">FULL 决策域</div><h2>信息完整度、待确认清单、假设与决策日志</h2>'
        + overview_ws + '</div>'
    ) if master_views['overview'] else ''

    page_parts=[]
    page_parts.append(f'''<section class=\"page\" data-route=\"overview\""""
if 'overview_decision_html=(' not in text:
    if parts_anchor not in text:
        raise SystemExit('overview page anchor not found')
    text=text.replace(parts_anchor,parts_insert,1)

needle="""{f'<div class=\"stats\">{stats_html}</div>' if stats_html else ''}<div class=\"panel\"><h2>当前可以做什么？</h2>"""
replacement="""{f'<div class=\"stats\">{stats_html}</div>' if stats_html else ''}{overview_decision_html}<div class=\"panel\"><h2>当前可以做什么？</h2>"""
if '{overview_decision_html}<div class="panel"><h2>当前可以做什么？</h2>' not in text:
    if needle not in text:
        raise SystemExit('overview insertion point not found')
    text=text.replace(needle,replacement,1)

P.write_text(text,encoding='utf-8')
print('FULL overview visibility repair applied')
