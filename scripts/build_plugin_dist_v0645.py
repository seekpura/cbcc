#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0644 as v0644
from scripts import build_plugin_dist_v0642 as v0642

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = (ROOT / 'prompts/commercial_delivery_stability_authority.md').read_text(encoding='utf-8').strip()
DEFAULT_PROMPTS: list[str] = []

_prev_wrapper = v0644.skill_wrapper
_prev_copy = v0644.copy_repo_resources


def skill_wrapper(version: str) -> str:
    text = _prev_wrapper(version)
    return v0642._inject(text, AUTHORITY)


def copy_repo_resources(dest: Path) -> None:
    _prev_copy(dest)
    canonical_path = dest / 'SKILL.md'
    canonical = canonical_path.read_text(encoding='utf-8')
    canonical = canonical.replace(
        'version: 0.6.44-default-prompt-authority-consolidation',
        'version: 0.6.45-commercial-delivery-stability',
        1,
    )
    canonical = v0642._inject(canonical, AUTHORITY)
    canonical_path.write_text(canonical, encoding='utf-8')


def plugin_manifest(version: str) -> dict:
    manifest = v0644.plugin_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    return manifest


def openai_yaml() -> str:
    # Invocation metadata only. Business/product authority lives in Host/Canonical Skill.
    return '''interface:
  display_name: Cross-Border Commerce Creative
  short_description: 跨境电商策略、内容、创意与完整交付
policy:
  allow_implicit_invocation: true
'''


def build(output_dir: Path) -> dict:
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    data['release'] = 'v0.6.45 Commercial Delivery Stability'
    data['authority_version'] = '0.6.45-commercial-delivery-stability'
    data.setdefault('delivery_contract', {}).update({
        'source_truth_media_portable': True,
        'platform_market_explicit_only': True,
        'no_historical_platform_default': True,
        'language_matrix_english_platform_primary_chinese': True,
        'china_platform_chinese_only': True,
        'workspace_shell_version': 'cbcc-commercial-v1',
        'workspace_shell_frozen_across_normal_releases': True,
        'manifest_default_prompt_absent': True,
        'agent_yaml_business_default_prompt_absent': True,
        'v0644_default_prompt_boundary_preserved': True,
        'v0643_chinese_interpretation_preserved': True,
        'v0642_routed_workspace_preserved': True,
    })
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.45 commercial delivery stability release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
