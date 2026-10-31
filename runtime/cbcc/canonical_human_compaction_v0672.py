from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping
import hashlib
import html
import json
import re

from .canonical_full_parity_v0671 import build_canonical_human_payload as _build_v0671
from .canonical_human_workspace_completion import apply_complete_canonical_human_projection

MARKER = 'CBCC_CANONICAL_STATIC_PROJECTION_V0672'
LAZY_MARKER = 'CBCC_CANONICAL_LAZY_INSPECTOR_V0672'
DATA_FILE = 'CANONICAL_HUMAN_DATA.json'
PAYLOAD_ID = 'cbcc-canonical-payload-v0672'
_LAZY_ROOTS = ('assets', 'universe', 'canonical_business_objects')


def _p(v: Any) -> bool:
    return v not in (None, '', [], {})


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _leaf_paths(value: Any, path: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f'{path}.{key}' if path else str(key)
            rows.extend(_leaf_paths(child, child_path))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            rows.extend(_leaf_paths(child, f'{path}[{i}]'))
    elif _p(value):
        rows.append((path, str(value)))
    return rows


def build_canonical_human_payload(package_dir: Path | str) -> dict[str, Any]:
    """Build the complete final-package Human payload while deduplicating heavy object families."""
    payload = _build_v0671(package_dir)
    business = deepcopy(payload.get('canonical_business_objects') or {})
    business.pop('assets', None)
    business.pop('asset_universe', None)
    payload['canonical_business_objects'] = business
    payload.setdefault('projection_contract', {})['version'] = '0.6.72'
    payload['projection_contract']['deduplicated_heavy_object_families'] = ['assets', 'asset_universe']
    payload['projection_contract']['heavy_object_rendering'] = 'single embedded canonical payload + lazy DOM inspector'
    video = _read_json(Path(package_dir) / 'supporting_analysis' / 'video_creator_plan.json')
    if video:
        payload['video'] = video
    return payload


def _light_asset(asset: Mapping[str, Any]) -> dict[str, Any]:
    """Only the summary needed by the legacy routed renderer; heavy 00–15 data stays in the lazy payload."""
    out: dict[str, Any] = {}
    for key in ('id', 'asset_id', 'card'):
        if _p(asset.get(key)):
            out[key] = deepcopy(asset.get(key))
    return out


def _ui_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Light projection for the v0.6.70 business renderers; never duplicate full asset package objects."""
    keep = (
        'info', 'truth', 'listing', 'market', 'strategy', 'visual', 'content', 'race', 'culture',
        'compliance', 'ads', 'reviews', 'sources', 'projection_contract',
    )
    out = {k: deepcopy(payload.get(k)) for k in keep if _p(payload.get(k))}
    out['assets'] = [_light_asset(a) for a in (payload.get('assets') or []) if isinstance(a, Mapping)]
    u = payload.get('universe') if isinstance(payload.get('universe'), Mapping) else {}
    out['universe'] = {
        k: deepcopy(u.get(k))
        for k in ('total_asset_candidates', 'family_sweep', 'additional_candidates')
        if _p(u.get(k))
    }
    return out


def _leaf_html(value: Any, path: str) -> str:
    """Static renderer is reserved for light business panels only."""
    if isinstance(value, Mapping):
        body = ''.join(_leaf_html(v, f'{path}.{k}' if path else str(k)) for k, v in value.items())
        if not body:
            return ''
        return f'<details class="cbcc-canonical-node"><summary>{html.escape(path or "object")}</summary>{body}</details>'
    if isinstance(value, list):
        body = ''.join(_leaf_html(v, f'{path}[{i}]') for i, v in enumerate(value))
        if not body:
            return ''
        return f'<details class="cbcc-canonical-node"><summary>{html.escape(path)} · {len(value)}</summary>{body}</details>'
    if not _p(value):
        return ''
    ep = html.escape(path, quote=True)
    ev = html.escape(str(value))
    return f'<div class="cbcc-canonical-leaf" data-canonical-path="{ep}"><div><code>{ep}</code><button type="button" class="cbcc-copy-v0672">复制</button></div><pre>{ev}</pre></div>'


def _insert_route(page: str, route: str, fragment: str) -> tuple[str, bool]:
    starts = list(re.finditer(r'<section class="page(?: [^"]*)?" data-route="([^"]+)">', page))
    for i, match in enumerate(starts):
        if match.group(1) != route:
            continue
        block_end = starts[i + 1].start() if i + 1 < len(starts) else len(page)
        block = page[match.start():block_end]
        close = block.rfind('</section>')
        if close >= 0:
            pos = match.start() + close
            return page[:pos] + fragment + page[pos:], True
        return page[:block_end] + fragment + page[block_end:], True
    return page, False


def _panel(title: str, value: Any, path: str, note: str = '') -> str:
    return (
        '<div class="panel cbcc-canonical-v0672"><h2>' + html.escape(title) + '</h2>'
        + (f'<p>{html.escape(note)}</p>' if note else '')
        + _leaf_html(value, path) + '</div>'
    )


def _lazy_panel(root: str, title: str, note: str, assets: list[Mapping[str, Any]] | None = None) -> str:
    root_esc = html.escape(root, quote=True)
    chunks = [
        f'<div class="panel cbcc-canonical-v0672 cbcc-lazy-panel" data-canonical-lazy-root="{root_esc}">',
        f'<h2>{html.escape(title)}</h2><p>{html.escape(note)}</p>',
    ]
    if root == 'assets':
        chunks.append('<div class="cbcc-asset-lazy-picker" role="list">')
        for i, asset in enumerate(assets or []):
            aid = str(asset.get('id') or asset.get('asset_id') or f'asset-{i+1}')
            chunks.append(
                f'<button type="button" class="cbcc-lazy-asset-button" data-cbcc-asset-index="{i}">{html.escape(aid)}</button>'
            )
        chunks.append('</div>')
    else:
        chunks.append(f'<button type="button" class="cbcc-lazy-root-button" data-cbcc-lazy-root="{root_esc}">打开完整对象</button>')
    chunks.append(f'<div class="cbcc-lazy-viewer" data-cbcc-lazy-viewer="{root_esc}"><p class="muted">按需展开；完整字段保留在同页 Canonical payload 中。</p></div></div>')
    return ''.join(chunks)


def _page_route_blocks(page: str) -> list[tuple[int, int, str, str]]:
    starts = list(re.finditer(r'<section class="page(?: [^"]*)?" data-route="([^"]+)">', page))
    rows: list[tuple[int, int, str, str]] = []
    for i, match in enumerate(starts):
        block_end = starts[i + 1].start() if i + 1 < len(starts) else (page.find('</main>', match.start()) if '</main>' in page[match.start():] else len(page))
        if block_end < 0:
            block_end = len(page)
        block = page[match.start():block_end]
        close = block.rfind('</section>')
        end = match.start() + close + len('</section>') if close >= 0 else block_end
        rows.append((match.start(), end, match.group(1), match.group(0)))
    return rows


def _compact_legacy_heavy_routes(page: str, payload: Mapping[str, Any]) -> str:
    assets = [a for a in (payload.get('assets') or []) if isinstance(a, Mapping)]
    asset_index = {str(a.get('id') or a.get('asset_id') or ''): i for i, a in enumerate(assets)}
    replacements: list[tuple[int, int, str]] = []
    for start, end, route, opening in _page_route_blocks(page):
        if route == 'archive':
            inner = (
                '<div class="page-head"><div><div class="kicker">机器归档</div><h1>完整结构化归档</h1>'
                '<p>机器文件仍完整保留在交付 ZIP；人类工作台不再把每个 JSON 字节重复摊平成静态 DOM。</p></div></div>'
                + _lazy_panel('canonical_business_objects', 'Canonical Business Objects / 完整业务对象', '按需展开当前项目的完整业务权威对象。')
            )
            replacements.append((start, end, opening + inner + '</section>'))
        elif route == 'video' and _p(payload.get('video')):
            inner = (
                '<div class="page-head"><div><div class="kicker">VIDEO · CREATOR · LIVE</div><h1>视频 / Creator 工作台</h1>'
                '<p>视频计划保留 Hook、逐镜头、字幕/声音/CTA 与来源关系；按需展开，不再静态复制整套资产对象。</p></div></div>'
                + _lazy_panel('video', 'Video / Creator 完整对象', '完整 video_creator_plan 从同一 Canonical payload 按需展开。')
            )
            replacements.append((start, end, opening + inner + '</section>'))
        elif route.startswith('asset/'):
            aid = route.split('/', 1)[1]
            if aid in asset_index:
                i = asset_index[aid]
                inner = (
                    '<div class="page-head"><div><a class="back route-link" href="#assets" data-route="assets">← 返回资产中心</a>'
                    f'<div class="kicker">资产工作台 <span class="heading-en">{html.escape(aid)}</span></div><h1>{html.escape(aid)}</h1>'
                    '<p>完整 00–15 对象从单一 Canonical payload 按需加载。</p></div></div>'
                    f'<div class="panel cbcc-canonical-v0672 cbcc-asset-route-lazy" data-cbcc-asset-route-index="{i}">'
                    f'<div class="cbcc-lazy-viewer" data-cbcc-asset-route-viewer="{i}"><p class="muted">进入此路由时加载完整资产对象。</p></div></div>'
                )
                replacements.append((start, end, opening + inner + '</section>'))
    for start, end, replacement in reversed(replacements):
        page = page[:start] + replacement + page[end:]
    return page


def _safe_json_for_script(value: Any) -> str:
    # HTML parser terminates script elements on literal </script, regardless of type. Escape angle brackets
    # in JSON strings; JSON.parse restores them without allowing embedded markup to execute.
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), default=str).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def _payload_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, separators=(',', ':'), sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def _payload_json_script(payload: Mapping[str, Any]) -> str:
    raw = _safe_json_for_script(payload)
    digest = _payload_hash(payload)
    return f'<script type="application/json" id="{PAYLOAD_ID}" data-canonical-sha256="{digest}">{raw}</script>'


def _payload_script(payload: Mapping[str, Any]) -> str:
    return (
        _payload_json_script(payload)
        + f'<script id="cbcc-canonical-payload-bootstrap-v0672">window.CBCC_CANONICAL_HUMAN_V0672=JSON.parse(document.getElementById("{PAYLOAD_ID}").textContent||"{{}}");</script>'
    )


def _refresh_embedded_payload(page: str, payload: Mapping[str, Any]) -> tuple[str, bool]:
    pattern = rf'<script\s+type="application/json"\s+id="{re.escape(PAYLOAD_ID)}"[^>]*>.*?</script>'
    updated, count = re.subn(pattern, lambda _m: _payload_json_script(payload), page, count=1, flags=re.S)
    return updated, bool(count)


def _dom_script() -> str:
    return r'''
<script id="cbcc-canonical-static-projection-v0672">
/* CBCC_CANONICAL_STATIC_PROJECTION_V0672 */
/* CBCC_CANONICAL_LAZY_INSPECTOR_V0672 */
(function(){
  const payloadNode=document.getElementById('cbcc-canonical-payload-v0672');
  const D=window.CBCC_CANONICAL_HUMAN_V0672||(payloadNode?JSON.parse(payloadNode.textContent||'{}'):{});
  window.CBCC_CANONICAL_HUMAN_V0672=D;

  function text(v){return v==null?'':(typeof v==='string'?v:JSON.stringify(v,null,2))}
  function lazyLeaf(value,path){
    const row=document.createElement('div');row.className='cbcc-canonical-leaf';row.dataset.canonicalLazyPath=path;
    const head=document.createElement('div');const code=document.createElement('code');code.textContent=path;
    const copy=document.createElement('button');copy.type='button';copy.className='cbcc-copy-v0672';copy.textContent='复制';
    const pre=document.createElement('pre');pre.textContent=text(value);head.append(code,copy);row.append(head,pre);return row;
  }
  function lazyNode(value,path){
    if(value===null||typeof value!=='object')return lazyLeaf(value,path);
    const details=document.createElement('details');details.className='cbcc-canonical-node cbcc-lazy-node';details.dataset.canonicalLazyPath=path;
    const summary=document.createElement('summary');const size=Array.isArray(value)?value.length:Object.keys(value).length;
    summary.textContent=`${path||'object'} · ${size}`;details.appendChild(summary);
    details.addEventListener('toggle',()=>{
      if(!details.open||details.dataset.loaded==='1')return;details.dataset.loaded='1';
      const entries=Array.isArray(value)?value.map((v,i)=>[String(i),v]):Object.entries(value);
      const frag=document.createDocumentFragment();entries.forEach(([key,child])=>{
        const childPath=Array.isArray(value)?`${path}[${key}]`:(path?`${path}.${key}`:key);frag.appendChild(lazyNode(child,childPath));
      });details.appendChild(frag);
    });
    return details;
  }
  function mount(value,path,viewer){viewer.replaceChildren(lazyNode(value,path));}
  document.addEventListener('click',async e=>{
    const copy=e.target.closest('.cbcc-copy-v0672');
    if(copy){const node=copy.closest('[data-canonical-lazy-path],[data-canonical-path]');const pre=node?node.querySelector('pre'):null;await navigator.clipboard.writeText(pre?pre.textContent:'');const old=copy.textContent;copy.textContent='已复制';setTimeout(()=>copy.textContent=old,800);return;}
    const assetBtn=e.target.closest('.cbcc-lazy-asset-button');
    if(assetBtn){const i=Number(assetBtn.dataset.cbccAssetIndex);const viewer=document.querySelector('[data-cbcc-lazy-viewer="assets"]');if(viewer&&Array.isArray(D.assets)&&D.assets[i])mount(D.assets[i],`assets[${i}]`,viewer);return;}
    const rootBtn=e.target.closest('.cbcc-lazy-root-button');
    if(rootBtn){const root=rootBtn.dataset.cbccLazyRoot;const viewer=document.querySelector(`[data-cbcc-lazy-viewer="${root}"]`);if(viewer)mount(D[root],root,viewer);}
  });

  function mountAssetRouteFromHash(){
    const route=decodeURIComponent((location.hash||'').replace(/^#/,''));if(!route.startsWith('asset/'))return;
    document.querySelectorAll('[data-cbcc-asset-route-index]').forEach(host=>{
      const section=host.closest('[data-route]');if(!section||section.dataset.route!==route||host.dataset.loaded==='1')return;
      const i=Number(host.dataset.cbccAssetRouteIndex),viewer=host.querySelector('[data-cbcc-asset-route-viewer]');
      if(viewer&&Array.isArray(D.assets)&&D.assets[i]){host.dataset.loaded='1';mount(D.assets[i],`assets[${i}]`,viewer);}
    });
  }
  window.addEventListener('hashchange',mountAssetRouteFromHash);mountAssetRouteFromHash();

  // Full-project search indexes the single canonical payload in memory, not expanded DOM nodes.
  const index=[];
  function walk(v,path){
    if(v==null)return;
    if(Array.isArray(v)){v.forEach((x,i)=>walk(x,`${path}[${i}]`));return;}
    if(typeof v==='object'){Object.entries(v).forEach(([k,x])=>walk(x,path?`${path}.${k}`:k));return;}
    const t=String(v);if(t.trim())index.push({path,text:t});
  }
  walk(D,'CANONICAL');window.CBCC_GLOBAL_SEARCH_INDEX_V0672=index;
  const host=document.querySelector('[data-route="overview"]')||document.querySelector('main')||document.body;
  if(host&&!document.getElementById('cbcc-canonical-search-v0672')){
    const box=document.createElement('div');box.className='panel cbcc-canonical-v0672';
    const h=document.createElement('h2');h.textContent='Canonical Workspace Search';
    const input=document.createElement('input');input.id='cbcc-canonical-search-v0672';input.type='search';input.placeholder='搜索 Listing / 策略 / 风险 / Prompt / 真源字段…';
    const out=document.createElement('div');out.id='cbcc-canonical-search-results-v0672';box.append(h,input,out);host.appendChild(box);
    input.addEventListener('input',()=>{const q=input.value.trim().toLowerCase();const rows=q?index.filter(x=>(x.path+' '+x.text).toLowerCase().includes(q)).slice(0,30):[];out.replaceChildren();rows.forEach(x=>{const p=document.createElement('p');const key=document.createElement('b');key.textContent=x.path;const br=document.createElement('br');const value=document.createTextNode(x.text.slice(0,260));p.append(key,br,value);out.appendChild(p)})});
  }
})();
</script>
<style id="cbcc-canonical-static-style-v0672">
.cbcc-canonical-v0672{margin-top:18px}.cbcc-canonical-node{border-top:1px solid var(--line,#ddd);padding:8px 0}.cbcc-canonical-node>summary{cursor:pointer;font-weight:700}.cbcc-canonical-leaf{padding:8px 0 10px 14px;border-left:2px solid var(--line,#ddd)}.cbcc-canonical-leaf>div{display:flex;gap:8px;justify-content:space-between;align-items:center}.cbcc-canonical-leaf code{font-size:10px;overflow-wrap:anywhere}.cbcc-canonical-leaf pre{white-space:pre-wrap;overflow-wrap:anywhere;margin:6px 0 0;font:inherit;font-size:11px}.cbcc-copy-v0672,.cbcc-lazy-root-button,.cbcc-lazy-asset-button{border:1px solid var(--line,#ddd);background:var(--panel,#fff);border-radius:999px;padding:5px 9px;cursor:pointer}.cbcc-asset-lazy-picker{display:flex;flex-wrap:wrap;gap:7px;margin:10px 0}.cbcc-lazy-viewer{margin-top:12px;max-height:70vh;overflow:auto;border-top:1px solid var(--line,#ddd);padding-top:10px}#cbcc-canonical-search-v0672{width:100%;padding:10px;border:1px solid var(--line,#ddd);border-radius:10px;background:var(--panel,#fff);color:inherit}
</style>
'''


def _extract_embedded_payload(html_text: str) -> dict[str, Any] | None:
    pattern = rf'<script\s+type="application/json"\s+id="{re.escape(PAYLOAD_ID)}"[^>]*>(.*?)</script>'
    m = re.search(pattern, html_text, flags=re.S)
    if not m:
        return None
    try:
        value = json.loads(m.group(1))
        return value if isinstance(value, dict) else None
    except Exception:
        return None


def expected_visible_paths(payload: Mapping[str, Any]) -> set[str]:
    """All canonical paths remain human-reachable, but heavy roots are reached through the lazy inspector."""
    paths = {p for p, _ in _leaf_paths(payload.get('canonical_business_objects') or {}, 'canonical_business_objects')}
    paths.update(p for p, _ in _leaf_paths(payload.get('assets') or [], 'assets'))
    paths.update(p for p, _ in _leaf_paths(payload.get('universe') or {}, 'universe'))
    return paths


def audit_generic_human_field_coverage(payload: Mapping[str, Any], html_text: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    embedded = _extract_embedded_payload(html_text)
    if embedded is None:
        return [{'code': 'HTML_CANONICAL_LAZY_PAYLOAD_MISSING_V0672'}]
    if _payload_hash(embedded) != _payload_hash(payload):
        issues.append({'code': 'HTML_CANONICAL_LAZY_PAYLOAD_DRIFT_V0672'})
    if LAZY_MARKER not in html_text:
        issues.append({'code': 'HTML_CANONICAL_LAZY_INSPECTOR_MISSING_V0672'})
    required_roots = list(_LAZY_ROOTS) + (['video'] if _p(payload.get('video')) else [])
    missing_roots = [root for root in required_roots if f'data-canonical-lazy-root="{root}"' not in html_text]
    if missing_roots:
        issues.append({'code': 'HTML_CANONICAL_LAZY_ROOT_MISSING_V0672', 'missing': missing_roots})
    # Light business routes are still rendered by the mature routed workspace. Full heavy coverage is proven
    # by exact embedded-payload parity + a safe lazy inspector, rather than millions of duplicated DOM leaves.
    return issues


def finalize_static_human_projection(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    html_path = package / 'index.html'
    if not html_path.exists():
        return {'status': 'NOT_FOUND', 'issues': [{'code': 'INDEX_MISSING'}]}
    payload = build_canonical_human_payload(package)
    data_text = json.dumps(payload, ensure_ascii=False, indent=2, default=str) + '\n'
    (package / DATA_FILE).write_text(data_text, encoding='utf-8')

    page = html_path.read_text(encoding='utf-8', errors='ignore')
    if MARKER not in page:
        # Compact legacy routes that statically duplicated machine archive, video and every full asset object.
        # Their route identity stays intact; the complete object is rendered lazily from the single payload.
        page = _compact_legacy_heavy_routes(page, payload)
        # The full canonical payload is embedded exactly once. The mature v0.6.70 renderers reference
        # that same in-page object instead of serializing a second Human payload.
        bootstrap = _payload_script(payload)
        page = page.replace('</body>', bootstrap + '</body>', 1) if '</body>' in page else page + bootstrap
        html_path.write_text(page, encoding='utf-8')
        prior = apply_complete_canonical_human_projection(
            html_path,
            {'projection_reference': 'CBCC_CANONICAL_HUMAN_V0672'},
            payload_expression='window.CBCC_CANONICAL_HUMAN_V0672',
        )
        page = html_path.read_text(encoding='utf-8', errors='ignore')
        # Mature v0.6.70 business renderers now reference the single v0.6.72 payload directly;
        # do not duplicate Listing/Strategy/Visual/Content trees as static leaf DOM.

        asset_panel = _lazy_panel(
            'assets',
            '逐资产 00–15 完整生产对象',
            '完整 Visual / Photography / Layout / Prompt / Source Trace / Strategy Trace / Visible Copy / Production / Lineage 只嵌入一次，并按资产按需展开。',
            [dict(x) for x in (payload.get('assets') or []) if isinstance(x, Mapping)],
        )
        page, inserted = _insert_route(page, 'prompts', asset_panel)
        if not inserted:
            page, inserted = _insert_route(page, 'assets', asset_panel)
        if not inserted:
            page = page.replace('</body>', asset_panel + '</body>', 1) if '</body>' in page else page + asset_panel

        archive = _lazy_panel(
            'canonical_business_objects',
            'Canonical Business Objects / 完整字段档案',
            '完整业务对象按需展开；HTML 不为每个叶子预生成 DOM。',
        )
        universe = _lazy_panel(
            'universe',
            'Asset Universe / 完整候选与家族扫描',
            '完整 Asset Universe 保留在同一 Canonical payload，按需展开。',
        )
        page, inserted = _insert_route(page, 'sources', archive + universe)
        if not inserted:
            page = page.replace('</body>', archive + universe + '</body>', 1) if '</body>' in page else page + archive + universe

        scripts = _dom_script()
        page = page.replace('</body>', scripts + '</body>', 1) if '</body>' in page else page + scripts
        html_path.write_text(page, encoding='utf-8')
        prior_result = prior
    else:
        prior_result = {'status':'PASS','already_applied':True}
        embedded = _extract_embedded_payload(page)
        if embedded is None or _payload_hash(embedded) != _payload_hash(payload):
            refreshed, replaced = _refresh_embedded_payload(page, payload)
            if replaced:
                html_path.write_text(refreshed, encoding='utf-8')
            else:
                # A partial/stale marker without the canonical payload is not trusted; rebuild from the
                # current HTML shell on the next audit rather than silently claiming parity.
                prior_result = {'status':'INCOMPLETE','issues':['CANONICAL_LAZY_PAYLOAD_REFRESH_TARGET_MISSING']}

    final_text = html_path.read_text(encoding='utf-8', errors='ignore')
    issues = audit_generic_human_field_coverage(payload, final_text)
    return {
        'status': 'PASS' if not issues else 'INCOMPLETE',
        'issues': issues,
        'path': str(html_path),
        'data_file': DATA_FILE,
        'v0670_projection': prior_result,
        'marker': MARKER,
        'canonical_leaf_count': len(expected_visible_paths(payload)),
        'html_bytes': html_path.stat().st_size,
        'canonical_data_bytes': (package / DATA_FILE).stat().st_size,
        'projection_mode': 'LAZY_SINGLE_EMBEDDED_CANONICAL_PAYLOAD',
    }
