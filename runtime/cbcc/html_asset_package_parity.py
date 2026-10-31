from __future__ import annotations
from pathlib import Path
from typing import Any
import json,re


def _data(html:str, package:Path|None=None)->dict[str,Any]:
    # Legacy function-based workspace.
    m=re.search(r'\bconst\s+DATA\s*=\s*',html)
    if m:
        try:
            value,_=json.JSONDecoder().raw_decode(html[m.end():])
            if isinstance(value,dict):return value
        except Exception:pass
    # v0.6.72 self-contained Human workspaces. Accept both the early Lazy id and the final
    # single-payload id so compatibility tests do not force the final exporter back to an older shape.
    for payload_id in ('cbcc-canonical-payload-v0672','cbcc-canonical-data-v0672'):
        m=re.search(rf'<script[^>]+id=["\']{re.escape(payload_id)}["\'][^>]*>(.*?)</script>',html,flags=re.S)
        if m:
            try:
                value=json.loads(m.group(1))
                if isinstance(value,dict):return value
            except Exception:pass
    # Final package also persists the exact canonical payload as a machine authority.
    if package is not None:
        p=Path(package)/'CANONICAL_HUMAN_DATA.json'
        if p.exists():
            try:
                value=json.loads(p.read_text(encoding='utf-8'))
                if isinstance(value,dict):return value
            except Exception:pass
    return {}
def _json(path:Path)->Any:
    try:return json.loads(path.read_text(encoding='utf-8'))
    except Exception:return None
def _text_first(root:Path,names:tuple[str,...])->str|None:
    for name in names:
        p=root/name
        if p.exists():return p.read_text(encoding='utf-8',errors='ignore').strip()
    return None
def audit_html_asset_package_parity(package:Path)->list[dict[str,Any]]:
    package=Path(package);html=package/'index.html';root=package/'asset_packages'
    if not html.exists() or not root.exists():return []
    data=_data(html.read_text(encoding='utf-8',errors='ignore'),package);assets=data.get('assets') if isinstance(data,dict) else None
    if not isinstance(assets,list):return [{'code':'HTML_ASSET_DATA_MISSING','why':'asset_packages exist but neither legacy const DATA nor v0.6.72 canonical payload exposes assets.'}]
    by_id={str(a.get('id') or a.get('asset_id') or ''):a for a in assets if isinstance(a,dict)};issues=[]
    for d in sorted(x for x in root.iterdir() if x.is_dir()):
        aid=d.name;a=by_id.get(aid)
        if not a:
            issues.append({'code':'HTML_ASSET_PACKAGE_PARITY_MISSING_ASSET','asset_id':aid});continue
        checks={
          'prompt_cn':('05_prompt_CN.txt',),
          'prompt_en':('06_prompt_EN.txt',),
          'visible_copy':('07_visible_copy.md','07_visible_copy.txt','14_visible_copy_block.md'),
          'production_notes':('09_production_notes.md','08_production_notes.txt','15_production_assembly_notes.md'),
        }
        for key,names in checks.items():
            file_value=_text_first(d,names);html_value=a.get(key)
            if file_value is not None and html_value is not None and str(html_value).strip()!=file_value:
                issues.append({'code':'HTML_ASSET_PACKAGE_TEXT_DRIFT','asset_id':aid,'field':key,'files':list(names)})
        card_file=None
        for name in ('12_design_card.json','11_design_card.json'):
            p=d/name
            if p.exists():card_file=_json(p);break
        if isinstance(card_file,dict) and isinstance(a.get('card'),dict):
            candidate=card_file.get('design_card') if isinstance(card_file.get('design_card'),dict) else (card_file.get('card') if isinstance(card_file.get('card'),dict) else card_file)
            if candidate!=a['card']:issues.append({'code':'HTML_ASSET_PACKAGE_DESIGN_CARD_DRIFT','asset_id':aid})
    extra=sorted(set(by_id)-{d.name for d in root.iterdir() if d.is_dir()})
    for aid in extra:issues.append({'code':'HTML_ASSET_DATA_WITHOUT_PACKAGE','asset_id':aid})
    return issues
