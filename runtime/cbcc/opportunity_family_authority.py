from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Mapping


OPPORTUNITY_FAMILY_REGISTRY = [
    {'family_id':'F01_HERO_IDENTITY','family':'Hero / Identity'},
    {'family_id':'F02_SELLING_POINT','family':'Selling Point'},
    {'family_id':'F03_LIFESTYLE_SCENARIO','family':'Lifestyle / Scenario'},
    {'family_id':'F04_HUMAN_INTERACTION','family':'Human Interaction'},
    {'family_id':'F05_NEGATIVE_COUNTEREXAMPLE','family':'Negative / Counterexample'},
    {'family_id':'F06_EXPECTATION_MANAGEMENT','family':'Expectation Management'},
    {'family_id':'F07_BRAND_IP_MEMORY','family':'Brand IP / Memory'},
    {'family_id':'F08_PACKAGING_UNBOXING_CONTENTS','family':'Packaging / Unboxing / Contents'},
    {'family_id':'F09_SIZE_COMPATIBILITY_COMPARISON','family':'Size / Compatibility / Comparison'},
    {'family_id':'F10_INGREDIENT_FORMULA_MATERIAL_TEXTURE_DETAIL_MACRO','family':'Ingredient / Formula / Material / Texture / Detail / Macro'},
    {'family_id':'F11_HOW_TO_ROUTINE_STEP','family':'How-to / Routine / Step'},
    {'family_id':'F12_FAQ_OBJECTION','family':'FAQ / Objection'},
    {'family_id':'F13_COMPARISON','family':'Comparison'},
    {'family_id':'F14_A_PLUS_PDP_LONGFORM','family':'A+ / PDP / Longform'},
    {'family_id':'F15_PAID_MEDIA_PERFORMANCE_CREATIVE','family':'Paid media / Performance creative'},
    {'family_id':'F16_SOCIAL_SEEDING_ORGANIC','family':'Social / Seeding / Organic'},
    {'family_id':'F17_CREATOR_UGC_AFFILIATE','family':'Creator / UGC / Affiliate'},
    {'family_id':'F18_PRODUCT_PDP_SHORT_VIDEO','family':'Product / PDP / Short video'},
    {'family_id':'F19_LIVE_COMMERCE','family':'LIVE commerce'},
    {'family_id':'F20_STORE_BANNER_LANDING_CAMPAIGN_SEASONAL','family':'Store / Banner / Landing / Campaign / Seasonal'},
    {'family_id':'F21_CRM_LIFECYCLE_POST_PURCHASE','family':'CRM / Lifecycle / Post-purchase'},
    {'family_id':'F22_TEST_ROTATION_AB_MULTIVARIATE','family':'Test / Rotation / A-B / Multivariate'},
    {'family_id':'F23_SOURCE_DOCUMENT_SYSTEM_INFORMATION','family':'Source-document / system-information output'},
]

_ALLOWED_STATES = {'NEEDED','NOT_NEEDED','TO_VERIFY','MISSING_INPUT'}


def _present(value: Any) -> bool:
    return value not in (None, '', [], {})


def _as_list(value: Any) -> list[Any]:
    if value in (None, '', [], {}):
        return []
    if isinstance(value, (list, tuple, set, frozenset)):
        return list(value)
    return [value]


def _decision_map(decisions: Any) -> dict[str, dict[str, Any]]:
    if isinstance(decisions, Mapping):
        out: dict[str, dict[str, Any]] = {}
        for key, value in decisions.items():
            if isinstance(value, Mapping):
                row = deepcopy(dict(value))
                row.setdefault('family_id', str(key))
                out[str(key).upper()] = row
        return out
    out = {}
    for value in _as_list(decisions):
        if not isinstance(value, Mapping):
            continue
        row = deepcopy(dict(value))
        family_id = str(row.get('family_id') or row.get('id') or '').upper()
        if family_id:
            out[family_id] = row
    return out


def compile_opportunity_family_evaluation(
    decisions: Any,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile the locked 23-family business evaluation *before* asset architecture.

    This is an evaluation authority, not an asset quota and not a visual-mechanism scorer.  Missing
    decisions stay visible as TO_VERIFY rather than being inferred from the absence/presence of assets.
    """
    context = dict(context or {})
    supplied = _decision_map(decisions)
    families: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    for order, registry_row in enumerate(OPPORTUNITY_FAMILY_REGISTRY, start=1):
        family_id = registry_row['family_id']
        raw = deepcopy(supplied.get(family_id) or {})
        authored_status = str(raw.get('status') or '').strip().upper()
        if authored_status not in _ALLOWED_STATES:
            if authored_status:
                issues.append({
                    'code':'PHASE3_OPPORTUNITY_FAMILY_STATUS_INVALID_V0676',
                    'family_id':family_id,
                    'value':authored_status,
                })
            authored_status = 'TO_VERIFY'

        why = raw.get('why')
        why_not = raw.get('why_not') or raw.get('omission_reason')
        satisfying_objects = _as_list(raw.get('satisfying_objects') or raw.get('planned_objects') or raw.get('object_refs'))
        missing_inputs = _as_list(raw.get('missing_inputs') or raw.get('missing_input'))
        evidence_refs = [str(x) for x in _as_list(raw.get('evidence_refs') or raw.get('source_refs')) if str(x or '').strip()]

        decision_status = 'TO_VERIFY'
        needed: bool | None = None
        if not raw:
            issues.append({
                'code':'PHASE3_OPPORTUNITY_FAMILY_DECISION_REQUIRED_V0676',
                'family_id':family_id,
                'message':'Every locked Phase 3 family must be explicitly evaluated before asset architecture; absence never means NOT_NEEDED.',
            })
        elif authored_status == 'NEEDED':
            needed = True
            valid = _present(why) and bool(satisfying_objects)
            decision_status = 'READY' if valid else 'TO_VERIFY'
            if not _present(why):
                issues.append({'code':'PHASE3_OPPORTUNITY_FAMILY_REASON_REQUIRED_V0676','family_id':family_id})
            if not satisfying_objects:
                issues.append({
                    'code':'PHASE3_NEEDED_FAMILY_SATISFIER_REQUIRED_V0676',
                    'family_id':family_id,
                    'message':'NEEDED requires at least one planned satisfying object/role before asset creation.',
                })
        elif authored_status == 'NOT_NEEDED':
            needed = False
            valid = _present(why) and _present(why_not)
            decision_status = 'READY' if valid else 'TO_VERIFY'
            if not _present(why):
                issues.append({'code':'PHASE3_OPPORTUNITY_FAMILY_REASON_REQUIRED_V0676','family_id':family_id})
            if not _present(why_not):
                issues.append({
                    'code':'PHASE3_NOT_NEEDED_REASON_REQUIRED_V0676',
                    'family_id':family_id,
                    'message':'NOT_NEEDED is a deliberate omission decision and therefore requires why_not/omission_reason.',
                })
        elif authored_status == 'MISSING_INPUT':
            needed = None
            decision_status = 'MISSING_INPUT'
            if not _present(why) or not missing_inputs:
                issues.append({
                    'code':'PHASE3_MISSING_INPUT_DETAIL_REQUIRED_V0676',
                    'family_id':family_id,
                    'message':'MISSING_INPUT must identify why evaluation is blocked and the exact missing input(s).',
                })
        else:
            needed = None
            decision_status = 'TO_VERIFY'
            if raw and not _present(why):
                issues.append({'code':'PHASE3_OPPORTUNITY_FAMILY_REASON_REQUIRED_V0676','family_id':family_id})

        row = {
            **registry_row,
            'order':order,
            'status':authored_status,
            'decision_status':decision_status,
            'needed':needed,
            'why':why or ('Explicit pre-asset family decision required.' if not raw else None),
            'why_not':why_not,
            'satisfying_objects':deepcopy(satisfying_objects),
            'missing_inputs':deepcopy(missing_inputs),
            'evidence_refs':evidence_refs,
            'source_refs':evidence_refs,
            'decision_origin':raw.get('decision_origin') or ('AGENT_OR_USER_AUTHORED' if raw else 'MISSING_EXPLICIT_DECISION'),
        }
        for key in ('surface_native_requirements','activation_boundary','notes','tradeoff','measurement'):
            if key in raw:
                row[key] = deepcopy(raw.get(key))
        families.append(row)

    unresolved = [x['family_id'] for x in families if x['decision_status'] != 'READY']
    needed_ids = [x['family_id'] for x in families if x['status'] == 'NEEDED']
    not_needed_ids = [x['family_id'] for x in families if x['status'] == 'NOT_NEEDED']
    return {
        'schema_version':'cbcc-phase3-opportunity-family-v0.6.76',
        'status':'READY' if not unresolved else 'TO_VERIFY',
        'evaluation_stage':'PRE_ASSET_ARCHITECTURE',
        'family_count':len(families),
        'locked_family_count':23,
        'families':families,
        'needed_family_ids':needed_ids,
        'not_needed_family_ids':not_needed_ids,
        'unresolved_family_ids':unresolved,
        'issues':issues,
        'fixed_asset_quota_per_family':False,
        'one_family_one_asset_required':False,
        'multiple_families_may_share_one_object':True,
        'platform_capacity_is_activation_constraint_only':True,
        'context':{
            'delivery_mode':context.get('delivery_mode') or context.get('scope_mode'),
            'market':context.get('market'),
            'platform_family':context.get('platform_family'),
            'site':context.get('site'),
            'category':context.get('category'),
        },
        'principle':'Evaluate every locked opportunity family before asset creation. A family may be NEEDED, deliberately NOT_NEEDED, TO_VERIFY or MISSING_INPUT; no family may disappear because no asset/file exists. Family evaluation never imposes one-family-one-asset or a fixed asset quota.',
    }


def _tokens(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value.strip().upper()} if value.strip() else set()
    if not isinstance(value, Mapping):
        return set()
    keys = ('asset_id','object_id','id','asset_role','role','family','asset_family','surface','decision_intent','variant_cluster','variant_id')
    return {str(value.get(k)).strip().upper() for k in keys if _present(value.get(k))}


def audit_opportunity_family_fulfillment(
    evaluation: Mapping[str, Any] | None,
    assets: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    evaluation = dict(evaluation or {})
    asset_rows = [dict(x) for x in (assets or []) if isinstance(x, Mapping)]
    asset_tokens = [(a, _tokens(a)) for a in asset_rows]
    rows: list[dict[str, Any]] = []
    unfulfilled: list[str] = []
    needed_count = 0
    fulfilled_needed = 0

    for family in evaluation.get('families') or []:
        if not isinstance(family, Mapping):
            continue
        row = deepcopy(dict(family))
        family_id = str(row.get('family_id') or '')
        if row.get('status') == 'NEEDED':
            needed_count += 1
            planned = _as_list(row.get('satisfying_objects'))
            matched_assets: list[str] = []
            matched_objects: list[Any] = []
            for planned_obj in planned:
                ptokens = _tokens(planned_obj)
                if not ptokens:
                    continue
                local_matches = [a for a, atokens in asset_tokens if ptokens & atokens]
                if local_matches:
                    matched_objects.append(deepcopy(planned_obj))
                    for asset in local_matches:
                        aid = str(asset.get('asset_id') or asset.get('id') or '')
                        if aid and aid not in matched_assets:
                            matched_assets.append(aid)
            fulfilled = bool(matched_objects)
            if fulfilled:
                fulfilled_needed += 1
            else:
                unfulfilled.append(family_id)
            rows.append({
                'family_id':family_id,
                'decision_status':row.get('decision_status'),
                'fulfillment_status':'FULFILLED' if fulfilled else 'TO_VERIFY',
                'planned_objects':deepcopy(planned),
                'matched_objects':matched_objects,
                'matched_asset_ids':matched_assets,
            })
        elif row.get('status') == 'NOT_NEEDED' and row.get('decision_status') == 'READY':
            rows.append({
                'family_id':family_id,
                'decision_status':'READY',
                'fulfillment_status':'NOT_REQUIRED_DELIBERATE_OMISSION',
                'planned_objects':[],
                'matched_objects':[],
                'matched_asset_ids':[],
                'why_not':row.get('why_not'),
            })
        else:
            rows.append({
                'family_id':family_id,
                'decision_status':row.get('decision_status'),
                'fulfillment_status':'TO_VERIFY',
                'planned_objects':deepcopy(_as_list(row.get('satisfying_objects'))),
                'matched_objects':[],
                'matched_asset_ids':[],
            })

    evaluation_ready = evaluation.get('status') == 'READY'
    return {
        'status':'READY' if evaluation_ready and not unfulfilled else 'TO_VERIFY',
        'evaluation_status':evaluation.get('status') or 'TO_VERIFY',
        'needed_family_count':needed_count,
        'fulfilled_needed_family_count':fulfilled_needed,
        'unfulfilled_family_ids':unfulfilled,
        'rows':rows,
        'asset_count':len(asset_rows),
        'fixed_asset_quota_per_family':False,
        'one_family_one_asset_required':False,
        'principle':'Fulfillment checks declared family decisions against produced architecture. One object may satisfy multiple families; missing active-family fulfillment remains visible and never forces unrelated extra assets.',
    }


def wrap_build_asset_architecture(fn: Callable[..., dict[str, Any]]):
    """Install Phase 3 evaluation before the mature asset architecture runs."""
    if getattr(fn, '_cbcc_v0676_phase3_opportunity_family', False):
        return fn

    def built(
        project_id: str,
        target: dict[str, Any],
        questions: list[str],
        content_objects: list[dict[str, Any]],
        asset_jobs: list[dict[str, Any]] | None = None,
        decision_context: dict[str, Any] | None = None,
        category_family: str = 'GENERAL_COMMERCE',
    ) -> dict[str, Any]:
        target_for_build = deepcopy(dict(target or {}))
        supplied_eval = target_for_build.get('phase3_opportunity_family_evaluation')
        if isinstance(supplied_eval, Mapping) and isinstance(supplied_eval.get('families'), list):
            evaluation = deepcopy(dict(supplied_eval))
        else:
            decisions = (
                target_for_build.get('opportunity_family_decisions')
                or target_for_build.get('phase3_opportunity_family_decisions')
                or {}
            )
            evaluation = compile_opportunity_family_evaluation(decisions, context=target_for_build)
        target_for_build['phase3_opportunity_family_evaluation'] = deepcopy(evaluation)
        out = deepcopy(fn(project_id, target_for_build, questions, content_objects, asset_jobs, decision_context, category_family))
        fulfillment = audit_opportunity_family_fulfillment(evaluation, out.get('assets') or [])
        out['phase3_opportunity_family_evaluation'] = deepcopy(evaluation)
        out['opportunity_family_fulfillment'] = fulfillment
        if isinstance(out.get('asset_universe'), dict):
            out['asset_universe']['phase3_opportunity_family_evaluation'] = deepcopy(evaluation)
            out['asset_universe']['opportunity_family_fulfillment'] = deepcopy(fulfillment)
        return out

    setattr(built, '_cbcc_v0676_phase3_opportunity_family', True)
    return built
