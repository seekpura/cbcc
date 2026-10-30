from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location('asset_universe_authority_v0655', path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_dynamic_asset_curation_no_longer_optimizes_for_minimum_asset_count():
    text = (ROOT / 'prompts' / 'dynamic_asset_curation.md').read_text(encoding='utf-8')
    assert 'Asset Opportunity Universe' in text
    assert 'Do not optimize the Asset Universe for the fewest assets' in text
    assert 'smallest sufficient' not in text
    assert 'portfolio goal is the fewest assets' not in text
    for token in [
        'Scenario / Lifestyle', 'A+ / Rich Content', 'Paid Ads', 'Creator / UGC',
        'Video / Short Video', 'Test Pool / Rotation Pool / A-B',
        'Surface × Shopper Decision × Creative Hypothesis',
        'platform gallery / video / slot capacity',
    ]:
        assert token in text, token


def test_same_question_surface_can_keep_distinct_ab_hypotheses():
    text = (ROOT / 'prompts' / 'dynamic_asset_curation.md').read_text(encoding='utf-8')
    assert 'A/B and multivariate assets are valid even when they communicate the same core information' in text
    assert 'Never merge merely because question, strategic job, family or surface are the same' in text
    for token in ['hook', 'evidence carrier', 'audience framing', 'offer', 'CTA', 'product presence', 'scene', 'composition grammar', 'motion/beat']:
        assert token in text, token


def test_runtime_keeps_total_universe_separate_from_platform_capacity_and_family_pools():
    mod = _load_module(ROOT / 'runtime' / 'cbcc' / 'asset_universe_authority.py')
    surfaces = [
        'GALLERY','GALLERY','GALLERY','A_PLUS','LONGFORM','PAID_AD','PAID_AD',
        'SOCIAL_CONTENT','CREATOR','SHORT_VIDEO','PDP_VIDEO','STORE_BANNER','CRM',
        'GALLERY','A_PLUS','PAID_AD','SOCIAL_CONTENT','CREATOR','SHORT_VIDEO','GALLERY',
        'LONGFORM','PAID_AD','STORE_BANNER','POST_PURCHASE',
    ]
    assets = []
    for i, surface in enumerate(surfaces, 1):
        assets.append({
            'asset_id': f'A{i:02d}',
            'surface': surface,
            'decision_intent': 'IDENTIFY' if surface == 'GALLERY' else 'DECISION_SUPPORT',
            'business_hypothesis': f'H{i:02d}',
            'variant_id': f'V{i:02d}',
        })
    out = mod.compile_asset_universe(assets, {'gallery_capacity': 9})
    assert out['fixed_total_asset_limit'] is False
    assert out['optimize_for_fewest_assets'] is False
    assert out['platform_capacity_is_activation_constraint_only'] is True
    assert out['activation_set_separate_from_asset_universe'] is True
    assert out['platform_capacity'] == 9
    assert out['total_asset_candidates'] == 24
    assert out['total_asset_candidates'] > out['platform_capacity']
    assert len(out['pools']['PAID_MEDIA']) == 4
    assert len(out['pools']['PDP_CONTENT']) >= 4
    assert len(out['pools']['SOCIAL']) == 2
    assert len(out['pools']['CREATOR']) == 2
    assert len(out['pools']['VIDEO']) == 3
    assert len(out['pools']['STORE']) == 2
    assert len(out['pools']['LIFECYCLE']) == 2


def test_open_world_contract_forbids_platform_slot_backflow():
    text = (ROOT / 'references' / 'ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md').read_text(encoding='utf-8')
    for token in [
        'Asset Opportunity Universe', 'Production Portfolio', 'Activation Set(s)',
        'There is no fixed minimum or maximum total asset count',
        '7/9/10-slot platform does not imply a 7/9/10-candidate universe',
        'A/B hypotheses are merged because core information is the same',
        'smallest sufficient', 'fewest assets possible',
    ]:
        assert token in text, token
