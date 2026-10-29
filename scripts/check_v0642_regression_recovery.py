#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def must(text: str, needles: list[str], label: str) -> None:
    missing = [n for n in needles if n not in text]
    if missing:
        raise SystemExit(f'{label} missing required authority: {missing}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('plugin_dir')
    args = ap.parse_args()
    root = Path(args.plugin_dir)

    manifest = json.loads((root / 'plugin.json').read_text(encoding='utf-8'))
    if manifest.get('version') != '0.6.42':
        raise SystemExit(f'plugin version mismatch: {manifest.get("version")}')

    skill_root = root / 'skills' / 'cross-border-commerce-creative'
    host = (skill_root / 'SKILL.md').read_text(encoding='utf-8')
    canonical = (skill_root / 'resources' / 'SKILL.md').read_text(encoding='utf-8')
    delivery = (skill_root / 'resources' / 'runtime' / 'cbcc' / 'delivery_workspace.py').read_text(encoding='utf-8')

    if len(host.encode('utf-8')) < 16000:
        raise SystemExit(f'Host Skill unexpectedly thin: {len(host.encode("utf-8"))} bytes')
    if len(canonical.encode('utf-8')) < 70000:
        raise SystemExit(f'Canonical Skill unexpectedly thin: {len(canonical.encode("utf-8"))} bytes')

    required = [
        'v0.6.42 Regression Recovery Authority',
        'v0.6.36',
        'Asset Universe',
        'Live / Activation Set',
        'H01/H02/H03',
        'Market Research',
        'Advertising Optimization',
        'Review Analysis',
        'Model Prompt CN',
        'Model Prompt EN',
        'Production / Assembly Notes',
        'MISSING_INPUT',
    ]
    must(host, required, 'Host Skill')
    must(canonical, required, 'Canonical Skill')

    if 'project_authored_html(text)' in delivery or 'from .project_authored_html import project_authored_html' in delivery:
        raise SystemExit('final delivery path still wires the v0.6.39-v0.6.41 global project_authored_html postprocessor')
    must(delivery, ['operator_execution_html', 'data-route="operations"', 'v0.6.36', 'never flatten FULL delivery into one long page'], 'delivery_workspace')

    prompts = manifest.get('extensions', {}).get('com.openai', {}).get('interface', {}).get('defaultPrompt') or []
    joined = '\n'.join(str(x) for x in prompts)
    must(joined, ['v0.6.42', '最多9图/7图/1视频', 'Asset Universe', '一次只显示一个一级工作面'], 'plugin defaultPrompt')

    print('v0.6.42 regression-recovery package guard: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
