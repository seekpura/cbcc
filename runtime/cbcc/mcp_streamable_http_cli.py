from __future__ import annotations

import argparse

from .host_actions import ProviderActionDispatcher
from .mcp_streamable_http import (
    DEFAULT_MAX_REQUEST_BYTES,
    allowed_origins_from_environment,
    http_authorization_resolver_from_environment,
    make_mcp_streamable_http_server,
)
from .provider_surface import provider_execution_surface_from_environment


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='cbcc-mcp-http')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8788)
    parser.add_argument('--endpoint', default='/mcp')
    parser.add_argument('--max-request-bytes', type=int, default=DEFAULT_MAX_REQUEST_BYTES)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    surface = provider_execution_surface_from_environment()
    dispatcher = ProviderActionDispatcher(surface)
    server = make_mcp_streamable_http_server(
        dispatcher,
        host=str(args.host),
        port=int(args.port),
        endpoint_path=str(args.endpoint),
        max_request_bytes=max(1, int(args.max_request_bytes)),
        authorization_resolver=http_authorization_resolver_from_environment(),
        allowed_origins=allowed_origins_from_environment(),
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
