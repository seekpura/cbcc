from __future__ import annotations

"""v0.6.76 Phase 2 business-object density closure.

Installed after the mature bootstrap and v0.6.74 cross-scope closure.  This module is additive: it
normalizes the already-authored FULL Information Audit into a first-class authority and adds a strict
delivery audit without changing Product Truth, Research, culture, visual, listing or prompt logic.
"""

from typing import Any

VERSION = '0.6.76-phase2-information-audit'


def apply_v0676_phase2_patches() -> dict[str, Any]:
    from . import strategy_authority
    from . import delivery_contract
    from . import delivery_export
    from .information_audit_authority import (
        wrap_build_master_strategy,
        wrap_validate_strategy_delivery,
    )

    if getattr(strategy_authority.build_master_strategy, '_cbcc_v0676_information_audit_authority', False):
        return {'status':'ALREADY_INSTALLED','version':VERSION}

    strategy_authority.build_master_strategy = wrap_build_master_strategy(strategy_authority.build_master_strategy)
    delivery_contract.validate_strategy_delivery = wrap_validate_strategy_delivery(delivery_contract.validate_strategy_delivery)

    # delivery_export imported this symbol before the final closure. Refresh only that cached consumer;
    # strategy_authority.materialize_strategy imports validate_strategy_delivery dynamically.
    delivery_export.validate_strategy_delivery = delivery_contract.validate_strategy_delivery

    return {
        'status':'INSTALLED',
        'version':VERSION,
        'closures':['INFORMATION_AUDIT_AUTHORITY','QUESTION_LIMIT_WITH_FULL_UNRESOLVED_PRESERVATION','FACT_ASSUMPTION_DECISION_LINEAGE','FULL_INFORMATION_AUDIT_DENSITY_AUDIT'],
    }
