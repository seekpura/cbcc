from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_workspace_prompt_continuity_authority_exists():
    p = ROOT / 'references' / 'HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md'
    assert p.exists()
    text = p.read_text(encoding='utf-8')
    for token in [
        'cbcc-commercial-v1', 'v0.6.36', 'runtime-first',
        'delivery_export.py', 'delivery_workspace.py', 'delivery_html.py',
        '不得重写 index.html', 'asset/<id>', 'Prompt 工作面', 'Prompt lens',
        '05_prompt_CN.txt', '06_prompt_EN.txt', '九域不是九个页面',
        '用户明确要求 redesign',
    ]:
        assert token in text, token


def test_mature_runtime_still_exposes_routed_workspace_and_prompts():
    delivery_workspace = (ROOT / 'runtime/cbcc/delivery_workspace.py').read_text(encoding='utf-8')
    delivery_html = (ROOT / 'runtime/cbcc/delivery_html.py').read_text(encoding='utf-8')
    shell = (ROOT / 'runtime/cbcc/commercial_workspace_shell.py').read_text(encoding='utf-8')
    export = (ROOT / 'runtime/cbcc/delivery_export.py').read_text(encoding='utf-8')
    assert 'v0.6.36 routed workspace' in delivery_workspace
    assert 'one routed primary work surface at a time' in delivery_workspace
    for token in ['05_prompt_CN.txt', '06_prompt_EN.txt', '_prompt_workspace', 'data-route="prompts"', 'Model Prompt CN', 'Model Prompt EN', 'asset/']:
        assert token in delivery_html, token
    assert "WORKSPACE_SHELL_VERSION='cbcc-commercial-v1'" in shell
    assert 'from .delivery_workspace import build_delivery_html' in export


def test_workspace_prompt_validator_and_builder_are_release_required():
    validator = ROOT / 'scripts' / 'check_v0654_workspace_prompt_continuity.py'
    builder = ROOT / 'scripts' / 'build_plugin_dist_v0654.py'
    assert validator.exists()
    assert builder.exists()
    vt = validator.read_text(encoding='utf-8')
    bt = builder.read_text(encoding='utf-8')
    for token in [
        'MATURE_ROUTED_WORKSPACE_LOST', 'ASSET_DETAIL_ROUTES_MISSING',
        'PROMPT_CN_NOT_PROJECTED_TO_HUMAN_HTML', 'PROMPT_EN_NOT_PROJECTED_TO_HUMAN_HTML',
        'FIXED_NINE_SECTION_REPLACEMENT_SHELL',
    ]:
        assert token in vt, token
    for token in [
        'build_plugin_dist_v0653', '0.6.54', 'HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md',
        'runtime_first_materialization_when_available', 'repair_shell_rewrite_forbidden',
        'prompt_files_must_be_human_projected', 'per_asset_prompt_lens_required',
        'prompt_workspace_required', 'asset_detail_routes_required',
        'v0653_business_object_density_preserved',
    ]:
        assert token in bt, token


def test_release_matrix_blocks_shell_and_prompt_projection_regression():
    text = (ROOT / 'references' / 'RELEASE_NON_REGRESSION_MATRIX.yaml').read_text(encoding='utf-8')
    for token in [
        'workspace_continuity_without_prompt_projection_loss',
        'repair_without_shell_replacement',
        'prompt_workspace', 'per_asset_prompt_lens', 'asset_detail_routes',
        'regenerating index.html from scratch',
        'preserving prompt files but removing them from Human HTML',
        'fixed nine-section report',
    ]:
        assert token in text, token
