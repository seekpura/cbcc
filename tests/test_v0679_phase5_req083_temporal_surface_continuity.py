from __future__ import annotations

from copy import deepcopy

from cbcc.prompt_compiler import compile_asset_prompt
from cbcc.video_creator import build_video_creator_plan, project_dynamic_art_direction_to_assets


def _source() -> dict:
    return {
        'asset_id': 'SRC-PRODUCT-01',
        'role': 'REAL_PRODUCT_MASTER',
        'provider_asset_handle': 'provider://real-product-master-01',
        'sha256': 'sha256-real-product-master-01',
        'ingest_status': 'READY',
        'pixel_lock': True,
        'identity_features': ['package geometry', 'logo', 'label layout', 'primary color'],
    }


def _asset(aid: str, family: str, surface: str) -> dict:
    return {
        'asset_id': aid,
        'asset_name': f'{surface} temporal continuity fixture',
        'asset_type': 'VIDEO',
        'family': family,
        'surface': surface,
        'production_mode': 'GENERATIVE_VIDEO',
        'art_direction_status': 'AUTHORED',
        'consumer_question': 'Can I understand the product proof and identity without losing continuity?',
        'strategic_job': 'Carry a surface-native temporal proof sequence without changing product identity.',
        'incremental_information': 'A timed product proof with explicit first-frame, text, motion and audio roles.',
        'product_presence': {
            'planning_state': 'REQUIRED',
            'production_state': 'PRESENT',
            'product_role': 'PROOF_SUBJECT',
            'source_reference_role': 'NATIVE_SUBJECT_REFERENCE',
        },
        'visible_copy': {
            'target_copy': 'Proof in one routine',
            'delivery_translation_zh': '一个流程看懂证据',
        },
        'asset_art_direction': {
            'visual_objective': 'Keep the product identity stable while the proof unfolds in time.',
            'visual_carrier': surface,
            'visual_language': 'surface-native vertical commerce video with restrained editorial control',
            'creative_thesis': 'Continuity makes the proof believable.',
            'decisive_moment': 'The proof action lands while the same product identity remains readable.',
            'subject': 'real referenced product handled naturally by one creator hand',
            'action': 'perform one proof action without swapping or redesigning the product',
            'environment': 'realistic everyday vanity context',
            'composition_grammar': 'vertical action-led framing with stable product readability',
            'layout_geometry': 'product remains inside the central safe field while proof action occurs',
            'scale_depth': 'close human-scale proof with shallow contextual depth',
            'focal_path': 'first-frame product identity -> proof action -> resolved hold',
            'negative_space': 'reserve upper safe area for timed copy and platform UI',
            'evidence_hierarchy': 'product identity -> proof action -> resolved decision',
            'camera_or_view': 'eye-level close three-quarter video view',
            'lighting': {
                'key': {'direction': 'camera-left 45 degrees', 'modifier': 'large diffusion'},
                'fill': {'direction': 'camera-right', 'level': '-1 stop'},
                'cct': 5200,
            },
            'cmf': {'color': 'neutral warm field', 'material': 'real package material', 'finish': 'truthful highlights'},
            'copy_render_mode': 'MODEL_RENDER_INTEGRATED',
            'typography': {
                'en': 'compact sans-serif, medium weight, upper safe-zone placement',
                'cn': '简洁无衬线，中等字重，上方安全区排版',
            },
            'output_spec': '1080x1920, 9:16, 12-second vertical commerce video',
            'product_presence': {
                'planning_state': 'REQUIRED',
                'production_state': 'PRESENT',
                'product_role': 'PROOF_SUBJECT',
                'source_reference_role': 'NATIVE_SUBJECT_REFERENCE',
            },
            'product_fidelity': {
                'authority': 'AGENT_ASSET_ART_DIRECTION',
                'mode': 'REFERENCE_GUIDED_NATIVE_LOCK',
                'source_asset_ids': ['SRC-PRODUCT-01'],
                'immutable_identity_fields': ['logo', 'packaging_print', 'geometry', 'proportions'],
            },
        },
        'approved_visual_elements': ['real referenced product', 'creator hand', 'routine context'],
        'precision_boundaries': ['no package redesign', 'no invented efficacy result'],
        'editable_layer_contract': {
            'editable_layers': ['environment', 'timed copy'],
            'frozen_layers': ['product identity', 'truth constraints'],
        },
    }


def _job(asset: dict) -> dict:
    surface = asset['surface']
    return {
        'family': asset['family'],
        'surface': surface,
        'source_asset': asset,
        'duration_seconds': 12,
        'narrative_carrier': f'{surface}_TEMPORAL_PROOF',
        'shots': [
            {'shot': 'OPEN', 'seconds': 3, 'job': 'identity lock', 'visual': 'same referenced product is readable before motion begins'},
            {'shot': 'PROOF', 'seconds': 6, 'job': 'proof action', 'visual': 'creator performs the proof action without hiding or swapping the product'},
            {'shot': 'HOLD', 'seconds': 3, 'job': 'resolved hold', 'visual': 'same product resolves into the final decision frame'},
        ],
        'subject_motion': 'creator hand lifts the same referenced product once, performs one proof gesture, then settles',
        'camera_motion': 'locked 10 cm push-in only during the proof beat; no orbit and no identity-breaking reframing',
        'transitions': [
            {'at_seconds': 3, 'type': 'action-matched straight cut'},
            {'at_seconds': 9, 'type': 'continuity cut into resolved hold'},
        ],
        'product_identity_continuity': 'the same referenced package geometry, logo, label layout and primary color remain unchanged in every frame',
        'first_frame_logic': 'frame 0 must establish the referenced product identity before any proof motion or copy appears',
        'cover_logic': 'cover uses the same frame-0 product identity and scene world; never substitute a separate packshot',
        'text_timing': [
            {'copy': 'Proof in one routine', 'start_seconds': 0.6, 'end_seconds': 2.4, 'role': 'opening decision promise'},
            {'copy': 'Same product. One proof.', 'start_seconds': 9.2, 'end_seconds': 11.6, 'role': 'resolved hold label'},
        ],
        'voice_locale': 'ms-MY',
        'subtitle_locales': ['ms-MY', 'en-MY'],
        'voiceover_style': 'creator-native conversational',
        'vo_role': 'VO explains only the shopper decision while the visual proof remains primary',
        'subtitle_role': 'subtitles mirror spoken proof and stay outside the product/action evidence area',
        'audio': {
            'music_role': 'low-bed only; never mask spoken proof',
            'sfx': ['single authentic handling sound at the proof gesture'],
            'silence_policy': 'leave a short pause over the resolved hold',
        },
    }


def _project(asset: dict) -> dict:
    plan = build_video_creator_plan(
        'P5-REQ083',
        [],
        ['What should the shopper understand?'],
        {'primary_locale': 'en-MY', 'script_subtitle_locales': ['en-MY']},
        [_job(asset)],
        assets=[asset],
        creative_council={'selected_direction': {'direction_id': 'DIR-REQ083'}},
    )
    out = project_dynamic_art_direction_to_assets({'assets': [asset]}, plan)
    return out['assets'][0]


def _compile(asset: dict) -> dict:
    return compile_asset_prompt(
        asset,
        {'name': 'K01'},
        {'market': 'MY', 'platform_family': 'TikTok Shop', 'site': 'MY', 'category': 'skincare'},
        {},
        {'primary_locale': 'en-MY', 'delivery_locale': 'zh-CN'},
        {},
        None,
        None,
        [_source()],
    )


def test_explicit_temporal_decisions_survive_video_creator_projection_for_pdp_ugc_and_live_surfaces():
    surfaces = [
        ('AST-PDP-TEMPORAL', 'VIDEO', 'PDP_VIDEO'),
        ('AST-UGC-TEMPORAL', 'CREATOR_AFFILIATE', 'UGC_BRIEF'),
        ('AST-LIVE-TEMPORAL', 'LIVE', 'LIVE'),
    ]
    for aid, family, surface in surfaces:
        projected = _project(_asset(aid, family, surface))
        art = projected['asset_art_direction']
        assert art['motion']['subject_motion'].startswith('creator hand lifts the same referenced product once'), (surface, art['motion'])
        assert art['motion']['camera_motion'].startswith('locked 10 cm push-in'), (surface, art['motion'])
        assert art['motion']['transitions'][0]['type'] == 'action-matched straight cut'
        assert art['motion']['product_identity_continuity'].startswith('the same referenced package geometry')
        assert art['motion']['first_frame_logic'].startswith('frame 0 must establish')
        assert art['motion']['cover_logic'].startswith('cover uses the same frame-0 product identity')
        assert art['timing']['text_timing'][0]['start_seconds'] == 0.6
        assert art['audio']['vo_role'].startswith('VO explains only the shopper decision')
        assert art['audio']['subtitle_role'].startswith('subtitles mirror spoken proof')
        assert projected['dynamic_art_direction_status'] == 'AUTHORED'
        assert projected['dynamic_art_direction_missing'] == []


def test_full_temporal_contract_reaches_final_acting_prompt_and_consumption_audit():
    projected = _project(_asset('AST-UGC-PROMPT', 'CREATOR_AFFILIATE', 'UGC_BRIEF'))
    out = _compile(projected)
    en = out['model_prompt_en']
    for concrete in (
        'creator hand lifts the same referenced product once',
        'locked 10 cm push-in only during the proof beat',
        'action-matched straight cut',
        'frame 0 must establish the referenced product identity',
        'cover uses the same frame-0 product identity',
        'Proof in one routine',
        '0.6',
        '2.4',
        'VO explains only the shopper decision',
        'subtitles mirror spoken proof',
        'the same referenced package geometry, logo, label layout and primary color remain unchanged in every frame',
    ):
        assert concrete in en, (concrete, en)

    checks = {
        row.get('decision'): row
        for row in (out.get('prompt_consumption_audit') or {}).get('checks') or []
        if isinstance(row, dict) and row.get('decision')
    }
    for decision in ('motion', 'timing', 'audio'):
        assert checks[decision]['projected'] is True, checks.get(decision)
    assert not {'motion', 'timing', 'audio'} & set(out['prompt_consumption_audit']['missing_decisions'])


def test_full_temporal_contract_reaches_production_parameter_closure_without_runtime_rewriting():
    projected = _project(_asset('AST-PDP-PRODUCTION', 'VIDEO', 'PDP_VIDEO'))
    out = _compile(projected)
    selected = out['production_parameter_closure']['selected_parameters']

    assert selected['motion']['subject_motion'].startswith('creator hand lifts the same referenced product once')
    assert selected['motion']['camera_motion'].startswith('locked 10 cm push-in')
    assert selected['motion']['transitions'][1]['type'] == 'continuity cut into resolved hold'
    assert selected['motion']['product_identity_continuity'].startswith('the same referenced package geometry')
    assert selected['motion']['first_frame_logic'].startswith('frame 0 must establish')
    assert selected['motion']['cover_logic'].startswith('cover uses the same frame-0 product identity')
    assert selected['timing']['text_timing'][1]['start_seconds'] == 9.2
    assert selected['audio']['vo_role'].startswith('VO explains only the shopper decision')
    assert selected['audio']['subtitle_role'].startswith('subtitles mirror spoken proof')

    # Runtime may serialize these decisions but must not replace them with defaults or generic animation language.
    assert 'animate this' not in out['model_prompt_en'].lower()
    assert out['production_parameter_closure']['status'] == 'PASS'
