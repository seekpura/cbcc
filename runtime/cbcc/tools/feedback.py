from __future__ import annotations
from collections import Counter,defaultdict
from typing import Any

ROUTES={
'PRODUCT_DEFECT':['PRODUCT_STRATEGY','QUALITY'],
'EXPECTATION_GAP':['LISTING','VISUAL','CREATOR'],
'MISUNDERSTANDING':['LISTING','CX','VISUAL'],
'PARAMETER_CONFUSION':['LISTING','SPEC_TABLE'],
'PACKAGE_CONFUSION':['LISTING','PACKAGE_ASSET','CX'],
'USAGE_DIFFICULTY':['USAGE_CONTENT','VIDEO','CX'],
'SIZE':['LISTING','SCALE_ASSET'],
'COMPATIBILITY':['LISTING','ATTRIBUTES','CX'],
'TEXTURE':['PRODUCT_TRUTH','VISUAL','LISTING'],
'LOGISTICS':['FULFILLMENT'],
'CUSTOMER_SERVICE':['CX'],
'OTHER':['REVIEW_REQUIRED'],
'UNCLASSIFIED':['REVIEW_REQUIRED'],
}
FROZEN_BY_ROUTE={
'PRODUCT_STRATEGY':['unrelated listing fields','unrelated visual style'],
'QUALITY':['positioning unless defect changes real value proposition'],
'LISTING':['product truth','unrelated photography/CMF'],
'VISUAL':['product truth','unrelated listing facts'],
'CREATOR':['product truth','core positioning unless evidence points there'],
'CX':['product truth','unrelated hero/creative'],
'PACKAGE_ASSET':['product formulation','unrelated message hierarchy'],
'USAGE_CONTENT':['unrelated offer/pricing'],
'VIDEO':['unrelated static assets'],
'FULFILLMENT':['creative strategy unless expectation communication is also implicated'],
}

def _category(r): return str(r.get('category') or 'UNCLASSIFIED').upper()

def stats(rows):
    rows=list(rows); cats=Counter(_category(r) for r in rows); total=len(rows)
    return {'total':total,'categories':dict(cats),'shares':{k:round(v/total,4) for k,v in cats.items()} if total else {}}


def _matrix(rows, row_key, col_key):
    rvals=sorted({str(x.get(row_key) or 'UNSPECIFIED').upper() for x in rows}); cvals=sorted({str(x.get(col_key) or 'UNSPECIFIED').upper() for x in rows})
    grid=[]
    for rv in rvals:
        row={'row':rv}
        for cv in cvals: row[cv]=sum(1 for x in rows if str(x.get(row_key) or 'UNSPECIFIED').upper()==rv and str(x.get(col_key) or 'UNSPECIFIED').upper()==cv)
        grid.append(row)
    return {'row_dimension':row_key,'column_dimension':col_key,'columns':cvals,'rows':grid}


def defect_vs_communication(issues:list[dict[str,Any]]) -> dict[str,Any]:
    product={'PRODUCT_DEFECT','TEXTURE'}
    communication={'EXPECTATION_GAP','MISUNDERSTANDING','PARAMETER_CONFUSION','PACKAGE_CONFUSION','SIZE','COMPATIBILITY','USAGE_DIFFICULTY'}
    p=sum(x['count'] for x in issues if x['category'] in product)
    c=sum(x['count'] for x in issues if x['category'] in communication)
    return {'product_issue_count':p,'communication_issue_count':c,'primary_direction':'PRODUCT_OR_QUALITY' if p>c else 'CONTENT_EXPECTATION' if c>p else 'MIXED','why':'Product defects and communication misunderstandings require different interventions; changing the product for a listing misunderstanding wastes cost, while copy changes cannot fix a real defect.'}


def revision_actions(issues:list[dict[str,Any]]) -> list[dict[str,Any]]:
    out=[]
    for x in issues[:10]:
        routes=x['routes']; frozen=[]
        for route in routes: frozen += FROZEN_BY_ROUTE.get(route,[])
        out.append({'category':x['category'],'priority_score':x['severity_points'],'routes':routes,'recommended_change':'Update only the routed module(s), then verify the original issue is reduced before broad redesign.','frozen_layers':sorted(set(frozen)),'evidence_examples':x.get('examples',[]),'why':f"{x['count']} classified records with severity score {x['severity_points']} indicate targeted follow-up rather than broad redesign."})
    return out


def analyze_feedback(rows:list[dict[str,Any]]) -> dict[str,Any]:
    rows=list(rows); s=stats(rows); by=defaultdict(lambda:{'count':0,'severity_points':0.0,'examples':[],'sources':Counter()})
    sev_weight={'LOW':1,'MEDIUM':2,'HIGH':3,'CRITICAL':4}
    for r in rows:
        c=_category(r); a=by[c]; a['count']+=1; a['severity_points']+=sev_weight.get(str(r.get('severity') or 'MEDIUM').upper(),2); a['sources'][str(r.get('source') or r.get('channel') or 'UNSPECIFIED').upper()]+=1
        if r.get('text') and len(a['examples'])<3: a['examples'].append(str(r['text'])[:300])
    issues=[]
    for c,a in by.items():
        issues.append({'category':c,'count':a['count'],'share':round(a['count']/len(rows),4) if rows else 0,'severity_points':a['severity_points'],'severity_per_record':round(a['severity_points']/a['count'],4) if a['count'] else 0,'routes':ROUTES.get(c,ROUTES['OTHER']),'source_breakdown':dict(a['sources']),'examples':a['examples']})
    issues.sort(key=lambda x:(x['severity_points'],x['count']),reverse=True)
    source=Counter(str(r.get('source') or r.get('channel') or 'UNSPECIFIED').upper() for r in rows)
    severity=Counter(str(r.get('severity') or 'MEDIUM').upper() for r in rows)
    return {'status':'AGGREGATED_FROM_CLASSIFIED_INPUT','summary':s,'issues':issues,'defect_vs_communication':defect_vs_communication(issues),'revision_actions':revision_actions(issues),'source_matrix':dict(source),'severity_matrix':dict(severity),'category_by_source':_matrix([{**r,'category':_category(r),'source':str(r.get('source') or r.get('channel') or 'UNSPECIFIED')} for r in rows],'category','source'),'category_by_severity':_matrix([{**r,'category':_category(r),'severity':str(r.get('severity') or 'MEDIUM')} for r in rows],'category','severity'),'unclassified_count':s['categories'].get('UNCLASSIFIED',0),'note':'Category assignment is semantic work upstream; this tool aggregates, prioritizes and routes supplied labels deterministically.'}
