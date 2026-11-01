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
    from .strategy_framework_authority import (
        wrap_build_master_strategy as wrap_strategy_framework_strategy,
        wrap_validate_strategy_delivery as wrap_strategy_framework_validator,
    )
    from .economics_offer_authority import (
        wrap_compile_pricing_economics_authority,
        wrap_build_master_strategy as wrap_economics_offer_strategy,
        wrap_validate_strategy_delivery as wrap_economics_offer_validator,
    )
    from .economics_offer_seven_tool_bridge import wrap_compile_seven_tool_continuity

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

    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_economics_offer_authority', False):
        strategy_authority.build_master_strategy = wrap_economics_offer_strategy(strategy_authority.build_master_strategy)
    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0676_economics_offer_authority', False):
        delivery_contract.validate_strategy_delivery = wrap_economics_offer_validator(delivery_contract.validate_strategy_delivery)

    # Seven-tool continuity remains mature; only its Economics evidence status is enriched so calculation
    # readiness cannot masquerade as Pricing/Offer business readiness.
    if not getattr(seven_tool_module.compile_seven_tool_continuity, '_cbcc_v0676_economics_offer_authority', False):
        seven_tool_module.compile_seven_tool_continuity = wrap_compile_seven_tool_continuity(
            seven_tool_module.compile_seven_tool_continuity
        )
        installed.append('SEVEN_TOOL_ECONOMICS_BUSINESS_READINESS_BRIDGE')

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
        'SEVEN_TOOL_ECONOMICS_BUSINESS_READINESS_BRIDGE',
    ]
    return {
        'status':'INSTALLED' if installed else 'ALREADY_INSTALLED',
        'version':VERSION,
        'installed_now':installed,
        'closures':closures,
    }
