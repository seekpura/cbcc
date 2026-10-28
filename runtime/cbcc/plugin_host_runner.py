from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import importlib
import json
import os

from .action_transports import PluginActionTransportAdapter
from .host_actions import ActionAuthorization, ProviderActionDispatcher
from .plugin_http_host import (
    DEFAULT_MAX_BODY_BYTES,
    DEFAULT_PENDING_RETRY_AFTER_SECONDS,
    HTTPRequestContext,
    PluginHTTPApplication,
    serve_plugin_http,
)
from .provider_surface import HOST_MODULE_ENV, provider_execution_surface_from_environment

VERSION = '0.6.19-plugin-http-host-runner'
ACTION_AUTH_MODULE_ENV = 'CBCC_ACTION_AUTH_MODULE'


def _authorization_from_value(value: Any) -> ActionAuthorization | None:
    if value is None:
        return None
    if isinstance(value, ActionAuthorization):
        return value
    if isinstance(value, dict):
        actor_id = str(value.get('actor_id') or 'host')
        scopes = value.get('scopes') or []
        if not isinstance(scopes, (list, tuple, set, frozenset)):
            raise TypeError('authorization scopes must be a sequence')
        return ActionAuthorization.from_scopes([str(item) for item in scopes], actor_id=actor_id)
    raise TypeError('authorization resolver must return ActionAuthorization, mapping, or None')


def load_authorization_resolver(module_name: str | None):
    name = str(module_name or '').strip()
    if not name:
        return None
    module = importlib.import_module(name)
    resolver = getattr(module, 'create_action_authorization', None)
    if resolver is None:
        return None
    if not callable(resolver):
        raise TypeError('host module create_action_authorization must be callable')

    def _resolve(request: HTTPRequestContext, operation_id: str, required_scope: str) -> ActionAuthorization | None:
        value = resolver(
            request_context=request,
            operation_id=operation_id,
            required_scope=required_scope,
        )
        return _authorization_from_value(value)

    return _resolve


def build_plugin_http_application_from_environment(
    *,
    env: dict[str, str] | None = None,
    max_body_bytes: int = DEFAULT_MAX_BODY_BYTES,
    server_url: str = '/',
    pending_retry_after_seconds: int = DEFAULT_PENDING_RETRY_AFTER_SECONDS,
) -> PluginHTTPApplication:
    values = os.environ if env is None else env
    surface = provider_execution_surface_from_environment(env=values)
    dispatcher = ProviderActionDispatcher(surface)
    adapter = PluginActionTransportAdapter(dispatcher)
    auth_module_name = str(values.get(ACTION_AUTH_MODULE_ENV) or values.get(HOST_MODULE_ENV) or '').strip()
    authorization_resolver = load_authorization_resolver(auth_module_name)
    return PluginHTTPApplication(
        adapter,
        authorization_resolver=authorization_resolver,
        max_body_bytes=max_body_bytes,
        server_url=server_url,
        pending_retry_after_seconds=pending_retry_after_seconds,
    )


def runner_contract() -> dict[str, Any]:
    return {
        'version': VERSION,
        'startup': 'python -m cbcc.plugin_host_runner',
        'provider_host_module_environment_variable': HOST_MODULE_ENV,
        'action_authorization_module_environment_variable': ACTION_AUTH_MODULE_ENV,
        'environment_values_are_module_names_not_credentials': True,
        'cli_secret_arguments': 'FORBIDDEN',
        'composition_chain': 'provider_execution_surface_from_environment -> ProviderActionDispatcher -> PluginActionTransportAdapter -> PluginHTTPApplication',
        'transport_host_direct_provider_runtime_access': False,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='cbcc-plugin-http-host')
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8787)
    parser.add_argument('--max-body-bytes', type=int, default=DEFAULT_MAX_BODY_BYTES)
    parser.add_argument('--server-url', default='/')
    parser.add_argument('--pending-retry-after-seconds', type=int, default=DEFAULT_PENDING_RETRY_AFTER_SECONDS)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    application = build_plugin_http_application_from_environment(
        max_body_bytes=max(1, int(args.max_body_bytes)),
        server_url=str(args.server_url or '/'),
        pending_retry_after_seconds=max(0, int(args.pending_retry_after_seconds)),
    )
    startup = {
        'status': 'STARTING',
        'version': VERSION,
        'bind': args.bind,
        'port': int(args.port),
        'health': '/healthz',
        'schema': '/schema/openapi.json',
        'runner_contract': runner_contract(),
    }
    print(json.dumps(startup, ensure_ascii=False), flush=True)
    try:
        serve_plugin_http(application, bind=str(args.bind), port=int(args.port))
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
