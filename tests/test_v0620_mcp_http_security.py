import argparse

import pytest

from cbcc.mcp_host_cli import build_http_transport_security


def test_loopback_security_uses_exact_port_allowlist_without_wildcards():
    security = build_http_transport_security(bind='127.0.0.1', port=8000)
    assert security.enable_dns_rebinding_protection is True
    assert security.allowed_hosts == ['127.0.0.1:8000', 'localhost:8000', '[::1]:8000']
    assert security.allowed_origins == [
        'http://127.0.0.1:8000',
        'http://localhost:8000',
        'http://[::1]:8000',
    ]
    assert all(not value.endswith(':*') for value in security.allowed_hosts + security.allowed_origins)


def test_public_bind_requires_explicit_host_allowlist():
    with pytest.raises(SystemExit):
        build_http_transport_security(bind='0.0.0.0', port=8000, parser=argparse.ArgumentParser(add_help=False))


def test_public_bind_accepts_exact_allowlist():
    security = build_http_transport_security(
        bind='0.0.0.0',
        port=8000,
        allowed_hosts=['mcp.example.com', 'mcp.example.com:443'],
        allowed_origins=['https://app.example.com'],
    )
    assert security.enable_dns_rebinding_protection is True
    assert security.allowed_hosts == ['mcp.example.com', 'mcp.example.com:443']
    assert security.allowed_origins == ['https://app.example.com']


def test_wildcard_port_patterns_are_rejected():
    parser = argparse.ArgumentParser(add_help=False)
    with pytest.raises(SystemExit):
        build_http_transport_security(
            bind='0.0.0.0',
            port=8000,
            allowed_hosts=['mcp.example.com:*'],
            parser=parser,
        )


def test_explicit_proxy_owned_host_validation_can_disable_sdk_check():
    security = build_http_transport_security(
        bind='0.0.0.0',
        port=8000,
        disable_dns_rebinding_protection=True,
    )
    assert security.enable_dns_rebinding_protection is False
