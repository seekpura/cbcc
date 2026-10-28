from pathlib import Path

p=Path('runtime/cbcc/compliance.py')
text=p.read_text(encoding='utf-8')
old="""    approved={
        c.get('claim_id') for c in claims
        if c.get('claim_id')
        and str(c.get('evidence_grade') or c.get('evidence_level') or '').upper() in {'A','B'}
        and str(c.get('publication_status') or '').upper() not in {'BLOCKED','SOFT_ONLY_NO_HARD_CLAIM'}
    }
"""
new="""    # Asset-reference routing and publication evidence are separate authorities.
    # A raw/direct caller may explicitly mark a known claim APPROVED before Claim Authority normalization;
    # that makes the claim a known reference target, but missing/weak evidence still creates claim_issues
    # and keeps overall Compliance on HOLD. Explicit C-grade or blocked claims are never route-authorized.
    route_authorized={
        c.get('claim_id') for c in claims
        if c.get('claim_id')
        and str(c.get('publication_status') or '').upper() not in {'BLOCKED','SOFT_ONLY_NO_HARD_CLAIM'}
        and str(c.get('status') or '').upper() not in {'BLOCKED','PROHIBITED','REJECTED','INVALID'}
        and (
            str(c.get('evidence_grade') or c.get('evidence_level') or '').upper() in {'A','B'}
            or (
                not str(c.get('evidence_grade') or c.get('evidence_level') or '').upper()
                and str(c.get('status') or '').upper() in {'APPROVED','VERIFIED','ACTIVE'}
            )
        )
    }
"""
if old not in text:
    raise SystemExit('compliance route-authority block not found')
text=text.replace(old,new,1)
text=text.replace("unknown=[x for x in a.get('claim_ids',[]) if x not in approved]","unknown=[x for x in a.get('claim_ids',[]) if x not in route_authorized]",1)
p.write_text(text,encoding='utf-8')
print('compliance route authority separated from evidence authority')
