from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v0646_builder_keeps_default_prompt_empty():
    text=(ROOT/'scripts/build_plugin_dist_v0646.py').read_text(encoding='utf-8')
    assert 'base.DEFAULT_PROMPTS = []' in text
    assert "interface.pop('defaultPrompt', None)" in text
