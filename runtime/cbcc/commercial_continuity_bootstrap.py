from __future__ import annotations

_INSTALLED = False


def install() -> None:
    """Install additive commercial continuity + FULL depth patches exactly once."""
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

    rich_compile = compatibility.wrap_compile_commerce_decision_context(context_module.compile_commerce_decision_context)
    context_module.compile_commerce_decision_context = rich_compile
    continuity_authority.compile_commerce_decision_context = rich_compile
    delivery_continuity.compile_commerce_decision_context = rich_compile

    from . import strategy_authority
    from .strategy_depth_projection_v3 import wrap_build_master_strategy
    from .long_requirement_runtime import wrap_build_master_strategy as wrap_long_requirements
    from .long_requirement_human_projection import wrap_render_master_strategy_cn
    from .claim_grade_safety_v0647 import wrap_build_master_strategy as wrap_claim_grade_safety
    if not getattr(strategy_authority.build_master_strategy, '_cbcc_v0662_long_requirement_runtime', False):
        wrapped_strategy = wrap_claim_grade_safety(
            wrap_long_requirements(
                wrap_build_master_strategy(strategy_authority.build_master_strategy)
            )
        )
        setattr(wrapped_strategy, '_cbcc_v0647_full_depth_projection', True)
        setattr(wrapped_strategy, '_cbcc_v0662_long_requirement_runtime', True)
        strategy_authority.build_master_strategy = wrapped_strategy
    if not getattr(strategy_authority.render_master_strategy_cn, '_cbcc_v0662_long_requirement_human_projection', False):
        wrapped_renderer = wrap_render_master_strategy_cn(strategy_authority.render_master_strategy_cn)
        setattr(wrapped_renderer, '_cbcc_v0662_long_requirement_human_projection', True)
        strategy_authority.render_master_strategy_cn = wrapped_renderer

    from . import delivery_contract
    from . import full_delivery_depth_v3 as full_depth
    from .long_requirement_full_audit import wrap_audit_full_strategy_depth_v3, wrap_audit_host_full_package

    if not getattr(full_depth.audit_full_strategy_depth_v3, '_cbcc_v0662_long_requirement_audit', False):
        wrapped_depth_audit = wrap_audit_full_strategy_depth_v3(full_depth.audit_full_strategy_depth_v3)
        setattr(wrapped_depth_audit, '_cbcc_v0662_long_requirement_audit', True)
        full_depth.audit_full_strategy_depth_v3 = wrapped_depth_audit

    if not getattr(delivery_contract.validate_strategy_delivery, '_cbcc_v0647_full_depth_v3', False):
        previous_validate = delivery_contract.validate_strategy_delivery
        def strict_validate_strategy_delivery(strategy):
            base = previous_validate(strategy)
            if str(base.get('mode') or '').upper() != 'FULL':
                return base
            upgraded = full_depth.audit_full_strategy_depth_v3(strategy, base)
            for key in ('required_sections', 'evidence_levels', 'race_stages'):
                if key in base and key not in upgraded:
                    upgraded[key] = base[key]
            return upgraded
        setattr(strict_validate_strategy_delivery, '_cbcc_v0647_full_depth_v3', True)
        delivery_contract.validate_strategy_delivery = strict_validate_strategy_delivery

    if not getattr(full_depth.audit_host_full_package, '_cbcc_v0662_long_requirement_package_audit', False):
        wrapped_package_audit = wrap_audit_host_full_package(full_depth.audit_host_full_package)
        setattr(wrapped_package_audit, '_cbcc_v0662_long_requirement_package_audit', True)
        full_depth.audit_host_full_package = wrapped_package_audit

    from .full_delivery_package_hardening import harden_full_package_audit
    if not getattr(full_depth.audit_host_full_package, '_cbcc_v0647_content_hardened', False):
        hardened_package_audit = harden_full_package_audit(
            full_depth.audit_host_full_package,
            delivery_contract.validate_strategy_delivery,
        )
        setattr(hardened_package_audit, '_cbcc_v0647_content_hardened', True)
        setattr(hardened_package_audit, '_cbcc_v0662_long_requirement_package_audit', True)
        full_depth.audit_host_full_package = hardened_package_audit
    for rel in ('DELIVERY_MANIFEST.json', 'FULL_MATERIALIZATION_AUDIT.json'):
        if rel not in full_depth.CORE_HOST_FULL_FILES:
            full_depth.CORE_HOST_FULL_FILES.append(rel)

    def materialized_asset_ids(package_dir):
        from pathlib import Path
        package = Path(package_dir)
        ids = set()
        for root_name in ('asset_packages', 'video'):
            root = package / root_name
            if root.exists():
                ids.update(p.name for p in root.iterdir() if p.is_dir())
        return ids
    full_depth._asset_ids_from_package = materialized_asset_ids

    # Final public prompt boundary. The Agent-authored structured Art Direction remains authority.
    # 1) normalize it before the historical chain;
    # 2) restore the current per-asset integrated render route so legacy deterministic-copy behavior
    #    cannot silently turn the image model into a background generator;
    # 3) apply the semantic membrane last so source/QA/revision prose stays out without deleting
    #    people/scene/composition/camera/light/CMF/material/copy decisions.
    from .full_art_direction_preservation import normalize_full_art_direction
    from .integrated_render_route_authority import finalize_integrated_render_route
    from .model_prompt_semantic_membrane import finalize_model_prompt_bundle

    existing_prompt_compile = prompt_compiler.compile_asset_prompt
    def strict_prompt_compile(*args, **kwargs):
        if args:
            call_args = list(args)
            normalized_asset = normalize_full_art_direction(call_args[0] or {})
            call_args[0] = normalized_asset
            out = existing_prompt_compile(*call_args, **kwargs)
        else:
            call_kwargs = dict(kwargs)
            normalized_asset = normalize_full_art_direction(call_kwargs.get('asset') or {}) if 'asset' in call_kwargs else {}
            if 'asset' in call_kwargs:
                call_kwargs['asset'] = normalized_asset
            out = existing_prompt_compile(**call_kwargs)

        out = finalize_integrated_render_route(normalized_asset, out)
        out = finalize_model_prompt_bundle(out)

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

    from . import asset_compiler
    asset_compiler.compile_asset_prompt = strict_prompt_compile
    from . import human_asset_commercial_projection
    if not getattr(asset_compiler._human_asset_design_card_markdown, '_cbcc_v0646_commercial_projection', False):
        wrapped = human_asset_commercial_projection.wrap_human_asset_design_card(asset_compiler._human_asset_design_card_markdown)
        setattr(wrapped, '_cbcc_v0646_commercial_projection', True)
        asset_compiler._human_asset_design_card_markdown = wrapped
