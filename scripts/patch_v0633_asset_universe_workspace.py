from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def replace(path:str,old:str,new:str, *, all_occurrences:bool=True):
    p=ROOT/path
    text=p.read_text(encoding='utf-8')
    if old not in text:
        if new in text: return
        raise SystemExit(f'missing anchor {path}: {old[:120]!r}')
    text=text.replace(old,new) if all_occurrences else text.replace(old,new,1)
    p.write_text(text,encoding='utf-8')

# Preserve variant/testing/deployment metadata in each compiled asset package.
replace('runtime/cbcc/asset_compiler.py',
"'asset_id','asset_name','asset_type','status','surface','family','consumer_question','decision_intent','decision_topic','merged_consumer_questions','strategic_job'",
"'asset_id','asset_name','asset_type','status','surface','family','variant_id','variant_cluster','deployment_state','testing_variant','test_hypothesis','activation_set_id','consumer_question','decision_intent','decision_topic','merged_consumer_questions','strategic_job'")
replace('runtime/cbcc/asset_compiler.py',
"        f\"- Surface / Family：{asset.get('surface')} / {asset.get('family')}\",\n        f\"- 优先级：{asset.get('priority')}\",",
"        f\"- Surface / Family：{asset.get('surface')} / {asset.get('family')}\",\n        f\"- 资产簇 / Variant：{asset.get('variant_cluster') or '—'} / {asset.get('variant_id') or '—'}\",\n        f\"- 部署状态：{asset.get('deployment_state') or 'LIVE_CANDIDATE'}\",\n        f\"- 测试假设：{asset.get('test_hypothesis') or asset.get('business_hypothesis') or '—'}\",\n        f\"- 优先级：{asset.get('priority')}\",")

# Human HTML reads the new metadata instead of losing it at the parser boundary.
replace('runtime/cbcc/delivery_html.py',
"        for key in ['asset_name','surface','decision_intent','consumer_question','asset_type','production_mode']:",
"        for key in ['asset_name','surface','decision_intent','consumer_question','asset_type','production_mode','variant_id','variant_cluster','deployment_state','test_hypothesis','activation_set_id']:")
replace('runtime/cbcc/delivery_html.py',
"    return {'id':aid,'title':display_title,'original_title':original_title,'summary':summary,'prompt_cn':prompt_cn,'prompt_en':prompt_en,'model_prompt_status':prompt_contract.get('model_prompt_status'),'views':views,'source_files':src,'surface':surface,'intent':intent,'asset_type':asset_type,'agent_view_order':design.get('workspace_view_order') or design.get('agent_view_order') or []}",
"    return {'id':aid,'title':display_title,'original_title':original_title,'summary':summary,'prompt_cn':prompt_cn,'prompt_en':prompt_en,'model_prompt_status':prompt_contract.get('model_prompt_status'),'views':views,'source_files':src,'surface':surface,'intent':intent,'asset_type':asset_type,'variant_id':design.get('variant_id') or manifest.get('variant_id'),'variant_cluster':design.get('variant_cluster') or manifest.get('variant_cluster'),'deployment_state':design.get('deployment_state') or manifest.get('deployment_state'),'test_hypothesis':design.get('test_hypothesis') or manifest.get('test_hypothesis'),'activation_set_id':design.get('activation_set_id') or manifest.get('activation_set_id'),'agent_view_order':design.get('workspace_view_order') or design.get('agent_view_order') or []}")

# Replace only the _asset_card function block using function boundaries, not a 100k-file literal.
p=ROOT/'runtime/cbcc/delivery_html.py'
text=p.read_text(encoding='utf-8')
if 'def _asset_universe_cards(' not in text:
    start=text.find('def _asset_card(a:dict[str,Any])->str:')
    if start < 0: raise SystemExit('missing _asset_card function')
    nxt=text.find('\ndef ', start+10)
    if nxt < 0: raise SystemExit('missing function boundary after _asset_card')
    block='''def _asset_card(a:dict[str,Any])->str:\n    orig=a.get('original_title') or ''\n    sec=f'<small>{html.escape(orig)}</small>' if orig and orig!=a.get('title') else ''\n    chips=''.join(f'<span>{html.escape(str(_humanize_asset_text(x)))}</span>' for x in [a.get('asset_type'),a.get('surface'),a.get('variant_cluster'),a.get('variant_id'),a.get('deployment_state'),a.get('intent')] if x)\n    hypothesis=f'<p><strong>测试 / 创意假设：</strong>{html.escape(str(a.get("test_hypothesis")))}</p>' if a.get('test_hypothesis') else ''\n    return f\'''<a class="asset-card searchable route-link" href="#asset/{html.escape(a['id'])}" data-route="asset/{html.escape(a['id'])}"><div class="asset-top"><b>{html.escape(a['id'])}</b><div class="asset-chips">{chips}</div></div><h3>{html.escape(a['title'])}</h3>{sec}<p>{html.escape(a.get('summary') or '打开查看完整资产工作区')}</p>{hypothesis}<span class="asset-open">进入资产工作区 →</span></a>\'''\n\n\ndef _asset_universe_cards(assets:list[dict[str,Any]])->str:\n    if not assets:\n        return '<div class="empty">暂无资产。</div>'\n    groups=[\n      ('LIVE_CANDIDATE','当前上线候选','可进入当前平台 activation set；平台槽位只限制这里同时上线数量。'),\n      ('TEST_POOL','测试池','用于 A/B、Hero 方向、卖点、构图、人群与文案假设测试；不受当前平台槽位总数限制。'),\n      ('ROTATION_POOL','轮换池','已生产、可按周期或数据表现替换上线的资产。'),\n      ('PAID_MEDIA','广告资产','Paid Ads / Retargeting / Hook 等广告创意资产。'),\n      ('PDP_CONTENT','PDP / A+ / 详情','A+、详情模块、长图、说明/证据/FAQ 等丰富内容。'),\n      ('ARCHIVE','归档','暂不激活但保留用于复盘、复用或历史对照的资产。'),\n      ('OTHER','其他资产','Store、Banner、Social、Creator、Video 等按实际 Surface 使用的资产。'),\n    ]\n    buckets={k:[] for k,_,_ in groups}\n    for a in assets:\n        state=str(a.get('deployment_state') or '').upper()\n        if state not in buckets:\n            surface=str(a.get('surface') or '').upper()\n            if surface=='PAID_AD': state='PAID_MEDIA'\n            elif surface in {'A_PLUS','LONGFORM'}: state='PDP_CONTENT'\n            elif surface in {'STORE_BANNER','SOCIAL_CONTENT','CREATOR','SHORT_VIDEO','PDP_VIDEO','LIVE'}: state='OTHER'\n            else: state='LIVE_CANDIDATE'\n        buckets[state].append(a)\n    out=[]\n    for key,title,desc in groups:\n        rows=buckets[key]\n        if not rows: continue\n        out.append(f'<section class="panel asset-universe-group"><div class="page-head"><div><span class="kicker">ASSET UNIVERSE · {html.escape(key)}</span><h2>{html.escape(title)} · {len(rows)}</h2><p>{html.escape(desc)}</p></div></div><div class="asset-grid">'+''.join(_asset_card(a) for a in rows)+'</div></section>')\n    return ''.join(out)\n\n'''
    text=text[:start]+block+text[nxt+1:]
    p.write_text(text,encoding='utf-8')

# Replace flat cards with the operational Asset Universe grouping.
replace('runtime/cbcc/delivery_html.py',
"    asset_cards=''.join(_asset_card(a) for a in assets) or '<div class=\"empty\">暂无资产。</div>'",
"    asset_cards=_asset_universe_cards(assets)")

# Asset detail passport also shows variant/deployment identity. Replace any remaining old chips form.
replace('runtime/cbcc/delivery_html.py',
"[a.get('asset_type'),a.get('surface'),a.get('intent')] if x)",
"[a.get('asset_type'),a.get('surface'),a.get('variant_cluster'),a.get('variant_id'),a.get('deployment_state'),a.get('intent')] if x)")

# Production notes expose native-reference generation explicitly.
replace('runtime/cbcc/delivery_html.py',
"('文字渲染路线',production_notes.get('copy_render_mode')),('产品 Fidelity',production_notes.get('product_fidelity')),('产品出现方式',production_notes.get('product_presence')),('产品参考规则',production_notes.get('product_reference_rule'))",
"('文字渲染路线',production_notes.get('copy_render_mode')),('产品 Fidelity',production_notes.get('product_fidelity')),('商品参考生成方式',production_notes.get('product_reference_generation_mode')),('真实商品 Reference Input',production_notes.get('reference_input_required')),('最终商品必须原生生成',production_notes.get('final_output_must_contain_generated_product')),('产品出现方式',production_notes.get('product_presence')),('产品参考规则',production_notes.get('product_reference_rule'))")

print('v0.6.33 asset universe human workspace patched')
