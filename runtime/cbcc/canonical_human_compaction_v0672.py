from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping
import html
import json
import re

from .canonical_full_parity_v0671 import build_canonical_human_payload as _build_v0671
from .canonical_human_workspace_completion import apply_complete_canonical_human_projection

MARKER = 'CBCC_CANONICAL_STATIC_PROJECTION_V0672'
DATA_FILE = 'CANONICAL_HUMAN_DATA.json'


def _p(v: Any) -> bool:
    return v not in (None, '', [], {})


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
    """Build v0.6.71 payload without storing the same heavy Asset/Universe objects twice."""
    payload = _build_v0671(package_dir)
    business = deepcopy(payload.get('canonical_business_objects') or {})
    business.pop('assets', None)
    business.pop('asset_universe', None)
    payload['canonical_business_objects'] = business
    payload.setdefault('projection_contract', {})['version'] = '0.6.72'
    payload['projection_contract']['deduplicated_heavy_object_families'] = ['assets', 'asset_universe']
    return payload


def _slim_asset(asset: Mapping[str, Any]) -> dict[str, Any]:
    keys = ('id', 'asset_id', 'card', 'prompt_cn', 'prompt_en', 'visible_copy', 'production_notes', 'review')
    return {k: deepcopy(asset.get(k)) for k in keys if _p(asset.get(k))}


def _ui_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    out = {k: deepcopy(v) for k, v in payload.items() if k != 'canonical_business_objects'}
    out['assets'] = [_slim_asset(a) for a in (payload.get('assets') or []) if isinstance(a, Mapping)]
    u = payload.get('universe') if isinstance(payload.get('universe'), Mapping) else {}
    out['universe'] = {k: deepcopy(u.get(k)) for k in ('total_asset_candidates', 'family_sweep', 'additional_candidates') if _p(u.get(k))}
    return out


def _leaf_html(value: Any, path: str) -> str:
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
    return '<div class="panel cbcc-canonical-v0672"><h2>' + html.escape(title) + '</h2>' + (f'<p>{html.escape(note)}</p>' if note else '') + _leaf_html(value, path) + '</div>'


def _asset_panel(assets: list[dict[str, Any]]) -> str:
    chunks = ['<div class="panel cbcc-canonical-v0672"><h2>逐资产 00–15 完整生产对象</h2><p>每个成熟资产对象只物化一次；Prompt、Design Card、Visual/Photography/Layout、Source/Strategy Trace、Visible Copy、Production 与 lineage 均可展开。</p>']
    for i, asset in enumerate(assets):
        aid = asset.get('id') or asset.get('asset_id') or f'asset-{i+1}'
        chunks.append(f'<details class="cbcc-asset-production-object"><summary>{html.escape(str(aid))}</summary>{_leaf_html(asset, f"assets[{i}]")}</details>')
    chunks.append('</div>')
    return ''.join(chunks)


def _dom_script() -> str:
    return r'''
<script id="cbcc-canonical-static-projection-v0672">
/* CBCC_CANONICAL_STATIC_PROJECTION_V0672 */
(function(){
  const leaves=()=>Array.from(document.querySelectorAll('[data-canonical-path]'));
  function valueOf(node){const pre=node.querySelector('pre');return pre?pre.textContent:''}
  window.CBCC_GLOBAL_SEARCH_INDEX_V0672=leaves().map(node=>({path:node.dataset.canonicalPath||'',text:valueOf(node),node}));
  document.addEventListener('click',async e=>{const b=e.target.closest('.cbcc-copy-v0672');if(!b)return;const node=b.closest('[data-canonical-path]');await navigator.clipboard.writeText(node?valueOf(node):'');const old=b.textContent;b.textContent='已复制';setTimeout(()=>b.textContent=old,800)});
  const host=document.querySelector('[data-route="overview"]')||document.querySelector('main')||document.body;
  if(host&&!document.getElementById('cbcc-canonical-search-v0672')){const box=document.createElement('div');box.className='panel cbcc-canonical-v0672';const h=document.createElement('h2');h.textContent='Canonical Workspace Search';const input=document.createElement('input');input.id='cbcc-canonical-search-v0672';input.type='search';input.placeholder='搜索 Listing / 策略 / 风险 / Prompt / 真源字段…';const out=document.createElement('div');out.id='cbcc-canonical-search-results-v0672';box.append(h,input,out);host.appendChild(box);input.addEventListener('input',()=>{const q=input.value.trim().toLowerCase();const rows=q?window.CBCC_GLOBAL_SEARCH_INDEX_V0672.filter(x=>(x.path+' '+x.text).toLowerCase().includes(q)).slice(0,30):[];out.replaceChildren();rows.forEach(x=>{const p=document.createElement('p');const key=document.createElement('b');key.textContent=x.path;const br=document.createElement('br');const value=document.createTextNode(x.text.slice(0,260));p.append(key,br,value);out.appendChild(p)})})}
})();
</script>
<style id="cbcc-canonical-static-style-v0672">
.cbcc-canonical-v0672{margin-top:18px}.cbcc-canonical-node{border-top:1px solid var(--line,#ddd);padding:8px 0}.cbcc-canonical-node>summary{cursor:pointer;font-weight:700}.cbcc-canonical-leaf{padding:8px 0 10px 14px;border-left:2px solid var(--line,#ddd)}.cbcc-canonical-leaf>div{display:flex;gap:8px;justify-content:space-between;align-items:center}.cbcc-canonical-leaf code{font-size:10px;overflow-wrap:anywhere}.cbcc-canonical-leaf pre{white-space:pre-wrap;overflow-wrap:anywhere;margin:6px 0 0;font:inherit;font-size:11px}.cbcc-copy-v0672{border:1px solid var(--line,#ddd);background:var(--panel,#fff);border-radius:999px;padding:4px 8px;cursor:pointer}#cbcc-canonical-search-v0672{width:100%;padding:10px;border:1px solid var(--line,#ddd);border-radius:10px;background:var(--panel,#fff);color:inherit}
</style>
'''


def expected_visible_paths(payload: Mapping[str, Any]) -> set[str]:
    paths = {p for p, _ in _leaf_paths(payload.get('canonical_business_objects') or {}, 'canonical_business_objects')}
    paths.update(p for p, _ in _leaf_paths(payload.get('assets') or [], 'assets'))
    paths.update(p for p, _ in _leaf_paths(payload.get('universe') or {}, 'universe'))
    return paths


def audit_generic_human_field_coverage(payload: Mapping[str, Any], html_text: str) -> list[dict[str, Any]]:
    visible = set(re.findall(r'data-canonical-path="([^"]+)"', html_text))
    expected = expected_visible_paths(payload)
    missing = [p for p in sorted(expected) if html.escape(p, quote=True) not in visible]
    if not missing:
        return []
    return [{'code': 'HTML_CANONICAL_GENERIC_FIELD_COVERAGE_INCOMPLETE_V0672', 'missing_count': len(missing), 'missing': missing[:100]}]


def finalize_static_human_projection(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    html_path = package / 'index.html'
    if not html_path.exists():
        return {'status': 'NOT_FOUND', 'issues': [{'code': 'INDEX_MISSING'}]}
    payload = build_canonical_human_payload(package)
    (package / DATA_FILE).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    page = html_path.read_text(encoding='utf-8', errors='ignore')
    if MARKER not in page:
        prior = apply_complete_canonical_human_projection(html_path, _ui_payload(payload))
        page = html_path.read_text(encoding='utf-8', errors='ignore')
        for route, title, value, path in (
            ('listing', 'Canonical Listing / 上架完整字段', payload.get('listing') or {}, 'listing'),
            ('strategy', 'Canonical Strategy / 商业决策完整字段', payload.get('strategy') or {}, 'strategy'),
            ('product', 'Product Truth / 产品真源完整字段', (payload.get('canonical_business_objects') or {}).get('product_truth') or payload.get('truth') or {}, 'product_truth'),
            ('visual', 'Visual / Photography / Inclusive 执行', payload.get('visual') or {}, 'visual'),
            ('content', 'Content / RACE / Culture / Ads', {'content':payload.get('content'),'race':payload.get('race'),'culture':payload.get('culture'),'ads':payload.get('ads')}, 'campaign'),
        ):
            page, _ = _insert_route(page, route, _panel(title, value, path))
        asset_panel = _asset_panel([dict(x) for x in (payload.get('assets') or []) if isinstance(x, Mapping)])
        page, inserted = _insert_route(page, 'prompts', asset_panel)
        if not inserted:
            page, _ = _insert_route(page, 'assets', asset_panel)
        archive = _panel('Canonical Business Objects / 完整字段档案', payload.get('canonical_business_objects') or {}, 'canonical_business_objects', '重型资产与 Asset Universe 在各自工作面只物化一次，避免重复复制。')
        universe = _panel('Asset Universe / 完整候选与家族扫描', payload.get('universe') or {}, 'universe')
        page, inserted = _insert_route(page, 'sources', archive + universe)
        if not inserted:
            page = page.replace('</body>', archive + universe + '</body>', 1) if '</body>' in page else page + archive + universe
        script = _dom_script()
        page = page.replace('</body>', script + '</body>', 1) if '</body>' in page else page + script
        html_path.write_text(page, encoding='utf-8')
        prior_result = prior
    else:
        prior_result = {'status':'PASS','already_applied':True}

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
        'projection_mode': 'DEDUPLICATED_SINGLE_MATERIALIZATION',
    }
