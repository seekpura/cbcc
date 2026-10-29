from pathlib import Path


def replace_once(path, old, new):
    p=Path(path); s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'anchor not found in {path}: {old[:180]!r}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

# Release manifest must state the current nonblocking/reference-guided authority.
replace_once(
    'scripts/build_plugin_dist.py',
    "            'prompt_consumption_audit_required': True,\n            'host_custom_short_report_cannot_substitute_full_delivery': True,\n",
    "            'prompt_consumption_audit_required': True,\n            'prompt_consumption_blocks_project_completion': False,\n            'product_source_default_reference_guided': True,\n            'photorealism_default_required': False,\n            'seven_agent_capability_continuity_required': True,\n            'host_custom_short_report_cannot_substitute_full_delivery': True,\n",
)

p=Path('.github/workflows/release-v0629.yml')
s=p.read_text(encoding='utf-8')
path_anchor="""      - 'runtime/cbcc/creative.py'\n      - 'runtime/cbcc/cli.py'\n"""
path_new="""      - 'runtime/cbcc/creative.py'\n      - 'runtime/cbcc/providers.py'\n      - 'runtime/cbcc/production.py'\n      - 'runtime/cbcc/video_creator.py'\n      - 'runtime/cbcc/tools/seven_agent.py'\n      - 'runtime/cbcc/cli.py'\n"""
if path_anchor not in s: raise SystemExit('release workflow runtime path anchor missing')
s=s.replace(path_anchor,path_new,1)

test_path_anchor="""      - 'tests/test_v067_workspace_information_architecture.py'\n      - 'README.md'\n"""
test_path_new="""      - 'tests/test_v067_workspace_information_architecture.py'\n      - 'tests/test_reference_guided_optional_prompt_and_capability_continuity.py'\n      - 'tests/test_reference_guided_video_provider_authority.py'\n      - 'tests/test_v060_capability_complete_rebase.py'\n      - 'tests/test_v0511_integration_quality_depth.py'\n      - 'tests/test_capability_contracts.py'\n      - 'tests/run_toolkit_smoke.py'\n      - 'references/capability_ledger.yaml'\n      - 'README.md'\n"""
if test_path_anchor not in s: raise SystemExit('release workflow test path anchor missing')
s=s.replace(test_path_anchor,test_path_new,1)

step_anchor="""      - name: Build Plugin and Skill archives\n        run: python scripts/build_plugin_dist.py --output-dir dist\n"""
step_new="""      - name: Reference-guided production and reference-capability continuity\n        env:\n          PYTHONPATH: runtime\n        run: |\n          pytest -q \\\n            tests/test_reference_guided_optional_prompt_and_capability_continuity.py \\\n            tests/test_reference_guided_video_provider_authority.py \\\n            tests/test_v060_capability_complete_rebase.py \\\n            tests/test_v0511_integration_quality_depth.py \\\n            tests/test_capability_contracts.py\n          python tests/run_toolkit_smoke.py\n          grep -q 'Product Reference / Fidelity — current authority' SKILL.md\n          grep -q 'Prompt Consumption Audit 是生产质量诊断，不是项目或资产完整度的全局阻断 Gate' SKILL.md\n          grep -q '七大第一类工具' SKILL.md\n          grep -q 'compile_seven_agent_synthesis' runtime/cbcc/tools/seven_agent.py\n          grep -q 'OPTIONAL_PRODUCTION_FILES' runtime/cbcc/asset_compiler.py\n          grep -q \"project_completion_blocking':False\" runtime/cbcc/delivery_export.py\n\n      - name: Build Plugin and Skill archives\n        run: python scripts/build_plugin_dist.py --output-dir dist\n"""
if step_anchor not in s: raise SystemExit('release workflow build step anchor missing')
s=s.replace(step_anchor,step_new,1)

req_anchor="""              'prompt_consumption_audit_required':True,\n              'host_custom_short_report_cannot_substitute_full_delivery':True,\n"""
req_new="""              'prompt_consumption_audit_required':True,\n              'prompt_consumption_blocks_project_completion':False,\n              'product_source_default_reference_guided':True,\n              'photorealism_default_required':False,\n              'seven_agent_capability_continuity_required':True,\n              'host_custom_short_report_cannot_substitute_full_delivery':True,\n"""
if req_anchor not in s: raise SystemExit('release manifest required-map anchor missing')
s=s.replace(req_anchor,req_new,1)

required_file_anchor="""                  root+'runtime/cbcc/asset_compiler.py',\n                  root+'builders/project_delivery_builder.py',\n"""
required_file_new="""                  root+'runtime/cbcc/asset_compiler.py',\n                  root+'runtime/cbcc/providers.py',\n                  root+'runtime/cbcc/production.py',\n                  root+'runtime/cbcc/video_creator.py',\n                  root+'runtime/cbcc/tools/seven_agent.py',\n                  root+'builders/project_delivery_builder.py',\n"""
if required_file_anchor not in s: raise SystemExit('packaged required-file anchor missing')
s=s.replace(required_file_anchor,required_file_new,1)

required_test_anchor="""                  root+'tests/test_prompt_execution_decision_preservation.py',\n              ]\n"""
required_test_new="""                  root+'tests/test_prompt_execution_decision_preservation.py',\n                  root+'tests/test_reference_guided_optional_prompt_and_capability_continuity.py',\n                  root+'tests/test_reference_guided_video_provider_authority.py',\n                  root+'tests/test_v060_capability_complete_rebase.py',\n                  root+'tests/test_v0511_integration_quality_depth.py',\n                  root+'tests/test_capability_contracts.py',\n              ]\n"""
if required_test_anchor not in s: raise SystemExit('packaged required-test anchor missing')
s=s.replace(required_test_anchor,required_test_new,1)

read_anchor="""              prompt=z.read(root+'runtime/cbcc/prompt_compiler.py').decode('utf-8')\n"""
read_new="""              prompt=z.read(root+'runtime/cbcc/prompt_compiler.py').decode('utf-8')\n              asset_compiler=z.read(root+'runtime/cbcc/asset_compiler.py').decode('utf-8')\n              production=z.read(root+'runtime/cbcc/production.py').decode('utf-8')\n              seven=z.read(root+'runtime/cbcc/tools/seven_agent.py').decode('utf-8')\n"""
if read_anchor not in s: raise SystemExit('packaged read anchor missing')
s=s.replace(read_anchor,read_new,1)

assert_anchor="""              assert 'CANONICAL_PROMPT_COMPILED_EXECUTION_PRESERVING' in prompt\n          print('packaged delivery + FULL depth + prompt continuity + Chinese-base host/runtime language authority PASS')\n"""
assert_new="""              assert 'CANONICAL_PROMPT_COMPILED_EXECUTION_PRESERVING' in prompt\n              assert 'REFERENCE_GUIDED' in prompt\n              assert 'OPTIONAL_PRODUCTION_FILES' in asset_compiler\n              assert \"_REAL_PRODUCT_MODES={'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT'}\" in production\n              assert 'compile_seven_agent_synthesis' in seven\n              assert 'Product Reference / Production Authority' in wrapper\n              assert 'Prompt、生图方案、摄影/灯光/Prelight 是能力与生产准备度，不是项目或资产完整度的全局 Gate' in wrapper\n          print('packaged delivery + Chinese language + reference-guided nonblocking production + reference capability continuity PASS')\n"""
if assert_anchor not in s: raise SystemExit('packaged assertion anchor missing')
s=s.replace(assert_anchor,assert_new,1)

p.write_text(s,encoding='utf-8')
print('release capability guard patched')
