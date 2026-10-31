from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import html
import json
import re

try:
    import yaml
except Exception:  # pragma: no cover - runtime already depends on PyYAML, fallback keeps audit readable.
    yaml = None

from .canonical_human_workspace_completion import apply_complete_canonical_human_projection


MARKER = 'CBCC_CANONICAL_STATIC_PROJECTION_V0671'
DATA_FILE = 'CANONICAL_HUMAN_DATA.json'


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='ignore').strip()
    except Exception:
        return ''


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    try:
        value = yaml.safe_load(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _p(v: Any) -> bool:
    return v not in (None, '', [], {})


def _d(v: Any) -> dict[str, Any]:
    return dict(v) if isinstance(v, Mapping) else {}


def _l(v: Any) -> list[Any]:
    if v in (None, '', {}):
        return []
    return list(v) if isinstance(v, (list, tuple)) else [v]


def _field_rows(center: Mapping[str, Any], field: str) -> list[dict[str, Any]]:
    rows = []
    for source in ('copy_center', 'localized_copy'):
        for row in _l(center.get(source)):
            if isinstance(row, Mapping) and str(row.get('field') or '') == field:
                rows.append(dict(row))
    return rows


def _locale_value(center: Mapping[str, Any], field: str, prefixes: tuple[str, ...]) -> Any:
    for row in _field_rows(center, field):
        locale = str(row.get('locale') or '').lower()
        if any(locale.startswith(prefix.lower()) for prefix in prefixes) and _p(row.get('value')):
            return row.get('value')
    return None


def _primary_value(center: Mapping[str, Any], field: str) -> Any:
    for row in _l(center.get('copy_center')):
        if isinstance(row, Mapping) and str(row.get('field') or '') == field and _p(row.get('value')):
            return row.get('value')
    return None


def _cn_companion(center: Mapping[str, Any], field: str) -> Any:
    for row in _field_rows(center, field):
        if _p(row.get('delivery_translation')):
            return row.get('delivery_translation')
    return None


def _as_list(v: Any) -> list[Any]:
    if v in (None, '', {}):
        return []
    return v if isinstance(v, list) else [v]


def _key_points(center: Mapping[str, Any]) -> list[dict[str, Any]]:
    bm = _as_list(_locale_value(center, 'bullets', ('ms', 'bm')) or _locale_value(center, 'highlights', ('ms', 'bm')) or _primary_value(center, 'bullets') or _primary_value(center, 'highlights'))
    en = _as_list(_locale_value(center, 'bullets', ('en',)) or _locale_value(center, 'highlights', ('en',)))
    cn = _as_list(_cn_companion(center, 'bullets') or _cn_companion(center, 'highlights'))
    count = max(len(bm), len(en), len(cn), 0)
    return [{'bm': bm[i] if i < len(bm) else '', 'en': en[i] if i < len(en) else '', 'cn': cn[i] if i < len(cn) else ''} for i in range(count)]


def _faq(center: Mapping[str, Any]) -> list[dict[str, Any]]:
    bm = _as_list(_locale_value(center, 'faq', ('ms', 'bm')) or _primary_value(center, 'faq'))
    en = _as_list(_locale_value(center, 'faq', ('en',)))
    cn = _as_list(_cn_companion(center, 'faq'))
    count = max(len(bm), len(en), len(cn), 0)
    rows = []
    for i in range(count):
        b = bm[i] if i < len(bm) else {}
        e = en[i] if i < len(en) else {}
        c = cn[i] if i < len(cn) else ''
        bd = _d(b); ed = _d(e); cd = _d(c)
        rows.append({
            'q_bm': bd.get('q') or bd.get('question') or (b if not isinstance(b, Mapping) else ''),
            'a_bm': bd.get('a') or bd.get('answer') or '',
            'q_en': ed.get('q') or ed.get('question') or (e if not isinstance(e, Mapping) else ''),
            'a_en': ed.get('a') or ed.get('answer') or '',
            'cn': cd.get('q') or cd.get('question') or c,
        })
    return rows


def _normalized_listing(center: Mapping[str, Any]) -> dict[str, Any]:
    bm_title = _locale_value(center, 'title', ('ms', 'bm')) or _primary_value(center, 'title') or _primary_value(center, 'product_name')
    en_title = _locale_value(center, 'title', ('en',))
    cn_title = _cn_companion(center, 'title') or _cn_companion(center, 'product_name')
    bm_desc = _locale_value(center, 'description', ('ms', 'bm')) or _primary_value(center, 'description')
    en_desc = _locale_value(center, 'description', ('en',))
    cn_desc = _cn_companion(center, 'description')
    attrs = _primary_value(center, 'attributes')
    package_bm = _locale_value(center, 'package', ('ms', 'bm')) or _primary_value(center, 'package')
    package_en = _locale_value(center, 'package', ('en',))
    package_cn = _cn_companion(center, 'package')
    return {
        'title': {'bm': bm_title or '', 'en': en_title or '', 'cn': cn_title or ''},
        'description_bm': bm_desc or '',
        'description_en': en_desc or '',
        'description_cn': cn_desc or '',
        'key_points': _key_points(center),
        'attributes': attrs if isinstance(attrs, Mapping) else ({'raw': attrs} if _p(attrs) else {}),
        'package_contents': {'bm': package_bm or '', 'en': package_en or '', 'cn': package_cn or ''},
        'faq': _faq(center),
        'raw_copy_center': deepcopy_json(center.get('copy_center') or []),
        'localized_copy': deepcopy_json(center.get('localized_copy') or []),
    }


def deepcopy_json(v: Any) -> Any:
    try:
        return json.loads(json.dumps(v, ensure_ascii=False, default=str))
    except Exception:
        return v


def _asset_payload(asset_dir: Path) -> dict[str, Any]:
    manifest = _read_yaml(asset_dir / '00_asset_manifest.yaml')
    return {
        'id': asset_dir.name,
        'asset_id': asset_dir.name,
        'manifest': manifest,
        'human_design_card': _read_text(asset_dir / '00_HUMAN_DESIGN_CARD_CN.md'),
        'strategy': _read_text(asset_dir / '01_strategy.md'),
        'visual_spec': _read_text(asset_dir / '02_visual_spec.md'),
        'photography_contract': _read_json(asset_dir / '03_photography_contract.json'),
        'layout_contract': _read_json(asset_dir / '04_layout_contract.json'),
        'prompt_cn': _read_text(asset_dir / '05_prompt_CN.txt'),
        'prompt_en': _read_text(asset_dir / '06_prompt_EN.txt'),
        'generation_guidance': _read_text(asset_dir / '07_generation_guidance.txt'),
        'copy_markdown': _read_text(asset_dir / '08_copy.md'),
        'production_notes': _read_text(asset_dir / '09_production_notes.md'),
        'source_trace': _read_text(asset_dir / '10_source_trace.md'),
        'strategy_trace': _read_json(asset_dir / '11_strategy_authority_trace.json'),
        'card': _read_json(asset_dir / '12_design_card.json'),
        'prompt_contract': _read_json(asset_dir / '13_prompt_contract.json'),
        'visible_copy': _read_json(asset_dir / '14_visible_copy_block.json'),
        'production_object': _read_json(asset_dir / '15_production_assembly_notes.json'),
        'canonical_lineage': _read_json(asset_dir / 'CANONICAL_LINEAGE.json'),
    }


def build_canonical_human_payload(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    human = _read_json(package / 'HUMAN_DELIVERY.json')
    strategy = _read_json(package / 'strategy/strategy_authority.json')
    if not strategy:
        strategy = _read_json(package / 'supporting_analysis/strategy_authority.json')
    sections = _d(strategy.get('sections'))
    info = _d(sections.get('01_information_completeness_assumptions_decisions'))
    truth_section = _d(sections.get('02_product_truth_value_ladder'))
    market_section = _d(sections.get('03_platform_region_audience_culture_insight'))
    core = _d(sections.get('04_marketing_core_strategy'))
    visual_section = _d(sections.get('05_visual_photography_strategy'))
    content_rows = [dict(x) for x in _l(sections.get('06_platform_content_matrix')) if isinstance(x, Mapping)]
    race_rows = []
    for raw in _l(sections.get('07_race_execution_table')):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        row.setdefault('actions', row.get('key_actions'))
        row.setdefault('outputs', row.get('output'))
        row.setdefault('culture', row.get('culture_check'))
        row.setdefault('metric', row.get('kpi'))
        race_rows.append(row)
    culture_rows = []
    for raw in _l(sections.get('08_culture_adaptation_checklist')):
        if not isinstance(raw, Mapping):
            continue
        row = dict(raw)
        row.setdefault('dimension', row.get('adaptation_point'))
        row.setdefault('basis', row.get('evidence_or_assumption'))
        row.setdefault('inclusive', row.get('inclusive_representation'))
        row.setdefault('risk', row.get('stereotype_taboo_risk'))
        row.setdefault('verification_result', row.get('validation_result') or row.get('result'))
        row.setdefault('modification_action', row.get('modification'))
        culture_rows.append(row)
    last = _d(sections.get('09_risk_measurement_priority_next_steps'))

    support = package / 'supporting_analysis'
    product_truth = _read_json(support / 'product_truth.json')
    target_context = _read_json(support / 'target_context.json')
    culture_context = _read_json(support / 'culture_context.json')
    market_analysis = _read_json(support / 'market_analysis.json')
    compliance = _read_json(support / 'compliance_report.json')
    ads_raw = _read_json(support / 'ad_analysis.json')
    reviews_raw = _read_json(support / 'feedback_analysis.json')
    sources_raw = _read_json(support / 'source_registry.json') or _read_json(support / 'sources.json')
    universe = _read_json(package / 'ASSET_UNIVERSE.json')

    asset_root = package / 'asset_packages'
    assets = [_asset_payload(d) for d in sorted(asset_root.iterdir()) if d.is_dir()] if asset_root.exists() else []

    product_business = product_truth or _d(human.get('product'))
    listing = _normalized_listing(human)
    self_check = last.get('output_self_check_rows') or last.get('output_self_check') or []
    if isinstance(self_check, Mapping):
        self_check = [{'item': k, 'status': v} for k, v in self_check.items()]
    compliance_view = {
        'claim_rows': last.get('p0_compliance_claim_checklist') or compliance.get('claim_rows') or compliance.get('claims') or [],
        'other_risks': compliance.get('other_risks') or compliance.get('risks') or compliance.get('issues') or [],
        'self_check': self_check,
    }
    ads_view = {
        'objective': ads_raw.get('objective') or ads_raw.get('campaign_objective'),
        'tests': ads_raw.get('tests') or ads_raw.get('ab_tests') or [],
        'economics_boundary': ads_raw.get('economics_boundary'),
        'landing': ads_raw.get('landing') or ads_raw.get('landing_page'),
        'attribution': ads_raw.get('attribution') or ads_raw.get('utm_attribution'),
        'failure_diagnosis': ads_raw.get('failure_diagnosis') or [],
        'raw': ads_raw,
    }
    reviews_view = {
        'status': reviews_raw.get('status'),
        'taxonomy': reviews_raw.get('taxonomy') or reviews_raw.get('issue_taxonomy') or [],
        'learning_loop': reviews_raw.get('learning_loop'),
        'raw': reviews_raw,
    }
    sources_view = {'sources': sources_raw.get('sources') or sources_raw.get('rows') or [], 'raw': sources_raw}

    business_objects = {
        'human_delivery': human,
        'product_truth': product_truth,
        'target_context': target_context,
        'culture_context': culture_context,
        'market_analysis': market_analysis,
        'strategy_authority': strategy,
        'compliance': compliance,
        'ads': ads_raw,
        'reviews': reviews_raw,
        'sources': sources_raw,
        'asset_universe': universe,
        'assets': assets,
    }
    business_objects = {k: v for k, v in business_objects.items() if _p(v)}

    return {
        'info': {
            'information_audit': product_business,
            'pending_confirmations': info.get('pending_confirmations') or info.get('pending_questions') or [],
            'assumptions_and_decisions': info.get('assumption_decision_log') or info.get('decision_log') or info.get('assumptions') or [],
        },
        'truth': {**truth_section, 'raw_product_truth': product_truth},
        'listing': listing,
        'market': {
            'platform_rules': market_section.get('platform_rules') or market_analysis.get('platform_rules') or [],
            'why': market_section.get('context_why') or market_section.get('platform_region_audience_culture_why') or {},
            'market_reference': market_section.get('market_reference') or market_analysis.get('market_reference') or [],
            'raw': market_section,
        },
        'strategy': {'strategy': core, 'economics': _d(last.get('economics'))},
        'visual': {
            'thesis': visual_section.get('visual_thesis') or visual_section.get('thesis'),
            'moodboard': visual_section.get('moodboard_direction'),
            'composition': visual_section.get('composition') or visual_section.get('composition_rules'),
            'palette': visual_section.get('palette_hex') or visual_section.get('palette'),
            'contrast': visual_section.get('contrast') or visual_section.get('contrast_ratio'),
            'typography': visual_section.get('typography'),
            'camera': visual_section.get('camera') or visual_section.get('photography_execution'),
            'lighting': visual_section.get('lighting_framework') or visual_section.get('lighting'),
            'cmf': visual_section.get('cmf'),
            'platform': visual_section.get('platform_dimensions'),
            'inclusive': visual_section.get('inclusive_dimension_decisions') or visual_section.get('inclusive_photography'),
            'shot_list': visual_section.get('shot_list') or visual_section.get('asset_parameter_reasoning'),
            'raw': visual_section,
        },
        'content': {'rows': content_rows},
        'race': {'rows': race_rows},
        'culture': {'rows': culture_rows, 'raw': culture_context},
        'compliance': compliance_view,
        'ads': ads_view,
        'reviews': reviews_view,
        'sources': sources_view,
        'universe': universe,
        'assets': assets,
        'canonical_business_objects': business_objects,
        'projection_contract': {
            'version': '0.6.71',
            'source': 'real_final_package_machine_authorities',
            'complete_field_archive_required': True,
            'static_delivery_html_supported': True,
        },
    }


def _primitive(v: Any) -> str:
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if v is None:
        return 'null'
    return str(v)


def _leaf_paths(value: Any, path: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f'{path}.{key}' if path else str(key)
            rows.extend(_leaf_paths(child, child_path))
        return rows
    if isinstance(value, list):
        for i, child in enumerate(value):
            rows.extend(_leaf_paths(child, f'{path}[{i}]'))
        return rows
    if _p(value):
        rows.append((path, _primitive(value)))
    return rows


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
    text = _primitive(value)
    ep = html.escape(path, quote=True)
    ev = html.escape(text)
    ea = html.escape(text, quote=True)
    return f'<div class="cbcc-canonical-leaf" data-canonical-path="{ep}"><div><code>{ep}</code><button type="button" class="cbcc-copy-v0671" data-copy-value="{ea}">复制</button></div><pre>{ev}</pre></div>'


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


def _summary_panel(title: str, value: Any, path: str) -> str:
    return (
        '<div class="panel cbcc-canonical-v0671"><h2>' + html.escape(title) + '</h2>'
        '<p>该区域由最终包中的 Canonical Business Object 正向投影；字段可折叠，但不会静默删除。</p>'
        + _leaf_html(value, path) + '</div>'
    )


def _asset_panel(assets: list[dict[str, Any]]) -> str:
    chunks = ['<div class="panel cbcc-canonical-v0671"><h2>逐资产完整生产对象</h2><p>Visual / Photography / Layout / Prompt / Source Trace / Strategy Trace / Visible Copy / Production 均独立可见。</p>']
    for i, asset in enumerate(assets):
        aid = asset.get('id') or asset.get('asset_id') or f'asset-{i+1}'
        chunks.append(f'<details class="cbcc-asset-production-object"><summary>{html.escape(str(aid))}</summary>')
        for key, label in (
            ('visual_spec', 'Visual Spec'), ('photography_contract', 'Photography Contract'), ('layout_contract', 'Layout Contract'),
            ('prompt_cn', 'Prompt CN'), ('prompt_en', 'Prompt EN'), ('source_trace', 'Source Trace'), ('strategy_trace', 'Strategy Trace'),
            ('visible_copy', 'Visible Copy'), ('production_object', 'Production Object'), ('prompt_contract', 'Prompt Contract'), ('canonical_lineage', 'Canonical Lineage'),
        ):
            if _p(asset.get(key)):
                chunks.append(f'<h3>{html.escape(label)}</h3>{_leaf_html(asset.get(key), f"assets[{i}].{key}")}')
        chunks.append('</details>')
    chunks.append('</div>')
    return ''.join(chunks)


def _script(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return f'''
<script id="cbcc-canonical-static-projection-v0671">
/* {MARKER} */
const CBCC_CANONICAL_HUMAN_V0671={raw};
(function(){{
  const D=CBCC_CANONICAL_HUMAN_V0671;
  const index=[];
  function walk(v,path){{if(v==null)return;if(Array.isArray(v)){{v.forEach((x,i)=>walk(x,`${{path}}[${{i}}]`));return}}if(typeof v==='object'){{Object.entries(v).forEach(([k,x])=>walk(x,path?`${{path}}.${{k}}`:k));return}}const text=String(v);if(text.trim())index.push({{path,text}})}}
  walk(D,'CANONICAL'); window.CBCC_GLOBAL_SEARCH_INDEX_V0671=index;
  document.addEventListener('click',async e=>{{const b=e.target.closest('.cbcc-copy-v0671');if(!b)return;await navigator.clipboard.writeText(b.dataset.copyValue||'');const old=b.textContent;b.textContent='已复制';setTimeout(()=>b.textContent=old,800)}});
  const host=document.querySelector('[data-route="overview"]')||document.querySelector('main')||document.body;
  if(host&&!document.getElementById('cbcc-canonical-search-v0671')){{const box=document.createElement('div');box.className='panel cbcc-canonical-v0671';box.innerHTML='<h2>Canonical Workspace Search</h2><input id="cbcc-canonical-search-v0671" type="search" placeholder="搜索 Listing / 策略 / 风险 / Prompt / 真源字段…"><div id="cbcc-canonical-search-results-v0671"></div>';host.appendChild(box);const input=box.querySelector('input'),out=box.querySelector('div');input.addEventListener('input',()=>{{const q=input.value.trim().toLowerCase();const rows=q?index.filter(x=>(x.path+' '+x.text).toLowerCase().includes(q)).slice(0,30):[];out.innerHTML=rows.map(x=>`<p><b>${{x.path}}</b><br>${{String(x.text).slice(0,260)}}</p>`).join('')}})}}
}})();
</script>
<style id="cbcc-canonical-static-style-v0671">
.cbcc-canonical-v0671{{margin-top:18px}}.cbcc-canonical-node{{border-top:1px solid var(--line,#ddd);padding:8px 0}}.cbcc-canonical-node>summary{{cursor:pointer;font-weight:700}}.cbcc-canonical-leaf{{padding:8px 0 10px 14px;border-left:2px solid var(--line,#ddd)}}.cbcc-canonical-leaf>div{{display:flex;gap:8px;justify-content:space-between;align-items:center}}.cbcc-canonical-leaf code{{font-size:10px;overflow-wrap:anywhere}}.cbcc-canonical-leaf pre{{white-space:pre-wrap;overflow-wrap:anywhere;margin:6px 0 0;font:inherit;font-size:11px}}.cbcc-copy-v0671{{border:1px solid var(--line,#ddd);background:var(--panel,#fff);border-radius:999px;padding:4px 8px;cursor:pointer}}#cbcc-canonical-search-v0671{{width:100%;padding:10px;border:1px solid var(--line,#ddd);border-radius:10px;background:var(--panel,#fff);color:inherit}}
</style>
'''


def audit_generic_human_field_coverage(payload: Mapping[str, Any], html_text: str) -> list[dict[str, Any]]:
    business = payload.get('canonical_business_objects') if isinstance(payload.get('canonical_business_objects'), Mapping) else {}
    missing = []
    for path, _ in _leaf_paths(business, 'canonical_business_objects'):
        marker = f'data-canonical-path="{html.escape(path, quote=True)}"'
        if marker not in html_text:
            missing.append(path)
    return [] if not missing else [{'code': 'HTML_CANONICAL_GENERIC_FIELD_COVERAGE_INCOMPLETE_V0671', 'missing_count': len(missing), 'missing': missing[:100]}]


def _primitive_tokens(v: Any) -> list[str]:
    return [text for _, text in _leaf_paths(v, '') if text.strip()]


def audit_listing_markdown_parity(package_dir: Path | str) -> list[dict[str, Any]]:
    package = Path(package_dir)
    center = _read_json(package / 'HUMAN_DELIVERY.json')
    if not center:
        return []
    md_path = package / '01_LISTING_UPLOAD_READY.md'
    if not md_path.exists():
        alt = package / 'listing/01_LISTING_UPLOAD_READY.md'
        md_path = alt if alt.exists() else md_path
    if not md_path.exists():
        return [{'code': 'LISTING_MARKDOWN_MISSING'}]
    text = md_path.read_text(encoding='utf-8', errors='ignore')
    missing: list[dict[str, Any]] = []
    for source in ('copy_center', 'localized_copy'):
        for i, row in enumerate(_l(center.get(source))):
            if not isinstance(row, Mapping):
                continue
            for field in ('value', 'delivery_translation'):
                if not _p(row.get(field)):
                    continue
                for token in _primitive_tokens(row.get(field)):
                    if token not in text:
                        missing.append({'source': source, 'row': i, 'field': row.get('field'), 'slot': field, 'token': token[:180]})
    if not missing:
        return []
    return [{'code': 'LISTING_MARKDOWN_CANONICAL_FIELD_DRIFT', 'missing_count': len(missing), 'missing': missing[:100]}]


def finalize_static_human_projection(package_dir: Path | str) -> dict[str, Any]:
    package = Path(package_dir)
    html_path = package / 'index.html'
    if not html_path.exists():
        return {'status': 'NOT_FOUND', 'issues': [{'code': 'INDEX_MISSING'}]}
    payload = build_canonical_human_payload(package)
    (package / DATA_FILE).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # Preserve the v0.6.70 renderer for legacy function-based workspaces, but pass real final-package data
    # explicitly so it never depends on a synthetic const DATA fixture.
    prior = apply_complete_canonical_human_projection(html_path, payload)
    page = html_path.read_text(encoding='utf-8', errors='ignore')
    if MARKER not in page:
        listing_panel = _summary_panel('Canonical Listing / 上架完整字段', payload.get('listing') or {}, 'listing')
        page, _ = _insert_route(page, 'listing', listing_panel)
        strategy_panel = _summary_panel('Canonical Strategy / 商业决策完整字段', payload.get('strategy') or {}, 'strategy')
        page, _ = _insert_route(page, 'strategy', strategy_panel)
        product_panel = _summary_panel('Product Truth / 产品真源完整字段', _d(payload.get('canonical_business_objects')).get('product_truth') or payload.get('truth') or {}, 'product_truth')
        page, _ = _insert_route(page, 'product', product_panel)
        visual_panel = _summary_panel('Visual / Photography / Inclusive 执行', payload.get('visual') or {}, 'visual')
        page, _ = _insert_route(page, 'visual', visual_panel)
        content_panel = _summary_panel('Content / RACE / Culture / Ads', {'content': payload.get('content'), 'race': payload.get('race'), 'culture': payload.get('culture'), 'ads': payload.get('ads')}, 'campaign')
        page, _ = _insert_route(page, 'content', content_panel)
        asset_panel = _asset_panel([x for x in _l(payload.get('assets')) if isinstance(x, dict)])
        page, inserted = _insert_route(page, 'prompts', asset_panel)
        if not inserted:
            page, _ = _insert_route(page, 'assets', asset_panel)
        archive = _summary_panel('Canonical Business Objects / 完整字段档案', payload.get('canonical_business_objects') or {}, 'canonical_business_objects')
        page, inserted = _insert_route(page, 'sources', archive)
        if not inserted:
            page = page.replace('</body>', archive + '</body>', 1) if '</body>' in page else page + archive
        script = _script(payload)
        page = page.replace('</body>', script + '</body>', 1) if '</body>' in page else page + script
        html_path.write_text(page, encoding='utf-8')

    final_text = html_path.read_text(encoding='utf-8', errors='ignore')
    issues = audit_generic_human_field_coverage(payload, final_text)
    return {
        'status': 'PASS' if not issues else 'INCOMPLETE',
        'issues': issues,
        'path': str(html_path),
        'data_file': DATA_FILE,
        'v0670_projection': prior,
        'marker': MARKER,
        'canonical_leaf_count': len(_leaf_paths(payload.get('canonical_business_objects') or {}, 'canonical_business_objects')),
    }
