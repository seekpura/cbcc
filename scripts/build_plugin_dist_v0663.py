#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0662 as v0662

ROOT = Path(__file__).resolve().parents[1]
CLOSURE = (ROOT / 'references' / 'REAL_K01_HOST_SHORTCUT_AUDIT_CLOSURE_V0663.md').read_text(encoding='utf-8').strip()
TEST = ROOT / 'tests' / 'test_v0663_real_k01_host_shortcut_audit.py'

CURRENT_PATCH = r'''
## 0.12 Real K01 Host-Shortcut Audit Closure — v0.6.63
The historical `data/project.json + assets/<id>/` Host shortcut is now part of the real FULL package audit, not an out-of-band manual observation. An equivalent package must fail for the frozen K01 structural regression classes, including incomplete five-file asset folders, missing structured Art Direction, unstructured/all-visible Product Presence, missing opportunity sweep, global post-composite/no-text/no-product patterns, missing generated media/Provider Result/Review/Revision, missing information-assumption-decision log, pricing ahead of unit economics, and fixed capability-menu/route taxonomy.

Production-ready mature assets must also materialize all four production objects plus the machine Design Card: `05_prompt_CN.txt`, `06_prompt_EN.txt`, `12_design_card.json`, `14_visible_copy_block.json`, `15_production_assembly_notes.json`. Missing any of them is `PRODUCTION_OBJECTS_INCOMPLETE`.

This closes the negative-fixture audit bypass only. Fresh positive K01 FULL generation, Provider execution, actual-output QA and review/revision lineage remain required before FULL behavior is called complete.
'''.strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.63-real-k01-host-shortcut-audit-closure', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.63', text, count=1)
    text = text.replace('Before claiming v0.6.62 behavior complete:', 'Before claiming v0.6.63 behavior complete:')
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(v0662.canonical_skill(version))
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('v0.6.62 canonical Skill lost expected FULL-depth marker')
    return text.replace(marker, '\n' + CURRENT_PATCH + '\n\n## 1. FULL depth remains mandatory', 1)


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0662.copy_repo_resources(dest)
    current = canonical_skill('0.6.63')
    (dest / 'SKILL.md').write_text(current, encoding='utf-8')
    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'REAL_K01_HOST_SHORTCUT_AUDIT_CLOSURE_V0663.md').write_text(CLOSURE + '\n', encoding='utf-8')
    tests = dest / 'tests'
    tests.mkdir(parents=True, exist_ok=True)
    (tests / TEST.name).write_text(TEST.read_text(encoding='utf-8'), encoding='utf-8')
    (dest / 'VERSION').write_text('0.6.63-real-k01-host-shortcut-audit-closure\n', encoding='utf-8')


def openai_yaml() -> str:
    return v0662.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0662.plugin_manifest(version)
    manifest['version'] = '0.6.63'
    manifest['description'] = 'Cross-border ecommerce Commerce Agent with cumulative requirement runtime enforcement, real K01 host-shortcut audit closure, integrated native render, full Art Direction and mature FULL materialization.'
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '真实K01旁路封死：data/project.json + 五文件assets简包也进入FULL审计；生产四对象强制物化'
    interface['longDescription'] = (
        'v0.6.63 将真实K01历史旁路直接纳入FULL Runtime审计：data/project.json、assets五文件简包、全局后合成/禁字/禁商品、'
        '商品铺满全部资产、缺结构化Art Direction、缺机会家族审计、缺真实输出/Provider/Review/Revision、固定能力菜单与Economics未闭环却给建议价均可被实际包级阻断。'
        '生产就绪成熟资产同时强制Prompt CN/EN、Design Card、Visible Copy与Production Notes完整物化。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0662.v0661.v0660.v0659.v0658.v0655.v0654.v0653.v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.63 Real K01 Host-Shortcut Audit Closure'
    release['authority_version'] = '0.6.63-real-k01-host-shortcut-audit-closure'
    release.setdefault('delivery_contract', {}).update({
        'real_k01_data_project_shortcut_audited': True,
        'historical_k01_17_structural_failures_locked': True,
        'production_objects_cn_en_design_card_visible_copy_notes_required': True,
        'host_five_file_asset_shortcut_blocked': True,
        'fresh_positive_k01_full_e2e_still_required': True,
        'v0662_one_to_one_long_requirement_runtime_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.63 real K01 host-shortcut audit closure release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist_v0663'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
