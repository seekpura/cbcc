from __future__ import annotations

import argparse

import anyio
from mcp.server.transport_security import TransportSecuritySettings

from .host_actions import ProviderActionDispatcher
from .mcp_host import (
    SUPPORTED_TRANSPORTS,
    authorization_resolver_from_environment,
    create_mcp_host,
)
from .provider_surface import provider_execution_surface_from_environment


_LOOPBACK_BINDS = {'127.0.0.1', 'localhost', '::1'}


def _reject_wildcard_port(values: list[str], parser: argparse.ArgumentParser, option: str) -> None:
    bad = [value for value in values if str(value).strip().endswith(':*')]
    if bad:
        parser.error(
            f'{option} does not accept :* wildcard ports; use exact host/origin values because '
            'the currently validated MCP SDK has a known wildcard-port matching edge case'
        )


def build_http_transport_security(
    *,
    bind: str,
    port: int,
    allowed_hosts: list[str] | None = None,
    allowed_origins: list[str] | None = None,
    disable_dns_rebinding_protection: bool = False,
    parser: argparse.ArgumentParser | None = None,
) -> TransportSecuritySettings:
    parser = parser or argparse.ArgumentParser(add_help=False)
    hosts = [str(value).strip() for value in (allowed_hosts or []) if str(value).strip()]
    origins = [str(value).strip() for value in (allowed_origins or []) if str(value).strip()]
    _reject_wildcard_port(hosts, parser, '--allowed-host')
    _reject_wildcard_port(origins, parser, '--allowed-origin')

    if disable_dns_rebinding_protection:
        return TransportSecuritySettings(enable_dns_rebinding_protection=False)

    if bind in _LOOPBACK_BINDS and not hosts:
        hosts = [f'127.0.0.1:{port}', f'localhost:{port}', f'[::1]:{port}']
        origins = origins or [
            f'http://127.0.0.1:{port}',
            f'http://localhost:{port}',
            f'http://[::1]:{port}',
        ]
    elif not hosts:
        parser.error(
            'non-loopback Streamable HTTP requires at least one exact --allowed-host, or explicit '
            '--disable-dns-rebinding-protection when a trusted reverse proxy owns Host validation'
        )

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=hosts,
        allowed_origins=origins,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='cbcc-mcp-host')
    parser.add_argument('--transport', choices=SUPPORTED_TRANSPORTS, default='stdio')
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--path', default='/mcp')
    parser.add_argument('--max-request-body-size', type=int, default=4 * 1024 * 1024)
    parser.add_argument('--stateful-http', action='store_true')
    parser.add_argument('--sse-response', action='store_true')
    parser.add_argument('--allowed-host', action='append', default=[])
    parser.add_argument('--allowed-origin', action='append', default=[])
    parser.add_argument('--disable-dns-rebinding-protection', action='store_true')
    args = parser.parse_args(argv)

    if not 1 <= int(args.port) <= 65535:
        parser.error('--port must be between 1 and 65535')

    surface = provider_execution_surface_from_environment()
    dispatcher = ProviderActionDispatcher(surface)
    authorization_resolver = authorization_resolver_from_environment()
    host = create_mcp_host(dispatcher, authorization_resolver=authorization_resolver)

    if args.transport == 'stdio':
        anyio.run(host.run_stdio_async)
        return 0

    security = build_http_transport_security(
        bind=args.bind,
        port=args.port,
        allowed_hosts=args.allowed_host,
        allowed_origins=args.allowed_origin,
        disable_dns_rebinding_protection=args.disable_dns_rebinding_protection,
        parser=parser,
    )

    import uvicorn

    app = host.streamable_http_app(
        host=args.bind,
        path=args.path,
        json_response=not args.sse_response,
        stateless_http=not args.stateful_http,
        max_request_body_size=max(1, args.max_request_body_size),
        transport_security=security,
    )
    uvicorn.run(app, host=args.bind, port=args.port)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
