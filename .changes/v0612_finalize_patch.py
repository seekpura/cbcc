from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f'{label} anchor not found')
    return text.replace(old, new, 1)


# 1) Provider portability primitives: repair staged capture-mode typo and add exact host-path rebinding.
portability = Path('runtime/cbcc/provider_portability.py')
text = portability.read_text(encoding='utf-8')
text = replace_once(
    text,
    "_CAPTURE_METADATA_MODES = {'REAL_PHOTO', 'VIDEO?}",
    "_CAPTURE_METADATA_MODES = {'REAL_PHOTO', 'VIDEO'}",
    'capture mode',
)
helper = '''\ndef rebind_portable_execution_metadata(value: Any, upstream_bindings: list[dict[str, Any]] | None, portable_bindings: list[dict[str, Any]] | None) -> Any:\n    """Replace only source-master host paths with verified portable job locators.\n\n    Frozen package hashes still bind the original compiled package. This projection is only the\n    provider-facing execution metadata, so stale host paths cannot become execution locators after\n    the job leaves the CBCC runtime host.\n    """\n    portable_by_id = {str(row.get('asset_id')): row for row in (portable_bindings or []) if isinstance(row, dict) and row.get('asset_id')}\n    replacements: dict[str, str] = {}\n    for row in upstream_bindings or []:\n        if not isinstance(row, dict):\n            continue\n        locator = row.get('locator') or {}\n        if str(locator.get('kind') or '').upper() != 'LOCAL_FILE_PATH' or not locator.get('value'):\n            continue\n        portable = portable_by_id.get(str(row.get('asset_id'))) or {}\n        portable_locator = portable.get('locator') or {}\n        if str(portable_locator.get('kind') or '').upper() == 'PACKAGE_RELATIVE_PATH' and portable_locator.get('value'):\n            replacements[str(locator.get('value'))] = str(portable_locator.get('value'))\n\n    def walk(node: Any) -> Any:\n        if isinstance(node, dict):\n            return {key: walk(item) for key, item in node.items()}\n        if isinstance(node, list):\n            return [walk(item) for item in node]\n        if isinstance(node, tuple):\n            return tuple(walk(item) for item in node)\n        if isinstance(node, str) and node in replacements:\n            return replacements[node]\n        return node\n\n    return walk(value)\n'''
anchor = '\ndef build_production_receipt_contract('
if 'def rebind_portable_execution_metadata(' not in text:
    if anchor not in text:
        raise SystemExit('provider portability helper anchor not found')
    text = text.replace(anchor, helper + anchor, 1)
portability.write_text(text, encoding='utf-8')


# 2) Production bridge: portable job projection must not overwrite the upstream run contract.
production = Path('runtime/cbcc/production.py')
p = production.read_text(encoding='utf-8')
old_import = 'from .provider_portability import materialize_portable_job_inputs, build_production_receipt_contract, production_receipt_template, validate_production_receipt'
p = replace_once(p, old_import, old_import + ', rebind_portable_execution_metadata', 'provider portability import')

quality_anchor = "        quality['canonical_prompt_contract']=canonical\n"
quality_new = quality_anchor + "        quality=rebind_portable_execution_metadata(quality,upstream_qc.get('source_product_bindings') or [],portable_bindings)\n        quality.setdefault('provider_job_portability',{})['host_source_paths_rebound']=True\n"
p = replace_once(p, quality_anchor, quality_new, 'quality portability')

binding_anchor = "        binding['canonical_prompt_contract']=bound_canonical\n"
binding_new = binding_anchor + "        binding=rebind_portable_execution_metadata(binding,upstream_qc.get('source_product_bindings') or [],portable_bindings)\n"
p = replace_once(p, binding_anchor, binding_new, 'binding portability')

old_assign = "        row['production_quality_contract']=quality\n        row['production_contract_binding']=binding\n        row['provider_job_id']=job_id\n"
new_assign = "        row['provider_job_quality_contract']=quality\n        row['provider_job_contract_binding']=binding\n        row['provider_job_source_binding_hash']=portable_hash\n        row['provider_job_source_product_bindings']=portable_bindings\n        row['provider_job_id']=job_id\n"
p = replace_once(p, old_assign, new_assign, 'provider job contract separation')

local_anchor = "        local=[]\n        if row.get('status')!='READY_TO_HANDOFF': local.append('PRODUCTION_PREFLIGHT_NOT_READY')\n"
local_new = "        contract_row=row\n        if r.get('_provider_job_ingest'):\n            contract_row={**row}\n            if isinstance(row.get('provider_job_quality_contract'),dict): contract_row['production_quality_contract']=row['provider_job_quality_contract']\n            if isinstance(row.get('provider_job_contract_binding'),dict): contract_row['production_contract_binding']=row['provider_job_contract_binding']\n        local=[]\n        if row.get('status')!='READY_TO_HANDOFF': local.append('PRODUCTION_PREFLIGHT_NOT_READY')\n"
p = replace_once(p, local_anchor, local_new, 'result contract projection')
p = replace_once(p, "local.extend(_quality_result_issues(row,r))", "local.extend(_quality_result_issues(contract_row,r))", 'quality result projection')
p = replace_once(p, "local.extend(validate_production_receipt(row,r))", "local.extend(validate_production_receipt(contract_row,r))", 'receipt projection')
p = replace_once(p, "        binding=row.get('production_contract_binding') or {}\n        fidelity=", "        binding=contract_row.get('production_contract_binding') or {}\n        fidelity=", 'binding projection')
p = replace_once(p, "fidelity=str((row.get('production_quality_contract') or {}).get('product_fidelity') or '').upper()", "fidelity=str((contract_row.get('production_quality_contract') or {}).get('product_fidelity') or '').upper()", 'fidelity projection')
p = replace_once(
    p,
    "        qc=row.get('production_quality_contract') or {}\n        expected_source_binding_hash=qc.get('source_binding_hash')",
    "        qc=contract_row.get('production_quality_contract') or {}\n        expected_source_binding_hash=qc.get('source_binding_hash')",
    'source binding projection',
)
production.write_text(p, encoding='utf-8')


# 3) Continuity tests: v0.6.11 handoff becomes package-relative under v0.6.12.
test = Path('tests/test_v0611_provider_source_binding.py')
t = test.read_text(encoding='utf-8')
t = replace_once(
    t,
    "assert job['source_product_bindings'][0]['handoff_status']=='READY_LOCAL_VERIFIED'",
    "assert job['source_product_bindings'][0]['handoff_status']=='READY_PACKAGE_VERIFIED'",
    'v0.6.11 portable handoff expectation',
)
test.write_text(t, encoding='utf-8')


# 4) Legacy external-provider lifecycle tests must return the v0.6.12 production receipt.
receipt_helper = '''\n\ndef _portable_receipt(job):\n    bindings=job.get('source_product_bindings') or []\n    return {\n        'job_id':job['job_id'],'asset_id':job['asset_id'],'provider':job['provider'],'package_hash':job['package_hash'],\n        'portable_manifest_hash':job['portable_package']['portable_manifest_hash'],'source_binding_hash':job.get('source_binding_hash'),\n        'output_artifacts':[{'uri':'fixture://provider-output/'+job['asset_id'],'sha256':'b'*64,'role':'FINAL'}],\n        'layer_manifest':[{'layer_id':'product-'+str(i),'role':'PRODUCT_MASTER','source_asset_id':x['asset_id'],'source_sha256':x['sha256'],'operation':'COMPOSITE_LOCKED','frozen':True} for i,x in enumerate(bindings)],\n        'capture_metadata':{},\n    }\n'''

alpha6 = Path('tests/test_alpha6_review_provider_overlays.py')
a = alpha6.read_text(encoding='utf-8')
if 'def _portable_receipt(job):' not in a:
    marker = '\n\ndef _asset():\n'
    if marker not in a:
        raise SystemExit('alpha6 receipt helper anchor not found')
    a = a.replace(marker, receipt_helper + marker, 1)
old = "'quality_observations':_quality_observations(job)}"
new = "'quality_observations':_quality_observations(job),'production_receipt':_portable_receipt(job)}"
if a.count(old) < 2:
    raise SystemExit('alpha6 provider result anchors not found')
a = a.replace(old, new)
alpha6.write_text(a, encoding='utf-8')

v512 = Path('tests/test_v0512_production_learning_loop.py')
v = v512.read_text(encoding='utf-8')
if 'def _portable_receipt(job):' not in v:
    marker = '\n\ndef test_v0512_host_final_copy_can_reach_approved_only_with_exact_review():\n'
    if marker not in v:
        raise SystemExit('v0512 receipt helper anchor not found')
    v = v.replace(marker, receipt_helper + marker, 1)
for var in ('job', 'rjob'):
    old = f"'quality_observations':_quality_observations({var})}}"
    new = f"'quality_observations':_quality_observations({var}),'production_receipt':_portable_receipt({var})}}"
    if old in v:
        v = v.replace(old, new)
v512.write_text(v, encoding='utf-8')


# 5) New regression: materializing a portable job keeps upstream and provider-job contracts separate.
v612 = Path('tests/test_v0612_provider_portability_receipt.py')
s = v612.read_text(encoding='utf-8')
if 'test_materialization_preserves_upstream_contract_and_adds_provider_projection' not in s:
    marker = '\n\ndef test_external_result_receipt_binds_job_source_layer_and_output_hash(tmp_path):\n'
    new_test = '''\n\ndef test_materialization_preserves_upstream_contract_and_adds_provider_projection(tmp_path):\n    packs = tmp_path / 'packs'; master = tmp_path / 'master.png'; _compile(packs, master)\n    run = build_production_run(packs); row = run['assets'][0]\n    upstream_hash = row['production_quality_contract']['source_binding_hash']\n    upstream_locator = dict(row['production_quality_contract']['source_product_bindings'][0]['locator'])\n    jobs = tmp_path / 'jobs'; materialize_provider_jobs(packs, run, jobs)\n    job = json.loads((jobs / row['asset_id'] / 'job.json').read_text(encoding='utf-8'))\n    assert row['production_quality_contract']['source_binding_hash'] == upstream_hash\n    assert row['production_quality_contract']['source_product_bindings'][0]['locator'] == upstream_locator\n    assert upstream_locator['kind'] == 'LOCAL_FILE_PATH'\n    assert row['provider_job_quality_contract']['source_binding_hash'] == job['source_binding_hash']\n    assert row['provider_job_quality_contract']['source_product_bindings'][0]['locator']['kind'] == 'PACKAGE_RELATIVE_PATH'\n'''
    if marker not in s:
        raise SystemExit('v0.6.12 contract separation test anchor not found')
    s = s.replace(marker, new_test + marker, 1)
v612.write_text(s, encoding='utf-8')
