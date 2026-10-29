from __future__ import annotations

from typing import Any

VERSION = '0.6.36-seven-tool-capability-continuity'

TOOL_ORDER = [
    '01_MARKET_RESEARCH',
    '02_PRODUCT_STRATEGY',
    '03_LISTING_CREATIVE',
    '04_PRODUCT_IMAGE',
    '05_PRODUCT_VIDEO',
    '06_ADVERTISING_OPTIMIZATION',
    '07_REVIEW_ANALYSIS',
]


def _status(obj: Any, default: str = 'NOT_SUPPLIED') -> str:
    if not isinstance(obj, dict) or not obj:
        return default
    return str(obj.get('status') or obj.get('release_status') or 'AVAILABLE')


def compile_seven_tool_continuity(
    *,
    domain: dict[str, Any] | None = None,
    architecture: dict[str, Any] | None = None,
    video_plan: dict[str, Any] | None = None,
    paid_campaigns: dict[str, Any] | None = None,
    pricing_economics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    domain = domain or {}
    architecture = architecture or {}
    video_plan = video_plan or {}
    paid_campaigns = paid_campaigns or {}
    pricing = pricing_economics or domain.get('pricing_economics_authority') or {}
    market = domain.get('market') or {}
    listing = domain.get('listing') or {}
    ads = domain.get('ads') or {}
    feedback = domain.get('feedback') or {}
    assets = architecture.get('assets') or []
    images = [x for x in assets if str(x.get('asset_type') or x.get('type') or '').upper() in {'IMAGE', 'STATIC_IMAGE', 'PRODUCT_IMAGE'}]
    videos = video_plan.get('assets') or [x for x in assets if str(x.get('asset_type') or x.get('type') or '').upper() == 'VIDEO']
    pricing_ready = pricing.get('status') in {'READY', 'PARTIAL_MISSING_INPUT'}
    scenarios = pricing.get('scenarios') or []
    strict_ready = [x for x in scenarios if x.get('status') == 'CALCULATED_FROM_EXPLICIT_INPUTS']
    ads_floors = ((pricing.get('downstream_consumers') or {}).get('advertising_optimization') or {}).get('floors') or []
    listing_context = ((pricing.get('downstream_consumers') or {}).get('listing_creative') or {})

    capabilities = [
        {
            'id': '01_MARKET_RESEARCH',
            'name': 'Market Research',
            'first_class': True,
            'project_status': _status(market),
            'runtime_entry': 'tools.market.analyze_market',
            'real_consumers': ['Product Strategy', 'Listing/Search', 'Asset strategy after Product-Truth fit'],
            'business_outputs': ['market structure', 'price bands', 'price valleys', 'price/configuration matrix', 'keyword/review/competitor evidence'],
            'human_delivery': 'Commercial Brain / Market Research',
            'evidence': {'row_count': market.get('row_count'), 'price_band_count': len(market.get('price_bands') or []), 'price_valley_count': len(market.get('price_valley_signals') or [])},
        },
        {
            'id': '02_PRODUCT_STRATEGY',
            'name': 'Product Strategy',
            'first_class': True,
            'project_status': 'ACTIVE',
            'runtime_entry': 'strategy_depth + pricing_economics_authority',
            'real_consumers': ['Master Strategy', 'Listing Creative', 'Product Image', 'Product Video', 'Advertising Optimization'],
            'business_outputs': ['SKU Roles', 'Price Bands', 'Price Valleys', 'Price/Configuration Matrix', 'Unit Economics', 'Contribution Margin', 'Break-even CPA/CPC/ROAS', 'Offer/Bundle/Discount Boundary', 'Pricing Decision + WHY'],
            'human_delivery': 'Commercial Brain / Product Strategy & Pricing',
            'evidence': {'pricing_status': pricing.get('status'), 'strict_scenario_count': len(strict_ready), 'pricing_decision_status': (pricing.get('pricing_decision') or {}).get('status'), 'missing_inputs': pricing.get('missing_inputs') or []},
        },
        {
            'id': '03_LISTING_CREATIVE',
            'name': 'Listing Creative',
            'first_class': True,
            'project_status': _status(listing),
            'runtime_entry': 'tools.listing.compile_listing',
            'real_consumers': ['PDP/listing fields', 'Search architecture', 'Objection-to-asset handoff'],
            'business_outputs': ['field decision map', 'keyword architecture', 'claim/fact trace', 'localized copy workflow', 'pricing/offer context'],
            'human_delivery': 'Listing workspace + Commercial Brain handoff',
            'evidence': {'listing_status': _status(listing), 'pricing_offer_context_status': listing_context.get('status'), 'pricing_decision_status': (listing_context.get('pricing_decision') or {}).get('status')},
        },
        {
            'id': '04_PRODUCT_IMAGE',
            'name': 'Product Image',
            'first_class': True,
            'project_status': 'ACTIVE' if images else ('ACTIVE_ASSET_UNIVERSE' if assets else 'NOT_REQUESTED_OR_NOT_MATERIALIZED'),
            'runtime_entry': 'asset architecture + creative council + prompt compiler + production parameter closure',
            'real_consumers': ['Provider production', 'Gallery/PDP/A+/Ads/Store/Social surfaces', 'Review learning loop'],
            'business_outputs': ['Portfolio Visual Program', 'per-asset Art Direction', 'Product Presence', 'Model Prompt CN/EN', 'Visible Copy Block', 'Production/Assembly Notes'],
            'human_delivery': 'Asset object workspace',
            'evidence': {'asset_count': len(assets), 'image_count': len(images), 'fixed_gallery_quota': False},
        },
        {
            'id': '05_PRODUCT_VIDEO',
            'name': 'Product Video',
            'first_class': True,
            'project_status': 'ACTIVE' if videos else 'AVAILABLE_NOT_REQUESTED',
            'runtime_entry': 'video_creator.build_video_creator_plan',
            'real_consumers': ['Video production', 'Creator/Social/PDP video', 'Paid creative'],
            'business_outputs': ['script', 'shot plan', 'reference/fidelity policy', 'voice/subtitle', 'cover/first frame', 'landing/attribution handoff'],
            'human_delivery': 'Video plan / asset workspace',
            'evidence': {'video_asset_count': len(videos)},
        },
        {
            'id': '06_ADVERTISING_OPTIMIZATION',
            'name': 'Advertising Optimization',
            'first_class': True,
            'project_status': _status(ads, 'AVAILABLE_NOT_SUPPLIED') if (ads or paid_campaigns.get('campaigns')) else 'AVAILABLE_NOT_SUPPLIED',
            'runtime_entry': 'tools.ads.analyze_ads / analyze_ad_portfolio',
            'real_consumers': ['Paid Campaign Architecture', 'Strategy diagnostics', 'Listing/Image/Offer local revision routing'],
            'business_outputs': ['traffic→click→PDP→economics diagnosis', 'break-even ROAS', 'break-even CPA', 'break-even CPC when CVR supplied', 'budget/bid hypotheses', 'incrementality boundary'],
            'human_delivery': 'Commercial Brain / Ads Economics',
            'evidence': {'ads_status': _status(ads), 'economic_floor_count': len(ads_floors), 'campaign_count': len(paid_campaigns.get('campaigns') or [])},
        },
        {
            'id': '07_REVIEW_ANALYSIS',
            'name': 'Review Analysis',
            'first_class': True,
            'project_status': _status(feedback, 'AVAILABLE_NOT_SUPPLIED'),
            'runtime_entry': 'tools.feedback.analyze_feedback + seven_agent.review_analysis_tool',
            'real_consumers': ['Listing correction', 'Product Image correction', 'Product Strategy learning loop'],
            'business_outputs': ['issue attribution', 'misunderstanding detection', 'communication-fixable routing', 'positive selling-point learning'],
            'human_delivery': 'Commercial Brain / Review Learning',
            'evidence': {'feedback_status': _status(feedback), 'issue_count': len(feedback.get('issues') or feedback.get('rows') or []) if isinstance(feedback, dict) else 0},
        },
    ]
    ordered_ids = [x['id'] for x in capabilities]
    continuity_pass = ordered_ids == TOOL_ORDER and all(x.get('first_class') for x in capabilities)
    return {
        'version': VERSION,
        'status': 'SEVEN_TOOL_CONTINUITY_COMPILED' if continuity_pass else 'SEVEN_TOOL_CONTINUITY_INVALID',
        'execution_model': 'Seven first-class commerce capabilities share project truth and strategy state; relevance controls project activation, not capability existence.',
        'tool_order': TOOL_ORDER,
        'capabilities': capabilities,
        'all_seven_first_class': continuity_pass,
        'pricing_economics_integrity': {
            'status': pricing.get('status') or 'NOT_SUPPLIED',
            'strict_calculated_scenarios': len(strict_ready),
            'missing_inputs': pricing.get('missing_inputs') or [],
            'listing_consumer': listing_context,
            'ads_consumer': (pricing.get('downstream_consumers') or {}).get('advertising_optimization') or {},
            'rule': 'No cost, fee, CVR, margin or price is invented. Explicit zero is valid; absent remains unresolved.',
        },
        'continuity_acceptance': {
            'required_chain': ['Runtime entry', 'real consumer', 'business output', 'human delivery', 'plugin top-level activation'],
            'pass': continuity_pass,
            'note': 'File presence alone never counts as preserved capability.',
        },
    }
