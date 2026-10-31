#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
import zipfile
from pathlib import Path

VERSION='0.6.75'
AUTHORITY='0.6.75-formal-full-package-identity-closure'
V0674_FLOOR_BYTES=71400
V0674_FLOOR_SHA256='8d5e62a0486c83712b61c31010b83b7bc59af0439e7546ba02f48627caecefc8'


def _root(extracted: Path) -> Path:
    if (extracted/'plugin.json').exists(): return extracted
    direct=extracted/'cross-border-commerce-creative'
    if (direct/'plugin.json').exists(): return direct
    candidates=[p for p in extracted.iterdir() if p.is_dir() and (p/'plugin.json').exists()]
    if len(candidates)==1:return candidates[0]
    raise RuntimeError('plugin root unresolved')


def audit(path: Path) -> dict:
    issues=[]
    def add(code,**data): issues.append({'code':code,**data})
    if not path.exists(): return {'status':'FAIL','issue_count':1,'issues':[{'code':'ZIP_MISSING'}]}
    try:
        with tempfile.TemporaryDirectory(prefix='cbcc-v0675-') as td:
            ex=Path(td)
            with zipfile.ZipFile(path) as zf:
                bad=zf.testzip()
                if bad:add('ZIP_CORRUPT_MEMBER',member=bad)
                zf.extractall(ex)
            root=_root(ex); skill=root/'skills'/'cross-border-commerce-creative'; res=skill/'resources'
            manifest=json.loads((root/'plugin.json').read_text(encoding='utf-8'))
            if manifest.get('version')!=VERSION:add('PLUGIN_VERSION_MISMATCH',actual=manifest.get('version'))
            if (manifest.get('delivery_contract') or {}).get('v075_verified_full_package_identity_closure_required') is not True:add('V075_IDENTITY_FLAG_MISSING')
            top=skill/'SKILL.md'; deep=res/'SKILL.md'
            if not top.exists() or not deep.exists():add('SKILL_MISSING')
            elif top.read_bytes()!=deep.read_bytes():add('TOP_DEEP_SKILL_DRIFT')
            if top.exists():
                text=top.read_text(encoding='utf-8-sig')
                for token in (f'version: {AUTHORITY}',f'# Cross-Border Commerce Creative v{VERSION}','## 0.24 Formal Full-Package Identity Closure','## 0.23 Cross-Scope Regression Closure','## 0.22 Bilingual Business-Object Delivery + Model Prompt Consumption Closure','## 1. FULL depth remains mandatory'):
                    if token not in text:add('SKILL_TOKEN_MISSING',token=token)
            vp=res/'VERSION'
            if not vp.exists() or vp.read_text(encoding='utf-8-sig').strip()!=AUTHORITY:add('RESOURCE_VERSION_MISMATCH')
            required=['runtime/cbcc/v0674_regression_closure.py','runtime/cbcc/__init__.py','tests/test_v0674_regression_closure.py','scripts/build_plugin_dist_v0674.py','scripts/build_plugin_dist_v0675.py','scripts/build_plugin_dist_current.py','scripts/check_v0674_release_delta.py','scripts/check_v0675_release_delta.py','references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json','references/CURRENT_CANONICAL_SKILL_BUILD.md','prompts/canonical_authority_loading_map_CURRENT.md']
            missing=[x for x in required if not (res/x).exists()]
            if missing:add('V0675_REQUIRED_FILE_MISSING',files=missing)
            current=(res/'scripts/build_plugin_dist_current.py').read_text(encoding='utf-8') if (res/'scripts/build_plugin_dist_current.py').exists() else ''
            if "CURRENT_BUILDER_TARGET = '0.6.75'" not in current or 'build_plugin_dist_v0675' not in current:add('CURRENT_BUILDER_NOT_V0675')
            builder=(res/'scripts/build_plugin_dist_v0675.py').read_text(encoding='utf-8') if (res/'scripts/build_plugin_dist_v0675.py').exists() else ''
            if f'V0674_FLOOR_BYTES = {V0674_FLOOR_BYTES}' not in builder:add('V0674_FLOOR_BYTES_NOT_HARD_LOCKED')
            if f"V0674_FLOOR_SHA256 = '{V0674_FLOOR_SHA256}'" not in builder:add('V0674_FLOOR_SHA256_NOT_HARD_LOCKED')
            override=json.loads((res/'references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json').read_text(encoding='utf-8')) if (res/'references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json').exists() else {}
            if str(override.get('current_release_version') or '')!=VERSION:add('CURRENT_OVERRIDE_NOT_V0675',actual=override.get('current_release_version'))
            init=(res/'runtime/cbcc/__init__.py').read_text(encoding='utf-8') if (res/'runtime/cbcc/__init__.py').exists() else ''
            a=init.find('_commercial_continuity_bootstrap.install()'); b=init.find('_v0674_regression_closure.apply_v0674_patches()')
            if a<0 or b<0 or a>=b:add('V0674_BOOTSTRAP_ORDER_INVALID_IN_V075',prior=a,v0674=b)
    except Exception as exc:add('V0675_CHECK_EXCEPTION',error=str(exc))
    return {'status':'PASS' if not issues else 'FAIL','issue_count':len(issues),'issues':issues,'version':VERSION,'authority':AUTHORITY,'v0674_floor_bytes':V0674_FLOOR_BYTES,'v0674_floor_sha256':V0674_FLOOR_SHA256,'business_runtime_delta_from_v0674':'NONE'}


def main():
    p=argparse.ArgumentParser();p.add_argument('plugin_zip');a=p.parse_args();r=audit(Path(a.plugin_zip));print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
