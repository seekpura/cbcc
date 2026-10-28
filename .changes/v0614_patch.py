from pathlib import Path

path = Path('runtime/cbcc/provider_executor.py')
text = path.read_text(encoding='utf-8')
old = """def _job_with_provider_sources(job: dict[str, Any], bindings: list[dict[str, Any]]) -> dict[str, Any]:
    executable = json.loads(json.dumps(job))
    executable['source_product_bindings'] = bindings
    executable['source_binding_hash'] = stable_hash(bindings)
    quality = executable.get('production_quality_contract') or {}
    quality['source_product_bindings'] = bindings
    quality['source_binding_hash'] = executable['source_binding_hash']
    executable['production_quality_contract'] = quality
    brief = executable.get('execution_brief') or {}
    brief['source_product_bindings'] = bindings
    brief['source_binding_hash'] = executable['source_binding_hash']
    executable['execution_brief'] = brief
    return executable
"""
new = """def _job_with_provider_sources(job: dict[str, Any], bindings: list[dict[str, Any]]) -> dict[str, Any]:
    executable = json.loads(json.dumps(job))
    execution_hash = stable_hash(bindings)
    executable['source_product_bindings'] = bindings
    # The portable source_binding_hash is immutable lineage from v0.6.12. Provider-side
    # upload/refresh changes locators, not source content identity, so it receives a separate hash.
    executable['provider_execution_source_binding_hash'] = execution_hash
    quality = executable.get('production_quality_contract') or {}
    quality['source_product_bindings'] = bindings
    quality['provider_execution_source_binding_hash'] = execution_hash
    executable['production_quality_contract'] = quality
    brief = executable.get('execution_brief') or {}
    brief['source_product_bindings'] = bindings
    brief['provider_execution_source_binding_hash'] = execution_hash
    executable['execution_brief'] = brief
    return executable
"""
if old not in text:
    raise SystemExit('target block not found')
path.write_text(text.replace(old, new), encoding='utf-8')
