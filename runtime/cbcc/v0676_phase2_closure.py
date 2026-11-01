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

    installed: list[str] = []

    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_information_audit_authority', False):
        strategy_authority.build_master_strategy = wrap_information_audit_strategy(strategy_authority.build_master_strategy)
        installed.append('INFORMATION_AUDIT_AUTHORITY')
    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0676_information_audit_authority', False):
        delivery_contract.validate_strategy_delivery = wrap_information_audit_validator(delivery_contract.validate_strategy_delivery)

    # Context WHY must wrap the final mature strategy chain plus the Information Audit layer. It does not
    # invent platform/region/audience/culture causality: incomplete or inherited project context remains
    # TO_VERIFY and the validator blocks a false FULL-depth pass.
    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_context_why_authority', False):
        strategy_authority.build_master_strategy = wrap_context_why_strategy(strategy_authority.build_master_strategy)
        installed.append('DECISION_SPECIFIC_CONTEXT_WHY_AUTHORITY')
    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0676_context_why_authority', False):
        delivery_contract.validate_strategy_delivery = wrap_context_why_validator(delivery_contract.validate_strategy_delivery)

    # Preserve the mature v0.6.69/v0.6.71 intersectionality and culture objects, then enforce business
    # density and evidence boundaries on those same objects. Missing identity/cultural facts remain
    # TO_VERIFY; Runtime never manufactures demographic causality or tokenistic cultural conclusions.
    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_intersectionality_culture_authority', False):
        strategy_authority.build_master_strategy = wrap_intersectionality_culture_strategy(strategy_authority.build_master_strategy)
        installed.append('INTERSECTIONALITY_CULTURE_DENSITY_AUTHORITY')
    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0676_intersectionality_culture_authority', False):
        delivery_contract.validate_strategy_delivery = wrap_intersectionality_culture_validator(delivery_contract.validate_strategy_delivery)

    # delivery_export imported this symbol before the final closure. Refresh only that cached consumer;
    # strategy_authority.materialize_strategy imports validate_strategy_delivery dynamically.
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
    ]
    return {
        'status':'INSTALLED' if installed else 'ALREADY_INSTALLED',
        'version':VERSION,
        'installed_now':installed,
        'closures':closures,
    }
