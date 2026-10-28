from __future__ import annotations

import argparse

from .host_actions import ProviderActionDispatcher
from .mcp_stdio import authorization_resolver_from_environment, run_stdio_server
from .provider_surface import provider_execution_surface_from_environment


def build_arg_parser() -> argparse.ArgumentParser:
    # stdio is intentionally configuration-light: credentials and authorization remain host-owned
    # environment/module concerns, never command-line arguments.
    return argparse.ArgumentParser(prog='cbcc-mcp-stdio')


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    parser.parse_args(argv)
    surface = provider_execution_surface_from_environment()
    dispatcher = ProviderActionDispatcher(surface)
    authorization_resolver = authorization_resolver_from_environment()
    run_stdio_server(dispatcher, authorization_resolver=authorization_resolver)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
