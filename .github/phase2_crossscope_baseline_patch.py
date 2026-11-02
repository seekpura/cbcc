from pathlib import Path


def patch_information_audit() -> None:
    path=Path('runtime/cbcc/information_audit_authority.py')
    text=path.read_text(encoding='utf-8')
    old="""    rows=[x for k in ('pending_confirmations','pending_confirmations_overflow','assumption_decision_log') for x in _l(info.get(k)) if isinstance(x,Mapping)]
    if not rows and (_l(info.get('required_missing')) or _l(info.get('assumptions')) or _l(info.get('decision_log'))): issues.append({'code':'FULL_INFORMATION_AUDIT_ROWS_MISSING'})
"""
    new="""    rows=[x for k in ('information_audit_items','pending_confirmations','pending_confirmations_overflow','assumption_decision_log') for x in _l(info.get(k)) if isinstance(x,Mapping)]
    if not rows and (_l(info.get('required_missing')) or _l(info.get('assumptions')) or _l(info.get('decision_log'))): issues.append({'code':'FULL_INFORMATION_AUDIT_ROWS_MISSING'})
"""
    if old not in text:
        raise SystemExit('information audit baseline marker missing')
    path.write_text(text.replace(old,new,1),encoding='utf-8')


def patch_review_analysis() -> None:
    path=Path('runtime/cbcc/review_analysis_authority.py')
    text=path.read_text(encoding='utf-8')
    old="""        'repair_rows':rows,
        'feedback_analysis':base,
        'verification_boundary':{
"""
    new="""        'repair_rows':rows,
        'smallest_repair_status':(
            'TO_VERIFY' if any(r.get('smallest_repair_status')=='TO_VERIFY' for r in rows)
            else ('READY' if rows and all(r.get('smallest_repair_status') in {'READY','NOT_APPLICABLE_POSITIVE_VALUE'} for r in rows) else 'TO_VERIFY')
        ),
        'feedback_analysis':base,
        'verification_boundary':{
"""
    if old not in text:
        raise SystemExit('review analysis baseline marker missing')
    path.write_text(text.replace(old,new,1),encoding='utf-8')


patch_information_audit()
patch_review_analysis()
print('Phase 2 cross-scope baseline patch applied')
