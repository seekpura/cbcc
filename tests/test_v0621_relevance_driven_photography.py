from cbcc.tools.visual import validate_photography_contract


def test_composite_mode_does_not_force_fake_camera_light_or_occupancy_parameters():
    out = validate_photography_contract({'capture_mode':'COMPOSITE'})
    assert out['pass'] is True
    assert out['issues'] == []
    assert 'CAMERA_PRECISION' in out['not_applicable_dimensions']
    assert 'LIGHTING_PRECISION' in out['not_applicable_dimensions']
    assert 'PRODUCT_OCCUPANCY_LOCK' in out['not_applicable_dimensions']


def test_real_photo_can_use_semantic_perspective_contract_without_numeric_focal_length():
    out = validate_photography_contract({
        'capture_mode':'REAL_PHOTO',
        'required_dimensions':['CAMERA'],
        'camera':{'perspective_contract':'truthful front three-quarter view chosen for label readability'},
    })
    assert out['pass'] is True
    assert not any(issue['code']=='FOCAL_LENGTH' for issue in out['issues'])


def test_numeric_occupancy_only_becomes_mandatory_when_agent_or_user_locks_it():
    free = validate_photography_contract({'capture_mode':'PHOTOREAL_AI'})
    assert free['pass'] is True
    locked = validate_photography_contract({'capture_mode':'PHOTOREAL_AI','required_dimensions':['PRODUCT_OCCUPANCY']})
    assert locked['pass'] is False
    assert any(issue['code']=='OCCUPANCY_PRECISION' for issue in locked['issues'])


def test_locked_pixel_makes_color_management_a_real_hard_constraint():
    missing = validate_photography_contract({'capture_mode':'COMPOSITE','product_fidelity':'LOCKED_PIXEL'})
    assert missing['pass'] is False
    assert {issue['code'] for issue in missing['issues']} == {'OUTPUT_SPACE','PRODUCT_COLOR_FIDELITY'}
    ready = validate_photography_contract({
        'capture_mode':'COMPOSITE','product_fidelity':'LOCKED_PIXEL',
        'color_management':{'output_space':'sRGB','product_color_fidelity':'preserve verified master pixels and packaging color'},
    })
    assert ready['pass'] is True


def test_repeatable_capture_raises_precision_only_for_relevant_dimensions():
    out = validate_photography_contract({
        'capture_mode':'REAL_PHOTO','repeatable_capture':True,
        'camera':{'perspective_contract':'front label-readable','camera_distance':'80cm','focus_plane':'front label plane'},
        'lighting':{'key':{'direction':'camera-left broad source','modifier':'large diffusion'},'white_balance_intent':'neutral product color'},
    })
    assert out['pass'] is True
    assert out['precision_level']=='REPEATABLE_CAPTURE_READY'
