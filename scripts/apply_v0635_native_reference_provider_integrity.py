from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]

def patch(path:str,old:str,new:str):
    p=ROOT/path
    text=p.read_text(encoding='utf-8')
    if old not in text:
        if new in text: return
        raise SystemExit(f'missing anchor {path}: {old[:160]!r}')
    p.write_text(text.replace(old,new),encoding='utf-8')

(ROOT/'VERSION').write_text('0.6.35-native-reference-provider-integrity\n',encoding='utf-8')
patch('SKILL.md','version: 0.6.34-native-reference-authority-cleanup','version: 0.6.35-native-reference-provider-integrity')

# Remove a lower historical section that still called itself current authority and contradicted the top authority.
p=ROOT/'SKILL.md'; text=p.read_text(encoding='utf-8')
pattern=r"### Product Reference / Fidelity — current authority\n.*?(?=\n## v0\.6\.29 Final Stabilization)"
replacement='''### Product Reference / Fidelity — compatibility note superseded by v0.6.35\n- Current authority is the top-level `Reference-Guided Native Product + Dynamic Asset Universe Authority`. When Product Presence requires a real product to be visible, use `REFERENCE_GUIDED_NATIVE_LOCK`: bind the real product image as a strong model Reference Input and natively render the same product identity inside the complete final image.\n- Plain `REFERENCE_GUIDED` remains valid only when the source image is a Truth/Identity/Design reference and the current asset does not require the real product to appear.\n- `EXACT_PIXEL_COMPOSITE` is explicit-only for a user requirement that original source pixels remain immutable. Historical `LOCKED_PIXEL / LOCKED_SOURCE_COMPOSITE` names below are compatibility/history notes, not current default production semantics.\n- Photography/lighting/CMF remain relevance-driven; Product Presence and Product Fidelity remain separate decisions.\n'''
new_text,n=re.subn(pattern,replacement,text,flags=re.S)
if n!=1:
    if '### Product Reference / Fidelity — compatibility note superseded by v0.6.35' not in text:
        raise SystemExit(f'expected exactly one Product Reference current-authority block, got {n}')
else:
    p.write_text(new_text,encoding='utf-8')

# Provider routing dictionary accumulated duplicate native mode rows during iterative patches; collapse them.
p=ROOT/'runtime/cbcc/providers.py'; text=p.read_text(encoding='utf-8')
text=re.sub(r"(?:    'AI_REFERENCE_PRODUCT':'AI_IMAGE_PROVIDER',\n    'AI_REFERENCE_HUMAN_PRODUCT':'AI_IMAGE_PROVIDER',\n){2,}","    'AI_REFERENCE_PRODUCT':'AI_IMAGE_PROVIDER',\n    'AI_REFERENCE_HUMAN_PRODUCT':'AI_IMAGE_PROVIDER',\n",text)
p.write_text(text,encoding='utf-8')

# Provider contract requires semantic reference-image binding fields, not just a generic asset locator.
patch('runtime/cbcc/providers.py',
"    if source_binding_required: required_inputs.extend(['source_product_assets','source_product_bindings'])\n    if real_product_mode: required_inputs.extend(['photography_contract','shot_lighting_reasoning'])\n",
"    if source_binding_required: required_inputs.extend(['source_product_assets','source_product_bindings'])\n    binding_fields=['asset_id','locator','sha256','pixel_lock','allowed_transforms','identity_features']\n    if native_reference and not exact_pixel:\n        binding_fields += ['usage_role','reference_input_required','native_generation_required','pixel_copy_required','fidelity_mode']\n    if real_product_mode: required_inputs.extend(['photography_contract','shot_lighting_reasoning'])\n")
patch('runtime/cbcc/providers.py',
"            'required_binding_fields':['asset_id','locator','sha256','pixel_lock','allowed_transforms','identity_features'],\n",
"            'required_binding_fields':binding_fields,\n")

# Carry native-reference semantics all the way into portable provider source bindings.
patch('runtime/cbcc/production.py',
"    ready=[]; errors=[]\n    for row in manifest.get('source_product_assets') or []:\n",
"    fidelity=str(manifest.get('product_fidelity') or 'REFERENCE_GUIDED').upper()\n    mode=str(manifest.get('production_mode') or '').upper()\n    exact_pixel=fidelity in {'EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'}\n    native_reference=(not exact_pixel) and (fidelity in {'REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} or mode in _NATIVE_REFERENCE_MODES)\n    usage_role='EXACT_PIXEL_SOURCE_LAYER' if exact_pixel else ('NATIVE_SUBJECT_REFERENCE' if native_reference else 'TRUTH_REFERENCE')\n    source_usage='EXACT_PIXEL_SOURCE_LAYER' if exact_pixel else ('MODEL_REFERENCE_INPUT' if native_reference else 'DESIGN_REFERENCE')\n    ready=[]; errors=[]\n    for row in manifest.get('source_product_assets') or []:\n")
patch('runtime/cbcc/production.py',
"                'pixel_lock':bool(row.get('pixel_lock')),\n                'allowed_transforms':list(row.get('allowed_transforms') or []),\n                'identity_features':list(row.get('identity_features') or []),\n                'provider_asset_lifecycle':lifecycle,\n",
"                'pixel_lock':bool(exact_pixel),\n                'identity_lock':bool(native_reference or exact_pixel),\n                'fidelity_mode':fidelity,\n                'source_usage':source_usage,\n                'usage_role':usage_role,\n                'reference_input_required':bool(native_reference),\n                'native_generation_required':bool(native_reference),\n                'pixel_copy_required':bool(exact_pixel),\n                'allowed_transforms':list(row.get('allowed_transforms') or []),\n                'identity_features':list(row.get('identity_features') or []),\n                'provider_asset_lifecycle':lifecycle,\n")
patch('runtime/cbcc/production.py',
"            'pixel_lock':bool(row.get('pixel_lock')),\n            'allowed_transforms':list(row.get('allowed_transforms') or []),\n            'identity_features':list(row.get('identity_features') or []),\n        }\n",
"            'pixel_lock':bool(exact_pixel),\n            'identity_lock':bool(native_reference or exact_pixel),\n            'fidelity_mode':fidelity,\n            'source_usage':source_usage,\n            'usage_role':usage_role,\n            'reference_input_required':bool(native_reference),\n            'native_generation_required':bool(native_reference),\n            'pixel_copy_required':bool(exact_pixel),\n            'allowed_transforms':list(row.get('allowed_transforms') or []),\n            'identity_features':list(row.get('identity_features') or []),\n        }\n")

# Quality contract and execution brief expose the actual reference-generation route.
patch('runtime/cbcc/production.py',
"        'product_reference_rule':('Explicit exact-pixel route: preserve the exact supplied source pixels as an immutable layer.' if exact_pixel else ('Native reference route: pass the real product image(s) into the generation model as strong subject references and natively render the same real product identity in the complete final image.' if native_reference else 'Product source files are truth/design references only.')),\n        'locked_pixel_rule':('EXACT_PIXEL_COMPOSITE_EXPLICIT_ONLY' if exact_pixel else 'NOT_DEFAULT_NATIVE_REFERENCE_GENERATION'),\n",
"        'product_reference_generation_mode':('EXACT_PIXEL_COMPOSITE' if exact_pixel else ('REFERENCE_GUIDED_NATIVE_GENERATION' if native_reference else 'TRUTH_REFERENCE_ONLY')),\n        'reference_input_required':bool(native_reference),\n        'native_product_generation_required':bool(native_reference),\n        'product_reference_rule':('Explicit exact-pixel route: preserve the exact supplied source pixels as an immutable layer.' if exact_pixel else ('Native reference route: pass the real product image(s) into the generation model as strong subject references and natively render the same real product identity in the complete final image.' if native_reference else 'Product source files are truth/design references only.')),\n        'locked_pixel_rule':('EXACT_PIXEL_COMPOSITE_EXPLICIT_ONLY' if exact_pixel else 'NOT_DEFAULT_NATIVE_REFERENCE_GENERATION'),\n")
patch('runtime/cbcc/production.py',
"                'locked_pixel_rule':quality.get('locked_pixel_rule'),\n                'source_product_bindings':portable_bindings,\n",
"                'locked_pixel_rule':quality.get('locked_pixel_rule'),\n                'product_reference_generation_mode':quality.get('product_reference_generation_mode'),\n                'reference_input_required':quality.get('reference_input_required'),\n                'native_product_generation_required':quality.get('native_product_generation_required'),\n                'source_product_bindings':portable_bindings,\n")

# Source lineage hash must be checked for native-reference execution as well as explicit exact-pixel execution.
patch('runtime/cbcc/production.py',
"        if (fidelity in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} and r.get('production_contract_ack') is not True) or ('production_contract_ack' in r and not r.get('production_contract_ack')):\n",
"        if (fidelity in {'REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE','EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'} and r.get('production_contract_ack') is not True) or ('production_contract_ack' in r and not r.get('production_contract_ack')):\n")
patch('runtime/cbcc/production.py',
"        if str(qc.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}:\n",
"        if str(qc.get('product_fidelity') or '').upper() in {'REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE','EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'}:\n")
patch('runtime/cbcc/production.py',
"                'required':['asset_id','provider','package_hash','output_path','qa','quality_observations','production_receipt'] + (['source_binding_hash','production_contract_ack'] if str(quality.get('product_fidelity') or '').upper() in {'REFERENCE_GUIDED','REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE','EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'} else []) + (['changed_fields','changed_layers'] if row.get('revision_scope') else []),\n",
"                'required':['asset_id','provider','package_hash','output_path','qa','quality_observations','production_receipt'] + (['source_binding_hash','production_contract_ack'] if str(quality.get('product_fidelity') or '').upper() in {'REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE','EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'} else []) + (['changed_fields','changed_layers'] if row.get('revision_scope') else []),\n")

# Provider receipt carries native-reference source lineage but does not require a pixel layer manifest.
patch('runtime/cbcc/provider_portability.py',
"    required = ['job_id', 'asset_id', 'provider', 'package_hash', 'portable_manifest_hash', 'output_artifacts']\n    if fidelity == 'LOCKED_PIXEL':\n        required += ['source_binding_hash', 'layer_manifest']\n",
"    required = ['job_id', 'asset_id', 'provider', 'package_hash', 'portable_manifest_hash', 'output_artifacts']\n    native_reference=fidelity in {'REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}\n    exact_pixel=fidelity in {'EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'}\n    if native_reference or exact_pixel:\n        required += ['source_binding_hash']\n    if exact_pixel:\n        required += ['layer_manifest']\n")
patch('runtime/cbcc/provider_portability.py',
"            'required': fidelity == 'LOCKED_PIXEL',\n",
"            'required': exact_pixel,\n")
patch('runtime/cbcc/provider_portability.py',
"    if str(qc.get('product_fidelity') or '').upper() == 'LOCKED_PIXEL':\n        expected['source_binding_hash'] = qc.get('source_binding_hash')\n",
"    fidelity = str(qc.get('product_fidelity') or '').upper()\n    native_reference=fidelity in {'REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}\n    exact_pixel=fidelity in {'EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'}\n    if native_reference or exact_pixel:\n        expected['source_binding_hash'] = qc.get('source_binding_hash')\n")
patch('runtime/cbcc/provider_portability.py',
"    fidelity = str(qc.get('product_fidelity') or '').upper()\n    if fidelity == 'LOCKED_PIXEL':\n",
"    fidelity = str(qc.get('product_fidelity') or '').upper()\n    exact_pixel=fidelity in {'EXACT_PIXEL_COMPOSITE','PIXEL_COMPOSITE_EXPLICIT'}\n    if exact_pixel:\n")

# Provider executor may not invent proof that a reference image was used or that a product was natively rendered.
patch('runtime/cbcc/provider_executor.py',
"    out: dict[str, Any] = {}\n    required = (job.get('result_contract') or {}).get('quality_observations_required') or []\n    for key in required:\n        if key == 'source_product_asset_ids_used':\n            out[key] = ids\n        elif key == 'source_product_hashes_used':\n            out[key] = hashes\n        elif key == 'product_layer_operation':\n            out[key] = collected.get('product_layer_operation') or 'COMPOSITE_LOCKED'\n        else:\n            out[key] = {'status': 'PASS', 'evidence': 'provider executor reported ' + str(key)}\n",
"    out: dict[str, Any] = {}\n    required = (job.get('result_contract') or {}).get('quality_observations_required') or []\n    fidelity=str((job.get('production_quality_contract') or {}).get('product_fidelity') or '').upper()\n    mode=str(job.get('production_mode') or '').upper()\n    native_reference=fidelity in {'REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} or mode in {'AI_REFERENCE_PRODUCT','AI_REFERENCE_HUMAN_PRODUCT'}\n    for key in required:\n        if native_reference and key == 'source_product_asset_ids_used':\n            out[key] = []\n        elif native_reference and key == 'source_product_hashes_used':\n            out[key] = {}\n        elif native_reference and key in {'product_reference_input_used','native_product_rendered_in_final_output','product_identity_preserved'}:\n            out[key] = {'status': 'UNVERIFIED', 'evidence': None}\n        elif key == 'source_product_asset_ids_used':\n            out[key] = ids\n        elif key == 'source_product_hashes_used':\n            out[key] = hashes\n        elif key == 'product_layer_operation':\n            out[key] = collected.get('product_layer_operation') or 'COMPOSITE_LOCKED'\n        else:\n            out[key] = {'status': 'PASS', 'evidence': 'provider executor reported ' + str(key)}\n")

# External provider adapter discovery must explicitly support reference-image input for AI_REFERENCE modes.
patch('runtime/cbcc/provider_bridge.py',
"        if job.get('source_product_bindings'):\n            caps.append('ASSET_HANDLE_LIFECYCLE')\n        return caps, operations\n",
"        if job.get('source_product_bindings'):\n            caps.append('ASSET_HANDLE_LIFECYCLE')\n        mode=str(job.get('production_mode') or '').upper()\n        fidelity=str((job.get('production_quality_contract') or {}).get('product_fidelity') or '').upper()\n        if mode in {'AI_REFERENCE_PRODUCT','AI_REFERENCE_HUMAN_PRODUCT'} or fidelity in {'REFERENCE_GUIDED_NATIVE','REFERENCE_GUIDED_NATIVE_LOCK','NATIVE_REFERENCE_LOCK','LOCKED_IDENTITY_REFERENCE','LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}:\n            caps.append('REFERENCE_IMAGE_INPUT')\n        return caps, operations\n")
patch('runtime/cbcc/provider_bridge.py',
"    capabilities = ['IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE', 'ASSET_HANDLE_LIFECYCLE', 'HOST_CALLBACK_INJECTION']\n",
"    capabilities = ['IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE', 'ASSET_HANDLE_LIFECYCLE', 'HOST_CALLBACK_INJECTION', 'REFERENCE_IMAGE_INPUT']\n")
patch('runtime/cbcc/provider_bridge.py',
"            'AI_HUMAN_REAL_PRODUCT', 'AI_GENERATIVE', 'GRAPHIC_DESIGN', 'THREE_D', 'VIDEO',\n",
"            'AI_HUMAN_REAL_PRODUCT', 'AI_REFERENCE_PRODUCT', 'AI_REFERENCE_HUMAN_PRODUCT', 'AI_GENERATIVE', 'GRAPHIC_DESIGN', 'THREE_D', 'VIDEO',\n")
patch('runtime/cbcc/provider_bridge.py',
"                'AI_HUMAN_REAL_PRODUCT', 'AI_GENERATIVE', 'GRAPHIC_DESIGN', 'THREE_D', 'VIDEO',\n            ),\n            capabilities=('IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE', 'ASSET_HANDLE_LIFECYCLE'),\n",
"                'AI_HUMAN_REAL_PRODUCT', 'AI_REFERENCE_PRODUCT', 'AI_REFERENCE_HUMAN_PRODUCT', 'AI_GENERATIVE', 'GRAPHIC_DESIGN', 'THREE_D', 'VIDEO',\n            ),\n            capabilities=('IDEMPOTENT_SUBMIT', 'RESUMABLE_POLL', 'OUTPUT_RESOLVE', 'ASSET_HANDLE_LIFECYCLE', 'REFERENCE_IMAGE_INPUT'),\n")

print('v0.6.35 native-reference provider integrity migration applied')
