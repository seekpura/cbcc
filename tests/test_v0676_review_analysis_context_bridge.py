from __future__ import annotations
from pathlib import Path
import importlib.util, sys, pytest

ROOT=Path(__file__).parents[1]
MODULE=ROOT/'runtime/cbcc/review_analysis_authority.py'
spec=importlib.util.spec_from_file_location('review_analysis_context_v0676',MODULE)
mod=importlib.util.module_from_spec(spec); assert spec and spec.loader
sys.modules[spec.name]=mod; spec.loader.exec_module(mod)

FIX=ROOT/'tests/test_v0676_review_analysis_authority.py'
fspec=importlib.util.spec_from_file_location('review_analysis_fixture_v0676',FIX)
fx=importlib.util.module_from_spec(fspec); assert fspec and fspec.loader
sys.modules[fspec.name]=fx; fspec.loader.exec_module(fx)


def test_feedback_analyzer_consumes_full_review_context_once():
    req=fx.request(); req['feedback_rows']=[{'category':'EXPECTATION_GAP','severity':'HIGH','text':'usage expectation mismatch'}]
    seed=mod.wrap_compile_request_checkpoint_for_review_context(lambda request,*a,**k:{'status':'READY'})
    analyze=mod.wrap_analyze_feedback(lambda rows:{'status':'AGGREGATED_FROM_CLASSIFIED_INPUT','summary':{'total':len(rows)},'issues':[]})
    seed(req)
    first=analyze(req['feedback_rows'])
    assert first['phase2_business_status']=='READY'
    assert first['phase2_review_analysis_authority']['status']=='READY'
    second=analyze(req['feedback_rows'])
    assert 'phase2_review_analysis_authority' not in second


def test_explicit_review_plan_without_feedback_data_materializes_without_fabricated_counts_and_restores_request():
    req=fx.request(); original=req.get('feedback_rows','__ABSENT__')
    seed=mod.wrap_compile_request_checkpoint_for_review_context(lambda request,*a,**k:{'status':'READY'})
    called={'n':0}
    def base(rows):
        called['n']+=1
        raise AssertionError('feedback aggregator must not run for internal no-data stub')
    analyze=mod.wrap_analyze_feedback(base)
    seed(req)
    assert req.get('feedback_rows')
    out=analyze(req['feedback_rows'])
    assert out['status']=='NO_CUSTOMER_REVIEW_DATA_SUPPLIED'
    assert out['summary']['total']==0
    assert out['issues']==[]
    assert out['phase2_business_status']=='READY'
    assert out['phase2_review_analysis_authority']['feedback_analysis']['summary']['total']==0
    assert called['n']==0
    if original=='__ABSENT__':
        assert 'feedback_rows' not in req
    else:
        assert req['feedback_rows']==original


def test_request_without_feedback_or_review_scope_clears_context():
    req={'delivery_mode':'FULL_PROJECT'}
    seed=mod.wrap_compile_request_checkpoint_for_review_context(lambda request,*a,**k:{'status':'READY'})
    analyze=mod.wrap_analyze_feedback(lambda rows:{'status':'AGGREGATED_FROM_CLASSIFIED_INPUT'})
    seed(req)
    out=analyze([])
    assert 'phase2_review_analysis_authority' not in out


def test_feedback_analyzer_exception_clears_context_and_restores_internal_stub():
    req=fx.request()
    seed=mod.wrap_compile_request_checkpoint_for_review_context(lambda request,*a,**k:{'status':'READY'})
    seed(req)
    boom=mod.wrap_analyze_feedback(lambda rows:(_ for _ in ()).throw(RuntimeError('boom')))
    mod._cleanup_internal_review_stub(); mod._REVIEW_CONTEXT.set({'request':fx.request(),'checkpoint':{'status':'READY'}})
    with pytest.raises(RuntimeError): boom([{'category':'EXPECTATION_GAP'}])
    safe=mod.wrap_analyze_feedback(lambda rows:{'status':'AGGREGATED_FROM_CLASSIFIED_INPUT'})
    assert 'phase2_review_analysis_authority' not in safe([])
    assert 'feedback_rows' not in req


def test_checkpoint_exception_clears_prior_review_context():
    req=fx.request(); req['feedback_rows']=[{'category':'EXPECTATION_GAP'}]
    good=mod.wrap_compile_request_checkpoint_for_review_context(lambda request,*a,**k:{'status':'READY'})
    good(req)
    bad=mod.wrap_compile_request_checkpoint_for_review_context(lambda *a,**k:(_ for _ in ()).throw(RuntimeError('checkpoint boom')))
    with pytest.raises(RuntimeError): bad(req)
    safe=mod.wrap_analyze_feedback(lambda rows:{'status':'AGGREGATED_FROM_CLASSIFIED_INPUT'})
    assert 'phase2_review_analysis_authority' not in safe([])


def test_review_no_data_stub_preserves_unrelated_listing_and_ads_request_inputs():
    from copy import deepcopy
    req=fx.request()
    req['listing_input']={'fields':{'title':'keep-me'}}
    req['ad_analysis']={'ad_data':{'impressions':100,'clicks':5}}
    expected_listing=deepcopy(req['listing_input']); expected_ads=deepcopy(req['ad_analysis'])
    seed=mod.wrap_compile_request_checkpoint_for_review_context(lambda request,*a,**k:{'status':'READY'})
    analyze=mod.wrap_analyze_feedback(lambda rows: (_ for _ in ()).throw(AssertionError('no-data stub must bypass aggregator')))
    seed(req)
    analyze(req['feedback_rows'])
    assert req['listing_input']==expected_listing
    assert req['ad_analysis']==expected_ads
    assert 'feedback_rows' not in req
