#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0637 as v0637

ROOT = Path(__file__).resolve().parents[1]

RECOVERY_AUTHORITY = r'''
## v0.6.42 Regression Recovery Authority — highest current precedence
- **升级只能做加法。** v0.6.36 的成熟人类工作区交互是最低底座：FULL / 高密度项目使用真实对象路由，一次只显示一个一级工作面；保留局部 subview/lens、独立 asset/<id> 详情、搜索、复制、响应式导航和打印/PDF 投影。不得把 FULL 项目全部摊成一个纵向长页面，不得再用全局 post-processor 重写/抹掉这套交互。
- **Project-authored 不等于拆交互。** 动态的是当前项目真实对象、名称、顺序、分组、局部结构、视觉主题和信息密度；不存在的对象不显示，页数不固定。但稳定 route/subview/asset-detail/search/copy floor 不得因为“去流水线”被删除。
- **平台槽位绝不是 Asset Universe 上限。** `max_images=9/7`、`max_videos=1` 只约束同时上线 Live / Activation Set。候选 Asset Universe 由购买决策、Surface、创意假设、测试和运营需求决定，可超过 9/7；多 Hero H01/H02/H03、多 Benefit/Proof、多 Paid Ads、PDP/A+/Detail/Longform、Store/Banner、Social/Creator/UGC、Short Video/Live、Test Pool、Rotation Pool 必须按独立商业/创意假设保留。绝不把“最多9图”解释成“只策划/生产9个资产”。
- **运营升级是加法。** v0.6.37+ Operator Execution / Commercial Brain 是有真实对象时出现的新增可切换工作面，不能注入成整页之前的巨型 section，也不能替代 Strategy、Listing、Visual/Video、Assets、Economics、Ads、Review、Evidence。
- **FULL 深度保持。** 九域仍是决策深度合同，不是固定页面模板；七大能力持续一等：Market Research；Product Strategy（SKU/Pricing/Economics/Offer）；Listing Creative；Product Image；Product Video；Advertising Optimization；Review Analysis。
- **逐资产完整生产对象。** 激活资产在人类 HTML 内直接可进入完整 Design Card / shopper job / creative thesis / Product Role / decisive moment / scene-action-props-evidence / composition-spatial geometry / scale-depth-occupancy-focal path-negative space / Visible Copy + 中文释义 / CMF-material / 相关 Camera-Lighting-Human / Surface-Output / Model Prompt CN / Model Prompt EN / Production-Assembly Notes / Truth-Claim-Reference / actual-output QA / smallest repair / portfolio delta。摘要只能做入口。
- **商业视觉默认一体成图。** 商品、目标市场文字、排版、场景、人物、道具、证据、摄影、灯光、CMF/材质与 finishing 可共同生成；商品/文字是否出现及路线由逐资产购买决策与策展决定。真实商品可见时默认强 Reference Input + native final render；EXACT_PIXEL_COMPOSITE 仅用于明确原像素层锁定。
- **禁止伪多样性。** Agent 是 Portfolio Curator + Creative Director + Per-Asset Art Director；不能用左右互换、统一暖白底、固定产品位置、同一卡片或固定五段视频冒充策展。
- **数字完整性。** 不得为填 UI 编造价格、预算、ROAS、CVR、费率、佣金、成本、销量、认证或排名；缺失经济输入保持 MISSING_INPUT。
- **Host / Canonical 必须同权威。** 安装包 Host Skill 与 resources/SKILL.md 必须同时包含本节、Asset Universe activation-only、多 Hero、七工具、FULL 深度、逐资产四类生产对象与 v0.6.36 interaction floor；版本必须与 manifest 一致。
'''.strip()

DEFAULT_PROMPT = (
    'v0.6.42 最高权威：升级只能做加法。恢复 v0.6.36 的正常交互底座——FULL 项目按当前真实对象做可切换 route，一次只显示一个一级工作面，保留模块 subview、独立资产详情、搜索、复制、响应式与打印；禁止把全部内容摊成一页。平台最多9图/7图/1视频仅限制同时上线 Live/Activation Set，绝不限制 Asset Universe；必须允许多 Hero、多卖点、多 Paid Ads、PDP/A+/Detail、Store/Banner、Social/Creator/UGC、Video、Test/Rotation 等独立变体。v0.6.37 的运营/商业深度作为新增工作面，不替代完整 Strategy/Listing/Visual/Video/Assets/Economics/Ads/Review/Evidence。'
)

_orig_wrapper = base.skill_wrapper
_orig_copy = base.copy_repo_resources


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
    text = _orig_wrapper(version)
    text = _inject(text, v0637.WRAPPER_AUTHORITY)
    text = _inject(text, RECOVERY_AUTHORITY)
    return text


def copy_repo_resources(dest: Path) -> None:
    _orig_copy(dest)
    canonical = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    for old in (
        'version: 0.6.37-commercial-operator-density',
        'version: 0.6.39-project-authored-html',
        'version: 0.6.41-project-authored-saas-workspace',
    ):
        canonical = canonical.replace(old, 'version: 0.6.42-regression-recovery', 1)
    canonical = _inject(canonical, RECOVERY_AUTHORITY)
    (dest / 'SKILL.md').write_text(canonical, encoding='utf-8')


def build(output_dir: Path) -> dict:
    base.DEFAULT_PROMPTS = [DEFAULT_PROMPT, v0637.INTEGRATED_DEFAULT_PROMPT] + [
        p for p in base.DEFAULT_PROMPTS if p not in {DEFAULT_PROMPT, v0637.INTEGRATED_DEFAULT_PROMPT}
    ]
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    manifest = base.build(output_dir)
    manifest_path = output_dir / 'release_manifest.json'
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    data['release'] = 'v0.6.42 Regression Recovery — v0.6.36 Interaction + v0.6.37 Commercial Depth'
    data['authority_version'] = '0.6.42-regression-recovery'
    data.setdefault('delivery_contract', {}).update({
        'v036_routed_interaction_floor_preserved': True,
        'single_active_primary_work_surface': True,
        'asset_detail_routes_preserved': True,
        'search_copy_responsive_print_preserved': True,
        'project_authored_global_postprocessor_disabled': True,
        'operator_execution_is_additive_route': True,
        'asset_universe_not_capped_by_platform_slots': True,
        'multi_hero_and_paid_pdp_social_video_variants_preserved': True,
        'commercial_depth_preserved_from_v0637': True,
        'host_canonical_authority_parity_required': True,
    })
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.42 regression-recovery plugin and skill archives.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
