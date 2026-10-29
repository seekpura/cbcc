#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0637 as v0637
from scripts import build_plugin_dist_v0638 as v0638

ROOT = Path(__file__).resolve().parents[1]

PROJECT_AUTHORITY = r'''
## Project-Authored Human HTML Authority — highest current precedence
- **最终 `index.html` 是当前商品项目的人类产品界面，不是 CBCC 能力目录，也不是流程图。** 一级信息架构由 Agent 根据本项目真实对象、决策、Surface、交付物与运营任务现场作者化；能力名称可以作为内部路由元数据，但不能自动变成固定页面。
- **首屏是项目对象地图，不是步骤列表。** 当前重点 / next action 单独显示，但不得决定永久导航顺序。禁止固定左侧 `Product → Market → Listing → Strategy → Content → Visual → Assets → Prompt → Risk → Sources` 能力菜单；禁止 01→02→03 的阅读暗示，除非该业务对象本身确实存在顺序。
- **页面数量与组合动态。** 没有真实对象就不生成入口；相关对象可以合并到更适合人类工作的同一工作面。Listing、Strategy、Visual、Asset、Video、Economics、Evidence 应使用各自适合的交互，不允许所有领域共用同一张 card-grid 模板。
- **资产是一个对象，不是一条 phase rail。** Design Card、画面、Photography/CMF、Visible Copy、Model Prompt CN/EN、Production/Assembly Notes、QA/来源/修复是同一资产的不同 lens，可按需要自由进入，不得标成固定步骤。
- **运营执行台降为 focus/drawer。** DO NOW / release status 可以存在，但不得以巨大固定区块强插在完整项目最前面；七工具连续性、Runtime consumer、hash、Gate、能力证明属于次级 Inspector/Archive，不得为了“证明系统有能力”强行追加为人类主页面。
- **UI 动态不等于内容缩水。** 项目地图必须能进入完整 Strategy、Listing 最终文案、Visual/Video 策展、逐资产完整 Design Card、Model Prompt CN/EN、Visible Copy Block、Production/Assembly Notes，以及当前相关的 Economics/Ads/Review/Evidence。
'''.strip()

PROJECT_DEFAULT_PROMPT = (
    'v0.6.39 人类交付最高权威：最终 index.html 必须由当前项目对象动态作者化，不得把 CBCC 能力目录做成固定左侧导航或顺序流水线。首屏使用项目对象地图；当前重点/next action 与信息架构分离。页面数量、组合、名称由当前商品、市场、平台、Locale、Listing、创意方向、资产宇宙与生产对象决定。资产详情是一个可自由切换 lens 的对象，不是 Design Card→画面→摄影→文案→Prompt→QA 的步骤轨。运营执行台只能作为 focus/drawer；七工具/Runtime/Gate/Hash 属于次级 Inspector。内容深度保持 0.6.37 商业能力，不得因 UI 动态化缩水。'
)


def _inject(text: str, section: str) -> str:
    if section in text:
        return text
    marker = text.find('\n# ')
    if marker == -1:
        return section + '\n\n' + text
    heading_end = text.find('\n', marker + 1)
    if heading_end == -1:
        return text + '\n\n' + section + '\n'
    return text[:heading_end + 1] + '\n' + section + '\n\n' + text[heading_end + 1:]


def skill_wrapper(version: str) -> str:
    return _inject(v0638.skill_wrapper(version), PROJECT_AUTHORITY)


def copy_repo_resources(dest: Path) -> None:
    v0638.copy_repo_resources(dest)
    canonical_path = dest / 'SKILL.md'
    canonical = canonical_path.read_text(encoding='utf-8')
    canonical = canonical.replace(
        'version: 0.6.38-host-delivery-regression-fix',
        'version: 0.6.39-project-authored-html',
        1,
    )
    canonical = canonical.replace(
        'version: 0.6.37-commercial-operator-density',
        'version: 0.6.39-project-authored-html',
        1,
    )
    canonical = _inject(canonical, PROJECT_AUTHORITY)
    canonical_path.write_text(canonical, encoding='utf-8')


def build(output_dir: Path) -> dict:
    base.DEFAULT_PROMPTS = [
        PROJECT_DEFAULT_PROMPT,
        v0638.HOST_DEFAULT_PROMPT,
        v0637.INTEGRATED_DEFAULT_PROMPT,
    ] + [
        p for p in base.DEFAULT_PROMPTS
        if p not in {PROJECT_DEFAULT_PROMPT, v0638.HOST_DEFAULT_PROMPT, v0637.INTEGRATED_DEFAULT_PROMPT}
    ]
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    release = base.build(output_dir)
    manifest_path = output_dir / 'release_manifest.json'
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    data['release'] = 'Project-Authored Human HTML + Commercial Operator Density'
    data['authority_version'] = '0.6.39-project-authored-html'
    data.setdefault('delivery_contract', {}).update({
        'project_authored_html_information_architecture': True,
        'project_object_map_first_screen': True,
        'fixed_capability_sidebar_forbidden': True,
        'next_action_separate_from_information_architecture': True,
        'asset_phase_rail_forbidden': True,
        'numbered_reading_order_default_forbidden': True,
        'operator_board_primary_injection_forbidden': True,
        'runtime_capability_proof_primary_section_forbidden': True,
        'commercial_depth_preserved_from_v0637': True,
    })
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.39 project-authored HTML release archives.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
