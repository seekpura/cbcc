#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0642 as v0642
from scripts import build_plugin_dist_v0647 as v0647

ROOT = Path(__file__).resolve().parents[1]
FINAL_ZIP_LOCK = (ROOT / 'prompts/full_delivery_final_zip_hard_rule_lock.md').read_text(encoding='utf-8').strip()
AUTHORITY_LOADING_MAP = (ROOT / 'prompts/canonical_authority_loading_map.md').read_text(encoding='utf-8').strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.48-final-zip-hard-rule-lock', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.48', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = v0647.canonical_skill(version)
    text = _normalize_version(text)
    text = v0642._inject(text, FINAL_ZIP_LOCK)
    text = v0642._inject(text, AUTHORITY_LOADING_MAP)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0647.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.48'), encoding='utf-8')


def openai_yaml() -> str:
    return v0647.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0647.plugin_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '商业级跨境电商策略、深度研究、创意资产宇宙与最终真实包硬验收'
    interface['longDescription'] = (
        'FULL 项目保持 Product Truth、Market/Region/Audience/Culture、Pricing/Economics/Offer、RACE、'
        'Listing/Search、Visual/Photography、Image/Video/Ads/Social/PDP/A+ Asset Universe、Reviews、Measurement 的完整连续性。'
        'v0.6.48 在 v0.6.47 Host/Runtime parity 之上增加最终真实 ZIP 硬验收：九域对象、A/B/C、交叉性、文化检查、'
        '包容性摄影、平台执行、RACE、P0/P1/P2 与 index.html 人类消费必须在最终包中真实存在，并在重新解压后复核。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)
    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.48 Final ZIP User Hard-Rule Completion Lock'
    release['authority_version'] = '0.6.48-final-zip-hard-rule-lock'
    release.setdefault('delivery_contract', {}).update({
        'final_materialized_package_is_completion_evidence': True,
        'final_zip_reextract_validation_required': True,
        'user_hard_rule_validation_required': True,
        'user_hard_rule_validation_path': 'qa/USER_HARD_RULE_VALIDATION.json',
        'nine_domain_machine_objects_required': True,
        'index_html_must_consume_nine_domains': True,
        'c_grade_hard_claim_forbidden': True,
        'race_ethnicity_not_relevant_cannot_bypass_full_culture_validation': True,
        'inclusive_photography_p0_when_humans_present': True,
        'platform_matrix_execution_fields_required': True,
        'race_four_stage_execution_required': True,
        'resource_tradeoff_p0_p1_p2_required': True,
        'launch_readiness_separate_from_hard_rule_completeness': True,
        'v0647_host_runtime_parity_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.48 final ZIP hard-rule lock release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist_v0648'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
