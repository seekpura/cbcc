from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
import json
import re

MARKET_CULTURE_DIMENSIONS = [
    'platform', 'market_region', 'subregion_geography', 'audience_segments', 'age', 'gender', 'income_spend',
    'language', 'race_ethnicity', 'religion', 'holiday_calendar', 'payment', 'logistics', 'local_regulation',
    'platform_behavior', 'search_demand', 'competition', 'price_band', 'intersectionality', 'stereotype_taboo',
]
DIMENSION_STATUSES = {'EVIDENCED', 'ASSUMPTION', 'TO_VERIFY', 'MISSING_INPUT', 'NOT_RELEVANT'}
FRAMEWORK_RELATIONS = ['RACE', 'STP', 'JTBD', 'AIDA', 'FABE', '4P', 'FUNNEL']
INCLUSIVE_PERSON_FIELDS = [
    'skin_tone_exposure', 'deep_skin_shadow_protection', 'reflector_bounce_diffusion', 'hair_texture',
    'body_representation', 'disability_representation', 'age_representation', 'ai_bias_check',
]
CORE_HOST_FULL_FILES = [
    'index.html', '00_PROJECT_HUB.md', 'HUMAN_DELIVERY.json', 'FULL_DELIVERY_DEPTH_AUDIT.json',
    'HUMAN_LANGUAGE_AUDIT.json', 'DELIVERY_LANGUAGE_MATRIX_AUDIT.json', 'PLATFORM_SCOPE.json',
    'SOURCE_TRUTH_MEDIA_AUDIT.json', 'strategy/MASTER_STRATEGY_CN.md', 'strategy/strategy_authority.json',
    'strategy/STRATEGY_DECISION_INDEX.json', 'strategy/COMMERCE_DECISION_CONTEXT.json',
    'strategy/COMMERCIAL_CONTINUITY_AUDIT.json', 'supporting_analysis/product_truth.json',
    'supporting_analysis/target_context.json', 'supporting_analysis/culture_context.json',
    'supporting_analysis/asset_architecture.json', 'supporting_analysis/seven_agent_synthesis.json',
    'ASSET_UNIVERSE.json', 'FULL_DELIVERY_OBJECT_MANIFEST.json',
]


def _present(value: Any) -> bool:
    return value not in (None, '', [], {})


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    if value in (None, '', {}):
        return []
    return value if isinstance(value, list) else [value]


def _status(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get('status') or '').upper()
    return str(value or '').upper()


def _reason_present(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    return any(_present(value.get(k)) for k in ('why', 'evidence', 'evidence_refs', 'assumption', 'source_refs', 'basis'))


def _issue(issues: list[dict[str, Any]], code: str, section: str | None = None, **extra: Any) -> None:
    row = {'code': code}
    if section:
        row['section'] = section
    row.update(extra)
    issues.append(row)


def _full_mode(strategy: dict[str, Any]) -> bool:
    hp = _dict(strategy.get('human_projection'))
    mode = str(hp.get('mode') or strategy.get('delivery_mode') or strategy.get('scope_mode') or '').upper()
    return mode == 'FULL' or hp.get('fixed_human_section_quota') is True


def _people_present(vis: dict[str, Any]) -> bool:
    marker = str(vis.get('people_applicability') or '').upper()
    if marker in {'PERSON_PRESENT', 'PEOPLE_PRESENT', 'HUMAN_PRESENT', 'APPLICABLE_P0'}:
        return True
    if _present(vis.get('casting')):
        return True
    for row in _list(vis.get('asset_parameter_reasoning')):
        if not isinstance(row, dict):
            continue
        subject = _dict(row.get('subject_system'))
        st = str(subject.get('subject_type') or row.get('subject_type') or '').upper()
        if st in {'PERSON', 'MULTI_SUBJECT'}:
            return True
        if any(_present(row.get(k)) for k in ('human_context', 'people', 'hands', 'body_relation')):
            return True
    return False


def audit_full_strategy_depth_v3(strategy: dict[str, Any], base_result: dict[str, Any] | None = None) -> dict[str, Any]:
    """Audit real FULL depth. Headings, booleans and one generic paragraph are never sufficient."""
    if not _full_mode(strategy):
        return {
            'status': 'NOT_REQUIRED_FOR_TASK_SCOPED', 'mode': 'TASK_SCOPED', 'issues': [], 'warnings': [],
            'depth_contract': 'FULL_COMMERCIAL_DEPTH_V3_HOST_RUNTIME_PARITY',
        }
    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if base_result:
        issues.extend(list(base_result.get('issues') or []))
        warnings.extend(list(base_result.get('warnings') or []))
    sections = _dict(strategy.get('sections'))

    # 01: audit / assumptions / tradeoffs.
    info = _dict(sections.get('01_information_completeness_assumptions_decisions'))
    if not _present(info.get('assumptions')):
        _issue(issues, 'FULL_ASSUMPTION_LOG_MISSING', '01_information_completeness_assumptions_decisions')
    for i, row in enumerate(_list(info.get('decision_log'))):
        if not isinstance(row, dict):
            _issue(issues, 'FULL_DECISION_LOG_INVALID', '01_information_completeness_assumptions_decisions', row=i)
            continue
        missing = [k for k in ('what', 'why', 'evidence', 'tradeoff', 'execution', 'measurement') if not _present(row.get(k))]
        if missing:
            _issue(issues, 'FULL_DECISION_LOG_DEPTH_MISSING', '01_information_completeness_assumptions_decisions', row=i, fields=missing)

    # 02: product truth/value ladder must retain source/evidence and the four requested commercial layers.
    value = _dict(sections.get('02_product_truth_value_ladder'))
    value_rows = _list(value.get('product_facts')) + _list(value.get('claim_value_ladder'))
    for i, row in enumerate(value_rows):
        if not isinstance(row, dict):
            continue
        required = ['real_selling_point', 'perceived_benefit', 'emotional_value', 'claim_boundary', 'evidence_grade']
        if not _present(row.get('source_refs')) and not _present(row.get('source_ids')) and not _present(row.get('evidence_refs')):
            required.append('source_refs')
        missing = [k for k in required if not _present(row.get(k))]
        if missing:
            _issue(issues, 'FULL_PRODUCT_TRUTH_VALUE_DEPTH_MISSING', '02_product_truth_value_ladder', row=i, fields=missing)
        if str(row.get('evidence_grade') or row.get('evidence_level') or '').upper() == 'C' and str(row.get('publication_status') or '').upper() in {'HARD', 'HARD_CLAIM', 'ACTIVE_HARD'}:
            _issue(issues, 'FULL_C_LEVEL_HARD_CLAIM_FORBIDDEN', '02_product_truth_value_ladder', row=i)

    # 03: platform × region × audience × culture must cover all operating dimensions explicitly.
    culture = _dict(sections.get('03_platform_region_audience_culture_insight'))
    dimensions = _dict(culture.get('dimension_status') or culture.get('research_dimension_status') or culture.get('market_culture_dimension_status'))
    for key in MARKET_CULTURE_DIMENSIONS:
        if key not in dimensions:
            _issue(issues, 'FULL_MARKET_CULTURE_DIMENSION_MISSING', '03_platform_region_audience_culture_insight', dimension=key)
            continue
        entry = dimensions.get(key)
        st = _status(entry)
        if st not in DIMENSION_STATUSES:
            _issue(issues, 'FULL_MARKET_CULTURE_DIMENSION_STATUS_INVALID', '03_platform_region_audience_culture_insight', dimension=key, status=st)
        if isinstance(entry, dict) and not _reason_present(entry):
            _issue(issues, 'FULL_MARKET_CULTURE_DIMENSION_BASIS_MISSING', '03_platform_region_audience_culture_insight', dimension=key)

    intersections = _list(culture.get('intersectionality_table'))
    if not intersections:
        _issue(issues, 'FULL_INTERSECTIONALITY_TABLE_MISSING', '03_platform_region_audience_culture_insight')
    for i, row in enumerate(intersections):
        if not isinstance(row, dict):
            _issue(issues, 'FULL_INTERSECTIONALITY_ROW_INVALID', '03_platform_region_audience_culture_insight', row=i)
            continue
        missing = [k for k in ('dimensions', 'implication', 'evidence_or_assumption', 'stereotype_guard', 'execution') if not _present(row.get(k))]
        if missing:
            _issue(issues, 'FULL_INTERSECTIONALITY_ROW_SHALLOW', '03_platform_region_audience_culture_insight', row=i, fields=missing)

    localization_rows = _list(culture.get('localization_operating_table') or culture.get('adaptation_rows'))
    required_localization = {'language', 'holiday_calendar', 'payment', 'logistics', 'religion', 'local_regulation'}
    seen_localization: set[str] = set()
    for i, row in enumerate(localization_rows):
        if not isinstance(row, dict):
            continue
        dim = str(row.get('dimension') or row.get('adaptation_point') or '').strip().lower()
        aliases = {
            'religion_taboo': 'religion', 'religion/faith': 'religion', 'religion_faith': 'religion',
            'law': 'local_regulation', 'regulation': 'local_regulation', 'local_law': 'local_regulation',
            'holidays': 'holiday_calendar', 'holiday': 'holiday_calendar', 'festival': 'holiday_calendar',
            'language_back_translation': 'language', 'back_translation': 'language',
            'fulfillment': 'logistics', 'shipping': 'logistics',
        }
        dim = aliases.get(dim, dim)
        if dim in required_localization:
            seen_localization.add(dim)
        missing = [k for k in ('status', 'action', 'why') if not _present(row.get(k))]
        if not _present(row.get('evidence_or_assumption')) and not _present(row.get('evidence_refs')):
            missing.append('evidence_or_assumption')
        if missing:
            _issue(issues, 'FULL_LOCALIZATION_OPERATING_ROW_SHALLOW', '03_platform_region_audience_culture_insight', row=i, fields=missing)
    for dim in sorted(required_localization - seen_localization):
        # A dimension may be explicitly declared NOT_RELEVANT / MISSING_INPUT / TO_VERIFY in the dimension map.
        mapped = dimensions.get('religion' if dim == 'religion' else dim)
        if _status(mapped) not in {'NOT_RELEVANT', 'MISSING_INPUT', 'TO_VERIFY'}:
            _issue(issues, 'FULL_LOCALIZATION_OPERATING_DIMENSION_MISSING', '03_platform_region_audience_culture_insight', dimension=dim)

    # 04: frameworks must explain relationships; they are lenses, not boxes to mechanically fill.
    core = _dict(sections.get('04_marketing_core_strategy'))
    relations = _dict(core.get('framework_relationships'))
    for key in FRAMEWORK_RELATIONS:
        entry = relations.get(key)
        if not isinstance(entry, dict) or not _present(entry.get('role')) or not _present(entry.get('why')):
            _issue(issues, 'FULL_FRAMEWORK_RELATION_MISSING', '04_marketing_core_strategy', framework=key)

    # 05: visual execution must include concrete routes and people-inclusive details only when people appear.
    vis = _dict(sections.get('05_visual_photography_strategy'))
    visual_aliases = {
        'style_moodboard': ('style_keywords', 'moodboard_direction', 'creative_direction', 'visual_thesis'),
        'composition': ('composition', 'composition_rules'),
        'palette_contrast': ('palette_hex', 'palette', 'color_system'),
        'lighting': ('lighting_framework', 'lighting'),
        'lens_camera': ('camera', 'lens', 'photography_execution'),
        'scene': ('scene', 'scene_system', 'environment_system'),
        'props': ('props', 'prop_system', 'supporting_elements'),
        'subject_casting': ('subject_system', 'casting', 'people_applicability'),
        'platform_dimensions': ('platform_dimensions',),
        'shot_list': ('shot_list', 'asset_parameter_reasoning'),
    }
    applicability = _dict(vis.get('visual_execution_status'))
    for dim, aliases in visual_aliases.items():
        if any(_present(vis.get(a)) for a in aliases):
            continue
        if _status(applicability.get(dim)) in {'NOT_RELEVANT', 'NOT_APPLICABLE', 'TO_VERIFY', 'MISSING_INPUT'}:
            continue
        _issue(issues, 'FULL_VISUAL_EXECUTION_DIMENSION_MISSING', '05_visual_photography_strategy', dimension=dim)
    if _people_present(vis):
        inclusive = _dict(vis.get('inclusive_photography'))
        for key in INCLUSIVE_PERSON_FIELDS:
            if not _present(inclusive.get(key)):
                _issue(issues, 'FULL_INCLUSIVE_PHOTOGRAPHY_DIMENSION_MISSING', '05_visual_photography_strategy', dimension=key)

    # 06: per-surface execution mechanics are mandatory when the row exists.
    matrix = _list(sections.get('06_platform_content_matrix'))
    matrix_fields = [
        'platform', 'audience', 'topic', 'hook', 'script_structure', 'visual_form', 'cta', 'metric', 'race_stage',
        'culture_adaptation', 'taboo_stereotype_check', 'platform_dimensions', 'duration', 'cover_first_frame',
        'subtitle_strategy', 'music_rights', 'traffic_mechanism', 'landing_handoff', 'utm_attribution', 'why',
    ]
    for i, row in enumerate(matrix):
        if not isinstance(row, dict):
            _issue(issues, 'FULL_CONTENT_MATRIX_ROW_INVALID', '06_platform_content_matrix', row=i)
            continue
        missing = [k for k in matrix_fields if not _present(row.get(k))]
        if missing:
            _issue(issues, 'FULL_CONTENT_MATRIX_DEPTH_MISSING', '06_platform_content_matrix', row=i, fields=missing)

    # 07: RACE = Research -> Action -> Communication -> Evaluation in CBCC.
    race = _list(sections.get('07_race_execution_table'))
    expected = ['RESEARCH', 'ACTION', 'COMMUNICATION', 'EVALUATION']
    actual = [str(_dict(row).get('stage') or '').upper() for row in race]
    if actual != expected:
        _issue(issues, 'FULL_RACE_STAGES_INCOMPLETE', '07_race_execution_table', expected=expected, actual=actual)
    for i, row in enumerate(race):
        if not isinstance(row, dict):
            continue
        missing = [k for k in ('stage', 'objective', 'key_actions', 'output', 'platform', 'culture_check', 'kpi', 'why') if not _present(row.get(k))]
        if missing:
            _issue(issues, 'FULL_RACE_ROW_DEPTH_MISSING', '07_race_execution_table', row=i, fields=missing)

    # 08: culture checklist needs evidence/assumption, not labels only.
    checklist = _list(sections.get('08_culture_adaptation_checklist'))
    for i, row in enumerate(checklist):
        if not isinstance(row, dict):
            continue
        missing = [k for k in ('adaptation_point', 'inclusive_representation', 'stereotype_taboo_risk', 'result', 'modification', 'why') if not _present(row.get(k))]
        if not _present(row.get('evidence_or_assumption')) and not _present(row.get('evidence_refs')):
            missing.append('evidence_or_assumption')
        if missing:
            _issue(issues, 'FULL_CULTURE_CHECKLIST_DEPTH_MISSING', '08_culture_adaptation_checklist', row=i, fields=missing)

    # 09: resource constraints must force tradeoffs; self-check expands beyond six booleans.
    last = _dict(sections.get('09_risk_measurement_priority_next_steps'))
    tradeoff = _dict(last.get('resource_tradeoff_plan'))
    for key in ('constraints', 'keep', 'cut', 'why'):
        if not _present(tradeoff.get(key)):
            _issue(issues, 'FULL_RESOURCE_TRADEOFF_MISSING', '09_risk_measurement_priority_next_steps', field=key)
    self_check = _dict(last.get('output_self_check'))
    for key in (
        'fabrication_check', 'why_check', 'culture_check', 'compliance_check', 'metric_check', 'assumption_check',
        'language_companion_check', 'asset_universe_check', 'prompt_depth_check',
    ):
        if key not in self_check:
            _issue(issues, 'FULL_OUTPUT_SELF_CHECK_MISSING', '09_risk_measurement_priority_next_steps', field=key)

    # De-duplicate exact issue signatures when base validator already reported the same defect.
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in issues:
        sig = json.dumps(item, ensure_ascii=False, sort_keys=True, default=str)
        if sig in seen:
            continue
        seen.add(sig)
        unique.append(item)
    return {
        'status': 'PASS' if not unique else 'INCOMPLETE',
        'mode': 'FULL',
        'issues': unique,
        'warnings': warnings,
        'required_market_culture_dimensions': MARKET_CULTURE_DIMENSIONS,
        'required_framework_relationships': FRAMEWORK_RELATIONS,
        'depth_contract': 'FULL_COMMERCIAL_DEPTH_V3_HOST_RUNTIME_PARITY',
    }


def audit_asset_portfolio_depth(universe: dict[str, Any], packaged_asset_ids: set[str] | None = None) -> dict[str, Any]:
    universe = _dict(universe)
    assets = _list(universe.get('assets'))
    packaged_asset_ids = set(packaged_asset_ids or set())
    rows: list[dict[str, Any]] = [x for x in assets if isinstance(x, dict)]
    ids = [str(x.get('asset_id') or x.get('id') or '') for x in rows if (x.get('asset_id') or x.get('id'))]
    live = [x for x in rows if str(x.get('deployment_state') or x.get('pool') or '').upper() in {'LIVE_CANDIDATE', 'LIVE', 'ACTIVATION'}]
    capacity = universe.get('activation_capacity') or universe.get('gallery_capacity') or universe.get('platform_slot_capacity')
    issues: list[dict[str, Any]] = []
    if universe.get('fixed_total_asset_limit') is True:
        _issue(issues, 'ASSET_UNIVERSE_TOTAL_LIMIT_FORBIDDEN')
    if universe.get('platform_capacity_is_activation_constraint_only') is not True:
        _issue(issues, 'ACTIVATION_CAPACITY_BOUNDARY_MISSING')
    materialization_required = {
        str(x.get('asset_id') or x.get('id'))
        for x in rows
        if (x.get('asset_id') or x.get('id')) and str(x.get('deployment_state') or x.get('pool') or '').upper() not in {'ARCHIVE', 'NOT_NEEDED'}
    }
    missing = sorted(materialization_required - packaged_asset_ids) if packaged_asset_ids else []
    if missing:
        _issue(issues, 'ASSET_UNIVERSE_CANDIDATES_NOT_MATERIALIZED', missing_asset_ids=missing)
    return {
        'status': 'PASS' if not issues else 'INCOMPLETE',
        'issues': issues,
        'total_asset_candidates': len(rows),
        'live_candidate_count': len(live),
        'activation_capacity': capacity,
        'missing_materialized_asset_ids': missing,
        'asset_family_counts': dict(Counter(str(x.get('asset_family') or x.get('family') or 'OTHER') for x in rows)),
        'deployment_state_counts': dict(Counter(str(x.get('deployment_state') or x.get('pool') or 'UNSPECIFIED') for x in rows)),
        'principle': 'Platform capacity constrains Activation Set only; it never truncates the commercial Asset Universe.',
    }


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r'[\u3400-\u4dbf\u4e00-\u9fff]', text or ''))


def _listing_has_foreign_copy(text: str) -> bool:
    low = text.lower()
    return any(token in low for token in ('title_en', 'title_bm', 'description — en', 'description — bm', 'key bullets — en', 'key bullets — bm', 'search terms\nen:', '## title_en'))


def _listing_has_chinese_companion(text: str) -> bool:
    low = text.lower()
    return any(token in low for token in ('中文释义', '中文用途', '中文说明', '_zh', '— 中文', '## 中文'))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _asset_ids_from_package(package_dir: Path) -> set[str]:
    root = package_dir / 'asset_packages'
    return {p.name for p in root.iterdir() if p.is_dir()} if root.exists() else set()


def _audit_design_card_depth(card: dict[str, Any], asset_id: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    # Current commercial Design Card may use compatibility aliases; accept them, but require the decision itself.
    required_groups = {
        'strategic_job': ('strategic_job', 'shopper_question', 'consumer_question', 'belief_transition'),
        'visual_carrier': ('visual_carrier', 'carrier', 'role'),
        'product_presence': ('product_presence', 'product_role', 'product'),
        'subject_system': ('subject_system', 'subject_type', 'subject'),
        'scene_environment': ('scene', 'environment', 'scene_system', 'decisive_moment'),
        'props_elements': ('props', 'supporting_elements', 'evidence_elements'),
        'evidence_mode': ('evidence_mode', 'evidence_hierarchy', 'proof', 'proof_mechanism'),
        'composition': ('composition_grammar', 'composition', 'spatial_rhythm'),
        'cmf_material': ('cmf', 'material', 'palette', 'palette_hex'),
        'portfolio_delta': ('portfolio_delta', 'variant_hypothesis', 'test_hypothesis', 'incremental_information'),
        'measurement': ('measurement_hypothesis', 'success_metric', 'metric'),
    }
    for label, aliases in required_groups.items():
        if not any(_present(card.get(k)) for k in aliases):
            _issue(issues, 'ASSET_DESIGN_CARD_DECISION_MISSING', asset_id=asset_id, decision=label)
    return issues


def audit_host_full_package(package_dir: Path | str) -> dict[str, Any]:
    """Host-native and Runtime exports must materialize the same FULL business object contract."""
    package_dir = Path(package_dir)
    issues: list[dict[str, Any]] = []
    for rel in CORE_HOST_FULL_FILES:
        if not (package_dir / rel).exists():
            _issue(issues, 'FULL_DELIVERY_OBJECT_MISSING', path=rel)

    # Listing foreign copy needs same-object Chinese interpretation/use in the human artifact.
    listing_candidates = [package_dir / '01_LISTING_UPLOAD_READY.md', package_dir / 'listing' / '01_LISTING_UPLOAD_READY.md']
    for path in listing_candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8', errors='ignore')
        if _listing_has_foreign_copy(text) and not _listing_has_chinese_companion(text):
            _issue(issues, 'LISTING_CHINESE_COMPANION_MISSING', path=str(path.relative_to(package_dir)))

    # English model prompt is provider-facing execution language. Chinese instructional prose belongs in CN prompt/human card.
    prompt_root = package_dir / 'asset_packages'
    if prompt_root.exists():
        for en_path in sorted(prompt_root.glob('*/06_prompt_EN.txt')):
            text = en_path.read_text(encoding='utf-8', errors='ignore')
            if _contains_cjk(text):
                _issue(issues, 'MODEL_PROMPT_EN_LANGUAGE_PURITY_FAILED', asset_id=en_path.parent.name, path=str(en_path.relative_to(package_dir)))
        for card_path in sorted(prompt_root.glob('*/12_design_card.json')):
            card = _read_json(card_path)
            issues.extend(_audit_design_card_depth(card, card_path.parent.name))

    # Asset Universe must be separately exported and all non-archive candidates materialized.
    universe = _read_json(package_dir / 'ASSET_UNIVERSE.json')
    if universe:
        portfolio = audit_asset_portfolio_depth(universe, _asset_ids_from_package(package_dir))
        issues.extend(portfolio.get('issues') or [])
    else:
        portfolio = {'status': 'INCOMPLETE', 'issues': [{'code': 'ASSET_UNIVERSE_EXPORT_MISSING'}]}
        issues.extend(portfolio['issues'])

    # Cross-object materialization: if the human strategy activates video/creator/paid/test pools, a real object must exist.
    content_text = ''
    for path in (package_dir / 'strategy', package_dir / 'content'):
        if path.exists():
            for f in path.rglob('*'):
                if f.is_file() and f.suffix.lower() in {'.md', '.txt', '.csv', '.json'}:
                    content_text += '\n' + f.read_text(encoding='utf-8', errors='ignore')
    low = content_text.lower()
    if any(t in low for t in ('creator video', 'product video', 'short video', 'pdp_video', 'video a', 'video b')):
        if not (package_dir / 'video').exists() and not (package_dir / 'video_packages').exists():
            _issue(issues, 'ACTIVE_VIDEO_OBJECT_NOT_MATERIALIZED')
    if any(t in low for t in ('paid/spark', 'paid media', 'spark-ready', 'paid creative')):
        ad_ids = {x for x in _asset_ids_from_package(package_dir) if x.upper().startswith(('AD-', 'PAID-'))}
        if not ad_ids:
            _issue(issues, 'ACTIVE_PAID_ASSET_NOT_MATERIALIZED')

    # Repeated generic production notes / hypotheses are a portfolio-depth regression signal.
    if prompt_root.exists():
        notes = []
        measurements = []
        for p in sorted(prompt_root.glob('*/09_production_notes.md')):
            notes.append(p.read_text(encoding='utf-8', errors='ignore').strip())
        for p in sorted(prompt_root.glob('*/12_design_card.json')):
            d = _read_json(p)
            if _present(d.get('measurement_hypothesis')):
                measurements.append(str(d.get('measurement_hypothesis')).strip())
        if len(notes) >= 5:
            top = Counter(notes).most_common(1)[0][1]
            if top / len(notes) >= 0.7:
                _issue(issues, 'PORTFOLIO_PRODUCTION_NOTES_OVER_REUSED', duplicate_ratio=round(top / len(notes), 3))
        if len(measurements) >= 5:
            top = Counter(measurements).most_common(1)[0][1]
            if top / len(measurements) >= 0.7:
                _issue(issues, 'PORTFOLIO_MEASUREMENT_HYPOTHESIS_OVER_REUSED', duplicate_ratio=round(top / len(measurements), 3))

    return {
        'status': 'PASS' if not issues else 'INCOMPLETE',
        'issues': issues,
        'asset_portfolio': portfolio,
        'contract': 'HOST_NATIVE_FULL_MATERIALIZATION_EQUALS_RUNTIME_EXPORT_V3',
    }
