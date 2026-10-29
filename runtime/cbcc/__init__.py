"""CBCC runtime package authority wiring.

v0.6.30+ keeps legacy module import surfaces for compatibility while installing narrow authority
bridges: the host Agent authors portfolio curation, product presence and per-asset Art Direction;
Python validates, serializes, compiles and executes those decisions. Missing creative decisions are
returned to the Agent instead of being filled with deterministic product/layout fallbacks.

Model-facing prompts are a distinct artifact from production/assembly contracts. Runtime may carry
locked-source, copy-composition, editable-layer and provider instructions separately, but must not
pollute the image/video model prompt with those engineering contracts.
"""

from . import prompt_compiler as _legacy_prompt_compiler
from . import agent_authority_prompt_compiler as _agent_authority_prompt_compiler
from . import model_native_prompt_contract as _model_native_prompt_contract
from . import art_direction_projection as _art_direction_projection
from . import agent_autonomy as _agent_autonomy
from . import creative as _creative
from . import surface_architecture as _surface_architecture
from . import agent_art_direction_authority as _agent_art_direction_authority
from . import agent_plan_input_bridge as _agent_plan_input_bridge
from . import surface_advisory_authority as _surface_advisory_authority

# Existing callers continue importing `prompt_compiler.compile_asset_prompt`. First project the
# Agent-authored Art Direction into compatibility fields, then compile the existing machine/design
# contracts, and finally replace the legacy execution-contract prose with a true model-facing prompt
# plus separate Visible Copy and Production / Assembly Notes objects.
_agent_authority_prompt_compiler.compile_asset_prompt = _art_direction_projection.wrap_compile_asset_prompt(
    _agent_authority_prompt_compiler.compile_asset_prompt
)
_agent_authority_prompt_compiler.compile_asset_prompt = _model_native_prompt_contract.wrap_compile_asset_prompt(
    _agent_authority_prompt_compiler.compile_asset_prompt
)
_legacy_prompt_compiler.compile_asset_prompt = _agent_authority_prompt_compiler.compile_asset_prompt

# The compiler imports these symbols after package initialization, so the overrides below become the
# canonical behavior without breaking the historical module/file contract.
_agent_autonomy.compile_agent_autonomy_plan = _agent_art_direction_authority.wrap_compile_agent_autonomy_plan(
    _agent_autonomy.compile_agent_autonomy_plan
)
# Normalize convenient host-Agent locations into the canonical creative_exploration contract.
_agent_autonomy.compile_agent_autonomy_plan = _agent_plan_input_bridge.wrap_compile_agent_autonomy_plan(
    _agent_autonomy.compile_agent_autonomy_plan
)
_agent_autonomy.agent_creative_directions = _agent_art_direction_authority.wrap_agent_creative_directions(
    _agent_autonomy.agent_creative_directions
)
_agent_autonomy.compile_agent_next_action = _agent_art_direction_authority.wrap_compile_agent_next_action(
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
