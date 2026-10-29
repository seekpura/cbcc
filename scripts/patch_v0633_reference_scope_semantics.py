from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def replace(path:str,old:str,new:str):
    p=ROOT/path
    text=p.read_text(encoding='utf-8')
    if old not in text:
        if new in text: return
        raise SystemExit(f'missing anchor {path}: {old[:120]!r}')
    p.write_text(text.replace(old,new),encoding='utf-8')

# Source ingestion alone does not mean the product must appear. Plain REFERENCE_GUIDED remains a
# truth/design reference. Explicit identity lock (including legacy pixel_lock) becomes native lock.
replace('runtime/cbcc/compiler.py',
"        fidelity_mode='EXACT_PIXEL_COMPOSITE' if exact_pixel else ('REFERENCE_GUIDED_NATIVE_LOCK' if identity_lock or not requested_fidelity else requested_fidelity)\n",
"        fidelity_mode='EXACT_PIXEL_COMPOSITE' if exact_pixel else ('REFERENCE_GUIDED_NATIVE_LOCK' if identity_lock else (requested_fidelity or 'REFERENCE_GUIDED'))\n")
replace('runtime/cbcc/compiler.py',
"            'identity_lock':identity_lock or not exact_pixel,\n            'fidelity_mode':fidelity_mode,\n            'source_usage':r.get('source_usage') or ('EXACT_PIXEL_SOURCE_LAYER' if exact_pixel else 'MODEL_REFERENCE_INPUT'),\n            'allowed_transforms':r.get('allowed_transforms') or (['PROPORTIONAL_SCALE','PLACEMENT','MASK_OR_CROP','COMPOSITE'] if exact_pixel else ['REFERENCE_INPUT','NATIVE_RENDER','CAMERA_MATCH','PERSPECTIVE_MATCH','LIGHTING_MATCH','DEPTH_MATCH']),\n",
"            'identity_lock':bool(identity_lock or fidelity_mode=='REFERENCE_GUIDED_NATIVE_LOCK'),\n            'fidelity_mode':fidelity_mode,\n            'source_usage':r.get('source_usage') or ('EXACT_PIXEL_SOURCE_LAYER' if exact_pixel else ('MODEL_REFERENCE_INPUT' if fidelity_mode=='REFERENCE_GUIDED_NATIVE_LOCK' else 'DESIGN_REFERENCE')),\n            'allowed_transforms':r.get('allowed_transforms') or (['PROPORTIONAL_SCALE','PLACEMENT','MASK_OR_CROP','COMPOSITE'] if exact_pixel else (['REFERENCE_INPUT','NATIVE_RENDER','CAMERA_MATCH','PERSPECTIVE_MATCH','LIGHTING_MATCH','DEPTH_MATCH'] if fidelity_mode=='REFERENCE_GUIDED_NATIVE_LOCK' else ['REFERENCE','REDRAW','RERENDER','RESTYLE','RECOMPOSE','PROPORTIONAL_SCALE','PLACEMENT','MASK_OR_CROP','COMPOSITE'])),\n")

# Provider binding must depend on a native-reference fidelity/mode, not the generic REFERENCE_GUIDED
# label alone. This keeps generic video/document assets from being forced to use a visible product.
replace('runtime/cbcc/providers.py',
"    native_reference=fidelity_u in {'REFERENCE_GUIDED','REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} or mode in {'AI_REFERENCE_PRODUCT','AI_REFERENCE_HUMAN_PRODUCT'}\n",
"    native_reference=fidelity_u in {'REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} or mode in {'AI_REFERENCE_PRODUCT','AI_REFERENCE_HUMAN_PRODUCT'}\n")

# Production follows the same scoped meaning: generic REFERENCE_GUIDED alone is not a visible-product
# requirement; AI_REFERENCE_* or identity-lock fidelity is.
replace('runtime/cbcc/production.py',
"    native_reference=fidelity in {'REFERENCE_GUIDED','REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} or mode in _NATIVE_REFERENCE_MODES\n",
"    native_reference=fidelity in {'REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} or mode in _NATIVE_REFERENCE_MODES\n")
replace('runtime/cbcc/production.py',
"    native_reference=fidelity in {'REFERENCE_GUIDED','REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}\n",
"    native_reference=fidelity in {'REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}\n")

print('v0.6.33 reference scope semantics patched')
