from runtime.cbcc.subject_presence_authority import normalize_subject_system, wrap_compile_asset_prompt
from runtime.cbcc.asset_portfolio_taxonomy import enrich_asset_portfolio_taxonomy, portfolio_taxonomy_summary


def test_subject_system_is_not_human_only():
    animal = normalize_subject_system({'asset_art_direction': {'subject_system': {'subject_type': 'ANIMAL', 'primary_subject': 'golden retriever', 'action': 'being brushed'}}})
    assert animal['subject_type'] == 'ANIMAL'
    assert animal['primary_subject'] == 'golden retriever'

    plant = normalize_subject_system({'asset_art_direction': {'subject_system': {'subject_type': 'PLANT', 'primary_subject': 'potted monstera', 'action': 'new leaf detail'}}})
    assert plant['subject_type'] == 'PLANT'

    object_only = normalize_subject_system({'asset_art_direction': {'subject_system': {'subject_type': 'PRODUCT_OR_OBJECT', 'primary_subject': 'product pack'}}})
    assert object_only['subject_type'] == 'PRODUCT_OR_OBJECT'


def test_legacy_human_context_migrates_but_never_becomes_global_default():
    legacy = normalize_subject_system({'asset_art_direction': {'human_context': 'adult hand applying product'}})
    assert legacy['subject_type'] == 'PERSON'
    assert legacy['migration_source'] == 'LEGACY_HUMAN_CONTEXT'

    missing = normalize_subject_system({'asset_art_direction': {'environment': 'bathroom vanity'}})
    assert missing['subject_type'] == 'UNRESOLVED'
    assert missing['living_subject_required'] is False


def test_subject_system_reaches_design_card_and_both_prompts():
    def base(asset, *args, **kwargs):
        return {'design_card': {}, 'prompt_cn': '基础中文', 'prompt_en': 'base english'}

    compile_prompt = wrap_compile_asset_prompt(base)
    asset = {
        'asset_id': 'PET-S01',
        'asset_art_direction': {
            'subject_system': {
                'subject_type': 'MULTI_SUBJECT',
                'primary_subject': 'dog',
                'secondary_subjects': ['owner hand'],
                'action': 'gentle coat brushing',
                'subject_product_relationship': 'dog is the outcome/usage subject; product supports the grooming routine',
                'subject_scene_relationship': 'realistic home grooming context',
            }
        },
    }
    out = compile_prompt(asset, {}, {}, {}, {})
    ss = out['design_card']['subject_system']
    assert ss['subject_type'] == 'MULTI_SUBJECT'
    assert 'dog' in out['prompt_en']
    assert 'gentle coat brushing' in out['prompt_en']
    assert '主体系统' in out['prompt_cn']


def test_asset_universe_has_commercial_families_without_total_slot_cap():
    assets = [
        {'asset_id': 'H01', 'surface': 'GALLERY', 'variant_cluster': 'HERO', 'deployment_state': 'LIVE_CANDIDATE'},
        {'asset_id': 'H02', 'surface': 'GALLERY', 'variant_cluster': 'HERO', 'deployment_state': 'TEST_POOL', 'testing_variant': True},
        {'asset_id': 'A01', 'surface': 'A_PLUS', 'family': 'RICH_CONTENT'},
        {'asset_id': 'P01', 'surface': 'PDP', 'family': 'RICH_CONTENT'},
        {'asset_id': 'AD01', 'surface': 'PAID_AD', 'family': 'PAID'},
        {'asset_id': 'S01', 'surface': 'SOCIAL_CONTENT', 'family': 'SOCIAL'},
        {'asset_id': 'C01', 'surface': 'CREATOR', 'family': 'CREATOR_AFFILIATE'},
        {'asset_id': 'V01', 'surface': 'SHORT_VIDEO', 'asset_type': 'VIDEO'},
        {'asset_id': 'B01', 'surface': 'STORE_BANNER', 'family': 'STORE'},
    ]
    enriched = enrich_asset_portfolio_taxonomy(assets)
    fams = {x['asset_family'] for x in enriched}
    assert {'HERO', 'A_PLUS', 'PDP', 'AD', 'SOCIAL_SEEDING', 'CREATOR_UGC', 'VIDEO', 'BANNER'} <= fams
    summary = portfolio_taxonomy_summary(enriched, {'gallery_capacity': 9})
    assert summary['fixed_total_asset_limit'] is False
    assert summary['platform_capacity_is_activation_constraint_only'] is True
    assert summary['total_asset_candidates'] == 9
    assert summary['activation_capacity'] == 9
    assert summary['activation_capacity_does_not_prune_universe'] is True
