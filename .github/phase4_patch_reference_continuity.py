from pathlib import Path

p=Path('runtime/cbcc/commercial_continuity_authority.py')
t=p.read_text(encoding='utf-8')
old="""        context = compile_commerce_decision_context(domain=_dict(domain))
        out['asset_input_summary'] = deepcopy(out.get('asset_inputs') or {})
        out['asset_inputs'] = context
        out['commerce_decision_context'] = context
"""
new="""        context = compile_commerce_decision_context(domain=_dict(domain))
        original_asset_inputs = deepcopy(out.get('asset_inputs') or {})
        # Commercial continuity upgrades summary-only business payloads, but product-source
        # reference inputs are an independent fidelity channel and must survive that upgrade.
        # Preserve the canonical source-usage contract without copying the old summary fields
        # back over the richer commerce decision context.
        product_sources = original_asset_inputs.get('product_sources')
        if _nonempty(product_sources):
            context['product_sources'] = deepcopy(product_sources)
        out['asset_input_summary'] = original_asset_inputs
        out['asset_inputs'] = context
        out['commerce_decision_context'] = context
"""
if old not in t:
    raise SystemExit('target continuity block not found; refusing blind patch')
p.write_text(t.replace(old,new,1),encoding='utf-8')
