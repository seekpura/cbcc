from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import html
import json
import re

from .canonical_human_compaction_v0672 import DATA_FILE, build_canonical_human_payload, expected_visible_paths

LAZY_MARKER = 'CBCC_CANONICAL_LAZY_PROJECTION_V0672'
_COMPACT_ROUTES = ('product','market','listing','strategy','content','visual','prompts','risk','sources','archive')


def _route_spans(page: str) -> list[re.Match[str]]:
    return list(re.finditer(r'<section class="page(?: [^"]*)?" data-route="([^"]+)">', page))


def _replace_route_body(page: str, route: str, body: str) -> tuple[str, bool]:
    starts = _route_spans(page)
    for i, match in enumerate(starts):
        if match.group(1) != route: continue
        block_end = starts[i+1].start() if i+1 < len(starts) else len(page)
        block = page[match.start():block_end]; close = block.rfind('</section>')
        if close < 0: return page, False
        close_pos = match.start() + close
        return page[:match.end()] + body + page[close_pos:], True
    return page, False


def _insert_route(page: str, route: str, fragment: str) -> tuple[str, bool]:
    starts = _route_spans(page)
    for i, match in enumerate(starts):
        if match.group(1) != route: continue
        block_end = starts[i+1].start() if i+1 < len(starts) else len(page)
        block = page[match.start():block_end]; close = block.rfind('</section>')
        if close < 0: return page[:block_end] + fragment + page[block_end:], True
        pos = match.start() + close
        return page[:pos] + fragment + page[pos:], True
    return page, False


def _placeholder(route: str) -> str:
    return '<div class="panel cbcc-legacy-compacted-v0672" data-legacy-compacted-route="' + html.escape(route, quote=True) + '"><p>旧重复投影已压缩；该路由由 Canonical Human Workspace 单源按需展开。</p></div>'


def _strip_prior_projection(page: str) -> str:
    ids = ('cbcc-canonical-human-projection-v0670','cbcc-canonical-human-completion-v0670','cbcc-canonical-static-projection-v0672','cbcc-canonical-static-style-v0672','cbcc-canonical-data-v0672','cbcc-canonical-lazy-projection-v0672','cbcc-canonical-lazy-style-v0672')
    for node_id in ids:
        page = re.sub(rf'<script[^>]+id="{re.escape(node_id)}"[^>]*>.*?</script>\s*', '', page, flags=re.S)
        page = re.sub(rf'<style[^>]+id="{re.escape(node_id)}"[^>]*>.*?</style>\s*', '', page, flags=re.S)
    return page


def _compact(page: str, asset_ids: list[str]) -> tuple[str, dict[str, Any]]:
    before = len(page.encode('utf-8')); page = _strip_prior_projection(page); compacted=[]
    for route in [*_COMPACT_ROUTES, *[f'asset/{aid}' for aid in asset_ids]]:
        page, found = _replace_route_body(page, route, _placeholder(route))
        if found: compacted.append(route)
    after = len(page.encode('utf-8'))
    return page, {'status':'APPLIED','routes_compacted':compacted,'bytes_before':before,'bytes_after':after,'bytes_removed':max(0,before-after)}


def _mount(title: str, path: str, note: str = '') -> str:
    return '<details class="panel cbcc-canonical-v0672 cbcc-canonical-mount-panel"><summary><strong>' + html.escape(title) + '</strong></summary>' + (f'<p>{html.escape(note)}</p>' if note else '') + f'<div data-canonical-mount="{html.escape(path, quote=True)}"></div></details>'


def _asset_index(assets: list[dict[str, Any]]) -> str:
    out=['<div class="panel cbcc-canonical-v0672"><h2>逐资产生产对象索引</h2><p>每个 00–15 资产对象只在自己的 Asset Detail 路由按需展开。</p><ul>']
    for asset in assets:
        aid=str(asset.get('id') or asset.get('asset_id') or '')
        if aid: out.append(f'<li><a href="#asset/{html.escape(aid, quote=True)}">{html.escape(aid)}</a></li>')
    out.append('</ul></div>'); return ''.join(out)


def _mount_routes(page: str, assets: list[dict[str, Any]]) -> str:
    plan={
        'product':[_mount('Product Truth / 产品真源','truth')],
        'market':[_mount('Market / Platform / Audience / Culture','market')],
        'listing':[_mount('Canonical Listing / 上架完整字段','listing')],
        'strategy':[_mount('Canonical Strategy / 商业决策完整字段','strategy')],
        'visual':[_mount('Visual / Photography / Inclusive','visual')],
        'content':[_mount('Content Matrix','content'),_mount('RACE','race'),_mount('Culture','culture'),_mount('Ads','ads')],
        'risk':[_mount('Compliance','compliance'),_mount('Reviews / Learning Loop','reviews'),_mount('Sources','sources')],
        'sources':[_mount('Canonical Business Objects / 完整字段档案','canonical_business_objects','完整业务对象只存一份；展开时按需构造 DOM。'),_mount('Asset Universe / 完整候选与家族扫描','universe')],
        'archive':[_mount('Canonical Business Objects / Archive','canonical_business_objects')],
    }
    for route,fragments in plan.items(): page,_=_insert_route(page,route,''.join(fragments))
    index=_asset_index(assets); page,inserted=_insert_route(page,'prompts',index)
    if not inserted: page,_=_insert_route(page,'assets',index)
    fallback=[]
    for i,asset in enumerate(assets):
        aid=str(asset.get('id') or asset.get('asset_id') or '')
        panel=_mount(f'{aid or "Asset"} · 00–15 完整生产对象',f'assets[{i}]','Visual / Photography / Layout / Prompt / Source Trace / Strategy Trace / Visible Copy / Production / Lineage 均来自同一 Canonical payload。')
        page,found=_insert_route(page,f'asset/{aid}',panel) if aid else (page,False)
        if not found: fallback.append(panel)
    if fallback:
        page,inserted=_insert_route(page,'prompts',''.join(fallback))
        if not inserted: page,_=_insert_route(page,'assets',''.join(fallback))
    return page


def _data_script(payload: Mapping[str, Any]) -> str:
    raw=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    return '<script id="cbcc-canonical-data-v0672" type="application/json">'+raw+'</script>'


def _runtime_script() -> str:
    return r'''
<script id="cbcc-canonical-lazy-projection-v0672">
/* CBCC_CANONICAL_LAZY_PROJECTION_V0672 */
(function(){
 const src=document.getElementById('cbcc-canonical-data-v0672');let DATA={};try{DATA=src?JSON.parse(src.textContent||'{}'):{};}catch(_){DATA={};}
 const mk=(t,x,c)=>{const n=document.createElement(t);if(c)n.className=c;if(x!==undefined&&x!==null)n.textContent=String(x);return n};
 function keys(path){const out=[];String(path||'').replace(/([^.\[\]]+)|\[(\d+)\]/g,(_,k,i)=>{out.push(i===undefined?k:Number(i));return _});return out}
 function at(path){let v=DATA;for(const k of keys(path)){if(v==null)return undefined;v=v[k]}return v}
 function leaf(v,path){const r=mk('div',null,'cbcc-canonical-leaf');r.dataset.canonicalPath=path;const h=mk('div'),c=mk('code',path),b=mk('button','复制','cbcc-copy-v0672');b.type='button';h.append(c,b);r.append(h,mk('pre',v));return r}
 function node(v,path){if(v===null||v===undefined||typeof v!=='object')return leaf(v,path);const d=mk('details',null,'cbcc-canonical-node'),count=Array.isArray(v)?v.length:Object.keys(v).length,body=mk('div');d.append(mk('summary',`${path||'object'} · ${count}`),body);d.addEventListener('toggle',()=>{if(!d.open||body.dataset.rendered)return;body.dataset.rendered='1';if(Array.isArray(v))v.forEach((x,i)=>body.append(node(x,`${path}[${i}]`)));else Object.entries(v).forEach(([k,x])=>body.append(node(x,path?`${path}.${k}`:k)))});return d}
 function render(m){if(!m||m.dataset.rendered)return;m.dataset.rendered='1';const p=m.dataset.canonicalMount||'';m.replaceChildren(node(at(p),p))}
 document.addEventListener('toggle',e=>{const p=e.target.closest&&e.target.closest('.cbcc-canonical-mount-panel');if(p&&p.open)render(p.querySelector('[data-canonical-mount]'))},true);
 document.addEventListener('click',async e=>{const b=e.target.closest('.cbcc-copy-v0672');if(!b)return;const p=b.closest('[data-canonical-path]')?.querySelector('pre');await navigator.clipboard.writeText(p?p.textContent:'');const old=b.textContent;b.textContent='已复制';setTimeout(()=>b.textContent=old,800)});
 let INDEX=null;function index(){if(INDEX)return INDEX;const rows=[];function walk(v,p){if(v==null)return;if(Array.isArray(v)){v.forEach((x,i)=>walk(x,`${p}[${i}]`));return}if(typeof v==='object'){Object.entries(v).forEach(([k,x])=>walk(x,p?`${p}.${k}`:k));return}const text=String(v);if(text.trim())rows.push({path:p,text})}walk(DATA,'');INDEX=rows;window.CBCC_GLOBAL_SEARCH_INDEX_V0672=rows;return rows}
 const host=document.querySelector('[data-route="overview"]')||document.querySelector('main')||document.body;if(host&&!document.getElementById('cbcc-canonical-search-v0672')){const box=mk('div',null,'panel cbcc-canonical-v0672'),inp=mk('input'),out=mk('div');box.append(mk('h2','Canonical Workspace Search'));inp.id='cbcc-canonical-search-v0672';inp.type='search';inp.placeholder='搜索 Listing / 策略 / 风险 / Prompt / 真源字段…';out.id='cbcc-canonical-search-results-v0672';box.append(inp,out);host.append(box);inp.addEventListener('input',()=>{const q=inp.value.trim().toLowerCase();out.replaceChildren();if(!q)return;index().filter(x=>(x.path+' '+x.text).toLowerCase().includes(q)).slice(0,30).forEach(x=>{const p=mk('p');p.append(mk('b',x.path),mk('br'),document.createTextNode(x.text.slice(0,260)));out.append(p)})})}
})();
</script>
<style id="cbcc-canonical-lazy-style-v0672">
.cbcc-canonical-v0672{margin-top:18px}.cbcc-canonical-mount-panel>summary,.cbcc-canonical-node>summary{cursor:pointer;font-weight:700}.cbcc-canonical-node{border-top:1px solid var(--line,#ddd);padding:8px 0}.cbcc-canonical-leaf{padding:8px 0 10px 14px;border-left:2px solid var(--line,#ddd)}.cbcc-canonical-leaf>div{display:flex;gap:8px;justify-content:space-between;align-items:center}.cbcc-canonical-leaf code{font-size:10px;overflow-wrap:anywhere}.cbcc-canonical-leaf pre{white-space:pre-wrap;overflow-wrap:anywhere;margin:6px 0 0;font:inherit;font-size:11px}.cbcc-copy-v0672{border:1px solid var(--line,#ddd);background:var(--panel,#fff);border-radius:999px;padding:4px 8px;cursor:pointer}#cbcc-canonical-search-v0672{width:100%;padding:10px;border:1px solid var(--line,#ddd);border-radius:10px;background:var(--panel,#fff);color:inherit}
</style>
'''


def _embedded(html_text: str) -> dict[str, Any] | None:
    m=re.search(r'<script id="cbcc-canonical-data-v0672" type="application/json">(.*?)</script>',html_text,flags=re.S)
    if not m:return None
    try:
        value=json.loads(m.group(1)); return value if isinstance(value,dict) else None
    except Exception:return None


def audit_generic_human_field_coverage(payload: Mapping[str, Any], html_text: str) -> list[dict[str, Any]]:
    data=_embedded(html_text)
    if data is None:return [{'code':'HTML_CANONICAL_EMBEDDED_DATA_MISSING_V0672'}]
    expected=expected_visible_paths(payload); actual=expected_visible_paths(data); missing_data=sorted(expected-actual)
    mounts=set(re.findall(r'data-canonical-mount="([^"]+)"',html_text)); required={'canonical_business_objects','universe'}|{f'assets[{i}]' for i,_ in enumerate(payload.get('assets') or [])}; missing_mounts=sorted(required-mounts)
    issues=[]
    if missing_data:issues.append({'code':'HTML_CANONICAL_EMBEDDED_DATA_INCOMPLETE_V0672','missing_count':len(missing_data),'missing':missing_data[:100]})
    if missing_mounts:issues.append({'code':'HTML_CANONICAL_DYNAMIC_MOUNT_INCOMPLETE_V0672','missing_count':len(missing_mounts),'missing':missing_mounts[:100]})
    return issues


def finalize_static_human_projection(package_dir: Path | str) -> dict[str, Any]:
    package=Path(package_dir); html_path=package/'index.html'
    if not html_path.exists():return {'status':'NOT_FOUND','issues':[{'code':'INDEX_MISSING'}]}
    page=html_path.read_text(encoding='utf-8',errors='ignore')
    if 'data-workspace-shell="cbcc-commercial-v1"' not in page and "data-workspace-shell='cbcc-commercial-v1'" not in page:
        from .canonical_human_compaction_v0672 import finalize_static_human_projection as legacy
        return legacy(package)
    payload=build_canonical_human_payload(package); (package/DATA_FILE).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if LAZY_MARKER not in page:
        assets=[dict(x) for x in (payload.get('assets') or []) if isinstance(x,Mapping)]; ids=[str(a.get('id') or a.get('asset_id') or '') for a in assets if a.get('id') or a.get('asset_id')]
        page,compaction=_compact(page,ids); page=_mount_routes(page,assets); bundle=_data_script(payload)+_runtime_script(); page=page.replace('</body>',bundle+'</body>',1) if '</body>' in page else page+bundle; html_path.write_text(page,encoding='utf-8')
    else:compaction={'status':'ALREADY_APPLIED','routes_compacted':[],'bytes_before':html_path.stat().st_size,'bytes_after':html_path.stat().st_size,'bytes_removed':0}
    final=html_path.read_text(encoding='utf-8',errors='ignore'); issues=audit_generic_human_field_coverage(payload,final)
    return {'status':'PASS' if not issues else 'INCOMPLETE','issues':issues,'path':str(html_path),'data_file':DATA_FILE,'marker':LAZY_MARKER,'canonical_leaf_count':len(expected_visible_paths(payload)),'html_bytes':html_path.stat().st_size,'projection_mode':'SELF_CONTAINED_LAZY_SINGLE_MATERIALIZATION','legacy_route_compaction':compaction}
