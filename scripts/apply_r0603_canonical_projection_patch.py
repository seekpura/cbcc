from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding='utf-8')
    if old not in text or text.count(old) != 1:
        raise SystemExit(f'{label}: expected exactly one target, found {text.count(old)}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


compiler = Path('runtime/cbcc/compiler.py')
replace_once(
    compiler,
    "from .operator_execution_board import build_operator_execution_board\nfrom .io import load_tabular, apply_field_map\n",
    "from .operator_execution_board import build_operator_execution_board\nfrom .canonical_commerce_graph import materialize_canonical_commerce_graph\nfrom .io import load_tabular, apply_field_map\n",
    'compiler import',
)
replace_once(
    compiler,
    "    st.set_gate('EXECUTION','READY_REVIEW' if execution_ready else 'PENDING',[exp],execution); st.checkpoint('EXECUTION','READY_REVIEW' if st.data['gates']['EXECUTION']['status']=='READY_REVIEW' else 'PENDING_CONTRACTS')\n    # final_ready is derived from current-scope closure; never reset it as a static pipeline flag.\n    refresh_review_workspace(p,st)\n",
    "    st.set_gate('EXECUTION','READY_REVIEW' if execution_ready else 'PENDING',[exp],execution); st.checkpoint('EXECUTION','READY_REVIEW' if st.data['gates']['EXECUTION']['status']=='READY_REVIEW' else 'PENDING_CONTRACTS')\n\n    # Materialize the relationship-only canonical authority after all project business objects exist.\n    # JSON authorities remain the source of truth; Markdown/HTML/prompts/asset packages are projections.\n    materialize_canonical_commerce_graph(p/'artifacts')\n    # final_ready is derived from current-scope closure; never reset it as a static pipeline flag.\n    refresh_review_workspace(p,st)\n",
    'compiler graph materialization',
)

integrity = Path('runtime/cbcc/canonical_materialization_integrity.py')
helper_block = r'''

def _read_json_file(path:Path)->dict[str,Any]:
    if not path.exists(): return {}
    try:
        value=json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value,dict) else {}
    except Exception:
        return {}

def _extract_fenced_json(text:str)->dict[str,Any]:
    match=re.search(r'```json\s*\n(.*?)\n```',str(text or ''),re.S|re.I)
    if not match: return {}
    try:
        value=json.loads(match.group(1))
        return value if isinstance(value,dict) else {}
    except Exception:
        return {}

def _normalized_visible_copy_raw(value:Mapping[str,Any])->dict[str,Any]:
    out=deepcopy(dict(value or {}))
    out.pop('copy_render_route',None)
    return out

def _projection_drift(asset_id:str,code:str,field:str,left:Any,right:Any,why:str)->dict[str,Any]:
    return {'asset_id':asset_id,'code':code,'field':field,'value':_text({'projection':left,'contract':right})[:500],'why':why}

def audit_asset_projection_parity(asset_dir:Path)->list[dict[str,Any]]:
    """Reject semantically conflicting projections even when byte lineage was freshly rebuilt."""
    asset_dir=Path(asset_dir); asset_id=asset_dir.name; issues=[]
    contract=_read_json_file(asset_dir/'13_prompt_contract.json')
    card=_read_json_file(asset_dir/'12_design_card.json')
    visible=_read_json_file(asset_dir/'14_visible_copy_block.json')
    production=_read_json_file(asset_dir/'15_production_assembly_notes.json')

    contract_card=contract.get('design_card') if isinstance(contract.get('design_card'),Mapping) else {}
    if card and contract_card and card!=contract_card:
        issues.append(_projection_drift(asset_id,'ASSET_DESIGN_CARD_PROMPT_CONTRACT_DRIFT','design_card',card,contract_card,'12_design_card.json and 13_prompt_contract.json must project one Design Card authority'))

    contract_visible=contract.get('visible_copy_block') if isinstance(contract.get('visible_copy_block'),Mapping) else {}
    if visible and contract_visible and visible!=contract_visible:
        issues.append(_projection_drift(asset_id,'ASSET_VISIBLE_COPY_PROMPT_CONTRACT_DRIFT','visible_copy_block',visible,contract_visible,'14_visible_copy_block.json and the Prompt Contract must project one Visible Copy authority'))

    contract_production=contract.get('production_assembly_notes') if isinstance(contract.get('production_assembly_notes'),Mapping) else {}
    if production and contract_production and production!=contract_production:
        issues.append(_projection_drift(asset_id,'ASSET_PRODUCTION_NOTES_PROMPT_CONTRACT_DRIFT','production_assembly_notes',production,contract_production,'15_production_assembly_notes.json and the Prompt Contract must project one production authority'))

    for field,file_name,model_key,canonical_key in (
        ('prompt_cn','05_prompt_CN.txt','model_prompt_cn','canonical_prompt_cn'),
        ('prompt_en','06_prompt_EN.txt','model_prompt_en','canonical_prompt_en'),
    ):
        path=asset_dir/file_name
        expected=contract.get(model_key) or contract.get(canonical_key)
        if path.exists() and isinstance(expected,str):
            actual=path.read_text(encoding='utf-8',errors='ignore')
            if actual!=expected:
                issues.append(_projection_drift(asset_id,'ASSET_PROMPT_CONTRACT_TEXT_DRIFT',field,actual,expected,f'{file_name} must be the exact model-facing projection recorded by 13_prompt_contract.json'))

    copy_path=asset_dir/'08_copy.md'
    if copy_path.exists() and visible:
        markdown_copy=_extract_fenced_json(copy_path.read_text(encoding='utf-8',errors='ignore'))
        visible_raw=visible.get('raw') if isinstance(visible.get('raw'),Mapping) else {}
        if markdown_copy and _normalized_visible_copy_raw(markdown_copy)!=_normalized_visible_copy_raw(visible_raw):
            issues.append(_projection_drift(asset_id,'ASSET_VISIBLE_COPY_CANONICAL_DRIFT','visible_copy',markdown_copy,visible_raw,'08_copy.md and 14_visible_copy_block.json must project the same shopper-visible copy truth'))
    return issues
'''
replace_once(
    integrity,
    "\ndef audit_asset_directory(asset_dir:Path)->list[dict[str,Any]]:\n",
    helper_block + "\ndef audit_asset_directory(asset_dir:Path)->list[dict[str,Any]]:\n",
    'integrity parity helpers',
)
replace_once(
    integrity,
    "def audit_asset_directory(asset_dir:Path)->list[dict[str,Any]]:\n    issues=[];card={}\n",
    "def audit_asset_directory(asset_dir:Path)->list[dict[str,Any]]:\n    issues=list(audit_asset_projection_parity(asset_dir));card={}\n",
    'integrity audit wiring',
)

parity = Path('runtime/cbcc/canonical_full_parity_v0671.py')
replace_once(
    parity,
    "from .canonical_human_workspace_completion import apply_complete_canonical_human_projection\n",
    "from .canonical_human_workspace_completion import apply_complete_canonical_human_projection\nfrom .canonical_materialization_integrity import audit_asset_directory\n",
    'parity import',
)
replace_once(
    parity,
    "    assets = [_asset_payload(d) for d in sorted(asset_root.iterdir()) if d.is_dir()] if asset_root.exists() else []\n\n    product_business = product_truth or _d(human.get('product'))\n",
    "    asset_dirs = [d for d in sorted(asset_root.iterdir()) if d.is_dir()] if asset_root.exists() else []\n    asset_projection_issues = [issue for d in asset_dirs for issue in audit_asset_directory(d)]\n    if asset_projection_issues:\n        raise RuntimeError('BLOCKED canonical asset projection drift: ' + json.dumps(asset_projection_issues[:50], ensure_ascii=False))\n    assets = [_asset_payload(d) for d in asset_dirs]\n    canonical_graph = _read_json(support / 'canonical_commerce_graph.json')\n\n    product_business = product_truth or _d(human.get('product'))\n",
    'parity asset audit',
)
replace_once(
    parity,
    "        'canonical_business_objects': business_objects,\n        'projection_contract': {\n",
    "        'canonical_business_objects': business_objects,\n        'projection_authority': ({\n            'source': 'supporting_analysis/canonical_commerce_graph.json',\n            'graph_sha256': canonical_graph.get('graph_sha256'),\n            'schema': canonical_graph.get('schema'),\n            'role': 'PROJECTION_LINEAGE_ONLY',\n        } if canonical_graph.get('graph_sha256') else {}),\n        'projection_contract': {\n",
    'parity graph lineage',
)

print('patched compiler + canonical materialization integrity + canonical human payload')
