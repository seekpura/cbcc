from runtime.cbcc.commercial_curation_lineage import _decision_basis

def test_curation_basis_has_market_listing_review_origins():
    basis=_decision_basis([
        {'asset_id':'M','decision_origin':'MARKET_THEME_FIT','decision_source':{'theme':'portable'},'consumer_question':'why this'},
        {'asset_id':'L','decision_origin':'LISTING_OBJECTION','decision_source':{'objection':'size'},'consumer_question':'will it fit'},
        {'asset_id':'R','decision_origin':'FEEDBACK_SIGNAL','decision_source':{'issue':'usage'},'consumer_question':'how to use'},
    ],{}, {'market':'MY'})
    assert {'MARKET_THEME_FIT','LISTING_OBJECTION','FEEDBACK_SIGNAL'} <= set(basis['decision_origins'])
    assert len(basis['decision_signals'])==3
