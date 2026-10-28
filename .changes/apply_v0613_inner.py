from pathlib import Path
import re

ROOT = Path('.')

def read(path):
    return (ROOT / path).read_text(encoding='utf-8')

def write(path, text):
    (ROOT / path).write_text(text, encoding='utf-8')

def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'PATCH_MISS:{label}')
    if text.count(old) != 1:
        raise SystemExit(f'PATCH_COUNT:{label}:{text.count(old)}')
    return text.replace(old, new, 1)

def regex_once(text, pattern, replacement, label, flags=0):
    new, n = re.subn(pattern, replacement, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'PATCH_REGEX_COUNT:{label}:{n}')
    return new

# providers.py
path = 'runtime/cbcc/providers.py'
text = read(path)
text = replace_once(
    text,
    'from typing import Any\n',
    'from typing import Any\n\nfrom .provider_transport import adapter_profile_for\n',
    'providers-import',
)
text = replace_once(
    text,
    "    'EPV_ADAPTER': {'modes':['REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT','AI_GENERATIVE','GRAPHIC_DESIGN','THREE_D','VIDEO'],'locked_pixel':'CONTRACT_DRIVEN','human_review':True,'adapter':'EXTERNAL_ADAPTER','outputs':['provider_manifest','artifact','qa']},",
    "    'EPV_ADAPTER': {'modes':['REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT','AI_GENERATIVE','GRAPHIC_DESIGN','THREE_D','VIDEO'],'locked_pixel':'CONTRACT_DRIVEN','human_review':True,'adapter':'EXTERNAL_ADAPTER','outputs':['provider_manifest','artifact','qa'],'adapter_profile':adapter_profile_for('EXTERNAL_ADAPTER','EPV_ADAPTER')},",
    'providers-epv-profile',
)
text = replace_once(
    text,
    "        'adapter':spec.get('adapter','FILE_HANDOFF'),'locked_pixel_support':spec['locked_pixel'],\n",
    "        'adapter':spec.get('adapter','FILE_HANDOFF'),'adapter_profile':spec.get('adapter_profile') or adapter_profile_for(spec.get('adapter','FILE_HANDOFF'),provider),'locked_pixel_support':spec['locked_pixel'],\n",
    'providers-contract-profile',
)
text = replace_once(
    text,
    "            'locked_pixel_result_evidence':['source_product_asset_ids_used','source_product_hashes_used','product_layer_operation','product_identity_preserved'] if fidelity=='LOCKED_PIXEL' else [],\n",
    "            'locked_pixel_result_evidence':['source_product_asset_ids_used','source_product_hashes_used','product_layer_operation','product_identity_preserved'] if fidelity=='LOCKED_PIXEL' else [],\n            'provider_asset_handle_lifecycle':{\n                'supported':True,\n                'structured_fields':['handle_id','provider','state','sha256','issued_at','verified_at','expires_at','supersedes_handle','generation'],\n                'legacy_string_semantics':'DECLARED_ONLY',\n                'rule':'Structured handles must be executable, unexpired and content-hash bound. Refreshes must rotate the handle and declare predecessor lineage.'\n            },\n",
    'providers-handle-contract',
)
write(path, text)

# provider_portability.py
path = 'runtime/cbcc/provider_portability.py'
text = read(path)
text = replace_once(
    text,
    'from .models import stable_hash\n',
    'from .models import stable_hash\nfrom .provider_transport import validate_provider_asset_binding, verify_artifact_reference\n',
    'portability-import',
)
text = replace_once(
    text,
    "        elif kind == 'PROVIDER_ASSET_HANDLE':\n            if not value or not declared:\n                errors.append({'asset_id': aid, 'code': 'PORTABLE_PROVIDER_HANDLE_INCOMPLETE'})\n                continue\n            binding['handoff_status'] = 'READY_PROVIDER_HANDLE_VERIFIED'\n            binding['handoff_sha256'] = declared\n",
    "        elif kind == 'PROVIDER_ASSET_HANDLE':\n            handle_issues = validate_provider_asset_binding(binding)\n            if handle_issues:\n                errors.extend({'asset_id': aid, 'code': code} for code in handle_issues)\n                continue\n            binding['handoff_status'] = 'READY_PROVIDER_HANDLE_LIFECYCLE_VERIFIED'\n            binding['handoff_sha256'] = declared\n",
    'portability-handle-lifecycle',
)
text = replace_once(
    text,
    'def validate_production_receipt(row: dict[str, Any], result: dict[str, Any]) -> list[str]:',
    'def validate_production_receipt(row: dict[str, Any], result: dict[str, Any], *, remote_artifact_resolver=None, require_remote_verification: bool = False) -> list[str]:',
    'portability-receipt-signature',
)
pattern = r"        base_raw = result\.get\('_provider_job_dir'\)\n        base = Path\(str\(base_raw\)\) if base_raw else None\n        for artifact in artifacts:\n            if not isinstance\(artifact, dict\):\n                issues\.append\('PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_INVALID'\)\n                continue\n            locator = artifact\.get\('path_or_uri'\) or artifact\.get\('path'\) or artifact\.get\('uri'\)\n            declared = str\(artifact\.get\('sha256'\) or ''\)\.lower\(\)\n            if not locator or not re\.fullmatch\(r'\[0-9a-f\]\{64\}', declared\):\n                issues\.append\('PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_INVALID'\)\n                continue\n            if base and artifact\.get\('uri'\) is None and '://' not in str\(locator\):\n                rel = Path\(str\(locator\)\)\n                if rel\.is_absolute\(\):\n                    issues\.append\('PRODUCTION_RECEIPT_OUTPUT_PATH_NOT_PORTABLE'\)\n                    continue\n                target = base / rel\n                if not target\.exists\(\) or not target\.is_file\(\):\n                    issues\.append\('PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_MISSING'\)\n                elif _sha256_file\(target\) != declared:\n                    issues\.append\('PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_HASH_MISMATCH'\)"
replacement = """        base_raw = result.get('_provider_job_dir')
        base = Path(str(base_raw)) if base_raw else None
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                issues.append('PRODUCTION_RECEIPT_OUTPUT_ARTIFACT_INVALID')
                continue
            check = verify_artifact_reference(
                artifact,
                base_dir=base,
                resolver=remote_artifact_resolver,
                require_remote_verification=require_remote_verification,
            )
            issues.extend(check.get('issues') or [])"""
text = regex_once(text, pattern, replacement, 'portability-artifact-verification', flags=re.S)
write(path, text)

# production.py
path = 'runtime/cbcc/production.py'
text = read(path)
text = replace_once(
    text,
    'from .provider_portability import materialize_portable_job_inputs, build_production_receipt_contract, production_receipt_template, validate_production_receipt, rebind_portable_execution_metadata\n',
    'from .provider_portability import materialize_portable_job_inputs, build_production_receipt_contract, production_receipt_template, validate_production_receipt, rebind_portable_execution_metadata\nfrom .provider_transport import normalize_provider_asset_handle, validate_provider_asset_binding, build_adapter_transmission, adapter_result_template, validate_adapter_result\n',
    'production-import',
)
new_source_fn = '''def _source_product_bindings(manifest:dict[str,Any])->tuple[list[dict[str,Any]],list[dict[str,Any]]]:
    """Resolve production-time source bindings and validate provider-handle lifecycle.

    Local masters are re-hashed at handoff. Provider handles may be legacy strings (declared-only
    compatibility) or structured lifecycle records with provider/state/expiry/refresh lineage.
    """
    ready=[]; errors=[]
    for row in manifest.get('source_product_assets') or []:
        if not isinstance(row,dict):
            continue
        aid=row.get('asset_id'); handle=row.get('provider_asset_handle'); raw_path=row.get('path'); declared=str(row.get('sha256') or '').lower() or None
        locator_kind='PROVIDER_ASSET_HANDLE' if handle else ('LOCAL_FILE_PATH' if raw_path else 'UNRESOLVED')
        actual=None; lifecycle=None; lifecycle_issues=[]
        if handle:
            lifecycle=normalize_provider_asset_handle(handle,source_sha256=declared,default_provider=row.get('provider_asset_provider'),source_row=row)
            locator_value=lifecycle.get('handle_id')
            binding={
                'asset_id':aid,'role':row.get('role'),
                'locator':{'kind':'PROVIDER_ASSET_HANDLE','value':locator_value},
                'sha256':declared,'handoff_sha256':declared,
                'pixel_lock':bool(row.get('pixel_lock')),
                'allowed_transforms':list(row.get('allowed_transforms') or []),
                'identity_features':list(row.get('identity_features') or []),
                'provider_asset_lifecycle':lifecycle,
            }
            lifecycle_issues=validate_provider_asset_binding(binding)
            status=('READY_PROVIDER_HANDLE' if lifecycle.get('legacy_declared') else 'READY_PROVIDER_HANDLE_LIFECYCLE_VERIFIED') if not lifecycle_issues else 'PROVIDER_HANDLE_LIFECYCLE_HOLD'
            binding['handoff_status']=status
            if not lifecycle_issues:
                ready.append(binding)
            else:
                binding['lifecycle_errors']=lifecycle_issues
                errors.append({'asset_id':aid,'status':status,'locator_kind':'PROVIDER_ASSET_HANDLE','errors':lifecycle_issues})
            continue
        locator_value=raw_path
        status='UNRESOLVED_AT_HANDOFF'
        if raw_path:
            path=Path(str(raw_path)).expanduser()
            if path.exists() and path.is_file():
                actual=_sha256_file(path)
                status='READY_LOCAL_VERIFIED' if declared and actual==declared else ('LOCAL_HASH_MISMATCH' if declared else 'LOCAL_HASH_MISSING')
            else:
                status='LOCAL_FILE_MISSING_AT_HANDOFF'
        binding={
            'asset_id':aid,'role':row.get('role'),
            'locator':{'kind':locator_kind,'value':locator_value},
            'sha256':declared,'handoff_sha256':actual or declared,'handoff_status':status,
            'pixel_lock':bool(row.get('pixel_lock')),
            'allowed_transforms':list(row.get('allowed_transforms') or []),
            'identity_features':list(row.get('identity_features') or []),
        }
        if status=='READY_LOCAL_VERIFIED':
            ready.append(binding)
        else:
            errors.append({'asset_id':aid,'status':status,'locator_kind':locator_kind})
    return ready,errors

'''
text = regex_once(
    text,
    r'def _source_product_bindings\(manifest:dict\[str,Any\]\)->tuple\[list\[dict\[str,Any\]\],list\[dict\[str,Any\]\]\]:.*?(?=def _usable_source_product_assets)',
    new_source_fn,
    'production-source-bindings',
    flags=re.S,
)
text = replace_once(
    text,
    'def apply_production_result(run:dict[str,Any], results:list[dict[str,Any]])->dict[str,Any]:',
    'def apply_production_result(run:dict[str,Any], results:list[dict[str,Any]], remote_artifact_resolver=None)->dict[str,Any]:',
    'production-apply-signature',
)
text = replace_once(
    text,
    '        local.extend(validate_production_receipt(contract_row,r))\n',
    "        local.extend(validate_production_receipt(contract_row,r,remote_artifact_resolver=remote_artifact_resolver,require_remote_verification=bool(r.get('_provider_transport_verification_required'))))\n        local.extend(validate_adapter_result(contract_row,r))\n",
    'production-result-validations',
)
anchor = """        job={
            'job_id':job_id,"""
if anchor not in text:
    raise SystemExit('PATCH_MISS:production-job-anchor')
# Insert adapter transmission after the complete job dictionary, immediately before write_text.
insert_before = """        (d/'job.json').write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
        qkeys=quality.get('required_result_observations',[])"""
insert_block = """        adapter_tx=build_adapter_transmission(job,(row.get('provider_contract') or {}).get('adapter_profile'))
        job['adapter_transmission']=adapter_tx
        row['provider_adapter_transmission']=adapter_tx
        if adapter_tx.get('status')!='READY':
            row['status']='HOLD_ADAPTER_TRANSMISSION'
            row['adapter_transmission_errors']=adapter_tx.get('mapping_errors') or []
            holds.append({'asset_id':aid,'errors':row['adapter_transmission_errors']})
            (d/'job.json').write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
            continue
        if str(job.get('adapter') or '').upper()=='EXTERNAL_ADAPTER':
            required=job['result_contract'].setdefault('required',[])
            if 'adapter_result' not in required: required.append('adapter_result')

        (d/'job.json').write_text(json.dumps(job,ensure_ascii=False,indent=2),encoding='utf-8')
        qkeys=quality.get('required_result_observations',[])"""
text = replace_once(text, insert_before, insert_block, 'production-adapter-transmission')
insert_before = """        (d/'result.template.json').write_text(json.dumps(template,ensure_ascii=False,indent=2),encoding='utf-8')
        index.append({"""
insert_block = """        if str(job.get('adapter') or '').upper()=='EXTERNAL_ADAPTER':
            template['adapter_result']=adapter_result_template(adapter_tx)
        (d/'result.template.json').write_text(json.dumps(template,ensure_ascii=False,indent=2),encoding='utf-8')
        index.append({"""
text = replace_once(text, insert_before, insert_block, 'production-adapter-template')
text = replace_once(
    text,
    'def ingest_provider_job_results(run:dict[str,Any], jobs_root:Path)->dict[str,Any]:',
    'def ingest_provider_job_results(run:dict[str,Any], jobs_root:Path, remote_artifact_resolver=None)->dict[str,Any]:',
    'production-ingest-signature',
)
text = replace_once(
    text,
    "            result['_provider_job_dir']=str(rp.parent)\n            results.append(result)\n",
    "            result['_provider_job_dir']=str(rp.parent)\n            result['_provider_transport_verification_required']=True\n            results.append(result)\n",
    'production-ingest-verification-flag',
)
text = replace_once(
    text,
    '    applied=apply_production_result(run,results)\n',
    '    applied=apply_production_result(run,results,remote_artifact_resolver=remote_artifact_resolver)\n',
    'production-ingest-resolver',
)
write(path, text)

# Version/docs
write('VERSION', '0.6.13\n')

path='SKILL.md'
text=read(path)
text=replace_once(text,'version: 0.6.12-portable-provider-package-production-receipt','version: 0.6.13-provider-transport-integrity','skill-version')
marker='## v0.6.12 可携带 Provider Package + Production Receipt\n'
section='''## v0.6.13 Provider Transport Integrity\n- `PROVIDER_ASSET_HANDLE` 支持结构化 lifecycle：provider / state / expires_at / supersedes_handle / generation / content SHA256；过期、撤销、内容 hash 不一致会在 handoff HOLD。旧字符串 handle 继续兼容，但只具有 `DECLARED_ONLY` 语义。\n- `EXTERNAL_ADAPTER` 现在有统一 Adapter Profile、字段映射、request hash、idempotency key、transmission ID 与 external job acknowledgement contract；统一 portable job 可以映射到真实 Provider API，而不把“已映射”误报为“已调用”。\n- 外部 Provider Job ingestion 对远程输出 URI 要求 resolver 提供真实字节并重算 SHA256；没有 resolver、下载失败或 hash 不一致均进入 Review。Runtime 本身不伪装拥有网络权限。\n- 新增可验证远程 artifact recovery：下载/解析后的字节必须先匹配 receipt SHA256，再写入本地恢复副本并再次校验。\n\n'''
if marker not in text: raise SystemExit('PATCH_MISS:skill-section-marker')
text=text.replace(marker,section+marker,1)
write(path,text)

path='CHANGELOG.md'
text=read(path)
entry='''## 0.6.13 — Provider Transport Integrity\n- Added structured provider-asset-handle lifecycle validation with expiry, terminal states and refresh lineage while preserving legacy declared-only string handles.\n- Added normalized adapter transmission profiles with deterministic field mapping, request hash, idempotency key and external-job acknowledgement binding.\n- Remote provider output URIs are no longer treated as byte-verified during real job ingestion without an injected resolver; resolved bytes are rehashed against the production receipt.\n- Added verified remote-artifact recovery that persists only hash-matching bytes.\n\n'''
if not text.startswith('## 0.6.12'): raise SystemExit('PATCH_MISS:changelog-head')
write(path,entry+text)

write('CHANGELOG_V0613.md','''# CBCC v0.6.13 — Provider Transport Integrity\n\n## Real breaks fixed\n1. Provider asset handles previously had no executable lifecycle semantics beyond a declared handle + SHA256.\n2. Remote receipt URIs could carry a declared hash without CBCC observing and hashing the returned bytes.\n3. `EXTERNAL_ADAPTER` existed as a registry label without a normalized request/idempotency/external-job acknowledgement contract.\n\n## Implementation\n- `runtime/cbcc/provider_transport.py` owns handle lifecycle, adapter mapping/transmission binding, remote artifact verification and recovery.\n- Structured handles may declare provider, state, issued/verified/expiry time, predecessor and generation. Refreshes rotate handles while preserving source content SHA256 lineage. Legacy string handles remain compatible but explicitly declared-only.\n- External adapter transmissions map the portable job contract to a vendor-neutral request envelope and bind it with request hash + idempotency key + transmission ID. This is a transport contract, not a claim that an API call occurred.\n- Real provider-job ingestion requires remote output bytes to be resolved and SHA256-verified. The core runtime accepts an injected resolver instead of embedding credentials or a network client.\n- Remote recovery writes only verified bytes and rechecks the local recovered copy.\n\n## Boundary\nProvider-specific credentials, upload APIs, polling clients and download authentication remain adapter/executor responsibilities. v0.6.13 defines the executable transport contract they must satisfy.\n''')

path='CURRENT_HANDOFF.md'
text=read(path)
text=replace_once(text,'# CBCC v0.6.12 CURRENT HANDOFF','# CBCC v0.6.13 CURRENT HANDOFF','handoff-title')
text=replace_once(text,'当前版本：`0.6.12-portable-provider-package-production-receipt`。','当前版本：`0.6.13-provider-transport-integrity`。','handoff-version')
old='''## 下一步唯一主任务\n**继续审计真实 Provider Adapter 的传输边界：PROVIDER_ASSET_HANDLE 的获取/刷新/失效语义、远程输出 URI 的可验证 hash/下载回收、以及不同 Provider adapter 如何把统一 portable job contract 映射到真实 API 请求与回执。只修真实断链。**'''
new='''## v0.6.13 已完成\n1. `PROVIDER_ASSET_HANDLE` 增加结构化 lifecycle：provider/state/expiry/supersedes/generation/content SHA256；失效、过期或内容 hash 不一致在 handoff HOLD。\n2. 旧字符串 handle 保持兼容，但明确为 `DECLARED_ONLY`，不再伪称已远程验证。\n3. `EXTERNAL_ADAPTER` 增加统一 Adapter Profile → vendor request 映射、request hash、idempotency key、transmission ID 和 external job acknowledgement。\n4. 真实 provider-job ingestion 遇到远程 URI 必须由 adapter/resolver 提供实际字节并重新计算 SHA256；无 resolver / 下载失败 / hash 不匹配进入 Review。\n5. 新增远程输出 recovery，只有 hash 匹配的实际字节才能落入恢复副本。\n\n## 下一步唯一主任务\n**把 transport contract 接到真实 Provider Adapter Executor 生命周期：upload/create-or-refresh asset → submit idempotent job → poll/resume → download/resolve outputs → production receipt。凭证与网络客户端保持 adapter 外置；优先实现可插拔 executor protocol + 一个可验证的 mock/reference adapter，再根据实际接入的 Provider 增加具体 API profile。**'''
text=replace_once(text,old,new,'handoff-next-task')
write(path,text)

print('v0.6.13 patch applied')
