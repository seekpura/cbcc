from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def _project(tmp_path: Path) -> Path:
    project = tmp_path / 'KIYUU_ACCEPTANCE'
    _write(
        project / 'artifacts/strategy/MASTER_STRATEGY_CN.md',
        '# KIYUU 商品商业与创意策略\n\n'
        '## 4. 营销核心策略\n'
        '### 第一购买判断\n先让消费者理解商品身份与当前购买理由。\n\n'
        '## 5. 视觉 / 摄影策略\n'
        '### 商品保真\n真实商品像素、包装文字与比例保持 source-bound。\n\n'
        '### 摄影与 CMF\n暖白背景，商品主导，材质高光受控；参数必须进入逐资产 Prompt。\n\n'
        '## 6. 平台内容矩阵\n'
        '### TikTok Shop PDP\n主图、证据图与使用图按当前消费者问题动态生成。\n',
    )
    _write(project / 'artifacts/strategy/strategy_authority.json', json.dumps({'status': 'READY'}, ensure_ascii=False))
    _write(
        project / 'artifacts/product_truth.json',
        json.dumps({'product': {'brand': 'KIYUU', 'product_name': 'Oil Control Anti Acne Moisturizing Gel', 'size': '30g'}}, ensure_ascii=False),
    )
    _write(
        project / 'artifacts/target_context.json',
        json.dumps({'target': {'market': 'malaysia', 'platform': 'tiktok_shop', 'locale': 'ms-MY', 'delivery_locale': 'zh-CN'}}, ensure_ascii=False),
    )
    _write(
        project / 'artifacts/asset_architecture.json',
        json.dumps({'assets': [{'asset_id': 'LST-01', 'surface': 'PDP gallery', 'decision_intent': 'IDENTIFY', 'asset_type': 'IMAGE'}]}, ensure_ascii=False),
    )
    asset = project / 'artifacts/asset_packages/LST-01'
    _write(
        asset / '00_asset_manifest.yaml',
        'asset_name: KIYUU K01 Hero\n'
        'surface: PDP gallery\n'
        'decision_intent: IDENTIFY\n'
        'consumer_question: What is it and what do I receive?\n'
        'asset_type: IMAGE\n',
    )
    _write(
        asset / '12_design_card.json',
        json.dumps({
            'asset_name': 'KIYUU K01 Hero',
            'surface': 'PDP gallery',
            'asset_type': 'IMAGE',
            'commerce_task': {
                'decision_intent': 'IDENTIFY',
                'consumer_question': 'What is it and what do I receive?',
                'reason_to_exist': '建立商品身份与第一购买理由',
                'purchase_barrier': '消费者无法快速确认商品与包装',
                'target_belief': '这是 KIYUU 30g 日常凝胶，并且包装与实物一致',
            },
            'visual_narrative': {'what_must_be_visible': '真实商品主体、包装关系与清晰标签'},
            'subject_action_environment_props': {'subject': '真实商品', 'environment': 'warm-white commerce field'},
            'composition_camera': {'focal_length_mm': '70–85mm equivalent', 'composition_grammar': 'product-dominant identity field'},
            'lighting_material_cmf': {'key': 'large soft key', 'highlight_policy': 'controlled packaging highlight'},
            'photography_execution': {'capture_mode': 'COMPOSITE', 'color_management': 'sRGB'},
        }, ensure_ascii=False, indent=2),
    )
    _write(asset / '05_prompt_CN.txt', '中文 Canonical Prompt：保持真实商品像素，执行商品主导构图、暖白环境与受控高光。')
    _write(asset / '06_prompt_EN.txt', 'English Canonical Prompt: preserve the supplied real-product pixels and execute the product-dominant composition.')
    return project


def test_project_delivery_builder_materializes_real_human_delivery(tmp_path: Path):
    project = _project(tmp_path)
    dist = tmp_path / 'dist'
    subprocess.run(
        [sys.executable, str(ROOT / 'builders/project_delivery_builder.py'), str(project), str(dist)],
        check=True,
        cwd=ROOT,
    )

    package = dist / f'{project.name}_DELIVERY'
    archive = dist / f'{project.name}_DELIVERY.zip'
    html_path = package / 'index.html'
    manifest_path = package / 'DELIVERY_MANIFEST.json'

    assert html_path.exists(), 'complete human delivery must include index.html'
    assert archive.exists(), 'complete human delivery must include a ZIP archive'
    assert manifest_path.exists()

    html = html_path.read_text(encoding='utf-8')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))

    assert '<html lang="zh-CN">' in html
    assert 'CBCC 电商工作台' in html
    assert 'data-workspace-kind="asset-object"' in html
    assert '资产对象' in html
    assert '自由进入' in html
    assert 'asset-production-rail' not in html
    assert 'asset-phase' not in html
    assert '中文 Canonical Prompt：保持真实商品像素' in html
    assert 'English Canonical Prompt: preserve the supplied real-product pixels' in html
    assert '摄影 / CMF' in html
    assert 'sRGB' in html

    assert manifest['status'] == 'DELIVERY_READY'
    assert manifest['workspace_contract']['complete_human_html'] is True
    assert manifest['workspace_contract']['chinese_first'] is True
    assert manifest['workspace_contract']['object_based_asset_workspace'] is True
    assert manifest['workspace_contract']['obsolete_phase_rail_absent'] is True
    assert manifest['asset_package_preserved'] is True

    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        prefix = f'{project.name}_DELIVERY/'
        assert prefix + 'index.html' in names
        assert prefix + 'asset_packages/LST-01/05_prompt_CN.txt' in names
        assert prefix + 'asset_packages/LST-01/06_prompt_EN.txt' in names
        assert prefix + 'DELIVERY_MANIFEST.json' in names
