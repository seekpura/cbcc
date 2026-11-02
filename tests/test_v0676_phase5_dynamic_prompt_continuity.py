from __future__ import annotations

from copy import deepcopy

from runtime.cbcc.prompt_compiler import compile_asset_prompt


def _asset() -> dict:
    return {
        'asset_id': 'AST-P5-DYNAMIC',
        'asset_name': 'Dynamic prompt continuity fixture',
        'asset_type': 'VIDEO',
        'surface': 'SHORT_VIDEO',
        'family': 'VIDEO',
        'production_mode': 'GENERATIVE_VIDEO',
        'product_fidelity': 'REFERENCE_GUIDED',
        'consumer_question': 'Can this fit naturally into the routine?',
        'strategic_job': 'Make the use sequence and proof rhythm immediately legible.',
        'incremental_information': 'A concise routine sequence with one visible proof action.',
        'product_presence': {
            'planning_state': 'FORBIDDEN',
            'production_state': 'ABSENT',
            'source_reference_role': 'TRUTH_REFERENCE_ONLY',
        },
        'asset_art_direction': {
            'visual_objective': 'Make the routine sequence and proof action immediately legible.',
            'visual_carrier': 'SHORT_VIDEO',
            'visual_language': 'Creator-native vertical commerce video with restrained editorial control.',
            'creative_thesis': 'Routine proof before persuasion.',
            'decisive_moment': 'The application gesture completes cleanly before the handoff hold.',
            'subject': 'A real hand performing the authored routine action; no visible product packshot.',
            'action': 'Complete one believable application gesture without decorative movement.',
            'environment': 'Realistic everyday vanity context with only task-relevant objects.',
            'composition_grammar': 'Vertical action-led framing with the hand entering from camera-left.',
            'layout_geometry': 'Action occupies the central 60% vertical field; upper safe area remains clear.',
            'scale_depth': 'Human-scale close context with a shallow environment layer behind the action.',
            'focal_path': 'hand entry -> proof gesture -> resolved routine state',
            'negative_space': 'Keep the upper 20% visually quiet for platform UI clearance.',
            'evidence_hierarchy': 'proof action -> routine context -> resolved state',
            'output_spec': '1080x1920, 9:16, 12-second TikTok Shop Malaysia short video',
            'copy_render_mode': 'NO_VISIBLE_COPY',
            'product_presence': {
                'planning_state': 'FORBIDDEN',
                'production_state': 'ABSENT',
                'source_reference_role': 'TRUTH_REFERENCE_ONLY',
            },
            'motion': {
                'authority': 'EXPLICIT_AGENT_VIDEO_JOB',
                'narrative_carrier': 'SURFACE_NATIVE_DECISION_SEQUENCE',
                'shots': [
                    {
                        'shot': 'OPEN',
                        'seconds': 3,
                        'job': 'native context open',
                        'visual': 'hand enters frame from camera-left and pauses over the routine area',
                    },
                    {
                        'shot': 'PROOF',
                        'seconds': 6,
                        'job': 'show decision proof',
                        'visual': 'two-finger application gesture completes in one continuous believable motion',
                    },
                    {
                        'shot': 'HANDOFF',
                        'seconds': 3,
                        'job': 'surface-native handoff',
                        'visual': 'hold the resolved routine state without adding a product packshot',
                    },
                ],
                'authored_fields': ['shots', 'narrative_carrier'],
            },
            'timing': {
                'authority': 'EXPLICIT_AGENT_VIDEO_JOB',
                'duration_seconds': 12,
                'shot_timing': [
                    {'shot': 'OPEN', 'start_seconds': 0, 'end_seconds': 3},
                    {'shot': 'PROOF', 'start_seconds': 3, 'end_seconds': 9},
                    {'shot': 'HANDOFF', 'start_seconds': 9, 'end_seconds': 12},
                ],
                'authored_fields': ['duration_seconds'],
            },
            'audio': {
                'authority': 'EXPLICIT_AGENT_VIDEO_JOB',
                'voice_locale': 'ms-MY',
                'subtitle_locales': ['ms-MY', 'en-MY'],
                'voiceover_style': 'creator-native conversational',
                'music_role': 'low-bed only; never mask spoken proof',
                'sfx': ['product handling only when captured or licensed'],
                'silence_policy': 'preserve proof pauses',
                'authored_fields': ['voice_locale', 'subtitle_locales', 'voiceover_style', 'audio'],
            },
        },
        'dynamic_art_direction_status': 'AUTHORED',
        'dynamic_art_direction_missing': [],
        'runtime_may_invent_missing_dynamic_art_direction': False,
        'approved_visual_elements': ['real hand', 'routine-area context'],
        'precision_boundaries': ['no invented packshot', 'no invented efficacy outcome'],
        'editable_layer_contract': {'editable_layers': ['environment'], 'frozen_layers': ['truth constraints']},
    }


def _compile(asset: dict) -> dict:
    return compile_asset_prompt(
        asset,
        {'name': 'K01'},
        {'market': 'MY', 'platform_family': 'TikTok Shop', 'site': 'MY', 'category': 'skincare'},
        {},
        {'primary_locale': 'ms-MY', 'delivery_locale': 'zh-CN'},
        {},
        None,
        None,
        [],
    )


def _checks(out: dict) -> dict[str, dict]:
    return {
        str(row.get('decision')): row
        for row in (out.get('prompt_consumption_audit') or {}).get('checks') or []
        if isinstance(row, dict) and row.get('decision')
    }


def test_phase4_canonical_motion_timing_audio_are_losslessly_projected_into_video_model_prompt():
    out = _compile(_asset())
    en = out['model_prompt_en']

    for concrete in (
        '12',
        'hand enters frame from camera-left and pauses over the routine area',
        'two-finger application gesture completes in one continuous believable motion',
        'creator-native conversational',
        'low-bed only; never mask spoken proof',
        'preserve proof pauses',
    ):
        assert concrete in en, (concrete, en)

    checks = _checks(out)
    for decision in ('motion', 'timing', 'audio'):
        assert decision in checks, checks
        assert checks[decision]['projected'] is True, checks[decision]
    assert not {'motion', 'timing', 'audio'} & set(out['prompt_consumption_audit']['missing_decisions'])


def test_manual_short_prompt_cannot_bypass_canonical_dynamic_parameter_consumption_audit():
    asset = _asset()
    art = deepcopy(asset['asset_art_direction'])
    art['model_prompt_en'] = 'Create a 12-second vertical creator video with the product absent.'
    art['model_prompt_cn'] = '创建一条12秒竖屏达人视频，产品不出现在画面中。'
    asset['asset_art_direction'] = art

    out = _compile(asset)
    missing = set(out['prompt_consumption_audit']['missing_decisions'])
    assert 'motion' in missing, missing
    assert 'audio' in missing, missing
    assert out['prompt_consumption_audit']['status'] == 'INCOMPLETE'


def test_missing_dynamic_audio_stays_missing_and_runtime_does_not_invent_audio_direction():
    asset = _asset()
    art = deepcopy(asset['asset_art_direction'])
    art.pop('audio')
    asset['asset_art_direction'] = art
    asset['dynamic_art_direction_status'] = 'TO_VERIFY'
    asset['dynamic_art_direction_missing'] = ['audio']

    out = _compile(asset)
    missing = set(out['prompt_consumption_audit']['missing_decisions'])
    assert 'audio' in missing, missing
    assert 'creator-native conversational' not in out['model_prompt_en']
    assert 'low-bed only' not in out['model_prompt_en']
    assert out.get('model_prompt_status') not in {'MODEL_NATIVE_PROMPT_READY', 'MODEL_NATIVE_PROMPT_PARAMETER_CLOSED'}


def test_static_asset_without_dynamic_authority_has_no_motion_timing_audio_requirement():
    asset = _asset()
    asset.update({'asset_id': 'AST-P5-STATIC', 'asset_type': 'IMAGE', 'surface': 'GALLERY', 'production_mode': 'GENERATIVE_IMAGE'})
    art = deepcopy(asset['asset_art_direction'])
    for key in ('motion', 'timing', 'audio'):
        art.pop(key, None)
    art['visual_carrier'] = 'EDITORIAL_COMMERCE_IMAGE'
    art['output_spec'] = '1600x1600, 1:1, sRGB'
    asset['asset_art_direction'] = art
    asset.pop('dynamic_art_direction_status', None)
    asset.pop('dynamic_art_direction_missing', None)
    asset.pop('runtime_may_invent_missing_dynamic_art_direction', None)

    out = _compile(asset)
    checks = _checks(out)
    assert not {'motion', 'timing', 'audio'} & set(checks)
    assert not {'motion', 'timing', 'audio'} & set(out['prompt_consumption_audit']['missing_decisions'])
