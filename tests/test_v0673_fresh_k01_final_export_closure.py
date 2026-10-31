from __future__ import annotations

from pathlib import Path
import json

from cbcc.commercial_continuity_authority import _commercial_prompt_lines
from cbcc.full_delivery_depth_v3 import _card_issues
from cbcc.long_requirement_full_audit import wrap_audit_host_full_package
from cbcc.listing_markdown_parity_v0671 import audit_listing_markdown_canonical_parity


def _current_card():
    return {
        'commerce_task': {'strategic_job': 'Resolve the shopper decision', 'success_metric': 'PDP CVR'},
        'visual_carrier': 'EDITORIAL_EVIDENCE',
        'product_presence': {'planning_state': 'REQUIRED', 'presence_why': 'Identity is needed here.'},
        'subject_system': {'subject': 'KIYUU gel'},
        'subject_action_environment_props': {'environment': 'warm ivory studio', 'props': ['verified carton']},
        'information_design': {'proof_plane': 'formula structure'},
        'composition_camera': {'composition_grammar': 'asymmetric editorial split'},
        'lighting_material_cmf': {'cmf': {'material': 'warm ivory matte'}},
        'agent_art_direction': {'portfolio_rhythm_delta': 'hero → evidence'},
    }


def test_en_commerce_context_does_not_emit_cjk_or_machine_translate():
    lineage = {
        'positioning': {'primary_conversion_proposition': 'Lightweight oil-balancing hydration'},
        'audience_culture': {
            'segments': [
                {'name': 'Oily-skin shoppers', 'why': 'Need lightweight hydration'},
                {'name': '马来西亚油皮消费者', 'why': '需要轻盈补水'},
            ],
            'visual_implications': ['natural skin texture', '避免刻板族裔符号'],
        },
        'race': [
            {'stage': 'COMMUNICATION', 'objective': 'Explain routine use'},
            {'stage': '传播', 'objective': '按平台原生方式传播'},
        ],
    }
    text = '\n'.join(_commercial_prompt_lines(lineage, 'EN'))
    assert 'Lightweight oil-balancing hydration' in text
    assert 'Oily-skin shoppers' in text
    assert 'Explain routine use' in text
    assert not any('\u3400' <= ch <= '\u9fff' for ch in text)


def test_current_nested_design_card_satisfies_semantic_decision_audit():
    assert _card_issues(_current_card(), 'AST-1') == []


def test_planning_only_mature_package_does_not_require_provider_media(tmp_path: Path):
    package = tmp_path
    root = package / 'asset_packages' / 'AST-1'
    root.mkdir(parents=True)
    (root / '05_prompt_CN.txt').write_text('prompt', encoding='utf-8')
    (root / '06_prompt_EN.txt').write_text('prompt', encoding='utf-8')
    (root / '12_design_card.json').write_text(json.dumps(_current_card(), ensure_ascii=False), encoding='utf-8')
    (package / 'ASSET_UNIVERSE.json').write_text(json.dumps({
        'assets': [{'asset_id': 'AST-1', 'deployment_state': 'ACTIVE'}],
        'product_presence_portfolio_audit': {'total_assets': 1, 'structured_presence_decisions': 1},
        'opportunity_family_audit': [],
    }), encoding='utf-8')
    (package / 'supporting_analysis').mkdir()
    (package / 'supporting_analysis' / 'evidence.json').write_text(json.dumps({
        'provider_media_status': 'E2E_PENDING',
        'why': 'Structural Prompt/package QA is not actual media/pixel QA.'
    }), encoding='utf-8')
    base = lambda _p: {'status': 'PASS', 'issues': []}
    result = wrap_audit_host_full_package(base)(package)
    codes = {x.get('code') for x in result.get('issues', [])}
    assert 'FULL_PROVIDER_RESULT_MISSING' not in codes
    assert 'FULL_ACTUAL_GENERATED_OUTPUT_MISSING' not in codes


def test_routed_business_workspace_is_not_fixed_taxonomy_by_route_names_alone(tmp_path: Path):
    package = tmp_path
    (package / 'index.html').write_text('''<!doctype html><main data-workspace-shell="cbcc-commercial-v1">
      <section data-route="product"></section><section data-route="market"></section>
      <section data-route="strategy"></section><section data-route="listing"></section>
      <section data-route="visual"></section><section data-route="assets"></section>
      <section data-route="sources"></section><div>asset/G01</div></main>''', encoding='utf-8')
    base = lambda _p: {'status': 'PASS', 'issues': []}
    result = wrap_audit_host_full_package(base)(package)
    assert not any(x.get('code') == 'FIXED_CAPABILITY_ROUTE_TAXONOMY' for x in result.get('issues', []))


def test_listing_parity_treats_markdown_escaped_pipe_as_same_text(tmp_path: Path):
    center = {
        'task_scope': {'listing_active': True},
        'copy_center': [{'field': 'title', 'value': 'KIYUU Gel 30g | Niacinamide + Salicylic Acid', 'delivery_translation': 'KIYUU 凝胶 30g｜烟酰胺+水杨酸'}],
        'localized_copy': [],
    }
    (tmp_path / 'HUMAN_DELIVERY.json').write_text(json.dumps(center, ensure_ascii=False), encoding='utf-8')
    (tmp_path / '01_LISTING_UPLOAD_READY.md').write_text('KIYUU Gel 30g \\| Niacinamide + Salicylic Acid\nKIYUU 凝胶 30g｜烟酰胺+水杨酸', encoding='utf-8')
    assert audit_listing_markdown_canonical_parity(tmp_path) == []
