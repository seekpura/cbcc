#!/usr/bin/env python3
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'runtime/cbcc/production_parameter_closure.py'
s=p.read_text(encoding='utf-8')
old="""    text = _blob({\n        'asset_type': asset.get('asset_type'),\n        'production_mode': asset.get('production_mode'),\n        'carrier': art.get('visual_carrier') or card.get('visual_carrier') or (card.get('information_assetization') or {}).get('representation'),\n        'camera': art.get('camera_or_view'),\n        'lighting': art.get('lighting'),\n    })\n"""
new="""    # Search authored values only. Field names such as `camera`/`lighting` must never make\n    # a graphic/illustration asset look photographic just because the schema has those slots.\n    text = _blob([\n        asset.get('asset_type'),\n        asset.get('production_mode'),\n        art.get('visual_carrier') or card.get('visual_carrier') or (card.get('information_assetization') or {}).get('representation'),\n        art.get('camera_or_view'),\n        art.get('lighting'),\n    ])\n"""
if old not in s:
    raise SystemExit('route detection anchor not found')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('patched route detection to authored values only')
