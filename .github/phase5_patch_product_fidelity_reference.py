from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'{label}: expected source shape not found')
    return text.replace(old, new, 1)


# Prompt compiler must read fidelity from the same per-object Art Direction authority as Product Presence.
path = Path('runtime/cbcc/agent_authority_prompt_compiler.py')
text = path.read_text(encoding='utf-8')
old = """def _art_direction_missing(asset: dict[str, Any]) -> bool:\n    return _art_direction_required(asset) and not isinstance(asset.get('asset_art_direction'), dict)\n\n\ndef _product_rule(asset: dict[str, Any], presence: dict[str, Any], product_fidelity: str) -> str:\n"""
new = """def _art_direction_missing(asset: dict[str, Any]) -> bool:\n    return _art_direction_required(asset) and not isinstance(asset.get('asset_art_direction'), dict)\n\n\ndef _canonical_product_fidelity(asset: dict[str, Any], fallback: Any = None) -> str:\n    \"\"\"Resolve Product Fidelity from canonical per-object Art Direction before legacy aliases.\"\"\"\n    art = asset.get('asset_art_direction') if isinstance(asset.get('asset_art_direction'), dict) else {}\n    authored = art.get('product_fidelity')\n    if isinstance(authored, dict):\n        authored = authored.get('mode') or authored.get('product_fidelity') or authored.get('fidelity_mode')\n    if authored not in (None, '', [], {}):\n        return str(authored)\n    legacy = asset.get('product_fidelity')\n    if legacy not in (None, '', [], {}):\n        return str(legacy)\n    if fallback not in (None, '', [], {}):\n        return str(fallback)\n    return 'REFERENCE_GUIDED'\n\n\ndef _product_rule(asset: dict[str, Any], presence: dict[str, Any], product_fidelity: str) -> str:\n"""
text = replace_once(text, old, new, 'canonical fidelity helper')

old = """    identity = dict(card.get('product_identity') or {})\n    fidelity = str(identity.get('product_fidelity') or asset.get('product_fidelity') or 'REFERENCE_GUIDED')\n"""
new = """    identity = dict(card.get('product_identity') or {})\n    fidelity = _canonical_product_fidelity(asset, identity.get('product_fidelity'))\n    identity['product_fidelity'] = fidelity\n"""
text = replace_once(text, old, new, 'design-card fidelity authority')

old = """    visible_product = _product_visible(card.get('product_presence') or {})\n    locked_fidelity = str(asset.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL', 'LOCKED_SOURCE_COMPOSITE', 'COMPOSITE'}\n    real_master_required = bool(visible_product and locked_fidelity)\n\n    machine = legacy._compact({\n"""
new = """    visible_product = _product_visible(card.get('product_presence') or {})\n    canonical_fidelity = _canonical_product_fidelity(asset, (card.get('product_identity') or {}).get('product_fidelity'))\n    locked_fidelity = canonical_fidelity.upper() in {\n        'LOCKED_PIXEL', 'LOCKED_SOURCE_COMPOSITE', 'COMPOSITE',\n        'EXACT_PIXEL_COMPOSITE', 'PIXEL_COMPOSITE_EXPLICIT',\n    }\n    real_master_required = bool(visible_product and locked_fidelity)\n\n    machine = legacy._compact({\n"""
text = replace_once(text, old, new, 'real-master canonical fidelity')
text = text.replace("        'product_fidelity': asset.get('product_fidelity'),\n        'fidelity': {\n            'mode': asset.get('product_fidelity'),", "        'product_fidelity': canonical_fidelity,\n        'fidelity': {\n            'mode': canonical_fidelity,", 1)
text = text.replace("        'product_fidelity': asset.get('product_fidelity'),\n        'editable_layer_contract':", "        'product_fidelity': canonical_fidelity,\n        'editable_layer_contract':", 1)
path.write_text(text, encoding='utf-8')


# Reference/native authority must honor canonical fidelity while keeping Product Presence independent.
path = Path('runtime/cbcc/reference_guided_native_authority.py')
text = path.read_text(encoding='utf-8')
old = """def _explicit_exact_pixel(asset:Mapping[str,Any], card:Mapping[str,Any])->bool:\n    fidelity=str((card.get('product_identity') or {}).get('product_fidelity') or asset.get('product_fidelity') or '').upper()\n    return bool(\n"""
new = """def _canonical_product_fidelity(asset:Mapping[str,Any], card:Mapping[str,Any]|None=None)->str:\n    art=asset.get('asset_art_direction') if isinstance(asset.get('asset_art_direction'),Mapping) else {}\n    authored=art.get('product_fidelity')\n    if isinstance(authored,Mapping):\n        authored=authored.get('mode') or authored.get('product_fidelity') or authored.get('fidelity_mode')\n    if _meaningful(authored):\n        return str(authored).upper()\n    identity=(card or {}).get('product_identity') if isinstance((card or {}).get('product_identity'),Mapping) else {}\n    if _meaningful(identity.get('product_fidelity')):\n        return str(identity.get('product_fidelity')).upper()\n    if _meaningful(asset.get('product_fidelity')):\n        return str(asset.get('product_fidelity')).upper()\n    return 'REFERENCE_GUIDED'\n\n\ndef _explicit_exact_pixel(asset:Mapping[str,Any], card:Mapping[str,Any])->bool:\n    fidelity=_canonical_product_fidelity(asset,card)\n    return bool(\n"""
text = replace_once(text, old, new, 'reference canonical fidelity helper')

old = """def normalize_native_reference_fidelity(asset:Mapping[str,Any], card:Mapping[str,Any])->str:\n    raw=str((card.get('product_identity') or {}).get('product_fidelity') or asset.get('product_fidelity') or 'REFERENCE_GUIDED').upper()\n"""
new = """def normalize_native_reference_fidelity(asset:Mapping[str,Any], card:Mapping[str,Any])->str:\n    raw=_canonical_product_fidelity(asset,card)\n"""
text = replace_once(text, old, new, 'reference fidelity normalization')

old = """    state,visible=_presence(card)\n    exact=_explicit_exact_pixel(asset,card)\n    normalized=normalize_native_reference_fidelity(asset,card)\n"""
new = """    state,visible=_presence(card)\n    exact_selected=_explicit_exact_pixel(asset,card)\n    # Presence and fidelity are independent axes: a dormant exact-pixel preference must not make\n    # an intentionally absent product become a required reference/input/layer.\n    exact=bool(visible and exact_selected)\n    normalized=normalize_native_reference_fidelity(asset,card)\n"""
text = replace_once(text, old, new, 'presence wins over fidelity activation')

old = """    identity['product_fidelity']=normalized\n    identity['reference_generation_mode']='EXACT_PIXEL_COMPOSITE' if exact else 'REFERENCE_GUIDED_NATIVE_GENERATION'\n    if visible and not exact:\n"""
new = """    identity['product_fidelity']=normalized\n    identity['reference_generation_mode']=('TRUTH_REFERENCE_ONLY' if not visible else ('EXACT_PIXEL_COMPOSITE' if exact else 'REFERENCE_GUIDED_NATIVE_GENERATION'))\n    if visible and not exact:\n"""
text = replace_once(text, old, new, 'presence-aware identity reference mode')

# The existing notes/renderer/closure expressions already branch on visible/exact after exact is presence-aware.
path.write_text(text, encoding='utf-8')
