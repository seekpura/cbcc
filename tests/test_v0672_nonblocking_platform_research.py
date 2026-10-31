from cbcc.compliance import compile_compliance


def test_nonblocking_platform_research_does_not_hold_current_scope_compliance():
    out = compile_compliance(
        {'sku':'K01'},
        [{'claim_id':'CLM-SIZE','evidence_grade':'A','status':'APPROVED'}],
        {'status':'LISTING_CONTRACT_COMPILED'},
        [{'asset_id':'AST-1','claim_ids':['CLM-SIZE']}],
        {'status':'RESEARCH_REQUIRED'},
        {'pending':[{'action_id':'RA-1','blocking':False,'reason':'refresh current category guidance'}]},
    )
    assert out['issues'] == []
    assert out['research_pending'] is True
    assert out['research_blocking_pending'] is False
    assert out['platform_status'] == 'RESEARCH_REQUIRED'
    assert out['status'] == 'READY_REVIEW'


def test_blocking_research_still_holds_compliance():
    out = compile_compliance(
        {'sku':'K01'}, [], {'status':'LISTING_CONTRACT_COMPILED'}, [],
        {'status':'RESEARCH_REQUIRED'},
        {'pending':[{'action_id':'RA-BLOCK','blocking':True}]},
    )
    assert out['status'] == 'HOLD'
