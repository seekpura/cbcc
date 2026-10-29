#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def must(text: str, needles: list[str], label: str) -> None:
    missing = [x for x in needles if x not in text]
    if missing:
        raise SystemExit(f'{label} missing v0.6.44 authority: {missing}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('plugin_dir')
    args = ap.parse_args()
    root = Path(args.plugin_dir)

    manifest = json.loads((root / 'plugin.json').read_text(encoding='utf-8'))
    compat = json.loads((root / '.codex-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    if manifest.get('version') != '0.6.44':
        raise SystemExit(f'plugin version mismatch: {manifest.get("version")}')

    for label, data in [('plugin.json', manifest), ('.codex-plugin/plugin.json', compat)]:
        interface = data.get('extensions', {}).get('com.openai', {}).get('interface') if label == 'plugin.json' else data.get('interface')
        interface = interface or {}
        if 'defaultPrompt' in interface:
            raise SystemExit(f'{label} must omit defaultPrompt; business authority belongs in Skill')

    skill_root = root / 'skills' / 'cross-border-commerce-creative'
    host = (skill_root / 'SKILL.md').read_text(encoding='utf-8')
    canonical = (skill_root / 'resources' / 'SKILL.md').read_text(encoding='utf-8')
    boundary = (skill_root / 'resources' / 'prompts' / 'default_prompt_authority_boundary.md').read_text(encoding='utf-8')

    required = [
        'Default Prompt Is Not Authority',
        'Host Skill / Canonical Skill',
        '人类交付中文优先',
        'Asset Universe',
        'Portfolio Curator + Creative Director + Per-Asset Art Director',
        '升级只能做加法',
        'defaultPrompt',
    ]
    must(host, required, 'Host Skill')
    must(canonical, required, 'Canonical Skill')
    must(boundary, required, 'authority boundary')

    for text, label in [(host, 'Host Skill'), (canonical, 'Canonical Skill')]:
        must(text, ['Global Chinese Interpretation Authority', 'v0.6.42 Regression Recovery Authority'], label)

    print('v0.6.44 default prompt authority package guard: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
