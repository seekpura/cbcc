from __future__ import annotations
from pathlib import Path
from typing import Any, Callable
import json


def _promote_contract(path:Path)->bool:
    if not path.exists():return False
    try:contract=json.loads(path.read_text(encoding='utf-8'))
    except Exception:return False
    if not isinstance(contract,dict):return False
    if isinstance(contract.get('canonical_prompt_lineage'),dict) and contract['canonical_prompt_lineage'].get('canonical_art_direction_sha256'):
        return True
    card=contract.get('design_card')
    lineage=card.get('canonical_prompt_lineage') if isinstance(card,dict) else None
    if not isinstance(lineage,dict) or not lineage.get('canonical_art_direction_sha256'):
        return False
    # Promotion is lossless: do not recompute or infer a different hash here.
    contract['canonical_prompt_lineage']=lineage
    path.write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return True


def promote_package_lineage(root:Path)->dict[str,Any]:
    root=Path(root);promoted=[];missing=[]
    if not root.exists():return {'status':'NOT_FOUND','promoted':[],'missing':[]}
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        contract=d/'13_prompt_contract.json'
        if not contract.exists():continue
        if _promote_contract(contract):promoted.append(d.name)
        else:missing.append(d.name)
    return {'status':'PASS' if not missing else 'INCOMPLETE','promoted':promoted,'missing':missing}


def wrap_compile_asset_packages(fn:Callable[...,dict[str,Any]]):
    def compiled(root:Path,*args,**kwargs):
        result=fn(root,*args,**kwargs)
        lineage=promote_package_lineage(Path(root))
        result=dict(result or {});result['canonical_prompt_lineage_materialization']=lineage
        return result
    setattr(compiled,'_cbcc_v0670_prompt_lineage_materialization',True)
    return compiled
