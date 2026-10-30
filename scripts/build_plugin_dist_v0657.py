#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0656 as v0656

ROOT = Path(__file__).resolve().parents[1]


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.57-model-prompt-runtime-parity', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.57', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(v0656.canonical_skill(version))
    header = '''\n## 0.6 MODEL PROMPT RUNTIME PARITY\n\nThe installed/runtime compiler must consume `resources/runtime/cbcc/model_prompt_semantic_membrane.py` after legacy prompt rendering and before readiness/Provider dispatch. Host authority, packaged runtime and Human Prompt surfaces must agree. A release is incomplete if the Skill bans Excel/QA/repair leakage but `agent_authority_prompt_compiler.py` still emits the pre-membrane prompt.\n'''
    return text + header


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0656.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.57'), encoding='utf-8')
    runtime = dest / 'runtime' / 'cbcc'
    runtime.mkdir(parents=True, exist_ok=True)
    for name in ('model_prompt_semantic_membrane.py', 'agent_authority_prompt_compiler.py'):
        src = ROOT / 'runtime' / 'cbcc' / name
        (runtime / name).write_text(src.read_text(encoding='utf-8'), encoding='utf-8')


def openai_yaml() -> str:
    return v0656.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0656.plugin_manifest(version)
    manifest['version'] = '0.6.57'
    interface = manifest['extensions']['com.openai']['interface']
    interface['shortDescription'] = '生图 Prompt 语义隔离 Runtime 对齐：真源/QA/修复链不再进入模型提示词'
    interface['longDescription'] = (
        '在 v0.6.56 Model Prompt Semantic Membrane 基础上完成 packaged runtime parity。'
        'agent_authority_prompt_compiler.py 在生成 Prompt 后强制经过 semantic membrane，再做 readiness 与 Provider dispatch。'
        'Excel/项目真源、内部 SKU/路径、QA 验收、最小修复链保留在 Production/Review；模型只收到真正会改变像素/帧的执行信息。'
        '继续保留 v0.6.55 开放式资产宇宙、v0.6.54 成熟工作台与此前全部商业对象能力。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0656.v0655.v0654.v0653.v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.57 Model Prompt Runtime Parity'
    release['authority_version'] = '0.6.57-model-prompt-runtime-parity'
    release.setdefault('delivery_contract', {}).update({
        'model_prompt_semantic_membrane_runtime_integrated': True,
        'agent_authority_prompt_compiler_membrane_required': True,
        'host_runtime_prompt_parity_required': True,
        'v0656_model_prompt_semantic_membrane_preserved': True,
        'v0655_open_world_asset_universe_preserved': True,
        'v0654_workspace_prompt_continuity_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.57 model-prompt runtime parity release.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0657'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
