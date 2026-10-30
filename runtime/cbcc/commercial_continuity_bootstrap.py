from __future__ import annotations

_INSTALLED = False


def install() -> None:
    """Install additive commercial continuity + FULL depth patches exactly once.

    v0.6.47 keeps the v0.6.46 decision-lineage / prompt stack and adds one more invariant:
    FULL Host-native and Runtime deliveries must satisfy the same content-depth and materialization contract.
    """
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from . import commerce_decision_context as context_module
    from . import commercial_context_compatibility as compatibility
    from . import commercial_continuity_authority as continuity_authority
    from . import commercial_delivery_continuity as delivery_continuity
    from . import prompt_compiler as prompt_compiler
    from .tools import seven_agent

    rich_compile = compatibility.wrap_compile_commerce_decision_context(
        context_module.compile_commerce_decision_context
    )
    context_module.compile_commerce_decision_context = rich_compile
    continuity_authority.compile_commerce_decision_context = rich_compile
    delivery_continuity.compile_commerce_decision_context = rich_compile

    # FULL strategy authoring must project multidimensional market/culture, framework relationships,
    # localization operations, resource tradeoffs and conditional inclusive-photography depth before audit.
    from . import strategy_authority
    from .strategy_depth_projection_v3 import wrap_build_master_strategy
    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0647_full_depth_projection', False):
        wrapped_strategy = wrap_build_master_strategy(strategy_authority.build_master_strategy)
        setattr(wrapped_strategy, '_cbcc_v0647_full_depth_projection', True)
        strategy_authority.build_master_strategy = wrapped_strategy

    # Replace existence-level FULL validation with content-depth V3 while keeping all established V2 issues.
    from . import delivery_contract
    from .full_delivery_depth_v3 import audit_full_strategy_depth_v3
    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0647_full_depth_v3', False):
        previous_validate = delivery_contract.validate_strategy_delivery

        def strict_validate_strategy_delivery(strategy):
            base = previous_validate(strategy)
            if str(base.get('mode') or '').upper() != 'FULL':
                return base
            upgraded = audit_full_strategy_depth_v3(strategy, base)
            # Preserve stable metadata expected by existing consumers.
            for key in ('required_sections', 'evidence_levels', 'race_stages'):
                if key in base and key not in upgraded:
                    upgraded[key] = base[key]
            return upgraded

        setattr(strict_validate_strategy_delivery, '_cbcc_v0647_full_depth_v3', True)
        delivery_contract.validate_strategy_delivery = strict_validate_strategy_delivery

    existing_prompt_compile = prompt_compiler.compile_asset_prompt

    def strict_prompt_compile(*args, **kwargs):
        out = existing_prompt_compile(*args, **kwargs)
        continuity = out.get('commerce_decision_consumption_audit') or (out.get('prompt_consumption_audit') or {}).get('commerce_decision_continuity') or {}
        if continuity and continuity.get('status') not in {'PASS', 'NOT_BOUND'}:
            out['model_prompt_status'] = 'MODEL_PROMPT_NEEDS_COMMERCIAL_DECISION_CONSUMPTION'
            out['status'] = 'MODEL_PROMPT_NEEDS_COMMERCIAL_DECISION_CONSUMPTION'
            card = out.setdefault('design_card', {})
            card['generation_blocking'] = True
            card['commercial_continuity_status'] = 'INCOMPLETE'
        return out

    prompt_compiler.compile_asset_prompt = strict_prompt_compile
    seven_agent.compile_asset_prompt = strict_prompt_compile

    # Import after the strict prompt compiler is installed so asset_compiler captures the final compiler.
    from . import asset_compiler
    asset_compiler.compile_asset_prompt = strict_prompt_compile
    from . import human_asset_commercial_projection
    if not getattr(asset_compiler._human_asset_design_card_markdown, '_cbcc_v0646_commercial_projection', False):
        wrapped = human_asset_commercial_projection.wrap_human_asset_design_card(
            asset_compiler._human_asset_design_card_markdown
        )
        setattr(wrapped, '_cbcc_v0646_commercial_projection', True)
        asset_compiler._human_asset_design_card_markdown = wrapped
