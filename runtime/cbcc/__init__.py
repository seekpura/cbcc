"""CBCC runtime package authority wiring.

v0.6.30+ keeps legacy module import surfaces for compatibility while installing narrow authority
bridges: the host Agent authors portfolio curation, product presence and per-asset Art Direction;
Python validates, serializes, compiles and executes those decisions. Missing creative decisions are
returned to the Agent instead of being filled with deterministic product/layout fallbacks.

Model-facing prompts are a distinct artifact from production/assembly contracts. Runtime may carry
copy-composition, editable-layer and provider instructions separately, but must not pollute the
image/video model prompt with those engineering contracts.

v0.6.33 makes reference-guided native generation the normal real-product path: supplied real product
images are strong model reference inputs and the product is rendered natively in the final image.
Exact immutable-pixel compositing is an explicit special route only.
"""

from . import prompt_compiler as _legacy_prompt_compiler
from . import agent_authority_prompt_compiler as _agent_authority_prompt_compiler
from . import model_native_prompt_contract as _model_native_prompt_contract
from . import model_native_prompt_audit_fix as _model_native_prompt_audit_fix
from . import production_parameter_closure as _production_parameter_closure
from . import reference_guided_native_authority as _reference_guided_native_authority
from . import human_delivery_art_direction_projection as _human_delivery_art_direction_projection
from . import photographic_route_agent_authority as _photographic_route_agent_authority
from . import art_direction_projection as _art_direction_projection
from . import agent_autonomy as _agent_autonomy
from . import creative as _creative
from . import surface_architecture as _surface_architecture
from . import asset_architecture as _asset_architecture
from . import agent_art_direction_authority as _agent_art_direction_authority
from . import agent_plan_input_bridge as _agent_plan_input_bridge
from . import portfolio_visual_authority as _portfolio_visual_authority
from . import asset_universe_authority as _asset_universe_authority
from . import surface_advisory_authority as _surface_advisory_authority

# Photography is not a universal runtime default. It becomes active only when the Agent's per-asset
# Art Direction selects photographic grammar / camera-light execution; then the strategy-level
# inclusive-photography and lens/lighting decisions remain consumable by the downstream Design Card.
_legacy_prompt_compiler._derived_photo_contract = _photographic_route_agent_authority.wrap_derived_photo_contract(
    _legacy_prompt_compiler._derived_photo_contract
)


def _preserve_canonical_status(fn):
    """Keep established package/compiler compatibility while exposing prompt readiness separately."""
    def compiled(*args, **kwargs):
        out=fn(*args, **kwargs)
        model_status=out.get('status')
        out['model_prompt_status']=model_status
        card=out.get('design_card') or {}
        presence=card.get('product_presence') or {}
        if str(presence.get('planning_state') or '').upper() in {'FORBIDDEN','ABSENT','NOT_APPLICABLE'}:
            prefix='Product is intentionally absent in this asset. Do not add a packshot, corner product, silhouette, podium object or product layer. '
            en=out.get('model_prompt_en') or out.get('prompt_en') or ''
            if 'Product is intentionally absent in this asset.' not in en:
                en=prefix+en
            elif 'Do not add a packshot' not in en:
                en=en.replace('Product is intentionally absent in this asset. ',prefix,1)
            out['model_prompt_en']=en
            out['prompt_en']=en
        if card.get('generation_blocking') or model_status=='AGENT_ART_DIRECTION_REQUIRED':
            out['status']='AGENT_ART_DIRECTION_REQUIRED'
        else:
            out['status']='CANONICAL_PROMPT_COMPILED_AGENT_AUTHORITY'
        return out
    return compiled


# Existing callers continue importing `prompt_compiler.compile_asset_prompt`. First project the
# Agent-authored Art Direction into compatibility fields, compile a true model-facing prompt plus
# separate Visible Copy / Production Notes, close all selected execution parameters, then apply the
# v0.6.33 real-product reference authority so visible real products are natively generated from the
# supplied reference image(s) rather than silently becoming a post-composite plate.
_agent_authority_prompt_compiler.compile_asset_prompt = _art_direction_projection.wrap_compile_asset_prompt(
    _agent_authority_prompt_compiler.compile_asset_prompt
)
_agent_authority_prompt_compiler.compile_asset_prompt = _model_native_prompt_contract.wrap_compile_asset_prompt(
    _agent_authority_prompt_compiler.compile_asset_prompt
)
_agent_authority_prompt_compiler.compile_asset_prompt = _model_native_prompt_audit_fix.wrap_compile_asset_prompt(
    _agent_authority_prompt_compiler.compile_asset_prompt
)
_agent_authority_prompt_compiler.compile_asset_prompt = _human_delivery_art_direction_projection.wrap_compile_asset_prompt(
    _agent_authority_prompt_compiler.compile_asset_prompt
)
_agent_authority_prompt_compiler.compile_asset_prompt = _preserve_canonical_status(
    _agent_authority_prompt_compiler.compile_asset_prompt
)
_agent_authority_prompt_compiler.compile_asset_prompt = _production_parameter_closure.wrap_compile_asset_prompt(
    _agent_authority_prompt_compiler.compile_asset_prompt
)
_agent_authority_prompt_compiler.compile_asset_prompt = _reference_guided_native_authority.wrap_compile_asset_prompt(
    _agent_authority_prompt_compiler.compile_asset_prompt
)
_legacy_prompt_compiler.compile_asset_prompt = _agent_authority_prompt_compiler.compile_asset_prompt

# Explicit Agent-authored variants are an asset universe, not one platform-slot list. H01/H02/H03,
# multiple benefit hypotheses, paid ads, A+/PDP modules, banners and rotation/test variants may coexist
# even when they answer the same shopper question on the same surface. Platform slot capacity limits
# only a simultaneous activation set; it never caps total asset candidates.
_asset_architecture.build_asset_architecture = _asset_universe_authority.wrap_build_asset_architecture(
    _asset_architecture.build_asset_architecture
)

# The compiler imports these symbols after package initialization, so the overrides below become the
# canonical behavior without breaking the historical module/file contract.
_agent_autonomy.compile_agent_autonomy_plan = _agent_art_direction_authority.wrap_compile_agent_autonomy_plan(
    _agent_autonomy.compile_agent_autonomy_plan
)
_agent_autonomy.compile_agent_autonomy_plan = _agent_plan_input_bridge.wrap_compile_agent_autonomy_plan(
    _agent_autonomy.compile_agent_autonomy_plan
)
_agent_autonomy.compile_agent_autonomy_plan = _portfolio_visual_authority.wrap_compile_agent_autonomy_plan(
    _agent_autonomy.compile_agent_autonomy_plan
)
_agent_autonomy.agent_creative_directions = _agent_art_direction_authority.wrap_agent_creative_directions(
    _agent_autonomy.agent_creative_directions
)
_agent_autonomy.agent_creative_directions = _portfolio_visual_authority.wrap_agent_creative_directions(
    _agent_autonomy.agent_creative_directions
)
_agent_autonomy.compile_agent_next_action = _agent_art_direction_authority.wrap_compile_agent_next_action(
    _agent_autonomy.compile_agent_next_action
)
_agent_autonomy.compile_agent_next_action = _portfolio_visual_authority.wrap_compile_agent_next_action(
    _agent_autonomy.compile_agent_next_action
)

# Surface architecture can still provide compatibility suggestions for representation and product
# usefulness, but those suggestions are explicitly non-authoritative for generation.
_surface_architecture.compile_surface_architecture = _surface_advisory_authority.wrap_compile_surface_architecture(
    _surface_architecture.compile_surface_architecture
)

# Final creative assignment consumes the Agent-authored per-asset Art Direction. In Agent-authority
# mode, missing decisions are returned to the Agent and deterministic layout/product fallbacks are disabled.
_creative.apply_creative_system_to_assets = _agent_art_direction_authority.wrap_apply_creative_system_to_assets(
    _creative
)
_creative.apply_creative_system_to_assets = _portfolio_visual_authority.wrap_apply_creative_system_to_assets(
    _creative.apply_creative_system_to_assets
)
