from __future__ import annotations

from copy import deepcopy
from typing import Any


def _cluster_key(asset:dict[str,Any])->str:
    explicit=asset.get('variant_cluster') or asset.get('asset_cluster') or asset.get('asset_role')
    if explicit:
        return str(explicit).upper()
    intent=str(asset.get('decision_intent') or '').upper()
    surface=str(asset.get('surface') or '').upper()
    family=str(asset.get('family') or '').upper()
    if intent=='IDENTIFY' and surface in {'GALLERY','SEARCH_RESULTS','LANDING_PAGE_HERO','PDP'}:
        return 'HERO'
    if intent in {'PROOF','PERFORMANCE_PROOF','INGREDIENT_COMPOSITION','MATERIAL_SENSORY'}:
        return 'BENEFIT_OR_PROOF'
    if intent in {'USAGE','CARE_MAINTENANCE'}:
        return 'HOW_TO'
    if surface=='PAID_AD' or family=='PAID':
        return 'PAID_AD'
    if surface in {'A_PLUS','LONGFORM'} or family=='RICH_CONTENT':
        return 'A_PLUS_PDP'
    if surface=='STORE_BANNER' or family=='STORE':
        return 'STORE'
    if surface in {'SOCIAL_CONTENT','CREATOR','SHORT_VIDEO','PDP_VIDEO','LIVE'}:
        return 'SOCIAL_VIDEO'
    return intent or surface or family or 'OTHER'


def _deployment_state(asset:dict[str,Any])->str:
    for key in ('deployment_state','activation_state','pool_state'):
        if asset.get(key):
            return str(asset.get(key)).upper()
    status=str(asset.get('status') or 'ACTIVATE').upper()
    return 'LIVE_CANDIDATE' if status=='ACTIVATE' else status


def compile_asset_universe(assets:list[dict[str,Any]], target:dict[str,Any]|None=None)->dict[str,Any]:
    target=target or {}
    clusters:dict[str,list[dict[str,Any]]]={}
    pools={'LIVE_CANDIDATE':[],'TEST_POOL':[],'ROTATION_POOL':[],'PAID_MEDIA':[],'PDP_CONTENT':[],'ARCHIVE':[],'OTHER':[]}
    for idx,raw in enumerate(assets or []):
        a=raw
        cluster=_cluster_key(a)
        a.setdefault('variant_cluster',cluster)
        a.setdefault('variant_id',str(a.get('asset_variant_id') or a.get('variant_id') or f'{cluster}-{idx+1:02d}'))
        a.setdefault('deployment_state',_deployment_state(a))
        a.setdefault('test_hypothesis',a.get('business_hypothesis'))
        clusters.setdefault(cluster,[]).append({
            'asset_id':a.get('asset_id'),'variant_id':a.get('variant_id'),'surface':a.get('surface'),
            'decision_intent':a.get('decision_intent'),'deployment_state':a.get('deployment_state'),
            'test_hypothesis':a.get('test_hypothesis')
        })
        state=str(a.get('deployment_state') or 'OTHER').upper()
        if state not in pools:
            if str(a.get('surface') or '').upper()=='PAID_AD': state='PAID_MEDIA'
            elif str(a.get('surface') or '').upper() in {'A_PLUS','LONGFORM','PDP'}: state='PDP_CONTENT'
            else: state='OTHER'
        pools[state].append(a.get('asset_id'))
    capacity=target.get('listing_image_capacity') or target.get('gallery_capacity') or target.get('platform_slot_capacity')
    return {
        'status':'DYNAMIC_ASSET_UNIVERSE',
        'fixed_total_asset_limit':False,
        'platform_capacity_is_activation_constraint_only':True,
        'platform_capacity':capacity,
        'total_asset_candidates':len(assets or []),
        'cluster_count':len(clusters),
        'clusters':clusters,
        'pools':pools,
        'principle':(
            'Asset universe size is determined by useful creative hypotheses, shopper decisions, surfaces and testing needs. '
            'Platform gallery capacity limits only the simultaneous live activation set; it never limits the total asset universe, Hero variants, benefit variants, paid ads, A+/PDP modules, detail visuals, banners, social/video or rotation/testing inventory.'
        ),
        'variant_rule':'Multiple assets may answer the same shopper question on the same surface when they carry distinct authored creative hypotheses or variant IDs. Do not merge them merely because role/surface/question match.',
    }


def wrap_build_asset_architecture(fn):
    def built(project_id:str,target:dict,questions:list[str],content_objects:list[dict[str,Any]],asset_jobs:list[dict[str,Any]]|None=None,decision_context:dict[str,Any]|None=None,category_family:str='GENERAL_COMMERCE'):
        # Explicit Agent-authored variants must survive. Historical architecture merged explicit jobs
        # sharing question+surface+family, which destroyed H01/H02/H03 and test variants.
        if asset_jobs:
            assets=[]; audits=[]; unrouted=[]
            for idx,job_raw in enumerate(asset_jobs):
                job=deepcopy(dict(job_raw or {}))
                variant_id=job.get('variant_id') or job.get('asset_variant_id') or job.get('creative_hypothesis_id') or f'VAR-{idx+1:02d}'
                job['variant_id']=variant_id
                one=fn(project_id,target,questions,content_objects,[job],decision_context,category_family)
                for a in one.get('assets') or []:
                    a['variant_id']=variant_id
                    a['variant_cluster']=job.get('variant_cluster') or job.get('asset_cluster') or job.get('asset_role') or _cluster_key(a)
                    a['deployment_state']=str(job.get('deployment_state') or job.get('activation_state') or ('TEST_POOL' if job.get('testing_variant') else 'LIVE_CANDIDATE')).upper()
                    a['test_hypothesis']=job.get('test_hypothesis') or job.get('creative_hypothesis') or a.get('business_hypothesis')
                    a['activation_set_id']=job.get('activation_set_id')
                    a['testing_variant']=bool(job.get('testing_variant') or a['deployment_state'] in {'TEST_POOL','ROTATION_POOL'})
                    assets.append(a)
                audits.extend(one.get('decision_question_audit') or [])
                unrouted.extend(one.get('unrouted_questions') or [])
            # Preserve every explicit variant. Asset IDs are generated from index inside each single-job call,
            # so make IDs unique when the same question/surface repeats.
            seen={}
            for idx,a in enumerate(assets):
                aid=str(a.get('asset_id') or '')
                if aid in seen:
                    a['asset_id']=aid+'-'+str(a.get('variant_id') or idx+1).replace(' ','-').upper()
                seen[a['asset_id']]=True
            universe=compile_asset_universe(assets,target)
            return {
                'status':'DYNAMIC_ASSET_ARCHITECTURE','fixed_count_authority':False,'asset_count':len(assets),'assets':assets,
                'decision_question_count':len({str(a.get('consumer_question') or '') for a in assets if a.get('consumer_question')}),
                'source_shopper_question_count':len([q for q in questions if str(q).strip()]),
                'atomic_decision_job_count':len(audits),'decision_intent_count':len({a.get('decision_intent') for a in assets if a.get('decision_intent')}),
                'decision_question_audit':audits,
                'decision_coverage_summary':{
                    'status':'COVERAGE_COMPILED','source_shopper_questions':len([q for q in questions if str(q).strip()]),
                    'atomic_decision_jobs':len(audits),'covered_atomic_jobs':len(audits),'uncovered_atomic_jobs':0,
                    'merged_atomic_jobs':0,
                    'principle':'Explicit Agent-authored variants are never merged solely because question/surface/family match.'
                },
                'asset_scope_active':True,'unrouted_questions':unrouted,'relationship_mode':'EXPLICIT_ONLY',
                'explicit_handoff_count':sum(1 for a in assets if a.get('handoff')),'auto_sequence_authority':False,
                'category_family':category_family,
                'curation_basis':['Consumer Decision Question','Decision Intent','Decision Topic','Strategic Job','Surface Need','Incremental Information','Business Hypothesis','Creative Hypothesis','Variant Cluster','Testing/Deployment State'],
                'asset_universe':universe,
            }
        out=fn(project_id,target,questions,content_objects,asset_jobs,decision_context,category_family)
        out=deepcopy(out)
        out['asset_universe']=compile_asset_universe(out.get('assets') or [],target)
        return out
    return built
