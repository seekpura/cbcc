#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scripts import build_plugin_dist_v0655 as v0655

ROOT = Path(__file__).resolve().parents[1]
MEMBRANE = (ROOT / 'references' / 'MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md').read_text(encoding='utf-8').strip()


def _normalize_version(text: str) -> str:
    text = re.sub(r'(?m)^version:\s*[^\n]+$', 'version: 0.6.56-model-prompt-semantic-membrane', text, count=1)
    text = re.sub(r'(?m)^# Cross-Border Commerce Creative v[^\n]+$', '# Cross-Border Commerce Creative v0.6.56', text, count=1)
    return text


def canonical_skill(version: str) -> str:
    text = _normalize_version(v0655.canonical_skill(version))
    header = '''\n## 0.5 MODEL PROMPT SEMANTIC MEMBRANE — model-facing prompt is not the production dossier\n\nFor every image/video production asset, `resources/references/MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md` is mandatory and has highest precedence over any older wording that could be interpreted as dumping the whole production/review chain into Model Prompt. **Only model-visible, pixel/frame-changing instructions belong in Model Prompt CN/EN.**\n\nDo not put source-of-truth hierarchy, Excel/project-file authority, local paths, internal SKU/asset IDs, provider routing, machine/audit metadata, editable/frozen-layer workflow, QA/acceptance checklists, or minimum-repair order into Model Prompt. Product Truth and Excel remain authoritative upstream; compile their resolved facts into explicit visual/copy instructions instead of telling the image model to consult files it cannot see.\n\nA prompt may say `attached/supplied product reference images` only when the Provider Job actually binds those images. Opaque project names such as `K01`, filenames or source-table names are not model instructions unless they are themselves visible consumer copy or disambiguate a real bound reference.\n\nQA remains a separate Review object. A QA criterion may be converted into a forward generation constraint only when it directly changes the render: e.g. `hands anatomically natural`, `render no extra marketing text`, `keep headline inside the mobile-safe area`. `QA:` labels and `minimum repair: text layer → pump reflection → full regeneration` never belong in Model Prompt.\n'''
    return text + header + '\n\n' + MEMBRANE + '\n'


def skill_wrapper(version: str) -> str:
    return canonical_skill(version)


def copy_repo_resources(dest: Path) -> None:
    v0655.copy_repo_resources(dest)
    (dest / 'SKILL.md').write_text(canonical_skill('0.6.56'), encoding='utf-8')
    refs = dest / 'references'
    refs.mkdir(parents=True, exist_ok=True)
    (refs / 'MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md').write_text(MEMBRANE + '\n', encoding='utf-8')


def openai_yaml() -> str:
    return v0655.openai_yaml()


def plugin_manifest(version: str) -> dict:
    manifest = v0655.plugin_manifest(version)
    interface = manifest['extensions']['com.openai']['interface']
    interface.pop('defaultPrompt', None)
    interface['shortDescription'] = '生图 Prompt 语义隔离：只给模型像素级执行信息，真源/QA/修复链留在生产与 Review'
    interface['longDescription'] = (
        '在 v0.6.55 开放式资产宇宙基础上增加 Model Prompt Semantic Membrane。'
        'Model Prompt CN/EN 只保留会改变图像/视频输出的视觉执行信息；Excel/项目文件真源层级、内部 SKU/资产 ID、Provider 路由、'
        'QA 验收、最小修复顺序、可编辑/冻结层工作流不再泄漏进生图提示词。只有真实绑定到 Provider Job 的商品参考图才可在 Prompt 中称为 attached/supplied reference。'
        'Product Truth、完整 Art Direction、Production Notes、Review/QA 和局部修复能力全部保留，只是投影到正确对象。'
    )
    return manifest


def build(output_dir: Path) -> dict:
    base = v0655.v0654.v0653.v0652.v0651.v0650.v0649.v0648.v0647.base
    base.DEFAULT_PROMPTS = []
    base.plugin_manifest = plugin_manifest
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.openai_yaml = openai_yaml
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    release = json.loads(manifest_path.read_text(encoding='utf-8'))
    release['release'] = 'v0.6.56 Model Prompt Semantic Membrane'
    release['authority_version'] = '0.6.56-model-prompt-semantic-membrane'
    release.setdefault('delivery_contract', {}).update({
        'model_prompt_semantic_membrane_required': True,
        'model_prompt_semantic_membrane_path': 'references/MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md',
        'model_prompt_pixel_changing_only': True,
        'excel_source_authority_in_model_prompt_forbidden': True,
        'qa_checklist_in_model_prompt_forbidden': True,
        'minimum_repair_route_in_model_prompt_forbidden': True,
        'opaque_internal_source_names_in_model_prompt_forbidden': True,
        'provider_bound_reference_required_for_attached_reference_wording': True,
        'qa_visual_constraints_may_be_forward_compiled': True,
        'production_notes_and_review_objects_preserved': True,
        'v0655_open_world_asset_universe_preserved': True,
        'v0654_workspace_prompt_continuity_preserved': True,
        'v0653_business_object_density_preserved': True,
        'v0652_master_construction_preserved': True,
    })
    manifest_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return release


def main() -> int:
    parser = argparse.ArgumentParser(description='Build CBCC v0.6.56 model-prompt semantic membrane release.')
    parser.add_argument('--output-dir', default=str(ROOT / 'dist_v0656'))
    args = parser.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
