#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

VERSION='0.6.74'
AUTHORITY='0.6.74-cross-scope-regression-closure'
V0673_FLOOR_SHA256='2e9bc6a6a0d9a002b3616df02a0c1ec92d7fdf7da1cb725afb1c714b0f7b2cb4'


def _root(extracted: Path) -> Path:
    if (extracted/'plugin.json').exists(): return extracted
    direct=extracted/'cross-border-commerce-creative'
    if (direct/'plugin.json').exists(): return direct
    candidates=[p for p in extracted.iterdir() if p.is_dir() and (p/'plugin.json').exists()]
    if len(candidates)==1:return candidates[0]
    raise RuntimeError('plugin root unresolved')


def _version_tuple(value: Any) -> tuple[int,int,int] | None:
    m=re.match(r'^(\d+)\.(\d+)\.(\d+)',str(value or ''))
    return tuple(map(int,m.groups())) if m else None


def audit(path: Path, *, floor_mode: bool=False) -> dict:
    issues=[]
    def add(code,**data): issues.append({'code':code,**data})
    if not path.exists(): return {'status':'FAIL','issue_count':1,'issues':[{'code':'ZIP_MISSING'}]}
    try:
        with tempfile.TemporaryDirectory(prefix='cbcc-v0674-') as td:
            ex=Path(td)
            with zipfile.ZipFile(path) as zf:
                bad=zf.testzip()
                if bad:add('ZIP_CORRUPT_MEMBER',member=bad)
                zf.extractall(ex)
            root=_root(ex); skill=root/'skills'/'cross-border-commerce-creative'; res=skill/'resources'
            manifest=json.loads((root/'plugin.json').read_text(encoding='utf-8'))
            actual=manifest.get('version')
            if floor_mode:
                if _version_tuple(actual) is None or _version_tuple(actual) < _version_tuple(VERSION):add('V0674_FLOOR_PLUGIN_VERSION_TOO_OLD',actual=actual)
            elif actual!=VERSION:add('PLUGIN_VERSION_MISMATCH',actual=actual)
            top=skill/'SKILL.md'; deep=res/'SKILL.md'
            if not top.exists() or not deep.exists():add('SKILL_MISSING')
            elif top.read_bytes()!=deep.read_bytes():add('TOP_DEEP_SKILL_DRIFT')
            if top.exists():
                text=top.read_text(encoding='utf-8-sig')
                tokens=['## 0.23 Cross-Scope Regression Closure','## 0.22 Bilingual Business-Object Delivery + Model Prompt Consumption Closure','## 1. FULL depth remains mandatory']
                if not floor_mode: tokens=[f'version: {AUTHORITY}',f'# Cross-Border Commerce Creative v{VERSION}',*tokens]
                for token in tokens:
                    if token not in text:add('SKILL_TOKEN_MISSING',token=token)
            vp=res/'VERSION'
            if not vp.exists():add('RESOURCE_VERSION_MISSING')
            elif not floor_mode and vp.read_text(encoding='utf-8-sig').strip()!=AUTHORITY:add('RESOURCE_VERSION_MISMATCH')
            required=['runtime/cbcc/v0674_regression_closure.py','runtime/cbcc/__init__.py','tests/test_v0674_regression_closure.py','scripts/build_plugin_dist_v0674.py','scripts/check_v0674_release_delta.py']
            missing=[x for x in required if not (res/x).exists()]
            if missing:add('V0674_REQUIRED_FILE_MISSING',files=missing)
            init=(res/'runtime/cbcc/__init__.py').read_text(encoding='utf-8') if (res/'runtime/cbcc/__init__.py').exists() else ''
            a=init.find('_commercial_continuity_bootstrap.install()'); b=init.find('_v0674_regression_closure.apply_v0674_patches()')
            if a<0 or b<0 or a>=b:add('V0674_BOOTSTRAP_ORDER_INVALID',prior=a,v0674=b)
            mod=(res/'runtime/cbcc/v0674_regression_closure.py').read_text(encoding='utf-8') if (res/'runtime/cbcc/v0674_regression_closure.py').exists() else ''
            for token in ('FULL_STRATEGY','FULL_E2E','visible_copy_locales','STRATEGY_READY','COPY_REVIEW_REQUIRED','PUBLISH_READY','safe_dump_no_aliases','SOURCE_LEDGER.json','PROVENANCE_METADATA','delivery_export.validate_strategy_delivery'):
                if token not in mod:add('V0674_RUNTIME_TOKEN_MISSING',token=token)
            dc=manifest.get('delivery_contract') or {}
            for flag in ('v074_explicit_platform_locale_scope_required','v074_full_alias_closure_required','v074_listing_release_state_required','v074_markdown_escaped_pipe_required','v074_prompt_provenance_membrane_required','v074_source_ledger_required','v074_yaml_no_anchor_required'):
                if dc.get(flag) is not True:add('V0674_DELIVERY_CONTRACT_FLAG_MISSING',flag=flag)
            builder=(res/'scripts/build_plugin_dist_v0674.py').read_text(encoding='utf-8') if (res/'scripts/build_plugin_dist_v0674.py').exists() else ''
            if f"V0673_FLOOR_SHA256 = '{V0673_FLOOR_SHA256}'" not in builder:add('V0673_FLOOR_SHA256_NOT_HARD_LOCKED')
            if not floor_mode:
                current=(res/'scripts/build_plugin_dist_current.py').read_text(encoding='utf-8') if (res/'scripts/build_plugin_dist_current.py').exists() else ''
                if "CURRENT_BUILDER_TARGET = '0.6.74'" not in current or 'build_plugin_dist_v0674' not in current:add('CURRENT_BUILDER_NOT_V0674')
                override=json.loads((res/'references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json').read_text(encoding='utf-8')) if (res/'references/REQUIREMENT_CONSUMER_MAP_CURRENT_OVERRIDES.json').exists() else {}
                if str(override.get('current_release_version') or '')!=VERSION:add('CURRENT_OVERRIDE_NOT_V0674',actual=override.get('current_release_version'))
    except Exception as exc:add('V0674_CHECK_EXCEPTION',error=str(exc))
    return {'status':'PASS' if not issues else 'FAIL','issue_count':len(issues),'issues':issues,'version':VERSION,'authority':AUTHORITY,'floor_mode':floor_mode,'v0673_floor_sha256':V0673_FLOOR_SHA256}


def main():
    p=argparse.ArgumentParser();p.add_argument('plugin_zip');p.add_argument('--floor-mode',action='store_true');a=p.parse_args();r=audit(Path(a.plugin_zip),floor_mode=a.floor_mode);print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
