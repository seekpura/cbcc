from __future__ import annotations

import argparse

from .host_actions import ProviderActionDispatcher
from .plugin_http import (
    ACTION_AUTH_MODULE_ENV,
    DEFAULT_MAX_REQUEST_BYTES,
    authorization_resolver_from_environment,
    serve_plugin_http_host,
)
from .provider_surface import provider_execution_surface_from_environment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='cbcc-plugin-http')
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8787)
    parser.add_argument('--max-request-bytes', type=int, default=DEFAULT_MAX_REQUEST_BYTES)
    parser.add_argument('--retry-after-seconds', type=int, default=1)
    parser.add_argument('--server-url', default='/')
    args = parser.parse_args(argv)

    surface = provider_execution_surface_from_environment()
    dispatcher = ProviderActionDispatcher(surface)
    authorization_resolver = authorization_resolver_from_environment()
    serve_plugin_http_host(
        dispatcher,
        host=args.bind,
        port=args.port,
        authorization_resolver=authorization_resolver,
        max_request_bytes=max(1, args.max_request_bytes),
        retry_after_seconds=max(0, args.retry_after_seconds),
        server_url=args.server_url,
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
