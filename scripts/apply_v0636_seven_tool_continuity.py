#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.6.36-seven-tool-capability-continuity'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding='utf-8')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'v0.6.36 patch anchor not found: {label}')
    return text.replace(old, new, 1)


def patch_version() -> None:
    write('VERSION', VERSION + '\n')


def patch_skill() -> None:
    text = read('SKILL.md')
    text = re.sub(r'^version:\s*[^\n]+$', f'version: {VERSION}', text, count=1, flags=re.M)
    heading = '## Seven First-Class Commerce Tools + Pricing/Economics Integrity — highest current precedence\n'
    if heading not in text:
        marker = '# Cross-Border Commerce Creative — Hard Contract Strategy → Creative → Production Build\n\n'
        section = '''## Seven First-Class Commerce Tools + Pricing/Economics Integrity — highest current precedence
- **七大工具是一等能力，不是文档目录，也不是固定七步流水线。** `01 Market Research / 02 Product Strategy / 03 Listing Creative / 04 Product Image / 05 Product Video / 06 Advertising Optimization / 07 Review Analysis` 必须持续可用；项目按相关性激活，但任何一次视觉/Prompt升级不得把商业能力挤出顶层权威。
- 每个工具的 release acceptance 必须证明 `Runtime 入口 → 真实 Consumer → 业务产物 → index.html 人类交付 → Plugin 顶层激活`；仅文件存在、import 成功或测试函数存在不算保留。
- **Product Strategy 必须包含 Pricing/Economics/Offer。** 至少物化 `SKU Roles / Price Bands / Price Valleys / Price×Configuration Matrix / Unit Economics / Contribution Waterfall / Contribution Margin / Break-even CPA / Break-even CPC / Break-even ROAS / Offer-Bundle-Discount Boundary / Pricing Decision + WHY`。
- **经济计算只允许显式输入。** 缺失的成本、平台费、履约、联盟佣金、税、退款预留、CVR、费率基数等保持 `MISSING_INPUT`；显式 0 可以参与计算，但“没填”绝不能自动当 0。Break-even CPC 只有在 click→order CVR 明确提供时才计算。
- 市场价格带/价格洼地是证据，不是自动定价建议。Runtime 可以计算与验证边界，但 **Pricing Decision + WHY、SKU 角色、Offer 取舍仍由 Agent 作者化**。
- Pricing/Economics 必须真正向下游消费：Listing 获得选定价格/Offer及边界但不得把价格强塞进所有字段；Ads 获得 Break-even CPA/CPC/ROAS 并与真实投放表现比较；Image/Video 仅在购买决策需要时消费 Offer/经济上下文，不得因此让所有资产出现价格。
- 七工具与视觉生产是并列一等能力：v0.6.30–v0.6.35 的 Agent Art Direction、Model-Native Prompt、Production Parameter Closure、Asset Universe、多 Hero、Reference-Guided Native Generation 全部继续有效。

'''
        text = replace_once(text, marker, marker + section, 'SKILL top authority')
    write('SKILL.md', text)


def patch_compiler() -> None:
    text = read('runtime/cbcc/compiler.py')
    import_anchor = 'from .evidence_reconciliation import compile_market_evidence_fit_contract\n'
    imports = (
        import_anchor
        + 'from .pricing_economics_authority import compile_pricing_economics_authority\n'
        + 'from .seven_tool_continuity import compile_seven_tool_continuity\n'
    )
    text = replace_once(text, import_anchor, imports, 'compiler imports')

    econ_anchor = "    ed=domain['economics']; ecp=_write(p/'artifacts/offer_economics.json',ed); st.set_gate('OFFER_ECONOMICS','READY_REVIEW',[ecp],ed)\n"
    econ_patch = econ_anchor + """    pricing_economics=compile_pricing_economics_authority(request,domain.get('market'),domain.get('economics'))
    domain['pricing_economics_authority']=pricing_economics
    if isinstance(domain.get('economics'),dict):
        domain['economics']['pricing_economics_authority']=pricing_economics
    _write(p/'artifacts/pricing_economics_authority.json',pricing_economics)
"""
    text = replace_once(text, econ_anchor, econ_patch, 'pricing authority after economics')

    strategy_anchor = "    strategy_context=compile_strategy_reasoning_context(request)\n"
    strategy_patch = """    pricing_consumers=(domain.get('pricing_economics_authority') or {}).get('downstream_consumers') or {}
    if domain.get('listing'):
        domain['listing']['pricing_offer_context']=pricing_consumers.get('listing_creative') or {}
        _write(p/'artifacts/listing_pricing_offer_context.json',domain['listing']['pricing_offer_context'])
    if domain.get('ads'):
        domain['ads']['pricing_economics_context']=pricing_consumers.get('advertising_optimization') or {}
        _write(p/'artifacts/ads_pricing_economics_context.json',domain['ads']['pricing_economics_context'])
    _write(p/'artifacts/product_strategy_pricing_context.json',pricing_consumers.get('product_strategy') or {})

""" + strategy_anchor
    text = replace_once(text, strategy_anchor, strategy_patch, 'downstream pricing consumers')

    seven_anchor = "    seven_agent_synthesis=compile_seven_agent_synthesis(domain=domain,architecture=architecture,video_plan=video_plan,paid_campaigns=paid_campaigns,source_product_assets=source_product_assets)\n"
    seven_patch = seven_anchor + """    seven_tool_continuity=compile_seven_tool_continuity(
        domain=domain,architecture=architecture,video_plan=video_plan,paid_campaigns=paid_campaigns,
        pricing_economics=domain.get('pricing_economics_authority'))
    seven_agent_synthesis['v0636_continuity']=seven_tool_continuity
    seven_agent_synthesis['capabilities']=seven_tool_continuity.get('capabilities') or seven_agent_synthesis.get('capabilities') or []
    seven_agent_synthesis['all_seven_first_class']=seven_tool_continuity.get('all_seven_first_class')
    seven_agent_synthesis['pricing_economics_integrity']=seven_tool_continuity.get('pricing_economics_integrity')
    _write(p/'artifacts/seven_tool_continuity.json',seven_tool_continuity)
"""
    text = replace_once(text, seven_anchor, seven_patch, 'seven tool synthesis integration')

    write('runtime/cbcc/compiler.py', text)


def patch_provider_executor() -> None:
    text = read('runtime/cbcc/provider_executor.py')
    text = replace_once(
        text,
        "    if fidelity != 'LOCKED_PIXEL':\n        return []\n",
        "    if fidelity not in {'EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'}:\n        return []\n",
        'exact pixel layer manifest',
    )
    write('runtime/cbcc/provider_executor.py', text)


def patch_build_plugin() -> None:
    text = read('scripts/build_plugin_dist.py')
    marker = "DEFAULT_PROMPTS = [\n"
    prompt = "    '七大工具按一等能力执行并保持连续性：Market Research → Product Strategy（含 SKU / Pricing / Economics / Offer）→ Listing Creative → Product Image → Product Video → Advertising Optimization → Review Analysis。项目按相关性激活，不得因视觉任务而降级商业能力。Pricing/Economics 必须使用显式输入物化 Price Bands / Price Valleys / Price×Configuration / Contribution Waterfall / Margin / Break-even CPA-CPC-ROAS / Offer Boundary / Pricing Decision + WHY；缺失成本、费率或 CVR 保持 MISSING_INPUT，不得默认 0。每个工具都要进入 Runtime consumer、业务产物和中文 index.html。',\n"
    if prompt not in text:
        text = replace_once(text, marker, marker + prompt, 'plugin default prompt')
    wrapper_anchor = "# Cross-Border Commerce Creative v{version}\\n\\n## Agent Creative Authority\n"
    # skill_wrapper is an f-string literal; patch its generated text source around the visible authority heading.
    source_anchor = "# Cross-Border Commerce Creative v{version}\n\n## Agent Creative Authority\n"
    if '## Seven First-Class Commerce Tools\n' not in text:
        source_replacement = """# Cross-Border Commerce Creative v{version}

## Seven First-Class Commerce Tools
七大工具始终是一等能力：Market Research；Product Strategy（SKU + Pricing + Economics + Offer）；Listing Creative；Product Image；Product Video；Advertising Optimization；Review Analysis。按项目相关性激活，不是固定流水线。Pricing/Economics 只使用显式输入，必须向 Listing/Ads/Strategy 真实投影；缺值保持 MISSING_INPUT。视觉/视频能力与商业能力并列，不能互相挤掉。

## Agent Creative Authority
"""
        text = replace_once(text, source_anchor, source_replacement, 'plugin wrapper seven tools')
    write('scripts/build_plugin_dist.py', text)


def patch_delivery_workspace() -> None:
    path = ROOT / 'runtime/cbcc/delivery_workspace.py'
    text = path.read_text(encoding='utf-8')
    if 'def _inject_commercial_brain(' in text:
        return
    text = text.replace('from pathlib import Path\n', 'from pathlib import Path\nimport html\nimport json\n')
    helper = r'''

def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _commercial_brain_html(package_dir: Path) -> str:
    artifacts = package_dir / 'artifacts'
    continuity = _load_json(artifacts / 'seven_tool_continuity.json')
    pricing = _load_json(artifacts / 'pricing_economics_authority.json')
    if not continuity and not pricing:
        return ''
    capabilities = continuity.get('capabilities') or []
    cards = []
    for item in capabilities:
        cards.append(
            '<article class="cbcc-commerce-card">'
            f'<div class="cbcc-commerce-kicker">{html.escape(str(item.get("id") or ""))}</div>'
            f'<h3>{html.escape(str(item.get("name") or item.get("id") or ""))}</h3>'
            f'<p><b>状态：</b>{html.escape(str(item.get("project_status") or ""))}</p>'
            f'<p><b>Runtime：</b>{html.escape(str(item.get("runtime_entry") or ""))}</p>'
            f'<p><b>真实 Consumer：</b>{html.escape(" · ".join(str(x) for x in item.get("real_consumers") or []))}</p>'
            f'<p><b>业务产物：</b>{html.escape(" · ".join(str(x) for x in item.get("business_outputs") or []))}</p>'
            f'<p><b>人类交付：</b>{html.escape(str(item.get("human_delivery") or ""))}</p>'
            '</article>'
        )
    scenario_rows = []
    for row in pricing.get('scenarios') or []:
        scenario_rows.append(
            '<tr>'
            f'<td>{html.escape(str(row.get("scenario_id") or ""))}</td>'
            f'<td>{html.escape(str(row.get("sku") or ""))}</td>'
            f'<td>{html.escape(str(row.get("price") if row.get("price") is not None else "—"))}</td>'
            f'<td>{html.escape(str(row.get("contribution_before_ads") if row.get("contribution_before_ads") is not None else "—"))}</td>'
            f'<td>{html.escape(str(row.get("contribution_margin_rate_before_ads") if row.get("contribution_margin_rate_before_ads") is not None else "—"))}</td>'
            f'<td>{html.escape(str(row.get("break_even_cpa") if row.get("break_even_cpa") is not None else "—"))}</td>'
            f'<td>{html.escape(str(row.get("break_even_cpc") if row.get("break_even_cpc") is not None else "待显式 CVR"))}</td>'
            f'<td>{html.escape(str(row.get("break_even_roas") if row.get("break_even_roas") is not None else "—"))}</td>'
            f'<td>{html.escape(str(row.get("status") or ""))}</td>'
            '</tr>'
        )
    decision = pricing.get('pricing_decision') or {}
    missing = pricing.get('missing_inputs') or []
    style = """<style id="cbcc-commerce-brain-style">
#commercial-brain{padding:28px 0}.cbcc-commerce-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.cbcc-commerce-card{border:1px solid var(--line,#ddd);border-radius:16px;padding:16px;background:#fff}.cbcc-commerce-card h3{margin:4px 0 10px}.cbcc-commerce-card p{margin:6px 0;font-size:12px;line-height:1.55}.cbcc-commerce-kicker{font-size:10px;letter-spacing:.08em;color:var(--muted,#666)}.cbcc-econ-table{width:100%;border-collapse:collapse;margin-top:12px;font-size:11px}.cbcc-econ-table th,.cbcc-econ-table td{border-bottom:1px solid var(--line,#ddd);padding:8px;text-align:left;vertical-align:top}.cbcc-commerce-note{border:1px solid var(--line,#ddd);border-radius:14px;padding:14px;margin:12px 0;background:var(--soft,#f7f7f7)}</style>"""
    return style + '<section id="commercial-brain" class="section"><div class="section-head"><div><div class="eyebrow">COMMERCIAL BRAIN</div><h2>七大工具 / 定价与经济性</h2><p>商业能力与视觉生产并列；这里展示真实 Runtime Consumer、业务产物与经济边界。</p></div></div>' + '<div class="cbcc-commerce-grid">' + ''.join(cards) + '</div>' + '<div class="cbcc-commerce-note"><b>Pricing Decision + WHY：</b> ' + html.escape(str(decision.get('decision') or '待 Agent 决策')) + '<br><b>WHY：</b> ' + html.escape(str(decision.get('why') or '需基于市场证据、SKU角色与单位经济作者化')) + '<br><b>状态：</b> ' + html.escape(str(decision.get('status') or pricing.get('status') or 'NOT_SUPPLIED')) + '</div>' + '<div class="cbcc-commerce-note"><b>市场价格带：</b> ' + html.escape(json.dumps(pricing.get('market_price_bands') or [], ensure_ascii=False)) + '<br><b>价格洼地：</b> ' + html.escape(json.dumps(pricing.get('market_price_valleys') or [], ensure_ascii=False)) + '<br><b>Price × Configuration：</b> ' + html.escape(json.dumps(pricing.get('price_configuration_matrix') or [], ensure_ascii=False)) + '</div>' + '<div class="cbcc-commerce-note"><b>SKU Roles：</b> ' + html.escape(json.dumps(pricing.get('sku_roles') or [], ensure_ascii=False)) + '<br><b>Offer / Bundle / Discount Boundary：</b> ' + html.escape(json.dumps(pricing.get('offer_bundle_discount_boundary') or [], ensure_ascii=False)) + '<br><b>缺失输入：</b> ' + html.escape(json.dumps(missing, ensure_ascii=False)) + '</div>' + '<div style="overflow:auto"><table class="cbcc-econ-table"><thead><tr><th>Scenario</th><th>SKU</th><th>Price</th><th>Contribution before Ads</th><th>Margin</th><th>Break-even CPA</th><th>Break-even CPC</th><th>Break-even ROAS</th><th>Status</th></tr></thead><tbody>' + ''.join(scenario_rows) + '</tbody></table></div></section>'


def _inject_commercial_brain(page: str, package_dir: Path) -> str:
    block = _commercial_brain_html(package_dir)
    if not block or 'id="commercial-brain"' in page:
        return page
    marker = '</main>' if '</main>' in page else '</body>'
    return page.replace(marker, block + marker, 1)
'''
    text = text.replace('\n\ndef build_delivery_html(', helper + '\n\ndef build_delivery_html(', 1)
    text = text.replace("    text = _transform_to_object_workspace(text)\n", "    text = _transform_to_object_workspace(text)\n    text = _inject_commercial_brain(text, package_dir)\n", 1)
    path.write_text(text, encoding='utf-8')


def main() -> None:
    patch_version()
    patch_skill()
    patch_compiler()
    patch_provider_executor()
    patch_build_plugin()
    patch_delivery_workspace()
    print('v0.6.36 seven-tool continuity migration applied')


if __name__ == '__main__':
    main()
