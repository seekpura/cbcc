from pathlib import Path

# 1) Restore justified Surface -> asset-family activation only when there is both
# explicit production intent and an authored shopper decision. Surface alone still has no quota authority.
p=Path('runtime/cbcc/decision_authority.py')
s=p.read_text(encoding='utf-8')
old="""    if any(request.get(k) for k in ('source_product_assets','creative_references','creative_directions','photography_contract','visual_strategy','cmf')):
        chosen.append('VISUAL')

    return [family for family in dict.fromkeys(chosen) if family in allowed]
"""
new="""    if any(request.get(k) for k in ('source_product_assets','creative_references','creative_directions','photography_contract','visual_strategy','cmf')):
        chosen.append('VISUAL')

    authored_questions = bool(
        request.get('shopper_questions')
        or scope.get('decision_questions')
        or scope.get('shopper_questions')
        or any((row.get('consumer_question') or row.get('shopper_question') or row.get('question')) for row in _rows(request.get('asset_jobs')))
        or any((row.get('consumer_question') or row.get('shopper_question') or row.get('question')) for row in _rows(request.get('video_jobs')))
    )
    if (request.get('compile_assets') or request.get('production_run')) and authored_questions:
        # Surface is only an execution constraint after a real decision scope exists.  It never creates
        # Listing/Search/Offer work by itself, but it may select the concrete asset family needed to
        # answer an already-authored shopper question.
        surface_asset_family = {
            'GALLERY':'VISUAL', 'LONGFORM':'RICH_CONTENT', 'PDP_VIDEO':'VIDEO',
            'CREATOR':'CREATOR_AFFILIATE', 'LIVE':'LIVE', 'PAID_AD':'PAID',
            'SOCIAL_CONTENT':'SOCIAL', 'STORE_BANNER':'STORE', 'FAQ':'CX', 'CRM':'LIFECYCLE',
        }
        for surface in _strings((request.get('target') or {}).get('surfaces')):
            family = surface_asset_family.get(surface)
            if family:
                chosen.append(family)

    return [family for family in dict.fromkeys(chosen) if family in allowed]
"""
if old not in s:
    raise SystemExit('decision_authority family block not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# 2) Upgrade the v0.6.21 static implementation-name assertion to the current stronger authority.
p=Path('tests/test_v0621_commerce_agent_autonomy.py')
s=p.read_text(encoding='utf-8')
old="""    assert 'derive_content_families(' in source
    assert 'agent_autonomy_plan.json' in source
"""
new="""    assert 'derive_task_content_families(' in source
    assert "['What is it?','Why is it relevant to me?','What evidence supports the choice?','What should happen after purchase?']" not in source
    assert 'agent_autonomy_plan.json' in source
"""
if old not in s:
    raise SystemExit('v0621 compiler assertion block not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# 3) Lock the compatibility boundary in the new v0.6.25 tests.
p=Path('tests/test_v0625_decision_question_authority.py')
s=p.read_text(encoding='utf-8')
addition="""

def test_authored_questions_plus_compile_assets_can_activate_requested_asset_surfaces():
    req=_request(
        compile_assets=True,
        shopper_questions=['What product proof must the shopper see?'],
        target={
            'market':'MY','jurisdiction':'MY','platform_family':'test_platform','site':'TEST',
            'primary_locale':'en-MY','visible_copy_locales':['en-MY'],
            'surfaces':['PDP','GALLERY','PDP_VIDEO','CREATOR','FAQ']
        },
    )
    families=derive_task_content_families(req,{},available_families=AVAILABLE)
    assert families==['VISUAL','VIDEO','CREATOR_AFFILIATE','CX']
    assert 'LISTING' not in families and 'OFFER_PROMOTION' not in families and 'SEARCH' not in families
"""
if 'test_authored_questions_plus_compile_assets_can_activate_requested_asset_surfaces' not in s:
    s += addition
p.write_text(s,encoding='utf-8')
print('v0.6.25 regression compatibility patch applied')
