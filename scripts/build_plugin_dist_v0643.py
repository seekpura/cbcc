#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import build_plugin_dist as base
from scripts import build_plugin_dist_v0637 as v0637
from scripts import build_plugin_dist_v0642 as v0642

ROOT = Path(__file__).resolve().parents[1]

CHINESE_INTERPRETATION_AUTHORITY = (ROOT / 'prompts/global_chinese_interpretation_authority.md').read_text(encoding='utf-8').strip()

DEFAULT_PROMPT = (
    'v0.6.43 最高权威：所有面向运营人员的人类交付内容以中文为基础语言。凡目标市场外文内容，只要出现在正式人类工作区，就必须保留外文原文，并在同一对象提供中文释义/用途；覆盖上架类目/分类、标题、卖点、描述、属性、变体、搜索词、FAQ、平台字段值，资产 Visible Copy，视频 Hook/屏显/字幕/VO/CTA，广告 Hook/Headline/Primary Text/CTA，评论/客服/退货原话，以及研究/竞品外文摘录。description/category/attributes 等原始平台 key 只作次级技术标识，主要人类字段名必须中文。搜索词可给中文搜索意图解释。SKU/GTIN/URL/HEX/INCI/型号/HS Code/品牌专名保留原值，但字段名称与用途仍中文。`待补中文释义` 不是 FULL 完成态；Agent 必须先补齐，Runtime 审计缺失项并 BLOCK，禁止用机器翻译硬凑 Gate。'
)

_prev_wrapper = v0642.skill_wrapper
_prev_copy = v0642.copy_repo_resources


def skill_wrapper(version: str) -> str:
    text = _prev_wrapper(version)
    return v0642._inject(text, CHINESE_INTERPRETATION_AUTHORITY)


def copy_repo_resources(dest: Path) -> None:
    _prev_copy(dest)
    canonical_path = dest / 'SKILL.md'
    canonical = canonical_path.read_text(encoding='utf-8')
    canonical = canonical.replace('version: 0.6.42-regression-recovery', 'version: 0.6.43-global-chinese-interpretation', 1)
    canonical = v0642._inject(canonical, CHINESE_INTERPRETATION_AUTHORITY)
    canonical_path.write_text(canonical, encoding='utf-8')


def build(output_dir: Path) -> dict:
    base.DEFAULT_PROMPTS = [DEFAULT_PROMPT, v0642.DEFAULT_PROMPT, v0637.INTEGRATED_DEFAULT_PROMPT] + [
        p for p in base.DEFAULT_PROMPTS if p not in {DEFAULT_PROMPT, v0642.DEFAULT_PROMPT, v0637.INTEGRATED_DEFAULT_PROMPT}
    ]
    base.skill_wrapper = skill_wrapper
    base.copy_repo_resources = copy_repo_resources
    base.build(output_dir)

    manifest_path = output_dir / 'release_manifest.json'
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    data['release'] = 'v0.6.43 Global Chinese Interpretation'
    data['authority_version'] = '0.6.43-global-chinese-interpretation'
    data.setdefault('delivery_contract', {}).update({
        'all_human_foreign_content_requires_chinese_interpretation': True,
        'listing_category_description_attributes_search_faq_bilingual': True,
        'asset_visible_copy_bilingual': True,
        'video_creator_copy_bilingual': True,
        'advertising_copy_bilingual': True,
        'review_customer_voice_bilingual': True,
        'research_foreign_excerpt_bilingual': True,
        'raw_platform_keys_secondary_to_chinese_labels': True,
        'technical_identifiers_keep_exact_value': True,
        'pending_chinese_interpretation_blocks_full_completion': True,
        'runtime_does_not_invent_machine_translation': True,
    })
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC v0.6.43 global Chinese interpretation release.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
