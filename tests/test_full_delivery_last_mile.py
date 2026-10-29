from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

from cbcc.compiler import build_project
from cbcc.delivery_export import export_delivery_package

ROOT=Path(__file__).resolve().parents[1]


def _pack(tmp_path:Path)->Path:
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
        'project_id':'FULL-LAST-MILE',
        'planning_only':True,
        'full_strategy':True,
        'product':{
            'name':'深度合同测试商品','category':'美妆','net_content':'30ml',
            'primary_conversion_proposition':'以证据边界约束的日常产品价值',
            'formula':{'niacinamide':'1%'},
        },
        'claims':[
            {'claim_id':'C1','claim':'含 1% 烟酰胺','evidence_grade':'B','status':'APPROVED','publication_status':'BOUNDED_SUPPORTED_CLAIM'},
            {'claim_id':'C2','claim':'轻盈肤感','evidence_grade':'C','status':'PENDING'},
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


def test_full_export_revalidates_depth_and_materializes_visible_audits(tmp_path:Path):
    project=tmp_path/'project'
    build_project(project,_request(),_pack(tmp_path))
    out=tmp_path/'delivery'
    manifest=export_delivery_package(project,out)

    depth=json.loads((out/'FULL_DELIVERY_DEPTH_AUDIT.json').read_text(encoding='utf-8'))
    prompt=json.loads((out/'PROMPT_CONSUMPTION_AUDIT.json').read_text(encoding='utf-8'))
    language=json.loads((out/'HUMAN_LANGUAGE_AUDIT.json').read_text(encoding='utf-8'))
    html=(out/'index.html').read_text(encoding='utf-8')

    assert depth['mode']=='FULL'
    assert depth['status']=='PASS', depth
    assert depth['depth_contract']=='FULL_DECISION_DEPTH_V2_CARRIER_AWARE_NO_SILENT_COMPRESSION'
    # Prompt/generation readiness remains visible for production work, but it is not a FULL-project gate.
    assert prompt['status']=='READY', prompt
    assert prompt['project_completion_blocking'] is False
    assert language['status']=='PASS', language
    for token in [
        '信息完整度、待确认清单、假设与决策日志',
        '产品真实事实审计与卖点分级表',
        '平台 × 区域 × 人群 × 族裔文化洞察',
        '营销框架与核心策略',
        '视觉总策略与拍摄执行清单',
        '分平台内容矩阵表',
        'RACE传播框架执行表',
        '族裔文化适配检查表',
        '合规、文化敏感与风险清单；评估指标与A/B测试建议；P0/P1/P2执行优先级与下一步需补充信息',
    ]:
        assert token in html, token
    assert manifest['workspace_contract']['full_decision_depth']=='PASS'
    assert manifest['workspace_contract']['full_visible_objects']=='PASS'
    assert manifest['workspace_contract']['foreign_human_copy_has_chinese_companion'] is True
    # This fixture explicitly disables asset compilation; absence of assets is scope, not incompleteness.
    assert manifest['workspace_contract']['prompt_generation_readiness']=='NO_ASSETS'
    assert manifest['workspace_contract']['prompt_generation_readiness_blocks_project_completion'] is False
    assert manifest['full_delivery_depth_audit']=='FULL_DELIVERY_DEPTH_AUDIT.json'
    assert manifest['prompt_consumption_audit']=='PROMPT_CONSUMPTION_AUDIT.json'
    assert manifest['human_language_audit']=='HUMAN_LANGUAGE_AUDIT.json'


def test_plugin_wrapper_requires_full_depth_and_nonblocking_prompt_audit(tmp_path:Path):
    # The repair script is idempotent; CI applies it before this test, but running it here makes
    # the contract independently reproducible in local acceptance.
    subprocess.run([sys.executable,str(ROOT/'scripts/repair_plugin_full_depth_contract.py')],cwd=ROOT,check=True)
    source=(ROOT/'scripts/build_plugin_dist.py').read_text(encoding='utf-8')
    for token in [
        'FULL 项目深度合同（宿主不可改写成简版报告）',
        'Prompt Consumption Audit',
        '九域决策深度合同',
        'FULL 与 TASK_SCOPED 分权',
        'host_custom_short_report_cannot_substitute_full_delivery',
        'prompt_consumption_blocks_project_completion',
        'product_source_default_reference_guided',
    ]:
        assert token in source, token

    dist=tmp_path/'dist'
    subprocess.run([sys.executable,str(ROOT/'scripts/build_plugin_dist.py'),'--output-dir',str(dist)],cwd=ROOT,check=True)
    release=json.loads((dist/'release_manifest.json').read_text(encoding='utf-8'))
    dc=release['delivery_contract']
    assert dc['full_nine_domain_decision_depth_required'] is True
    assert dc['prompt_consumption_audit_required'] is True
    assert dc['prompt_consumption_blocks_project_completion'] is False
    assert dc['product_source_default_reference_guided'] is True
    assert dc['photorealism_default_required'] is False
    assert dc['seven_agent_capability_continuity_required'] is True
    assert dc['host_custom_short_report_cannot_substitute_full_delivery'] is True
