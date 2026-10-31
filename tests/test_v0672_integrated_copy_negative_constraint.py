from pathlib import Path
import json

from cbcc.long_requirement_full_audit import _prompt_route_contradictions, _project_shortcut_audit


def _asset(root: Path, aid: str, prompt_cn: str, prompt_en: str = '') -> Path:
    d = root / 'asset_packages' / aid
    d.mkdir(parents=True, exist_ok=True)
    (d / '12_design_card.json').write_text(json.dumps({
        'information_design': {
            'copy_render_route': 'MODEL_RENDER_INTEGRATED',
            'locked_visible_copy': {'target_copy': 'KULIT BERMINYAK MASIH PERLUKAN HIDRASI.'},
        },
        'product_presence': {'planning_state': 'ABSENT', 'presence_why': 'information-led asset'},
        'product_identity': {'product_fidelity': 'REFERENCE_GUIDED_NATIVE_LOCK'},
    }, ensure_ascii=False), encoding='utf-8')
    (d / '05_prompt_CN.txt').write_text(prompt_cn, encoding='utf-8')
    (d / '06_prompt_EN.txt').write_text(prompt_en, encoding='utf-8')
    return d


def test_integrated_locked_copy_can_forbid_only_extra_unapproved_text_without_route_contradiction(tmp_path: Path):
    d = _asset(
        tmp_path,
        'AST-1',
        '画面可见文字必须准确呈现："KULIT BERMINYAK MASIH PERLUKAN HIDRASI."\n'
        '不生成额外营销文字、水印或无关品牌。',
        'Render this exact visible market copy: "KULIT BERMINYAK MASIH PERLUKAN HIDRASI."\n'
        'Do not generate extra or unapproved marketing text, watermarks, or unrelated brand names.',
    )
    codes = {row['code'] for row in _prompt_route_contradictions(d)}
    assert 'PROMPT_COPY_ROUTE_CONTRADICTION' not in codes


def test_extra_text_negative_constraint_does_not_create_global_no_visible_copy_pattern(tmp_path: Path):
    for idx in range(3):
        _asset(
            tmp_path,
            f'AST-{idx}',
            '画面可见文字必须准确呈现："KULIT BERMINYAK MASIH PERLUKAN HIDRASI."\n'
            '不要生成额外或未批准的文字、水印、价格或促销信息。',
            'Render this exact visible market copy: "KULIT BERMINYAK MASIH PERLUKAN HIDRASI."\n'
            'Do not generate additional or unapproved text, watermark copy, pricing, or promotions.',
        )
    codes = {row['code'] for row in _project_shortcut_audit(tmp_path)}
    assert 'GLOBAL_NO_VISIBLE_COPY_PATTERN' not in codes


def test_true_no_visible_text_instruction_is_still_detected(tmp_path: Path):
    d = _asset(
        tmp_path,
        'AST-NONE',
        '不要生成任何可见文字或数字。',
        'Do not render any visible text or numbers.',
    )
    codes = {row['code'] for row in _prompt_route_contradictions(d)}
    assert 'PROMPT_COPY_ROUTE_CONTRADICTION' in codes
