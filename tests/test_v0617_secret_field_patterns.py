from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))

from cbcc.host_actions import forbidden_secret_fields


def test_namespaced_and_nested_credential_fields_are_rejected():
    payload = {
        'provider_api_key': 'x',
        'nested': {
            'oauthToken': 'y',
            'safe_tokenizer_name': 'allowed',
        },
        'items': [
            {'clientSecret': 'z'},
            {'normal_field': 'ok'},
        ],
    }
    found = forbidden_secret_fields(payload)
    assert 'provider_api_key' in found
    assert 'nested.oauthToken' in found
    assert 'items[0].clientSecret' in found
    assert 'nested.safe_tokenizer_name' not in found
