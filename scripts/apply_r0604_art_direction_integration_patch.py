from pathlib import Path

p = Path('runtime/cbcc/compiler.py')
s = p.read_text(encoding='utf-8')
old = """    if 'creative_directions' in request:
        council_directions=request.get('creative_directions')
    elif 'directions' in creative_scope:
        council_directions=agent_creative_directions(agent_plan)
    else:
        council_directions=None
"""
new = """    if 'creative_directions' in request:
        council_directions=request.get('creative_directions')
    elif any(key in creative_scope for key in ('directions','asset_art_directions','per_asset_art_directions')):
        council_directions=agent_creative_directions(agent_plan)
    else:
        council_directions=None
"""
if s.count(old) != 1:
    raise SystemExit(f'expected compiler creative direction presence block once, found {s.count(old)}')
p.write_text(s.replace(old, new), encoding='utf-8')
