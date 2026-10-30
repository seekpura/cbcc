#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0664 as v0664

ROOT = Path(__file__).resolve().parents[1]
LEDGER = (ROOT / 'references' / 'CONVERSATION_REQUIREMENT_AUDIT.md').read_text(encoding='utf-8').strip()
EXT = (ROOT / 'references' / 'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md').read_text(encoding='utf-8').strip()
VERBATIM = (ROOT / 'references' / 'USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md').read_text(encoding='utf-8').strip()
MATRIX = (ROOT / 'references' / 'REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md').read_text(encoding='utf-8').strip()
CONSUMER_MAP = (ROOT / 'references' / 'REQUIREMENT_CONSUMER_MAP_V0664.json').read_text(encoding='utf-8').strip()
SOURCE_LOCK = (ROOT / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').read_text(encoding='utf-8').strip()
SOURCE_ADDENDUM = (ROOT / 'references' / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK_V0664_ADDENDUM.md').read_text(encoding='utf-8').strip()
HOST_SNAPSHOT = (ROOT / 'references' / 'HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md').read_text(encoding='utf-8').strip()
TEXT_PARITY = (ROOT / 'references' / 'AUTHORITY_TEXT_PARITY_V0665.md').read_text(encoding='utf-8').strip()
ADDENDUM = (ROOT / 'prompts' / 'canonical_authority_loading_map_v0665_addendum.md').read_text(encoding='utf-8').strip()
CONSUMER_CHECKER = ROOT / 'scripts' / 'check_v0664_requirement_consumer_map.py'

PATCH = r'''
## 0.14 Current-Release Text Parity + Strict Requirement Consumer Accounting — v0.6.65
Forward-carried completion gates use release-agnostic wording (`current installed release`) instead of embedding a historical version that becomes stale on the next patch. The stable human implementation ledger is `resources/references/REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md`; the stable source lock is `resources/references/SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md` with `CURRENT` authority semantics.

**One-to-one implementation proof is stricter than the human matrix.** `resources/references/REQUIREMENT_CONSUMER_MAP_V0664.json` is the machine-level authority for REQ-001..060: every requirement names concrete existing Consumer paths, concrete downstream proof objects, and an explicit evidence status. `resources/scripts/check_v0664_requirement_consumer_map.py` must pass `60/60` with zero issues. Generic placeholders such as “relevant Runtime consumer”, `TBD` or `TODO` are release failures.

Installed-plugin parity and active Host Skill snapshot parity are separate evidence. Load `resources/references/HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md`. If the current conversation/session still resolves an older Skill after the plugin is updated, record `HOST_SKILL_SNAPSHOT_STALE`; that Host context cannot supply positive FULL E2E proof for the new release. A fresh Host context that actually loads the current installed Skill is required for final positive E2E acceptance.

Business Runtime remains additive: long-requirement Runtime consumers, 12-family Asset Universe audit, Product Presence audit, integrated native render authority, real-K01 17-class shortcut rejection, four-production-object materialization, complete Art Direction/Prompt preservation and mature workspace contracts all remain in force.

Fresh positive K01 FULL host/plugin E2E remains required before behavioral closure.
'''.strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.65-current-release-text-parity', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.65', text, count=1)
    text = text.replace('REQUIREMENT_IMPLEMENTATION_MATRIX_V0662.md', 'REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md')
    text = text.replace('REQUIREMENT_IMPLEMENTATION_MATRIX_V0663.md', 'REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md')
    text = text.replace('REQUIREMENT_IMPLEMENTATION_MATRIX_V0664.md', 'REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md')
    text = re.sub(
        r'Before claiming v0\.6\.\d+ behavior complete:',
        'Before claiming current installed release behavior complete:',
        text,
    )
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(v0664.canonical_skill(version))
    marker = '\n## 1. FULL depth remains mandatory'
    if marker not in text:
        raise RuntimeError('v0.6.64 canonical Skill lost expected FULL-depth marker')
    if '## 0.14 Current-Release Text Parity + Strict Requirement Consumer Accounting' not in text:
        text = text.replace(marker, '\n' + PATCH + '\n\n## 1. FULL depth remains mandatory', 1)
    return text


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0664.copy_repo_resources(dest)
    current = canonical_skill('0.6.65')
    (dest / 'SKILL.md').write_text(current, encoding='utf-8')

    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'CONVERSATION_REQUIREMENT_AUDIT.md').write_text(LEDGER + '\n', encoding='utf-8')
    (refs / 'CONVERSATION_REQUIREMENT_LEDGER_EXTENSION_01.md').write_text(EXT + '\n', encoding='utf-8')
    (refs / 'USER_LONG_REQUIREMENTS_STRATEGY_CULTURE_EXECUTION_CN.md').write_text(VERBATIM + '\n', encoding='utf-8')
    (refs / 'REQUIREMENT_IMPLEMENTATION_MATRIX_CURRENT.md').write_text(MATRIX + '\n', encoding='utf-8')
    (refs / 'REQUIREMENT_CONSUMER_MAP_V0664.json').write_text(CONSUMER_MAP + '\n', encoding='utf-8')
    (refs / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK.md').write_text(SOURCE_LOCK + '\n', encoding='utf-8')
    (refs / 'SOURCE_REQUIREMENT_NON_REGRESSION_LOCK_V0664_ADDENDUM.md').write_text(SOURCE_ADDENDUM + '\n', encoding='utf-8')
    (refs / 'HOST_SKILL_SNAPSHOT_PARITY_LOCK_V0664.md').write_text(HOST_SNAPSHOT + '\n', encoding='utf-8')
    (refs / 'AUTHORITY_TEXT_PARITY_V0665.md').write_text(TEXT_PARITY + '\n', encoding='utf-8')

    prompts = dest / 'prompts'
    prompts.mkdir(parents=True, exist_ok=True)
    (prompts / 'canonical_authority_loading_map_v0665_addendum.md').write_text(ADDENDUM + '\n', encoding='utf-8')

    scripts = dest / 'scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / CONSUMER_CHECKER.name).write_text(CONSUMER_CHECKER.read_text(encoding='utf-8'), encoding='utf-8')

    (dest / 'VERSION').write_text('0.6.65-current-release-text-parity\n', encoding='utf-8')


def openai_yaml() -> str:
    return v0664.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0664.plugin_manifest(version)
    manifest['version'] = '0.6.65'
    manifest['description'] = 'Cross-border ecommerce Commerce Agent with strict REQ-001..060 consumer accounting, Host-snapshot parity proof, cumulative/verbatim requirements, real K01 shortcut closure, integrated native render and mature FULL materialization.'
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '60条需求逐条绑定具体Consumer/Proof；Host Skill快照与installed release分开验，真实K01旁路继续阻断'
    interface['longDescription'] = (
        'v0.6.65 将REQ-001..060逐条绑定到具体存在的Runtime/Release Consumer与Proof Object，GitHub Actions严格检查60/60、0缺口。'
        '同时锁定Host Skill Snapshot parity：插件更新后旧会话若仍加载旧Skill，不得拿旧快照冒充新版本正向E2E。'
        '继续保留累计/原文长要求、12家族Asset Universe、Product Presence、一体成图、完整Art Direction、真实K01 17项阻断与成熟物化链。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0664.v0663.v0662.v0661.v0660.v0659.v0658.v0655.v0654.v0653.v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.65 Current-Release Text Parity + Strict Consumer Accounting'
    release['authority_version'] = '0.6.65-current-release-text-parity'
    release.setdefault('delivery_contract', {}).update({
        'release_proof_wording_version_agnostic': True,
        'stable_current_requirement_matrix_packaged': True,
        'strict_req_001_060_consumer_map_packaged': True,
        'strict_consumer_map_ci_60_of_60_zero_issues_required': True,
        'host_skill_snapshot_parity_required_for_positive_e2e': True,
        'stable_current_source_lock_packaged': True,
        'v0663_real_k01_17_structural_failures_preserved': True,
        'fresh_positive_k01_full_e2e_still_required': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.65 current-release text parity + strict consumer-accounting release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist_v0665'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
