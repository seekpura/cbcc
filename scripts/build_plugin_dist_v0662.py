#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0661 as v0661
from scripts import build_plugin_dist_v0659 as v0659

ROOT = Path(__file__).resolve().parents[1]
MATRIX = (ROOT / 'references' / 'REQUIREMENT_IMPLEMENTATION_MATRIX_V0662.md').read_text(encoding='utf-8').strip()
SOURCE_LOCK = (ROOT / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').read_text(encoding='utf-8').strip()
CANONICAL_BASE = (ROOT / 'prompts' / 'canonical_authority_loading_map.md').read_text(encoding='utf-8').strip()
CANONICAL_ADDENDUM = (ROOT / 'prompts' / 'canonical_authority_loading_map_v0662_addendum.md').read_text(encoding='utf-8').strip()
TESTS = [
    ROOT / 'tests' / 'test_v0662_long_requirements_runtime_enforcement.py',
    ROOT / 'tests' / 'test_v0662_asset_universe_and_package_regressions.py',
]

CURRENT_AUTHORITY = r'''
## 0.9 Cumulative User Requirements + Real FULL Output Lock — current highest release authority
The latest local bug, latest user turn, or latest test is never the whole CBCC specification. FULL/release work must load and consume:
- `resources/references/CONVERSATION_REQUIREMENT_AUDIT.md` — cumulative REQ-001..050 ledger;
- `resources/references/CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md` — REQ-051..060;
- `resources/references/USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md` — verbatim long-form user authority; exact sequencing, thresholds, table columns and execution details may not be replaced by a summary;
- `resources/references/REQUIREMENT_IMPLEMENTATION_MATRIX_V0662.md` — source → Runtime/Consumer → Human/package evidence → proof status for REQ-001..060;
- `resources/references/K01_2026-10-30_REAL_OUTPUT_REGRESSION.md` — real negative FULL fixture;
- `resources/prompts/canonical_authority_loading_map.md` plus the v0.6.62 Runtime consumer addendum.

Rules without a consumed downstream object are intent, not completion. `E2E_PENDING` rows remain pending until the named real output exists.

The 2026-10-30 K01 failure pattern is explicitly prohibited: no Host-authored five-file `assets/` shortcut, no global background-generator / post-composite / no-text / no-product route, no product-everywhere default, no thin asset rows in place of structured Art Direction, no fixed capability-menu shell, no prompts-only claim of produced assets, and no price recommendation ahead of required unit-economics inputs.

## 0.10 One-to-One Long-Requirement Runtime Enforcement
For FULL projects the verbatim user requirements are real Runtime/Human/package contracts:
- Information audit → pending confirmations → explicit assumptions → continue. Human/operator clarification questions are capped at **10**; the complete unresolved count/overflow remains recorded as `TO_VERIFY / MISSING_INPUT / assumption` rather than stopping unrelated work.
- Product Truth separates **真实卖点 / 可感知利益 / 情绪价值 / 不可宣称项**, with A/B/C evidence. C remains subjective/pending and cannot become a hard claim.
- Major decisions expose separate **platform / region / audience / race-ethnicity-culture WHY** with status, basis/assumption, tradeoff, execution and measurement.
- P0 claim/compliance review is materialized separately for **efficacy, ingredients/formula, certifications, price, sales volume, regulated category**. Unknown current law/platform mechanics remain `TO_VERIFY`; missing evidence is never fabricated.
- Intersectionality covers **race/ethnicity × gender × age × income × geography**, with language/religion/lifestyle when relevant. Culture checklist rows separately inspect **script / casting / wardrobe-grooming / color / CTA**.
- When people appear, inclusive photography is an execution object: deep-skin metering/exposure compensation is **Prelight-dependent**, with neutral reflector/bounce/diffusion planning; hair texture, body, disability, age, beauty-standard risk and AI-bias review remain active.
- Platform execution includes dimensions/aspect, duration, cover/first frame, subtitles, music rights, traffic mechanism, CTA, landing handoff, UTM/attribution; regional localization includes back-translation, holiday calendar, payment/logistics, religious taboos and local law.
- P0/P1/P2 resource tradeoff must state what is kept, cut/deferred, why, and restoration condition. “Do everything” is not a tradeoff.
- RACE execution and ethnicity/culture adaptation are explicit tables; Content Matrix carries RACE stage and culture/taboo validation.
- The nine requested output areas are semantic business objects, never permission to make nine fixed pages or a permanent capability taxonomy.

### Asset Universe / Product Presence implementation
FULL Asset Universe performs a 12-family opportunity sweep: Gallery/Hero/Search/PDP; Benefit/Proof/Ingredient/Material/Detail; Scenario/Lifestyle/Human-use; How-to/Routine/Comparison/Objection; A+/Rich/PDP longform/source; Paid; Social/Seeding; Creator/UGC/Affiliate; Video/LIVE; Store/Banner/Landing/Campaign/Seasonal; Lifecycle/Post-purchase; Test/Rotation/A-B. An absent family needs `NOT_NEEDED / TO_VERIFY / MISSING_INPUT + WHY`.

Product Presence is independently authored per asset with `planning_state + presence_why`; real references do not imply visible product on every asset. A portfolio where every asset shows product triggers a portfolio review rather than becoming a default.

### Integrated final-render implementation
Integrated commercial final render is the normal route. When the Agent selects integrated/model-render or hybrid:
- exact target-market visible copy and typography/layout may be rendered in the final image;
- a visible real product uses `REFERENCE_GUIDED_NATIVE_LOCK` with actual provider reference binding unless immutable source pixels are explicitly required;
- legacy “reserve a product/text zone; do not generate product/text; compose later” instructions are a route contradiction unless the asset explicitly selects `POST_COMPOSITE / NO_VISIBLE_COPY / EXACT_PIXEL_COMPOSITE`.

Prompt compilation order is protected:
`structured Agent Art Direction → normalize full Art Direction → historical compiler → per-asset integrated render authority → final semantic membrane`.
The final membrane removes source/Excel/QA/revision/provider orchestration only; it must preserve selected people/scene/composition/copy/camera/light/CMF/material/motion values.

### Mature materialization and real-output completion
FULL production uses mature `asset_packages/<id>` materialization and preserves manifest, strategy, visual spec, photography/layout contracts, source/strategy trace, Design Card, Prompt contract, Visible Copy and Production Notes. A five-file shortcut is rejected.

A production-ready prompt is not a produced asset. Claiming produced/FULL production completion requires the appropriate real chain:
`Provider Job → Provider Result → actual media → Review → smallest Local Revision when needed → provenance/hash`.
If provider execution is unavailable, say so and do not claim actual-output QA.

Human delivery must expose the complete strategy/Art Direction/Prompt/Production/Review objects in Chinese-first routed workspace. `cbcc-commercial-v1` interaction mechanics remain, but Product/Market/Listing/Strategy/Visual/Assets cannot become a permanent global capability menu.

## 0.11 Release Proof Boundary
Before claiming v0.6.62 behavior complete:
1. installed `plugin.json`, top Skill, `resources/SKILL.md`, `resources/VERSION` and changed Runtime files must be re-read from the actual plugin;
2. top and deep Skills must be byte-identical and current;
3. focused/unit/package tests prove local behavior only;
4. a fresh real K01 FULL project must still be run through the installed plugin and inspected against REQ-001..060 plus the K01 negative fixture;
5. actual Provider/Review/Revision/QA rows stay `E2E_PENDING` until real outputs exist.
'''.strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.62-one-to-one-long-requirement-runtime', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.62', text, count=1)
    return text


def _current_canonical_map() -> str:
    base = re.sub(
        r'(?m)^# CBCC Canonical Authority Loading Map — v[^\n]+$',
        '# CBCC Canonical Authority Loading Map — v0.6.62',
        CANONICAL_BASE,
        count=1,
    )
    return base + '\n\n' + CANONICAL_ADDENDUM + '\n'


def canonical_skill(version: str) -> str:
    # Deliberately use the verified v0.6.59 canonical Skill as the mature additive floor.
    # v0.6.60-62 source authorities remain independent packaged files and are loaded by the current
    # authority block below instead of repeatedly embedding every ledger/fixture into the Skill body.
    text = _normalize_version(v0659.canonical_skill(version))
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('v0.6.59 canonical Skill lost expected FULL-depth marker')
    return text.replace(marker, '\n' + CURRENT_AUTHORITY + '\n\n## 1. FULL depth remains mandatory', 1)


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    # Use v0.6.61 resource copying so the cumulative/verbatim authorities remain packaged.
    v0661.copy_repo_resources(dest)
    current = canonical_skill('0.6.62')
    (dest / 'SKILL.md').write_text(current, encoding='utf-8')

    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'REQUIREMENT_IMPLEMENTATION_MATRIX_V0662.md').write_text(MATRIX + '\n', encoding='utf-8')
    (refs / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').write_text(SOURCE_LOCK + '\n', encoding='utf-8')

    prompts = dest / 'prompts'
    prompts.mkdir(parents=True, exist_ok=True)
    (prompts / 'canonical_authority_loading_map.md').write_text(_current_canonical_map(), encoding='utf-8')
    (prompts / 'canonical_authority_loading_map_v0662_addendum.md').write_text(CANONICAL_ADDENDUM + '\n', encoding='utf-8')

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
