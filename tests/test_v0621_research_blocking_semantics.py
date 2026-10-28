from cbcc.agent_autonomy import compile_agent_autonomy_plan
from cbcc.compliance import compile_compliance
from cbcc.research import compile_research_gate


def _platform_ready():
    return {'status':'VERIFIED_FOR_REQUEST'}


def test_agent_fallback_research_gaps_are_advisory_by_default():
    plan=compile_agent_autonomy_plan({'target':{'market':'Malaysia','platform_family':'TIKTOK_SHOP','site':'MY'}})
    requirements=plan['research']['requirements']
    assert requirements
    assert all(row['blocking'] is False for row in requirements)
    gate=compile_research_gate(requirements,[])
    assert gate['status']=='RESEARCH_REQUIRED'
    assert gate['blocking_pending']==[]
    assert len(gate['advisory_pending'])==len(requirements)


def test_advisory_research_stays_visible_without_forcing_compliance_hold():
    gate=compile_research_gate([
        {'id':'R1','topic':'shopper objections','domain':'MARKET','blocking':False,'required_for':['STRATEGY']}
    ],[])
    out=compile_compliance({},[],None,[],_platform_ready(),gate)
    assert out['research_pending'] is True
    assert out['research_blocking_pending'] is False
    assert out['status']=='READY_REVIEW'


def test_explicit_blocking_research_preserves_fail_closed_boundary():
    gate=compile_research_gate([
        {'id':'R2','topic':'current restricted claim rule','domain':'LEGAL','blocking':True,'required_for':['COMPLIANCE']}
    ],[])
    out=compile_compliance({},[],None,[],_platform_ready(),gate)
    assert out['research_pending'] is True
    assert out['research_blocking_pending'] is True
    assert out['status']=='HOLD'


def test_legacy_explicit_research_requirement_remains_blocking_when_flag_is_absent():
    gate=compile_research_gate([
        {'id':'R3','topic':'explicit caller requirement','domain':'PLATFORM_RULE','required_for':['PLATFORM_COMPILE']}
    ],[])
    assert gate['pending'][0]['blocking'] is True
    assert gate['actions'][0]['blocking'] is True
