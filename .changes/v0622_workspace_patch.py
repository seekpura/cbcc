from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'missing workspace patch target: {label}')
    return text.replace(old, new, 1)

p=Path('runtime/cbcc/delivery_html.py')
text=p.read_text(encoding='utf-8')
text=replace_once(
    text,
    'import base64, html, json, mimetypes, re\n',
    'import base64, html, json, mimetypes, re\n\nfrom .workspace_autonomy import build_workspace_route_plan, relevant_asset_view_keys\n',
    'workspace autonomy import',
)

# Do not create an empty photography/CMF view just because the Design Card schema has a photography slot.
old="""        photo_exec=design.get('photography_execution') or {}
        photo=_human_kv([
          ('拍摄 / 合成模式',photo_exec.get('capture_mode')),('构图执行合同',photo_exec.get('composition')),('输出色彩管理',photo_exec.get('color_management')),('焦段',comp.get('focal_length_mm')),('镜头家族',comp.get('lens_family')),('方位角',comp.get('azimuth')),('俯仰 / 高度',comp.get('elevation') or comp.get('camera_height')),('对焦平面',comp.get('focus_plane')),('景深 / 光圈意图',comp.get('aperture_dof_intent')),('快门起点',comp.get('shutter_speed')),('ISO 起点',comp.get('iso')),('主光',light.get('key')),('补光',light.get('fill')),('负补光',light.get('negative_fill')),('轮廓光',light.get('rim')),('色温',light.get('cct')),('阴影策略',light.get('shadow')),('高光策略',light.get('highlight_policy')),('Prelight',light.get('prelight_plan')),('偏振',light.get('polarization_plan')),('色彩一致性',light.get('color_consistency_plan'))
        ])
        views.append({'key':'photo','title':'摄影 / CMF','html':photo})
"""
new="""        photo_exec=design.get('photography_execution') or {}
        photo_rows=[
          ('拍摄 / 合成模式',photo_exec.get('capture_mode')),('构图执行合同',photo_exec.get('composition')),('输出色彩管理',photo_exec.get('color_management')),('焦段',comp.get('focal_length_mm')),('镜头家族',comp.get('lens_family')),('方位角',comp.get('azimuth')),('俯仰 / 高度',comp.get('elevation') or comp.get('camera_height')),('对焦平面',comp.get('focus_plane')),('景深 / 光圈意图',comp.get('aperture_dof_intent')),('快门起点',comp.get('shutter_speed')),('ISO 起点',comp.get('iso')),('主光',light.get('key')),('补光',light.get('fill')),('负补光',light.get('negative_fill')),('轮廓光',light.get('rim')),('色温',light.get('cct')),('阴影策略',light.get('shadow')),('高光策略',light.get('highlight_policy')),('Prelight',light.get('prelight_plan')),('偏振',light.get('polarization_plan')),('色彩一致性',light.get('color_consistency_plan'))
        ]
        if any(v not in (None,'',[],{}) for _,v in photo_rows):
            views.append({'key':'photo','title':'摄影 / CMF','html':_human_kv(photo_rows)})
"""
text=replace_once(text,old,new,'conditional photography view')

# Preserve an Agent-authored workspace view order when one exists.
old_return="""    return {'id':aid,'title':display_title,'original_title':original_title,'summary':summary,'prompt_cn':prompt_cn,'prompt_en':prompt_en,'views':views,'source_files':src,'surface':surface,'intent':intent,'asset_type':asset_type}
"""
new_return="""    return {'id':aid,'title':display_title,'original_title':original_title,'summary':summary,'prompt_cn':prompt_cn,'prompt_en':prompt_en,'views':views,'source_files':src,'surface':surface,'intent':intent,'asset_type':asset_type,'agent_view_order':design.get('workspace_view_order') or design.get('agent_view_order') or []}
"""
text=replace_once(text,old_return,new_return,'asset view order')

# Replace the phase/pipeline asset page with independent task lenses.
start=text.index('def _asset_page(a:dict[str,Any])->str:\n')
end=text.index('\ndef _json_panel(',start)
new_func=r'''def _asset_page(a:dict[str,Any])->str:
    raw_views=list(a.get('views') or [])
    by_key={str(v.get('key') or ''):v for v in raw_views if isinstance(v,dict)}
    ordered_keys=relevant_asset_view_keys(a)
    group=f'asset-workspace-{_slug(a["id"])}'
    panels=[]

    def prompt_body()->str:
        parts=[];aid=_slug(a['id'])
        if a.get('prompt_cn'):
            cid=f'asset-{aid}-prompt-cn'
            parts.append(f'''<section class="prompt-primary"><div class="prompt-head"><div><span>人类生产说明</span><h3>中文规范生产提示词</h3></div><button class="copy-btn mini" data-copy="{cid}">复制中文</button></div><pre id="{cid}"><code>{html.escape(a['prompt_cn'])}</code></pre></section>''')
        if a.get('prompt_en'):
            eid=f'asset-{aid}-prompt-en'
            parts.append(f'''<section class="prompt-secondary"><div class="prompt-head"><div><span>发送生成模型</span><h3>英文 / 目标模型提示词</h3></div><button class="copy-btn mini" data-copy="{eid}">复制生成提示词</button></div><pre id="{eid}"><code>{html.escape(a['prompt_en'])}</code></pre></section>''')
        return '<div class="asset-prompt-console"><div class="prompt-workbench">'+''.join(parts)+'</div><div class="language-note">只核对当前资产实际相关的决策、画面、摄影 / CMF、文案和保真约束。缺失或不相关的维度不应为了“字段完整”被补造；Prompt 是执行合同，不是独立创意来源。</div></div>'

    title_map={'overview':'资产概览','strategy':'策划与决策','visual':'画面与版式','photo':'摄影 / CMF','copy':'文案','production':'生产说明','trace':'合同 / 参数追踪','prompt':'Prompt 执行','qa':'来源 / QA'}
    eyebrow_map={'overview':'WHY','strategy':'DECISION','visual':'VISUAL','photo':'PHOTO / CMF','copy':'COPY','production':'PRODUCTION','trace':'TRACE','prompt':'EXECUTION','qa':'SOURCE / QA'}
    description_map={
        'overview':'快速理解这张资产存在的理由与消费者问题。',
        'strategy':'查看当前资产自己的购买决策、证据和商业假设。',
        'visual':'查看当前资产实际采用的主体、关系、构图和信息层级。',
        'photo':'仅显示本资产真正需要的摄影、灯光、材质、CMF或色彩执行参数。',
        'copy':'查看本资产实际承担的目标市场可见文案与中文说明。',
        'production':'查看与本资产执行方式直接相关的生产备注。',
        'trace':'核对事实、参数与机器合同的来源追踪。',
        'prompt':'执行当前已编译的生产 Prompt；不补造无关参数。',
        'qa':'查看源文件与必要的质量追踪。',
    }
    source_files=a.get('source_files') or []
    for key in ordered_keys:
        if key=='prompt':
            body=prompt_body()
        elif key=='qa':
            if not source_files: continue
            body='<section class="asset-source-ledger"><div class="asset-section-label">源文件账本</div><ul>'+''.join(f'<li>{html.escape(str(x))}</li>' for x in source_files)+'</ul></section>'
        else:
            view=by_key.get(key)
            if not view: continue
            body=view.get('html') or ''
            if not body.strip() or '暂无已确认内容' in body: continue
        panels.append({'key':key,'title':title_map.get(key,by_key.get(key,{}).get('title') or '工作视图'),'eyebrow':eyebrow_map.get(key,'VIEW'),'description':description_map.get(key,'这是由当前资产内容动态生成的工作视图。'),'body':body})

    if not panels:
        panels=[{'key':'empty','title':'资产概览','eyebrow':'ASSET','description':'当前资产还没有可执行的人类工作视图。','body':'<div class="empty">暂无资产内容。</div>'}]

    rail=[];stage=[]
    for i,s in enumerate(panels):
        view=f'asset-view-{_slug(a["id"])}-{s["key"]}'
        active='active' if i==0 else ''
        rail.append(f'''<button class="asset-phase workspace-switch {active}" data-switch-group="{group}" data-view="{view}"><span class="asset-phase-copy"><small>{html.escape(s['eyebrow'])}</small><b>{html.escape(s['title'])}</b></span></button>''')
        stage.append(f'''<section class="asset-stage asset-stage-{_slug(s['key'])} workspace-panel searchable {active}" data-switch-group="{group}" data-view="{view}"><header class="asset-stage-head"><div><span>{html.escape(s['eyebrow'])}</span><h2>{html.escape(s['title'])}</h2><p>{html.escape(s['description'])}</p></div></header><div class="asset-stage-body">{s['body']}</div></section>''')

    sec=f'<div class="asset-original">{html.escape(str(a.get("original_title") or ""))}</div>' if a.get('original_title') and a.get('original_title')!=a.get('title') else ''
    chips=''.join(f'<span>{html.escape(str(_humanize_asset_text(x)))}</span>' for x in [a.get('asset_type'),a.get('surface'),a.get('intent')] if x)
    readiness=[]
    if a.get('prompt_cn'): readiness.append('中文 Prompt 已就绪')
    if a.get('prompt_en'): readiness.append('生成模型 Prompt 已就绪')
    if source_files: readiness.append(f'{len(source_files)} 个源文件可追溯')
    ready_html=''.join(f'<span>{html.escape(x)}</span>' for x in readiness) or '<span>等待当前资产所需合同补齐</span>'
    passport=f'''<div class="asset-passport"><div><span class="asset-passport-id">{html.escape(a['id'])}</span><div class="asset-passport-chips">{chips}</div></div><div class="asset-readiness">{ready_html}</div></div>'''
    return f'''<section class="page asset-page" data-route="asset/{html.escape(a['id'])}"><div class="page-head"><div><a class="back route-link" href="#assets" data-route="assets">← 返回资产中心</a><div class="kicker">资产工作台 <span class="heading-en">{html.escape(a['id'])}</span></div><h1>{html.escape(a['title'])}</h1>{sec}<p>{html.escape(a.get('summary') or '')}</p></div></div>{passport}<div class="asset-production-workspace" data-workspace-kind="asset-production"><aside class="asset-production-rail"><div class="asset-rail-head"><b>当前工作视图</b><span>{len(panels)} 个相关视图 · 无固定先后顺序</span></div>{''.join(rail)}</aside><div class="asset-production-stage">{''.join(stage)}</div></div></section>'''
'''
text=text[:start]+new_func+text[end:]

# Dynamic project-level routes and commands. Primary navigation only shows business objects that exist.
nav_start=text.index("    nav=[('overview','⌂','工作台')")
source_marker="    source_doc_views=_doc_views(docs['sources'],package_dir,'sources') if docs['sources'] else []\n"
source_pos=text.index(source_marker,nav_start)
new_nav=r'''    agent_next_action=_read_json(package_dir/'artifacts/agent_next_action.json',{})
    availability={
        'product':bool(product_views),'market':bool(market_views),'listing':bool(copy_rows or center.get('localized_copy')),
        'strategy':bool(strategy_views),'content':bool(content_views),'visual':bool(visual_views),
        'assets':bool(assets),'prompts':any(a.get('prompt_cn') or a.get('prompt_en') for a in assets),
        'risk':bool(risks or risk_views),'sources':bool(docs['sources']),'archive':bool(machine),
    }
    route_plan=build_workspace_route_plan(availability=availability,agent_next_action=agent_next_action)
    nav_html=''.join(f'<a href="#{row["route"]}" data-route="{row["route"]}" class="route-link"><span class="ico">{row["icon"]}</span>{row["label"]}</a>' for row in route_plan['primary_routes'])
    commands=''.join(f'<a class="command-card route-link" href="#{row["route"]}" data-route="{row["route"]}"><b>{html.escape(str(row["name"]))}</b><span>{html.escape(str(row["description"]))}</span></a>' for row in route_plan['commands']) or '<div class="empty">当前没有需要额外推进的工作对象；可在现有项目范围内复核或停止。</div>'
    archive_link=''.join(f'<a class="route-link secondary-route" href="#{row["route"]}" data-route="{row["route"]}">{row["label"]}</a>' for row in route_plan['secondary_routes'])

'''
text=text[:nav_start]+new_nav+text[source_pos:]

# Include media/source files in source-route availability after they are discovered.
needle="    machine_html=''.join(machine) or '<div class=\"empty\">暂无结构化归档。</div>'\n\n    css=f'''\n"
replacement="""    machine_html=''.join(machine) or '<div class=\"empty\">暂无结构化归档。</div>'
    if media or source_doc_views or source_files:
        availability['sources']=True
    availability['archive']=bool(machine)
    route_plan=build_workspace_route_plan(availability=availability,agent_next_action=agent_next_action)
    nav_html=''.join(f'<a href=\"#{row[\"route\"]}\" data-route=\"{row[\"route\"]}\" class=\"route-link\"><span class=\"ico\">{row[\"icon\"]}</span>{row[\"label\"]}</a>' for row in route_plan['primary_routes'])
    commands=''.join(f'<a class=\"command-card route-link\" href=\"#{row[\"route\"]}\" data-route=\"{row[\"route\"]}\"><b>{html.escape(str(row[\"name\"]))}</b><span>{html.escape(str(row[\"description\"]))}</span></a>' for row in route_plan['commands']) or '<div class=\"empty\">当前没有需要额外推进的工作对象；可在现有项目范围内复核或停止。</div>'
    archive_link=''.join(f'<a class=\"route-link secondary-route\" href=\"#{row[\"route\"]}\" data-route=\"{row[\"route\"]}\">{row[\"label\"]}</a>' for row in route_plan['secondary_routes'])

    css=f'''\n"""
text=replace_once(text,needle,replacement,'refresh dynamic route availability')

# Replace static page table-of-contents projection with pages generated only for available objects.
pages_start=text.index("    pages=f'''\n<section class=\"page\" data-route=\"overview\">")
pages_end=text.index("\n\n    js=r'''",pages_start)
new_pages=r'''    stat_rows=[]
    if availability.get('listing'):
        stat_rows += [(ready,'上架字段就绪'),(pending,'待补 / 待查证')]
        if companion_missing: stat_rows.append((companion_missing,'待补中文释义'))
    if assets: stat_rows.append((len(assets),'当前资产'))
    if risks: stat_rows.append((len(risks),'结构化风险'))
    stats_html=''.join(f'<div class="stat"><strong>{value}</strong><span>{html.escape(label)}</span></div>' for value,label in stat_rows)
    next_status=str(agent_next_action.get('recommended_next_action') or 'STOP_CURRENT_SCOPE_SATISFIED')
    next_frontier=agent_next_action.get('frontier') or []
    next_items=''.join(f'<li><b>{html.escape(str(x.get("action") or "下一步"))}</b><span>{html.escape(str(x.get("reason") or ""))}</span></li>' for x in next_frontier)
    if not next_items: next_items='<li><b>当前范围可停止</b><span>没有检测到必须继续推进的固定步骤；由 Agent / 用户决定是否扩展目标。</span></li>'

    page_parts=[]
    page_parts.append(f'''<section class="page" data-route="overview"><div class="page-head"><div><div class="kicker">电商工作区</div><h1>{html.escape(product_name)}</h1>{f'<div class="heading-en project-original">{html.escape(product_name_secondary)}</div>' if product_name_secondary else ''}<p>工作台只显示当前项目真实存在的业务对象和 Agent 识别到的下一步，不按固定报告目录展开。</p></div></div>{f'<div class="stats">{stats_html}</div>' if stats_html else ''}<div class="panel"><h2>当前可以做什么？</h2><div class="command-grid">{commands}</div></div><div class="panel agent-frontier"><h2>Agent 决策前沿</h2><p><b>建议：</b>{html.escape(next_status)}</p><ul>{next_items}</ul></div><div class="panel"><h2>项目语言</h2><p><b>交付语言：</b>{html.escape(str(delivery_locale))}（默认中文，除非用户明确要求其他语言）</p><p><b>目标市场语言：</b>{html.escape(str(target_locale))}。目标语言上架文案 / 资产文案保留原文，同时显示中文释义或用途说明。</p></div></section>''')
    if availability.get('product'): page_parts.append(f'''<section class="page" data-route="product"><div class="page-head"><div><div class="kicker">商品真源 / 证据</div><h1>产品事实与证据</h1><p>只呈现当前项目实际存在的事实、证据与缺口主题。</p></div></div>{product_ws}</section>''')
    if availability.get('market'): page_parts.append(f'''<section class="page" data-route="market"><div class="page-head"><div><div class="kicker">目标市场语境</div><h1>市场、平台、人群与文化</h1><p>研究主题来自当前决策缺口；没有固定竞品数、报告章节数或研究配额。</p></div></div>{market_ws}</section>''')
    if availability.get('listing'): page_parts.append(f'''<section class="page" data-route="listing"><div class="page-head"><div><div class="kicker">上架工作室</div><h1>上架资料中心</h1><p>只呈现当前上架任务涉及的字段；目标市场文案保留目标语言，并提供中文释义 / 用途。</p></div></div>{listing_ws}</section>''')
    if availability.get('strategy'): page_parts.append(f'''<section class="page" data-route="strategy"><div class="page-head"><div><div class="kicker">策略工作室</div><h1>营销与商业决策</h1><p>以当前商品需要解决的决策为单位阅读；框架只在 Agent / 用户选择并确实有用时出现。</p></div></div>{strategy_ws}</section>''')
    if availability.get('content'): page_parts.append(f'''<section class="page" data-route="content"><div class="page-head"><div><div class="kicker">内容系统</div><h1>平台内容与传播对象</h1><p>内容对象、叙事、Surface 与数量由当前消费者问题和商业任务动态产生；不预设 Hook / CTA / 固定传播阶段。</p></div></div>{content_ws}</section>''')
    if availability.get('visual'): page_parts.append(f'''<section class="page" data-route="visual"><div class="page-head"><div><div class="kicker">视觉工作室</div><h1>视觉、摄影与 CMF</h1><p>只显示当前项目真正采用的创意、构图、摄影、材质和颜色决策；无关参数保持缺席。</p></div></div>{visual_ws}</section>''')
    if availability.get('assets'): page_parts.append(f'''<section class="page" data-route="assets"><div class="page-head"><div><div class="kicker">资产工作室</div><h1>资产中心</h1><p>每个资产拥有自己的工作视图；视图按实际内容出现，不是一条必须依次完成的流水线。</p></div></div><div class="asset-grid">{asset_cards}</div></section>''')
    if availability.get('prompts'): page_parts.append(f'''<section class="page" data-route="prompts"><div class="page-head"><div><div class="kicker">提示词工作室</div><h1>提示词工作台</h1><p>Prompt 只投影当前资产真正需要的执行参数；中文生产说明与目标模型提示词同屏核对。</p></div></div>{prompt_ws}</section>''')
    if availability.get('risk'): page_parts.append(f'''<section class="page" data-route="risk"><div class="page-head"><div><div class="kicker">风险中心</div><h1>风险、合规与待查证</h1><p>区分真正阻断执行的硬边界与 Agent 可继续研究的 advisory gap。</p></div></div><div class="panel">{risk_cards}</div>{risk_ws}</section>''')
    if availability.get('sources'): page_parts.append(f'''<section class="page" data-route="sources"><div class="page-head"><div><div class="kicker">证据中心</div><h1>来源与产品真源</h1><p>只在当前项目存在来源媒体、证据文档或源文件时出现。</p></div></div>{sources_ws}</section>''')
    if availability.get('archive'): page_parts.append(f'''<section class="page" data-route="archive"><div class="page-head"><div><div class="kicker">机器归档</div><h1>完整结构化归档</h1><p>仅用于追溯和机器合同，不进入一级人类工作导航。</p></div></div><div class="panel">{machine_html}</div></section>''')
    page_parts.extend(_asset_page(a) for a in assets)
    pages=''.join(page_parts)
'''
text=text[:pages_start]+new_pages+text[pages_end:]

# Sidebar archive remains a secondary trace link, not a top-level work route.
old="""<div class=\"sidebar-foot\">默认中文交付<br>目标语言文案 + 中文释义<br>HTML = 完整人类交付</div>"""
new="""<div class=\"sidebar-foot\">默认中文交付<br>目标语言文案 + 中文释义<br>HTML = 完整人类交付<br>{archive_link}</div>"""
text=replace_once(text,old,new,'secondary archive link')

p.write_text(text,encoding='utf-8')
