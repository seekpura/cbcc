#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,tempfile,zipfile
from pathlib import Path

REQUIRED={
 'runtime/cbcc/canonical_art_direction_projection.py':(
   'project_named_art_direction','canonical_photography_contract','focal_length_mm','camera_height','pitch_deg','prelight_plan'),
 'runtime/cbcc/canonical_human_workspace_projection.py':(
   'CBCC_CANONICAL_HUMAN_PROJECTION_V0670','description_en','key_points','package_contents','CBCC_GLOBAL_SEARCH_INDEX','data-copy-payload','navigator.clipboard.writeText'),
 'runtime/cbcc/canonical_human_workspace_completion.py':(
   'CBCC_CANONICAL_HUMAN_COMPLETION_V0670','Review evidence status','verification_result','modification_action'),
 'runtime/cbcc/canonical_prompt_guard.py':(
   '_install_positive_prompt_projection','project_named_art_direction','canonical_photography_contract','prompt_cn_source_sha256','prompt_en_source_sha256','design_card_source_sha256'),
 'runtime/cbcc/canonical_materialization_package_audit.py':(
   'apply_complete_canonical_human_projection','audit_human_projection_html','PROMPT_CANONICAL_LINEAGE_MISMATCH'),
 'runtime/cbcc/human_projection_integrity.py':(
   'HTML_LISTING_PROJECTION_INCOMPLETE','HTML_ASSET_PRODUCT_PRESENCE_PROJECTION_INCOMPLETE','CBCC_GLOBAL_SEARCH_INDEX','data-copy-payload'),
}

def _plugin_root(extracted:Path)->Path:
    direct=extracted/'cross-border-commerce-creative'
    if direct.exists():return direct
    candidates=[p for p in extracted.iterdir() if p.is_dir() and (p/'plugin.json').exists()]
    if len(candidates)==1:return candidates[0]
    if (extracted/'plugin.json').exists():return extracted
    return direct

def audit(plugin_zip:Path)->dict:
    issues=[]
    with tempfile.TemporaryDirectory(prefix='cbcc-v0670-positive-') as td:
        root=Path(td)
        with zipfile.ZipFile(plugin_zip) as zf:
            bad=zf.testzip()
            if bad:issues.append({'code':'ZIP_CORRUPT','member':bad})
            zf.extractall(root)
        plugin=_plugin_root(root); resources=plugin/'skills'/'cross-border-commerce-creative'/'resources'
        for rel,tokens in REQUIRED.items():
            path=resources/rel
            if not path.exists():
                issues.append({'code':'POSITIVE_PROJECTION_FILE_MISSING','path':rel});continue
            text=path.read_text(encoding='utf-8',errors='ignore')
            missing=[t for t in tokens if t not in text]
            if missing:issues.append({'code':'POSITIVE_PROJECTION_TOKEN_MISSING','path':rel,'tokens':missing})
        bootstrap=resources/'runtime/cbcc/commercial_continuity_bootstrap.py'
        if bootstrap.exists():
            text=bootstrap.read_text(encoding='utf-8',errors='ignore')
            for token in ('validate_canonical_asset_or_raise','finalize_prompt_lineage','wrap_canonical_materialization_package_audit'):
                if token not in text:issues.append({'code':'POSITIVE_PROJECTION_BOOTSTRAP_BINDING_MISSING','token':token})
        else:issues.append({'code':'BOOTSTRAP_MISSING'})
    return {'status':'PASS' if not issues else 'FAIL','issue_count':len(issues),'issues':issues,'required_files':len(REQUIRED)}

def main()->int:
    p=argparse.ArgumentParser();p.add_argument('plugin_zip');args=p.parse_args();result=audit(Path(args.plugin_zip));print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
