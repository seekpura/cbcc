from __future__ import annotations

"""v0.6.76 Phase 2 business-object density closure.

Installed after the mature bootstrap and v0.6.74 cross-scope closure. This module is additive and
installs each verified Phase 2 authority independently so later subtask additions cannot be skipped
merely because an earlier v0.6.76 wrapper is already present.
"""

from typing import Any

VERSION = '0.6.76-phase2-business-density'


def apply_v0676_phase2_patches() -> dict[str, Any]:
    from . import strategy_authority
    from . import delivery_contract
    from . import delivery_export
    from . import pricing_economics_authority as pricing_economics_module
    from . import seven_tool_continuity as seven_tool_module
    from .tools import listing as listing_module
    from .tools import ads as ads_module
    from .tools import feedback as feedback_module
    from .information_audit_authority import (
        wrap_build_master_strategy as wrap_information_audit_strategy,
        wrap_validate_strategy_delivery as wrap_information_audit_validator,
    )
    from .context_why_authority import (
        wrap_build_master_strategy as wrap_context_why_strategy,
        wrap_validate_strategy_delivery as wrap_context_why_validator,
    )
    from .intersectionality_culture_authority import (
        wrap_build_master_strategy as wrap_intersectionality_culture_strategy,
        wrap_validate_strategy_delivery as wrap_intersectionality_culture_validator,
    )
    from .content_matrix_race_authority import (
        wrap_build_master_strategy as wrap_content_matrix_race_strategy,
        wrap_validate_strategy_delivery as wrap_content_matrix_race_validator,
    )
    from .strategy_framework_authority import (
        wrap_build_master_strategy as wrap_strategy_framework_strategy,
        wrap_validate_strategy_delivery as wrap_strategy_framework_validator,
    )
    from .economics_offer_authority import (
        wrap_compile_pricing_economics_authority,
        wrap_build_master_strategy as wrap_economics_offer_strategy,
        wrap_validate_strategy_delivery as wrap_economics_offer_validator,
    )
    from .economics_offer_refinement_v0676 import (
        wrap_compile_pricing_economics_authority as wrap_economics_offer_refinement_compile,
        wrap_build_master_strategy as wrap_economics_offer_refinement_strategy,
        wrap_validate_strategy_delivery as wrap_economics_offer_refinement_validator,
    )
    from .economics_offer_seven_tool_bridge import wrap_compile_seven_tool_continuity
    from .listing_search_authority import (
        wrap_compile_pricing_economics_for_listing_context,
        wrap_compile_listing,
        wrap_compile_seven_tool_continuity as wrap_listing_search_seven_tool_continuity,
    )
    from .ads_optimization_authority import (
        wrap_compile_pricing_economics_for_ads_context,
        wrap_analyze_ads,
        wrap_analyze_ad_portfolio,
        wrap_compile_seven_tool_continuity as wrap_ads_optimization_seven_tool_continuity,
    )
    from .review_analysis_authority import (
        wrap_compile_request_checkpoint_for_review_context,
        wrap_analyze_feedback,
        wrap_compile_seven_tool_continuity as wrap_review_analysis_seven_tool_continuity,
    )
    from .measurement_authority import (
        wrap_build_master_strategy as wrap_measurement_strategy,
        wrap_validate_strategy_delivery as wrap_measurement_validator,
    )

    installed: list[str] = []

    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_information_audit_authority', False):
        strategy_authority.build_master_strategy = wrap_information_audit_strategy(strategy_authority.build_master_strategy)
        installed.append('INFORMATION_AUDIT_AUTHORITY')
    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0676_information_audit_authority', False):
        delivery_contract.validate_strategy_delivery = wrap_information_audit_validator(delivery_contract.validate_strategy_delivery)

    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_context_why_authority', False):
        strategy_authority.build_master_strategy = wrap_context_why_strategy(strategy_authority.build_master_strategy)
        installed.append('DECISION_SPECIFIC_CONTEXT_WHY_AUTHORITY')
    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0676_context_why_authority', False):
        delivery_contract.validate_strategy_delivery = wrap_context_why_validator(delivery_contract.validate_strategy_delivery)

    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_intersectionality_culture_authority', False):
        strategy_authority.build_master_strategy = wrap_intersectionality_culture_strategy(strategy_authority.build_master_strategy)
        installed.append('INTERSECTIONALITY_CULTURE_DENSITY_AUTHORITY')
    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0676_intersectionality_culture_authority', False):
        delivery_contract.validate_strategy_delivery = wrap_intersectionality_culture_validator(delivery_contract.validate_strategy_delivery)

    # Phase 2 Content Matrix/RACE must exist before asset/prompt work. Install this before the
    # Strategy/Framework wrapper so section 07 is finalized before the existing applied-RACE authority
    # snapshots it. The same order is preserved on delivery validation.
    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_content_matrix_race_authority', False):
        strategy_authority.build_master_strategy = wrap_content_matrix_race_strategy(strategy_authority.build_master_strategy)
        installed.append('CONTENT_MATRIX_RACE_BUSINESS_AUTHORITY')
    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0676_content_matrix_race_authority', False):
        delivery_contract.validate_strategy_delivery = wrap_content_matrix_race_validator(delivery_contract.validate_strategy_delivery)

    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_strategy_framework_authority', False):
        strategy_authority.build_master_strategy = wrap_strategy_framework_strategy(strategy_authority.build_master_strategy)
        installed.append('APPLIED_STRATEGY_FRAMEWORK_AUTHORITY')
    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0676_strategy_framework_authority', False):
        delivery_contract.validate_strategy_delivery = wrap_strategy_framework_validator(delivery_contract.validate_strategy_delivery)

    # The established pricing_economics_authority remains the only deterministic calculator. Phase 2
    # wraps that same object with missing-input integrity + Agent-authored Pricing/Offer decision density.
    # This is installed before compiler import, so compiler.py captures the final wrapped symbol.
    if not getattr(pricing_economics_module.compile_pricing_economics_authority, '_cbcc_v0676_economics_offer_authority', False):
        pricing_economics_module.compile_pricing_economics_authority = wrap_compile_pricing_economics_authority(
            pricing_economics_module.compile_pricing_economics_authority
        )
        installed.append('ECONOMICS_OFFER_BUSINESS_AUTHORITY')

    # Refinement is deliberately a second additive layer: it adds REQ-088 lineage and distinguishes a
    # zero-contribution mathematical floor from a real operating break-even boundary. It never recalculates
    # price, cost, contribution, CPA, CPC or ROAS.
    if not getattr(pricing_economics_module.compile_pricing_economics_authority, '_cbcc_v0676_economics_offer_refinement', False):
        pricing_economics_module.compile_pricing_economics_authority = wrap_economics_offer_refinement_compile(
            pricing_economics_module.compile_pricing_economics_authority
        )
        installed.append('ECONOMICS_OFFER_LINEAGE_AND_BREAK_EVEN_REFINEMENT')

    # The mature compiler calls Pricing/Economics before Listing. Preserve that path and carry the final
    # verified #7 object through a request-local ContextVar rather than changing compiler.py or creating a
    # second Listing engine. The Listing wrapper consumes and clears this context on its next call.
    if not getattr(pricing_economics_module.compile_pricing_economics_authority, '_cbcc_v0676_listing_search_context_bridge', False):
        pricing_economics_module.compile_pricing_economics_authority = wrap_compile_pricing_economics_for_listing_context(
            pricing_economics_module.compile_pricing_economics_authority
        )
        installed.append('LISTING_SEARCH_PRICING_CONTEXT_BRIDGE')

    # Ads analysis is also downstream of the final #7 Economics object. Seed a separate request-local
    # one-use context only when the compiler will actually analyze ad_rows/ad_analysis. This avoids both
    # stale cross-project state and any compiler.py fork while keeping Ads arithmetic in tools.ads.
    if not getattr(pricing_economics_module.compile_pricing_economics_authority, '_cbcc_v0676_ads_optimization_context_bridge', False):
        pricing_economics_module.compile_pricing_economics_authority = wrap_compile_pricing_economics_for_ads_context(
            pricing_economics_module.compile_pricing_economics_authority
        )
        installed.append('ADS_OPTIMIZATION_ECONOMICS_CONTEXT_BRIDGE')

    # Review Analysis does not depend semantically on Economics. We reuse this already-early compiler
    # request checkpoint only to carry the FULL request to the later feedback branch without forking
    # compiler.py. The Review wrapper consumes and clears the context exactly once.
    if not getattr(pricing_economics_module.compile_pricing_economics_authority, '_cbcc_v0676_review_analysis_context_bridge', False):
        pricing_economics_module.compile_pricing_economics_authority = wrap_compile_request_checkpoint_for_review_context(
            pricing_economics_module.compile_pricing_economics_authority
        )
        installed.append('REVIEW_ANALYSIS_REQUEST_CONTEXT_BRIDGE')

    # Listing 2.0 remains the mature field/search/localization compiler. Phase 2 wraps that same compiler;
    # it does not introduce a second copy generator. The wrapper adds first-class publishability, decision
    # density, source lineage and explicit Pricing/Offer handoff in FULL project scope.
    if not getattr(listing_module.compile_listing, '_cbcc_v0676_listing_search_authority', False):
        listing_module.compile_listing = wrap_compile_listing(listing_module.compile_listing)
        installed.append('LISTING_SEARCH_BUSINESS_AUTHORITY')

    # Preserve tools.ads as the only deterministic metrics/diagnosis calculator. Phase 2 enriches its real
    # result with authored optimization decisions and final Economics/Offer boundaries. Portfolio analysis
    # suppresses enrichment for its internal analyze_ads calls and consumes the context once at portfolio end.
    if not getattr(ads_module.analyze_ads, '_cbcc_v0676_ads_optimization_authority', False):
        ads_module.analyze_ads = wrap_analyze_ads(ads_module.analyze_ads)
        installed.append('ADS_OPTIMIZATION_BUSINESS_AUTHORITY')
    if not getattr(ads_module.analyze_ad_portfolio, '_cbcc_v0676_ads_optimization_authority', False):
        ads_module.analyze_ad_portfolio = wrap_analyze_ad_portfolio(ads_module.analyze_ad_portfolio)
        installed.append('ADS_OPTIMIZATION_PORTFOLIO_BUSINESS_AUTHORITY')

    # Preserve tools.feedback.analyze_feedback as the deterministic aggregation/prioritization engine.
    # Phase 2 adds Agent-authored root-cause and smallest-repair decisions around that real output.
    if not getattr(feedback_module.analyze_feedback, '_cbcc_v0676_review_analysis_authority', False):
        feedback_module.analyze_feedback = wrap_analyze_feedback(feedback_module.analyze_feedback)
        installed.append('REVIEW_ANALYSIS_ROOT_CAUSE_REPAIR_AUTHORITY')

    # Phase 2 Measurement is the final business-object density layer. It consumes explicit
    # Measurement/A-B/P0-P1-P2/next-input decisions and mature experiment output without creating a
    # second statistics engine or an eighth Seven-tool capability.
    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_measurement_authority', False):
        strategy_authority.build_master_strategy = wrap_measurement_strategy(strategy_authority.build_master_strategy)
        installed.append('MEASUREMENT_BUSINESS_AUTHORITY')
    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0676_measurement_authority', False):
        delivery_contract.validate_strategy_delivery = wrap_measurement_validator(delivery_contract.validate_strategy_delivery)

    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_economics_offer_authority', False):
        strategy_authority.build_master_strategy = wrap_economics_offer_strategy(strategy_authority.build_master_strategy)
    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_economics_offer_refinement', False):
        strategy_authority.build_master_strategy = wrap_economics_offer_refinement_strategy(strategy_authority.build_master_strategy)

    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0676_economics_offer_authority', False):
        delivery_contract.validate_strategy_delivery = wrap_economics_offer_validator(delivery_contract.validate_strategy_delivery)
    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0676_economics_offer_refinement', False):
        delivery_contract.validate_strategy_delivery = wrap_economics_offer_refinement_validator(delivery_contract.validate_strategy_delivery)

    # Seven-tool continuity remains mature. Each commercial authority adds business readiness separately
    # from legacy calculator/compiler status so a metric calculation can never masquerade as business closure.
    if not getattr(seven_tool_module.compile_seven_tool_continuity, '_cbcc_v0676_economics_offer_authority', False):
        seven_tool_module.compile_seven_tool_continuity = wrap_compile_seven_tool_continuity(
            seven_tool_module.compile_seven_tool_continuity
        )
        installed.append('SEVEN_TOOL_ECONOMICS_BUSINESS_READINESS_BRIDGE')
    if not getattr(seven_tool_module.compile_seven_tool_continuity, '_cbcc_v0676_listing_search_authority', False):
        seven_tool_module.compile_seven_tool_continuity = wrap_listing_search_seven_tool_continuity(
            seven_tool_module.compile_seven_tool_continuity
        )
        installed.append('SEVEN_TOOL_LISTING_BUSINESS_READINESS_BRIDGE')
    if not getattr(seven_tool_module.compile_seven_tool_continuity, '_cbcc_v0676_ads_optimization_authority', False):
        seven_tool_module.compile_seven_tool_continuity = wrap_ads_optimization_seven_tool_continuity(
            seven_tool_module.compile_seven_tool_continuity
        )
        installed.append('SEVEN_TOOL_ADS_BUSINESS_READINESS_BRIDGE')
    if not getattr(seven_tool_module.compile_seven_tool_continuity, '_cbcc_v0676_review_analysis_authority', False):
        seven_tool_module.compile_seven_tool_continuity = wrap_review_analysis_seven_tool_continuity(
            seven_tool_module.compile_seven_tool_continuity
        )
        installed.append('SEVEN_TOOL_REVIEW_BUSINESS_READINESS_BRIDGE')

    delivery_export.validate_strategy_delivery = delivery_contract.validate_strategy_delivery

    closures = [
        'INFORMATION_AUDIT_AUTHORITY',
        'QUESTION_LIMIT_WITH_FULL_UNRESOLVED_PRESERVATION',
        'FACT_ASSUMPTION_DECISION_LINEAGE',
        'FULL_INFORMATION_AUDIT_DENSITY_AUDIT',
        'DECISION_SPECIFIC_CONTEXT_WHY_AUTHORITY',
        'PLATFORM_REGION_AUDIENCE_CULTURE_SIX_FIELD_DENSITY_AUDIT',
        'PROJECT_CONTEXT_CANNOT_FALSE_PASS_AS_CAUSAL_WHY',
        'INTERSECTIONALITY_CULTURE_DENSITY_AUTHORITY',
        'CORE_INTERSECTION_DIMENSION_COVERAGE_WITHOUT_BEHAVIOR_INFERENCE',
        'CULTURE_SCRIPT_CASTING_WARDROBE_COLOR_CTA_EXECUTION_AUDIT',
        'RELEVANCE_AWARE_CULTURAL_CONTEXT_COVERAGE',
        'CONTENT_MATRIX_RACE_BUSINESS_AUTHORITY',
        'CONTENT_MATRIX_PLATFORM_EXECUTION_AND_ATTRIBUTION',
        'CONTENT_MATRIX_SIX_FIELD_DECISION_DENSITY',
        'CONTENT_MATRIX_REQ088_LINEAGE',
        'CONTENT_MATRIX_VALID_RACE_LINKAGE',
        'RACE_PLATFORM_CULTURE_ATTRIBUTION_NEXT_DECISION',
        'RACE_REQ088_LINEAGE',
        'CONTENT_MATRIX_ASSET_INDEPENDENT_PHASE2_AUTHORITY',
        'APPLIED_STRATEGY_FRAMEWORK_AUTHORITY',
        'FRAMEWORK_DEFINITION_CANNOT_FALSE_PASS_AS_APPLICATION',
        'POSITIONING_VALUE_MESSAGE_SIX_FIELD_DENSITY_AUDIT',
        'RACE_APPLIED_DECISION_DENSITY_AUDIT',
        'ECONOMICS_OFFER_BUSINESS_AUTHORITY',
        'PAYMENT_FEE_AND_REQUIRED_INPUT_INTEGRITY',
        'PRICING_AND_OFFER_SIX_FIELD_DECISION_DENSITY',
        'BREAK_EVEN_INPUT_CONDITIONALITY',
        'MARKET_PRICE_EVIDENCE_NOT_PRICE_RECOMMENDATION',
        'LEGACY_SENSITIVITY_NOT_OFFER_AUTHORITY',
        'ECONOMICS_REQ088_LINEAGE_REFINEMENT',
        'ZERO_CONTRIBUTION_BREAK_EVEN_BASELINE_NOT_OPERATING_BOUNDARY',
        'SEVEN_TOOL_ECONOMICS_BUSINESS_READINESS_BRIDGE',
        'LISTING_SEARCH_PRICING_CONTEXT_BRIDGE',
        'LISTING_SEARCH_BUSINESS_AUTHORITY',
        'LISTING_SEARCH_NINE_OBJECT_DECISION_DENSITY',
        'LISTING_SEARCH_REQ088_LINEAGE',
        'SEARCH_EVIDENCE_SOURCE_BINDING',
        'EXPLICIT_PRICING_OFFER_TO_LISTING_HANDOFF',
        'TARGET_ENGLISH_DELIVERY_COMPANION_LISTING_CONTINUITY',
        'SEVEN_TOOL_LISTING_BUSINESS_READINESS_BRIDGE',
        'ADS_OPTIMIZATION_ECONOMICS_CONTEXT_BRIDGE',
        'ADS_OPTIMIZATION_BUSINESS_AUTHORITY',
        'ADS_OPTIMIZATION_OBJECTIVE_AUDIENCE_CREATIVE_OFFER_LANDING_CONTRACT',
        'ADS_OPTIMIZATION_ATTRIBUTION_TEST_REPAIR_LEARNING_CONTRACT',
        'ADS_OPTIMIZATION_SIX_FIELD_DECISION_DENSITY',
        'ADS_OPTIMIZATION_REQ088_LINEAGE',
        'ADS_OPTIMIZATION_INCREMENTALITY_BOUNDARY',
        'ADS_OPTIMIZATION_ASSET_INDEPENDENT_PHASE2_AUTHORITY',
        'SEVEN_TOOL_ADS_BUSINESS_READINESS_BRIDGE',
        'REVIEW_ANALYSIS_REQUEST_CONTEXT_BRIDGE',
        'REVIEW_ANALYSIS_ROOT_CAUSE_REPAIR_AUTHORITY',
        'REVIEW_ANALYSIS_SMALLEST_RESPONSIBLE_LAYER_REPAIR',
        'REVIEW_ANALYSIS_SIX_FIELD_DECISION_DENSITY',
        'REVIEW_ANALYSIS_REQ088_LINEAGE',
        'REVIEW_ANALYSIS_LOCAL_VERIFY_GLOBAL_MEASUREMENT_BOUNDARY',
        'REVIEW_ANALYSIS_ASSET_AND_PRODUCTION_REVIEW_INDEPENDENCE',
        'SEVEN_TOOL_REVIEW_BUSINESS_READINESS_BRIDGE',
        'MEASUREMENT_BUSINESS_AUTHORITY',
        'MEASUREMENT_AB_TEST_VARIABLE_ISOLATION',
        'MEASUREMENT_P0_P1_P2_PRIORITY_AUTHORITY',
        'MEASUREMENT_NEXT_INPUT_PLAN_AUTHORITY',
        'MEASUREMENT_REQ088_LINEAGE',
        'MEASUREMENT_EXPERIMENT_CALCULATOR_SEPARATION',
        'MEASUREMENT_PHASE2_COMPLETION_WITH_POST_PRODUCTION_LEARNING_DEFERRED',
    ]
    return {
        'status':'INSTALLED' if installed else 'ALREADY_INSTALLED',
        'version':VERSION,
        'installed_now':installed,
        'closures':closures,
    }
