from runtime.cbcc.asset_portfolio_taxonomy import enrich_asset_portfolio_taxonomy, portfolio_taxonomy_summary


def test_nine_slot_platform_does_not_reduce_twenty_asset_universe():
    assets=[]
    for i in range(20):
        assets.append({
            'asset_id': f'A{i+1:02d}',
            'surface': 'GALLERY' if i < 9 else ('PAID_AD' if i < 13 else ('A_PLUS' if i < 16 else 'SOCIAL_CONTENT')),
            'variant_cluster': 'HERO' if i < 3 else None,
            'testing_variant': i in {1, 2, 8, 18, 19},
        })
    enriched= enrich_asset_portfolio_taxonomy(assets)
    summary = portfolio_taxonomy_summary(enriched, {'gallery_capacity': 9})
    assert len(enriched) == 20
    assert summary['total_asset_candidates'] == 20
    assert summary['activation_capacity'] == 9
    assert summary['fixed_total_asset_limit'] is False
    assert summary['activation_capacity_does_not_prune_universe'] is True
