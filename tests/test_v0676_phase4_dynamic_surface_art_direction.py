from __future__ import annotations

from copy import deepcopy

from cbcc.video_creator import build_video_creator_plan, project_dynamic_art_direction_to_assets


def _art(label: str):
    return {
        'visual_master_lineage': {'visual_master_id': 'VM-P4', 'role': label},
        'product_presence': {'planning_state': 'REQUIRED', 'product_role': label},
        'product_fidelity': {'mode': 'REFERENCE_GUIDED_NATIVE_LOCK', 'source_asset_ids': ['SRC-PRODUCT-01']},
        'inclusive_photography': {'authority': 'INCLUSIVE_PHOTOGRAPHY_AUTHORITY', 'status': 'READY'},
        'scene': f'{label} scene',
        'lighting': {'key': {'direction': 'camera-left broad key'}},
    }


def _asset(aid: str, family: str, surface: str):
    return {
        'asset_id': aid,
        'family': family,
        'surface': surface,
        'art_direction_status': 'AUTHORED',
        'asset_art_direction': _art(aid),
    }


def _explicit_job(asset: dict, *, family: str, surface: str, audio: bool = True):
    job = {
        'family': family,
        'surface': surface,
        'source_asset': asset,
        'duration_seconds': 12,
        'narrative_carrier': 'SURFACE_NATIVE_DECISION_SEQUENCE',
        'shots': [
            {'shot': 'OPEN', 'seconds': 3, 'job': 'native context open', 'visual': 'hand enters the real use context'},
            {'shot': 'PROOF', 'seconds': 6, 'job': 'show decision proof', 'visual': 'product stays readable during the proof action'},
            {'shot': 'HANDOFF', 'seconds': 3, 'job': 'surface-native handoff', 'visual': 'hold the resolved decision'},
        ],
    }
    if audio:
        job.update({
            'voice_locale': 'ms-MY',
            'subtitle_locales': ['ms-MY', 'en-MY'],
            'voiceover_style': 'creator-native conversational',
            'audio': {
                'music_role': 'low-bed only; never mask spoken proof',
                'sfx': ['product handling only when captured or licensed'],
                'silence_policy': 'preserve proof pauses',
            },
        })
    return job


def _plan(assets, jobs):
    return build_video_creator_plan(
        'P4-DYNAMIC',
        [],
        ['What should the shopper understand?'],
        {'primary_locale': 'en-MY', 'script_subtitle_locales': ['en-MY']},
        jobs,
        assets=assets,
        creative_council={'selected_direction': {'direction_id': 'DIR-P4'}},
    )


def test_explicit_pdp_ugc_live_jobs_project_motion_timing_audio_into_same_asset_art_direction():
    pdp = _asset('AST-PDP-VIDEO', 'VIDEO', 'PDP_VIDEO')
    ugc = _asset('AST-UGC', 'CREATOR_AFFILIATE', 'UGC_BRIEF')
    live = _asset('AST-LIVE', 'LIVE', 'LIVE')
    static = _asset('AST-STATIC', 'VISUAL', 'GALLERY')
    architecture = {'assets': [pdp, ugc, live, static]}
    original = deepcopy(architecture)

    plan = _plan(
        architecture['assets'],
        [
            _explicit_job(pdp, family='VIDEO', surface='PDP_VIDEO'),
            _explicit_job(ugc, family='CREATOR_AFFILIATE', surface='UGC_BRIEF'),
            _explicit_job(live, family='LIVE', surface='LIVE'),
        ],
    )
    out = project_dynamic_art_direction_to_assets(architecture, plan)
    rows = {row['asset_id']: row for row in out['assets']}

    for aid in ['AST-PDP-VIDEO', 'AST-UGC', 'AST-LIVE']:
        before = next(row for row in original['assets'] if row['asset_id'] == aid)['asset_art_direction']
        after = rows[aid]['asset_art_direction']
        assert after['visual_master_lineage'] == before['visual_master_lineage']
        assert after['product_presence'] == before['product_presence']
        assert after['product_fidelity'] == before['product_fidelity']
        assert after['inclusive_photography'] == before['inclusive_photography']
        assert after['motion']['authority'] == 'EXPLICIT_AGENT_VIDEO_JOB'
        assert after['motion']['shots'][0]['shot'] == 'OPEN'
        assert after['timing']['duration_seconds'] == 12
        assert after['timing']['shot_timing']
        assert after['audio']['voice_locale'] == 'ms-MY'
        assert after['audio']['voiceover_style'] == 'creator-native conversational'
        assert after['audio']['music_role'].startswith('low-bed')
        assert rows[aid]['dynamic_art_direction_status'] == 'AUTHORED'
        assert rows[aid]['dynamic_art_direction_missing'] == []

    assert rows['AST-STATIC']['asset_art_direction'] == original['assets'][3]['asset_art_direction']
    assert 'motion' not in rows['AST-STATIC']['asset_art_direction']
    assert 'timing' not in rows['AST-STATIC']['asset_art_direction']
    assert 'audio' not in rows['AST-STATIC']['asset_art_direction']
    assert 'dynamic_art_direction_status' not in rows['AST-STATIC']


def test_runtime_fallback_plan_never_becomes_authoritative_dynamic_art_direction():
    asset = _asset('AST-FALLBACK', 'VIDEO', 'PDP_VIDEO')
    plan = _plan([asset], [{'family': 'VIDEO', 'surface': 'PDP_VIDEO', 'source_asset': asset}])
    assert plan['assets'][0]['narrative_source'] == 'DECISION_DERIVED_RUNTIME_FALLBACK'

    out = project_dynamic_art_direction_to_assets({'assets': [asset]}, plan)
    row = out['assets'][0]
    art = row['asset_art_direction']
    assert 'motion' not in art
    assert 'timing' not in art
    assert 'audio' not in art
    assert row['dynamic_art_direction_status'] == 'TO_VERIFY'
    assert set(row['dynamic_art_direction_missing']) == {'motion', 'timing', 'audio'}
    assert row['runtime_may_invent_missing_dynamic_art_direction'] is False


def test_partial_explicit_job_projects_only_authored_dynamic_decisions_and_keeps_audio_missing():
    asset = _asset('AST-PARTIAL', 'CREATOR_AFFILIATE', 'UGC_BRIEF')
    plan = _plan([asset], [_explicit_job(asset, family='CREATOR_AFFILIATE', surface='UGC_BRIEF', audio=False)])
    out = project_dynamic_art_direction_to_assets({'assets': [asset]}, plan)
    row = out['assets'][0]
    art = row['asset_art_direction']

    assert art['motion']['shots']
    assert art['timing']['duration_seconds'] == 12
    assert 'audio' not in art
    assert row['dynamic_art_direction_status'] == 'TO_VERIFY'
    assert row['dynamic_art_direction_missing'] == ['audio']
    assert row['runtime_may_invent_missing_dynamic_art_direction'] is False


def test_video_plan_carries_field_level_authorship_instead_of_treating_defaults_as_authority():
    asset = _asset('AST-PROVENANCE', 'VIDEO', 'PDP_VIDEO')
    explicit = _plan([asset], [_explicit_job(asset, family='VIDEO', surface='PDP_VIDEO')])['assets'][0]
    assert explicit['dynamic_art_direction_authorship']['motion'] is True
    assert explicit['dynamic_art_direction_authorship']['timing'] is True
    assert explicit['dynamic_art_direction_authorship']['audio'] is True
    assert set(explicit['authored_dynamic_fields']['audio']) >= {'voice_locale', 'subtitle_locales', 'voiceover_style', 'audio'}

    fallback = _plan([asset], [{'family': 'VIDEO', 'surface': 'PDP_VIDEO', 'source_asset': asset}])['assets'][0]
    assert fallback['dynamic_art_direction_authorship'] == {'motion': False, 'timing': False, 'audio': False}
    assert fallback['authored_dynamic_fields'] == {'motion': [], 'timing': [], 'audio': []}
