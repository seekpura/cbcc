from __future__ import annotations

from pathlib import Path
import html
import json


def _load(path:Path)->dict:
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return {}


def _e(v)->str:
    if v in (None,''): return '—'
    if isinstance(v,(dict,list)): return html.escape(json.dumps(v,ensure_ascii=False))
    return html.escape(str(v))


def _copy_text(v)->str:
    if v in (None,''): return '—'
    if isinstance(v,str): return html.escape(v)
    return '<code>'+_e(v)+'</code>'


def _style()->str:
    return '''<style id="cbcc-operator-execution-style">
#operator-execution{padding:30px 0}.op-hero{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(260px,.6fr);gap:16px;margin-bottom:16px}.op-card{background:#fff;border:1px solid var(--line,#ddd);border-radius:18px;padding:18px;box-shadow:0 8px 26px rgba(20,35,28,.035)}.op-kicker{font-size:10px;letter-spacing:.09em;color:var(--muted,#666);text-transform:uppercase}.op-card h2,.op-card h3{margin:5px 0 10px}.op-card p{margin:6px 0;line-height:1.6}.op-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}.op-table-wrap{overflow:auto}.op-table{width:100%;border-collapse:collapse;font-size:12px}.op-table th,.op-table td{padding:9px 8px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line,#ddd)}.op-table th{font-size:10px;color:var(--muted,#666);white-space:nowrap}.op-badge{display:inline-block;border:1px solid var(--line,#ddd);border-radius:999px;padding:3px 8px;font-size:10px;margin:1px 3px 1px 0}.op-p0{font-weight:800}.op-section{margin:16px 0}.op-copy{white-space:pre-wrap;line-height:1.55}.op-muted{color:var(--muted,#666);font-size:11px}.op-details{margin-top:10px}.op-details summary{cursor:pointer;font-weight:700}.op-asset{display:grid;grid-template-columns:minmax(0,1fr) minmax(220px,.45fr);gap:14px}.op-object-id{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10px;color:var(--muted,#666)}
@media(max-width:800px){.op-hero,.op-asset{grid-template-columns:1fr}.op-card{padding:14px}.op-table{font-size:11px}}
</style>'''


def _launch(board:dict)->str:
    rows=[]
    for r in board.get('launch_board') or []:
        rows.append('<tr>'
            f'<td class="op-p0">{_e(r.get("priority"))}</td>'
            f'<td>{_e(r.get("owner"))}</td>'
            f'<td><b>{_e(r.get("exact_action"))}</b><div class="op-muted">目标：{_e(r.get("target_object"))}</div></td>'
            f'<td>{_e(r.get("artifact_or_object"))}</td>'
            f'<td>{_e(r.get("completion_check"))}</td>'
            '</tr>')
    if not rows: return '<p class="op-muted">当前没有需要排队的运营动作。</p>'
    return '<div class="op-table-wrap"><table class="op-table"><thead><tr><th>优先级</th><th>负责人</th><th>现在做什么</th><th>直接使用</th><th>完成标准</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'


def _listing(board:dict)->str:
    listing=board.get('listing_release') or {}; chunks=[]
    for pkg in listing.get('packages') or []:
        rows=[]
        for f in pkg.get('fields') or []:
            rows.append('<tr>'
                f'<td>{_e(f.get("field"))}</td>'
                f'<td><div class="op-copy">{_copy_text(f.get("final_or_current_copy"))}</div></td>'
                f'<td><div class="op-copy">{_copy_text(f.get("delivery_translation_zh"))}</div></td>'
                f'<td><span class="op-badge">{_e(f.get("release_status"))}</span></td>'
                f'<td>{_e(f.get("operator_action"))}</td>'
                '</tr>')
        chunks.append(f'<h3>{_e(pkg.get("locale"))} · {_e(pkg.get("status"))}</h3><div class="op-table-wrap"><table class="op-table"><thead><tr><th>字段</th><th>目标市场最终/当前文案</th><th>中文释义/用途</th><th>状态</th><th>运营动作</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    return ''.join(chunks) or '<p class="op-muted">当前项目未提供 Listing 发布对象。</p>'


def _assets(board:dict)->str:
    asset_board=board.get('asset_production_board') or {}; chunks=[]
    for a in asset_board.get('assets') or []:
        copy=a.get('visible_copy') or {}
        chunks.append('<article class="op-card op-asset">'
            '<div>'
            f'<div class="op-object-id">{_e(a.get("asset_id"))} · {_e(a.get("surface"))} · {_e(a.get("activation_state"))}</div>'
            f'<h3>{_e(a.get("asset_name") or a.get("commercial_job") or a.get("asset_id"))}</h3>'
            f'<p><b>购买问题：</b>{_e(a.get("shopper_question"))}</p>'
            f'<p><b>商业任务：</b>{_e(a.get("commercial_job"))}</p>'
            f'<p><b>创意假设：</b>{_e(a.get("creative_hypothesis"))}</p>'
            f'<p><b>视觉载体：</b>{_e(a.get("visual_carrier"))}</p>'
            f'<p><b>商品出现：</b>{_e(a.get("product_presence"))}</p>'
            f'<p><b>可见文案：</b><span class="op-copy">{_copy_text(copy)}</span></p>'
            '</div><div>'
            f'<span class="op-badge">{_e(a.get("release_status"))}</span>'
            f'<p><b>生产路线：</b>{_e(a.get("production_route"))}</p>'
            f'<p><b>逐资产包：</b>{_e(a.get("compiled_package_path"))}</p>'
            f'<p><b>Provider：</b>{_e(a.get("compiled_provider"))}</p>'
            f'<p>{_e(a.get("operator_action"))}</p>'
            '</div></article>')
    return '<div class="op-grid">'+''.join(chunks)+'</div>' if chunks else '<p class="op-muted">当前没有资产生产对象。</p>'


def _simple_json_card(title:str,obj)->str:
    return f'<article class="op-card"><div class="op-kicker">OPERATOR OBJECT</div><h3>{html.escape(title)}</h3><details class="op-details"><summary>展开完整对象</summary><pre>{_e(obj)}</pre></details></article>'


def operator_execution_html(package_dir:Path)->str:
    board=_load(Path(package_dir)/'artifacts/operator_execution_board.json')
    if not board: return ''
    thesis=board.get('commercial_thesis') or {}; release=board.get('release_status') or {}
    top=_style()+'''<section id="operator-execution" class="section">
<div class="section-head"><div><div class="eyebrow">OPERATOR EXECUTION</div><h2>运营执行台</h2><p>先看“今天做什么”，再进入策略与 Runtime Inspector。目标市场文案保留原文，中文负责运营理解。</p></div></div>'''
    top+='<div class="op-hero"><article class="op-card"><div class="op-kicker">COMMERCIAL THESIS</div><h2>'+_e(thesis.get('primary_conversion_proposition'))+'</h2><p><b>目标用户：</b>'+_e(thesis.get('target_user'))+'</p><p><b>执行原则：</b>'+_e(thesis.get('operator_read'))+'</p></article>'
    top+='<article class="op-card"><div class="op-kicker">RELEASE STATUS</div><h3>'+_e(release.get('state'))+'</h3><p><b>Compliance：</b>'+_e(release.get('compliance_status'))+'</p><p><b>Asset Compile：</b>'+_e(release.get('asset_compile_status'))+'</p><p><b>Production：</b>'+_e(release.get('production_status'))+'</p></article></div>'
    top+='<section class="op-section op-card"><div class="op-kicker">LAUNCH BOARD</div><h2>现在做什么</h2>'+_launch(board)+'</section>'
    top+='<section class="op-section op-card"><div class="op-kicker">LISTING RELEASE</div><h2>可发布 Listing</h2>'+_listing(board)+'</section>'
    top+='<section class="op-section"><div class="op-kicker">ASSET PRODUCTION BOARD</div><h2>逐资产直接生产</h2>'+_assets(board)+'</section>'
    top+='<section class="op-section op-grid">'+_simple_json_card('视频生产对象',board.get('video_production_board') or {})+_simple_json_card('Paid Test Queue',board.get('paid_test_queue') or {})+_simple_json_card('评论 / 退货 / 客服修订队列',board.get('review_revision_queue') or {})+_simple_json_card('Economics Control Panel',board.get('economics_control_panel') or {})+'</section>'
    top+='</section>'
    return top


def inject_operator_execution(page:str,package_dir:Path)->str:
    block=operator_execution_html(package_dir)
    if not block or 'id="operator-execution"' in page: return page
    # Operator execution is primary: inject immediately after <main> when possible.
    marker='<main>'
    if marker in page: return page.replace(marker,marker+block,1)
    marker='</body>'
    return page.replace(marker,block+marker,1)
