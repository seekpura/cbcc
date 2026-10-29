from runtime.cbcc.asset_portfolio_taxonomy import portfolio_taxonomy_summary

def test_portfolio_summary_has_no_family_quota():
    summary=portfolio_taxonomy_summary([],{'gallery_capacity':9})
    assert summary['fixed_total_asset_limit'] is False
    assert 'HERO' in summary['supported_asset_families']
    assert 'A_PLUS' in summary['supported_asset_families']
    assert 'SOCIAL_SEEDING' in summary['supported_asset_families']
    assert 'CREATOR_UGC' in summary['supported_asset_families']
