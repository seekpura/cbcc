from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'missing regression-fix target: {label}')
    return text.replace(old, new, 1)


# Auto-discovered research remains actionable but advisory unless the user/agent explicitly marks it blocking.
p=Path('runtime/cbcc/agent_autonomy.py')
text=p.read_text(encoding='utf-8')
text=replace_once(
    text,
    "def _research_requirement(topic: str, domain: str, reason: str, required_for: list[str], *, query: str | None = None, preferred_source: str | None = None) -> dict[str, Any]:\n",
    "def _research_requirement(topic: str, domain: str, reason: str, required_for: list[str], *, query: str | None = None, preferred_source: str | None = None, blocking: bool = False) -> dict[str, Any]:\n",
    'autonomy research blocking signature',
)
text=replace_once(
    text,
    "        'query': query or f'Find current evidence that can materially change the decision about {topic}',\n    }\n",
    "        'query': query or f'Find current evidence that can materially change the decision about {topic}',\n        'blocking': bool(blocking),\n    }\n",
    'autonomy research blocking field',
)
p.write_text(text,encoding='utf-8')

# Research Gate preserves explicit blocking semantics. Legacy/caller-authored requirements default to blocking=True.
p=Path('runtime/cbcc/research.py')
text=p.read_text(encoding='utf-8')
old="""        verified=bool(needed and needed.issubset(source_ids)) or bool(row.get('verified'))
        rec={'requirement_id':rid,'topic':row.get('topic'),'domain':row.get('domain','GENERAL'),'required_for':row.get('required_for',[]),'verified':verified}
        if verified:
            resolved.append(rec); continue
        pending.append(rec)
        domain=str(row.get('domain','GENERAL')).upper()
        actions.append(ResearchAction(
            'RA-'+stable_hash([rid,row.get('topic')])[:10],
            row.get('reason') or f\"Current evidence is needed for {row.get('topic') or rid}\",
            row.get('query') or f\"Verify current authoritative evidence for {row.get('topic') or rid}\",
            row.get('required_for',[]) or ['RESEARCH'],
            preferred_source=row.get('preferred_source') or ('OFFICIAL_CURRENT_SOURCE' if domain in HIGH_RISK_DOMAINS else 'AUTHORITATIVE_CURRENT_SOURCE')
        ).to_dict())
"""
new="""        verified=bool(needed and needed.issubset(source_ids)) or bool(row.get('verified'))
        blocking=bool(row.get('blocking', True))
        rec={'requirement_id':rid,'topic':row.get('topic'),'domain':row.get('domain','GENERAL'),'required_for':row.get('required_for',[]),'verified':verified,'blocking':blocking}
        if verified:
            resolved.append(rec); continue
        pending.append(rec)
        domain=str(row.get('domain','GENERAL')).upper()
        action=ResearchAction(
            'RA-'+stable_hash([rid,row.get('topic')])[:10],
            row.get('reason') or f\"Current evidence is needed for {row.get('topic') or rid}\",
            row.get('query') or f\"Verify current authoritative evidence for {row.get('topic') or rid}\",
            row.get('required_for',[]) or ['RESEARCH'],
            preferred_source=row.get('preferred_source') or ('OFFICIAL_CURRENT_SOURCE' if domain in HIGH_RISK_DOMAINS else 'AUTHORITATIVE_CURRENT_SOURCE')
        ).to_dict()
        action['blocking']=blocking
        actions.append(action)
"""
text=replace_once(text,old,new,'research gate blocking propagation')
text=replace_once(
    text,
    "        'resolved':resolved,'pending':pending,'actions':actions,\n",
    "        'resolved':resolved,'pending':pending,'actions':actions,\n        'blocking_pending':[row for row in pending if row.get('blocking')],\n        'advisory_pending':[row for row in pending if not row.get('blocking')],\n",
    'research gate pending classes',
)
p.write_text(text,encoding='utf-8')

# Compliance only blocks on research explicitly marked blocking; advisory gaps remain visible to the Agent frontier.
p=Path('runtime/cbcc/compliance.py')
text=p.read_text(encoding='utf-8')
text=replace_once(
    text,
    "    research_pending=bool((research_gate or {}).get('pending'))\n    platform_ready=platform_compile.get('status') in {'VERIFIED_FOR_REQUEST','FAMILY_PLANNING_ONLY','PLANNING_ONLY_RESEARCH_PENDING'}\n    return {\n        'status':'HOLD' if issues or research_pending or not platform_ready else 'READY_REVIEW',\n",
    "    research_rows=list((research_gate or {}).get('pending') or [])\n    research_pending=bool(research_rows)\n    research_blocking_pending=any(bool(row.get('blocking', True)) for row in research_rows)\n    platform_ready=platform_compile.get('status') in {'VERIFIED_FOR_REQUEST','FAMILY_PLANNING_ONLY','PLANNING_ONLY_RESEARCH_PENDING'}\n    return {\n        'status':'HOLD' if issues or research_blocking_pending or not platform_ready else 'READY_REVIEW',\n",
    'compliance research blocking status',
)
text=replace_once(
    text,
    "        'research_pending':research_pending,\n",
    "        'research_pending':research_pending,'research_blocking_pending':research_blocking_pending,\n",
    'compliance research metadata',
)
p.write_text(text,encoding='utf-8')

# Upgrade two old static-authority tests to the new v0.6.21 contract instead of restoring deprecated behavior.
p=Path('tests/test_alpha4_creative_research.py')
text=p.read_text(encoding='utf-8')
old="""def test_persuasion_frameworks_are_decision_aids_not_asset_templates():
    out=compile_persuasion_frameworks(['What is it?','Why choose it?'],{'material':'steel'},{'status':'CALCULATED_FROM_INPUTS'})
    assert {'AIDA','FABE','4P'} <= set(out['frameworks'])
    assert 'fixed asset' in out['principle'].lower()
"""
new="""def test_persuasion_frameworks_are_decision_aids_not_asset_templates():
    default_out=compile_persuasion_frameworks(['What is it?','Why choose it?'],{'material':'steel'},{'status':'CALCULATED_FROM_INPUTS'})
    assert default_out['status']=='NOT_REQUESTED' and default_out['frameworks']=={}
    out=compile_persuasion_frameworks(['What is it?','Why choose it?'],{'material':'steel'},{'status':'CALCULATED_FROM_INPUTS'},requested=['AIDA','FABE','4P'])
    assert {'AIDA','FABE','4P'} <= set(out['frameworks'])
    assert 'optional reasoning tools' in out['principle'].lower()
"""
text=replace_once(text,old,new,'legacy persuasion test')
p.write_text(text,encoding='utf-8')

p=Path('tests/test_visual_and_foundation_runtime.py')
text=p.read_text(encoding='utf-8')
old="""def test_photography_contract_has_machine_precision_gate():
    o=validate_photography_contract(good_contract()); assert o['pass'] and o['precision_level']=='SHOOT_READY_MINIMUM'
    bad=good_contract(); del bad['lighting']['key']['modifier']; assert not validate_photography_contract(bad)['pass']
"""
new="""def test_photography_contract_has_machine_precision_gate():
    o=validate_photography_contract(good_contract()); assert o['pass'] and o['precision_level']=='RELEVANCE_READY'
    # Modifier is no longer a universal mandatory field; do not force fake shoot precision when it is not required.
    flexible=good_contract(); del flexible['lighting']['key']['modifier']; assert validate_photography_contract(flexible)['pass']
    # A dimension that is actually active for truth preservation remains a hard contract.
    bad=good_contract(); del bad['color_management']['product_color_fidelity']; assert not validate_photography_contract(bad)['pass']
"""
text=replace_once(text,old,new,'legacy photography precision test')
p.write_text(text,encoding='utf-8')
