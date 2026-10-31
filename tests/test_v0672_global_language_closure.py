from pathlib import Path
import json

from cbcc.global_chinese_interpretation import _asset_visible_copy_companion_present, _audit_structured_copy
from cbcc.video_creator import build_video_creator_plan


def test_visible_copy_raw_chinese_meaning_counts_as_same_object_companion(tmp_path: Path):
    asset = tmp_path / 'asset_packages' / 'AST-1'
    asset.mkdir(parents=True)
    (asset / '14_visible_copy_block.json').write_text(json.dumps({
        'target_market_copy': 'KAWAL MINYAK. KEKALKAN HIDRASI.',
        'delivery_translation_zh': None,
        'raw': {
            'primary_locale': 'ms-MY',
            'target_copy': 'KAWAL MINYAK. KEKALKAN HIDRASI.',
            'english_baseline': 'BALANCE OIL. KEEP HYDRATION.',
            'chinese_meaning': '平衡油脂，同时保留补水护理。',
        },
    }, ensure_ascii=False), encoding='utf-8')
    assert _asset_visible_copy_companion_present(tmp_path, 'AST-1') is True


def test_video_plan_preserves_authored_chinese_hook_and_runtime_default_creator_cta_companion():
    assets = [{
        'asset_id': 'AST-S02',
        'family': 'CREATOR_AFFILIATE',
        'surface': 'CREATOR',
        'consumer_question': 'What should a creator naturally demonstrate while preserving product truth?',
        'consumer_question_cn': '达人应如何自然演示，同时守住产品真源边界？',
        'decision_intent': 'RELEVANCE',
        'incremental_information': 'show routine use without overclaiming',
    }]
    plan = build_video_creator_plan(
        'P1',
        [{'family': 'CREATOR_AFFILIATE', 'surface': 'CREATOR', 'curation_job': 'creator brief'}],
        [],
        {'primary_locale': 'ms-MY', 'visible_copy_locales': ['ms-MY']},
        assets=assets,
    )
    row = plan['assets'][0]
    assert row['hook_cn'] == '达人应如何自然演示，同时守住产品真源边界？'
    assert row['creator_contract']['cta'] == 'native recommendation / shop action after proof'
    assert row['creator_contract']['cta_cn']
    assert not _audit_structured_copy({'hook': row['hook'], 'hook_cn': row['hook_cn']}, 'VIDEO')
    assert not _audit_structured_copy(row['creator_contract'], 'VIDEO')


def test_video_plan_does_not_invent_chinese_hook_when_none_is_authored():
    assets = [{
        'asset_id': 'AST-V01', 'family': 'VIDEO', 'surface': 'PDP_VIDEO',
        'consumer_question': 'Can a short routine video explain use?',
    }]
    plan = build_video_creator_plan('P2', [{'family': 'VIDEO', 'surface': 'PDP_VIDEO', 'curation_job': 'video'}], [], {'primary_locale': 'ms-MY'}, assets=assets)
    row = plan['assets'][0]
    assert row.get('hook_cn') in (None, '')
