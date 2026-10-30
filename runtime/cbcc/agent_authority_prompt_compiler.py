from __future__ import annotations

from typing import Any

from . import prompt_compiler as legacy
from .model_prompt_semantic_membrane import sanitize_model_prompt, model_prompt_orchestration_leaks

_VISIBLE_STATES = {'HERO_REQUIRED', 'REQUIRED', 'SUPPORTING', 'DETAIL_ONLY'}
_ABSENT_STATES = {'FORBIDDEN', 'ABSENT', 'NOT_APPLICABLE'}
_UNRESOLVED_STATES = {'', 'UNRESOLVED', 'UNRESOLVED_AGENT_DECISION', 'AGENT_DECISION_REQUIRED'}


def _presence_contract(asset: dict[str, Any]) -> dict[str, Any]:
    raw = dict(asset.get('product_presence') or {})
    art = asset.get('asset_art_direction') if isinstance(asset.get('asset_art_direction'), dict) else {}
    if not raw and isinstance(art.get('product_presence'), dict):
        raw = dict(art.get('product_presence') or {})
    state = str(raw.get('planning_state') or raw.get('state') or '').upper()
    if not state:
        state = 'UNRESOLVED_AGENT_DECISION'
    raw['planning_state'] = state
    raw.setdefault('authority', 'HOST_AGENT_ART_DIRECTION' if state not in _UNRESOLVED_STATES else 'AGENT_DECISION_REQUIRED')
    if state in _ABSENT_STATES:
        raw.setdefault('production_state', 'ABSENT')
        raw.setdefault('source_reference_role', 'TRUTH_REFERENCE_ONLY')
    elif state in _VISIBLE_STATES:
        raw.setdefault('production_state', 'PRESENT')
        raw.setdefault('source_reference_role', 'SUBJECT_REFERENCE')
    elif state == 'OPTIONAL':
        raw.setdefault('source_reference_role', 'TRUTH_REFERENCE_ONLY')
    else:
        raw.setdefault('production_state', 'UNRESOLVED')
        raw.setdefault('source_reference_role', 'TRUTH_REFERENCE_ONLY')
    return raw


def _presence_state(presence: dict[str, Any]) -> str:
    return str((presence or {}).get('planning_state') or '').upper()


def _product_visible(presence: dict[str, Any]) -> bool:
    state = _presence_state(presence)
    production_state = str((presence or {}).get('production_state') or '').upper()
    reference_role = str((presence or {}).get('source_reference_role') or '').upper()
    if state in _VISIBLE_STATES:
        return reference_role != 'TRUTH_REFERENCE_ONLY'
    if state == 'OPTIONAL':
        return production_state == 'PRESENT' and reference_role != 'TRUTH_REFERENCE_ONLY'
    return False


def _presence_unresolved(presence: dict[str, Any]) -> bool:
    state = _presence_state(presence)
    if state in _UNRESOLVED_STATES:
        return True
    if state == 'OPTIONAL' and str((presence or {}).get('production_state') or '').upper() not in {'PRESENT', 'ABSENT'}:
        return True
    return False


def _art_direction_required(asset: dict[str, Any]) -> bool:
    value = asset.get('art_direction_required')
    if value is not None:
        return bool(value)
    direction = asset.get('creative_direction') if isinstance(asset.get('creative_direction'), dict) else {}
    return bool(direction.get('require_per_asset_art_direction'))


def _art_direction_missing(asset: dict[str, Any]) -> bool:
    return _art_direction_required(asset) and not isinstance(asset.get('asset_art_direction'), dict)


def _product_rule(asset: dict[str, Any], presence: dict[str, Any], product_fidelity: str) -> str:
    """Design-card / production rule. Semantic membrane decides what part reaches Model Prompt."""
    state = _presence_state(presence)
    role = str(presence.get('source_reference_role') or '').upper()
    if _presence_unresolved(presence):
        return (
            'Agent Art Direction has not resolved product presence. Supplied product/source files are truth references only. '
            'Do not place, generate, composite, silhouette, ghost, corner-signature, podium or otherwise imply a visible product until the Agent authors that decision.'
        )
    if state in _ABSENT_STATES or str(presence.get('production_state') or '').upper() == 'ABSENT':
        return (
            'Product is intentionally absent in this asset. Supplied product/source files may verify Product Truth and identity constraints only. '
            'Do not add a packshot, product signature, silhouette, ghosted product, corner product, podium product or product layer.'
        )
    if role == 'TRUTH_REFERENCE_ONLY':
        return (
            'Source files are Product Truth / identity references only for this asset. They are not a visible subject reference. '
            'Do not place or regenerate the product unless Product Presence separately resolves to PRESENT with a subject-capable reference role.'
        )
    if str(product_fidelity).upper() in {'LOCKED_PIXEL', 'LOCKED_SOURCE_COMPOSITE', 'COMPOSITE'}:
        return (
            'Product is explicitly present and locked-source fidelity is selected. Use supplied product master pixels only as the declared product layer; '
            'do not regenerate, redraw, retype, recolor or reshape that locked layer.'
        )
    return (
        'Product is explicitly present by Agent Art Direction. Supplied files are design/product references rather than immutable pixels. '
        'Redraw, rerender, stylize, illustrate or recompose only within the authored product role and verified Product Truth; do not invent facts or claims.'
    )


def _patch_design_card(card: dict[str, Any], asset: dict[str, Any]) -> dict[str, Any]:
    card = dict(card)
    presence = _presence_contract(asset)
    card['product_presence'] = presence
    card['art_direction_status'] = 'MISSING_AGENT_DECISION' if _art_direction_missing(asset) else (
        'UNRESOLVED_PRODUCT_PRESENCE' if _presence_unresolved(presence) else 'AUTHORED_OR_RESOLVED'
    )
    visible = _product_visible(presence)
    art = asset.get('asset_art_direction') if isinstance(asset.get('asset_art_direction'), dict) else {}

    subject = dict(card.get('subject_action_environment_props') or {})
    authored_subject = art.get('subject') or (art.get('subject_action_environment_props') or {}).get('subject') if isinstance(art.get('subject_action_environment_props'), dict) else art.get('subject')
    if authored_subject:
        subject['subject'] = authored_subject
    elif not visible:
        subject['subject'] = 'Use only the Agent-authored non-product subject, evidence, action or context. Do not place the product in frame.'
    elif not subject.get('subject'):
        subject['subject'] = 'Use the product only in the explicit role defined by Product Presence and the per-asset Agent Art Direction.'
    card['subject_action_environment_props'] = subject

    identity = dict(card.get('product_identity') or {})
    fidelity = str(identity.get('product_fidelity') or asset.get('product_fidelity') or 'REFERENCE_GUIDED')
    identity['visual_presence_state'] = _presence_state(presence)
    identity['production_state'] = presence.get('production_state')
    identity['source_reference_role'] = presence.get('source_reference_role')
    identity['visible_product_required'] = visible
    identity['rule'] = _product_rule(asset, presence, fidelity)
    card['product_identity'] = identity
    return card


def _renderer_layer_plan(card: dict[str, Any], locked_copy: dict[str, Any]) -> list[str]:
    layers: list[str] = []
    subject = card.get('subject_action_environment_props') or {}
    presence = card.get('product_presence') or {}
    if legacy._meaningful(subject.get('environment')):
        layers.append('background_environment')
    if legacy._meaningful(subject.get('human_context')):
        layers.append('human_or_context_if_required')
    if _product_visible(presence):
        role = str(presence.get('source_reference_role') or '').upper()
        layers.append('locked_product_source_layer' if role == 'LOCKED_SOURCE_LAYER' else 'product_subject_or_reference_layer')
    if legacy._meaningful((card.get('information_design') or {}).get('proof_plane')):
        layers.append('evidence_graphics')
    if locked_copy:
        layers.append('locked_typography')
    if legacy._meaningful((card.get('photography_execution') or {}).get('color_management')) or legacy._meaningful((card.get('lighting_material_cmf') or {}).get('post_implications')):
        layers.append('final_color_grade')
    return list(dict.fromkeys(layers))


def _presence_consumption(card: dict[str, Any], prompt_cn: str, prompt_en: str, reference_bound: bool) -> dict[str, Any]:
    presence = card.get('product_presence') or {}
    state = _presence_state(presence)
    locked = str((card.get('product_identity') or {}).get('product_fidelity') or '').upper() in {'LOCKED_PIXEL', 'LOCKED_SOURCE_COMPOSITE', 'COMPOSITE'}
    if state in _ABSENT_STATES or str(presence.get('production_state') or '').upper() == 'ABSENT':
        projected = ('Keep the product absent' in prompt_en) or ('不出现商品主体' in prompt_cn)
    elif _product_visible(presence) and reference_bound:
        if locked:
            projected = ('locked product layer' in prompt_en) or ('锁定商品图层' in prompt_cn)
        else:
            projected = ('attached product reference images' in prompt_en) or ('附带的商品参考图' in prompt_cn)
    else:
        # Product may be visible without an external source binding only when the authored prompt can
        # express its visual role without pretending the model can inspect an unavailable file.
        projected = not _presence_unresolved(presence)
    return {
        'decision': 'product_presence_and_role',
        'required': True,
        'projected': bool(projected),
        'value': presence,
    }


def _reference_binding_ready(source_bindings: list[dict[str, Any]]) -> bool:
    for row in source_bindings:
        if not row.get('visible_subject_binding'):
            continue
        locator = row.get('locator') or {}
        if str(locator.get('kind') or '').upper() in {'PROVIDER_ASSET_HANDLE', 'LOCAL_FILE_PATH'} and locator.get('value'):
            return True
    return False


def compile_asset_prompt(
    asset: dict[str, Any],
    product: dict[str, Any],
    target: dict[str, Any],
    culture: dict[str, Any],
    language_contract: dict[str, Any],
    locale_profiles: dict[str, Any] | None = None,
    photography: dict[str, Any] | None = None,
    strategy_authority: dict[str, Any] | None = None,
    source_product_assets: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    del locale_profiles
    card = legacy._design_card(asset, product, target, culture, language_contract, photography, strategy_authority, source_product_assets)
    card = _patch_design_card(card, asset)
    source_assets = card.get('product_identity', {}).get('source_product_assets') or []
    locked_copy = card.get('information_design', {}).get('locked_visible_copy') or {}
    visible_product = _product_visible(card.get('product_presence') or {})
    locked_fidelity = str(asset.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL', 'LOCKED_SOURCE_COMPOSITE', 'COMPOSITE'}
    real_master_required = bool(visible_product and locked_fidelity)

    machine = legacy._compact({
        'asset_id': card.get('asset_id'),
        'surface': card.get('surface'),
        'production_mode': asset.get('production_mode'),
        'art_direction_status': card.get('art_direction_status'),
        'product_fidelity': asset.get('product_fidelity'),
        'fidelity': {
            'mode': asset.get('product_fidelity'),
            'source_product_asset_ids': [x.get('asset_id') for x in source_assets if isinstance(x, dict) and x.get('asset_id')],
            'real_product_master_required': real_master_required,
            'real_product_master_substitution_allowed': not real_master_required,
            'immutable_identity_fields': ['logo', 'packaging_print', 'product_color_identity', 'geometry', 'proportions'] if real_master_required else ['verified_product_facts', 'approved_claim_facts'],
        },
        'product_presence': card.get('product_presence'),
        'information_assetization': card.get('information_assetization'),
        'composition_camera': card.get('composition_camera'),
        'photography_execution': card.get('photography_execution'),
        'lighting_material_cmf': card.get('lighting_material_cmf'),
        'inclusive_photography': card.get('inclusive_photography'),
        'information_design': card.get('information_design'),
        'surface_contract': card.get('surface_contract'),
        'creative_system': card.get('creative_system'),
        'editable_layer_contract': card.get('editable_layer_contract'),
        'precision_boundaries': card.get('precision_boundaries'),
        'approved_visual_elements': card.get('approved_visual_elements'),
    })

    source_bindings = []
    source_reference_role = str((card.get('product_presence') or {}).get('source_reference_role') or '').upper()
    for row in source_assets:
        if not isinstance(row, dict):
            continue
        handle = row.get('provider_asset_handle')
        path = row.get('path')
        source_bindings.append({
            'asset_id': row.get('asset_id'),
            'role': row.get('role'),
            'usage_role': source_reference_role or 'TRUTH_REFERENCE_ONLY',
            'visible_subject_binding': bool(visible_product and source_reference_role != 'TRUTH_REFERENCE_ONLY'),
            'locator': {
                'kind': 'PROVIDER_ASSET_HANDLE' if handle else ('LOCAL_FILE_PATH' if path else 'UNRESOLVED'),
                'value': handle or path,
            },
            'sha256': row.get('sha256'),
            'ingest_status': row.get('ingest_status'),
            'pixel_lock': bool(row.get('pixel_lock')),
            'allowed_transforms': list(row.get('allowed_transforms') or []),
            'identity_features': list(row.get('identity_features') or []),
        })

    provider_reference_bound = _reference_binding_ready(source_bindings)
    raw_prompt_cn = '\n'.join(legacy._render_lines(card, 'CN')).strip() + '\n'
    raw_prompt_en = '\n'.join(legacy._render_lines(card, 'EN')).strip() + '\n'
    prompt_cn = sanitize_model_prompt(
        raw_prompt_cn,
        language='CN',
        reference_bound=provider_reference_bound,
        locked_source=real_master_required,
    )
    prompt_en = sanitize_model_prompt(
        raw_prompt_en,
        language='EN',
        reference_bound=provider_reference_bound,
        locked_source=real_master_required,
    )

    membrane_cn = model_prompt_orchestration_leaks(prompt_cn)
    membrane_en = model_prompt_orchestration_leaks(prompt_en)
    membrane_issues = membrane_cn + membrane_en
    semantic_membrane = {
        'status': 'PASS' if not membrane_issues else 'FAIL',
        'principle': 'Only model-visible, pixel-changing instructions belong in Model Prompt; source authority, QA and repair routing stay outside.',
        'reference_bound': provider_reference_bound,
        'cn_issues': membrane_cn,
        'en_issues': membrane_en,
    }

    consumption = legacy._prompt_consumption_audit(card, prompt_cn, prompt_en)
    checks = [x for x in list(consumption.get('checks') or []) if x.get('decision') != 'visual_boundaries_editability']
    checks.append(_presence_consumption(card, prompt_cn, prompt_en, provider_reference_bound))
    checks.append({
        'decision': 'model_prompt_semantic_membrane',
        'required': True,
        'projected': not membrane_issues,
        'value': semantic_membrane,
    })
    missing = [x.get('decision') for x in checks if x.get('required') and not x.get('projected')]
    consumption = {
        **consumption,
        'checks': checks,
        'missing_decisions': missing,
        'status': 'PASS' if not missing else 'INCOMPLETE',
        'authority': 'AGENT_ART_DIRECTION_CONSUMPTION',
    }

    decision_missing = _art_direction_missing(asset) or _presence_unresolved(card.get('product_presence') or {})
    reference_missing = bool(visible_product and source_assets and not provider_reference_bound)
    ready_for_generation = not decision_missing and not reference_missing and not membrane_issues
    status = 'AGENT_ART_DIRECTION_REQUIRED' if decision_missing else (
        'PROVIDER_REFERENCE_BINDING_REQUIRED' if reference_missing else (
            'MODEL_PROMPT_ORCHESTRATION_LEAK' if membrane_issues else 'CANONICAL_PROMPT_COMPILED_AGENT_AUTHORITY'
        )
    )
    renderer = {
        'route': asset.get('production_mode'),
        'ready_for_generation': ready_for_generation,
        'blocked_reason': (
            'MISSING_AGENT_ART_DIRECTION_OR_PRODUCT_PRESENCE' if decision_missing else
            'VISIBLE_PRODUCT_REFERENCE_NOT_BOUND_TO_PROVIDER_JOB' if reference_missing else
            'MODEL_PROMPT_ORCHESTRATION_LEAK' if membrane_issues else None
        ),
        'single_asset_single_canvas': True,
        'contact_sheet': False,
        'real_product_master_required': real_master_required,
        'source_product_bindings': source_bindings,
        'deterministic_text_composition': bool(locked_copy),
        'text_policy': {
            'exact_copy_mode': 'DETERMINISTIC_COMPOSITION_AFTER_RENDER',
            'image_model_may_rewrite_locked_copy': False,
            'image_model_may_retype_packaging': False,
            'visible_copy_present': bool(locked_copy),
            'locked_copy': locked_copy,
        },
        'layer_plan': _renderer_layer_plan(card, locked_copy),
        'local_revision_contract': asset.get('editable_layer_contract') or {},
    }

    qa = {
        'decision_answer_visible': asset.get('incremental_information') or asset.get('belief_target'),
        'art_direction_status': card.get('art_direction_status'),
        'product_presence_state': _presence_state(card.get('product_presence') or {}),
        'product_identity': card['product_identity']['rule'],
        'relevant_parameter_trace_complete': consumption.get('status') == 'PASS',
        'same_layout_guard': 'The result must visibly differ from adjacent assets when Agent Art Direction changes composition, carrier, decisive moment or evidence plane.',
        'copy_visual_alignment': card['information_design']['copy_visual_rule'],
        'surface_native': card.get('surface_contract'),
        'culture_locale': card.get('market_locale'),
        'material_truth': card['lighting_material_cmf']['material_truth_rule'],
        'photography_checks': legacy._dynamic_photography_checks(card),
    }

    production_notes_contract = {
        'source_product_bindings': source_bindings,
        'source_truth_and_evidence_authority': 'Resolved upstream from Product Truth / evidence sources; never instruct the generation model to consult Excel or project files.',
        'product_fidelity': asset.get('product_fidelity'),
        'editable_layer_contract': asset.get('editable_layer_contract') or {},
        'copy_render_mode': (asset.get('copy_render_mode') or (card.get('information_design') or {}).get('copy_render_mode')),
        'qa_target_contract_location': 'qa_target_contract',
        'local_revision_contract_location': 'renderer_recipe.local_revision_contract',
    }

    return {
        'status': status,
        'design_card': card,
        'prompt_cn': prompt_cn,
        'prompt_en': prompt_en,
        'deterministic_copy_overlay': locked_copy,
        'parameter_trace': legacy._parameter_trace(card),
        'prompt_consumption_audit': consumption,
        'model_prompt_semantic_membrane': semantic_membrane,
        'machine_visual_contract': machine,
        'renderer_recipe': renderer,
        'production_notes_contract': production_notes_contract,
        'qa_target_contract': qa,
    }


_cn_phrase = legacy._cn_phrase
