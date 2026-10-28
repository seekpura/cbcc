from __future__ import annotations
from typing import Any

VALID_CONFIDENCE={'VERIFIED','LIKELY','ASSUMPTION','PENDING'}

def compile_culture_context(data:dict[str,Any]|None)->dict[str,Any]:
    data=data or {}
    statements=[]; issues=[]
    raw_statements=data.get('statements',[]) or []
    if not isinstance(raw_statements,list):
        raw_statements=[raw_statements]
    for row in raw_statements:
        if not isinstance(row,dict):
            row={'statement':str(row),'status':'ASSUMPTION'}
        status=str(row.get('status','PENDING')).upper()
        if status not in VALID_CONFIDENCE:
            issues.append(f"invalid culture status: {status}")
            status='PENDING'
        statements.append({
            'statement':row.get('statement',''), 'status':status,
            'confidence':row.get('confidence'), 'source_ids':row.get('source_ids',[]),
            'implications':row.get('implications',[])
        })
    dims=data.get('intersectionality',{}) or {}
    if isinstance(dims,dict):
        normalized={k:list(v) if isinstance(v,list) else ([v] if v not in (None,'') else []) for k,v in dims.items()}
    elif isinstance(dims,list):
        normalized={'intersectionality_notes':[str(v) for v in dims if v not in (None,'')]}
        issues.append('intersectionality supplied as list; normalized to intersectionality_notes')
    else:
        normalized={'intersectionality_notes':[str(dims)]} if dims not in (None,'') else {}
        if normalized:
            issues.append('intersectionality supplied as scalar; normalized to intersectionality_notes')
    race_ethnicity=data.get('race_ethnicity',{}) or {}
    if not isinstance(race_ethnicity,dict):
        race_ethnicity={'groups':[str(race_ethnicity)],'status':'ASSUMPTION','relevance':['context only; no deterministic behavior inference']}
        issues.append('race_ethnicity supplied as scalar/list; normalized to structured context')
    groups=race_ethnicity.get('groups',[]) or []
    if not isinstance(groups,list): groups=[groups]
    race_context={
        'groups':[str(v) for v in groups if v not in (None,'')],
        'source_ids':race_ethnicity.get('source_ids',[]),
        'status':str(race_ethnicity.get('status','PENDING')).upper(),
        'relevance':race_ethnicity.get('relevance',[]),
        'behavior_inference_allowed':False
    }
    casting=data.get('casting',{}) or {}
    if not isinstance(casting,dict):
        casting={'notes':list(casting) if isinstance(casting,list) else [casting]}
        issues.append('casting supplied in non-object form; normalized to notes')
    visual=data.get('visual_implications',[]) or []
    copy=data.get('copy_implications',[]) or []
    return {
        'status':'COMPILED_FROM_SUPPLIED_EVIDENCE' if (statements or normalized or casting or visual or copy) else 'NO_CULTURE_INPUT',
        'statements':statements,
        'intersectionality':normalized,
        'race_ethnicity':race_context,
        'casting_constraints':casting,
        'visual_implications':visual,
        'copy_implications':copy,
        'issues':issues,
        'principle':'Identity dimensions are context signals, not automatic behavior predictions.'
    }
