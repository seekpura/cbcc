#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0660 as v0660

ROOT = Path(__file__).resolve().parents[1]
VERBATIM = (ROOT / 'references' / 'USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md').read_text(encoding='utf-8').strip()
EXTENSION = (ROOT / 'references' / 'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md').read_text(encoding='utf-8').strip()
SOURCE_LOCK = (ROOT / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').read_text(encoding='utf-8').strip()
CANONICAL_MAP = (ROOT / 'prompts' / 'canonical_authority_loading_map.md').read_text(encoding='utf-8').strip()
TEST = ROOT / 'tests' / 'test_v0661_verbatim_long_requirement_lock.py'


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.61-verbatim-long-requirement-source-lock', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.61', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(v0660.canonical_skill(version))
    header = '''
## 0.9 VERBATIM LONG-REQUIREMENT SOURCE LOCK — exact execution details cannot be summarized away

`resources/references/USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md` is a mandatory verbatim user authority. `resources/references/CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md` maps its concrete requirements to REQ-051..060 for release traceability. The normalized IDs never authorize replacing the source's exact sequence, thresholds, table columns, P0/P1/P2 definitions, visual-execution requirements or semantic output objects with a shorter summary.

For relevant FULL projects, preserve and visibly consume at least the following concrete locks: information audit → pending questions → assumptions → continue (maximum 10 questions before continuing under assumptions); Product Truth `真实卖点 / 可感知利益 / 情绪价值 / 不可宣称项` + A/B/C; platform × region × audience × ethnicity/culture WHY; P0 compliance; `族裔 × 性别 × 年龄 × 收入 × 地域`; deep-skin exposure/reflector/diffusion and inclusive casting; platform dimensions/duration/cover/subtitles/music rights/traffic/CTA/landing/UTM/attribution; back-translation/festival/payment/logistics/religious taboo/local law with `待查证`; explicit P0/P1/P2 keep/cut tradeoff; RACE execution table; ethnicity/culture adaptation checklist; Content Matrix columns `RACE阶段` and `族裔文化适配/禁忌校验`; separate assumption/decision log; and all nine semantic FULL output objects.

These are semantic/business-object requirements, **not permission to recreate a fixed nine-page report or permanent Product/Market/Strategy/Listing/Visual/Assets menu**. Project-authored routed workspace requirements remain unchanged.
'''
    return text + '\n' + header + '\n\n' + EXTENSION + '\n\n' + VERBATIM + '\n'


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0660.copy_repo_resources(dest)
    current = canonical_skill('0.6.61')
    (dest / 'SKILL.md').write_text(current, encoding='utf-8')

    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md').write_text(VERBATIM + '\n', encoding='utf-8')
    (refs / 'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md').write_text(EXTENSION + '\n', encoding='utf-8')
    (refs / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').write_text(SOURCE_LOCK + '\n', encoding='utf-8')

    prompts = dest / 'prompts'
    prompts.mkdir(parents=True, exist_ok=True)
    (prompts / 'canonical_authority_loading_map.md').write_text(CANONICAL_MAP + '\n', encoding='utf-8')

    tests = dest / 'tests'
    tests.mkdir(parents=True, exist_ok=True)
    (tests / TEST.name).write_text(TEST.read_text(encoding='utf-8'), encoding='utf-8')

    (dest / 'VERSION').write_text('0.6.61-verbatim-long-requirement-source-lock\n', encoding='utf-8')


def openai_yaml() -> str:
    return v0660.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0660.plugin_manifest(version)
    manifest['version'] = '0.6.61'
    manifest['description'] = 'Cross-border ecommerce Commerce Agent with verbatim cumulative user-requirement authority, real FULL output regression blocking, integrated native render, full Art Direction and project-authored workspace continuity.'
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '长要求原文锁：具体执行顺序/表格/阈值不可被摘要；继续保留一体成图、完整Art Direction与FULL真实输出阻断'
    interface['longDescription'] = (
        'v0.6.61 将用户长要求按原文冻结并建立 REQ-051..060 映射，防止 Product Truth、平台/区域/人群/族裔文化 WHY、'
        '交叉性、P0 合规、深肤色摄影、平台执行、本地化、P0/P1/P2、RACE/文化表、Content Matrix 两列和九项 FULL 对象在后续修复中被摘要掉。'
        '同时保留 v0.6.60 的真实 FULL 输出负例阻断、一体最终成图/REFERENCE_GUIDED_NATIVE_LOCK、成熟资产包、Provider/Review/Revision/QA 与项目作者化 routed workspace。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0660.v0659.v0658.v0655.v0654.v0653.v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.61 Verbatim Long Requirement Source Lock'
    release['authority_version'] = '0.6.61-verbatim-long-requirement-source-lock'
    release.setdefault('delivery_contract', {}).update({
        'verbatim_user_long_requirement_source_required': True,
        'normalized_requirement_ids_do_not_replace_source_detail': True,
        'max_ten_questions_then_continue_under_assumptions': True,
        'product_truth_four_way_plus_abc_required': True,
        'platform_region_audience_ethnicity_culture_why_required': True,
        'p0_compliance_and_regulated_category_review_required': True,
        'intersectionality_required': True,
        'inclusive_deep_skin_photography_execution_required_when_relevant': True,
        'platform_execution_and_localization_objects_required': True,
        'p0_p1_p2_keep_cut_tradeoff_required': True,
        'race_and_ethnicity_culture_execution_tables_required': True,
        'content_matrix_race_and_culture_columns_required': True,
        'nine_semantic_full_output_objects_required_without_fixed_ui_shell': True,
        'v0660_real_full_output_regression_lock_preserved': True,
        'v0660_integrated_native_render_authority_preserved': True,
        'v0659_authority_source_parity_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.61 verbatim long-requirement source-lock release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist_v0661'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
