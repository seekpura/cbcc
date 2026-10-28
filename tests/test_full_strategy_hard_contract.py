from pathlib import Path
import json

from cbcc.compiler import build_project
from cbcc.delivery_contract import REQUIRED_SECTIONS, RACE_STAGES


def _pack(tmp_path):
    pack=tmp_path/'packs'; pack.mkdir(exist_ok=True)
    (pack/'test.yaml').write_text(
        'pack_id: test\nplatform_family: test_platform\nsite: "*"\nstatus: TEST_FIXTURE_VERIFIED\nsynthetic_for_test: true\n'
        'capabilities: [LISTING, SEARCH, VISUAL, VIDEO, PAID, MEASUREMENT, COMPLIANCE]\n'
        'surfaces: [PDP, GALLERY, PDP_VIDEO, PAID_AD]\nrule_atoms: []\nresearch_required_for: []\n',
        encoding='utf-8'
    )
    return pack


def _request():
    return {
        'project_id':'FULL-HARD-CONTRACT',
        'planning_only':True,
        'full_strategy':True,
        'product':{
            'name':'Contract Product','category':'beauty','net_content':'30ml',
            'primary_conversion_proposition':'Evidence-bounded daily product value',
            'formula':{'niacinamide':'1%'},
        },
        'claims':[
            {'claim_id':'C1','claim':'Contains 1% niacinamide','evidence_grade':'B','status':'APPROVED','publication_status':'BOUNDED_SUPPORTED_CLAIM'},
            {'claim_id':'C2','claim':'Feels lightweight','evidence_grade':'C','status':'PENDING'},
        ],
        'sources':[{'source_id':'SRC-PRODUCT','kind':'PRODUCT_TRUTH','source_type':'SUPPLIER_SPECIFICATION'}],
        'target':{
            'market':'MY','jurisdiction':'MY','platform_family':'test_platform','site':'TEST',
            'primary_locale':'ms-MY','visible_copy_locales':['ms-MY'],'delivery_locale':'zh-CN','surfaces':['PDP','GALLERY']
        },
        'audience_culture':{
            'race_ethnicity':[{'group':'多元马来西亚城市消费者','audience':'城市生活方式消费者'}],
            'intersectionality':{'gender':'mixed','age':'18-34','income':'mid','geography':'urban'},
            'copy_implications':['目标市场文案需本地自然表达并回译'],
            'visual_implications':['避免单一族裔标签化'],
            'casting_constraints':['人物出现时保持多样、真实、非刻板化'],
        },
        'content_families':['LISTING','VISUAL'],
        'shopper_questions':['它是什么？','为什么与我有关？','凭什么相信？'],
        'compile_assets':False,
    }


def test_full_strategy_restores_original_hard_contract(tmp_path):
    project=tmp_path/'project'
    build_project(project,_request(),_pack(tmp_path))
    strategy=json.loads((project/'artifacts/strategy/strategy_authority.json').read_text(encoding='utf-8'))
    hp=strategy['human_projection']
    assert hp['mode']=='FULL'
    assert hp['active_sections']==REQUIRED_SECTIONS
    assert hp['fixed_human_section_quota'] is True

    selected=set(strategy.get('selected_strategy_frameworks') or [])
    assert {'RACE','STP','JTBD','AIDA','FABE','4P','Funnel'} <= selected

    race=strategy['sections']['07_race_execution_table']
    assert [x['stage'] for x in race]==RACE_STAGES

    value=strategy['sections']['02_product_truth_value_ladder']
    all_rows=(value.get('product_facts') or [])+(value.get('claim_value_ladder') or [])
    assert all(str(x.get('evidence_grade') or x.get('evidence_level') or '').upper() in {'A','B','C'} for x in all_rows)
    c_rows=[x for x in all_rows if str(x.get('evidence_grade') or x.get('evidence_level') or '').upper()=='C']
    assert c_rows and all(str(x.get('publication_status') or '').upper()!='ACTIVE' for x in c_rows)

    culture=strategy['sections']['03_platform_region_audience_culture_insight']
    assert culture.get('intersectionality_table')
    checklist=strategy['sections']['08_culture_adaptation_checklist']
    assert checklist

    matrix=strategy['sections']['06_platform_content_matrix']
    assert matrix
    assert all(row.get('race_stage') for row in matrix)
    assert all(row.get('culture_adaptation') not in (None,'') for row in matrix)
    assert all(row.get('taboo_stereotype_check') not in (None,'') for row in matrix)

    last=strategy['sections']['09_risk_measurement_priority_next_steps']
    assert last['priority_plan']['P0']
    assert last['priority_plan']['P1']
    assert last['priority_plan']['P2']
    assert last.get('output_self_check')
    assert last.get('ab_test_hypotheses')

    contract=strategy.get('delivery_contract') or {}
    assert contract.get('status')=='PASS', contract

    md=(project/'artifacts/strategy/MASTER_STRATEGY_CN.md').read_text(encoding='utf-8')
    assert '人类策略投影：FULL' in md
    assert 'RACE=Research → Action → Communication → Evaluation' in md
    assert 'RACE传播框架执行表' in md
    assert '族裔文化适配检查表' in md
    assert '输出前自检' in md
