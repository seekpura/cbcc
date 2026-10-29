from __future__ import annotations


def install() -> None:
    """Install final v0.6.46 compatibility/strictness patches after the normal authority stack.

    Kept in one bootstrap so future versions have one explicit place to verify that mature pricing field
    names, prompt status and human asset cards remain connected.
    """
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
    asset_compiler._human_asset_design_card_markdown = human_asset_commercial_projection.wrap_human_asset_design_card(
        asset_compiler._human_asset_design_card_markdown
    )
