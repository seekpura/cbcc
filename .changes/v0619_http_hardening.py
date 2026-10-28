from pathlib import Path

path = Path('runtime/cbcc/plugin_http.py')
text = path.read_text(encoding='utf-8')
old = """        try:\n            authorization = _coerce_authorization(self.authorization_resolver(context))\n        except Exception as exc:\n            return self._transport_error(start_response, 500, 'AUTHORIZATION_RESOLVER_FAILED', str(exc))\n"""
new = """        try:\n            authorization = _coerce_authorization(self.authorization_resolver(context))\n        except Exception:\n            return self._transport_error(start_response, 500, 'AUTHORIZATION_RESOLVER_FAILED')\n"""
if old in text:
    text = text.replace(old, new)
elif new not in text:
    raise SystemExit('expected authorization resolver block not found')
path.write_text(text, encoding='utf-8')
