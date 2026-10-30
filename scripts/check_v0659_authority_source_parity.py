#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _skill_version(path: Path) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(encoding='utf-8')
    m = re.search(r'(?m)^version:\s*([^\n]+)$', text)
    return m.group(1).strip() if m else None


def _semver_family(value: str | None) -> str | None:
    if not value:
        return None
    m = re.match(r'^(\d+\.\d+\.\d+)', value.strip())
    return m.group(1) if m else None


def run(plugin_root: Path) -> dict:
    issues: list[dict[str, str]] = []
    skill_root = plugin_root / 'skills' / 'cross-border-commerce-creative'
    top_skill = skill_root / 'SKILL.md'
    resource_skill = skill_root / 'resources' / 'SKILL.md'
    version_file = skill_root / 'resources' / 'VERSION'
    manifest_path = plugin_root / 'plugin.json'

    top_version = _skill_version(top_skill)
    resource_version = _skill_version(resource_skill)
    resource_marker = version_file.read_text(encoding='utf-8').strip() if version_file.exists() else None
    manifest_version = None
    if manifest_path.exists():
        manifest_version = str(json.loads(manifest_path.read_text(encoding='utf-8')).get('version') or '') or None

    values = {
        'plugin_manifest': manifest_version,
        'top_skill': top_version,
        'resources_skill': resource_version,
        'resources_version': resource_marker,
    }
    families = {k: _semver_family(v) for k, v in values.items()}
    expected = families.get('plugin_manifest')

    for key, family in families.items():
        if family != expected:
            issues.append({
                'code': 'AUTHORITY_VERSION_FAMILY_MISMATCH',
                'detail': f'{key}={values[key]!r} family={family!r}, expected={expected!r}',
            })

    if top_skill.exists() and resource_skill.exists():
        top_text = top_skill.read_text(encoding='utf-8')
        resource_text = resource_skill.read_text(encoding='utf-8')
        if top_text != resource_text:
            issues.append({
                'code': 'CURRENT_SKILL_CONTENT_DIVERGENCE',
                'detail': 'packaged top-level SKILL.md and resources/SKILL.md are not byte-identical current authority',
            })
    else:
        issues.append({'code': 'CURRENT_SKILL_MISSING', 'detail': 'one or both packaged current Skill files are missing'})

    required_tokens = [
        'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md',
        'PROMPT_ART_DIRECTION_MASTER_CONTRACT.md',
        '人物', '场景', '摄影', '灯光', 'CMF', '材质',
        'Asset Opportunity Universe', 'cbcc-commercial-v1',
    ]
    if top_skill.exists():
        text = top_skill.read_text(encoding='utf-8')
        for token in required_tokens:
            if token not in text:
                issues.append({'code': 'CURRENT_SKILL_CAPABILITY_TOKEN_MISSING', 'detail': token})

    return {
        'status': 'PASS' if not issues else 'FAIL',
        'values': values,
        'families': families,
        'issues': issues,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('plugin_root', type=Path)
    args = ap.parse_args()
    result = run(args.plugin_root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
