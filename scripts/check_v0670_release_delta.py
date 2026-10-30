#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,tempfile,zipfile
from pathlib import Path

REQUIRED={
 'references/V0670_CANONICAL_MATERIALIZATION_PARITY.md':('A01, A02, G08, L01, R01, S01, S02, T01, T02, V01','48517','f3ed58aa'),
 'references/V0670_REQUIREMENT_IMPLEMENTATION_DELTA.json':('REQ-014','REQ-030','REQ-033','REQ-042','REQ-060','FRESH_HOST_E2E_PENDING'),
 'runtime/cbcc/canonical_materialization_integrity.py':('ASSET_SCHEMA_SEMANTIC_MISMATCH','VISIBLE_COPY_LANGUAGE_SLOT_MISMATCH','canonical_art_direction_sha256'),
 'runtime/cbcc/canonical_prompt_guard.py':('CanonicalMaterializationError','validate_canonical_asset_or_raise','finalize_prompt_lineage'),
 'runtime/cbcc/canonical_asset_package_lineage.py':('canonical_prompt_lineage','canonical_art_direction_sha256','wrap_compile_asset_packages'),
 'runtime/cbcc/canonical_materialization_package_audit.py':('PROMPT_CANONICAL_LINEAGE_MISSING','audit_human_projection_html','audit_asset_directory'),
 'runtime/cbcc/human_projection_integrity.py':('HTML_LISTING_PROJECTION_INCOMPLETE','WORKSPACE_COPY_BINDING_MISSING','WORKSPACE_SEARCH_SCOPE_INCOMPLETE'),
 'runtime/cbcc/strategy_culture_completion_v0670.py':('FULL_RACE_PLATFORM_MISSING','FULL_CULTURE_EXECUTION_COLUMNS_MISSING_V0670','inclusive_dimension_decisions'),
 'runtime/cbcc/delivery_export_continuity.py':('_canonical_materialization_export_audit','CANONICAL_MATERIALIZATION_PARITY_AUDIT.json','BLOCKED canonical materialization / Human projection parity failed'),
 'runtime/cbcc/commercial_continuity_bootstrap.py':('validate_canonical_asset_or_raise','finalize_prompt_lineage','wrap_compile_asset_packages','wrap_canonical_materialization_package_audit','wrap_strategy_culture_completion'),
}

def _root(extracted:Path)->Path:
    direct=extracted/'cross-border-commerce-creative'
    if direct.exists():return direct
    c=[p for p in extracted.iterdir() if p.is_dir() and (p/'plugin.json').exists()]
    return c[0] if len(c)==1 else extracted

def audit(zip_path:Path)->dict:
    issues=[]
    def add(code,**kw):issues.append({'code':code,**kw})
    if not zip_path.exists():return {'status':'FAIL','issue_count':1,'issues':[{'code':'ZIP_MISSING'}]}
    with tempfile.TemporaryDirectory(prefix='cbcc-v0670-delta-') as td:
        out=Path(td)
        try:
            with zipfile.ZipFile(zip_path) as zf:
                bad=zf.testzip()
                if bad:add('ZIP_CORRUPT_MEMBER',member=bad)
                zf.extractall(out)
        except Exception as exc:
            return {'status':'FAIL','issue_count':1,'issues':[{'code':'ZIP_INVALID','error':str(exc)}]}
        plugin=_root(out);resources=plugin/'skills'/'cross-border-commerce-creative'/'resources'
        for rel,tokens in REQUIRED.items():
            p=resources/rel
            if not p.exists():
                add('V0670_REQUIRED_FILE_MISSING',path=rel);continue
            text=p.read_text(encoding='utf-8-sig',errors='replace')
            for token in tokens:
                if token not in text:add('V0670_REQUIRED_TOKEN_MISSING',path=rel,token=token)
        bootstrap=resources/'runtime/cbcc/commercial_continuity_bootstrap.py'
        if bootstrap.exists():
            text=bootstrap.read_text(encoding='utf-8')
            order=['normalize_full_art_direction(call_args[0] or {})','validate_canonical_asset_or_raise(normalized_asset)','existing_prompt_compile(*call_args, **kwargs)','finalize_integrated_render_route(normalized_asset, out)','finalize_model_prompt_bundle(out)','finalize_prompt_lineage(normalized_asset, out)']
            offsets=[text.find(x) for x in order]
            if any(i<0 for i in offsets) or offsets!=sorted(offsets):add('V0670_PROMPT_ORDER_INVALID',offsets=offsets)
        skill=plugin/'skills/cross-border-commerce-creative/SKILL.md'
        if skill.exists():
            text=skill.read_text(encoding='utf-8-sig')
            for token in ('## 0.19 Canonical Materialization + Human Projection Parity','canonical_art_direction_sha256','HTML_LISTING_PROJECTION_INCOMPLETE'):
                if token not in text:add('V0670_SKILL_TOKEN_MISSING',token=token)
    return {'status':'PASS' if not issues else 'FAIL','issue_count':len(issues),'issues':issues,'required_file_count':len(REQUIRED)}

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('plugin_zip');args=ap.parse_args()
    result=audit(Path(args.plugin_zip));print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
