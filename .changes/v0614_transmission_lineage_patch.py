from pathlib import Path

executor_path = Path('runtime/cbcc/provider_executor.py')
text = executor_path.read_text(encoding='utf-8')
text = text.replace(
    "state['executable_source_binding_hash'] = executable_job.get('source_binding_hash')",
    "state['executable_source_binding_hash'] = executable_job.get('provider_execution_source_binding_hash')",
)
old = """        transmission = build_adapter_transmission(executable_job, profile)
        if transmission.get('status') != 'READY':
            raise ValueError('adapter transmission not ready')
        state['transmission'] = transmission
"""
new = """        transmission = build_adapter_transmission(executable_job, profile)
        if transmission.get('status') != 'READY':
            raise ValueError('adapter transmission not ready')
        upstream_transmission = job.get('adapter_transmission') or {}
        transmission['parent_transmission_binding'] = {
            'transmission_id': upstream_transmission.get('transmission_id'),
            'request_hash': upstream_transmission.get('request_hash'),
            'idempotency_key': upstream_transmission.get('idempotency_key'),
        }
        transmission['portable_source_binding_hash'] = job.get('source_binding_hash')
        transmission['provider_execution_source_binding_hash'] = executable_job.get('provider_execution_source_binding_hash')
        state['transmission'] = transmission
"""
if old not in text:
    raise SystemExit('executor transmission block not found')
text = text.replace(old, new)
old = """        'source_binding_hash': job.get('source_binding_hash'),
        'adapter_result': adapter_result,
        'production_receipt': receipt,
"""
new = """        'source_binding_hash': job.get('source_binding_hash'),
        'provider_execution_source_binding_hash': job.get('provider_execution_source_binding_hash'),
        'provider_execution_transmission': transmission,
        'adapter_result': adapter_result,
        'production_receipt': receipt,
"""
if old not in text:
    raise SystemExit('executor result block not found')
executor_path.write_text(text.replace(old, new), encoding='utf-8')

transport_path = Path('runtime/cbcc/provider_transport.py')
text = transport_path.read_text(encoding='utf-8')
old = """def validate_adapter_result(row: dict[str, Any], result: dict[str, Any]) -> list[str]:
    contract = row.get('provider_contract') or {}
    adapter = str(contract.get('adapter') or '').upper()
    transmission = row.get('provider_adapter_transmission') or {}
    if adapter != 'EXTERNAL_ADAPTER' and str(transmission.get('adapter') or '').upper() != 'EXTERNAL_ADAPTER':
        return []
    issues: list[str] = []
    if not transmission:
        return ['ADAPTER_TRANSMISSION_CONTRACT_MISSING']
    if transmission.get('status') != 'READY':
        issues.append('ADAPTER_TRANSMISSION_NOT_READY')
    ack = result.get('adapter_result')
    if not isinstance(ack, dict):
        return list(dict.fromkeys(issues + ['ADAPTER_RESULT_MISSING']))
    for key in ['transmission_id', 'request_hash', 'idempotency_key']:
        if ack.get(key) != transmission.get(key):
            issues.append('ADAPTER_RESULT_BINDING_MISMATCH:' + key)
    if not ack.get('external_job_id'):
        issues.append('ADAPTER_EXTERNAL_JOB_ID_MISSING')
    raw_status = str(ack.get('status') or '').upper()
    if not raw_status:
        issues.append('ADAPTER_EXTERNAL_STATUS_MISSING')
    else:
        status_map = (transmission.get('external_job_contract') or {}).get('status_map') or {}
        normalized = status_map.get(raw_status)
        if not normalized:
            issues.append('ADAPTER_EXTERNAL_STATUS_UNMAPPED')
        elif normalized == 'FAILED':
            issues.append('ADAPTER_EXTERNAL_JOB_FAILED')
    return list(dict.fromkeys(issues))
"""
new = """def validate_adapter_result(row: dict[str, Any], result: dict[str, Any]) -> list[str]:
    contract = row.get('provider_contract') or {}
    adapter = str(contract.get('adapter') or '').upper()
    portable_transmission = row.get('provider_adapter_transmission') or {}
    execution_transmission = result.get('provider_execution_transmission')
    transmission = execution_transmission if isinstance(execution_transmission, dict) else portable_transmission
    if adapter != 'EXTERNAL_ADAPTER' and str(portable_transmission.get('adapter') or '').upper() != 'EXTERNAL_ADAPTER':
        return []
    issues: list[str] = []
    if not portable_transmission:
        return ['ADAPTER_TRANSMISSION_CONTRACT_MISSING']
    if portable_transmission.get('status') != 'READY':
        issues.append('ADAPTER_TRANSMISSION_NOT_READY')

    if isinstance(execution_transmission, dict):
        parent = execution_transmission.get('parent_transmission_binding') or {}
        for key in ['transmission_id', 'request_hash', 'idempotency_key']:
            if parent.get(key) != portable_transmission.get(key):
                issues.append('ADAPTER_EXECUTION_PARENT_BINDING_MISMATCH:' + key)
        vendor_request = execution_transmission.get('vendor_request') or {}
        if stable_hash(vendor_request) != execution_transmission.get('request_hash'):
            issues.append('ADAPTER_EXECUTION_REQUEST_HASH_MISMATCH')
        if execution_transmission.get('portable_source_binding_hash') and row.get('provider_job_source_binding_hash') and execution_transmission.get('portable_source_binding_hash') != row.get('provider_job_source_binding_hash'):
            issues.append('ADAPTER_EXECUTION_PORTABLE_SOURCE_BINDING_MISMATCH')
        if execution_transmission.get('status') != 'READY':
            issues.append('ADAPTER_EXECUTION_TRANSMISSION_NOT_READY')

    ack = result.get('adapter_result')
    if not isinstance(ack, dict):
        return list(dict.fromkeys(issues + ['ADAPTER_RESULT_MISSING']))
    for key in ['transmission_id', 'request_hash', 'idempotency_key']:
        if ack.get(key) != transmission.get(key):
            issues.append('ADAPTER_RESULT_BINDING_MISMATCH:' + key)
    if not ack.get('external_job_id'):
        issues.append('ADAPTER_EXTERNAL_JOB_ID_MISSING')
    raw_status = str(ack.get('status') or '').upper()
    if not raw_status:
        issues.append('ADAPTER_EXTERNAL_STATUS_MISSING')
    else:
        status_map = (transmission.get('external_job_contract') or {}).get('status_map') or {}
        normalized = status_map.get(raw_status)
        if not normalized:
            issues.append('ADAPTER_EXTERNAL_STATUS_UNMAPPED')
        elif normalized == 'FAILED':
            issues.append('ADAPTER_EXTERNAL_JOB_FAILED')
    return list(dict.fromkeys(issues))
"""
if old not in text:
    raise SystemExit('transport validator block not found')
transport_path.write_text(text.replace(old, new), encoding='utf-8')
