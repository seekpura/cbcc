from runtime.cbcc.asset_portfolio_taxonomy import enrich_asset_portfolio_taxonomy

def test_non_gallery_families_coexist():
    rows=enrich_asset_portfolio_taxonomy([
        {'asset_id':'P','surface':'PDP'},
        {'asset_id':'A','surface':'A_PLUS'},
        {'asset_id':'D','surface':'PAID_AD'},
        {'asset_id':'S','surface':'SOCIAL_CONTENT'},
    ])
    assert {x['asset_family'] for x in rows}=={'PDP','A_PLUS','AD','SOCIAL_SEEDING'}
