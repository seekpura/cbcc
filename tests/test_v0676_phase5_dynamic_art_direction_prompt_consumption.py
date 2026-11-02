from __future__ import annotations

from runtime.cbcc.prompt_compiler import compile_asset_prompt


def _dynamic_asset():
    return {
        'asset_id': 'VID-P5-DYNAMIC',
        'asset_name': 'Phase4 dynamic AD prompt bridge',
        'asset_type': 'VIDEO',
        'surface': 'PDP_VIDEO',
        'family': 'VIDEO',
        'production_mode': 'GENERATIVE_VIDEO',
        'visible_copy': {'target_copy': 'RUTIN HARIAN'},
        'product_presence': {
            'planning_state': 'REQUIRED',
            'production_state': 'PRESENT',
            'product_role': 'hero product throughout proof beat',
            'scale_relationship': 'readable label in proof and handoff',
            'source_reference_role': 'SUBJECT_REFERENCE',
        },
        'asset_art_direction': {
            'visual_objective': {
                'cn': '让用户看懂真实使用动作与产品证据。',
                'en': 'Make the real use action and product proof immediately understandable.',
            },
            'visual_carrier': 'PDP_SHORT_VIDEO',
            'visual_language': {
                'cn': '真实创作者短视频，克制商业质感。',
                'en': 'Creator-native short video with restrained commercial polish.',
            },
            'creative_thesis': {'cn': '先用后证据。', 'en': 'Use first, proof second.'},
            'subject': {
                'cn': '真实手部使用产品，瓶身标签持续可辨。',
                'en': 'A real hand uses the product while the bottle label remains readable.',
            },
            'action': {
                'cn': '拿起、使用、停留展示证据。',
                'en': 'Pick up, use, then hold on the proof state.',
            },
            'environment': {'cn': '真实日常梳妆台。', 'en': 'A real everyday vanity context.'},
            'composition_grammar': {
                'cn': '竖屏近景，动作与产品证据同画面。',
                'en': 'Vertical close framing keeps the action and product proof in the same frame.',
            },
            'camera_or_view': 'handheld eye-level close creator view',
            'focal_length_mm': '35mm full-frame equivalent',
            'lighting': {
                'key': 'soft window-side key from camera-left',
                'fill': 'natural room bounce',
                'highlight_policy': 'protect label and bottle highlights',
            },
            'cmf': {
                'color': 'warm neutral vanity with true product color',
                'material': 'real bottle, real skin and vanity materials',
                'finish': 'natural controlled specular response',
            },
            'copy_render_mode': 'MODEL_RENDER',
            'copy_zone': {'cn': '上方安全区。', 'en': 'Upper safe zone.'},
            'typography': {'cn': '简洁无衬线。', 'en': 'Clean sans serif.'},
            'output_spec': '1080×1920, 9:16, 12 seconds, TikTok Shop Malaysia',
            'product_presence': {
                'planning_state': 'REQUIRED',
                'product_role': 'hero product throughout proof beat',
                'scale_relationship': 'readable label in proof and handoff',
                'source_reference_role': 'SUBJECT_REFERENCE',
            },
            # Exact authority shape produced by Phase 4 project_dynamic_art_direction_to_assets().
            'motion': {
                'authority': 'EXPLICIT_AGENT_VIDEO_JOB',
                'video_id': 'VID-P5-DYNAMIC',
                'family': 'VIDEO',
                'surface': 'PDP_VIDEO',
                'narrative_carrier': 'SURFACE_NATIVE_DECISION_SEQUENCE',
                'shots': [
                    {
                        'shot': 'OPEN',
                        'seconds': 3,
                        'job': 'native context open',
                        'visual': 'hand enters the real use context and reaches for the bottle',
                    },
                    {
                        'shot': 'PROOF',
                        'seconds': 6,
                        'job': 'show decision proof',
                        'visual': 'product stays readable during the proof application action',
                    },
                    {
                        'shot': 'HANDOFF',
                        'seconds': 3,
                        'job': 'surface-native handoff',
                        'visual': 'hold the resolved product decision with label readable',
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
    }


def _compile(asset):
    return compile_asset_prompt(
        asset,
        {'name': 'K01'},
        {'market': 'MY', 'platform_family': 'TikTok Shop', 'site': 'MY', 'category': 'skincare'},
        {},
        {'primary_locale': 'ms-MY', 'delivery_locale': 'zh-CN'},
        {},
        None,
        None,
        [
            {
                'asset_id': 'MASTER-FRONT',
                'role': 'FRONT',
                'provider_asset_handle': 'ref://master-front',
                'sha256': 'abc123',
                'ingest_status': 'HASH_VERIFIED_LOCAL',
            }
        ],
    )


def test_phase4_dynamic_motion_timing_audio_are_consumed_by_model_acting_plane():
    out = _compile(_dynamic_asset())
    en = out['model_prompt_en']

    # Semantic membrane may split authored semicolon clauses into separate provider-facing lines;
    # require the authored semantics, not byte-identical punctuation.
    for token in (
        'hand enters the real use context and reaches for the bottle',
        'product stays readable during the proof application action',
        '12',
        'ms-MY',
        'creator-native conversational',
        'low-bed only',
        'never mask spoken proof',
        'product handling only when captured or licensed',
        'preserve proof pauses',
    ):
        assert token in en, token

    checks = {row['decision']: row for row in out['prompt_consumption_audit']['checks']}
    for decision in ('motion', 'timing', 'audio'):
        assert decision in checks, decision
        assert checks[decision]['projected'] is True


def test_source_binding_hash_and_runtime_authority_metadata_stay_out_of_model_prompt():
    out = _compile(_dynamic_asset())
    en = out['model_prompt_en']

    for forbidden in (
        'ref://master-front',
        'abc123',
        'HASH_VERIFIED_LOCAL',
        'EXPLICIT_AGENT_VIDEO_JOB',
        'authored_fields',
        'provider_asset_handle',
    ):
        assert forbidden not in en

    notes = out['production_assembly_notes']
    assert notes['source_product_bindings']
    binding = notes['source_product_bindings'][0]
    assert binding['locator']['kind'] == 'PROVIDER_ASSET_HANDLE'
    assert binding['locator']['value'] == 'ref://master-front'
    assert binding['sha256'] == 'abc123'
    assert binding['ingest_status'] == 'HASH_VERIFIED_LOCAL'
