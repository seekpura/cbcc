from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Callable

from .canonical_materialization_integrity import audit_asset_directory, COPY_ROUTES
from .human_projection_integrity import audit_human_projection_html


def _read_json(path:Path)->dict[str,Any]:
    try:
        value=json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value,dict) else {}
    except Exception:
        return {}


def _extract_prompt_lineage(contract:dict[str,Any])->dict[str,Any]:
    direct=contract.get('canonical_prompt_lineage')
    if isinstance(direct,dict) and direct.get('canonical_art_direction_sha256'):
        return direct
    card=contract.get('design_card')
    if isinstance(card,dict):
        nested=card.get('canonical_prompt_lineage')
        if isinstance(nested,dict) and nested.get('canonical_art_direction_sha256'):
            return nested
    return {}


def _prompt_lineage_issue(asset_dir:Path)->dict[str,Any]|None:
    contract={}
    for name in ('13_prompt_contract.json','12_prompt_contract.json'):
        p=asset_dir/name
        if p.exists(): contract=_read_json(p);break
    if not contract:return {'code':'PROMPT_CANONICAL_LINEAGE_MISSING','asset_id':asset_dir.name,'why':'Prompt contract is missing.'}
    lineage=_extract_prompt_lineage(contract)
    if not lineage:
        return {'code':'PROMPT_CANONICAL_LINEAGE_MISSING','asset_id':asset_dir.name,'why':'CN/EN Prompt package has no persisted canonical Art Direction lineage hash at contract or design_card level.'}
    return None


def _prompt_contract_route_issue(asset_dir:Path)->dict[str,Any]|None:
    for name in ('13_prompt_contract.json','12_prompt_contract.json'):
        p=asset_dir/name
        if not p.exists():continue
        contract=_read_json(p)
        route=str(contract.get('exact_copy_route') or contract.get('copy_render_route') or '').upper().strip()
        if route and route not in COPY_ROUTES:
            return {'code':'PROMPT_CONTRACT_COPY_ROUTE_INVALID','asset_id':asset_dir.name,'value':route[:500]}
    return None


def wrap_audit_host_full_package(fn:Callable[[Path],dict[str,Any]]):
    def audited(package_dir:Path):
        package=Path(package_dir);result=fn(package);issues=list(result.get('issues') or [])
        root=package/'asset_packages'
        if root.exists():
            for asset_dir in sorted(x for x in root.iterdir() if x.is_dir()):
                issues.extend(audit_asset_directory(asset_dir))
                route_issue=_prompt_contract_route_issue(asset_dir)
                if route_issue:issues.append(route_issue)
                lineage_issue=_prompt_lineage_issue(asset_dir)
                if lineage_issue:issues.append(lineage_issue)
        html=package/'index.html'
        if html.exists():
            issues.extend(audit_human_projection_html(html.read_text(encoding='utf-8',errors='ignore')))
        out=[];seen=set()
        for row in issues:
            key=json.dumps(row,ensure_ascii=False,sort_keys=True,default=str)
            if key not in seen:seen.add(key);out.append(row)
        result['issues']=out
        result['status']='PASS' if not out else 'INCOMPLETE'
        result['canonical_materialization_parity_audit']={
            'status':'PASS' if not out else 'INCOMPLETE',
            'asset_semantic_guard':True,
            'prompt_single_source_lineage_required':True,
            'human_projection_integrity_required':True,
        }
        return result
    setattr(audited,'_cbcc_v0670_canonical_materialization_parity',True)
    return audited
