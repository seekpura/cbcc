from pathlib import Path
import json, sys, hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project
from cbcc.cli import main as cli_main
from cbcc.state import ProjectState
from cbcc.review import materialize_review_workspace
from cbcc.learning_loop import compile_local_revision_jobs, ingest_local_revision_results, sync_local_revision_review_state, compile_learning_cycle, apply_learning_to_strategy

FX=ROOT/'tests/fixtures/kiyuu_my_tiktok'

def _sha(path:Path):
    h=hashlib.sha256(path.read_bytes()).hexdigest(); return h

def _base_req():
    return json.loads((FX/'request.json').read_text(encoding='utf-8'))

def _all_true_qa():
    return {'product':True,'fact':True,'claim':True,'visual':True,'culture':True,'platform':True}


def _bind_test_master(req,tmp_path):
    master=tmp_path/'test-product-master.bin'; master.write_bytes(b'test-product-master')
    req['source_product_assets']=[{'asset_id':'TEST-MASTER','role':'FRONT_MASTER','path':str(master),'pixel_lock':True,'note':'TEST FIXTURE ONLY'}]
    return req

def _quality_observations(job):
    out={}
    for k in job['result_contract']['quality_observations_required']:
        if k=='source_product_asset_ids_used': out[k]=['TEST-MASTER']
        elif k=='source_product_hashes_used':
            bindings=job.get('source_product_bindings') or (job.get('production_quality_contract') or {}).get('source_product_bindings') or []
            out[k]={x['asset_id']:x['sha256'] for x in bindings}
        elif k=='product_layer_operation': out[k]='COMPOSITE_LOCKED'
        else: out[k]={'status':'PASS','evidence':'test observation for '+k}
    return out


def _portable_receipt(job):
    bindings=job.get('source_product_bindings') or []
    return {
        'job_id':job['job_id'],'asset_id':job['asset_id'],'provider':job['provider'],'package_hash':job['package_hash'],
        'portable_manifest_hash':job['portable_package']['portable_manifest_hash'],'source_binding_hash':job.get('source_binding_hash'),
        'output_artifacts':[{'uri':'fixture://provider-output/'+job['asset_id'],'sha256':'b'*64,'role':'FINAL'}],
        'layer_manifest':[{'layer_id':'product-'+str(i),'role':'PRODUCT_MASTER','source_asset_id':x['asset_id'],'source_sha256':x['sha256'],'operation':'COMPOSITE_LOCKED','frozen':True} for i,x in enumerate(bindings)],
        'capture_metadata':{},
    }


def test_v0512_host_final_copy_can_reach_approved_only_with_exact_review():
    req=_base_req(); li=req['listing_input']; fields=li['fields']
    fields['_localized_copy_reviews']=[
        {'locale':'en-MY','field':'title','decision':'APPROVED','native_fluency':'PASS','claim_equivalence':'PASS','platform_fit':'PASS','culture_fit':'PASS'},
        {'locale':'en-MY','field':'highlights','decision':'APPROVED','native_fluency':'PASS','claim_equivalence':'PASS','platform_fit':'PASS','culture_fit':'PASS'},
        {'locale':'ms-MY','field':'title','version_id':'MS-T-V1','decision':'APPROVED','native_fluency':'PASS','claim_equivalence':'PASS','platform_fit':'PASS','culture_fit':'PASS'},
        {'locale':'ms-MY','field':'highlights','version_id':'MS-H-V1','decision':'APPROVED','native_fluency':'PASS','claim_equivalence':'PASS','platform_fit':'PASS','culture_fit':'PASS'},
    ]
    li['host_authoring_responses']=[
        {'locale':'ms-MY','field':'title','version_id':'MS-T-V1','copy':'KIYUU K01 Gel Pelembap Kawalan Minyak Anti Acne 30g','author':'HOST-MODEL'},
        {'locale':'ms-MY','field':'highlights','version_id':'MS-H-V1','copy':['Pelembap gel harian untuk kulit berminyak dan mudah berjerawat.'],'author':'HOST-MODEL'},
    ]
    from cbcc.tools.listing import apply_host_copy_authoring_responses, compile_listing
    f,applied=apply_host_copy_authoring_responses(fields,li['host_authoring_responses'])
    out=compile_listing(f,req['product'],req['claims'],{}, {'primary_locale':'en-MY','visible_copy_locales':['en-MY','ms-MY']},li['keywords'],req['target'])
    assert applied['status']=='HOST_AUTHORING_RESPONSES_APPLIED'
    assert out['final_copy_workflow']['release_counts']['APPROVED_FINAL']==4
    assert out['copy_authoring_iteration_plan']['authoring_tasks']==[]
    assert out['copy_authoring_iteration_plan']['revision_tasks']==[]


def test_v0512_provider_review_local_revision_and_learning_are_one_bounded_loop(tmp_path):
    req=_base_req(); req['project_id']='V0512-LOOP'; req['production_run']={'asset_ids':[]}
    _bind_test_master(req,tmp_path)
    project=tmp_path/'project'; build_project(project,req,FX)
    base_truth_hash=_sha(project/'artifacts/product_truth.json')
    pkg_idx=json.loads((project/'artifacts/asset_packages/ASSET_PACKAGE_INDEX.json').read_text())
    aid=pkg_idx['assets'][0]['asset_id']; pkg=project/'artifacts/asset_packages'/aid
    base_pkg_hashes={f.name:_sha(f) for f in pkg.iterdir() if f.is_file()}
    # Initial provider result is explicit; runtime does not fabricate completion.
    job=json.loads((project/'artifacts/provider_jobs'/aid/'job.json').read_text())
    output=project/'outputs'/f'{aid}.png'; output.parent.mkdir(exist_ok=True); output.write_bytes(b'initial-provider-output')
    result={'asset_id':aid,'provider':job['provider'],'package_hash':job['package_hash'],'output_path':str(output),'changed_fields':[],'changed_layers':[],'qa':_all_true_qa(),'production_contract_ack':True,'source_binding_hash':job['source_binding_hash'],'layout_contract_hash':job['production_contract_binding']['layout_contract_hash'],'photography_contract_hash':job['production_contract_binding']['photography_contract_hash'],'quality_observations':_quality_observations(job),'production_receipt':_portable_receipt(job)}
    (project/'artifacts/provider_jobs'/aid/'result.json').write_text(json.dumps(result),encoding='utf-8')
    assert cli_main(['provider-ingest','--project-dir',str(project)])==0
    manifest=json.loads((project/'.cbcc/review/delivery_manifest.json').read_text())
    output_item=next(x for x in manifest['items'] if x['kind']=='PRODUCTION_OUTPUT' and x['asset_id']==aid)
    # Human review asks for a local-only headline change.
    st=ProjectState.load(project)
    st.apply_review_decision({'project_id':st.data['project_id'],'revision':st.data['revision'],'revise_items':[{'item_id':output_item['item_id'],'requested_change':'Clarify the first-frame headline only.','allowed_fields':['headline_copy'],'note':'Keep product, positioning, offer and visual system frozen.'}]})
    materialize_review_workspace(project,st.data)
    rr=st.data['local_revision_requests'][-1]
    assert rr['revision_request_id'].startswith('LRQ-') and rr['allowed_fields']==['headline_copy']
    comp=compile_local_revision_jobs(project,st.data,req.get('production_provider_preferences'))
    st.save(); materialize_review_workspace(project,st.data)
    assert comp['status']=='LOCAL_REVISION_JOBS_COMPILED' and comp['count']==1
    lineage=comp['compiled'][0]; rid=lineage['revision_id']
    assert lineage['parent_package_hash']==job['package_hash']
    rjob=json.loads((project/'artifacts/local_revisions'/rid/'provider_jobs'/aid/'job.json').read_text())
    assert rjob['revision_scope']['allowed_fields']==['headline_copy']
    assert rjob['package_hash']==job['package_hash']
    # Revised provider result changes only the approved field.
    rout=project/'outputs'/f'{aid}-rev1.png'; rout.write_bytes(b'revised-provider-output-headline-only')
    rres={'asset_id':aid,'provider':rjob['provider'],'package_hash':rjob['package_hash'],'output_path':str(rout),'changed_fields':['headline_copy'],'changed_layers':['typography_copy'],'qa':_all_true_qa(),'production_contract_ack':True,'source_binding_hash':rjob['source_binding_hash'],'layout_contract_hash':rjob['production_contract_binding']['layout_contract_hash'],'photography_contract_hash':rjob['production_contract_binding']['photography_contract_hash'],'quality_observations':_quality_observations(rjob),'production_receipt':_portable_receipt(rjob)}
    (project/'artifacts/local_revisions'/rid/'provider_jobs'/aid/'result.json').write_text(json.dumps(rres),encoding='utf-8')
    ing=ingest_local_revision_results(project,st.data,[rid]); st.save(); materialize_review_workspace(project,st.data)
    assert ing['revisions'][0]['status']=='READY_REVIEW'
    assert ing['revisions'][0]['output_hash']==_sha(rout)
    manifest=json.loads((project/'.cbcc/review/delivery_manifest.json').read_text())
    rev_item=next(x for x in manifest['items'] if x['kind']=='LOCAL_REVISION_OUTPUT' and x['revision_id']==rid)
    st.apply_review_decision({'project_id':st.data['project_id'],'revision':st.data['revision'],'accept_items':[rev_item['item_id']]})
    sync_local_revision_review_state(project,st.data); st.save(); materialize_review_workspace(project,st.data)
    assert next(x for x in st.data['local_revision_requests'] if x['revision_request_id']==rr['revision_request_id'])['status']=='ACCEPTED'
    # Learning is bounded to the edited layer; arithmetic improvement is not mislabeled causal.
    cycle={'cycle_id':'LC-HEADLINE-1','revision_id':rid,'edit_layers':['LISTING_HERO'],'freeze_layers':['PRODUCT_TRUTH','POSITIONING','OFFER','VISUAL_SYSTEM'],'baseline_metrics':{'cvr':0.020,'return_rate':0.080},'after_metrics':{'cvr':0.026,'return_rate':0.060},'metric_directions':{'cvr':'UP','return_rate':'DOWN'}}
    learning=compile_learning_cycle(project,st.data,cycle)
    assert learning['recommendation']=='KEEP_LOCAL_CHANGE_MONITOR'
    assert learning['causal_credit_allowed'] is False
    applied=apply_learning_to_strategy(project,learning)
    assert applied['status']=='STRATEGY_AUTHORITY_LEARNING_APPLIED'
    strategy=json.loads((project/'artifacts/strategy_authority.json').read_text())
    overlays=strategy['sections']['04_marketing_core_strategy']['listing_strategy']['learning_revision_overlays']
    assert overlays[-1]['cycle_id']=='LC-HEADLINE-1'
    assert not strategy['sections']['04_marketing_core_strategy']['positioning'].get('learning_revision_overlays')
    assert _sha(project/'artifacts/product_truth.json')==base_truth_hash
    assert {f.name:_sha(f) for f in pkg.iterdir() if f.is_file()}==base_pkg_hashes


def test_v0512_cli_revision_and_learning_lifecycle(tmp_path):
    req=_base_req(); req['project_id']='V0512-CLI'; req['production_run']={'asset_ids':[]}
    _bind_test_master(req,tmp_path)
    project=tmp_path/'cli-project'; build_project(project,req,FX)
    idx=json.loads((project/'artifacts/provider_jobs/PROVIDER_JOB_INDEX.json').read_text()); row=idx['jobs'][0]; aid=row['asset_id']
    job=json.loads(Path(row['job_path']).read_text()); out=project/'outputs'/f'{aid}.png'; out.parent.mkdir(exist_ok=True); out.write_bytes(b'initial')
    Path(row['result_path']).write_text(json.dumps({'asset_id':aid,'provider':job['provider'],'package_hash':job['package_hash'],'output_path':str(out),'changed_fields':[],'changed_layers':[],'qa':_all_true_qa(),'production_contract_ack':True,'source_binding_hash':job['source_binding_hash'],'quality_observations':_quality_observations(job),'production_receipt':_portable_receipt(job)}),encoding='utf-8')
    assert cli_main(['provider-ingest','--project-dir',str(project)])==0
    manifest=json.loads((project/'.cbcc/review/delivery_manifest.json').read_text()); oi=next(x for x in manifest['items'] if x['kind']=='PRODUCTION_OUTPUT' and x['asset_id']==aid)
    st=ProjectState.load(project); decision=tmp_path/'decision.json'; decision.write_text(json.dumps({'project_id':st.data['project_id'],'revision':st.data['revision'],'revise_items':[{'item_id':oi['item_id'],'requested_change':'Local CTA copy only','allowed_fields':['cta_copy']}]}),encoding='utf-8')
    assert cli_main(['review-apply','--project-dir',str(project),'--review-file',str(decision)])==0
    assert cli_main(['revision-compile','--project-dir',str(project)])==0
    ridx=json.loads((project/'artifacts/local_revisions/LOCAL_REVISION_INDEX.json').read_text()); rev=ridx['revisions'][0]; rid=rev['revision_id']
    rji=json.loads((project/'artifacts/local_revisions'/rid/'provider_jobs/PROVIDER_JOB_INDEX.json').read_text()); rr=rji['jobs'][0]; rjob=json.loads(Path(rr['job_path']).read_text()); rout=project/'outputs'/f'{aid}-cta.png'; rout.write_bytes(b'cta-revision')
    Path(rr['result_path']).write_text(json.dumps({'asset_id':aid,'provider':rjob['provider'],'package_hash':rjob['package_hash'],'output_path':str(rout),'changed_fields':['cta_copy'],'changed_layers':['typography_copy'],'qa':_all_true_qa(),'production_contract_ack':True,'source_binding_hash':rjob['source_binding_hash'],'quality_observations':_quality_observations(rjob),'production_receipt':_portable_receipt(rjob)}),encoding='utf-8')
    assert cli_main(['revision-ingest','--project-dir',str(project),'--revision-id',rid])==0
    manifest=json.loads((project/'.cbcc/review/delivery_manifest.json').read_text()); ri=next(x for x in manifest['items'] if x['kind']=='LOCAL_REVISION_OUTPUT' and x['revision_id']==rid)
    st=ProjectState.load(project); accept=tmp_path/'accept.json'; accept.write_text(json.dumps({'project_id':st.data['project_id'],'revision':st.data['revision'],'accept_items':[ri['item_id']]}),encoding='utf-8')
    assert cli_main(['review-apply','--project-dir',str(project),'--review-file',str(accept)])==0
    learning_file=tmp_path/'learning.json'; learning_file.write_text(json.dumps({'cycle_id':'LC-CLI-1','revision_id':rid,'edit_layers':['CTA_COPY'],'freeze_layers':['PRODUCT_TRUTH','POSITIONING'],'baseline_metrics':{'click_to_checkout':0.10},'after_metrics':{'click_to_checkout':0.12},'metric_directions':{'click_to_checkout':'UP'}}),encoding='utf-8')
    assert cli_main(['learning-apply','--project-dir',str(project),'--learning-file',str(learning_file)])==0
    st=ProjectState.load(project)
    assert st.data['gates']['MEASUREMENT']['status']=='READY_REVIEW'
    assert st.data['gates']['LEARNING']['status']=='READY_REVIEW'
    assert (project/'artifacts/learning_latest.json').exists()
    assert 'LC-CLI-1' in (project/'artifacts/strategy/MASTER_STRATEGY_CN.md').read_text(encoding='utf-8')
    loop=json.loads((project/'artifacts/production_learning_loop.json').read_text()); assert loop['status']=='PRODUCTION_LEARNING_LOOP_MATERIALIZED'
    cmap=json.loads((project/'artifacts/capability_integration_map.json').read_text()); row=next(x for x in cmap['capabilities'] if x['capability']=='POST_PRODUCTION_LEARNING_LOOP'); assert row['runtime_wiring_status']=='INTEGRATED_ACTIVE'
