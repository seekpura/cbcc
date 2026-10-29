from runtime.cbcc.commerce_decision_context import compile_commerce_decision_context, bind_asset_decision_lineage

def test_reviews_bind_to_feedback_usage_assets_only():
    ctx=compile_commerce_decision_context(domain={'feedback':{'issues':['usage confusion']}})
    hero=bind_asset_decision_lineage({'asset_id':'H','decision_intent':'IDENTIFY'},ctx)
    usage=bind_asset_decision_lineage({'asset_id':'U','decision_intent':'USAGE'},ctx)
    assert 'reviews' not in hero
    assert usage['reviews']['issues']==['usage confusion']
