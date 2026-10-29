#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0637 as v0637

ROOT = Path(__file__).resolve().parents[1]

HOST_ANTI_REGRESSION = r'''
## Host-Native FULL Delivery Anti-Regression Authority — highest current precedence
- **Skills-only / Host-native 是一等生产路径。** Runtime/MCP 不可用时，宿主 Agent 仍必须完成同等商业推理、创意作者化和人类交付深度；不得把 FULL 项目缩成短 dashboard、摘要卡、自定义 mini-report 或“先看目录里的正文”。
- **运营执行台是入口，不是替代品。** DO NOW / release status 可以放在首页，但必须能进入/展开完整 Strategy、Listing、Visual、Video、Economics、Ads、Review、Evidence 等当前相关对象。状态徽章不等于内容完成。
- **Workspace 按项目对象动态作者化。** 禁止固定 `总控台/产品真源/Listing/市场策略/视觉资产/视频/合规/研究证据` 八页壳、固定 7/8/9 页、固定 01→02→03 流程，或所有领域共用同一张 card-grid 模板。九域是 FULL 决策深度合同，不是导航模板。
- **逐资产完整深度必须直接可见。** FULL 主界面内，每个激活图片/视频资产都能查看 shopper job、creative thesis、product role、decisive moment、subject/action/environment/props/evidence、composition/spatial geometry、scale/depth/occupancy/focal path/negative space、copy hierarchy、CMF/material/color、相关 camera/light/human、surface/output、Model Prompt CN、Model Prompt EN、Visible Copy Block、Production/Assembly Notes、QA/repair 与 portfolio delta。不能只显示 Product Role / Copy / Render Route 再把正文藏到文件夹。
- **禁止为了填 UI 编造数字。** 没有显式经济输入/证据时，不得凭空写 RM/USD/AED 价格档、预算、ROAS、费率、CVR、佣金或利润假设；缺值保持 `MISSING_INPUT`。市场价格带可以形成测试假设，但不会自动成为批准价格。
- **视频/视觉不能退回单一模板。** 视觉资产由逐资产购买决策与策展决定；Video 展示动态 narrative/variant/shot universe，不把一个固定 first frame + 一条 16–18s choreography 当作完整视频策略。
- **Host 与 Runtime 交付同级。** 宿主原生生成的 HTML/Artifact 必须达到 canonical Runtime 的能力密度；不能因为“没有直接调用 Python runtime”而压缩策略、Prompt、Design Card 或运营对象。
'''.strip()

HOST_DEFAULT_PROMPT = (
    'v0.6.38 最高权威：Host-native/Skills-only 是一等生产路径。FULL 商品项目不得缩成固定导航、几张摘要卡、状态徽章或自定义短 dashboard；运营执行台只能做入口，不能替代九域决策深度、Listing 最终文案、完整 Visual/Video 策展、逐资产 Design Card、Model Prompt CN/EN、Visible Copy Block、Production/Assembly Notes、Economics/Ads/Review/Evidence 等当前相关对象。一级信息架构按项目对象动态作者化，不固定页面数。不得为填 UI 凭空写价格、预算、ROAS、费率或 CVR。'
)

_orig_base_wrapper = base.skill_wrapper
_orig_copy_resources = base.copy_repo_resources


def _inject(text: str, section: str) -> str:
    if section in text:
        return text
    marker = text.find('\n# ')
    if marker == -1:
        return section + '\n\n' + text
    heading_end = text.find('\n', marker + 1)
    if heading_end == -1:
        return text + '\n\n' + section + '\n'
    return text[:heading_end+1] + '\n' + section + '\n\n' + text[heading_end+1:]


def skill_wrapper(version: str) -> str:
    text = _orig_base_wrapper(version)
    text = _inject(text, v0637.WRAPPER_AUTHORITY)
    text = _inject(text, HOST_ANTI_REGRESSION)
    return text


def copy_repo_resources(dest: Path) -> None:
    _orig_copy_resources(dest)
    canonical = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    canonical = canonical.replace(
        'version: 0.6.37-commercial-operator-density',
        'version: 0.6.38-host-delivery-regression-fix',
        1,
    )
    canonical = _inject(canonical, HOST_ANTI_REGRESSION)
    (dest / 'SKILL.md').write_text(canonical, encoding='utf-8')


def build(output_dir: Path) -> dict:
    base.DEFAULT_PROMPTS = [HOST_DEFAULT_PROMPT, v0637.INTEGRATED_DEFAULT_PROMPT] + [
        p for p in base.DEFAULT_PROMPTS
        if p not in {HOST_DEFAULT_PROMPT, v0637.INTEGRATED_DEFAULT_PROMPT}
    ]
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    release = base.build(output_dir)
    manifest_path = output_dir / 'release_manifest.json'
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    data['release'] = 'Host FULL Delivery Regression Fix + Commercial Operator Density'
    data['authority_version'] = '0.6.38-host-delivery-regression-fix'
    data.setdefault('delivery_contract', {}).update({
        'host_native_full_delivery_is_first_class': True,
        'fixed_global_dashboard_shell_forbidden': True,
        'operator_board_cannot_replace_full_objects': True,
        'complete_per_asset_human_design_card_required': True,
        'per_asset_four_way_production_objects_visible_in_html': True,
        'unsupported_numeric_ui_fill_forbidden': True,
        'packaged_host_skill_density_guard_required': True,
        'packaged_canonical_skill_parity_guard_required': True,
    })
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.38 installable Plugin and Skill archives.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
