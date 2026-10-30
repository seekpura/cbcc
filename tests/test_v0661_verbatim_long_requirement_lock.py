from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_verbatim_long_requirement_source_preserves_concrete_execution_anchors():
    path = ROOT / 'references' / 'USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md'
    text = path.read_text(encoding='utf-8')
    anchors = [
        '真实卖点/可感知利益/情绪价值/不可宣称项',
        'A=检测报告/官方认证/可复现实测',
        'C级不得作硬宣称',
        '为什么这个平台、这个区域、这个人群、这个族裔文化背景下要这样做',
        '族裔×性别×年龄×收入×地域',
        '深肤色曝光',
        '音乐版权',
        'UTM与归因',
        '语言回译',
        '宗教禁忌',
        'P0=不做会翻车，P1=影响效果，P2=加分项',
        '最多列10问',
        'RACE传播框架执行表',
        '族裔文化适配检查表',
        'RACE阶段',
        '族裔文化适配/禁忌校验',
        '假设与决策日志',
        '主/辅/背景/文字色HEX及对比度',
        '反光板/柔光方案',
        '不确定标“待查证”',
    ]
    missing = [anchor for anchor in anchors if anchor not in text]
    assert missing == []


def test_long_requirement_extension_has_release_ids_051_to_060():
    text = (ROOT / 'references' / 'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md').read_text(encoding='utf-8')
    for n in range(51, 61):
        assert f'REQ-{n:03d}' in text


def test_source_requirement_lock_requires_verbatim_source_and_extension():
    text = (ROOT / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').read_text(encoding='utf-8')
    assert 'USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md' in text
    assert 'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md' in text
    assert 'max-10-question continuation behavior' in text
    assert 'RACE/culture tables' in text
    assert 'nine semantic FULL output objects' in text


def test_canonical_loading_map_consumes_verbatim_source_not_only_summary():
    text = (ROOT / 'prompts' / 'canonical_authority_loading_map.md').read_text(encoding='utf-8')
    assert 'v0.6.61' in text
    assert 'USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md' in text
    assert 'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md' in text
    assert '最多 10 问' in text or 'no more than 10 questions' in text
    assert 'RACE阶段' in text
    assert '族裔文化适配/禁忌校验' in text
    assert 'nine required semantic FULL output objects' in text
