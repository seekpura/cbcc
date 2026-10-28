from __future__ import annotations

import argparse

import anyio

from .host_actions import ProviderActionDispatcher
from .mcp_host import (
    MCP_AUTH_MODULE_ENV,
    SUPPORTED_TRANSPORTS,
    authorization_resolver_from_environment,
    create_mcp_host,
)
from .provider_surface import provider_execution_surface_from_environment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='cbcc-mcp-host')
    parser.add_argument('--transport', choices=SUPPORTED_TRANSPORTS, default='stdio')
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--path', default='/mcp')
    parser.add_argument('--max-request-body-size', type=int, default=4 * 1024 * 1024)
    parser.add_argument('--stateful-http', action='store_true')
    parser.add_argument('--sse-response', action='store_true')
    args = parser.parse_args(argv)

    surface = provider_execution_surface_from_environment()
    dispatcher = ProviderActionDispatcher(surface)
    authorization_resolver = authorization_resolver_from_environment()
    host = create_mcp_host(dispatcher, authorization_resolver=authorization_resolver)

    if args.transport == 'stdio':
        anyio.run(host.run_stdio_async)
        return 0

    import uvicorn

    app = host.streamable_http_app(
        host=args.bind,
        path=args.path,
        json_response=not args.sse_response,
        stateless_http=not args.stateful_http,
        max_request_body_size=max(1, args.max_request_body_size),
    )
    uvicorn.run(app, host=args.bind, port=max(1, args.port))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
