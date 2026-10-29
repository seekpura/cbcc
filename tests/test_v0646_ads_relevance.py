from runtime.cbcc.commerce_decision_context import compile_commerce_decision_context, bind_asset_decision_lineage

def test_ads_context_is_relevance_filtered():
    ctx=compile_commerce_decision_context(domain={'ads':{'diagnosis':[{'route':'CLICK_PACKAGE'}]}})
    hero=bind_asset_decision_lineage({'asset_id':'H','surface':'GALLERY'},ctx)
    ad=bind_asset_decision_lineage({'asset_id':'A','surface':'PAID_AD'},ctx)
    assert 'ads' not in hero
    assert ad['ads']['diagnosis'][0]['route']=='CLICK_PACKAGE'
