from __future__ import annotations

from cbcc import strategy_depth
from cbcc.tools import listing


def test_visual_master_projects_authored_per_asset_scene_and_props_without_invention():
    request = {
        'agent_plan': {
            'creative_exploration': {
                'asset_art_directions': [
                    {'asset_name': 'G01', 'environment': 'warm ivory editorial field', 'props': []},
                    {'asset_name': 'G08', 'environment': 'ordinary vanity / bathroom context', 'props': ['neutral towel edge']},
                    {'asset_name': 'G03', 'environment': 'warm ivory editorial field', 'props': ['thin rules / type grid']},
                ]
            }
        }
    }
    out = strategy_depth.build_visual_depth(request, {}, {}, {}, [], None)
    scene = out.get('scene') or {}
    props = out.get('props') or {}
    assert scene
    assert 'warm ivory editorial field' in str(scene)
    assert 'ordinary vanity / bathroom context' in str(scene)
    assert props
    assert 'neutral towel edge' in str(props)
    assert 'thin rules / type grid' in str(props)


def test_explicit_project_visual_scene_and_props_still_override_asset_aggregation():
    request = {
        'visual_strategy': {'scene': {'master': 'explicit scene'}, 'props': ['explicit prop']},
        'agent_plan': {
            'creative_exploration': {
                'asset_art_directions': [
                    {'asset_name': 'G01', 'environment': 'asset scene', 'props': ['asset prop']},
                ]
            }
        },
    }
    out = strategy_depth.build_visual_depth(request, {}, {}, {}, [], None)
    assert out.get('scene') == {'master': 'explicit scene'}
    assert out.get('props') == ['explicit prop']


def test_authored_delivery_locale_copy_becomes_same_field_human_companion():
    fields = {'title': 'BM TITLE', 'description': 'BM DESC'}
    contract = {
        'primary_locale': 'ms-MY',
        'visible_copy_locales': ['ms-MY', 'en-MY'],
        'delivery_locale': 'zh-CN',
    }
    localized = {
        'ms-MY': {'title': 'BM TITLE', 'description': 'BM DESC'},
        'en-MY': {'title': 'EN TITLE', 'description': 'EN DESC'},
        'zh-CN': {'title': '中文标题', 'description': '中文描述'},
    }
    out = listing.final_copy_release_workflow(fields, contract, localized, [], {'issues': []})
    expected = {'title': '中文标题', 'description': '中文描述'}
    for package in out['packages']:
        for row in package['fields']:
            assert row['delivery_translation'] == expected[row['field']]
            assert row['delivery_companion_status'] == 'READY_AUTHORED_DELIVERY_LOCALE_COPY'


def test_missing_delivery_locale_copy_stays_unresolved():
    fields = {'title': 'BM TITLE'}
    contract = {
        'primary_locale': 'ms-MY',
        'visible_copy_locales': ['ms-MY', 'en-MY'],
        'delivery_locale': 'zh-CN',
    }
    localized = {'ms-MY': {'title': 'BM TITLE'}, 'en-MY': {'title': 'EN TITLE'}}
    out = listing.final_copy_release_workflow(fields, contract, localized, [], {'issues': []})
    assert all(row.get('delivery_translation') in (None, '') for p in out['packages'] for row in p['fields'])
    assert all(row.get('delivery_companion_status') == 'TO_AUTHOR' for p in out['packages'] for row in p['fields'])
