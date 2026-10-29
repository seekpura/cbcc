"""CBCC runtime package authority wiring.

v0.6.30 keeps the legacy prompt compiler import surface for compatibility, while production callers
receive the Agent-authority compiler. This bridge is intentionally narrow: it replaces prompt
compilation only; it does not move creative decisions into Python.
"""

from . import prompt_compiler as _legacy_prompt_compiler
from . import agent_authority_prompt_compiler as _agent_authority_prompt_compiler

# Compatibility bridge for existing `from .prompt_compiler import compile_asset_prompt` callers.
# The replacement compiler consumes Agent-authored art direction and refuses to invent product
# presence when that decision is missing.
_legacy_prompt_compiler.compile_asset_prompt = _agent_authority_prompt_compiler.compile_asset_prompt
