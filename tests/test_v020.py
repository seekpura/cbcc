from pathlib import Path
import json,yaml
ROOT=Path(__file__).resolve().parents[1]
def test_legacy_requirements_preserved():
    skill=(ROOT/'SKILL.md').read_text(encoding='utf-8').lower()
    assert 'race' in skill
    assert 'race/ethnicity' in skill
    assert 'positive-first' in skill
    reg=yaml.safe_load((ROOT/'references/platforms/platform_registry.yaml').read_text(encoding='utf-8'))
    for p in ['shopee_br','mercadolivre_br','amazon','tiktok_shop','shopify','noon_uae']:
        assert p in reg['platforms']
    asset=json.loads((ROOT/'schemas/asset_map.schema.json').read_text(encoding='utf-8'))
    assert 'approved_visual_elements' in asset['properties']['assets']['items']['properties']
