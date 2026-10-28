from pathlib import Path

p=Path('runtime/cbcc/delivery_html.py')
text=p.read_text(encoding='utf-8')
old="""    machine_html=''.join(machine) or '<div class=\"empty\">暂无结构化归档。</div>'
    if media or source_doc_views or source_files:
        availability['sources']=True
    availability['archive']=bool(machine)
    route_plan=build_workspace_route_plan(availability=availability,agent_next_action=agent_next_action)
    nav_html=''.join(f'<a href=\"#{row[\"route\"]}\" data-route=\"{row[\"route\"]}\" class=\"route-link\"><span class=\"ico\">{row[\"icon\"]}</span>{row[\"label\"]}</a>' for row in route_plan['primary_routes'])
    commands=''.join(f'<a class=\"command-card route-link\" href=\"#{row[\"route\"]}\" data-route=\"{row[\"route\"]}\"><b>{html.escape(str(row[\"name\"]))}</b><span>{html.escape(str(row[\"description\"]))}</span></a>' for row in route_plan['commands']) or '<div class=\"empty\">当前没有需要额外推进的工作对象；可在现有项目范围内复核或停止。</div>'
    archive_link=''.join(f'<a class=\"route-link secondary-route\" href=\"#{row[\"route\"]}\" data-route=\"{row[\"route\"]}\">{row[\"label\"]}</a>' for row in route_plan['secondary_routes'])

    css=f'''\n"""
new="""    machine_html=''.join(machine) or '<div class=\"empty\">暂无结构化归档。</div>'

    css=f'''\n"""
if old in text:
    text=text.replace(old,new,1)
elif "if media or source_doc_views or source_files:" in text:
    raise SystemExit('unexpected dynamic route refresh shape')

marker="""    source_doc_views=_doc_views(docs['sources'],package_dir,'sources') if docs['sources'] else []
    sources_ws=_evidence_workspace(media,source_doc_views,source_files)

"""
insert=marker+"""    if media or source_doc_views or source_files:
        availability['sources']=True
    availability['archive']=bool(machine)
    route_plan=build_workspace_route_plan(availability=availability,agent_next_action=agent_next_action)
    nav_html=''.join(f'<a href=\"#{row[\"route\"]}\" data-route=\"{row[\"route\"]}\" class=\"route-link\"><span class=\"ico\">{row[\"icon\"]}</span>{row[\"label\"]}</a>' for row in route_plan['primary_routes'])
    commands=''.join(f'<a class=\"command-card route-link\" href=\"#{row[\"route\"]}\" data-route=\"{row[\"route\"]}\"><b>{html.escape(str(row[\"name\"]))}</b><span>{html.escape(str(row[\"description\"]))}</span></a>' for row in route_plan['commands']) or '<div class=\"empty\">当前没有需要额外推进的工作对象；可在现有项目范围内复核或停止。</div>'
    archive_link=''.join(f'<a class=\"route-link secondary-route\" href=\"#{row[\"route\"]}\" data-route=\"{row[\"route\"]}\">{row[\"label\"]}</a>' for row in route_plan['secondary_routes'])

"""
if insert not in text:
    if marker not in text:
        raise SystemExit('sources workspace marker missing')
    text=text.replace(marker,insert,1)
p.write_text(text,encoding='utf-8')
