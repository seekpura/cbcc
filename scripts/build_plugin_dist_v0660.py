#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0659 as v0659

ROOT = Path(__file__).resolve().parents[1]
LEDGER = (ROOT / 'references' / 'CONVERSATION_REQUIREMENT_AUDIT.md').read_text(encoding='utf-8').strip()
K01_FIXTURE = (ROOT / 'references' / 'K01_2026-10-30_REAL_OUTPUT_REGRESSION.md').read_text(encoding='utf-8').strip()
FULL_VALIDATOR = ROOT / 'scripts' / 'check_full_requirement_continuity.py'


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.60-cumulative-requirements-real-output-lock', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.60', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(v0659.canonical_skill(version))
    header = '''
## 0.8 CUMULATIVE USER REQUIREMENT LEDGER + REAL FULL OUTPUT LOCK — highest current precedence

`resources/references/CONVERSATION_REQUIREMENT_AUDIT.md` is mandatory release authority. It is the cumulative ledger of the user's long-form requirements; the latest local bug or latest turn is never the whole product specification unless the user explicitly replaces prior requirements. Before any change to strategy, assets, Art Direction, Prompt, production, Human Workspace, language, economics, review or runtime, re-read the cumulative ledger and its companion source contracts.

A requirement is not satisfied because the rule exists in Skill/Markdown or because a unit test passes. The affected real object must prove consumption: authored project object → structured Asset Art Direction → Design Card → Model Prompt/Visible Copy/Production Notes → Provider Job/Result → Review/Revision → Human Workspace, according to the requirement's semantic plane.

The 2026-10-30 KIYUU K01 Malaysia package is a frozen negative fixture. FULL acceptance must reject equivalent regressions: `assets/` five-file Host shortcut, missing structured Art Direction, global POST_COMPOSITE/no-text/background-generator behavior, product-everywhere portfolio, missing opportunity-sweep decisions, fixed capability-menu shell, missing Provider Result/Review/Revision/actual-output QA, incomplete decision logs, or pricing recommendation ahead of required unit-economics inputs.

### Integrated render correction
- Integrated final render remains the normal route. Exact target-market visible copy, typography/layout, real-product reference, scene, people, props, evidence, camera/light, CMF/material and finishing may be produced together when the Agent selects that route.
- Historical `DETERMINISTIC_COMPOSITION_AFTER_RENDER` is not a global default. `POST_COMPOSITE / EXACT_PIXEL_COMPOSITE / NO_VISIBLE_COPY / PRODUCT_ABSENT` require an explicit per-asset professional reason or real provider limitation.
- When Product Presence requires a visible real product and exact source pixels are not explicitly immutable, use `REFERENCE_GUIDED_NATIVE_LOCK` and bind real product references into the Provider Job.
- The Prompt Compiler may not invent product presence, copy route or layout. Those are structured Agent Art Direction decisions.

### Materialization correction
FULL projects must use the mature asset compiler/export path. The Host may not hand-author a thin replacement package containing only Design Card + Prompt CN/EN + Visible Copy + Notes. Human HTML must project the full structured Art Direction and all currently relevant deep business objects; mature routing mechanics alone do not excuse thin objects or a fixed capability taxonomy.
'''
    return text + '\n' + header + '\n\n' + LEDGER + '\n\n' + K01_FIXTURE + '\n'


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0659.copy_repo_resources(dest)
    current = canonical_skill('0.6.60')
    (dest / 'SKILL.md').write_text(current, encoding='utf-8')
    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'CONVERSATION_REQUIREMENT_AUDIT.md').write_text(LEDGER + '\n', encoding='utf-8')
    (refs / 'K01_2026-10-30_REAL_OUTPUT_REGRESSION.md').write_text(K01_FIXTURE + '\n', encoding='utf-8')
    scripts = dest / 'scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / FULL_VALIDATOR.name).write_text(FULL_VALIDATOR.read_text(encoding='utf-8'), encoding='utf-8')
    (dest / 'VERSION').write_text('0.6.60-cumulative-requirements-real-output-lock\n', encoding='utf-8')


def openai_yaml() -> str:
    return v0659.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0659.plugin_manifest(version)
    manifest['version'] = '0.6.60'
    manifest['description'] = 'Cross-border ecommerce Commerce Agent with cumulative user-requirement authority, real FULL output regression blocking, integrated native render, full Art Direction, open-world assets and mature workspace continuity.'
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '累计长要求总账 + 真实FULL输出阻断；默认一体最终成图，禁止五文件简包和固定能力壳回归'
    interface['longDescription'] = (
        'v0.6.60 将历次用户长要求恢复为累计 release authority，并把 2026-10-30 K01 实际失败包冻结为 negative fixture。'
        'FULL 不再允许 Host 手搓五文件 assets/ 简包、默认后合成/禁字/禁商品、商品铺满全部资产、缺完整结构化 Art Direction、'
        '固定能力菜单、缺 Provider Result/Review/Revision/真实输出 QA。Runtime 恢复逐资产 MODEL_RENDER_INTEGRATED 与 REFERENCE_GUIDED_NATIVE_LOCK 默认路线，'
        'POST_COMPOSITE/EXACT_PIXEL/NO_VISIBLE_COPY/PRODUCT_ABSENT 仅按资产专业选择或真实 Provider 限制使用。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0659.v0658.v0655.v0654.v0653.v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.60 Cumulative Requirements + Real FULL Output Lock'
    release['authority_version'] = '0.6.60-cumulative-requirements-real-output-lock'
    release.setdefault('delivery_contract', {}).update({
        'cumulative_conversation_requirement_ledger_required': True,
        'new_long_requirements_must_merge_into_ledger': True,
        'real_full_output_regression_fixture_required': True,
        'host_five_file_asset_shortcut_forbidden': True,
        'structured_asset_art_direction_required_before_prompt': True,
        'integrated_final_render_is_normal_default': True,
        'global_post_composite_or_no_visible_copy_default_forbidden': True,
        'reference_guided_native_product_default_when_visible': True,
        'product_presence_is_per_asset_decision': True,
        'fixed_capability_menu_shell_forbidden': True,
        'provider_result_review_revision_actual_output_qa_required_for_production_completion_claim': True,
        'v0659_authority_source_parity_preserved': True,
        'v0658_full_art_direction_end_to_end_preserved': True,
        'v0655_open_world_asset_universe_preserved': True,
        'v0654_workspace_prompt_continuity_preserved': True,
        'v0653_business_object_density_preserved': True,
        'v0652_master_construction_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.60 cumulative requirements and real FULL output lock release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist_v0660'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
