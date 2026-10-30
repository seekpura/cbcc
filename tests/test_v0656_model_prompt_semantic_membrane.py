from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_model_prompt_authority_explicitly_separates_generation_from_orchestration():
    compiler = (ROOT / 'prompts' / 'creative_direction_surface_prompt_compiler.md').read_text(encoding='utf-8')
    visual = (ROOT / 'prompts' / 'commercial_visual_generation_authority.md').read_text(encoding='utf-8')
    joined = compiler + '\n' + visual
    for token in [
        'Model Prompt Semantic Membrane',
        'source-of-truth hierarchy',
        'Excel',
        'QA checklist',
        'minimum-repair route',
        'Production / Assembly Notes',
        'Review / QA',
        'provider-bound reference',
    ]:
        assert token in joined, token


def test_runtime_model_prompt_does_not_render_editability_or_internal_reference_mode_sections():
    text = (ROOT / 'runtime' / 'cbcc' / 'prompt_compiler.py').read_text(encoding='utf-8')
    render_start = text.index('def _render_lines')
    render_end = text.index('def _parameter_trace')
    render = text[render_start:render_end]
    assert '[VISUAL EXECUTION BOUNDARIES / EDITABILITY]' not in render
    assert '【视觉执行边界 / 可编辑性】' not in render
    assert 'Product reference mode:' not in render
    assert '产品参考模式：' not in render
    assert 'Editable layers:' not in render
    assert 'Frozen layers:' not in render


def test_runtime_has_orchestration_leak_detector_for_model_prompt():
    text = (ROOT / 'runtime' / 'cbcc' / 'prompt_compiler.py').read_text(encoding='utf-8')
    for token in [
        'def _model_prompt_orchestration_leaks',
        'EXCEL_SOURCE_AUTHORITY',
        'QA_CHECKLIST',
        'MINIMUM_REPAIR_ROUTE',
        'LOCAL_FILE_OR_INTERNAL_SOURCE',
    ]:
        assert token in text, token


def test_prompt_contract_keeps_pixel_relevant_constraints_but_not_project_orchestration():
    contract = (ROOT / 'references' / 'MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md').read_text(encoding='utf-8')
    for token in [
        'Only model-visible, pixel-changing instructions belong in Model Prompt',
        'Use the attached product reference images',
        'Excel is the highest authority',
        'QA:',
        'minimum repair',
        'hands anatomically natural',
        'render no extra marketing text',
    ]:
        assert token in contract, token
