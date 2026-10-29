#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def must(text: str, needles: list[str], label: str) -> None:
    missing = [x for x in needles if x not in text]
    if missing:
        raise SystemExit(f'{label} missing required v0.6.43 authority: {missing}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('plugin_dir')
    args = ap.parse_args()
    root = Path(args.plugin_dir)

    manifest = json.loads((root / 'plugin.json').read_text(encoding='utf-8'))
    if manifest.get('version') != '0.6.43':
        raise SystemExit(f'plugin version mismatch: {manifest.get("version")}')

    skill_root = root / 'skills' / 'cross-border-commerce-creative'
    host = (skill_root / 'SKILL.md').read_text(encoding='utf-8')
    canonical = (skill_root / 'resources' / 'SKILL.md').read_text(encoding='utf-8')
    authority = (skill_root / 'resources' / 'prompts' / 'global_chinese_interpretation_authority.md').read_text(encoding='utf-8')
    final_contract = (skill_root / 'resources' / 'references' / 'FINAL_OUTPUT_CONTRACT.md').read_text(encoding='utf-8')
    export = (skill_root / 'resources' / 'runtime' / 'cbcc' / 'delivery_export.py').read_text(encoding='utf-8')
    global_runtime = (skill_root / 'resources' / 'runtime' / 'cbcc' / 'global_chinese_interpretation.py').read_text(encoding='utf-8')
    ui_runtime = (skill_root / 'resources' / 'runtime' / 'cbcc' / 'chinese_interpretation_ui.py').read_text(encoding='utf-8')

    if len(host.encode('utf-8')) < 18000:
        raise SystemExit(f'Host Skill unexpectedly thin: {len(host.encode("utf-8"))} bytes')
    if len(canonical.encode('utf-8')) < 70000:
        raise SystemExit(f'Canonical Skill unexpectedly thin: {len(canonical.encode("utf-8"))} bytes')

    required = [
        'Global Chinese Interpretation Authority',
        'category / classification / category path',
        'description / short description / long description',
        'search terms / backend terms / keyword clusters',
        'Video / creator',
        'Advertising',
        'Review / CS / returns',
        'Research / strategy / competitor evidence',
        '待补中文释义',
        'Runtime must audit and BLOCK',
    ]
    must(host, required, 'Host Skill')
    must(canonical, required, 'Canonical Skill')
    must(authority, required, 'Global Chinese Interpretation Authority')

    must(final_contract, [
        '全局中文释义合同',
        '类目 / 分类 / 类目路径',
        '资产 Visible Copy',
        'Video / Creator',
        'Ads',
        'Review / CS / Return',
        '待补中文释义',
    ], 'Final Output Contract')

    must(export, [
        'normalize_global_chinese_interpretation',
        'audit_global_chinese_interpretation',
        'render_upload_center_md_with_global_cn',
        'apply_chinese_interpretation_ui',
        'BLOCKED global Chinese interpretation contract failed',
    ], 'delivery_export')
    must(global_runtime, [
        "'PRESERVED_LISTING'",
        "'VIDEO'",
        "'ADS'",
        "'REVIEW'",
        "'RESEARCH'",
        'delivery_translation_zh',
        'Runtime never machine-translates arbitrary copy',
    ], 'global_chinese_interpretation.py')
    must(ui_runtime, ['商品描述', '平台类目', '商品属性', '搜索词', 'heading-en'], 'chinese_interpretation_ui.py')

    prompts = manifest.get('extensions', {}).get('com.openai', {}).get('interface', {}).get('defaultPrompt') or []
    joined = '\n'.join(str(x) for x in prompts)
    must(joined, [
        'v0.6.43',
        '类目/分类',
        '描述',
        '属性',
        '搜索词',
        'FAQ',
        '视频',
        '广告',
        '评论',
        '研究',
        '待补中文释义',
    ], 'plugin defaultPrompt')

    print('v0.6.43 global Chinese interpretation package guard: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
