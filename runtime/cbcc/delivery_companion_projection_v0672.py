from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Mapping


def _meaningful(value: Any) -> bool:
    return value not in (None, '', [], {})


def _norm_locale(value: Any) -> str:
    return str(value or '').strip().lower().replace('_', '-')


def _locale_matches(actual: Any, required: Any) -> bool:
    a = _norm_locale(actual)
    r = _norm_locale(required)
    if not a or not r:
        return False
    if a == r:
        return True
    zh_aliases = {'zh', 'zh-cn', 'zh-hans', 'cn'}
    if r in zh_aliases and a in zh_aliases:
        return True
    if r.startswith('en') and a.startswith('en'):
        return True
    return a.split('-', 1)[0] == r.split('-', 1)[0]


def _delivery_payload(localized_copy: Mapping[str, Any], delivery_locale: str) -> dict[str, Any]:
    for locale, payload in localized_copy.items():
        if _locale_matches(locale, delivery_locale) and isinstance(payload, Mapping):
            return dict(payload)
    return {}


def apply_authored_delivery_locale_companions(result: Mapping[str, Any], language_contract: Mapping[str, Any] | None, localized_copy: Mapping[str, Any] | None) -> dict[str, Any]:
    out = deepcopy(dict(result))
    contract = language_contract or {}
    delivery_locale = str(contract.get('delivery_locale') or 'zh-CN')
    delivery = _delivery_payload(localized_copy or {}, delivery_locale)
    if not delivery:
        return out
    for package in out.get('packages') or []:
        if not isinstance(package, dict) or _locale_matches(package.get('locale'), delivery_locale):
            continue
        for row in package.get('fields') or []:
            if not isinstance(row, dict):
                continue
            field = str(row.get('field') or '')
            companion = delivery.get(field)
            if not field or not _meaningful(companion) or _meaningful(row.get('delivery_translation')):
                continue
            row['delivery_translation'] = deepcopy(companion)
            row['delivery_note'] = row.get('delivery_note') or f'直接复用已作者化 {delivery_locale} 同字段作为人类交付 companion；未执行机器翻译。'
            row['delivery_companion_status'] = 'READY_AUTHORED_DELIVERY_LOCALE_COPY'
    out['delivery_companion_projection_v0672'] = {
        'status': 'APPLIED',
        'delivery_locale': delivery_locale,
        'principle': 'Only authored delivery-locale copy is reused; missing companions remain unresolved.',
    }
    return out


def _visible_copy_companion_present(package_dir: Path, asset_id: str) -> bool:
    """Accept the canonical v0.6.70+ Visible Copy object's authored Chinese meaning.

    The mature 14_visible_copy_block shape keeps the exact target copy plus English baseline and
    Chinese meaning under `raw`. This helper only recognizes already-authored Chinese; it does not
    translate or infer missing copy.
    """
    from .global_chinese_interpretation import _read_json, _cn_value

    asset_dir = Path(package_dir) / 'asset_packages' / asset_id
    companion_keys = (
        'delivery_translation_zh', 'delivery_translation', 'chinese_interpretation',
        'chinese_meaning', 'zh', 'zh_cn', 'zh-CN', '中文释义', '中文说明',
    )
    for path in (asset_dir / '14_visible_copy_block.json', asset_dir / '04_layout_contract.json'):
        data = _read_json(path)
        candidates: list[Mapping[str, Any]] = []
        if isinstance(data, Mapping):
            candidates.append(data)
            for key in ('raw', 'visible_copy'):
                child = data.get(key)
                if isinstance(child, Mapping):
                    candidates.append(child)
                    nested = child.get('raw')
                    if isinstance(nested, Mapping):
                        candidates.append(nested)
        for obj in candidates:
            if any(_cn_value(obj.get(key)) for key in companion_keys):
                return True
    return False


def _wrap_video_creator_plan(fn: Callable[..., dict[str, Any]]):
    if getattr(fn, '_cbcc_v0672_video_human_companions', False):
        return fn

    def compiled(project_id, content_objects, shopper_questions, language_contract, video_jobs=None, *, assets=None, creative_council=None):
        result = fn(
            project_id,
            content_objects,
            shopper_questions,
            language_contract,
            video_jobs,
            assets=assets,
            creative_council=creative_council,
        )
        out = deepcopy(dict(result or {}))
        asset_rows = [dict(a) for a in (assets or []) if isinstance(a, Mapping)]
        jobs = [dict(j) for j in (video_jobs or []) if isinstance(j, Mapping)]
        for index, row in enumerate(out.get('assets') or []):
            if not isinstance(row, dict):
                continue
            source_id = str(row.get('source_asset_id') or '')
            source = next((a for a in asset_rows if str(a.get('asset_id') or '') == source_id), {})
            job = jobs[index] if index < len(jobs) else {}

            # An explicit custom hook only receives a Chinese companion when the job explicitly supplied it.
            # A hook inherited from the source shopper question may reuse that question's authored CN companion.
            hook_cn = job.get('hook_cn')
            if not _meaningful(hook_cn) and not _meaningful(job.get('hook')):
                hook_cn = (
                    job.get('shopper_question_cn')
                    or source.get('consumer_question_cn')
                    or source.get('shopper_question_cn')
                    or ((source.get('asset_art_direction') or {}).get('consumer_question_cn') if isinstance(source.get('asset_art_direction'), Mapping) else None)
                )
            if _meaningful(hook_cn):
                row['hook_cn'] = deepcopy(hook_cn)

            if _meaningful(job.get('cta_cn')):
                row['cta_cn'] = deepcopy(job.get('cta_cn'))

            creator = row.get('creator_contract')
            if isinstance(creator, dict):
                explicit_creator_cta = job.get('creator_cta') or job.get('cta')
                if explicit_creator_cta:
                    creator['cta'] = explicit_creator_cta
                    authored_cn = job.get('creator_cta_cn') or job.get('cta_cn')
                    if _meaningful(authored_cn):
                        creator['cta_cn'] = deepcopy(authored_cn)
                elif creator.get('cta') == 'native recommendation / shop action after proof':
                    creator['cta_cn'] = '在证据展示之后自然推荐 / 引导进入店铺操作'

        out['video_human_companion_projection_v0672'] = {
            'status': 'APPLIED',
            'principle': 'Authored Chinese hook/CTA companions are preserved; Runtime only bilingualizes its own fixed default Creator CTA.',
        }
        return out

    setattr(compiled, '_cbcc_v0672_video_human_companions', True)
    return compiled


def _install_global_language_closure() -> None:
    """Patch captured Runtime references without importing later bootstrap consumers early."""
    from .fresh_k01_runtime_closure_v0672 import install as install_fresh_k01_runtime_closure
    install_fresh_k01_runtime_closure()

    from . import global_chinese_interpretation as global_cn
    global_cn._asset_visible_copy_companion_present = _visible_copy_companion_present

    from . import video_creator as video_module
    wrapped = _wrap_video_creator_plan(video_module.build_video_creator_plan)
    video_module.build_video_creator_plan = wrapped

    # Some mature consumers import the function by value. Patch only modules already loaded.
    # Importing compiler here would freeze an intermediate Strategy builder before later wrappers install.
    import sys
    package = __package__ or 'cbcc'
    for module_name in (f'{package}.compiler', f'{package}.tools.seven_agent'):
        module = sys.modules.get(module_name)
        if module is not None:
            module.build_video_creator_plan = wrapped


def wrap_final_copy_release_workflow(fn: Callable[..., dict[str, Any]]):
    _install_global_language_closure()
    if getattr(fn, '_cbcc_v0672_delivery_companion_projection', False):
        return fn

    def compiled(fields, language_contract, localized_copy, *args, **kwargs):
        result = fn(fields, language_contract, localized_copy, *args, **kwargs)
        return apply_authored_delivery_locale_companions(result, language_contract, localized_copy)

    setattr(compiled, '_cbcc_v0672_delivery_companion_projection', True)
    return compiled
