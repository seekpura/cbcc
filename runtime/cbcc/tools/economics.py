from __future__ import annotations
from typing import Any


def _f(v, default=0.0):
    try:
        return default if v in (None,'') else float(v)
    except (TypeError, ValueError):
        return default


def fee_amount(component: Any, price: float, base: float | None = None) -> float:
    """Resolve a fee component without guessing its unit.

    Numbers are fixed amounts for backward compatibility.
    Dict form: {'type':'fixed','value':X} or {'type':'rate','value':0.12}.
    """
    if component is None:
        raise ValueError('missing fee component')
    if isinstance(component,(int,float,str)):
        return float(component)
    typ=component.get('type','fixed'); val=float(component.get('value',0))
    if typ=='fixed': return val
    if typ=='rate': return (price if base is None else base)*val
    raise ValueError(f'unsupported fee type: {typ}')


def contribution_waterfall(price: float, components: dict[str, Any], ad_cost_override: float | None = None) -> dict[str, Any]:
    price=float(price)
    resolved={}; missing=[]
    for name, comp in components.items():
        if comp is None:
            missing.append(name); continue
        resolved[name]=fee_amount(comp,price)
    if missing:
        return {'status':'INSUFFICIENT_DATA','missing':missing,'price':price,'components':resolved}
    if ad_cost_override is not None:
        resolved['ad_cost']=float(ad_cost_override)
    total=sum(resolved.values()); contribution=price-total
    return {
        'status':'CALCULATED_FROM_INPUTS','price':price,'components':{k:round(v,6) for k,v in resolved.items()},
        'total_cost':round(total,6),'contribution':round(contribution,6),'contribution_margin':round(contribution/price,6) if price else None,
        'waterfall':[{'name':'revenue','amount':round(price,6)}]+[{'name':k,'amount':round(-v,6)} for k,v in resolved.items()]+[{'name':'contribution','amount':round(contribution,6)}]
    }


def contribution_before_ads(price: float, costs: dict[str,Any]) -> float | None:
    no_ads=dict(costs); no_ads.pop('ad_cost',None)
    required=['landed_cost','platform_fee','fulfillment','affiliate_commission','tax','refund_allowance']
    if any(no_ads.get(k) is None for k in required): return None
    out=contribution_waterfall(price,{k:no_ads[k] for k in required})
    return out.get('contribution')


def break_even_roas(price, contribution_before_ads_value):
    c=float(contribution_before_ads_value)
    if c<=0: return None
    return round(float(price)/c,6)


def allowable_cpa(price:float,costs:dict[str,Any],target_contribution:float=0.0):
    c=contribution_before_ads(price,costs)
    if c is None: return None
    return round(max(0.0,c-float(target_contribution)),6)


def allowable_cpc(price:float,costs:dict[str,Any],conversion_rate:float,target_contribution:float=0.0):
    cpa=allowable_cpa(price,costs,target_contribution)
    if cpa is None or conversion_rate is None: return None
    return round(cpa*float(conversion_rate),6)


def coupon_headroom(price:float,costs:dict[str,Any],minimum_contribution:float=0.0):
    c=contribution_before_ads(price,costs)
    if c is None: return None
    ad=fee_amount(costs.get('ad_cost',0),float(price)) if costs.get('ad_cost') is not None else 0
    return round(max(0.0,c-ad-float(minimum_contribution)),6)


def affiliate_rate_ceiling(price:float,costs:dict[str,Any],minimum_contribution:float=0.0):
    if not price: return None
    base=dict(costs); base['affiliate_commission']=0
    head=coupon_headroom(price,base,minimum_contribution)
    return None if head is None else round(head/float(price),6)


def shared_growth_budget(price:float,costs:dict[str,Any],minimum_contribution:float=0.0) -> dict[str,Any]:
    """Show the common pool consumed by discount, affiliate and media."""
    required=['landed_cost','platform_fee','fulfillment','tax','refund_allowance']
    if any(costs.get(k) is None for k in required):
        return {'status':'INSUFFICIENT_DATA','missing':[k for k in required if costs.get(k) is None]}
    base_components={k:costs[k] for k in required}
    calc=contribution_waterfall(price,base_components)
    pool=(calc.get('contribution') or 0)-float(minimum_contribution)
    affiliate=fee_amount(costs.get('affiliate_commission',0),price) if costs.get('affiliate_commission') is not None else 0
    ad=fee_amount(costs.get('ad_cost',0),price) if costs.get('ad_cost') is not None else 0
    coupon=_f(costs.get('coupon_discount'),0)
    used=affiliate+ad+coupon
    return {
        'status':'CALCULATED_FROM_INPUTS','minimum_contribution':round(float(minimum_contribution),6),
        'pool_before_coupon_affiliate_ads':round(max(0.0,pool),6),
        'current_coupon_discount':round(coupon,6),'current_affiliate_cost':round(affiliate,6),'current_ad_cost':round(ad,6),
        'current_growth_spend':round(used,6),'remaining_growth_pool':round(pool-used,6),
        'decision_rule':'Coupon/discount, affiliate/creator payout and paid media draw from one contribution pool. Increasing one reduces room for the others unless price/cost/mix changes.'
    }


def unit_economics(price, costs:dict, target_contribution:float=0.0):
    required=['landed_cost','platform_fee','fulfillment','affiliate_commission','ad_cost','tax','refund_allowance']
    missing=[k for k in required if costs.get(k) is None]
    if missing: return {'status':'INSUFFICIENT_DATA','missing':missing,'contribution':None,'price':float(price) if price not in (None,'') else price}
    price=float(price)
    out=contribution_waterfall(price,{k:costs[k] for k in required})
    cba=contribution_before_ads(price,costs)
    base=dict(costs); base['affiliate_commission']=0; base['ad_cost']=0
    base_calc=contribution_waterfall(price,{k:base[k] for k in required})
    growth_pool=base_calc.get('contribution') if base_calc.get('status')=='CALCULATED_FROM_INPUTS' else None
    affiliate=fee_amount(costs['affiliate_commission'],price); ad=fee_amount(costs['ad_cost'],price)
    out.update({
        'target_contribution':round(float(target_contribution),6),
        'contribution_before_ads':cba,
        'break_even_roas':break_even_roas(price,cba) if cba is not None else None,
        'allowable_cpa_zero_contribution':allowable_cpa(price,costs,0),
        'allowable_cpa_target_contribution':allowable_cpa(price,costs,target_contribution),
        'coupon_headroom_zero_contribution':coupon_headroom(price,costs,0),
        'coupon_headroom_target_contribution':coupon_headroom(price,costs,target_contribution),
        'affiliate_rate_ceiling_zero_contribution':affiliate_rate_ceiling(price,costs,0),
        'affiliate_rate_ceiling_target_contribution':affiliate_rate_ceiling(price,costs,target_contribution),
        'growth_budget_pool_before_affiliate_and_ads':growth_pool,
        'current_growth_spend':round(affiliate+ad,6),
        'growth_pool_remaining_after_affiliate_and_ads':None if growth_pool is None else round(growth_pool-affiliate-ad,6),
        'shared_growth_budget':shared_growth_budget(price,costs,target_contribution),
        'decision_note':'Coupon/discount, affiliate/creator payout and paid media consume the same unit contribution pool; plan them together rather than as independent percentages.'
    })
    return out


def _scenario_costs_with_discount(price:float,costs:dict[str,Any],discount:float):
    # Treat discount as revenue reduction, not a cost-line rewrite, because rate fees may move with selling price.
    return max(0.0,float(price)-float(discount)), dict(costs)


def sensitivity_matrix(price:float,costs:dict[str,Any], target_contribution:float=0.0, discount_steps:list[float]|None=None, affiliate_rate_steps:list[float]|None=None, ad_cost_steps:list[float]|None=None) -> list[dict[str,Any]]:
    """One-variable sensitivity around the supplied base economics."""
    discount_steps=discount_steps if discount_steps is not None else [0, round(price*0.05,6), round(price*0.10,6)]
    affiliate_rate_steps=affiliate_rate_steps if affiliate_rate_steps is not None else [0.0,0.1,0.2]
    base_ad=fee_amount(costs.get('ad_cost',0),price) if costs.get('ad_cost') is not None else 0
    ad_cost_steps=ad_cost_steps if ad_cost_steps is not None else sorted(set([0.0,round(base_ad,6),round(base_ad*1.5,6)]))
    out=[]
    for d in discount_steps:
        p,c=_scenario_costs_with_discount(price,costs,d); calc=unit_economics(p,c,target_contribution)
        out.append({'variable':'coupon_discount','value':d,'effective_price':p,'contribution':calc.get('contribution'),'margin':calc.get('contribution_margin'),'break_even_roas':calc.get('break_even_roas'),'allowable_cpa':calc.get('allowable_cpa_target_contribution')})
    for rate in affiliate_rate_steps:
        c=dict(costs); c['affiliate_commission']={'type':'rate','value':rate}; calc=unit_economics(price,c,target_contribution)
        out.append({'variable':'affiliate_rate','value':rate,'effective_price':price,'contribution':calc.get('contribution'),'margin':calc.get('contribution_margin'),'break_even_roas':calc.get('break_even_roas'),'allowable_cpa':calc.get('allowable_cpa_target_contribution')})
    for ad in ad_cost_steps:
        c=dict(costs); c['ad_cost']={'type':'fixed','value':ad}; calc=unit_economics(price,c,target_contribution)
        out.append({'variable':'ad_cost_per_order','value':ad,'effective_price':price,'contribution':calc.get('contribution'),'margin':calc.get('contribution_margin'),'break_even_roas':calc.get('break_even_roas'),'allowable_cpa':calc.get('allowable_cpa_target_contribution')})
    return out


def scenario_matrix(scenarios:list[dict[str,Any]]) -> list[dict[str,Any]]:
    out=[]
    for s in scenarios:
        row={'scenario_id':s.get('scenario_id') or f'S{len(out)+1}','sku':s.get('sku'),'price':s.get('price'),'configuration':s.get('configuration'),'bundle':s.get('bundle'),'channel':s.get('channel'),'buyer_job':s.get('buyer_job'),'target_segment':s.get('target_segment'),'lifecycle_stage':s.get('lifecycle_stage'),'offer_type':s.get('offer_type'),'product_family':s.get('product_family'),'unit_count':s.get('unit_count'),'retention':s.get('retention'),'trial':s.get('trial'),'premium':s.get('premium')}
        calc=unit_economics(s['price'],s.get('costs',{}),s.get('minimum_contribution',s.get('target_contribution',0)))
        row.update(calc)
        if calc.get('status')=='CALCULATED_FROM_INPUTS':
            cba=contribution_before_ads(s['price'],s['costs']); row['contribution_before_ads']=cba
            row['break_even_roas']=break_even_roas(s['price'],cba) if cba is not None else None
            row['coupon_headroom']=coupon_headroom(s['price'],s['costs'],s.get('minimum_contribution',0))
            row['affiliate_rate_ceiling']=affiliate_rate_ceiling(s['price'],s['costs'],s.get('minimum_contribution',0))
            if s.get('include_sensitivity'):
                row['sensitivity']=sensitivity_matrix(s['price'],s['costs'],s.get('minimum_contribution',0),s.get('discount_steps'),s.get('affiliate_rate_steps'),s.get('ad_cost_steps'))
        out.append(row)
    return out


def price_ladder(scenarios:list[dict[str,Any]]) -> list[dict[str,Any]]:
    rows=scenario_matrix(scenarios)
    valid=[r for r in rows if r.get('status')=='CALCULATED_FROM_INPUTS' and r.get('price') is not None]
    valid.sort(key=lambda r:float(r['price']))
    for i,r in enumerate(valid):
        r['price_rank']=i+1
        r['price_gap_from_previous']=None if i==0 else round(float(r['price'])-float(valid[i-1]['price']),6)
        r['price_gap_pct_from_previous']=None if i==0 or not float(valid[i-1]['price']) else round((float(r['price'])/float(valid[i-1]['price'])-1),6)
    return valid


def _demand_role_signal(signal:Any) -> tuple[str|None,str]:
    if not isinstance(signal,dict): return None,''
    if signal.get('retention') or signal.get('repeat_rate'):
        return 'RETENTION','Demand signal includes retention/repeat evidence.'
    if signal.get('traffic') or signal.get('search_volume'):
        return 'TRAFFIC','Demand signal indicates search/traffic acquisition potential.'
    if signal.get('conversion') or signal.get('orders'):
        return 'HERO','Demand signal indicates conversion/order strength.'
    return None,''


def dynamic_sku_roles(scenarios:list[dict[str,Any]], demand_signals:dict[str,Any]|None=None) -> list[dict[str,Any]]:
    rows=scenario_matrix(scenarios); demand_signals=demand_signals or {}
    valid=[r for r in rows if r.get('status')=='CALCULATED_FROM_INPUTS']
    if not valid: return []
    max_contrib=max(r.get('contribution') or float('-inf') for r in valid)
    max_price=max(float(r.get('price') or 0) for r in valid); min_price=min(float(r.get('price') or 0) for r in valid)
    out=[]
    for r in valid:
        src=next((s for s in scenarios if (s.get('scenario_id') or s.get('sku')) in {r.get('scenario_id'),r.get('sku')}),{})
        explicit=src.get('role'); demand=demand_signals.get(r.get('sku')) or demand_signals.get(r.get('scenario_id'))
        demand_role,demand_why=_demand_role_signal(demand)
        if explicit: role=explicit; why='Explicit project role supplied.'; confidence='HIGH'
        elif src.get('bundle') or src.get('multipack'): role='BUNDLE'; why='Offer is explicitly a bundle/multipack; role still needs demand and cannibalization validation.'; confidence='MEDIUM'
        elif demand_role: role=demand_role; why=demand_why+' Economics remain a constraint, not the only role signal.'; confidence='MEDIUM'
        elif r.get('contribution')==max_contrib: role='MARGIN'; why='Highest calculated unit contribution among supplied scenarios; commercial role remains subject to demand/portfolio evidence.'; confidence='MEDIUM'
        elif float(r.get('price') or 0)==min_price: role='TRIAL_OR_TRAFFIC'; why='Lowest offer price can reduce entry friction; use only if channel strategy and demand support this job.'; confidence='LOW'
        elif float(r.get('price') or 0)==max_price and len(valid)>1: role='PREMIUM_CANDIDATE'; why='Highest supplied price can form the top of a price ladder, but premium value must be earned by product/offer differentiation.'; confidence='LOW'
        else: role='ASSORTMENT_SUPPORT'; why='No stronger role signal established from current economics/demand evidence.'; confidence='LOW'
        out.append({'scenario_id':r.get('scenario_id'),'sku':r.get('sku'),'role':role,'confidence':confidence,'why':why,'price':r.get('price'),'contribution':r.get('contribution'),'margin':r.get('contribution_margin'),'break_even_roas':r.get('break_even_roas'),'demand_signal':demand})
    return out



def _same_explicit(a:dict[str,Any], b:dict[str,Any], key:str) -> bool|None:
    av=a.get(key); bv=b.get(key)
    if av in (None,'',[]) or bv in (None,'',[]): return None
    return str(av).strip().casefold()==str(bv).strip().casefold()


def portfolio_interaction_analysis(scenarios:list[dict[str,Any]], roles:list[dict[str,Any]]|None=None) -> dict[str,Any]:
    """Evaluate SKU overlap, cannibalization risk and price-step justification from explicit evidence.

    Scores are intentionally ordinal evidence signals, not forecasted cannibalization percentages.
    """
    matrix=scenario_matrix(scenarios); roles=roles or []
    role_map={(r.get('sku') or r.get('scenario_id')):r.get('role') for r in roles}
    pairs=[]
    for i,a in enumerate(matrix):
        for b in matrix[i+1:]:
            evidence=[]; unknown=[]
            for key,label in [('buyer_job','same buyer job'),('target_segment','same target segment'),('configuration','same configuration'),('channel','same channel'),('product_family','same product family')]:
                same=_same_explicit(a,b,key)
                if same is True: evidence.append(label)
                elif same is None: unknown.append(key)
            pa=_f(a.get('price'),None); pb=_f(b.get('price'),None); gap_pct=None
            if pa not in (None,0) and pb is not None:
                low=min(pa,pb); high=max(pa,pb); gap_pct=(high/low-1) if low else None
                if gap_pct is not None and gap_pct<=0.15: evidence.append('price gap <= 15%')
            ra=role_map.get(a.get('sku') or a.get('scenario_id')); rb=role_map.get(b.get('sku') or b.get('scenario_id'))
            if ra and rb and ra==rb: evidence.append('same inferred/commercial role')
            strength='HIGH' if len(evidence)>=4 else ('MEDIUM' if len(evidence)>=2 else 'LOW')
            pairs.append({
                'sku_a':a.get('sku'),'scenario_a':a.get('scenario_id'),'sku_b':b.get('sku'),'scenario_b':b.get('scenario_id'),
                'overlap_signal_strength':strength,'evidence':evidence,'unknown_inputs':unknown,'price_gap_pct':round(gap_pct,6) if gap_pct is not None else None,
                'role_a':ra,'role_b':rb,'decision_status':'CANNIBALIZATION_HYPOTHESIS',
                'why':'Cannibalization risk rises when two offers solve the same explicit buyer job for the same segment/channel/configuration at similar prices. This is not a demand forecast; validate with traffic, attach-rate, switch and incrementality data.'
            })
    return {'status':'PORTFOLIO_INTERACTIONS_COMPILED','pairs':pairs,'high_overlap_pairs':[x for x in pairs if x['overlap_signal_strength']=='HIGH'],'principle':'Do not launch or keep adjacent SKUs merely because each is individually profitable; each should earn a distinct decision role or incremental demand contribution.'}




def _pair_key(a:Any,b:Any):
    vals=sorted([str(a or ''),str(b or '')])
    return tuple(vals)


def portfolio_behavior_validation(behavior_rows:list[dict[str,Any]]|None=None, pair_behavior_rows:list[dict[str,Any]]|None=None, cohort_rows:list[dict[str,Any]]|None=None, incrementality_rows:list[dict[str,Any]]|None=None) -> dict[str,Any]:
    """Aggregate supplied behavioral/cohort/counterfactual observations without inventing causality."""
    behavior_rows=list(behavior_rows or []); pair_behavior_rows=list(pair_behavior_rows or []); cohort_rows=list(cohort_rows or []); incrementality_rows=list(incrementality_rows or [])
    sku= {}
    for r in behavior_rows:
        k=str(r.get('sku') or r.get('scenario_id') or 'UNSPECIFIED')
        a=sku.setdefault(k,{'sku':k,'records':0,'visitors':0.0,'clicks':0.0,'orders':0.0,'new_customers':0.0,'repeat_customers':0.0,'revenue':0.0,'contribution':0.0,'source_ids':set()})
        a['records']+=1
        for f in ['visitors','clicks','orders','new_customers','repeat_customers','revenue','contribution']:
            a[f]+=_f(r.get(f),0)
        if r.get('source_id') not in (None,''): a['source_ids'].add(str(r.get('source_id')))
    sku_rows=[]
    for a in sku.values():
        visitors=a['visitors']; orders=a['orders']; acquired=a['new_customers']
        sku_rows.append({**{k:(sorted(v) if isinstance(v,set) else round(v,6) if isinstance(v,float) else v) for k,v in a.items()},
            'observed_cvr':round(orders/visitors,6) if visitors>0 else None,
            'repeat_customer_share_of_reported_customers':round(a['repeat_customers']/(a['new_customers']+a['repeat_customers']),6) if (a['new_customers']+a['repeat_customers'])>0 else None,
            'contribution_per_order':round(a['contribution']/orders,6) if orders>0 else None,
            'interpretation_boundary':'Observed SKU behavior only; differences may reflect traffic mix, placement, price, seasonality or targeting and are not causal by themselves.'})
    pair_rows=[]
    for r in pair_behavior_rows:
        a=str(r.get('sku_a') or r.get('from_sku') or ''); b=str(r.get('sku_b') or r.get('to_sku') or '')
        va=_f(r.get('visitors_a'),None); vb=_f(r.get('visitors_b'),None); shared=_f(r.get('shared_visitors'),None)
        pair_rows.append({
            'sku_a':a,'sku_b':b,'period':r.get('period'),'shared_visitors':shared,'visitors_a':va,'visitors_b':vb,
            'shared_on_a':round(shared/va,6) if shared is not None and va not in (None,0) else None,
            'shared_on_b':round(shared/vb,6) if shared is not None and vb not in (None,0) else None,
            'switch_a_to_b':_f(r.get('switch_a_to_b'),None),'switch_b_to_a':_f(r.get('switch_b_to_a'),None),
            'paired_orders':_f(r.get('paired_orders'),None),'exclusive_orders_a':_f(r.get('exclusive_orders_a'),None),'exclusive_orders_b':_f(r.get('exclusive_orders_b'),None),
            'source_id':r.get('source_id'),'validation_status':'OBSERVED_PAIR_BEHAVIOR_AVAILABLE',
            'interpretation_boundary':'Cross-shopping and switching describe observed overlap. They do not estimate cannibalized demand without a valid counterfactual.'
        })
    cohorts=[]
    for r in cohort_rows:
        acquired=_f(r.get('acquired_customers'),None); repeat=_f(r.get('repeat_customers'),None); orders=_f(r.get('orders'),None); contrib=_f(r.get('contribution'),None)
        cohorts.append({
            'cohort':r.get('cohort') or r.get('period'),'sku':r.get('sku'),'lifecycle_stage':r.get('lifecycle_stage'),
            'acquired_customers':acquired,'repeat_customers':repeat,'repeat_customer_rate':round(repeat/acquired,6) if repeat is not None and acquired not in (None,0) else None,
            'orders':orders,'revenue':_f(r.get('revenue'),None),'contribution':contrib,'contribution_per_acquired_customer':round(contrib/acquired,6) if contrib is not None and acquired not in (None,0) else None,
            'source_id':r.get('source_id'),'interpretation_boundary':'Cohort rates are descriptive for the supplied cohort definition and observation window; compare only when cohort construction is compatible.'
        })
    incr=[]
    for r in incrementality_rows:
        tn=_f(r.get('treatment_n'),None); cn=_f(r.get('control_n'),None); to=_f(r.get('treatment_orders'),None); co=_f(r.get('control_orders'),None)
        tr=(to/tn) if to is not None and tn not in (None,0) else None; cr=(co/cn) if co is not None and cn not in (None,0) else None
        abs_lift=(tr-cr) if tr is not None and cr is not None else None
        rel_lift=(tr/cr-1) if tr is not None and cr not in (None,0) else None
        tc=_f(r.get('treatment_contribution'),None); cc=_f(r.get('control_contribution'),None)
        tpc=(tc/tn) if tc is not None and tn not in (None,0) else None; cpc=(cc/cn) if cc is not None and cn not in (None,0) else None
        declared_randomized=bool(r.get('randomized'))
        incr.append({
            'test_id':r.get('test_id'),'sku':r.get('sku'),'offer':r.get('offer'),'treatment_n':tn,'control_n':cn,'treatment_orders':to,'control_orders':co,
            'treatment_conversion_rate':round(tr,6) if tr is not None else None,'control_conversion_rate':round(cr,6) if cr is not None else None,
            'absolute_conversion_lift':round(abs_lift,6) if abs_lift is not None else None,'relative_conversion_lift':round(rel_lift,6) if rel_lift is not None else None,
            'treatment_contribution_per_subject':round(tpc,6) if tpc is not None else None,'control_contribution_per_subject':round(cpc,6) if cpc is not None else None,
            'contribution_per_subject_lift':round(tpc-cpc,6) if tpc is not None and cpc is not None else None,
            'randomized_declared':declared_randomized,'causal_readiness':'RANDOMIZED_DESIGN_DECLARED_NEEDS_STATISTICAL_REVIEW' if declared_randomized else 'DESCRIPTIVE_COUNTERFACTUAL_UNCERTAIN',
            'source_id':r.get('source_id'),'interpretation_boundary':'Lift is arithmetic from supplied treatment/control aggregates. Statistical significance, assignment integrity and interference require experiment-level review.'
        })
    return {
        'status':'BEHAVIORAL_VALIDATION_COMPILED' if (behavior_rows or pair_behavior_rows or cohort_rows or incrementality_rows) else 'BEHAVIOR_DATA_NOT_SUPPLIED',
        'sku_behavior':sku_rows,'pair_behavior':pair_rows,'cohorts':cohorts,'incrementality':incr,
        'principle':'Use observed behavior to validate portfolio hypotheses, but distinguish descriptive overlap/cohort patterns from causal incrementality.'
    }


def validate_interaction_hypotheses(interactions:dict[str,Any], behavior:dict[str,Any]) -> dict[str,Any]:
    pair_obs={_pair_key(x.get('sku_a'),x.get('sku_b')):x for x in (behavior.get('pair_behavior') or [])}
    rows=[]
    for h in interactions.get('pairs',[]) or []:
        obs=pair_obs.get(_pair_key(h.get('sku_a'),h.get('sku_b')))
        if obs:
            status='BEHAVIORAL_EVIDENCE_AVAILABLE'
            evidence={'shared_on_a':obs.get('shared_on_a'),'shared_on_b':obs.get('shared_on_b'),'switch_a_to_b':obs.get('switch_a_to_b'),'switch_b_to_a':obs.get('switch_b_to_a'),'source_id':obs.get('source_id')}
        else:
            status='HYPOTHESIS_AWAITING_BEHAVIORAL_VALIDATION'; evidence=None
        rows.append({'sku_a':h.get('sku_a'),'sku_b':h.get('sku_b'),'hypothesis_strength':h.get('overlap_signal_strength'),'validation_status':status,'observed_behavior':evidence,'why':'Structural overlap identifies where to look; observed cross-shopping/switching can validate overlap, while causal cannibalization still requires a counterfactual or incrementality design.'})
    return {'status':'PORTFOLIO_HYPOTHESES_LINKED_TO_BEHAVIOR','pairs':rows}


def portfolio_switch_matrix(pair_behavior_rows:list[dict[str,Any]]|None=None, switch_rows:list[dict[str,Any]]|None=None) -> dict[str,Any]:
    """Build directional switch observations. Rates require an explicit eligible-from denominator."""
    transitions=[]
    for r in list(switch_rows or []):
        count=_f(r.get('switch_count') if r.get('switch_count') is not None else r.get('count'),None)
        eligible=_f(r.get('eligible_from') if r.get('eligible_from') is not None else r.get('from_population'),None)
        transitions.append({'from_sku':r.get('from_sku'),'to_sku':r.get('to_sku'),'switch_count':count,'eligible_from':eligible,'switch_rate':round(count/eligible,6) if count is not None and eligible not in (None,0) else None,'period':r.get('period'),'source_id':r.get('source_id'),'rate_status':'CALCULATED_FROM_EXPLICIT_DENOMINATOR' if count is not None and eligible not in (None,0) else 'COUNT_ONLY_NO_VALID_DENOMINATOR'})
    for r in list(pair_behavior_rows or []):
        a,b=r.get('sku_a') or r.get('from_sku'),r.get('sku_b') or r.get('to_sku')
        for src,dst,key,den_key in [(a,b,'switch_a_to_b','eligible_a'),(b,a,'switch_b_to_a','eligible_b')]:
            count=_f(r.get(key),None); eligible=_f(r.get(den_key),None)
            if count is None: continue
            transitions.append({'from_sku':src,'to_sku':dst,'switch_count':count,'eligible_from':eligible,'switch_rate':round(count/eligible,6) if eligible not in (None,0) else None,'period':r.get('period'),'source_id':r.get('source_id'),'rate_status':'CALCULATED_FROM_EXPLICIT_DENOMINATOR' if eligible not in (None,0) else 'COUNT_ONLY_NO_VALID_DENOMINATOR'})
    skus=sorted({str(x.get('from_sku')) for x in transitions if x.get('from_sku') not in (None,'')}|{str(x.get('to_sku')) for x in transitions if x.get('to_sku') not in (None,'')})
    matrix={a:{b:0.0 for b in skus} for a in skus}
    for x in transitions:
        a,b=x.get('from_sku'),x.get('to_sku')
        if a in matrix and b in matrix[a] and x.get('switch_count') is not None: matrix[a][b]+=x['switch_count']
    return {'status':'SWITCH_MATRIX_COMPILED' if transitions else 'SWITCH_DATA_NOT_SUPPLIED','skus':skus,'count_matrix':matrix,'transitions':transitions,'principle':'A switch count is descriptive. A switch rate requires an explicit eligible-from denominator; cannibalized incremental demand still requires a counterfactual.'}


def cohort_comparability_review(cohort_rows:list[dict[str,Any]]|None=None) -> dict[str,Any]:
    rows=list(cohort_rows or []); cards=[]
    for r in rows:
        supplied=[k for k in ['cohort_definition','observation_window','acquisition_channel','market','platform_family','eligibility'] if r.get(k) not in (None,'')]
        cards.append({'cohort':r.get('cohort') or r.get('period'),'sku':r.get('sku'),'comparability_metadata_supplied':supplied,'comparability_status':'DOCUMENTED_FOR_COMPARISON_REVIEW' if len(supplied)>=3 else 'COMPARABILITY_UNDER_SPECIFIED','why':'Repeat/contribution differences across cohorts should be compared only when cohort construction, observation window and acquisition context are sufficiently compatible.'})
    return {'status':'COHORT_COMPARABILITY_COMPILED' if rows else 'COHORT_DATA_NOT_SUPPLIED','cohorts':cards}


def holdout_marginal_contribution(rows:list[dict[str,Any]]|None=None) -> dict[str,Any]:
    out=[]; segment_rollup=[]
    for r in list(rows or []):
        tn=_f(r.get('treatment_n'),None); cn=_f(r.get('control_n'),None); to=_f(r.get('treatment_orders'),None); co=_f(r.get('control_orders'),None)
        tr=to/tn if to is not None and tn not in (None,0) else None; cr=co/cn if co is not None and cn not in (None,0) else None
        expected_control_orders=cr*tn if cr is not None and tn is not None else None
        incremental_orders=to-expected_control_orders if to is not None and expected_control_orders is not None else None
        tc=_f(r.get('treatment_contribution'),None); cc=_f(r.get('control_contribution'),None)
        cpc=cc/cn if cc is not None and cn not in (None,0) else None
        expected_control_contribution=cpc*tn if cpc is not None and tn is not None else None
        gross_incremental=tc-expected_control_contribution if tc is not None and expected_control_contribution is not None else None
        intervention_cost=_f(r.get('intervention_cost'),0.0) or 0.0
        net_incremental=gross_incremental-intervention_cost if gross_incremental is not None else None
        contamination=_f(r.get('contamination_rate'),None)
        assignment=bool(r.get('assignment_unit')); randomized=bool(r.get('randomized'))
        design='CAUSAL_REVIEW_READY_NOT_SIGNIFICANCE_TESTED' if randomized and assignment and tn not in (None,0) and cn not in (None,0) and (contamination is None or contamination<=0.05) else 'DESIGN_RISK_OR_INCOMPLETE'
        out.append({'test_id':r.get('test_id'),'sku':r.get('sku'),'offer':r.get('offer'),'segment':r.get('segment'),'cohort':r.get('cohort'),'period':r.get('period'),'assignment_unit':r.get('assignment_unit'),'randomized_declared':randomized,'contamination_rate':contamination,'treatment_n':tn,'control_n':cn,'treatment_conversion_rate':round(tr,6) if tr is not None else None,'control_conversion_rate':round(cr,6) if cr is not None else None,'expected_control_orders_at_treatment_n':round(expected_control_orders,6) if expected_control_orders is not None else None,'incremental_orders':round(incremental_orders,6) if incremental_orders is not None else None,'gross_incremental_contribution':round(gross_incremental,6) if gross_incremental is not None else None,'intervention_cost':intervention_cost,'net_incremental_contribution':round(net_incremental,6) if net_incremental is not None else None,'marginal_contribution_per_treatment_subject':round(net_incremental/tn,6) if net_incremental is not None and tn not in (None,0) else None,'design_readiness':design,'source_id':r.get('source_id'),'interpretation_boundary':'Arithmetic lift/marginal contribution is not a statistical significance test. Assignment integrity, interference, pre-period balance and power still require experiment review.'})
    groups={}
    for x in out:
        key=(x.get('segment') or 'ALL',x.get('cohort') or 'ALL')
        g=groups.setdefault(key,{'segment':key[0],'cohort':key[1],'tests':0,'treatment_n':0.0,'net_incremental_contribution':0.0,'incremental_orders':0.0,'fully_observed':True})
        g['tests']+=1; g['treatment_n']+=x.get('treatment_n') or 0
        if x.get('net_incremental_contribution') is None: g['fully_observed']=False
        else: g['net_incremental_contribution']+=x.get('net_incremental_contribution')
        if x.get('incremental_orders') is None: g['fully_observed']=False
        else: g['incremental_orders']+=x.get('incremental_orders')
    for g in groups.values():
        g['marginal_contribution_per_treatment_subject']=round(g['net_incremental_contribution']/g['treatment_n'],6) if g['fully_observed'] and g['treatment_n'] else None
        g['interpretation_boundary']='Segment/cohort rollups are arithmetic summaries; use pre-specified heterogeneity analysis before claiming a true differential treatment effect.'
        segment_rollup.append(g)
    return {'status':'HOLDOUT_MARGINAL_CONTRIBUTION_COMPILED' if out else 'HOLDOUT_DATA_NOT_SUPPLIED','tests':out,'segment_cohort_rollup':segment_rollup,'principle':'Portfolio incrementality should be judged on net incremental contribution, not attributed revenue alone; segment/cohort differences require heterogeneity review.'}

def trade_up_architecture(scenarios:list[dict[str,Any]], roles:list[dict[str,Any]]|None=None) -> list[dict[str,Any]]:
    rows=[r for r in scenario_matrix(scenarios) if r.get('price') is not None]
    rows.sort(key=lambda x:float(x['price']))
    roles=roles or []; role_map={(r.get('sku') or r.get('scenario_id')):r.get('role') for r in roles}
    out=[]
    for i,r in enumerate(rows):
        if i==0:
            out.append({'sku':r.get('sku'),'scenario_id':r.get('scenario_id'),'price':r.get('price'),'position':'ENTRY','role':role_map.get(r.get('sku') or r.get('scenario_id')),'upgrade_from':None,'upgrade_reason_evidence':[],'step_status':'ENTRY_POINT','why':'Entry offer should reduce the right friction without teaching the market to wait for permanent discounting.'})
            continue
        prev=rows[i-1]; evidence=[]
        for key,label in [('configuration','configuration change'),('buyer_job','buyer-job change'),('target_segment','segment change'),('offer_type','offer-type change'),('lifecycle_stage','lifecycle-stage change'),('unit_count','unit-count change')]:
            if prev.get(key) not in (None,'') and r.get(key) not in (None,'') and str(prev.get(key))!=str(r.get(key)): evidence.append(label)
        if bool(r.get('bundle'))!=bool(prev.get('bundle')): evidence.append('bundle structure change')
        if role_map.get(r.get('sku') or r.get('scenario_id'))!=role_map.get(prev.get('sku') or prev.get('scenario_id')): evidence.append('portfolio role change')
        status='JUSTIFIED_BY_EXPLICIT_DIFFERENCE' if evidence else 'PRICE_STEP_REQUIRES_VALUE_REASON'
        out.append({'sku':r.get('sku'),'scenario_id':r.get('scenario_id'),'price':r.get('price'),'position':'TRADE_UP','role':role_map.get(r.get('sku') or r.get('scenario_id')),'upgrade_from':prev.get('sku') or prev.get('scenario_id'),'upgrade_reason_evidence':evidence,'step_status':status,'why':'A higher price earns a place in the ladder only when the buyer receives a distinct configuration, job, bundle, lifecycle or value reason; price distance alone is not premium strategy.'})
    return out


def lifecycle_offer_map(scenarios:list[dict[str,Any]], roles:list[dict[str,Any]]|None=None) -> list[dict[str,Any]]:
    roles=roles or []; role_map={(r.get('sku') or r.get('scenario_id')):r.get('role') for r in roles}
    out=[]
    for r in scenario_matrix(scenarios):
        stage=r.get('lifecycle_stage')
        role=role_map.get(r.get('sku') or r.get('scenario_id'))
        if not stage:
            if role in {'TRIAL_OR_TRAFFIC','TRAFFIC'} or r.get('trial'): stage='ACQUISITION / TRIAL CANDIDATE'
            elif role=='RETENTION' or r.get('retention'): stage='RETENTION / REPLENISHMENT CANDIDATE'
            elif role=='BUNDLE': stage='CONVERSION / AOV / STOCK-UP CANDIDATE'
            else: stage='TO_BE_RESOLVED'
        out.append({'sku':r.get('sku'),'scenario_id':r.get('scenario_id'),'role':role,'lifecycle_stage':stage,'buyer_job':r.get('buyer_job'),'channel':r.get('channel'),'offer_type':r.get('offer_type'),'contribution':r.get('contribution'),'why':'Lifecycle role should connect acquisition → conversion/AOV → repeat/retention without forcing one SKU to do every job. Where stage is inferred, validate with cohort/repeat and switch data.'})
    return out



def promo_response_analysis(rows:list[dict[str,Any]]|None)->dict[str,Any]:
    """Descriptive promo/price response. Never claims causal elasticity from observational rows."""
    rows=list(rows or []); out=[]
    by_sku={}
    for i,r in enumerate(rows):
        sku=str(r.get('sku') or 'ALL'); price=_f(r.get('price'),None); qty=_f(r.get('orders') if r.get('orders') not in (None,'') else r.get('units'),None)
        conv=_f(r.get('conversion_rate'),None); disc=_f(r.get('discount_pct') if r.get('discount_pct') not in (None,'') else r.get('discount_rate'),None)
        contrib=_f(r.get('contribution_per_order') if r.get('contribution_per_order') not in (None,'') else r.get('contribution'),None)
        row={'row_id':r.get('row_id') or f'PROMO-{i+1:02d}','sku':sku,'price':price,'orders_or_units':qty,'conversion_rate':conv,'discount_rate':disc,'contribution_per_order':contrib,'period':r.get('period'),'channel':r.get('channel'),'source_id':r.get('source_id')}
        out.append(row); by_sku.setdefault(sku,[]).append(row)
    elasticity=[]
    for sku,items in by_sku.items():
        pts=[x for x in items if x.get('price') not in (None,0) and x.get('orders_or_units') not in (None,0)]
        pts.sort(key=lambda x:x['price'])
        for a,b in zip(pts,pts[1:]):
            avg_p=(a['price']+b['price'])/2; avg_q=(a['orders_or_units']+b['orders_or_units'])/2
            if not avg_p or not avg_q: continue
            ep=((b['orders_or_units']-a['orders_or_units'])/avg_q)/((b['price']-a['price'])/avg_p) if b['price']!=a['price'] else None
            elasticity.append({'sku':sku,'from_price':a['price'],'to_price':b['price'],'arc_elasticity':round(ep,6) if ep is not None else None,'status':'DESCRIPTIVE_ARC_ELASTICITY_NOT_CAUSAL','boundary':'Price and quantity may co-move with traffic, seasonality, placement, inventory or audience mix. Use randomized/controlled evidence before causal price elasticity claims.'})
    return {'status':'PROMO_RESPONSE_COMPILED' if out else 'PROMO_RESPONSE_NOT_SUPPLIED','rows':out,'descriptive_elasticity':elasticity,'principle':'Observed discount/price response can narrow offer hypotheses but does not prove causal lift or optimal discount.'}


def bundle_affinity_analysis(rows:list[dict[str,Any]]|None)->dict[str,Any]:
    rows=list(rows or []); out=[]
    for i,r in enumerate(rows):
        eligible=_f(r.get('eligible_orders') if r.get('eligible_orders') not in (None,'') else r.get('base_orders'),None)
        paired=_f(r.get('paired_orders') if r.get('paired_orders') not in (None,'') else r.get('bundle_orders'),None)
        attach=paired/eligible if eligible not in (None,0) and paired is not None else None
        out.append({'pair_id':r.get('pair_id') or f'PAIR-{i+1:02d}','base_sku':r.get('base_sku') or r.get('sku_a'),'add_on_sku':r.get('add_on_sku') or r.get('sku_b'),'eligible_orders':eligible,'paired_orders':paired,'attach_rate':round(attach,6) if attach is not None else None,'incremental_contribution':_f(r.get('incremental_contribution'),None),'source_id':r.get('source_id'),'status':'OBSERVED_AFFINITY_NOT_INCREMENTALITY','boundary':'Attach rate describes observed co-purchase among an explicit denominator; it does not prove the bundle caused incremental orders or contribution.'})
    return {'status':'BUNDLE_AFFINITY_COMPILED' if out else 'BUNDLE_AFFINITY_NOT_SUPPLIED','pairs':out,'principle':'Bundle affinity needs an explicit eligible denominator and should be separated from causal incrementality.'}


def repeat_replacement_cycle_analysis(rows:list[dict[str,Any]]|None)->dict[str,Any]:
    rows=list(rows or []); out=[]
    for i,r in enumerate(rows):
        days=_f(r.get('days_between_orders') if r.get('days_between_orders') not in (None,'') else r.get('replacement_days'),None)
        n=_f(r.get('customers') if r.get('customers') not in (None,'') else r.get('n'),None)
        out.append({'observation_id':r.get('observation_id') or f'CYCLE-{i+1:02d}','sku':r.get('sku'),'segment':r.get('segment'),'cohort':r.get('cohort'),'observed_days':days,'sample_n':n,'repeat_rate':_f(r.get('repeat_rate'),None),'source_id':r.get('source_id'),'status':'OBSERVED_CYCLE_NOT_PRESCRIPTIVE','boundary':'Observed repeat/replacement timing describes the supplied cohort only; do not turn it into a replenishment promise or CRM cadence without product/usage fit.'})
    vals=[x['observed_days'] for x in out if x.get('observed_days') is not None]
    return {'status':'REPEAT_REPLACEMENT_CYCLE_COMPILED' if out else 'REPEAT_REPLACEMENT_CYCLE_NOT_SUPPLIED','observations':out,'observed_range_days':[min(vals),max(vals)] if vals else None,'principle':'Repeat/replacement evidence can validate lifecycle offer hypotheses but does not create recommended usage frequency.'}
def economics_strategy(scenarios:list[dict[str,Any]], demand_signals:dict[str,Any]|None=None, behavior_rows:list[dict[str,Any]]|None=None, pair_behavior_rows:list[dict[str,Any]]|None=None, cohort_rows:list[dict[str,Any]]|None=None, incrementality_rows:list[dict[str,Any]]|None=None, switch_rows:list[dict[str,Any]]|None=None, holdout_rows:list[dict[str,Any]]|None=None, promo_response_rows:list[dict[str,Any]]|None=None, bundle_affinity_rows:list[dict[str,Any]]|None=None, repeat_cycle_rows:list[dict[str,Any]]|None=None) -> dict[str,Any]:
    matrix=scenario_matrix(scenarios)
    roles=dynamic_sku_roles(scenarios,demand_signals)
    interactions=portfolio_interaction_analysis(scenarios,roles)
    behavior=portfolio_behavior_validation(behavior_rows,pair_behavior_rows,cohort_rows,incrementality_rows)
    interaction_validation=validate_interaction_hypotheses(interactions,behavior)
    trade_up=trade_up_architecture(scenarios,roles)
    lifecycle=lifecycle_offer_map(scenarios,roles)
    switch_matrix=portfolio_switch_matrix(pair_behavior_rows,switch_rows)
    cohort_comparability=cohort_comparability_review(cohort_rows)
    holdout=holdout_marginal_contribution(holdout_rows or incrementality_rows)
    promo=promo_response_analysis(promo_response_rows)
    bundle=bundle_affinity_analysis(bundle_affinity_rows)
    cycle=repeat_replacement_cycle_analysis(repeat_cycle_rows)
    return {
        'status':'ECONOMICS_STRATEGY_COMPILED',
        'scenarios':matrix,
        'price_ladder':price_ladder(scenarios),
        'dynamic_sku_roles':roles,
        'role_decision_matrix':[{k:r.get(k) for k in ['sku','scenario_id','role','confidence','price','contribution','margin','break_even_roas','demand_signal','why']} for r in roles],
        'portfolio_interactions':interactions,
        'portfolio_behavior_validation':behavior,
        'interaction_behavior_validation':interaction_validation,
        'trade_up_architecture':trade_up,
        'lifecycle_offer_map':lifecycle,
        'switch_matrix':switch_matrix,
        'cohort_comparability':cohort_comparability,
        'holdout_marginal_contribution':holdout,
        'promo_response':promo,
        'bundle_affinity':bundle,
        'repeat_replacement_cycle':cycle,
        'decision_notes':[
            'Contribution protects decision quality better than revenue-only comparisons.',
            'Coupon, affiliate and paid-media headroom share the same contribution pool and should not be planned independently.',
            'SKU roles are hypotheses derived from economics plus demand/channel evidence, not fixed labels.',
            'A price ladder is only useful when each step earns a distinct buyer reason; price distance alone does not create premium architecture.',
            'Adjacent offers must be reviewed for buyer-job overlap, cannibalization and trade-up justification; individually positive contribution is not enough.',
            'Lifecycle architecture should distinguish acquisition/trial, conversion/AOV and retention/replenishment jobs where evidence supports them.',
            'Observed cross-shopping, cohort retention and treatment/control lift should validate portfolio hypotheses; descriptive behavior is not causal incrementality.',
            'Directional switch rates require explicit eligible-from denominators; net marginal contribution from a holdout/counterfactual is a stronger portfolio decision signal than attributed revenue.',
            'Observed promo response, bundle affinity and repeat/replacement cycles can validate offer hypotheses, but observational association is not causal elasticity or incrementality.'
        ]
    }
