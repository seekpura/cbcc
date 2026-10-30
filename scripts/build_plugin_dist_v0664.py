#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0663 as v0663

ROOT = Path(__file__).resolve().parents[1]
LEDGER = (ROOT / 'references' / 'CONVERSATION_REQUIREMENT_AUDIT.md').read_text(encoding='utf-8').strip()
EXT = (ROOT / 'references' / 'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md').read_text(encoding='utf-8').strip()
VERBATIM = (ROOT / 'references' / 'USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md').read_text(encoding='utf-8').strip()
MATRIX = (ROOT / 'references' / 'REQUIREMENT_IMPLEMENTATION_MATRIX_V0664.md').read_text(encoding='utf-8').strip()
SOURCE_LOCK = (ROOT / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').read_text(encoding='utf-8').strip()
PARITY = (ROOT / 'references' / 'AUTHORITY_PARITY_REPAIR_V0664.md').read_text(encoding='utf-8').strip()
K01_CLOSURE = (ROOT / 'references' / 'REAL_K01_HOST_SHORTCUT_AUDIT_CLOSURE_V0663.md').read_text(encoding='utf-8').strip()
ADDENDUM = (ROOT / 'prompts' / 'canonical_authority_loading_map_v0664_addendum.md').read_text(encoding='utf-8').strip()

PATCH = r'''
## 0.13 Installed Authority Parity Repair — v0.6.64
Post-install readback of v0.6.63 proved that Runtime changes landed while three authority files drifted: the cumulative ledger was reduced to headings, the source lock still identified v0.6.62, and the current implementation matrix was missing. This is itself a release failure.

v0.6.64 requires the actual installed plugin to contain the **detailed** cumulative REQ-001..050 ledger, REQ-051..060 extension, verbatim user long requirements, `REQUIREMENT_IMPLEMENTATION_MATRIX_V0664.md`, current v0.6.64 source lock, `AUTHORITY_PARITY_REPAIR_V0664.md`, and the v0.6.63 real-K01 shortcut Runtime/authority. Top Skill and `resources/SKILL.md` remain byte-identical. Manifest, both Skills and `resources/VERSION` must identify one 0.6.64 release family.

Source ZIP/build intent is not proof. Re-read the installed plugin after update. Fresh positive K01 FULL E2E remains separately required before behavioral closure.
'''.strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.64-installed-authority-parity-repair', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.64', text, count=1)
    text = text.replace('REQUIREMENT_IMPLEMENTATION_MATRIX_V0662.md', 'REQUIREMENT_IMPLEMENTATION_MATRIX_V0664.md')
    text = text.replace('REQUIREMENT_IMPLEMENTATION_MATRIX_V0663.md', 'REQUIREMENT_IMPLEMENTATION_MATRIX_V0664.md')
    # Release-proof wording must never carry a hard-coded historical version forward.
    text = re.sub(
        r'Before claiming v0\.6\.\d+ behavior complete:',
        'Before claiming current installed release behavior complete:',
        text,
    )
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(v0663.canonical_skill(version))
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('v0.6.63 canonical Skill lost expected FULL-depth marker')
    if '## 0.13 Installed Authority Parity Repair' not in text:
        text = text.replace(marker, '\n' + PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0663.copy_repo_resources(dest)
    current = canonical_skill('0.6.64')
    (dest / 'SKILL.md').write_text(current, encoding='utf-8')

    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'CONVERSATION_REQUIREMENT_AUDIT.md').write_text(LEDGER + '\n', encoding='utf-8')
    (refs / 'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md').write_text(EXT + '\n', encoding='utf-8')
    (refs / 'USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md').write_text(VERBATIM + '\n', encoding='utf-8')
    (refs / 'REQUIREMENT_IMPLEMENTATION_MATRIX_V0664.md').write_text(MATRIX + '\n', encoding='utf-8')
    (refs / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').write_text(SOURCE_LOCK + '\n', encoding='utf-8')
    (refs / 'AUTHORITY_PARITY_REPAIR_V0664.md').write_text(PARITY + '\n', encoding='utf-8')
    (refs / 'REAL_K01_HOST_SHORTCUT_AUDIT_CLOSURE_V0663.md').write_text(K01_CLOSURE + '\n', encoding='utf-8')

    prompts = dest / 'prompts'
    prompts.mkdir(parents=True, exist_ok=True)
    (prompts / 'canonical_authority_loading_map_v0664_addendum.md').write_text(ADDENDUM + '\n', encoding='utf-8')
    (dest / 'VERSION').write_text('0.6.64-installed-authority-parity-repair\n', encoding='utf-8')


def openai_yaml() -> str:
    return v0663.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0663.plugin_manifest(version)
    manifest['version'] = '0.6.64'
    manifest['description'] = 'Cross-border ecommerce Commerce Agent with installed-authority parity repair, cumulative/verbatim requirements, real K01 shortcut closure, integrated native render and mature FULL materialization.'
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '0.6.64权威源一致性修复：详细REQ总账/当前矩阵/Source Lock与Runtime同版，安装后必须回读'
    interface['longDescription'] = (
        'v0.6.64 修复0.6.63实际安装后的权威漂移：恢复详细REQ-001..050累计总账，保留REQ-051..060与用户长要求原文，'
        '打包当前实施矩阵和Source Lock，并继续保留真实K01 17项结构性旁路阻断与生产对象硬约束。安装完成必须从实际插件回读验证。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0663.v0662.v0661.v0660.v0659.v0658.v0655.v0654.v0653.v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.64 Installed Authority Parity Repair'
    release['authority_version'] = '0.6.64-installed-authority-parity-repair'
    release.setdefault('delivery_contract', {}).update({
        'detailed_cumulative_ledger_explicitly_packaged': True,
        'verbatim_long_requirement_explicitly_packaged': True,
        'current_v0664_matrix_explicitly_packaged': True,
        'current_source_lock_explicitly_packaged': True,
        'post_install_actual_plugin_readback_required': True,
        'v0663_real_k01_17_structural_failures_preserved': True,
        'fresh_positive_k01_full_e2e_still_required': True,
        'release_proof_wording_version_agnostic': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.64 installed authority parity repair release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist_v0664'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
