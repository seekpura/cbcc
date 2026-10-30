from __future__ import annotations

import json
from pathlib import Path

from scripts.check_v0648_user_hard_rule_final_zip import audit_package, HTML_TOKENS


def _write(root: Path, rel: str, value) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        p.write_text(value, encoding='utf-8')
    else:
        p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def _valid_package(root: Path) -> Path:
    _write(root, 'supporting_analysis/INFORMATION_COMPLETENESS_ASSUMPTION_DECISION.json', {
        'information_completeness': [{'domain': 'product', 'status': 'EVIDENCED'}],
        'pending_questions': [{'question': 'q1'}],
        'assumptions': [{'assumption': 'a1'}],
        'decision_log': [{'decision': 'd1'}],
    })
    _write(root, 'supporting_analysis/PRODUCT_FACT_AUDIT.json', {
        'evidence_scale': {'A': 'test/certification', 'B': 'supply/formula', 'C': 'subjective/pending'},
        'rows': [
            {'item': 'fact', 'category': '真实卖点', 'evidence_grade': 'B', 'source': 'source', 'publish_rule': 'fact only', 'hard_claim_allowed': True},
            {'item': 'benefit', 'category': '可感知利益', 'evidence_grade': 'B', 'source': 'source', 'publish_rule': 'bounded', 'hard_claim_allowed': True},
            {'item': 'emotion', 'category': '情绪价值', 'evidence_grade': 'C', 'source': 'strategy', 'publish_rule': 'soft only', 'hard_claim_allowed': False},
            {'item': 'forbidden', 'category': '不可宣称项', 'evidence_grade': 'C', 'source': 'missing', 'publish_rule': 'no', 'hard_claim_allowed': False},
        ],
    })
    _write(root, 'supporting_analysis/PLATFORM_REGION_AUDIENCE_CULTURE.json', {
        'why_dimensions': [
            {'dimension': '平台', 'why': 'why'}, {'dimension': '区域', 'why': 'why'},
            {'dimension': '人群', 'why': 'why'}, {'dimension': '族裔文化背景', 'why': 'why'},
        ],
        'intersectionality': [{'intersection': '族裔 × 性别 × 年龄 × 收入 × 地域'}],
        'localization_operating_table': [
            {'dimension': '语言与回译'}, {'dimension': '节日日历'}, {'dimension': '支付'},
            {'dimension': '物流'}, {'dimension': '宗教禁忌'}, {'dimension': '当地法规'},
        ],
    })
    _write(root, 'supporting_analysis/MARKETING_FRAMEWORK_CORE_STRATEGY.json', {
        'framework_relationships': [
            {'framework': 'RACE'}, {'framework': 'STP + JTBD'}, {'framework': 'AIDA / FABE'}, {'framework': '4P + Funnel'},
        ],
        'strategy_rows': [{
            'decision': 'd', 'basis': 'b', 'tradeoff': 't', 'why_platform_region_audience_culture': 'why',
            'execution': 'e', 'metric': 'm',
        }],
        'resource_tradeoff': [
            {'priority': 'P0', 'keep': 'a', 'cut_first': 'x', 'why': 'w'},
            {'priority': 'P1', 'keep': 'b', 'cut_first': 'y', 'why': 'w'},
            {'priority': 'P2', 'keep': 'c', 'cut_first': 'z', 'why': 'w'},
        ],
    })
    _write(root, 'supporting_analysis/VISUAL_EXECUTION_LOCK.json', {
        'style_keywords': ['editorial'], 'moodboard_direction': ['direction'], 'composition_rules': ['rule'],
        'palette': [{'hex': '#000000', 'contrast_ratio': 21}],
        'lighting_master': {'human': '深肤色 +0.3~+0.7 EV Prelight; neutral bounce/反光板; large 柔光 diffusion'},
        'camera_framework': [{'lens': '85mm', 'shot': 'medium', 'camera': 'eye-level'}],
        'scene_props_wardrobe': {'models': '人物 Creator 模特 手部'},
        'inclusive_photography_p0': [
            {'dimension': '深肤色'}, {'dimension': '发质'}, {'dimension': '体型'},
            {'dimension': '残障'}, {'dimension': '年龄'}, {'dimension': 'AI偏见'},
        ],
        'platform_sizes': [{'surface': 'gallery', 'production_spec': '1600x1600'}],
        'shot_list': ['shot 1'],
    })
    _write(root, 'supporting_analysis/PLATFORM_CONTENT_MATRIX.json', {'rows': [{
        'platform': 'p', 'audience': 'a', 'topic': 't', 'hook': 'h', 'script_structure': 's',
        'visual_form': 'v', 'cta': 'c', 'metric': 'm', 'race_stage': 'Communication',
        'culture_taboo_check': 'checked', 'size_duration': 'spec', 'cover': 'cover', 'subtitle': 'subtitle',
        'music_rights': 'licensed', 'traffic_mechanism': 'TO_VERIFY', 'landing': 'PDP', 'utm_attribution': 'creative id',
    }]})
    _write(root, 'supporting_analysis/RACE_FRAMEWORK.json', {'rows': [{
        'stage': stage, 'objective': 'o', 'key_actions': 'a', 'outputs': 'out', 'platform': 'p',
        'culture_validation': 'c', 'metrics': 'm', 'why': 'w',
    } for stage in ('Research', 'Action', 'Communication', 'Evaluation')]})
    _write(root, 'supporting_analysis/CULTURAL_ADAPTATION.json', {'rows': [{
        'check': '族裔/语言', 'adaptation': 'a', 'inclusive_representation': 'i', 'stereotype_taboo': 's',
        'result': 'PASS_WITH_GUARD', 'modification': 'm', 'basis': 'ASSUMPTION',
    }]})
    _write(root, 'supporting_analysis/COMPLIANCE_RISK_EVALUATION_PRIORITY.json', {
        'risk_list': [{'priority': 'P0', 'risk': 'r'}],
        'ab_tests': [{'test': 'a/b'}],
        'self_check': [{'check': f'c{i}', 'result': 'PASS'} for i in range(6)],
        'next_inputs': ['external input'],
    })
    _write(root, 'supporting_analysis/CLAIM_EVIDENCE_MATRIX.json', {
        'rows': [{'claim': '功效 成分 认证 价格 销量', 'publish': 'bounded'}],
    })
    _write(root, 'index.html', '<html><body>' + ''.join(f'<section>{x}</section>' for x in HTML_TOKENS) + '</body></html>')
    return root


def test_valid_final_package_passes(tmp_path: Path):
    report = audit_package(_valid_package(tmp_path))
    assert report['status'] == 'PASS', report['issues']
    assert report['issues'] == []
    assert report['project_completion_blocking'] is True


def test_c_grade_hard_claim_fails(tmp_path: Path):
    root = _valid_package(tmp_path)
    p = root / 'supporting_analysis/PRODUCT_FACT_AUDIT.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    data['rows'][2]['hard_claim_allowed'] = True
    _write(root, 'supporting_analysis/PRODUCT_FACT_AUDIT.json', data)
    report = audit_package(root)
    assert report['status'] == 'FAIL'
    assert any(x.startswith('C_GRADE_HARD_CLAIM') for x in report['issues'])


def test_race_ethnicity_not_relevant_cannot_bypass_full_culture_validation(tmp_path: Path):
    root = _valid_package(tmp_path)
    _write(root, 'supporting_analysis/MARKET_AUDIENCE.json', {'status_dimensions': {'race_ethnicity': 'NOT_RELEVANT'}})
    report = audit_package(root)
    assert report['status'] == 'FAIL'
    assert 'RACE_ETHNICITY_WRONGLY_NOT_RELEVANT' in report['issues']


def test_missing_race_object_fails_even_if_old_audit_says_pass(tmp_path: Path):
    root = _valid_package(tmp_path)
    (root / 'supporting_analysis/RACE_FRAMEWORK.json').unlink()
    _write(root, 'FULL_MATERIALIZATION_AUDIT.json', {'status': 'PASS'})
    report = audit_package(root)
    assert report['status'] == 'FAIL'
    assert any('RACE_FRAMEWORK.json' in x for x in report['issues'])


def test_short_index_cannot_replace_nine_domains(tmp_path: Path):
    root = _valid_package(tmp_path)
    _write(root, 'index.html', '<html><body><h1>Project Ready</h1></body></html>')
    report = audit_package(root)
    assert report['status'] == 'FAIL'
    assert any(x.startswith('INDEX_MISSING_DOMAIN:') for x in report['issues'])
