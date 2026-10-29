from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_full_authority_loading_map_preserves_mature_depth():
    text = (ROOT / 'prompts' / 'canonical_authority_loading_map.md').read_text(encoding='utf-8')
    for token in [
        'SKILL_AUTHORITY_v0.6.6.md',
        'dynamic_asset_curation.md',
        'creative_direction_surface_prompt_compiler.md',
        'commercial_visual_generation_authority.md',
        'commercial_delivery_stability_authority.md',
        'Photography / CMF / material',
        'Pricing / economics / offer / SKU',
    ]:
        assert token in text


def test_specialist_authorities_still_exist():
    paths = [
        ROOT / 'SKILL_AUTHORITY_v0.6.6.md',
        ROOT / 'prompts' / 'dynamic_asset_curation.md',
        ROOT / 'prompts' / 'creative_direction_surface_prompt_compiler.md',
        ROOT / 'prompts' / 'commercial_visual_generation_authority.md',
        ROOT / 'prompts' / 'commercial_delivery_stability_authority.md',
    ]
    for path in paths:
        assert path.exists(), path
        assert path.stat().st_size > 1000, path
