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

def validate_strategy_delivery(strategy: dict[str, Any]) -> dict[str, Any]:
    sections = strategy.get('sections') or {}
    issues=[]; warnings=[]
    for key in REQUIRED_SECTIONS:
        if key not in sections: issues.append({'code':'MISSING_REQUIRED_SECTION','section':key})
    race=sections.get('07_race_execution_table') or []
    got=[str(x.get('stage') or '').upper() for x in race]
    if got != RACE_STAGES: issues.append({'code':'RACE_STAGE_DEFINITION_MISMATCH','expected':RACE_STAGES,'actual':got})
    value=sections.get('02_product_truth_value_ladder') or {}
    for row in (value.get('product_facts') or []) + (value.get('claim_value_ladder') or []):
        grade=str(row.get('evidence_grade') or row.get('evidence_level') or '').upper()
        if grade not in EVIDENCE_LEVELS: issues.append({'code':'EVIDENCE_GRADE_MISSING','item':row.get('claim') or row.get('fact')})
        if grade=='C' and str(row.get('publication_status') or '').upper() in {'ACTIVE','HARD_CLAIM','HARD_CLAIM_ALLOWED'}:
            issues.append({'code':'C_LEVEL_HARD_CLAIM_FORBIDDEN','item':row.get('claim') or row.get('fact')})
    info=sections.get('01_information_completeness_assumptions_decisions') or {}
    if len(info.get('clarifying_questions') or [])>10: issues.append({'code':'TOO_MANY_CLARIFYING_QUESTIONS','count':len(info.get('clarifying_questions') or [])})
    vis=sections.get('05_visual_photography_strategy') or {}
    for k in ['palette_hex','composition','lighting_framework','camera','lens','scene','casting','platform_dimensions','photography_execution']:
        if vis.get(k) in (None,'',{},[]): warnings.append({'code':'VISUAL_EXECUTION_FIELD_EMPTY','field':k})
    matrix=sections.get('06_platform_content_matrix') or []
    matrix_fields=['platform','audience','topic','hook','script_structure','visual_form','cta','metric','race_stage','culture_adaptation','taboo_stereotype_check','why']
    for i,row in enumerate(matrix):
        miss=[k for k in matrix_fields if row.get(k) in (None,'',[],{})]
        if miss: warnings.append({'code':'CONTENT_MATRIX_FIELDS_EMPTY','row':i,'fields':miss})
        if str(row.get('race_stage') or '').upper() in {'REACH','ACT','CONVERT','ENGAGE','PLAN'}: issues.append({'code':'LEGACY_RACE_STAGE_FORBIDDEN','row':i,'actual':row.get('race_stage')})
    last=sections.get('09_risk_measurement_priority_next_steps') or {}
    pr=last.get('priority_plan') or {}
    for key in ['P0','P1','P2']:
        if not pr.get(key): issues.append({'code':'PRIORITY_BUCKET_EMPTY','bucket':key})
    sc=last.get('output_self_check') or {}
    for key in ['fabrication_check','why_check','culture_check','compliance_check','metric_check','assumption_check']:
        if key not in sc: issues.append({'code':'OUTPUT_SELF_CHECK_MISSING','field':key})
    return {'status':'PASS' if not issues else 'INCOMPLETE','issues':issues,'warnings':warnings,'required_sections':REQUIRED_SECTIONS,'evidence_levels':EVIDENCE_LEVELS,'race_stages':RACE_STAGES}
