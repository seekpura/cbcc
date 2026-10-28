from pathlib import Path

path = Path('runtime/cbcc/host_actions.py')
text = path.read_text(encoding='utf-8')
old = """def forbidden_secret_fields(payload: Any, prefix: str = '') -> list[str]:
    \"\"\"Return forbidden credential-bearing field paths from an action payload.

    The policy is intentionally field based. Credential values belong to the v0.6.16 runtime-context
    resolver, never to host action/MCP/plugin JSON payloads.
    \"\"\"
    found: list[str] = []
    if isinstance(payload, dict):
        for raw_key, value in payload.items():
            key = _normalize_key(raw_key)
            path = f'{prefix}.{raw_key}' if prefix else str(raw_key)
            if key in _FORBIDDEN_SECRET_KEYS:
                found.append(path)
            found.extend(forbidden_secret_fields(value, path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            path = f'{prefix}[{index}]' if prefix else f'[{index}]'
            found.extend(forbidden_secret_fields(value, path))
    return list(dict.fromkeys(found))
"""
new = """def _credential_like_key(key: str) -> bool:
    if key in _FORBIDDEN_SECRET_KEYS:
        return True
    suffixes = (
        '_api_key', '_api_token', '_access_token', '_refresh_token', '_token',
        '_secret', '_client_secret', '_password', '_passwd', '_credentials',
        '_credential', '_authorization', '_auth_header', '_private_key',
        '_access_key', '_secret_key', '_session_token',
    )
    prefixes = ('authorization_', 'bearer_', 'secret_', 'password_')
    return key.endswith(suffixes) or key.startswith(prefixes)


def forbidden_secret_fields(payload: Any, prefix: str = '') -> list[str]:
    \"\"\"Return credential-bearing field paths from an action payload.

    Credential-like keys are rejected even when namespaced (for example provider_api_key or
    oauth_token). Credential values belong only to the v0.6.16 runtime-context resolver, never to
    host action/MCP/plugin JSON payloads.
    \"\"\"
    found: list[str] = []
    if isinstance(payload, dict):
        for raw_key, value in payload.items():
            key = _normalize_key(raw_key)
            path = f'{prefix}.{raw_key}' if prefix else str(raw_key)
            if _credential_like_key(key):
                found.append(path)
            found.extend(forbidden_secret_fields(value, path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            path = f'{prefix}[{index}]' if prefix else f'[{index}]'
            found.extend(forbidden_secret_fields(value, path))
    return list(dict.fromkeys(found))
"""
if old not in text:
    if 'def _credential_like_key' in text:
        raise SystemExit(0)
    raise SystemExit('target block not found')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
