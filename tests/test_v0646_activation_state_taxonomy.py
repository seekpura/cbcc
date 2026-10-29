from runtime.cbcc.asset_portfolio_taxonomy import enrich_asset_portfolio_taxonomy

def test_deployment_states_are_business_pools_not_total_asset_quota():
    rows=enrich_asset_portfolio_taxonomy([
        {'asset_id':'L','surface':'GALLERY'},
        {'asset_id':'T','surface':'GALLERY','testing_variant':True},
        {'asset_id':'P','surface':'PAID_AD'},
        {'asset_id':'A','surface':'A_PLUS'},
        {'asset_id':'S','surface':'SOCIAL_CONTENT'},
    ])
    states={x['asset_id']:x['deployment_state'] for x in rows}
    assert states=={'L':'LIVE_CANDIDATE','T':'TEST_POOL','P':'PAID_MEDIA','A':'APLUS_CONTENT','S':'SOCIAL_CONTENT'}
