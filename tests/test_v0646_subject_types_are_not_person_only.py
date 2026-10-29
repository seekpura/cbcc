from runtime.cbcc.subject_presence_authority import SUBJECT_TYPES

def test_subject_types_include_non_person_primary_subjects():
    assert {'ANIMAL','PLANT','PRODUCT_OR_OBJECT','ENVIRONMENT','MULTI_SUBJECT','NONE'} <= SUBJECT_TYPES
