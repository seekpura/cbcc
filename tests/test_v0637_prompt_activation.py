from __future__ import annotations

from runtime.cbcc.strategy_sources import compile_strategy_reasoning_context


def test_core_commercial_authorities_are_selected_into_reasoning_context():
    ctx=compile_strategy_reasoning_context({'target':{'platform_family':'tiktok_shop','surfaces':['GALLERY','PDP_VIDEO']},'video_jobs':[{'family':'VIDEO','surface':'PDP_VIDEO'}]})
    ids={p.get('id') for p in ctx.get('selected_prompts') or []}
    assert 'PROMPT-SEVEN-TOOLS' in ids
    assert 'PROMPT-COMMERCIAL-INTEGRATED-VISUAL' in ids
    assert 'PROMPT-COMMERCIAL-VIDEO' in ids
    assert 'PROMPT-OPERATOR-EXECUTION-DENSITY' in ids


def test_video_authority_is_not_forced_when_project_has_no_video_surface_or_job():
    ctx=compile_strategy_reasoning_context({'target':{'platform_family':'amazon','surfaces':['GALLERY']}})
    ids={p.get('id') for p in ctx.get('selected_prompts') or []}
    assert 'PROMPT-COMMERCIAL-INTEGRATED-VISUAL' in ids
    assert 'PROMPT-OPERATOR-EXECUTION-DENSITY' in ids
    assert 'PROMPT-COMMERCIAL-VIDEO' not in ids
