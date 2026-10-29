from pathlib import Path

patch = Path('scripts/repair_reference_guided_assets_and_capability_continuity.py')
s = patch.read_text(encoding='utf-8')
bad = '''replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "        'principle':'Semantic compression may remove repetition and irrelevant toolbox fields, but never an already-selected pixel/capture/composite-affecting execution decision.',\\n",
    "        'principle':'Prompt readiness is a production-quality diagnostic, not a project-completion gate. When prompts are requested, preserve the selected execution decisions that actually matter to that production route.',\\n",
)
'''
if bad not in s:
    raise SystemExit('expected brittle principle patch block not found')
s = s.replace(bad, '', 1)
# Apply the same semantic change against the actual compact return line after the main patch runs.
exec(compile(s, str(patch), 'exec'), {'__name__': '__main__'})

p = Path('runtime/cbcc/prompt_compiler.py')
text = p.read_text(encoding='utf-8')
old = "'principle':'Semantic compression may remove repetition and irrelevant toolbox fields, but never an already-selected pixel/capture/composite-affecting execution decision.'"
new = "'principle':'Prompt readiness is a production-quality diagnostic, not a project-completion gate. When prompts are requested, preserve the selected execution decisions that actually matter to that production route.'"
if old not in text:
    raise SystemExit('actual compact prompt audit principle anchor missing')
p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Retire two obsolete v0.6.0 assertions that conflict with the current authority:
# 1) reference image bound != immutable source layer; 2) no fixed direction/opportunity quotas.
t = Path('tests/test_v060_capability_complete_rebase.py')
ts = t.read_text(encoding='utf-8')
ts = ts.replace(
    "        assert 6 <= opportunity['opportunity_count'] <= 12\n",
    "        assert opportunity['opportunity_count'] > 0\n",
    1,
)
ts = ts.replace(
    "        assert 3 <= len(council['directions']) <= 5\n",
    "        assert len(council['directions']) > 0\n",
    1,
)
ts = ts.replace(
    "def test_v060_provider_job_inherits_canonical_prompt_contract_when_product_master_is_bound(tmp_path):\n    # Existing real-production preflight tests cover bound-master job creation; here the package contract itself must be available.\n    p=_build(tmp_path,'beauty_kiyuu.json')\n    idx=json.loads((p/'artifacts/asset_packages/ASSET_PACKAGE_INDEX.json').read_text(encoding='utf-8'))\n    d=p/'artifacts/asset_packages'/idx['assets'][0]['asset_id']\n    contract=json.loads((d/'13_prompt_contract.json').read_text(encoding='utf-8'))\n    assert contract['renderer_recipe']['text_policy']['exact_copy_mode']=='DETERMINISTIC_COMPOSITION_AFTER_RENDER'\n    assert contract['machine_visual_contract']['fidelity']['real_product_master_substitution_allowed'] is False\n",
    "def test_v060_bound_product_reference_does_not_imply_pixel_lock(tmp_path):\n    # Product source files are design references by default. Exact immutable-source composition is explicit-only.\n    p=_build(tmp_path,'beauty_kiyuu.json')\n    idx=json.loads((p/'artifacts/asset_packages/ASSET_PACKAGE_INDEX.json').read_text(encoding='utf-8'))\n    d=p/'artifacts/asset_packages'/idx['assets'][0]['asset_id']\n    contract=json.loads((d/'13_prompt_contract.json').read_text(encoding='utf-8'))\n    assert contract['renderer_recipe']['text_policy']['exact_copy_mode']=='DETERMINISTIC_COMPOSITION_AFTER_RENDER'\n    assert contract['machine_visual_contract']['fidelity']['real_product_master_required'] is False\n    assert contract['machine_visual_contract']['fidelity']['real_product_master_substitution_allowed'] is True\n",
    1,
)
t.write_text(ts,encoding='utf-8')
print('resilient repair applied; obsolete fixed-count/pixel-lock assertions retired')
