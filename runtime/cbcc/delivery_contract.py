from __future__ import annotations
from typing import Any

EVIDENCE_LEVELS = {
    'A': '检测报告 / 官方认证 / 可复现实测或可重复客观测量',
    'B': '供应链规格 / 配方数据 / 成分或机理支持 / 有边界的事实支持',
    'C': '主观体验 / 创意假设 / 待验证感知；不得作硬宣称',
}
RACE_STAGES = ['RESEARCH','ACTION','COMMUNICATION','EVALUATION']
REQUIRED_SECTIONS = [
    '01_information_completeness_assumptions_decisions',
    '02_product_truth_value_ladder',
    '03_platform_region_audience_culture_insight',
    '04_marketing_core_strategy',
    '05_visual_photography_strategy',
    '06_platform_content_matrix',
    '07_race_execution_table',
    '08_culture_adaptation_checklist',
    '09_risk_measurement_priority_next_steps',
]


def normalize_evidence_grade(value: Any, *, source_type: str = '', subjective: bool = False) -> str:
    v = str(value or '').strip().upper()
    if v in EVIDENCE_LEVELS:
        return v
    st = str(source_type or '').upper()
    if subjective or any(x in st for x in ['REVIEW','UGC','SUBJECTIVE','SENSORY','HYPOTHESIS']):
        return 'C'
    if any(x in st for x in ['TEST','LAB','CERT','CERTIFICATION','OFFICIAL','MEASUREMENT','INSTRUMENT']):
        return 'A'
    return 'B'


def publication_rule(grade: str) -> str:
    grade = normalize_evidence_grade(grade)
    if grade == 'A': return 'HARD_CLAIM_ALLOWED_WITH_SCOPE'
    if grade == 'B': return 'SUPPORTED_CLAIM_WITH_BOUNDED_WORDING'
    return 'SOFT_EXPERIENCE_OR_HYPOTHESIS_ONLY_NO_HARD_CLAIM'


def _present(value: Any) -> bool:
    return value not in (None, '', [], {})


def _missing(row: dict[str, Any], fields: list[str]) -> list[str]:
    return [k for k in fields if not _present(row.get(k))]


def _full_mode(strategy: dict[str, Any]) -> bool:
    hp = strategy.get('human_projection') or {}
    mode = str(hp.get('mode') or strategy.get('delivery_mode') or strategy.get('scope_mode') or '').upper()
    return mode == 'FULL' or hp.get('fixed_human_section_quota') is True


def _depth_issue(issues: list[dict[str, Any]], code: str, section: str, **extra: Any) -> None:
    issues.append({'code': code, 'section': section, **extra})


def validate_strategy_delivery(strategy: dict[str, Any]) -> dict[str, Any]:
    sections = strategy.get('sections') or {}
    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    full = _full_mode(strategy)

    for key in REQUIRED_SECTIONS:
        if key not in sections:
            issues.append({'code':'MISSING_REQUIRED_SECTION','section':key})

    race = sections.get('07_race_execution_table') or []
    got = [str(x.get('stage') or '').upper() for x in race]
    if full and got != RACE_STAGES:
        issues.append({'code':'RACE_STAGE_DEFINITION_MISMATCH','expected':RACE_STAGES,'actual':got})
    elif got and got != RACE_STAGES:
        warnings.append({'code':'RACE_STAGE_DEFINITION_MISMATCH','expected':RACE_STAGES,'actual':got})

    value = sections.get('02_product_truth_value_ladder') or {}
    value_rows = (value.get('product_facts') or []) + (value.get('claim_value_ladder') or [])
    for row in value_rows:
        grade = str(row.get('evidence_grade') or row.get('evidence_level') or '').upper()
        if grade not in EVIDENCE_LEVELS:
            issues.append({'code':'EVIDENCE_GRADE_MISSING','item':row.get('claim') or row.get('fact')})
        if grade == 'C' and str(row.get('publication_status') or '').upper() in {'ACTIVE','HARD_CLAIM','HARD_CLAIM_ALLOWED'}:
            issues.append({'code':'C_LEVEL_HARD_CLAIM_FORBIDDEN','item':row.get('claim') or row.get('fact')})

    info = sections.get('01_information_completeness_assumptions_decisions') or {}
    if len(info.get('clarifying_questions') or []) > 10:
        issues.append({'code':'TOO_MANY_CLARIFYING_QUESTIONS','count':len(info.get('clarifying_questions') or [])})

    vis = sections.get('05_visual_photography_strategy') or {}
    for k in ['palette_hex','composition','lighting_framework','camera','lens','scene','casting','platform_dimensions','photography_execution']:
        if not _present(vis.get(k)):
            warnings.append({'code':'VISUAL_EXECUTION_FIELD_EMPTY','field':k})

    matrix = sections.get('06_platform_content_matrix') or []
    matrix_fields = ['platform','audience','topic','hook','script_structure','visual_form','cta','metric','race_stage','culture_adaptation','taboo_stereotype_check','why']
    for i,row in enumerate(matrix):
        miss = _missing(row, matrix_fields)
        if miss:
            warnings.append({'code':'CONTENT_MATRIX_FIELDS_EMPTY','row':i,'fields':miss})
        if str(row.get('race_stage') or '').upper() in {'REACH','ACT','CONVERT','ENGAGE','PLAN'}:
            issues.append({'code':'LEGACY_RACE_STAGE_FORBIDDEN','row':i,'actual':row.get('race_stage')})

    last = sections.get('09_risk_measurement_priority_next_steps') or {}
    pr = last.get('priority_plan') or {}
    for key in ['P0','P1','P2']:
        if full and not pr.get(key):
            issues.append({'code':'PRIORITY_BUCKET_EMPTY','bucket':key})
    sc = last.get('output_self_check') or {}
    for key in ['fabrication_check','why_check','culture_check','compliance_check','metric_check','assumption_check']:
        if full and key not in sc:
            issues.append({'code':'OUTPUT_SELF_CHECK_MISSING','field':key})

    # FULL means decision-depth, not merely nine keys. TASK_SCOPED work remains dynamic.
    if full:
        # 01 — information / assumptions / decision log must explain consequences and continuation behavior.
        if not _present(info.get('domain_matrix')):
            _depth_issue(issues, 'FULL_INFO_DOMAIN_MATRIX_MISSING', REQUIRED_SECTIONS[0])
        if not _present(info.get('decision_log')):
            _depth_issue(issues, 'FULL_DECISION_LOG_MISSING', REQUIRED_SECTIONS[0])
        else:
            for i,row in enumerate(info.get('decision_log') or []):
                miss = _missing(row, ['what','why','execution','measurement'])
                if miss:
                    _depth_issue(issues, 'FULL_DECISION_LOG_SHALLOW', REQUIRED_SECTIONS[0], row=i, fields=miss)

        # 02 — fact -> selling point -> perceived benefit -> emotional value -> boundary, with evidence authority.
        if not value_rows:
            _depth_issue(issues, 'FULL_VALUE_LADDER_EMPTY', REQUIRED_SECTIONS[1])
        for i,row in enumerate(value_rows):
            commercial_fields = ['real_selling_point','perceived_benefit','emotional_value','claim_boundary']
            # compatibility aliases may be present on older fact rows.
            if not _present(row.get('real_selling_point')) and _present(row.get('selling_point')):
                row = {**row, 'real_selling_point': row.get('selling_point')}
            miss = _missing(row, commercial_fields)
            if miss:
                _depth_issue(issues, 'FULL_VALUE_TRANSLATION_SHALLOW', REQUIRED_SECTIONS[1], row=i, item=row.get('claim') or row.get('fact'), fields=miss)

        # 03 — region/platform/audience/culture must be operational, intersectional and stereotype-aware.
        culture = sections.get('03_platform_region_audience_culture_insight') or {}
        if not _present(culture.get('platform_audience_culture_rows')):
            _depth_issue(issues, 'FULL_PLATFORM_AUDIENCE_CULTURE_ROWS_MISSING', REQUIRED_SECTIONS[2])
        if not _present(culture.get('intersectionality_table')):
            _depth_issue(issues, 'FULL_INTERSECTIONALITY_MISSING', REQUIRED_SECTIONS[2])
        if not _present(culture.get('adaptation_rows')):
            _depth_issue(issues, 'FULL_LOCALIZATION_ADAPTATION_MISSING', REQUIRED_SECTIONS[2])
        for i,row in enumerate(culture.get('platform_audience_culture_rows') or []):
            miss = _missing(row, ['platform','region','audience','adaptation','stereotype_taboo_check','why'])
            if miss:
                _depth_issue(issues, 'FULL_PLATFORM_CULTURE_ROW_SHALLOW', REQUIRED_SECTIONS[2], row=i, fields=miss)

        # 04 — major strategy must expose positioning, message architecture, frameworks and decision rationale.
        core = sections.get('04_marketing_core_strategy') or {}
        for k in ['positioning','message_hierarchy','frameworks']:
            if not _present(core.get(k)):
                _depth_issue(issues, 'FULL_CORE_STRATEGY_COMPONENT_MISSING', REQUIRED_SECTIONS[3], field=k)
        positioning = core.get('positioning') or {}
        if positioning and not _present(positioning.get('why')):
            _depth_issue(issues, 'FULL_POSITIONING_WHY_MISSING', REQUIRED_SECTIONS[3])

        # 05 — visual strategy must be executable and asset-specific, not adjectives.
        for k in ['palette_hex','composition','lighting_framework','camera','lens','color_management','casting','platform_dimensions','shot_list','asset_parameter_reasoning','photography_rationale']:
            if not _present(vis.get(k)):
                _depth_issue(issues, 'FULL_VISUAL_EXECUTION_DEPTH_MISSING', REQUIRED_SECTIONS[4], field=k)
        if _present(vis.get('casting')) and not _present(vis.get('inclusive_photography')):
            _depth_issue(issues, 'FULL_INCLUSIVE_PHOTOGRAPHY_MISSING', REQUIRED_SECTIONS[4])

        # 06 — platform matrix must include production mechanics, localization and attribution, not just topic/hook.
        platform_exec_fields = [
            'platform_dimensions','duration','cover_first_frame','subtitle_strategy','music_rights',
            'traffic_mechanism','landing_handoff','utm_attribution'
        ]
        if not matrix:
            _depth_issue(issues, 'FULL_CONTENT_MATRIX_EMPTY', REQUIRED_SECTIONS[5])
        for i,row in enumerate(matrix):
            miss = _missing(row, matrix_fields + platform_exec_fields)
            if miss:
                _depth_issue(issues, 'FULL_CONTENT_MATRIX_SHALLOW', REQUIRED_SECTIONS[5], row=i, fields=miss)

        # 07 — every RACE phase requires objective, action, output, culture check, KPI and WHY.
        for i,row in enumerate(race):
            miss = _missing(row, ['stage','objective','key_actions','output','platform','culture_check','kpi','why'])
            if miss:
                _depth_issue(issues, 'FULL_RACE_ROW_SHALLOW', REQUIRED_SECTIONS[6], row=i, fields=miss)

        # 08 — culture checklist must say what changes, not merely acknowledge culture.
        checklist = sections.get('08_culture_adaptation_checklist') or []
        if not checklist:
            _depth_issue(issues, 'FULL_CULTURE_CHECKLIST_EMPTY', REQUIRED_SECTIONS[7])
        for i,row in enumerate(checklist):
            miss = _missing(row, ['adaptation_point','inclusive_representation','stereotype_taboo_risk','result','modification','why'])
            if miss:
                _depth_issue(issues, 'FULL_CULTURE_CHECKLIST_SHALLOW', REQUIRED_SECTIONS[7], row=i, fields=miss)

        # 09 — risk/measurement must include tests, next information and explicit tradeoffs.
        if not _present(last.get('ab_test_hypotheses')):
            _depth_issue(issues, 'FULL_AB_TESTS_MISSING', REQUIRED_SECTIONS[8])
        if not _present(last.get('next_information_needed')) and not _present(last.get('next_information')):
            _depth_issue(issues, 'FULL_NEXT_INFORMATION_MISSING', REQUIRED_SECTIONS[8])
        if not _present(last.get('risks')) and not _present(last.get('risk_register')):
            _depth_issue(issues, 'FULL_RISK_REGISTER_MISSING', REQUIRED_SECTIONS[8])

    return {
        'status':'PASS' if not issues else 'INCOMPLETE',
        'mode':'FULL' if full else 'TASK_SCOPED',
        'issues':issues,
        'warnings':warnings,
        'required_sections':REQUIRED_SECTIONS,
        'evidence_levels':EVIDENCE_LEVELS,
        'race_stages':RACE_STAGES,
        'depth_contract':'FULL_DECISION_DEPTH_V1',
    }
