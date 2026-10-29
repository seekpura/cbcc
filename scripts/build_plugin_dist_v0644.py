#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0643 as v0643
from scripts import build_plugin_dist_v0642 as v0642

ROOT = Path(__file__).resolve().parents[1]

AUTHORITY_BOUNDARY = (ROOT / 'prompts/default_prompt_authority_boundary.md').read_text(encoding='utf-8').strip()
CHINESE_INTERPRETATION_AUTHORITY = v0643.CHINESE_INTERPRETATION_AUTHORITY
DEFAULT_PROMPTS: list[str] = []

_prev_wrapper = v0643.skill_wrapper
_prev_copy = v0643.copy_repo_resources
_orig_manifest = base.plugin_manifest


def skill_wrapper(version: str) -> str:
    text = _prev_wrapper(version)
    return v0642._inject(text, AUTHORITY_BOUNDARY)


def copy_repo_resources(dest: Path) -> None:
    _prev_copy(dest)
    canonical_path = dest / 'SKILL.md'
    canonical = canonical_path.read_text(encoding='utf-8')
    canonical = canonical.replace(
        'version: 0.6.43-global-chinese-interpretation',
        'version: 0.6.44-default-prompt-authority-consolidation',
        1,
    )
    canonical = v0642._inject(canonical, AUTHORITY_BOUNDARY)
    canonical_path.write_text(canonical, encoding='utf-8')


def plugin_manifest(version: str) -> dict:
    """Manifest metadata only. Business authority lives in Host/Canonical Skill."""
    manifest = _orig_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    return manifest


def build(output_dir: Path) -> dict:
    # v0.6.44 establishes a permanent packaging boundary: manifest prompts are not policy.
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    data['release'] = 'v0.6.44 Default Prompt Authority Consolidation'
    data['authority_version'] = '0.6.44-default-prompt-authority-consolidation'
    data.setdefault('delivery_contract', {}).update({
        'default_prompt_is_not_business_authority': True,
        'manifest_default_prompt_omitted': True,
        'host_and_canonical_are_single_business_authority': True,
        'fixed_business_principles_integrated_in_skill': True,
        'v0643_global_chinese_interpretation_preserved': True,
        'v0642_interaction_and_asset_universe_preserved': True,
    })
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.44 with business authority consolidated into Skill.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
