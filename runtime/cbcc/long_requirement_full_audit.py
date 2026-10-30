from __future__ import annotations

from pathlib import Path
import json
import re
from typing import Any, Callable

QUESTION_LIMIT = 10
P0_AREAS = {
    'efficacy_claims', 'ingredients_formula', 'certifications', 'price', 'sales_volume', 'regulated_category'
}
CULTURE_CHECK_FIELDS = {
    'script_check', 'casting_check', 'wardrobe_grooming_check', 'color_check', 'cta_check'
}


def _p(v: Any) -> bool:
    return v not in (None, '', [], {})


def _d(v: Any) -> dict[str, Any]:
    return v if isinstance(v, dict) else {}


def _l(v: Any) -> list[Any]:
    if v in (None, '', {}):
        return []
    return v if isinstance(v, list) else [v]


def _sig(row: dict[str, Any]) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)


def _dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out, seen = [], set()
    for row in rows:
        key = _sig(row)
        if key not in seen:
            seen.add(key)
            out.append(row)
    return out


def wrap_audit_full_strategy_depth_v3(fn: Callable[..., dict[str, Any]]):
    def audited(strategy: dict[str, Any], base_result=None):
        result = fn(strategy, base_result)
        if str(result.get('mode') or '').upper() != 'FULL':
            return result

        issues = list(result.get('issues') or [])
        sections = _d(strategy.get('sections'))
        info = _d(sections.get('01_information_completeness_assumptions_decisions'))
        pending = _l(info.get('pending_confirmations'))
        if len(pending) > QUESTION_LIMIT:
            issues.append({'code': 'FULL_PENDING_CONFIRMATION_LIMIT_EXCEEDED', 'count': len(pending), 'limit': QUESTION_LIMIT})
        if info.get('question_limit') not in (None, QUESTION_LIMIT):
            issues.append({'code': 'FULL_PENDING_CONFIRMATION_LIMIT_INVALID', 'value': info.get('question_limit'), 'expected': QUESTION_LIMIT})
        if info.get('continue_under_assumptions') is not True:
            issues.append({'code': 'FULL_CONTINUE_UNDER_ASSUMPTIONS_MISSING'})

        for i, row in enumerate(_l(info.get('decision_log'))):
            if not isinstance(row, dict):
                continue
            context = _d(row.get('context_why'))
            missing = [k for k in ('platform', 'region', 'audience', 'race_ethnicity_culture') if not _p(context.get(k))]
            if missing:
                issues.append({'code': 'FULL_DECISION_CONTEXT_WHY_MISSING', 'row': i, 'fields': missing})
            else:
                shallow = [k for k in ('platform', 'region', 'audience', 'race_ethnicity_culture') if not _p(_d(context.get(k)).get('why')) or not _p(_d(context.get(k)).get('status'))]
                if shallow:
                    issues.append({'code': 'FULL_DECISION_CONTEXT_WHY_SHALLOW', 'row': i, 'fields': shallow})

        vis = _d(sections.get('05_visual_photography_strategy'))
        people = str(vis.get('people_applicability') or '').upper() in {'PERSON_PRESENT', 'PEOPLE_PRESENT', 'HUMAN_PRESENT', 'APPLICABLE_P0'}
        if people:
            inc = _d(vis.get('inclusive_photography'))
            for field in ('deep_skin_exposure_compensation_plan', 'reflector_bounce_diffusion'):
                if not _p(inc.get(field)):
                    issues.append({'code': 'FULL_INCLUSIVE_PHOTOGRAPHY_DIMENSION_MISSING', 'section': '05_visual_photography_strategy', 'dimension': field})

        for i, row in enumerate(_l(sections.get('08_culture_adaptation_checklist'))):
            if not isinstance(row, dict):
                continue
            missing = sorted(field for field in CULTURE_CHECK_FIELDS if not _p(row.get(field)))
            if missing:
                issues.append({'code': 'FULL_CULTURE_EXECUTION_CHECK_COLUMNS_MISSING', 'section': '08_culture_adaptation_checklist', 'row': i, 'fields': missing})

        last = _d(sections.get('09_risk_measurement_priority_next_steps'))
        p0 = [x for x in _l(last.get('p0_compliance_claim_checklist')) if isinstance(x, dict)]
        if not p0:
            issues.append({'code': 'FULL_P0_COMPLIANCE_CHECKLIST_MISSING', 'section': '09_risk_measurement_priority_next_steps'})
        else:
            areas = {str(x.get('check_area') or '') for x in p0}
            missing_areas = sorted(P0_AREAS - areas)
            if missing_areas:
                issues.append({'code': 'FULL_P0_COMPLIANCE_CHECK_AREAS_MISSING', 'areas': missing_areas})
            for i, row in enumerate(p0):
                missing = [k for k in ('check_area', 'priority', 'status', 'action', 'why') if not _p(row.get(k))]
                if missing:
                    issues.append({'code': 'FULL_P0_COMPLIANCE_CHECK_ROW_SHALLOW', 'row': i, 'fields': missing})
                if row.get('priority') != 'P0':
                    issues.append({'code': 'FULL_P0_COMPLIANCE_PRIORITY_INVALID', 'row': i, 'value': row.get('priority')})

        result['issues'] = _dedupe(issues)
        result['status'] = 'PASS' if not result['issues'] else 'INCOMPLETE'
        result['verbatim_long_requirement_audit'] = {
            'question_limit': QUESTION_LIMIT,
            'required_p0_areas': sorted(P0_AREAS),
            'required_culture_check_fields': sorted(CULTURE_CHECK_FIELDS),
        }
        return result
    return audited


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _has_production_ready_assets(package: Path) -> bool:
    root = package / 'asset_packages'
    if not root.exists():
        return False
    return any((d / '05_prompt_CN.txt').exists() or (d / '06_prompt_EN.txt').exists() for d in root.iterdir() if d.is_dir())


def wrap_audit_host_full_package(fn: Callable[[Path], dict[str, Any]]):
    def audited(package_dir: Path):
        package = Path(package_dir)
        result = fn(package)
        issues = list(result.get('issues') or [])

        shortcut = package / 'assets'
        mature = package / 'asset_packages'
        if shortcut.exists() and not mature.exists():
            issues.append({'code': 'HOST_SHORTCUT_ASSET_PACKAGE_FORBIDDEN', 'path': 'assets/', 'expected': 'asset_packages/'})

        universe = _read_json(package / 'ASSET_UNIVERSE.json')
        active_assets = [
            x for x in _l(universe.get('assets')) if isinstance(x, dict)
            and str(x.get('deployment_state') or x.get('pool') or '').upper() not in {'ARCHIVE', 'NOT_NEEDED'}
        ]
        if active_assets and not mature.exists():
            issues.append({'code': 'MATURE_ASSET_PACKAGES_REQUIRED', 'active_asset_count': len(active_assets)})

        if mature.exists():
            try:
                from .asset_compiler import validate_asset_packages
                validation = validate_asset_packages(mature)
                if not validation.get('pass'):
                    issues.append({'code': 'MATURE_ASSET_PACKAGE_VALIDATION_FAILED', 'errors': validation.get('errors') or []})
            except Exception as exc:
                issues.append({'code': 'MATURE_ASSET_PACKAGE_VALIDATION_ERROR', 'error': str(exc)})

            for asset_dir in sorted(x for x in mature.iterdir() if x.is_dir()):
                manifest = asset_dir / '00_asset_manifest.yaml'
                if manifest.exists():
                    text = manifest.read_text(encoding='utf-8', errors='ignore')
                    # YAML parser is optional here; a non-empty serialized art-direction mapping is enough
                    # to distinguish a real structured authority from the old five-file shortcut.
                    if not re.search(r'(?m)^asset_art_direction:\s*(?!\{\}\s*$|null\s*$)', text):
                        issues.append({'code': 'STRUCTURED_ASSET_ART_DIRECTION_NOT_MATERIALIZED', 'asset_id': asset_dir.name})

        # FULL production completion requires real downstream evidence, not prompts alone.
        if _has_production_ready_assets(package):
            files = [p for p in package.rglob('*') if p.is_file()]
            if not any('provider' in p.name.casefold() and 'result' in p.name.casefold() for p in files):
                issues.append({'code': 'FULL_PROVIDER_RESULT_MISSING'})
            if not any('review' in p.name.casefold() for p in files):
                issues.append({'code': 'FULL_ACTUAL_OUTPUT_REVIEW_MISSING'})
            if not any('revision' in p.name.casefold() for p in files):
                issues.append({'code': 'FULL_LOCAL_REVISION_LINEAGE_MISSING'})

        html_path = package / 'index.html'
        if html_path.exists():
            page = html_path.read_text(encoding='utf-8', errors='ignore')
            fixed = ['产品事实', '马来市场', '成交策略', '上架文案', '视觉系统', '资产宇宙', '合规证据', '研究来源']
            hits = [x for x in fixed if x in page]
            if len(hits) >= 7:
                issues.append({'code': 'FIXED_CAPABILITY_MENU_SHELL', 'labels': hits})
            if mature.exists() and not any(token in page for token in ('完整逐资产 Art Direction', 'asset_art_direction', 'Art Direction')):
                issues.append({'code': 'FULL_ART_DIRECTION_NOT_PROJECTED_TO_HTML'})

        result['issues'] = _dedupe(issues)
        result['status'] = 'PASS' if not result['issues'] else 'INCOMPLETE'
        result['verbatim_long_requirement_package_audit'] = True
        return result
    return audited
