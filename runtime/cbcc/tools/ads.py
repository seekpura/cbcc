from __future__ import annotations
from typing import Any
from .economics import contribution_before_ads, break_even_roas, allowable_cpa, allowable_cpc


def _rate(n,d): return None if d in (None,0) else float(n)/float(d)


def ad_metrics(data:dict[str,Any]) -> dict[str,Any]:
    imp=float(data.get('impressions') or 0); clicks=float(data.get('clicks') or 0); orders=float(data.get('orders') or 0)
    spend=float(data.get('spend') or 0); revenue=float(data.get('revenue') or 0)
    return {'impressions':imp,'clicks':clicks,'orders':orders,'spend':spend,'revenue':revenue,
            'ctr':_rate(clicks,imp),'cvr':_rate(orders,clicks),'cpc':_rate(spend,clicks),'cpa':_rate(spend,orders),
            'roas':_rate(revenue,spend),'acos':_rate(spend,revenue)}


def diagnose(metrics:dict[str,Any], thresholds:dict[str,Any]|None=None) -> list[dict[str,str]]:
    """Deterministic symptom routing using caller-provided thresholds only."""
    t=thresholds or {}; out=[]
    def low(name): return t.get(f'min_{name}') is not None and metrics.get(name) is not None and metrics[name] < float(t[f'min_{name}'])
    if low('impressions'):
        out.append({'symptom':'LOW_IMPRESSIONS','route':'ELIGIBILITY_TRAFFIC','next_check':'eligibility / indexing / keyword coverage / bid / inventory / budget pacing'})
    if low('ctr'):
        out.append({'symptom':'LOW_CTR','route':'CLICK_PACKAGE','next_check':'hero / thumbnail / title / first proposition / audience-message match'})
    if low('cvr'):
        out.append({'symptom':'LOW_CVR','route':'PDP_CONVERSION','next_check':'fit / proof / offer / trust / price / objections / traffic quality'})
    if t.get('max_cpc') is not None and metrics.get('cpc') is not None and metrics['cpc'] > float(t['max_cpc']):
        out.append({'symptom':'CPC_ABOVE_TARGET','route':'MEDIA_EFFICIENCY','next_check':'bid / auction / query mix / placement / click quality'})
    if t.get('min_roas') is not None and metrics.get('roas') is not None and metrics['roas'] < float(t['min_roas']):
        out.append({'symptom':'ROAS_BELOW_TARGET','route':'ECONOMICS_OR_MEDIA','next_check':'break-even economics first, then traffic quality / bid / PDP conversion'})
    return out


def economics_guard(price:float,costs:dict[str,Any],conversion_rate:float|None=None,target_contribution:float=0) -> dict[str,Any]:
    cba=contribution_before_ads(price,costs)
    return {'contribution_before_ads':cba,'break_even_roas':break_even_roas(price,cba) if cba is not None else None,
            'allowable_cpa':allowable_cpa(price,costs,target_contribution),'allowable_cpc':allowable_cpc(price,costs,conversion_rate,target_contribution) if conversion_rate is not None else None,
            'target_contribution':target_contribution}


def diagnostic_tree(metrics:dict[str,Any], economics:dict[str,Any]|None, thresholds:dict[str,Any]|None=None)->dict[str,Any]:
    t=thresholds or {}; nodes=[]
    nodes.append({'node':'ELIGIBILITY_TRAFFIC','question':'Is the campaign receiving enough eligible impressions?','signal':metrics.get('impressions'),'route':'SEARCH / FEED / INVENTORY / BID' if t.get('min_impressions') is not None and metrics.get('impressions',0)<t['min_impressions'] else 'NEXT','why':'Without eligible reach, creative/PDP diagnosis is premature.'})
    nodes.append({'node':'CLICK_PACKAGE','question':'Do title/hero/proposition earn the click from eligible impressions?','signal':metrics.get('ctr'),'route':'LISTING HERO / TITLE / THUMBNAIL / MESSAGE' if t.get('min_ctr') is not None and metrics.get('ctr') is not None and metrics['ctr']<t['min_ctr'] else 'NEXT','why':'CTR is primarily a first-impression symptom, not proof of PDP quality.'})
    nodes.append({'node':'PDP_CONVERSION','question':'Does the offer convert qualified clicks?','signal':metrics.get('cvr'),'route':'FIT / PROOF / PRICE / TRUST / OBJECTIONS / TRAFFIC QUALITY' if t.get('min_cvr') is not None and metrics.get('cvr') is not None and metrics['cvr']<t['min_cvr'] else 'NEXT','why':'CVR reflects the full post-click decision environment; do not attribute it to creative alone.'})
    if economics:
        roas=metrics.get('roas'); be=economics.get('break_even_roas'); cpa=metrics.get('cpa'); allowable=economics.get('allowable_cpa')
        nodes.append({'node':'ECONOMICS','question':'Is media performance above the actual economic floor?','signal':{'roas':roas,'break_even_roas':be,'cpa':cpa,'allowable_cpa':allowable},'route':'BUDGET / BID / OFFER / MARGIN' if ((roas is not None and be is not None and roas<be) or (cpa is not None and allowable is not None and cpa>allowable)) else 'ECONOMICALLY_VIABLE_OR_UNRESOLVED','why':'A campaign can have attractive CTR/CVR and still destroy contribution if the economics are wrong.'})
    return {'nodes':nodes,'principle':'Diagnose in causal order: eligibility/traffic → click package → PDP conversion → economics. Do not jump to creative changes when the binding constraint is margin, eligibility or traffic quality.'}


def budget_headroom(metrics:dict[str,Any], economics:dict[str,Any]|None)->dict[str,Any]:
    if not economics: return {'status':'ECONOMICS_REQUIRED'}
    cpa=economics.get('allowable_cpa'); current=metrics.get('cpa')
    if cpa is None or current is None: return {'status':'INSUFFICIENT_DATA','allowable_cpa':cpa,'current_cpa':current}
    return {'status':'CALCULATED','allowable_cpa':cpa,'current_cpa':current,'cpa_headroom':round(cpa-current,6),'headroom_ratio':round((cpa-current)/cpa,6) if cpa else None,'scale_signal':'HEADROOM' if current<cpa else 'NO_HEADROOM'}


def budget_bid_hypotheses(metrics:dict[str,Any], economics:dict[str,Any]|None, diagnosis:list[dict[str,Any]])->list[dict[str,Any]]:
    routes={d.get('route') for d in diagnosis}; out=[]
    if 'ELIGIBILITY_TRAFFIC' in routes:
        out.append({'hypothesis':'TRAFFIC_CONSTRAINT','action':'Before increasing creative volume, verify eligibility, query/placement coverage, inventory and bid/budget pacing.','why':'Low reach prevents reliable downstream creative/PDP conclusions.','measurement':'impressions/reach after isolated traffic change; hold creative constant where possible.'})
    if 'CLICK_PACKAGE' in routes:
        out.append({'hypothesis':'CLICK_PACKAGE_CONSTRAINT','action':'Test one first-impression variable at a time: hero/thumbnail, title or primary proposition.','why':'Low CTR points to the impression→click transition, but changing multiple elements destroys attribution.','measurement':'CTR + qualified-click CVR, not CTR alone.'})
    if 'PDP_CONVERSION' in routes:
        out.append({'hypothesis':'PDP_OR_TRAFFIC_QUALITY_CONSTRAINT','action':'Audit message-match, price/offer, proof, objections and traffic intent before scaling spend.','why':'Qualified click quality and PDP decision architecture jointly drive CVR.','measurement':'CVR / contribution per click / objection themes.'})
    bh=budget_headroom(metrics,economics)
    if bh.get('scale_signal')=='HEADROOM' and not diagnosis:
        out.append({'hypothesis':'ECONOMIC_HEADROOM','action':'Run controlled budget expansion while monitoring marginal CPA/ROAS, inventory and incrementality.','why':'Current average CPA is below the supplied economic ceiling, but marginal performance can worsen as spend expands.','measurement':'marginal CPA/ROAS + contribution, not only blended average.'})
    return out


def incrementality_readiness(data:dict[str,Any]) -> dict[str,Any]:
    signals={k:data.get(k) for k in ['baseline_orders','baseline_revenue','holdout_orders','holdout_revenue','organic_orders','new_customer_orders'] if data.get(k) is not None}
    return {'status':'EVIDENCE_AVAILABLE' if signals else 'NOT_ESTABLISHED','signals':signals,'next_step':'Use holdout/geo/time-series or another defensible counterfactual before claiming incremental sales from ads.' if not signals else 'Interpret supplied counterfactual evidence separately from platform-attributed conversions.','why':'Platform attribution measures credited conversions, not necessarily conversions caused by the ads.'}


def analyze_ads(data:dict[str,Any],price:float|None=None,costs:dict[str,Any]|None=None,thresholds:dict[str,Any]|None=None,target_contribution:float=0) -> dict[str,Any]:
    m=ad_metrics(data); e=None
    if price is not None and costs is not None: e=economics_guard(price,costs,m.get('cvr'),target_contribution)
    merged=dict(thresholds or {})
    if e and e.get('break_even_roas') is not None and merged.get('min_roas') is None: merged['min_roas']=e['break_even_roas']
    if e and e.get('allowable_cpc') is not None and merged.get('max_cpc') is None: merged['max_cpc']=e['allowable_cpc']
    diag=diagnose(m,merged)
    return {'status':'CALCULATED_FROM_INPUTS','metrics':m,'economics':e,'diagnosis':diag,'diagnostic_tree':diagnostic_tree(m,e,merged),'budget_headroom':budget_headroom(m,e),'budget_bid_hypotheses':budget_bid_hypotheses(m,e,diag),'incrementality':incrementality_readiness(data),'thresholds_used':merged,'decision_note':'Use economics-aware causal diagnosis before changing bids or creative; thresholds come only from supplied goals, verified benchmarks, baseline or break-even math.'}


def analyze_ad_portfolio(rows:list[dict[str,Any]], price:float|None=None, costs:dict[str,Any]|None=None, thresholds:dict[str,Any]|None=None)->dict[str,Any]:
    """Analyze multiple campaigns/ad groups without inventing benchmarks."""
    rows=list(rows or [])
    total={'impressions':0.0,'clicks':0.0,'orders':0.0,'spend':0.0,'revenue':0.0}
    details=[]
    for i,r in enumerate(rows):
        raw=r.get('ad_data') if isinstance(r.get('ad_data'),dict) else r
        for k in total: total[k]+=float(raw.get(k) or 0)
        x=analyze_ads(raw, r.get('price',price), r.get('costs',costs), r.get('thresholds',thresholds),r.get('target_contribution',0))
        details.append({'id':r.get('campaign_id') or r.get('ad_group_id') or f'ROW-{i+1}','name':r.get('name'),'objective':r.get('objective'),'audience':r.get('audience'),'creative_id':r.get('creative_id'),'analysis':x})
    agg=analyze_ads(total,price,costs,thresholds)
    scale=[]; diagnose_rows=[]
    for d in details:
        a=d['analysis']; bh=a.get('budget_headroom') or {}; di=a.get('diagnosis') or []
        if bh.get('scale_signal')=='HEADROOM' and not di:
            scale.append({'id':d['id'],'why':'Current CPA is below the supplied economic ceiling and no caller-supplied diagnostic threshold is failing; still validate marginal performance, inventory and incrementality.'})
        if di: diagnose_rows.append({'id':d['id'],'diagnosis':di,'hypotheses':a.get('budget_bid_hypotheses',[])})
    return {'status':'PORTFOLIO_CALCULATED','aggregate':agg,'rows':details,'scale_candidates':scale,'diagnosis_required':diagnose_rows,'portfolio_learning_map':[{'id':d['id'],'creative_id':d.get('creative_id'),'objective':d.get('objective'),'audience':d.get('audience'),'metrics':d['analysis'].get('metrics'),'routes':[x.get('route') for x in d['analysis'].get('diagnosis',[])]} for d in details],'decision_note':'Portfolio analysis compares campaigns against supplied goals/economics only; it does not invent industry CTR/CVR benchmarks.'}
