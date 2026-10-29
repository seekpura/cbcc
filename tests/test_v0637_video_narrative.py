from __future__ import annotations

from runtime.cbcc.video_creator import build_video_creator_plan


def test_size_fit_video_uses_decision_derived_narrative_not_legacy_five_beat():
    objects=[{'object_id':'CO-VIDEO','family':'VIDEO','surface':'PDP_VIDEO','curation_job':'Resolve size and fit'}]
    assets=[{'asset_id':'AST-SIZE','family':'VIDEO','surface':'PDP_VIDEO','consumer_question':'Will this fit in my carry-on bag?','strategic_job':'Make dimensions and real fit obvious','incremental_information':'verified dimensions 23 × 13 × 16 cm','decision_intent':'FIT_SIZE_COMPATIBILITY'}]
    out=build_video_creator_plan('P1',objects,['Will this fit in my carry-on bag?'],{'primary_locale':'en-MY'},assets=assets)
    row=out['assets'][0]
    assert row['fixed_five_beat_template'] is False
    assert row['narrative_source']=='DECISION_DERIVED_RUNTIME_FALLBACK'
    assert row['narrative_carrier']=='FIT_SCALE_PROOF'
    names=[s['shot'] for s in row['shots']]
    assert names==['DECISION_QUESTION','MEASURED_PROOF','USE_CONTEXT','DECISION_CLOSE']
    assert 'NATIVE_HOOK' not in names
    assert 'CTA_HANDOFF' not in names


def test_explicit_agent_shots_remain_authoritative():
    jobs=[{'family':'VIDEO','surface':'PDP_VIDEO','shopper_question':'How does it open?','duration_seconds':10,'narrative_carrier':'TACTILE_DEMO','shots':[{'shot':'MACRO_OPEN','seconds':4,'job':'Show zipper movement'},{'shot':'HAND_LOAD','seconds':6,'job':'Show actual loading'}]}]
    out=build_video_creator_plan('P2',[],[],{'primary_locale':'en-MY'},video_jobs=jobs)
    row=out['assets'][0]
    assert row['narrative_source']=='EXPLICIT_AGENT_VIDEO_JOB'
    assert row['narrative_carrier']=='TACTILE_DEMO'
    assert [s['shot'] for s in row['shots']]==['MACRO_OPEN','HAND_LOAD']
    assert row['fixed_five_beat_template'] is False
