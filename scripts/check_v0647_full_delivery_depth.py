#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def must(text: str, needles: list[str], label: str) -> None:
    missing = [x for x in needles if x not in text]
    if missing:
        raise SystemExit(f'{label} missing v0.6.47 contract: {missing}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('plugin_dir')
    args = ap.parse_args()
    root = Path(args.plugin_dir)
    manifest = json.loads((root / 'plugin.json').read_text(encoding='utf-8'))
    if manifest.get('version') != '0.6.47':
        raise SystemExit(f'plugin version mismatch: {manifest.get("version")}')
    interface = manifest.get('extensions', {}).get('com.openai', {}).get('interface') or {}
    if interface.get('defaultPrompt'):
        raise SystemExit('business-policy defaultPrompt must remain absent')

    skill_root = root / 'skills/cross-border-commerce-creative'
    host = (skill_root / 'SKILL.md').read_text(encoding='utf-8')
    canonical = (skill_root / 'resources/SKILL.md').read_text(encoding='utf-8')
    for text, label in ((host, 'Host Skill'), (canonical, 'Canonical Skill')):
        must(text, [
            'v0.6.47', 'Host-native FULL Materialization Contract',
            '平台 × 区域 × 人群', 'race_ethnicity', 'religion', 'holiday_calendar', 'payment', 'logistics', 'local_regulation',
            'English baseline', '中文释义', 'Asset Universe', 'Activation Set',
            'Subject Presence System', 'Production Parameter Closure', 'cbcc-commercial-v1',
        ], label)

    prompts = skill_root / 'resources/prompts'
    for name in ('full_delivery_materialization_authority.md', 'commercial_continuity_lineage_authority.md', 'dynamic_asset_curation.md', 'creative_direction_surface_prompt_compiler.md', 'commercial_delivery_stability_authority.md'):
        if not (prompts / name).exists():
            raise SystemExit(f'missing required authority: {name}')

    runtime = skill_root / 'resources/runtime/cbcc'
    required = {
        'full_delivery_depth_v3.py': ['MARKET_CULTURE_DIMENSIONS', 'audit_full_strategy_depth_v3', 'audit_host_full_package', 'audit_asset_portfolio_depth'],
        'strategy_depth_projection_v3.py': ['intersectionality', 'holiday_calendar', 'religion', 'resource_tradeoff_plan', 'inclusive_photography'],
        'claim_grade_safety_v0647.py': ['PENDING_EVIDENCE', 'evidence_grade', "'C'"],
        'full_delivery_materialization.py': ['ASSET_UNIVERSE.json', 'FULL_DELIVERY_OBJECT_MANIFEST.json', 'FULL_MATERIALIZATION_AUDIT.json', 'materialize_video_objects'],
        'commercial_continuity_bootstrap.py': ['_cbcc_v0647_full_depth_projection', '_cbcc_v0647_full_depth_v3', 'wrap_claim_grade_safety'],
        'commercial_delivery_continuity.py': ['finalize_full_delivery_materialization', 'materialize_commerce_decision_context'],
    }
    for name, needles in required.items():
        path = runtime / name
        if not path.exists():
            raise SystemExit(f'missing v0.6.47 runtime file: {name}')
        must(path.read_text(encoding='utf-8'), needles, name)

    openai_yaml = (skill_root / 'agents/openai.yaml').read_text(encoding='utf-8')
    if 'default_prompt:' in openai_yaml:
        raise SystemExit('agents/openai.yaml regained a business default_prompt')

    for path in root.rglob('*'):
        if path.is_file() and (path.suffix in {'.pyc', '.pyo'} or '__pycache__' in path.parts):
            raise SystemExit(f'compiled cache leaked into plugin: {path.relative_to(root)}')

    print('v0.6.47 FULL commercial depth / Host materialization parity guard: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
