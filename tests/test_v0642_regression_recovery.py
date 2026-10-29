from pathlib import Path

import cbcc.delivery_workspace as delivery_workspace
from cbcc.asset_universe_authority import compile_asset_universe


LEGACY_HTML = '''<!doctype html><html><head><style>
.page{display:none}.page.active{display:block}.sidebar{position:sticky}
</style></head><body><div class="app"><aside class="sidebar"><div class="nav"><div class="nav-label">工作区</div><a href="#overview" data-route="overview" class="route-link">工作台</a><a href="#assets" data-route="assets" class="route-link">资产中心</a></div><div class="sidebar-foot">默认中文交付</div></aside><div class="workspace"><header class="topbar"><input id="global-search"></header><section class="page active" data-route="overview"><h1>项目</h1></section><section class="page" data-route="assets"><div class="asset-card route-link" data-route="asset/A01">A01</div></section><section class="page asset-page" data-route="asset/A01"><button class="subnav-btn">设计卡</button><button class="copy-btn">复制</button></section></div></div><script>const allPages=[...document.querySelectorAll('.page')];const routeLinks=[...document.querySelectorAll('.route-link')];function go(r){allPages.forEach(x=>x.classList.remove('active'));const t=allPages.find(x=>x.dataset.route===r);if(t)t.classList.add('active')}</script></body></html>'''


def test_delivery_workspace_preserves_v036_interaction_floor_and_adds_operations(tmp_path, monkeypatch):
    package_dir = tmp_path / 'project'
    artifacts = package_dir / 'artifacts'
    artifacts.mkdir(parents=True)
    output = package_dir / 'index.html'
    (artifacts / 'operator_execution_board.json').write_text('{"launch_board":[{"priority":"P0","exact_action":"发布已批准 Listing"}]}', encoding='utf-8')
    (artifacts / 'seven_tool_continuity.json').write_text('{"capabilities":[{"id":"listing","name":"Listing Creative","project_status":"ACTIVE","business_outputs":["final listing"]}]}', encoding='utf-8')
    (artifacts / 'pricing_economics_authority.json').write_text('{"status":"MISSING_INPUT","missing_inputs":["unit_cost"]}', encoding='utf-8')

    def fake_legacy(package_dir: Path, output: Path, title: str = 'CBCC Delivery') -> Path:
        output.write_text(LEGACY_HTML, encoding='utf-8')
        return output

    monkeypatch.setattr(delivery_workspace, '_build_legacy_delivery_html', fake_legacy)
    monkeypatch.setattr(delivery_workspace, 'operator_execution_html', lambda _: '<section id="operator-execution">运营动作正文</section>')

    result = delivery_workspace.build_delivery_html(package_dir, output)
    page = result.read_text(encoding='utf-8')

    # v0.6.36 interaction floor is preserved: routed pages, one active page, asset detail,
    # local views, copy action and search remain in the final artifact.
    assert '.page{display:none}' in page
    assert '.page.active{display:block}' in page
    assert 'function go(r)' in page
    assert 'data-route="asset/A01"' in page
    assert 'subnav-btn' in page
    assert 'copy-btn' in page
    assert 'global-search' in page
    assert 'class="sidebar"' in page

    # v0.6.37+ operator/commercial density is additive as a normal routed work surface.
    assert 'data-route="operations"' in page
    assert '运营执行' in page
    assert 'id="operator-execution"' in page
    assert 'id="commercial-brain"' in page

    # The v0.6.39–0.6.41 post-processing shell must not replace the legacy interaction model.
    assert 'cbcc-project-authored-workspace' not in page
    assert 'project-object-switcher' not in page


def test_platform_gallery_capacity_does_not_cap_asset_universe():
    assets = []
    for idx in range(1, 4):
        assets.append({'asset_id': f'H{idx:02d}', 'variant_cluster': 'HERO', 'surface': 'GALLERY', 'decision_intent': 'IDENTIFY', 'variant_id': f'H{idx:02d}'})
    for idx in range(1, 7):
        assets.append({'asset_id': f'B{idx:02d}', 'variant_cluster': 'BENEFIT_OR_PROOF', 'surface': 'GALLERY', 'decision_intent': 'PROOF', 'variant_id': f'B{idx:02d}'})
    for idx in range(1, 5):
        assets.append({'asset_id': f'AD{idx:02d}', 'variant_cluster': 'PAID_AD', 'surface': 'PAID_AD', 'decision_intent': 'RELATE', 'variant_id': f'AD{idx:02d}', 'deployment_state': 'PAID_MEDIA'})
    assets.append({'asset_id': 'PDP01', 'variant_cluster': 'A_PLUS_PDP', 'surface': 'LONGFORM', 'decision_intent': 'PROOF', 'variant_id': 'PDP01', 'deployment_state': 'PDP_CONTENT'})
    assets.append({'asset_id': 'VID01', 'variant_cluster': 'SOCIAL_VIDEO', 'surface': 'SHORT_VIDEO', 'decision_intent': 'RELATE', 'variant_id': 'VID01'})

    universe = compile_asset_universe(assets, {'listing_image_capacity': 9})

    assert universe['platform_capacity'] == 9
    assert universe['platform_capacity_is_activation_constraint_only'] is True
    assert universe['fixed_total_asset_limit'] is False
    assert universe['total_asset_candidates'] == 15
    assert len(universe['clusters']['HERO']) == 3
    assert len(universe['clusters']['PAID_AD']) == 4
    assert 'PDP01' in universe['pools']['PDP_CONTENT']


def test_platform_capacity_language_is_activation_only():
    universe = compile_asset_universe([{'asset_id': 'H01', 'surface': 'GALLERY', 'decision_intent': 'IDENTIFY'}], {'gallery_capacity': 9})
    principle = universe['principle'].lower()
    assert 'simultaneous live activation set' in principle
    assert 'never limits the total asset universe' in principle
