from pathlib import Path


def test_v0631_model_native_release_gate_uses_explicit_copy_render_contract():
    root=Path(__file__).resolve().parents[1]
    native=(root/'runtime/cbcc/model_native_prompt_contract.py').read_text(encoding='utf-8')
    assert 'COPY_RENDER_MODE_REQUIRED' in native
    assert 'DETERMINISTIC_COMPOSITION_AFTER_RENDER' not in native
