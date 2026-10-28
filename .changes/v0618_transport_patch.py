from pathlib import Path

path = Path('runtime/cbcc/action_transports.py')
text = path.read_text(encoding='utf-8')
text = text.replace("server_url: str = 'https://host.invalid'", "server_url: str = '/'")
text = text.replace("def descriptor(self, *, server_url: str = 'https://host.invalid')", "def descriptor(self, *, server_url: str = '/')")
path.write_text(text, encoding='utf-8')
