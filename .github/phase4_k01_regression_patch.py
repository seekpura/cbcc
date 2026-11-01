from pathlib import Path

path = Path('runtime/cbcc/portfolio_visual_authority.py')
text = path.read_text(encoding='utf-8')
old = """        'production_route': art.get('production_route'),
        'camera_or_view': art.get('camera_or_view'),
        'focal_length_mm': art.get('focal_length_mm'),
"""
new = """        'production_route': art.get('production_route'),
        # camera_or_view is a composition/framing label. It is not, by itself, proof that
        # this object is a photographic production route; explicit photo carrier/mode or
        # concrete capture fields below remain authoritative activation signals.
        'focal_length_mm': art.get('focal_length_mm'),
"""
if text.count(old) != 1:
    raise SystemExit(f'expected exactly one photographic-route candidate block, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
