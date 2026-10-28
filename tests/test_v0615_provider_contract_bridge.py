from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.providers import provider_contract


def test_external_provider_contract_exposes_single_bridge_execution_chain():
    asset = {
        'asset_id': 'AST-V0615-CONTRACT',
        'production_mode': 'REAL_PRODUCT_COMPOSITE',
        'product_fidelity': 'LOCKED_PIXEL',
    }
    contract = provider_contract('EPV_ADAPTER', 'REAL_PRODUCT_COMPOSITE', asset)
    assert contract['status'] == 'READY'
    assert contract['adapter'] == 'EXTERNAL_ADAPTER'
    assert contract['executor_contract']['protocol'] == 'ProviderExecutor'
    bridge = contract['executor_bridge_contract']
    assert bridge['version'].startswith('0.6.15-')
    assert bridge['registry']['credential_storage'] == 'FORBIDDEN'
    assert bridge['single_execution_chain'].endswith('Production Receipt → Ingest')
    assert set(bridge['bridge_semantics']) == {'RETRY', 'BACKOFF', 'RATE_LIMIT', 'CANCEL', 'RECONCILE'}
