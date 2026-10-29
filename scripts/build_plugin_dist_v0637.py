#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import build_plugin_dist as base

ROOT = Path(__file__).resolve().parents[1]

INTEGRATED_DEFAULT_PROMPT = (
    'v0.6.37 最高权威：默认把商业视觉作为一体化最终成图问题处理。商品、目标市场可见文案、排版、场景、人物、道具、证据、摄影、灯光、CMF/材质与 finishing 可由当前模型在同一资产中共同生成；是否出现商品/文字由逐资产购买决策与策展决定，不做全局强制。POST_COMPOSITE / EXACT_PIXEL_COMPOSITE / NO_VISIBLE_COPY 仅在用户明确锁定、Product Truth/Claim/Compliance/平台硬规则、明确专业路线或真实 Provider 限制时使用。正常创意与生产选择由 Agent 自主闭合，不转成运营门禁。每个可生产资产必须具有商业级 Prompt 密度、真实输出 QA、最小修复路由，并进入中文优先运营执行台。'
)

WRAPPER_AUTHORITY = r'''
## Autonomous Integrated Render + Operator Density Authority — highest current precedence
- 默认以**一体化最终商业成图**为目标：商品、目标市场可见文案、排版、场景、人物、道具、证据、摄影、灯光、CMF/材质与 finishing 可在同一模型生成任务中共同完成。
- 商品是否出现、文字是否出现、采用 `MODEL_RENDER / HYBRID / POST_COMPOSITE / NO_VISIBLE_COPY` 哪条路线，均由 Agent 按逐资产购买决策、Surface、平台规则与真实 Provider 能力决定；不得把“无商品”“无文字”“后期合成”做成全局默认。
- 只有用户明确锁定、Product Truth / Claim / Compliance / 平台硬规则、明确选择 exact-pixel/post-composite 专业路线，或真实 Provider 限制，才形成相应约束。
- 商业 Prompt 必须达到可直接生产的 briefing 密度：Commerce objective、visual thesis、product/reference role、decisive scene、composition geometry、visible-copy typography、evidence、camera/optics、lighting、CMF/material response、color system、human/culture execution、platform behavior、finishing、truth boundary、variant hypothesis；只保留与当前资产相关的项。
- Provider 返回成功不等于商业完成。必须检查真实输出像素/帧：首扫购买答案、商品身份、文字准确度与层级、构图裁切、材质物理、人物/手部完整性、证据真实性、伪影、平台可用性及与相邻资产的差异；失败时走最小修复而不是整套重做。
- Video 不使用固定五段模板；由 shopper tension / decision job 动态作者化 narrative、first frame、shot choreography、copy/subtitle/VO、motion、sound、evidence、variants 与 cover。
- 七大工具按相关性激活，每个工具最终必须落成运营可执行对象。中文优先 `运营执行台` 是业务主界面；Runtime/Consumer/hash/status 仅作为次级 Inspector。
- 完整权威、Prompt 体系与运行时实现位于 `resources/SKILL.md`、`resources/prompts/` 与 `resources/runtime/cbcc/`。
'''.strip()

_orig_skill_wrapper = base.skill_wrapper


def skill_wrapper(version: str) -> str:
    text = _orig_skill_wrapper(version)
    marker = f'# Cross-Border Commerce Creative v{version}\n'
    if WRAPPER_AUTHORITY in text:
        return text
    return text.replace(marker, marker + '\n' + WRAPPER_AUTHORITY + '\n\n', 1)


def build(output_dir: Path) -> dict:
    base.DEFAULT_PROMPTS = [INTEGRATED_DEFAULT_PROMPT] + [
        p for p in base.DEFAULT_PROMPTS if p != INTEGRATED_DEFAULT_PROMPT
    ]
    base.skill_wrapper = skill_wrapper
    release = base.build(output_dir)
    manifest_path = output_dir / 'release_manifest.json'
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    data['release'] = 'Commercial Operator Density + Autonomous Integrated Render'
    data['authority_version'] = '0.6.37-commercial-operator-density'
    data.setdefault('delivery_contract', {}).update({
        'autonomous_integrated_render_default': True,
        'product_presence_is_per_asset_decision': True,
        'copy_render_route_is_per_asset_decision': True,
        'post_composite_is_exception_not_global_default': True,
        'actual_output_visual_qa_required': True,
        'operator_execution_board_primary': True,
        'commercial_prompt_density_guard_required': True,
        'fixed_five_beat_video_template_forbidden': True,
    })
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.37 installable Plugin and Skill archives.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
