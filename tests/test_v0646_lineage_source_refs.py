from runtime.cbcc.commerce_decision_context import compile_commerce_decision_context, bind_asset_decision_lineage

def test_asset_lineage_keeps_source_artifact_and_path():
    ctx=compile_commerce_decision_context(domain={'market':{'customer_voice':['clear']},'pricing_economics_authority':{'pricing_decision':{'decision':49,'why':'fit'}}})
    out=bind_asset_decision_lineage({'asset_id':'A','surface':'PAID_AD','offer_relevant':True},ctx)
    assert out['lineage_refs']
    assert all(x.get('source_artifact') and x.get('source_path') for x in out['lineage_refs'])
