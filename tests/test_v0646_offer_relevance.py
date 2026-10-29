from runtime.cbcc.commerce_decision_context import compile_commerce_decision_context, bind_asset_decision_lineage

def test_pricing_decision_only_for_offer_relevant_asset():
    ctx=compile_commerce_decision_context(domain={'pricing_economics_authority':{'pricing_decision':{'decision':69,'why':'fit'},'price_bands':[50,80]}})
    hero=bind_asset_decision_lineage({'asset_id':'H','surface':'GALLERY','decision_intent':'IDENTIFY'},ctx)
    paid=bind_asset_decision_lineage({'asset_id':'P','surface':'PAID_AD','offer_relevant':True},ctx)
    assert 'pricing_decision' not in hero.get('pricing_economics',{})
    assert paid['pricing_economics']['pricing_decision']['decision']==69
