from __future__ import annotations

import html
import re


_FIELD_LABELS_ZH = {
    'title': '产品标题',
    'product_title': '产品标题',
    'product_name': '商品名称',
    'brand': '品牌',
    'category': '平台类目',
    'platform_category': '平台类目',
    'category_name': '平台类目名称',
    'category_path': '平台类目路径',
    'category_id': '平台类目 ID',
    'product_type': '商品类型',
    'attributes': '商品属性',
    'attribute': '商品属性',
    'highlights': '核心卖点',
    'bullets': '卖点',
    'bullet_points': '卖点',
    'description': '商品描述',
    'short_description': '简短描述',
    'long_description': '完整描述',
    'search_terms': '搜索词',
    'backend_terms': '后台关键词',
    'keywords': '关键词',
    'usage': '使用方法',
    'directions': '使用方法',
    'ingredients': '成分',
    'warnings': '警示',
    'cautions': '注意事项',
    'faq': '常见问题',
    'package': '包装 / 包含物',
    'package_contents': '包装内含物',
    'variant': '变体',
    'variation': '变体',
    'color': '颜色',
    'size': '规格 / 容量',
    'material': '材质',
    'price': '价格',
    'offer': '优惠 / Offer',
    'shipping': '物流承诺',
    'returns': '退换货 / 售后',
    'seller_info': '卖家 / 责任方信息',
}


def apply_chinese_interpretation_ui(page: str) -> str:
    """Chinese-first labels in human localized-copy views; raw platform keys stay secondary."""
    pattern = re.compile(r'(<div class="locale-field"><strong>)([^<]+)(</strong>)')

    def repl(match: re.Match[str]) -> str:
        raw = html.unescape(match.group(2)).strip()
        label = _FIELD_LABELS_ZH.get(raw.casefold())
        if not label:
            return match.group(0)
        raw_key = html.escape(raw)
        return f'{match.group(1)}{html.escape(label)}<small class="heading-en">{raw_key}</small>{match.group(3)}'

    return pattern.sub(repl, page)
