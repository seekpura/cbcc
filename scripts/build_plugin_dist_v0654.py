#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0653 as v0653

ROOT = Path(__file__).resolve().parents[1]
CONTINUITY_LOCK = (ROOT / 'references' / 'HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md').read_text(encoding='utf-8').strip()
VALIDATOR = ROOT / 'scripts' / 'check_v0654_workspace_prompt_continuity.py'


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.54-workspace-prompt-continuity', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.54', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(v0653.canonical_skill(version))
    header = '''\n## 0.3 HUMAN WORKSPACE + PROMPT CONTINUITY LOCK — highest materialization precedence\n\nFor FULL generation and repair, `resources/references/HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md` is mandatory. When packaged runtime is executable, materialization is runtime-first through `resources/runtime/cbcc/delivery_export.py` → `delivery_workspace.py` → `delivery_html.py` → `commercial_workspace_shell.py`. Do not hand-author a replacement `index.html` for language/compliance/nine-domain/media/density fixes. Preserve `cbcc-commercial-v1`, the mature routed primary work-surface model, local subviews/lenses, `asset/<id>` detail routes, Prompt workspace, per-asset Prompt lens, search/copy/back/hash, responsive behavior and print/PDF unless the user explicitly requests a redesign.\n\nIf an asset has `05_prompt_CN.txt` or `06_prompt_EN.txt`, the Human HTML must directly expose its Model Prompt CN/EN; retaining prompt files only is not completion. Nine domains are completeness semantics, not nine fixed pages/sections. Exact-heading validation must never drive a new global shell.\n'''
    return text + header + '\n\n' + CONTINUITY_LOCK + '\n'


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0653.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.54'), encoding='utf-8')
    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md').write_text(CONTINUITY_LOCK + '\n', encoding='utf-8')
    scripts = dest / 'scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    if VALIDATOR.exists():
        (scripts / VALIDATOR.name).write_text(VALIDATOR.read_text(encoding='utf-8'), encoding='utf-8')


def openai_yaml() -> str:
    return v0653.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0653.plugin_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '全业务密度 + 成熟工作台连续性：Prompt 可见、asset 详情、路由版式与商业对象只加不减'
    interface['longDescription'] = (
        '在 v0.6.53 全业务对象密度基础上锁定 Human Workspace 与 Prompt 投影连续性。FULL/修复优先使用成熟 delivery runtime，'
        '保留 cbcc-commercial-v1、v0.6.36 routed workspace、一次一个一级工作面、project-authored routes、asset/<id> 详情、Prompt 工作面、'
        '逐资产 Prompt lens、search/copy/back/hash、responsive、print/PDF。资产包存在 Model Prompt CN/EN 时必须在人类 HTML 中直接可达；'
        '九域只定义完整度，不允许为了补规则重写成固定九页/九 section 报告。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0653.v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.54 Workspace + Prompt Projection Continuity'
    release['authority_version'] = '0.6.54-workspace-prompt-continuity'
    release.setdefault('delivery_contract', {}).update({
        'human_workspace_prompt_continuity_lock_required': True,
        'human_workspace_prompt_continuity_lock_path': 'references/HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md',
        'workspace_prompt_continuity_validator': 'scripts/check_v0654_workspace_prompt_continuity.py',
        'mature_workspace_shell_required': True,
        'cbcc_commercial_v1_required': True,
        'runtime_first_materialization_when_available': True,
        'repair_shell_rewrite_forbidden': True,
        'prompt_files_must_be_human_projected': True,
        'per_asset_prompt_lens_required': True,
        'prompt_workspace_required': True,
        'asset_detail_routes_required': True,
        'exact_heading_validation_cannot_drive_layout': True,
        'top_level_ia_change_requires_user_redesign_request': True,
        'v0653_business_object_density_preserved': True,
        'v0652_master_construction_preserved': True,
        'v0651_chinese_canonical_preserved': True,
        'mature_commercial_creative_capabilities_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.54 workspace/prompt continuity release.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0654'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
