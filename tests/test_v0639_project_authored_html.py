from pathlib import Path
import inspect

import cbcc.delivery_workspace as delivery_workspace
from cbcc.project_authored_html import project_authored_html


SAMPLE = '''<!doctype html><html><head><style>.app{display:grid}.sidebar{position:sticky}</style></head><body><div class="app"><aside class="sidebar"><div class="nav"><a href="#overview" data-route="overview" class="route-link">工作台</a><a href="#assets" data-route="assets" class="route-link">资产中心</a></div><div class="sidebar-foot">默认中文交付</div></aside><div class="workspace"><section class="page active" data-route="overview"><h1>KIYUU K01</h1></section><section class="page" data-route="assets"><h1>资产中心</h1></section></div></div></body></html>'''


def test_v0639_transform_remains_available_only_as_historical_compatibility():
    out = project_authored_html(SAMPLE)
    assert 'cbcc-project-authored-workspace' in out
    assert 'project-object-switcher' in out


def test_v0642_final_renderer_no_longer_calls_project_authored_html():
    source = inspect.getsource(delivery_workspace)
    assert 'from .project_authored_html import project_authored_html' not in source
    assert 'project_authored_html(text)' not in source


def test_v0642_without_operator_artifacts_preserves_legacy_routed_shell(tmp_path, monkeypatch):
    package_dir = tmp_path / 'project'
    package_dir.mkdir()
    output = package_dir / 'index.html'

    def fake_legacy(package_dir: Path, output: Path, title: str = 'CBCC Delivery') -> Path:
        output.write_text(SAMPLE, encoding='utf-8')
        return output

    monkeypatch.setattr(delivery_workspace, '_build_legacy_delivery_html', fake_legacy)
    monkeypatch.setattr(delivery_workspace, 'operator_execution_html', lambda _: '')
    result = delivery_workspace.build_delivery_html(package_dir, output)
    out = result.read_text(encoding='utf-8')

    assert 'class="sidebar"' in out
    assert 'data-route="overview"' in out
    assert 'data-route="assets"' in out
    assert 'project-object-switcher' not in out
