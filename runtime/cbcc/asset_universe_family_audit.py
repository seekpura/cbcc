from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

FAMILY_AXES = (
    ('gallery_identity', 'Gallery / Hero / Search / PDP identity & conversion'),
    ('benefit_proof_detail', 'Benefit / Proof / Ingredient / Material / Detail'),
    ('scenario_human_context', 'Scenario / Lifestyle / Context / Human-use'),
    ('howto_objection_comparison', 'How-to / Routine / Comparison / Objection'),
    ('rich_pdp_source', 'A+ / Rich Content / PDP longform / specification / source-document'),
    ('paid_media', 'Paid Ads / performance creative'),
    ('social_seeding', 'Social / Seeding'),
    ('creator_affiliate', 'Creator / UGC / Affiliate'),
    ('video_live', 'Short Video / PDP Video / LIVE'),
    ('store_campaign', 'Store / Banner / Landing / Campaign / Seasonal'),
    ('lifecycle', 'CRM / Lifecycle / Post-purchase'),
    ('test_rotation', 'Test / Rotation / A-B / multivariate'),
)


def _txt(v: Any) -> str:
    return str(v or '').upper()


def _family_keys(asset: dict[str, Any]) -> set[str]:
    surface = _txt(asset.get('surface'))
    family = _txt(asset.get('family'))
    cluster = _txt(asset.get('variant_cluster'))
    intent = _txt(asset.get('decision_intent'))
    deployment = _txt(asset.get('deployment_state'))
    blob = ' '.join((surface, family, cluster, intent, deployment))
    out = set()
    if any(x in blob for x in ('GALLERY', 'HERO', 'SEARCH', 'PDP', 'IDENTIFY')):
        out.add('gallery_identity')
    if any(x in blob for x in ('BENEFIT', 'PROOF', 'INGREDIENT', 'MATERIAL', 'DETAIL', 'PERFORMANCE')):
        out.add('benefit_proof_detail')
    if any(x in blob for x in ('SCENARIO', 'LIFESTYLE', 'CONTEXT', 'HUMAN', 'PERSON')):
        out.add('scenario_human_context')
    if any(x in blob for x in ('HOW_TO', 'HOWTO', 'ROUTINE', 'COMPARISON', 'OBJECTION', 'USAGE', 'CARE')):
        out.add('howto_objection_comparison')
    if any(x in blob for x in ('A_PLUS', 'RICH', 'LONGFORM', 'SPECIFICATION', 'SOURCE_DOCUMENT', 'PDP_CONTENT')):
        out.add('rich_pdp_source')
    if any(x in blob for x in ('PAID', 'AD', 'SPARK')):
        out.add('paid_media')
    if any(x in blob for x in ('SOCIAL', 'SEEDING')):
        out.add('social_seeding')
    if any(x in blob for x in ('CREATOR', 'UGC', 'AFFILIATE')):
        out.add('creator_affiliate')
    if any(x in blob for x in ('VIDEO', 'LIVE')):
        out.add('video_live')
    if any(x in blob for x in ('STORE', 'BANNER', 'LANDING', 'CAMPAIGN', 'SEASONAL')):
        out.add('store_campaign')
    if any(x in blob for x in ('CRM', 'LIFECYCLE', 'POST_PURCHASE', 'RETENTION')):
        out.add('lifecycle')
    if any(x in blob for x in ('TEST_POOL', 'ROTATION', 'A/B', 'AB_', 'MULTIVARIATE', 'TESTING')) or asset.get('testing_variant'):
        out.add('test_rotation')
    return out


def _presence_state(asset: dict[str, Any]) -> tuple[str, bool, str]:
    presence = asset.get('product_presence')
    if not isinstance(presence, dict):
        art = asset.get('asset_art_direction') if isinstance(asset.get('asset_art_direction'), dict) else {}
        presence = art.get('product_presence')
    if isinstance(presence, dict):
        state = _txt(presence.get('planning_state')) or 'UNRESOLVED'
        why = str(presence.get('presence_why') or '')
        structured = bool(presence.get('planning_state') and presence.get('presence_why'))
        return state, structured, why
    raw = _txt(asset.get('presence') or presence)
    return raw or 'UNRESOLVED', False, ''


def wrap_compile_asset_universe(fn: Callable[..., dict[str, Any]]):
    def compiled(assets: list[dict[str, Any]], target: dict[str, Any] | None = None):
        out = deepcopy(fn(assets, target))
        assets = [x for x in (assets or []) if isinstance(x, dict)]

        coverage: dict[str, list[str]] = {key: [] for key, _ in FAMILY_AXES}
        for asset in assets:
            aid = str(asset.get('asset_id') or asset.get('id') or '')
            for key in _family_keys(asset):
                coverage[key].append(aid)

        supplied_decisions = {}
        if isinstance((target or {}).get('asset_family_decisions'), dict):
            supplied_decisions = (target or {}).get('asset_family_decisions') or {}

        family_audit = []
        unresolved = []
        for key, label in FAMILY_AXES:
            if coverage[key]:
                family_audit.append({
                    'family_key': key, 'family': label, 'status': 'COVERED',
                    'asset_ids': coverage[key], 'why': '当前 Asset Universe 已存在该家族的一个或多个商业候选。',
                })
                continue
            decision = supplied_decisions.get(key)
            if isinstance(decision, dict) and str(decision.get('status') or '').upper() in {'NOT_NEEDED', 'TO_VERIFY', 'MISSING_INPUT'} and decision.get('why'):
                row = {'family_key': key, 'family': label, 'asset_ids': [], **decision}
                row['status'] = str(row.get('status')).upper()
                family_audit.append(row)
                if row['status'] == 'TO_VERIFY':
                    unresolved.append(key)
            else:
                family_audit.append({
                    'family_key': key, 'family': label, 'status': 'TO_VERIFY', 'asset_ids': [],
                    'why': '本家族当前没有候选，也没有 Agent 明确的 NOT_NEEDED / MISSING_INPUT + WHY；FULL 完成前必须判断其商业相关性，不能静默省略。',
                })
                unresolved.append(key)

        presence_rows = []
        structured = 0
        visible = 0
        absent = 0
        for asset in assets:
            state, is_structured, why = _presence_state(asset)
            if is_structured:
                structured += 1
            if state in {'FORBIDDEN', 'ABSENT', 'PRODUCT_ABSENT', 'NOT_NEEDED'}:
                absent += 1
            elif state != 'UNRESOLVED':
                visible += 1
            presence_rows.append({
                'asset_id': asset.get('asset_id') or asset.get('id'),
                'planning_state': state,
                'structured_decision': is_structured,
                'presence_why': why,
            })

        out['opportunity_family_audit'] = family_audit
        out['opportunity_family_unresolved'] = unresolved
        out['opportunity_family_audit_status'] = 'PASS' if not unresolved else 'TO_VERIFY'
        out['product_presence_portfolio_audit'] = {
            'status': 'PASS' if structured == len(assets) else 'INCOMPLETE',
            'total_assets': len(assets),
            'structured_presence_decisions': structured,
            'visible_or_optional_count': visible,
            'absent_or_forbidden_count': absent,
            'all_visible_review_required': bool(assets and visible == len(assets)),
            'all_visible_review_rule': '全资产都显示商品并非绝对禁止，但不能来自默认值。若全部可见，每个资产必须有独立 presence_why，且组合层说明为何不存在更强的产品缺席/证据/人物/信息载体方案。',
            'assets': presence_rows,
        }
        return out
    return compiled
