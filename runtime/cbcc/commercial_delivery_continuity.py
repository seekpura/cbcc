from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
import json

from .commerce_decision_context import compile_commerce_decision_context
from .commercial_intelligence_workspace import render_commercial_intelligence_workspace, commercial_intelligence_css
from .asset_portfolio_taxonomy import enrich_asset_portfolio_taxonomy, portfolio_taxonomy_summary
from .asset_portfolio_workspace import render_asset_portfolio_workspace, asset_portfolio_css


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _asset_portfolio(project: Path, target: dict[str, Any]) -> dict[str, Any]:
    architecture = _read_json(project / 'artifacts' / 'asset_architecture.json')
    assets = enrich_asset_portfolio_taxonomy(architecture.get('assets') or [])
    summary = portfolio_taxonomy_summary(assets, target)
    compact = []
    for a in assets:
        compact.append({
            'asset_id': a.get('asset_id'),
            'asset_family': a.get('asset_family'),
            'surface': a.get('surface'),
            'deployment_state': a.get('deployment_state'),
            'variant_id': a.get('variant_id'),
            'variant_cluster': a.get('variant_cluster'),
            'test_hypothesis': a.get('test_hypothesis'),
            'business_hypothesis': a.get('business_hypothesis'),
            'decision_intent': a.get('decision_intent'),
        })
    return {
        'summary': summary,
        'assets': compact,
        'commercial_curation_continuity': architecture.get('commercial_curation_continuity'),
        'asset_universe': architecture.get('asset_universe'),
    }


def materialize_commerce_decision_context(project_dir: Path | str) -> dict[str, Any]:
    project = Path(project_dir)
    artifacts = project / 'artifacts'
    domain = _read_json(artifacts / 'domain_analysis.json')
    pricing = _read_json(artifacts / 'pricing_economics_authority.json')
    if pricing:
        domain['pricing_economics_authority'] = pricing
        economics = dict(domain.get('economics') or {})
        economics['pricing_economics_authority'] = pricing
        domain['economics'] = economics
    strategy = _read_json(artifacts / 'strategy_authority.json') or _read_json(artifacts / 'strategy' / 'strategy_authority.json')
    culture = _read_json(artifacts / 'culture_context.json')
    target_context = _read_json(artifacts / 'target_context.json')
    target = target_context.get('target') if isinstance(target_context.get('target'), dict) else target_context
    decision_trace = _read_json(artifacts / 'decision_trace.json')
    context = compile_commerce_decision_context(
        domain=domain, strategy=strategy, culture=culture, target=target, decision_trace=decision_trace
    )
    context['asset_portfolio'] = _asset_portfolio(project, target if isinstance(target, dict) else {})
    _write_json(artifacts / 'commerce_decision_context.json', context)
    _write_json(artifacts / 'strategy' / 'COMMERCE_DECISION_CONTEXT.json', context)
    return context


def compile_continuity_audit(project_dir: Path | str, context: dict[str, Any]) -> dict[str, Any]:
    project = Path(project_dir)
    asset_root = project / 'artifacts' / 'asset_packages'
    assets = []
    if asset_root.exists():
        for path in sorted(asset_root.glob('*/13_prompt_contract.json')):
            data = _read_json(path)
            continuity = data.get('commerce_decision_consumption_audit') or (data.get('prompt_consumption_audit') or {}).get('commerce_decision_continuity') or {}
            subject = (data.get('design_card') or {}).get('subject_system') or {}
            assets.append({
                'asset_id': path.parent.name,
                'status': continuity.get('status') or 'MISSING_CONTINUITY_AUDIT',
                'issues': continuity.get('issues') or [],
                'bound_domains': continuity.get('bound_domains') or [],
                'lineage_refs': continuity.get('lineage_refs') or [],
                'subject_type': subject.get('subject_type'),
                'subject_authority': subject.get('authority'),
            })
    gaps = [x for x in assets if x.get('status') not in {'PASS', 'NOT_BOUND'}]
    portfolio = context.get('asset_portfolio') or {}
    curation = portfolio.get('commercial_curation_continuity') or {}
    audit = {
        'status': 'PASS' if not gaps else 'INCOMPLETE',
        'context_status': context.get('status'),
        'lineage_domain_count': len(context.get('lineage_index') or []),
        'asset_count': len(assets),
        'assets': assets,
        'gaps': gaps,
        'curation_continuity': curation,
        'asset_portfolio_summary': portfolio.get('summary') or {},
        'rule': 'Commercial integration is proven by real downstream consumption, not by file presence or status/count summaries. Platform activation capacity never caps the asset universe.',
    }
    _write_json(project / 'artifacts' / 'commercial_continuity_audit.json', audit)
    _write_json(project / 'artifacts' / 'strategy' / 'COMMERCIAL_CONTINUITY_AUDIT.json', audit)
    return audit


def wrap_export_delivery_package(fn: Callable[..., dict[str, Any]]):
    def exported(project_dir, output, *args, **kwargs):
        context = materialize_commerce_decision_context(project_dir)
        compile_continuity_audit(project_dir, context)
        return fn(project_dir, output, *args, **kwargs)
    return exported


def _commerce_page(context: dict[str, Any]) -> str:
    body = render_commercial_intelligence_workspace(context)
    portfolio = render_asset_portfolio_workspace(context.get('asset_portfolio') or {})
    return (
        '<section class="page" data-route="commerce">'
        '<div class="page-head"><div><div class="kicker">COMMERCIAL INTELLIGENCE</div>'
        '<h1>商业洞察与决策血缘</h1>'
        '<p>市场、区域、人群、价格经济、RACE、Listing、Ads、Reviews、资产策展与 Prompt 使用同一来源链；只显示当前项目真实存在的对象。</p>'
        '</div></div>' + body + portfolio + '</section>'
    )


def _load_packaged_context(package_dir: Path) -> dict[str, Any]:
    for path in (
        package_dir / 'strategy' / 'COMMERCE_DECISION_CONTEXT.json',
        package_dir / 'supporting_analysis' / 'commerce_decision_context.json',
        package_dir / 'COMMERCE_DECISION_CONTEXT.json',
    ):
        data = _read_json(path)
        if data:
            return data
    return {}


def wrap_build_delivery_html(fn: Callable[..., Path]):
    """Add one routed commercial-intelligence work surface inside cbcc-commercial-v1."""
    def built(package_dir, output=None, title='CBCC Delivery', *args, **kwargs):
        result = fn(package_dir, output, title=title, *args, **kwargs)
        package = Path(package_dir)
        context = _load_packaged_context(package)
        if not context:
            return result
        page = result.read_text(encoding='utf-8')
        if 'data-route="commerce"' in page:
            return result

        nav_marker = '</div><div class="sidebar-foot">'
        nav_link = '<a href="#commerce" data-route="commerce" class="route-link"><span class="ico">◆</span>商业洞察</a>'
        if nav_marker in page:
            page = page.replace(nav_marker, nav_link + nav_marker, 1)

        route_page = _commerce_page(context)
        workspace_end = page.rfind('</div></div><script>')
        if workspace_end != -1:
            page = page[:workspace_end] + route_page + page[workspace_end:]
        elif '</body>' in page:
            page = page.replace('</body>', route_page + '</body>', 1)

        css = commercial_intelligence_css() + asset_portfolio_css()
        if '</style>' in page:
            page = page.replace('</style>', css + '</style>', 1)
        elif '</head>' in page:
            page = page.replace('</head>', '<style>' + css + '</style></head>', 1)
        result.write_text(page, encoding='utf-8')
        return result
    return built


# This module is imported as the final human-delivery layer from runtime.cbcc.__init__. Install the
# strict compatibility/bootstrap here so mature Pricing field names, false-READY prevention and the
# human asset commercial lineage projection are always active without replacing the existing authority stack.
from .commercial_continuity_bootstrap import install as _install_commercial_continuity
_install_commercial_continuity()
