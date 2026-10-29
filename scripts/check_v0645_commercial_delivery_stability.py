#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def must(text: str, needles: list[str], label: str) -> None:
    missing = [x for x in needles if x not in text]
    if missing:
        raise SystemExit(f'{label} missing v0.6.45 contract: {missing}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('plugin_dir')
    args = ap.parse_args()
    root = Path(args.plugin_dir)

    manifest = json.loads((root / 'plugin.json').read_text(encoding='utf-8'))
    interface = manifest.get('extensions', {}).get('com.openai', {}).get('interface') or {}
    if manifest.get('version') != '0.6.45':
        raise SystemExit(f'plugin version mismatch: {manifest.get("version")}')
    if 'defaultPrompt' in interface and interface.get('defaultPrompt'):
        raise SystemExit('defaultPrompt must not regain business-policy content')

    skill_root = root / 'skills' / 'cross-border-commerce-creative'
    agent_yaml = (skill_root / 'agents' / 'openai.yaml').read_text(encoding='utf-8')
    if 'default_prompt:' in agent_yaml:
        raise SystemExit('agents/openai.yaml must not carry a hidden business default_prompt')

    host = (skill_root / 'SKILL.md').read_text(encoding='utf-8')
    canonical = (skill_root / 'resources' / 'SKILL.md').read_text(encoding='utf-8')
    required_authority = [
        'Commercial Delivery Stability Authority',
        'English baseline',
        'Platform primary language',
        'Chinese interpretation',
        'cbcc-commercial-v1',
        'UNSPECIFIED',
        '真源媒体',
    ]
    must(host, required_authority, 'Host Skill')
    must(canonical, required_authority, 'Canonical Skill')

    runtime = skill_root / 'resources' / 'runtime' / 'cbcc'
    files = {
        'platform_scope.py': ['UNSPECIFIED', 'CURRENT_REQUEST', '_target_is_explicit'],
        'delivery_language_matrix.py': ['EN_PLATFORM_PRIMARY_CN', 'CN_ONLY', 'EN_CN_PENDING_PLATFORM_PRIMARY'],
        'source_truth_media.py': ['SOURCE_TRUTH_MEDIA_AUDIT.json', 'SOURCE_TRUTH_STATUS.md', "package / 'sources'"],
        'commercial_workspace_shell.py': ["WORKSPACE_SHELL_VERSION = 'cbcc-commercial-v1'", '一次只显示一个一级工作面'],
        'delivery_export.py': ['materialize_source_truth_media', 'resolve_platform_scope', 'audit_language_delivery', 'apply_commercial_workspace_shell'],
    }
    for name, needles in files.items():
        path = runtime / name
        if not path.exists():
            raise SystemExit(f'missing runtime file: {name}')
        must(path.read_text(encoding='utf-8'), needles, name)

    print('v0.6.45 commercial delivery stability package guard: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
