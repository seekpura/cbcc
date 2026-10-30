from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path):
    spec = importlib.util.spec_from_file_location('model_prompt_semantic_membrane', path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_model_prompt_authority_explicitly_separates_generation_from_orchestration():
    contract = (ROOT / 'references' / 'MODEL_PROMPT_SEMANTIC_MEMBRANE_CONTRACT.md').read_text(encoding='utf-8')
    for token in [
        'Model Prompt',
        'source-of-truth hierarchy',
        'Excel',
        'QA checklist',
        'minimum repair',
        'Production / Assembly Notes',
        'Review / QA',
        'provider-bound reference',
    ]:
        assert token in contract, token


def test_runtime_semantic_membrane_removes_orchestration_but_keeps_pixel_constraints():
    mod = _load(ROOT / 'runtime' / 'cbcc' / 'model_prompt_semantic_membrane.py')
    raw = '''Create a finished ecommerce image.\nUse the user-provided KIYUU K01 full-view package image as product identity reference; Excel is the highest authority.\nQA: product geometry must match; hands anatomically natural; safe-zone readability passes.\nMinimum repair: text layer -> pump reflection -> full regeneration.\nKeep hands anatomically natural and keep the headline inside the mobile-safe area.\n'''
    cleaned = mod.sanitize_model_prompt(raw, language='EN', reference_bound=True)
    assert 'Excel is the highest authority' not in cleaned
    assert 'QA:' not in cleaned
    assert 'Minimum repair' not in cleaned
    assert 'KIYUU K01' not in cleaned
    assert 'hands anatomically natural' in cleaned
    assert 'mobile-safe area' in cleaned
    assert 'attached product reference images' in cleaned
    assert mod.model_prompt_orchestration_leaks(cleaned) == []


def test_runtime_detects_orchestration_leaks():
    mod = _load(ROOT / 'runtime' / 'cbcc' / 'model_prompt_semantic_membrane.py')
    bad = 'Excel 为最高权威。QA：检查拼写。最小修复：文字层→整图。source/a.xlsx'
    codes = {x['code'] for x in mod.model_prompt_orchestration_leaks(bad)}
    assert 'EXCEL_SOURCE_AUTHORITY' in codes
    assert 'QA_CHECKLIST' in codes
    assert 'MINIMUM_REPAIR_ROUTE' in codes
    assert 'LOCAL_FILE_OR_INTERNAL_SOURCE' in codes


def test_agent_authority_compiler_applies_semantic_membrane_after_rendering():
    text = (ROOT / 'runtime' / 'cbcc' / 'agent_authority_prompt_compiler.py').read_text(encoding='utf-8')
    for token in [
        'model_prompt_semantic_membrane',
        'sanitize_model_prompt',
        'model_prompt_orchestration_leaks',
        "'model_prompt_semantic_membrane'",
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
