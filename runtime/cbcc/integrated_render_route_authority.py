from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Mapping


def _meaningful(value: Any) -> bool:
    return value not in (None, '', [], {})


def _visible_copy(asset: Mapping[str, Any], bundle: Mapping[str, Any]) -> str:
    visible = asset.get('visible_copy')
    if isinstance(visible, Mapping):
        for key in ('target_copy', 'copy', 'text', 'headline', 'bm', 'ms', 'en'):
            if _meaningful(visible.get(key)):
                return str(visible.get(key))
    block = bundle.get('visible_copy_block')
    if isinstance(block, Mapping):
        for key in ('target_copy', 'copy', 'text', 'headline'):
            if _meaningful(block.get(key)):
                return str(block.get(key))
    return ''


def _copy_route(asset: Mapping[str, Any]) -> str:
    art = asset.get('asset_art_direction') if isinstance(asset.get('asset_art_direction'), Mapping) else {}
    route = str(art.get('copy_render_route') or asset.get('copy_render_route') or '').upper().strip()
    # Current authority: integrated final render is the normal route. Post-composite/no-visible-copy
    # remain explicit per-asset professional choices, not historical defaults.
    return route or 'MODEL_RENDER_INTEGRATED'


def _presence(asset: Mapping[str, Any]) -> str:
    presence = asset.get('product_presence')
    if isinstance(presence, Mapping):
        return str(presence.get('planning_state') or '').upper()
    art = asset.get('asset_art_direction') if isinstance(asset.get('asset_art_direction'), Mapping) else {}
    presence = art.get('product_presence')
    if isinstance(presence, Mapping):
        return str(presence.get('planning_state') or '').upper()
    return ''


def _strip_legacy_post_copy(prompt: str) -> str:
    patterns = [
        r'生成画面时为锁定文案预留清晰版式区，但不要让图像模型重写包装文字或最终营销文案；精确文案在后期确定性合成。?',
        r'Reserve deliberate layout zones for locked copy, but do not ask the image model to retype packaging or final marketing copy\. Exact approved text is composed deterministically after generation\.?',
    ]
    out = str(prompt or '')
    for pattern in patterns:
        out = re.sub(pattern, '', out, flags=re.I)
    return re.sub(r'\n{3,}', '\n\n', out).strip() + ('\n' if out.strip() else '')


def finalize_integrated_render_route(asset: Mapping[str, Any], bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Apply the current per-asset integrated-render authority before the final semantic membrane.

    This function does not choose the creative design. The Agent-authored asset object remains authority.
    It only prevents historical renderer defaults from rewriting integrated copy/product execution into a
    background-only + deterministic-post-composite workflow.
    """
    out = deepcopy(dict(bundle))
    route = _copy_route(asset)
    visible_copy = _visible_copy(asset, out)

    renderer = out.setdefault('renderer_recipe', {})
    text_policy = renderer.setdefault('text_policy', {})
    card = out.setdefault('design_card', {})
    info = card.setdefault('information_design', {})
    identity = card.setdefault('product_identity', {})

    presence = _presence(asset)
    visible_product = presence in {'HERO_REQUIRED', 'REQUIRED', 'SUPPORTING', 'DETAIL_ONLY', 'OPTIONAL'}
    exact_pixel = str(asset.get('product_fidelity') or '').upper() in {
        'EXACT_PIXEL_COMPOSITE', 'LOCKED_PIXEL', 'LOCKED_SOURCE_COMPOSITE', 'COMPOSITE'
    }

    # Product Presence is not invented here. When the Agent selected a visible product and did not
    # explicitly request immutable source pixels, restore the current native reference-guided route.
    if visible_product and not exact_pixel:
        identity['product_fidelity'] = 'REFERENCE_GUIDED_NATIVE_LOCK'
        renderer['real_product_master_required'] = False
        renderer['native_product_reference_required'] = True
        for row in renderer.get('source_product_bindings') or []:
            if isinstance(row, dict):
                row['visible_subject_binding'] = True

    integrated_routes = {'MODEL_RENDER_INTEGRATED', 'MODEL_RENDER', 'INTEGRATED', 'HYBRID'}
    if route in integrated_routes:
        out['prompt_cn'] = out['model_prompt_cn'] = _strip_legacy_post_copy(
            out.get('model_prompt_cn') or out.get('prompt_cn') or ''
        )
        out['prompt_en'] = out['model_prompt_en'] = _strip_legacy_post_copy(
            out.get('model_prompt_en') or out.get('prompt_en') or ''
        )

        text_policy['exact_copy_mode'] = (
            'HYBRID_MODEL_RENDER_PLUS_LOCAL_REFINEMENT' if route == 'HYBRID' else 'MODEL_RENDER_INTEGRATED'
        )
        text_policy['image_model_may_render_locked_copy'] = True
        text_policy['image_model_may_rewrite_locked_copy'] = False
        if route != 'HYBRID':
            renderer['deterministic_text_composition'] = False

        if visible_copy:
            art = asset.get('asset_art_direction') if isinstance(asset.get('asset_art_direction'), Mapping) else {}
            typography = art.get('typography')
            cn = (
                '【最终可见文案 / 一体排版】\n'
                '请在最终商业画面中直接、准确呈现以下目标市场文案，不改写、不漏字：\n'
                + visible_copy
            )
            en = (
                '[FINAL VISIBLE COPY / INTEGRATED TYPOGRAPHY]\n'
                'Render the following target-market copy directly and accurately in the final commercial image; '
                'do not rewrite or omit it:\n'
                + visible_copy
            )
            if _meaningful(typography):
                cn += '\n排版执行：' + str(typography)
                en += '\nTypography/layout execution: ' + str(typography)
            out['prompt_cn'] = out['model_prompt_cn'] = out['prompt_cn'].rstrip() + '\n\n' + cn + '\n'
            out['prompt_en'] = out['model_prompt_en'] = out['prompt_en'].rstrip() + '\n\n' + en + '\n'

    info['copy_render_route'] = route
    out['integrated_render_route_authority'] = {
        'copy_render_route': route,
        'product_presence_state': presence,
        'default_integrated_copy': route in {'MODEL_RENDER_INTEGRATED', 'MODEL_RENDER', 'INTEGRATED'},
        'native_reference_product': bool(visible_product and not exact_pixel),
        'principle': 'Integrated render is the normal route; post-composite/no-visible-copy/exact-pixel remain explicit per-asset choices.',
    }
    return out
