from runtime.cbcc.subject_presence_authority import normalize_subject_system


def test_explicit_none_is_valid_subject_decision():
    out = normalize_subject_system({'asset_art_direction': {'subject_system': {
        'subject_type': 'NONE',
        'subject_product_relationship': 'product and evidence carry the decision job',
    }}})
    assert out['subject_type'] == 'NONE'
    assert out['living_subject_required'] is False
