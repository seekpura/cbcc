from runtime.cbcc.subject_presence_authority import normalize_subject_system

def test_subject_relations_are_preserved():
    out=normalize_subject_system({'asset_art_direction':{'subject_system':{'subject_type':'MULTI_SUBJECT','primary_subject':'dog','secondary_subjects':['owner hand'],'subject_product_relationship':'routine support','subject_scene_relationship':'home grooming'}}})
    assert out['subject_product_relationship']=='routine support'
    assert out['subject_scene_relationship']=='home grooming'
