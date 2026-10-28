from io import BytesIO
import json

from cbcc.action_transports import plugin_openapi_descriptor
from cbcc.host_actions import ACTION_ADAPTER_LIST, ProviderActionDispatcher
from cbcc.plugin_http import create_plugin_http_application


class FakeSurface:
    def list_adapters(self, **kwargs):
        return {'status': 'ADAPTERS_DISCOVERED', 'count': 0, 'adapters': []}


def _path_for(action_id):
    for path, item in plugin_openapi_descriptor()['paths'].items():
        if (item.get('post') or {}).get('x-cbcc-action-id') == action_id:
            return path
    raise AssertionError(action_id)


def test_authorization_resolver_failure_is_stable_and_redacted():
    def resolver(_context):
        raise RuntimeError('do-not-leak-host-auth-secret')

    app = create_plugin_http_application(
        ProviderActionDispatcher(FakeSurface()),
        authorization_resolver=resolver,
    )
    raw = b'{}'
    environ = {
        'REQUEST_METHOD': 'POST',
        'PATH_INFO': _path_for(ACTION_ADAPTER_LIST),
        'CONTENT_TYPE': 'application/json',
        'CONTENT_LENGTH': str(len(raw)),
        'wsgi.input': BytesIO(raw),
    }
    captured = {}

    def start_response(status, headers):
        captured['status'] = status
        captured['headers'] = headers

    body = b''.join(app(environ, start_response)).decode('utf-8')
    payload = json.loads(body)
    assert captured['status'].startswith('500 ')
    assert payload['errors'] == [{'code': 'AUTHORIZATION_RESOLVER_FAILED'}]
    assert 'do-not-leak-host-auth-secret' not in body
