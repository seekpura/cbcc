from __future__ import annotations

"""v0.6.76 Phase 3 Opportunity-Family Evaluation closure.

This layer is deliberately additive.  It wraps the mature asset architecture only after the full
Phase 2 closure has been installed.  It does not replace asset taxonomy, visual mechanism search,
Art Direction, Prompt, Human Workspace shell, or production authorities.
"""

from . import asset_architecture
from .opportunity_family_authority import wrap_build_asset_architecture

_INSTALLED = False


def apply_v0676_phase3_patches() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    if not getattr(asset_architecture.build_asset_architecture, '_cbcc_v0676_phase3_opportunity_family', False):
        asset_architecture.build_asset_architecture = wrap_build_asset_architecture(
            asset_architecture.build_asset_architecture
        )
