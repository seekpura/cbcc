from runtime.cbcc.subject_presence_authority import normalize_subject_system

def test_missing_subject_is_unresolved_not_person():
    out=normalize_subject_system({'asset_art_direction':{'environment':'home'}})
    assert out['subject_type']=='UNRESOLVED'
    assert out['living_subject_required'] is False
