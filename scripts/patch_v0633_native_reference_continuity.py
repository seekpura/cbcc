from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def replace(path:str,old:str,new:str):
    p=ROOT/path
    text=p.read_text(encoding='utf-8')
    if old not in text:
        if new in text: return
        raise SystemExit(f'missing anchor {path}: {old[:120]!r}')
    p.write_text(text.replace(old,new),encoding='utf-8')

# Native reference route must not retain a legacy composite audit flag.
replace('runtime/cbcc/reference_guided_native_authority.py',
"    closure['native_product_generation_required']=bool(visible and not exact)\n    closure['exact_pixel_composite_explicit_only']=True\n",
"    closure['native_product_generation_required']=bool(visible and not exact)\n    closure['exact_pixel_composite_explicit_only']=True\n    if visible and not exact:\n        closure['locked_source_final_composite_instruction']=False\n")

# Preserve a more specific upstream prompt-readiness reason when reference input is also missing.
replace('runtime/cbcc/reference_guided_native_authority.py',
"        closure['status']='INCOMPLETE'\n        closure['model_generation_blocking']=True\n        out['model_prompt_status']='REAL_PRODUCT_REFERENCE_INPUT_REQUIRED'\n",
"        closure['status']='INCOMPLETE'\n        closure['model_generation_blocking']=True\n        prior=str(out.get('model_prompt_status') or '')\n        if prior not in {'BILINGUAL_RENDER_SEMANTICS_REQUIRED','COPY_RENDER_MODE_REQUIRED','AGENT_ART_DIRECTION_REQUIRED','ART_DIRECTION_EXECUTION_DEPTH_REQUIRED'}:\n            out['model_prompt_status']='REAL_PRODUCT_REFERENCE_INPUT_REQUIRED'\n")

source="[{'asset_id':'MASTER-FRONT','role':'FRONT','provider_asset_handle':'ref://master-front','sha256':'abc123','ingest_status':'HASH_VERIFIED_LOCAL'}]"
replace('tests/test_v0632_production_parameter_closure.py',
"        {}, None, None, [],\n",
"        {}, None, None, "+source+",\n")
replace('tests/test_v0632_production_parameter_closure.py',
"def test_locked_source_composite_prompt_consumes_full_execution_program():",
"def test_reference_locked_product_prompt_consumes_full_execution_program_and_renders_product_natively():")
replace('tests/test_v0632_production_parameter_closure.py',
"    assert closure['locked_source_final_composite_instruction'] is True\n",
"    assert closure['locked_source_final_composite_instruction'] is False\n    assert closure['product_reference_generation_mode']=='REFERENCE_GUIDED_NATIVE_GENERATION'\n    assert closure['native_product_generation_required'] is True\n")
replace('tests/test_v0632_production_parameter_closure.py',
"    assert 'final composite' in en.lower()\n    assert 'do not render, redraw or substitute the product itself' in en.lower()\n",
"    assert 'natively render the product inside the complete final image' in en.lower()\n    assert 'do not render, redraw or substitute the product itself' not in en.lower()\n")

replace('tests/test_v0631_model_native_prompt_contract.py',
"    return compile_asset_prompt(asset,{'name':'K01'},{'market':'MY','platform_family':'TikTok Shop','site':'MY','category':'skincare'}, {}, {'primary_locale':'ms-MY','delivery_locale':'zh-CN'}, {}, None, None, [])",
"    return compile_asset_prompt(asset,{'name':'K01'},{'market':'MY','platform_family':'TikTok Shop','site':'MY','category':'skincare'}, {}, {'primary_locale':'ms-MY','delivery_locale':'zh-CN'}, {}, None, None, "+source+")")

print('v0.6.33 native reference continuity fixtures patched')
