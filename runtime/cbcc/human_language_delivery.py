from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
import json
import re


_COMMON_FIELD_LABELS = {
    'title': '产品标题',
    'product_title': '产品标题',
    'product_name': '商品名称',
    'name': '名称',
    'brand': '品牌',
    'seller_sku': '商家 SKU',
    'sku': 'SKU',
    'parent_sku': '父 SKU',
    'variation_sku': '变体 SKU',
    'variant': '变体',
    'variation': '变体',
    'category': '平台类目',
    'category_name': '平台类目名称',
    'category_id': '平台类目 ID',
    'category_path': '平台类目路径',
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
    'net_content': '净含量',
    'size': '规格 / 容量',
    'weight': '重量',
    'dimensions': '尺寸',
    'price': '价格',
    'sale_price': '销售价',
    'msrp': '建议零售价',
    'offer': '优惠 / Offer',
    'shipping': '物流承诺',
    'returns': '退换货 / 售后',
    'seller_info': '卖家 / 责任方信息',
    'manufacturer': '制造商',
    'manufacturer_name': '制造商名称',
    'responsible_party': '责任方',
    'country_of_origin': '原产国',
    'origin_country': '原产国',
    'country': '国家 / 地区',
    'gtin': 'GTIN 商品条码',
    'ean': 'EAN 商品条码',
    'upc': 'UPC 商品条码',
    'barcode': '商品条码',
    'hs_code': 'HS 编码',
    'dangerous_goods': '危险品属性',
    'hazmat': '危险品属性',
    'warranty': '保修 / 质保',
    'condition': '商品状态',
    'inventory': '库存',
    'stock': '库存',
    'quantity': '数量',
    'color': '颜色',
    'material': '材质',
    'model': '型号',
    'model_number': '型号',
    'part_number': '部件编号',
    'tax_code': '税务编码',
    'vat': '增值税 / VAT',
}

_TOKEN_ZH = {
    'product': '商品', 'item': '商品', 'seller': '商家', 'merchant': '商家', 'title': '标题', 'name': '名称',
    'brand': '品牌', 'sku': 'SKU', 'parent': '父级', 'child': '子级', 'variation': '变体', 'variant': '变体',
    'category': '类目', 'type': '类型', 'id': 'ID', 'path': '路径', 'attribute': '属性', 'attributes': '属性',
    'description': '描述', 'short': '简短', 'long': '完整', 'search': '搜索', 'term': '词', 'terms': '词', 'keyword': '关键词', 'keywords': '关键词',
    'country': '国家', 'origin': '原产地', 'manufacturer': '制造商', 'responsible': '责任', 'party': '方',
    'price': '价格', 'sale': '销售', 'retail': '零售', 'shipping': '物流', 'return': '退换', 'returns': '退换',
    'warning': '警示', 'warnings': '警示', 'ingredient': '成分', 'ingredients': '成分', 'usage': '使用方法', 'direction': '使用方法', 'directions': '使用方法',
    'size': '规格', 'weight': '重量', 'dimension': '尺寸', 'dimensions': '尺寸', 'color': '颜色', 'material': '材质',
    'model': '型号', 'number': '编号', 'part': '部件', 'quantity': '数量', 'stock': '库存', 'inventory': '库存',
    'barcode': '条码', 'code': '编码', 'tax': '税务', 'warranty': '质保', 'condition': '商品状态', 'goods': '商品', 'dangerous': '危险品',
}

_IDENTIFIER_FIELDS = {
    'brand', 'sku', 'seller_sku', 'parent_sku', 'variation_sku', 'category_id', 'gtin', 'ean', 'upc', 'barcode',
    'hs_code', 'model_number', 'part_number', 'tax_code', 'url', 'uri', 'asin', 'id',
}

_COMPANION_KEYS = {
    'delivery_translation', 'delivery_note', 'zh', 'zh-cn', 'zh_cn', 'chinese', 'cn', '中文', '中文释义', '中文说明',
}

_METADATA_KEYS = {
    'locale', 'language', 'delivery_locale', 'asset_id', 'surface', 'role', 'status', 'source', 'source_id', 'source_ids',
    'claim_id', 'claim_ids', 'sku', 'brand', 'url', 'uri', 'path', 'file', 'filename', 'mime', 'hex', 'id',
}


def _has_cjk(value: Any) -> bool:
    return bool(re.search(r'[\u3400-\u9fff]', str(value or '')))


def _contains_letters(value: Any) -> bool:
    text = str(value or '')
    return bool(re.search(r'[A-Za-z\u00C0-\u024F\u0600-\u06FF\u0750-\u077F\u0E00-\u0E7F]', text))


def _looks_machineish(value: Any) -> bool:
    text = str(value or '').strip()
    if not text:
        return True
    if re.fullmatch(r'https?://\S+|www\.\S+', text, re.I):
        return True
    if re.fullmatch(r'#[0-9a-fA-F]{3,8}', text):
        return True
    if re.fullmatch(r'[A-Z0-9_.:/+\-]{2,}', text) and ' ' not in text:
        return True
    if re.fullmatch(r'[\d\s.,%+\-/×x]+(?:mm|cm|m|ml|l|g|kg|oz|fl\.\s*oz|px|dpi|fps|hz)?', text, re.I):
        return True
    return False


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return ' | '.join(f'{k}: {_flatten_text(v)}' for k, v in value.items())
    if isinstance(value, (list, tuple, set)):
        return ' | '.join(_flatten_text(v) for v in value)
    return '' if value is None else str(value)


def _needs_cn_companion(value: Any, field: str | None = None) -> bool:
    if value in (None, '', [], {}):
        return False
    if field and str(field).casefold() in _IDENTIFIER_FIELDS:
        return False
    text = _flatten_text(value).strip()
    if not text or _has_cjk(text) or _looks_machineish(text):
        return False
    return _contains_letters(text)


def _semantic_field_label(field: Any, existing: Any = None, explicit_zh: Any = None) -> tuple[str, bool]:
    raw = str(field or '').strip()
    if explicit_zh and _has_cjk(explicit_zh):
        return str(explicit_zh).strip(), True
    if existing and _has_cjk(existing):
        return str(existing).strip(), True
    key = raw.casefold().strip()
    if key in _COMMON_FIELD_LABELS:
        return _COMMON_FIELD_LABELS[key], True
    normalized = re.sub(r'(?<!^)(?=[A-Z])', '_', raw).casefold()
    tokens = [x for x in re.split(r'[^a-z0-9]+', normalized) if x]
    if tokens and all(t in _TOKEN_ZH or t.isdigit() for t in tokens):
        label = ''.join(_TOKEN_ZH.get(t, t) for t in tokens)
        return label or f'平台字段（原字段：{raw}）', bool(label)
    return f'平台字段（原字段：{raw or "未命名"}）', False


def _identifier_explanation(field: str, value: Any) -> str:
    key = str(field or '').casefold()
    mapping = {
        'brand': '品牌专名，保留官方写法。',
        'sku': 'SKU 为商品库存管理标识，保留平台 / 商家原始写法。',
        'seller_sku': '商家 SKU 为库存管理标识，保留商家原始写法。',
        'parent_sku': '父 SKU 为变体关系标识，保留原始写法。',
        'variation_sku': '变体 SKU 为具体变体标识，保留原始写法。',
        'category_id': '平台类目 ID，属于技术标识，保留原值。',
        'gtin': 'GTIN 为全球商品贸易项目代码，保留原值。',
        'ean': 'EAN 为商品条码标识，保留原值。',
        'upc': 'UPC 为商品条码标识，保留原值。',
        'barcode': '商品条码标识，保留原值。',
        'hs_code': 'HS 编码为海关商品分类编码，保留原值并按目的国 / 地区要求复核。',
        'model_number': '商品型号标识，保留官方原值。',
        'part_number': '部件编号标识，保留官方原值。',
        'tax_code': '税务 / 平台编码，保留平台要求的原值。',
    }
    return mapping.get(key, f'这是平台 / 商品技术标识，保留原值：{value}。')


def normalize_upload_center(center: dict[str, Any]) -> dict[str, Any]:
    """Make the human layer Chinese-first without changing target-market copy.

    Platform/raw field identifiers remain available as secondary metadata. Human-facing labels are
    Chinese. Foreign target copy is never machine-translated here; instead the existing Chinese
    companion is preserved and missing companions are made explicit so the delivery audit can block
    incomplete FULL output rather than silently shipping untranslated foreign copy.
    """
    out = deepcopy(center or {})
    rows = out.get('copy_center') or []
    row_map: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        field = str(row.get('field') or '')
        label, semantic = _semantic_field_label(field, row.get('label'), row.get('delivery_label_zh'))
        row['field_raw'] = field
        row['label'] = label
        row['label_zh_semantic'] = semantic
        if field.casefold() in _IDENTIFIER_FIELDS and row.get('value') not in (None, '', [], {}) and not _has_cjk(row.get('delivery_translation')):
            row['delivery_translation'] = _identifier_explanation(field, row.get('value'))
            row['delivery_companion_status'] = 'TECHNICAL_IDENTIFIER_EXPLAINED_CN'
        elif _needs_cn_companion(row.get('value'), field) and not _has_cjk(row.get('delivery_translation')):
            row['delivery_companion_status'] = '待补中文释义'
        elif row.get('value') not in (None, '', [], {}) and _has_cjk(row.get('value')):
            row['delivery_companion_status'] = row.get('delivery_companion_status') or 'DELIVERY_LOCALE_CONTENT'
        row_map[field] = row

    localized = out.get('localized_copy') or []
    localized_map: dict[str, dict[str, Any]] = {}
    for row in localized:
        if isinstance(row, dict) and row.get('field'):
            localized_map[str(row.get('field'))] = row

    for row in out.get('preserved_listing_fields') or []:
        if not isinstance(row, dict):
            continue
        field = str(row.get('field') or '')
        label, semantic = _semantic_field_label(field, row.get('label'), row.get('delivery_label_zh'))
        row['field_raw'] = field
        row['label'] = label
        row['label_zh_semantic'] = semantic
        source = row_map.get(field) or localized_map.get(field) or {}
        if source.get('delivery_translation') not in (None, ''):
            row['delivery_translation'] = source.get('delivery_translation')
        elif field.casefold() in _IDENTIFIER_FIELDS and row.get('value') not in (None, '', [], {}):
            row['delivery_translation'] = _identifier_explanation(field, row.get('value'))
        if source.get('delivery_note') not in (None, ''):
            row['delivery_note'] = source.get('delivery_note')

    lang = out.setdefault('delivery_language', {})
    lang.setdefault('locale', ((out.get('target') or {}).get('delivery_locale') or 'zh-CN'))
    lang['default_rule'] = '人类交付以中文为基础语言；用户明确要求其他交付语言时覆盖。'
    lang['foreign_copy_rule'] = '所有目标市场外文可见内容必须在同一对象提供中文释义 / 用途；平台原始字段名、技术 ID、品牌和 SKU 只能作为次级标识存在。'
    return out


def _copy_leaf_paths(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], str]]:
    out: list[tuple[tuple[str, ...], str]] = []
    if isinstance(value, dict):
        for key, val in value.items():
            skey = str(key)
            low = skey.casefold()
            if low in _COMPANION_KEYS or low in _METADATA_KEYS or low.endswith(('_zh', '_cn', '_zh_cn', '_zh-cn', '_delivery_translation')):
                continue
            out.extend(_copy_leaf_paths(val, path + (skey,)))
        return out
    if isinstance(value, (list, tuple)):
        for idx, val in enumerate(value):
            out.extend(_copy_leaf_paths(val, path + (str(idx),)))
        return out
    if _needs_cn_companion(value):
        out.append((path, str(value)))
    return out


def _dig(value: Any, path: tuple[str, ...]) -> Any:
    cur = value
    for part in path:
        if isinstance(cur, dict):
            if part not in cur:
                return None
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return None
    return cur


def _asset_copy_has_companion(visible_copy: Any, path: tuple[str, ...], foreign_count: int) -> bool:
    if not isinstance(visible_copy, dict):
        return False
    last = path[-1] if path else ''
    for sibling in (f'{last}_zh', f'{last}_cn', f'{last}_zh_cn', f'{last}_delivery_translation'):
        if sibling in visible_copy and _has_cjk(visible_copy.get(sibling)):
            return True
    for key in ('delivery_translation', 'zh', 'zh-CN', 'zh_cn', 'chinese', 'cn', '中文释义'):
        comp = visible_copy.get(key)
        if comp in (None, '', [], {}):
            continue
        if isinstance(comp, str):
            if foreign_count == 1 and _has_cjk(comp):
                return True
        elif isinstance(comp, dict):
            candidates = [path, (last,), tuple(str(x) for x in path if not str(x).isdigit())]
            for candidate in candidates:
                val = _dig(comp, candidate)
                if _has_cjk(val):
                    return True
            if last in comp and _has_cjk(comp.get(last)):
                return True
    return False


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def audit_human_language_delivery(package_dir: Path, center: dict[str, Any]) -> dict[str, Any]:
    """Audit only human-facing objects that are actually delivered.

    Machine JSON/archive may keep raw foreign identifiers. Human UI labels must be Chinese-first;
    foreign target-market copy must carry a Chinese companion in the same business object; English
    execution prompts must have a Chinese canonical prompt beside them.
    """
    package = Path(package_dir)
    issues: list[dict[str, Any]] = []
    listing_active = bool(((center or {}).get('task_scope') or {}).get('listing_active'))

    if listing_active:
        for row in (center or {}).get('copy_center') or []:
            if not isinstance(row, dict):
                continue
            field = str(row.get('field') or '')
            label = str(row.get('label') or '')
            if not _has_cjk(label):
                issues.append({'scope': 'LISTING', 'field': field, 'code': 'LISTING_FIELD_TITLE_NOT_CHINESE_BASE', 'value': label})
            if not bool(row.get('label_zh_semantic', True)):
                issues.append({'scope': 'LISTING', 'field': field, 'code': 'LISTING_FIELD_TITLE_CN_SEMANTIC_MISSING', 'value': label})
            if _needs_cn_companion(row.get('value'), field) and not _has_cjk(row.get('delivery_translation')):
                issues.append({'scope': 'LISTING', 'field': field, 'code': 'FOREIGN_LISTING_COPY_WITHOUT_CN_COMPANION', 'value': _flatten_text(row.get('value'))[:240]})

    asset_issues: list[dict[str, Any]] = []
    asset_root = package / 'asset_packages'
    if asset_root.exists():
        for asset_dir in sorted(p for p in asset_root.iterdir() if p.is_dir()):
            asset_id = asset_dir.name
            layout = _read_json(asset_dir / '04_layout_contract.json')
            visible = layout.get('visible_copy')
            foreign = _copy_leaf_paths(visible)
            for path, text in foreign:
                if not _asset_copy_has_companion(visible, path, len(foreign)):
                    asset_issues.append({
                        'scope': 'ASSET_VISIBLE_COPY',
                        'asset_id': asset_id,
                        'path': '.'.join(path) or '<root>',
                        'code': 'FOREIGN_ASSET_COPY_WITHOUT_CN_COMPANION',
                        'value': text[:240],
                    })
            prompt_en = asset_dir / '06_prompt_EN.txt'
            prompt_cn = asset_dir / '05_prompt_CN.txt'
            if prompt_en.exists() and prompt_en.read_text(encoding='utf-8', errors='replace').strip():
                if not prompt_cn.exists() or not _has_cjk(prompt_cn.read_text(encoding='utf-8', errors='replace')):
                    asset_issues.append({'scope': 'ASSET_PROMPT', 'asset_id': asset_id, 'code': 'EN_PROMPT_WITHOUT_CN_CANONICAL_PROMPT'})
            human_card = asset_dir / '00_HUMAN_DESIGN_CARD_CN.md'
            if not human_card.exists() or not _has_cjk(human_card.read_text(encoding='utf-8', errors='replace')):
                asset_issues.append({'scope': 'ASSET_HUMAN_CARD', 'asset_id': asset_id, 'code': 'ASSET_CHINESE_HUMAN_CARD_MISSING'})

    issues.extend(asset_issues)
    status = 'PASS' if not issues else 'INCOMPLETE'
    return {
        'status': status,
        'delivery_locale': (((center or {}).get('delivery_language') or {}).get('locale') or 'zh-CN'),
        'rules': {
            'human_base_language': '中文为基础人类交付语言；用户明确要求其他交付语言时覆盖。',
            'foreign_copy_companion': '目标市场英文 / 马来文 / 阿语等外文内容必须在同一对象提供中文释义 / 用途。',
            'listing_field_titles': 'Listing 人类字段标题必须中文在前；平台原始字段 key 仅作为次级技术标识。',
            'asset_visible_copy': '资产目标市场可见文案保留目标语言，同时逐项提供中文释义；资产中文设计卡不可缺失。',
            'prompt_pair': '英文 / 目标模型 Prompt 不能成为唯一生产说明；必须存在中文 Canonical Prompt。',
            'technical_identifier_exception': '品牌、SKU、GTIN、类目 ID、URL、HEX 等可保留原文 / 原值，但必须有中文字段标题或用途说明。',
        },
        'listing': {
            'active': listing_active,
            'status': 'PASS' if not any(x.get('scope') == 'LISTING' for x in issues) else 'INCOMPLETE',
            'issue_count': sum(1 for x in issues if x.get('scope') == 'LISTING'),
        },
        'assets': {
            'status': 'PASS' if not asset_issues else 'INCOMPLETE',
            'asset_root_present': asset_root.exists(),
            'issue_count': len(asset_issues),
        },
        'issues': issues,
    }
