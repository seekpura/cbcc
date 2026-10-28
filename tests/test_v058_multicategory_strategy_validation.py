from pathlib import Path
import json,sys,copy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.compiler import build_project

FULL_ASSET_FILES={
'00_asset_manifest.yaml','01_strategy.md','02_visual_spec.md','03_photography_contract.json','04_layout_contract.json','05_prompt_CN.txt','06_prompt_EN.txt','07_generation_guidance.txt','08_copy.md','09_production_notes.md','10_source_trace.md','11_strategy_authority_trace.json'}


def _build(tmp_path,name):
    fx=ROOT/'tests/fixtures/v058_multicategory'/name
    req=json.loads(fx.read_text(encoding='utf-8'))
    p=tmp_path/fx.stem
    build_project(p,req,ROOT/'platform_packs')
    return p,req


def test_v058_multicategory_runtime_is_category_specific_and_asset_count_is_question_driven(tmp_path):
    results={}
    for name in ['beauty_kiyuu.json','fashion_uniqlo_bag.json','home_ikea365_container.json']:
        p,req=_build(tmp_path,name)
        strategy=json.loads((p/'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
        arch=json.loads((p/'artifacts/asset_architecture.json').read_text(encoding='utf-8'))
        assert len(strategy['sections'])==9
        visual=strategy['sections']['05_visual_photography_strategy']
        cat=visual['category_execution_profile']['category_family']
        assert cat==arch['category_family']
        assert visual['category_photography_plan']['status']=='STRATEGY_RECOMMENDATION_REQUIRES_PRELIGHT'
        assert visual['camera']['status']=='STRATEGY_RECOMMENDATION_REQUIRES_PRELIGHT'
        assert arch['asset_count'] not in {9,12}  # no fixed commerce-template count
        idx=json.loads((p/'artifacts/asset_packages/ASSET_PACKAGE_INDEX.json').read_text(encoding='utf-8'))
        assert idx['count']==arch['asset_count']
        for row in idx['assets']:
            d=p/'artifacts/asset_packages'/row['asset_id']
            assert FULL_ASSET_FILES.issubset({x.name for x in d.iterdir()})
            asset=next(a for a in arch['assets'] if a['asset_id']==row['asset_id'])
            photo=json.loads((d/'03_photography_contract.json').read_text(encoding='utf-8'))
            if asset['asset_type']=='IMAGE':
                assert photo['status']=='STRATEGY_DERIVED_PHOTOGRAPHY_PLAN'
                assert photo['asset_reasoning']['camera_choice']['status']=='STRATEGY_RECOMMENDATION_REQUIRES_PRELIGHT'
                assert photo['asset_reasoning']['decision_intent']==asset['decision_intent']
        jobs=json.loads((p/'artifacts/provider_jobs/PROVIDER_JOB_INDEX.json').read_text(encoding='utf-8'))
        production=json.loads((p/'artifacts/production_run.json').read_text(encoding='utf-8'))
        assert jobs['job_count'] + len(production.get('preflight_holds') or []) == arch['asset_count']
        assert all('REAL_PRODUCT_MASTER_NOT_BOUND' in x.get('errors',[]) for x in production.get('preflight_holds') or [])
        assert all(x.get('status') in {'READY_TO_HANDOFF','HOLD_REAL_PRODUCT_PREFLIGHT'} for x in production.get('assets') or [])
        ctx=json.loads((p/'artifacts/strategy_reasoning_context.json').read_text(encoding='utf-8'))
        assert 'PROMPT-MULTICATEGORY-SPECIFICITY' in {x['id'] for x in ctx['selected_prompts']}
        assert 'KNOW-MULTICATEGORY-SPECIFICITY' in {x.get('id') for x in ctx['selected_knowledge'] if x.get('id')}
        assert {'CategoryDecisionProfile','DecisionIntent','CategoryPhotographyPlan'}.issubset(set(ctx['ontology']['entities']))
        results[cat]={'style':visual['style'],'assets':arch['assets'],'material':visual['material_lighting_profile']}

    assert set(results)=={'BEAUTY_PERSONAL_CARE','FASHION_ACCESSORY','HOME_DURABLE'}
    assert len({x['style'] for x in results.values()})==3

    beauty=results['BEAUTY_PERSONAL_CARE']['assets']
    assert {(a['decision_intent'],a['surface']) for a in beauty} >= {('IDENTIFY','GALLERY'),('RELEVANCE','CREATOR'),('PROOF','GALLERY'),('USAGE','PDP_VIDEO')}

    fashion=results['FASHION_ACCESSORY']['assets']
    assert {(a['decision_intent'],a['surface']) for a in fashion} >= {('IDENTIFY','GALLERY'),('FIT_WEAR','CREATOR'),('WEATHER_BOUNDARY','GALLERY'),('CARE_MAINTENANCE','FAQ')}
    fit=next(a for a in fashion if a['decision_intent']=='FIT_WEAR')
    assert len(fit.get('merged_consumer_questions') or [])==2  # two wear/adjustment questions become one asset job
    textile=results['FASHION_ACCESSORY']['material']
    assert any('weave' in x.lower() for x in textile['optical_risks']+textile['lighting_geometry_logic'])

    home=results['HOME_DURABLE']['assets']
    assert {(a['decision_intent'],a['surface']) for a in home} >= {('PACKAGE_CONTENTS','GALLERY'),('SIZE_CAPACITY','GALLERY'),('SEAL_LEAK','PDP_VIDEO'),('STORAGE_STACKING','PDP_VIDEO'),('MATERIAL_SENSORY','GALLERY')}
    size=next(a for a in home if a['decision_intent']=='SIZE_CAPACITY')
    assert len(size.get('merged_consumer_questions') or [])==2  # repeated capacity question is merged
    assert any('transparent' in x.lower() or 'refraction' in x.lower() for x in results['HOME_DURABLE']['material']['optical_risks'])


def test_v058_platform_pack_does_not_censor_unverified_strategy_surfaces(tmp_path):
    # TikTok Shop US exact pack intentionally has limited verified capabilities/surfaces.
    # Strategy planning must retain requested GALLERY/PDP_VIDEO objects while marking them research-required.
    req=json.loads((ROOT/'tests/fixtures/v058_multicategory/fashion_uniqlo_bag.json').read_text(encoding='utf-8'))
    req=copy.deepcopy(req)
    req['project_id']='V058-US-CAPABILITY-SEPARATION'
    req['target'].update({'market':'United States','jurisdiction':'US','site':'US','primary_locale':'en-US','support_locales':[],'visible_copy_locales':['en-US']})
    p=tmp_path/'us'
    build_project(p,req,ROOT/'platform_packs')
    pc=json.loads((p/'artifacts/platform_compile.json').read_text(encoding='utf-8'))
    assert pc['resolution']=='EXACT'
    assert 'GALLERY' in pc['unsupported_surfaces'] and 'PDP_VIDEO' in pc['unsupported_surfaces']
    cg=json.loads((p/'artifacts/content_graph.json').read_text(encoding='utf-8'))
    by_family={x['family']:x for x in cg['objects']}
    assert 'VISUAL' in by_family and 'VIDEO' in by_family
    assert by_family['VISUAL']['payload']['platform_capability_status']=='STRATEGY_PLANNING_RESEARCH_REQUIRED'
    arch=json.loads((p/'artifacts/asset_architecture.json').read_text(encoding='utf-8'))
    assert any(a['surface']=='GALLERY' for a in arch['assets'])
    assert json.loads((p/'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))['platform_compile_status'] in {'RESEARCH_REQUIRED','PLANNING_ONLY_RESEARCH_PENDING'}
