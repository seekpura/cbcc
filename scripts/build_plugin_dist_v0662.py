#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0661 as v0661

ROOT = Path(__file__).resolve().parents[1]
MATRIX = (ROOT / 'references' / 'REQUIREMENT_IMPLEMENTATION_MATRIX_V0662.md').read_text(encoding='utf-8').strip()
TESTS = [
    ROOT / 'tests' / 'test_v0662_long_requirements_runtime_enforcement.py',
    ROOT / 'tests' / 'test_v0662_asset_universe_and_package_regressions.py',
]


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.62-one-to-one-long-requirement-runtime', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.62', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(v0661.canonical_skill(version))
    header = '''
## 0.10 ONE-TO-ONE LONG-REQUIREMENT RUNTIME ENFORCEMENT — current highest precedence

The verbatim long-requirement source is now consumed by Runtime, Human Projection and FULL package audits, not only by release documentation.

For FULL projects:
- pending clarification questions are capped at 10 in the human/operator list; the complete unresolved count/overflow remains recorded and the Agent continues under explicit assumptions / `TO_VERIFY / MISSING_INPUT` instead of stopping;
- major decision logs expose separate `platform / region / audience / race_ethnicity_culture` WHY objects with status + basis/assumption;
- people-inclusive routes expose deep-skin exposure handling plus neutral reflector/bounce/diffusion planning, with final EV/lighting values explicitly Prelight-dependent rather than fabricated;
- the ethnicity/culture checklist carries per-row script, casting, wardrobe/grooming, color and CTA checks;
- P0 compliance is materialized as separate efficacy / ingredients-formula / certification / price / sales-volume / regulated-category checks; missing evidence stays HOLD/TO_VERIFY/MISSING_INPUT;
- the Human Strategy exposes those context-WHY, platform execution/localization/UTM, culture execution and P0 compliance objects directly;
- Asset Universe contains a 12-family opportunity sweep with `COVERED / NOT_NEEDED / TO_VERIFY / MISSING_INPUT + WHY`, never silent omission;
- Product Presence is a structured per-asset decision and the Universe exposes portfolio presence rhythm; real references do not imply product on every asset;
- FULL package acceptance rejects the historical five-file `assets/` shortcut, missing structured Art Direction, integrated-route prompts that still say no-text/no-product, missing Provider Result/Review/Revision/real output, fixed capability-menu shells and missing full Art Direction HTML projection;
- pricing recommendations are blocked when required unit-economics inputs remain missing/unknown.

`resources/references/REQUIREMENT_IMPLEMENTATION_MATRIX_V0662.md` maps REQ-001..060 to source, Runtime consumer, Human/package evidence and current proof status. Rows requiring a fresh real FULL project remain `E2E_PENDING`; tests/source presence cannot promote them to complete.
'''
    return text + '\n' + header + '\n\n' + MATRIX + '\n'


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0661.copy_repo_resources(dest)
    current = canonical_skill('0.6.62')
    (dest / 'SKILL.md').write_text(current, encoding='utf-8')

    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'REQUIREMENT_IMPLEMENTATION_MATRIX_V0662.md').write_text(MATRIX + '\n', encoding='utf-8')

    tests = dest / 'tests'
    tests.mkdir(parents=True, exist_ok=True)
    for test in TESTS:
        (tests / test.name).write_text(test.read_text(encoding='utf-8'), encoding='utf-8')

    (dest / 'VERSION').write_text('0.6.62-one-to-one-long-requirement-runtime\n', encoding='utf-8')


def openai_yaml() -> str:
    return v0661.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0661.plugin_manifest(version)
    manifest['version'] = '0.6.62'
    manifest['description'] = 'Cross-border ecommerce Commerce Agent with one-to-one cumulative requirement runtime enforcement, integrated native render, complete Art Direction, open-world assets and real FULL output blocking.'
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '一一落实：长要求进入Runtime/Human/FULL审计；10问、P0合规、文化五项校验、开放资产宇宙与真实输出链强制消费'
    interface['longDescription'] = (
        'v0.6.62 将用户长要求从原文/Requirement Ledger进一步落实到真实 Runtime Consumer。'
        'FULL 强制最多10个关键问题后继续、平台/区域/人群/族裔文化WHY、深肤色摄影执行、文化脚本/模特/服化道/配色/CTA校验、'
        '功效/成分/认证/价格/销量/强监管P0检查、平台执行/本地化/UTM、开放式12家族机会审计、逐资产Product Presence、'
        '一体成图路线一致性、成熟asset_packages、Provider Result/Review/Revision/真实输出QA与项目作者化Workspace。'
        'REQ-001..060实施矩阵明确区分代码已落实与仍需Fresh K01 FULL E2E的项目。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0661.v0660.v0659.v0658.v0655.v0654.v0653.v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.62 One-to-One Long Requirement Runtime Enforcement'
    release['authority_version'] = '0.6.62-one-to-one-long-requirement-runtime'
    release.setdefault('delivery_contract', {}).update({
        'requirement_implementation_matrix_req_001_060_required': True,
        'max_ten_questions_runtime_enforced': True,
        'four_context_why_runtime_enforced': True,
        'deep_skin_exposure_and_reflector_plan_runtime_enforced': True,
        'culture_script_casting_wardrobe_color_cta_checks_runtime_enforced': True,
        'six_area_p0_compliance_checklist_runtime_enforced': True,
        'platform_execution_localization_attribution_human_projected': True,
        'twelve_family_asset_opportunity_audit_required': True,
        'product_presence_portfolio_audit_required': True,
        'integrated_prompt_route_contradiction_blocked': True,
        'host_five_file_asset_shortcut_blocked': True,
        'structured_art_direction_materialization_required': True,
        'provider_result_review_revision_real_output_required_for_production_completion': True,
        'pricing_recommendation_ahead_of_missing_economics_blocked': True,
        'fixed_capability_menu_shell_blocked': True,
        'fresh_real_full_k01_e2e_still_required_before_complete_claim': True,
        'v0661_verbatim_requirement_source_lock_preserved': True,
        'v0660_integrated_native_render_and_real_output_negative_fixture_preserved': True,
        'v0659_authority_source_parity_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.62 one-to-one long-requirement runtime enforcement release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist_v0662'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
