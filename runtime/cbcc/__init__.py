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

v0.6.46 adds commercial decision continuity: real Market/Pricing/Audience/RACE/Listing/Ads/Review
payloads must survive into relevant asset lineage, Creative Curation, Design Cards, model prompts and
human delivery. Status/count summaries never substitute for real downstream consumption. Subject
choice is per asset: person, animal, plant, object/product, environment, multi-subject or none are valid.
"""

from . import prompt_compiler as _legacy_prompt_compiler
from . import agent_authority_prompt_compiler as _agent_authority_prompt_compiler
from . import model_native_prompt_contract as _model_native_prompt_contract
from . import model_native_prompt_audit_fix as _model_native_prompt_audit_fix
from . import production_parameter_closure as _production_parameter_closure
from . import reference_guided_native_authority as _reference_guided_native_authority
from . import commercial_operator_density_authority as _commercial_operator_density_authority
from . import commercial_continuity_authority as _commercial_continuity_authority
from . import commercial_curation_lineage as _commercial_curation_lineage
from . import subject_presence_authority as _subject_presence_authority
from . import human_delivery_art_direction_projection as _human_delivery_art_direction_projection
from . import photographic_route_agent_authority as _photographic_route_agent_authority
from . import art_direction_projection as _art_direction_projection
from . import agent_autonomy as _agent_autonomy
from . import creative as _creative
from . import creative_opportunity as _creative_opportunity
from . import surface_architecture as _surface_architecture
from . import asset_architecture as _asset_architecture
from . import agent_art_direction_authority as _agent_art_direction_authority
from . import agent_plan_input_bridge as _agent_plan_input_bridge
from . import portfolio_visual_authority as _portfolio_visual_authority
from . import asset_universe_authority as _asset_universe_authority
from . import asset_portfolio_taxonomy as _asset_portfolio_taxonomy
from . import surface_advisory_authority as _surface_advisory_authority
from .tools import seven_agent as _seven_agent

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
_agent_authority_prompt_compiler.compile_asset_prompt = _commercial_operator_density_authority.wrap_compile_asset_prompt(
    _agent_authority_prompt_compiler.compile_asset_prompt
)
_agent_authority_prompt_compiler.compile_asset_prompt = _commercial_continuity_authority.wrap_compile_asset_prompt(
    _agent_authority_prompt_compiler.compile_asset_prompt
)
_agent_authority_prompt_compiler.compile_asset_prompt = _subject_presence_authority.wrap_compile_asset_prompt(
    _agent_authority_prompt_compiler.compile_asset_prompt
)
_legacy_prompt_compiler.compile_asset_prompt = _agent_authority_prompt_compiler.compile_asset_prompt

# Seven-tool continuity must hand real business payloads to assets, not only status/count summaries.
# The standalone image tool also receives the same wrapped prompt compiler as the full project compiler.
_seven_agent.compile_asset_prompt = _legacy_prompt_compiler.compile_asset_prompt
_seven_agent.compile_seven_agent_synthesis = _commercial_continuity_authority.wrap_compile_seven_agent_synthesis(
    _seven_agent.compile_seven_agent_synthesis
)

# Explicit Agent-authored variants are an asset universe, not one platform-slot list. H01/H02/H03,
# benefit/proof/scenario alternatives, paid ads, A+/PDP, seeding/social, creator/UGC, video, banners and
# test/rotation pools may coexist. Platform capacity limits only a simultaneous activation set.
_asset_architecture.build_asset_architecture = _asset_universe_authority.wrap_build_asset_architecture(
    _asset_architecture.build_asset_architecture
)
_asset_architecture.build_asset_architecture = _asset_portfolio_taxonomy.wrap_build_asset_architecture(
    _asset_architecture.build_asset_architecture
)

# Commercial analysis must enter curation before it reaches the final prompt. Preserve current asset
# decision origins/sources plus target/culture in Creative Opportunity and Creative Council, then carry
# the same basis into per-asset Art Direction. This prevents style-only curation from severing analysis.
_creative_opportunity.compile_creative_opportunity_universe = _commercial_curation_lineage.wrap_compile_creative_opportunity_universe(
    _creative_opportunity.compile_creative_opportunity_universe
)
_creative.compile_creative_council = _commercial_curation_lineage.wrap_compile_creative_council(
    _creative.compile_creative_council
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
_creative.apply_creative_system_to_assets = _commercial_curation_lineage.wrap_apply_creative_system_to_assets(
    _creative.apply_creative_system_to_assets
)

# Human delivery receives the same structured commercial intelligence instead of relegating Market /
# Pricing / Audience / RACE / Ads / Reviews to machine JSON archives. Keep it inside the existing
# v0.6.36/v1 routed workspace rather than replacing the shell.
from . import commercial_delivery_continuity as _commercial_delivery_continuity
from . import delivery_workspace as _delivery_workspace
_delivery_workspace.build_delivery_html = _commercial_delivery_continuity.wrap_build_delivery_html(
    _delivery_workspace.build_delivery_html
)
from . import delivery_export as _delivery_export
_delivery_export.build_delivery_html = _delivery_workspace.build_delivery_html
_delivery_export.export_delivery_package = _commercial_delivery_continuity.wrap_export_delivery_package(
    _delivery_export.export_delivery_package
)

# Install the release-level strictness layer after normal authority wiring so asset_compiler captures
# the final prompt compiler and human Design Card projection. This also prevents future wrappers from
# silently weakening commercial-continuity readiness.
from . import commercial_continuity_bootstrap as _commercial_continuity_bootstrap
_commercial_continuity_bootstrap.install()
