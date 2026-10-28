from pathlib import Path

# 1) Prompt inheritance: asset-specific reasoning makes the selected strategy photography parameters relevant.
p=Path('runtime/cbcc/prompt_compiler.py')
text=p.read_text(encoding='utf-8')
old="inherit_global=bool(explicit.get('inherit_strategy_photography') or reasoning.get('inherit_strategy_photography') or capture_mode=='REAL_PHOTO')"
new="inherit_global=bool(explicit.get('inherit_strategy_photography') or reasoning.get('inherit_strategy_photography') or bool(reasoning) or capture_mode=='REAL_PHOTO')"
if old not in text and new not in text:
    raise SystemExit('missing prompt inherit_global target')
text=text.replace(old,new,1)
p.write_text(text,encoding='utf-8')

# 2) Asset workspace: dynamic lenses, no mandatory sequence; preserve decision grouping and all trace/legacy material.
p=Path('runtime/cbcc/delivery_html.py')
text=p.read_text(encoding='utf-8')
start=text.index('def _asset_page(a:dict[str,Any])->str:\n')
end=text.index('\ndef _json_panel(',start)
new_func=r'''def _asset_page(a:dict[str,Any])->str:
    raw_views=list(a.get('views') or [])
    by_key={str(v.get('key') or ''):v for v in raw_views if isinstance(v,dict)}
    raw_order=relevant_asset_view_keys(a)
    group=f'asset-workspace-{_slug(a["id"])}'
    lenses={}

    def add(key:str,title:str,eyebrow:str,description:str,body:str):
        if body and body.strip() and '暂无已确认内容' not in body:
            lenses[key]={'key':key,'title':title,'eyebrow':eyebrow,'description':description,'body':body}

    # Decision lens groups the Design Card overview and strategy because they answer one work object,
    # but it is not a first step and carries no execution-order authority.
    decision_parts=[]
    for key,label in [('overview','Design Card 概览'),('strategy','购买决策')]:
        view=by_key.get(key)
        if view and (view.get('html') or '').strip():
            decision_parts.append(f'<section class="asset-decision-block"><div class="asset-section-label">{label}</div>{view.get("html") or ""}</section>')
    if decision_parts:
        add('decision','决策 / Design Card','WHY · DECISION','查看这张资产为什么存在、要解决什么购买判断以及依据。',''.join(decision_parts))

    direct={
        'visual':('画面执行','VISUAL','查看当前资产实际采用的主体、关系、构图与信息层级。'),
        'photo':('摄影 / CMF','PHOTO · CMF','仅显示本资产真正需要的摄影、灯光、材质、CMF 或色彩执行参数。'),
        'copy':('文案','COPY','查看本资产实际承担的目标市场可见文案与中文说明。'),
        'production':('生产说明','PRODUCTION','查看与本资产执行方式直接相关的生产备注。'),
    }
    for key,(title,eyebrow,desc) in direct.items():
        view=by_key.get(key)
        if view:
            add(key,title,eyebrow,desc,view.get('html') or '')

    if a.get('prompt_cn') or a.get('prompt_en'):
        parts=[];aid=_slug(a['id'])
        if a.get('prompt_cn'):
            cid=f'asset-{aid}-prompt-cn'
            parts.append(f'''<section class="prompt-primary"><div class="prompt-head"><div><span>人类生产说明</span><h3>中文规范生产提示词</h3></div><button class="copy-btn mini" data-copy="{cid}">复制中文</button></div><pre id="{cid}"><code>{html.escape(a['prompt_cn'])}</code></pre></section>''')
        if a.get('prompt_en'):
            eid=f'asset-{aid}-prompt-en'
            parts.append(f'''<section class="prompt-secondary"><div class="prompt-head"><div><span>发送生成模型</span><h3>英文 / 目标模型提示词</h3></div><button class="copy-btn mini" data-copy="{eid}">复制生成提示词</button></div><pre id="{eid}"><code>{html.escape(a['prompt_en'])}</code></pre></section>''')
        body='<div class="asset-prompt-console"><div class="prompt-workbench">'+''.join(parts)+'</div><div class="language-note">只核对当前资产实际相关的决策、画面、摄影 / CMF、文案和保真约束。缺失或不相关的维度不应为了“字段完整”被补造；Prompt 是执行合同，不是独立创意来源。</div></div>'
        add('prompt','Prompt 执行','EXECUTION','执行当前已编译的生产 Prompt；不补造无关参数。',body)

    # QA/trace is one recoverability lens: machine trace, source files and unknown legacy views all remain accessible.
    qa_parts=[]
    trace=by_key.get('trace')
    if trace and (trace.get('html') or '').strip():
        qa_parts.append('<section class="asset-qa-source"><div class="asset-section-label">合同 / 参数追踪</div>'+str(trace.get('html') or '')+'</section>')
    known={'overview','strategy','visual','photo','copy','production','trace'}
    for view in raw_views:
        if not isinstance(view,dict): continue
        key=str(view.get('key') or '')
        if key in known: continue
        body=str(view.get('html') or '').strip()
        if not body: continue
        title=str(view.get('title') or '补充资料')
        qa_parts.append(f'<section class="asset-qa-source"><div class="asset-section-label">{html.escape(title)}</div>{body}</section>')
    source_files=a.get('source_files') or []
    if source_files:
        qa_parts.append('<section class="asset-source-ledger"><div class="asset-section-label">源文件账本</div><ul>'+''.join(f'<li>{html.escape(str(x))}</li>' for x in source_files)+'</ul></section>')
    if qa_parts:
        add('qa','QA / 来源','TRACE · QA','核对事实、参数、机器合同、源文件与兼容性资料；这些追踪信息不进入生成 Prompt。',''.join(qa_parts))

    # Agent-authored order wins. Otherwise use a stable UI reading order only for presentation;
    # absent lenses are never manufactured and this order has no planning/execution authority.
    alias={'overview':'decision','strategy':'decision','trace':'qa','qa':'qa','prompt':'prompt'}
    explicit=list(a.get('agent_view_order') or a.get('workspace_view_order') or [])
    order=[]
    for key in explicit:
        mapped=alias.get(str(key),str(key))
        if mapped in lenses and mapped not in order: order.append(mapped)
    for raw in raw_order:
        mapped=alias.get(str(raw),str(raw))
        if mapped not in lenses and str(raw) not in known and 'qa' in lenses: mapped='qa'
        if mapped in lenses and mapped not in order: order.append(mapped)
    for key in ['decision','visual','photo','copy','production','prompt','qa']:
        if key in lenses and key not in order: order.append(key)

    panels=[lenses[k] for k in order]
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
p.write_text(text,encoding='utf-8')

# 3) Update only the obsolete presentation wording in the older workspace regression.
p=Path('tests/test_v068_asset_production_workspace.py')
text=p.read_text(encoding='utf-8')
text=text.replace("assert '2 个动态阶段' not in page\n    assert '1 个动态阶段' in page", "assert '2 个相关视图' not in page\n    assert '1 个相关视图' in page\n    assert '无固定先后顺序' in page")
text=text.replace('data-view="asset-stage-lst-03-decision"','data-view="asset-view-lst-03-decision"')
p.write_text(text,encoding='utf-8')
