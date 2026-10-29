#!/usr/bin/env python3
from pathlib import Path

p=Path(__file__).with_name('apply_v0636_seven_tool_continuity.py')
s=p.read_text(encoding='utf-8')
s=s.replace("    style = '''<style id=\"cbcc-commerce-brain-style\">", "    style = \"\"\"<style id=\"cbcc-commerce-brain-style\">")
s=s.replace("</style>'''\n    return style + '<section id=\"commercial-brain\"", "</style>\"\"\"\n    return style + '<section id=\"commercial-brain\"")
p.write_text(s,encoding='utf-8')
print('repaired v0.6.36 migration quoting')
