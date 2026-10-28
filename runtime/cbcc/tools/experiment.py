from __future__ import annotations
from math import erf,sqrt


def rate(success,total): return None if not total else float(success)/float(total)
def relative_lift(control_success,control_total,test_success,test_total):
    c=rate(control_success,control_total); t=rate(test_success,test_total)
    if c in (None,0) or t is None: return None
    return (t-c)/c

def _normal_cdf(z): return 0.5*(1+erf(z/sqrt(2)))

def two_proportion_z(control_success,control_total,test_success,test_total):
    n1=float(control_total); n2=float(test_total); x1=float(control_success); x2=float(test_success)
    if n1<=0 or n2<=0: return {'status':'INSUFFICIENT_DATA'}
    p1=x1/n1; p2=x2/n2; pooled=(x1+x2)/(n1+n2); se=sqrt(max(pooled*(1-pooled)*(1/n1+1/n2),0))
    if se==0: z=0.0; p=1.0
    else: z=(p2-p1)/se; p=2*(1-_normal_cdf(abs(z)))
    return {'status':'CALCULATED','control_rate':p1,'test_rate':p2,'absolute_delta':p2-p1,'relative_lift':relative_lift(x1,n1,x2,n2),'z':z,'p_value_two_sided':p}

def wilson(success,total,z=1.959963984540054):
    if not total: return None
    n=float(total); p=float(success)/n; den=1+z*z/n; center=(p+z*z/(2*n))/den; half=z*sqrt((p*(1-p)+z*z/(4*n))/n)/den
    return {'rate':p,'lower':max(0,center-half),'upper':min(1,center+half)}

def relative_change(baseline, variant):
    """Descriptive relative change only; no sampling or causal inference is implied."""
    try:
        b=float(baseline); v=float(variant)
    except (TypeError, ValueError):
        return None
    return None if b == 0 else (v-b)/b


def evaluate_binary_experiment(control_success,control_total,test_success,test_total,alpha=0.05,min_relative_lift=None):
    z=two_proportion_z(control_success,control_total,test_success,test_total)
    if z.get('status')!='CALCULATED': return z
    significant=z['p_value_two_sided'] < alpha
    meets_lift=True if min_relative_lift is None else (z['relative_lift'] is not None and z['relative_lift'] >= min_relative_lift)
    decision='EVIDENCE_SUPPORTS_TEST' if significant and z['absolute_delta']>0 and meets_lift else 'NO_CLEAR_WINNER'
    return {**z,'alpha':alpha,'significant':significant,'min_relative_lift':min_relative_lift,'meets_lift':meets_lift,'decision':decision,
            'control_ci95':wilson(control_success,control_total),'test_ci95':wilson(test_success,test_total),'caution':'Statistical result does not prove causality if allocation, exposure window, instrumentation, or concurrent changes are uncontrolled.'}

from statistics import NormalDist

def _safe_float(v, default=None):
    try:
        if v in (None,''): return default
        return float(v)
    except Exception: return default

def _standardized_difference(mean_t,mean_c,sd_t,sd_c):
    vals=[_safe_float(x) for x in [mean_t,mean_c,sd_t,sd_c]]
    if any(x is None for x in vals): return None
    mt,mc,st,sc=vals; pooled=sqrt((st*st+sc*sc)/2) if st is not None and sc is not None else 0
    return None if pooled==0 else (mt-mc)/pooled

def _required_n_two_proportion(p0:float, absolute_mde:float, alpha:float=0.05, power:float=0.8):
    p1=p0+absolute_mde
    if not (0<p0<1 and 0<p1<1 and 0<alpha<1 and 0<power<1): return None
    nd=NormalDist(); za=nd.inv_cdf(1-alpha/2); zb=nd.inv_cdf(power); pbar=(p0+p1)/2
    num=(za*sqrt(2*pbar*(1-pbar))+zb*sqrt(p0*(1-p0)+p1*(1-p1)))**2
    den=(p1-p0)**2
    return int(num/den)+1 if den>0 else None

def experiment_design_review(spec:dict|None)->dict:
    """Compile pre-period balance, MDE/power, contamination and interference review.

    The runtime reports arithmetic/design readiness. It does not claim causal validity when allocation,
    instrumentation, interference or sample planning are unresolved.
    """
    spec=spec or {}; alpha=_safe_float(spec.get('alpha'),0.05); target_power=_safe_float(spec.get('target_power'),0.8)
    baseline=_safe_float(spec.get('baseline_rate'))
    absolute_mde=_safe_float(spec.get('absolute_mde'))
    rel_mde=_safe_float(spec.get('relative_mde'))
    if absolute_mde is None and baseline is not None and rel_mde is not None: absolute_mde=baseline*rel_mde
    required_n=_required_n_two_proportion(baseline,absolute_mde,alpha,target_power) if baseline is not None and absolute_mde is not None else None
    pre=[]; balance_risks=[]
    for row in spec.get('pre_period_metrics') or []:
        smd=_standardized_difference(row.get('treatment_mean'),row.get('control_mean'),row.get('treatment_sd'),row.get('control_sd'))
        status='BALANCE_REVIEW_REQUIRED' if smd is None else ('LARGE_IMBALANCE_SIGNAL' if abs(smd)>=0.20 else ('MODERATE_IMBALANCE_SIGNAL' if abs(smd)>=0.10 else 'SMALL_BALANCE_DIFFERENCE'))
        if status in {'LARGE_IMBALANCE_SIGNAL','MODERATE_IMBALANCE_SIGNAL','BALANCE_REVIEW_REQUIRED'}: balance_risks.append(row.get('metric'))
        pre.append({'metric':row.get('metric'),'treatment_mean':row.get('treatment_mean'),'control_mean':row.get('control_mean'),'standardized_difference':round(smd,6) if smd is not None else None,'status':status,'source_id':row.get('source_id')})
    contamination=_safe_float(spec.get('contamination_rate'))
    spillover=_safe_float(spec.get('spillover_rate'))
    interference=str(spec.get('interference_risk') or '').upper()
    assignment=spec.get('assignment_unit'); randomized=bool(spec.get('randomized'))
    design_risks=[]
    if not assignment: design_risks.append('ASSIGNMENT_UNIT_NOT_SUPPLIED')
    if not randomized: design_risks.append('RANDOMIZATION_NOT_DECLARED')
    if contamination is not None and contamination>0.05: design_risks.append('CONTAMINATION_ABOVE_5_PERCENT')
    if spillover is not None and spillover>0.05: design_risks.append('SPILLOVER_ABOVE_5_PERCENT')
    if interference in {'HIGH','KNOWN','LIKELY'}: design_risks.append('INTERFERENCE_RISK')
    if balance_risks: design_risks.append('PRE_PERIOD_BALANCE_REVIEW')
    if baseline is not None and absolute_mde is not None and required_n is None: design_risks.append('MDE_POWER_INPUT_INVALID')
    readiness='DESIGN_REVIEW_READY' if not design_risks else 'DESIGN_RISKS_REQUIRE_RESOLUTION'
    return {'status':'EXPERIMENT_DESIGN_REVIEW_COMPILED','assignment_unit':assignment,'randomized_declared':randomized,'pre_period_balance':pre,'balance_risk_metrics':balance_risks,'power_plan':{'baseline_rate':baseline,'absolute_mde':absolute_mde,'relative_mde':rel_mde,'alpha':alpha,'target_power':target_power,'approx_required_n_per_arm':required_n,'boundary':'Approximate two-proportion planning only; clustered allocation, repeated measures, sequential testing or unequal allocation require a different power model.'},'contamination_rate':contamination,'spillover_rate':spillover,'interference_risk':spec.get('interference_risk'),'design_risks':design_risks,'design_readiness':readiness,'principles':['Pre-period balance is a diagnostic, not proof of randomization quality.','Power/MDE should be set before reading outcome results where possible.','Contamination/spillover can dilute measured treatment effects and invalidate naive attribution.','A statistically significant difference does not repair broken assignment or instrumentation.']}


def _cluster_geo_cuped_sequential_review(spec:dict, power_plan:dict, outcome:dict)->dict:
    """Add cluster/geo/CUPED/sequential diagnostics without overstating causal certainty."""
    cluster=spec.get('cluster_design') or {}
    cluster_out={'status':'NOT_SUPPLIED'}
    if cluster:
        m=_safe_float(cluster.get('avg_cluster_size'))
        icc=_safe_float(cluster.get('icc'))
        design_effect=(1+(m-1)*icc) if m is not None and icc is not None and m>=1 and icc>=0 else None
        base_n=(power_plan or {}).get('approx_required_n_per_arm')
        adjusted_n=int(base_n*design_effect)+1 if base_n and design_effect else None
        cluster_out={
            'status':'CLUSTER_DESIGN_REVIEW_COMPILED','assignment_unit':cluster.get('assignment_unit') or spec.get('assignment_unit'),
            'cluster_id_field':cluster.get('cluster_id_field'),'avg_cluster_size':m,'icc':icc,'design_effect':round(design_effect,6) if design_effect is not None else None,
            'approx_required_individuals_per_arm_with_design_effect':adjusted_n,
            'clusters_per_arm':cluster.get('clusters_per_arm'),
            'boundary':'Design-effect adjustment is approximate. Cluster-level randomization/inference should use cluster-aware variance and enough independent clusters; individual-level z-tests are not a substitute.'
        }
    geo=spec.get('geo_design') or {}
    geo_out={'status':'NOT_SUPPLIED'}
    if geo:
        pairs=[]; comparable=0
        for row in geo.get('pairs') or []:
            t=_safe_float(row.get('treatment_pre')); c=_safe_float(row.get('control_pre'))
            rel=None if c in (None,0) or t is None else (t-c)/c
            status='PRE_PERIOD_NOT_SUPPLIED' if rel is None else ('PAIR_PRE_PERIOD_REVIEW' if abs(rel)>0.20 else 'PAIR_PRE_PERIOD_COMPARABLE_SIGNAL')
            if status=='PAIR_PRE_PERIOD_COMPARABLE_SIGNAL': comparable+=1
            pairs.append({'treatment_geo':row.get('treatment_geo'),'control_geo':row.get('control_geo'),'treatment_pre':t,'control_pre':c,'relative_pre_gap':round(rel,6) if rel is not None else None,'status':status})
        geo_out={'status':'GEO_DESIGN_REVIEW_COMPILED','assignment_level':geo.get('assignment_level') or 'geo','pairs':pairs,'comparable_pair_count':comparable,'pair_count':len(pairs),'exclusion_window':geo.get('exclusion_window'),'boundary':'Pre-period similarity is a diagnostic only. Geo experiments also require spillover, media-market overlap, seasonality and concurrent-intervention review.'}
    cuped=spec.get('cuped') or {}
    cuped_out={'status':'NOT_SUPPLIED'}
    if cuped:
        rho=_safe_float(cuped.get('pre_outcome_correlation'))
        vr=(rho*rho) if rho is not None and -1<=rho<=1 else None
        factor=(1-vr) if vr is not None else None
        cuped_out={'status':'CUPED_REVIEW_COMPILED','pre_metric':cuped.get('pre_metric'),'outcome_metric':cuped.get('outcome_metric'),'pre_outcome_correlation':rho,'approx_variance_reduction':round(vr,6) if vr is not None else None,'approx_remaining_variance_factor':round(factor,6) if factor is not None else None,'pre_period_frozen_before_outcome':cuped.get('pre_period_frozen_before_outcome'),'boundary':'CUPED requires a pre-treatment covariate and correct implementation on unit-level data. Correlation-derived variance reduction is planning context, not an adjusted treatment effect.'}
    sequential=spec.get('sequential') or {}
    seq_out={'status':'NOT_SUPPLIED'}
    if sequential:
        looks=int(sequential.get('planned_looks') or 0); current=int(sequential.get('current_look') or 0); alpha=_safe_float(spec.get('alpha'),0.05)
        method=str(sequential.get('method') or 'BONFERRONI_CONSERVATIVE').upper()
        alpha_threshold=(alpha/looks) if looks>0 else None
        pval=(outcome or {}).get('p_value_two_sided') if isinstance(outcome,dict) else None
        crosses=bool(pval is not None and alpha_threshold is not None and pval<alpha_threshold)
        seq_out={'status':'SEQUENTIAL_REVIEW_COMPILED','method':method,'planned_looks':looks or None,'current_look':current or None,'nominal_alpha':alpha,'conservative_alpha_per_look':alpha_threshold,'current_p_value':pval,'crosses_conservative_boundary':crosses,'decision':'BOUNDARY_CROSSED_REVIEW_SCALE' if crosses else 'CONTINUE_OR_REVIEW_PER_PLAN','boundary':'This runtime uses a conservative Bonferroni-style diagnostic only; it does not implement alpha-spending/OBrien-Fleming/Pocock inference or optional-stopping repair.'}
    return {'cluster':cluster_out,'geo':geo_out,'cuped':cuped_out,'sequential':seq_out}

def compile_experiment_analysis(spec:dict|None)->dict:
    spec=spec or {}; design=experiment_design_review(spec)
    outcome={}
    keys=['control_success','control_total','test_success','test_total']
    if all(spec.get(k) not in (None,'') for k in keys):
        outcome=evaluate_binary_experiment(spec['control_success'],spec['control_total'],spec['test_success'],spec['test_total'],spec.get('alpha',0.05),spec.get('min_relative_lift'))
    else: outcome={'status':'OUTCOME_NOT_SUPPLIED'}
    segments=[]
    for r in spec.get('segments') or []:
        if all(r.get(k) not in (None,'') for k in keys):
            res=evaluate_binary_experiment(r['control_success'],r['control_total'],r['test_success'],r['test_total'],spec.get('alpha',0.05),r.get('min_relative_lift'))
            segments.append({'segment':r.get('segment') or r.get('cohort'),**res,'boundary':'Segment results are exploratory unless multiplicity/heterogeneity analysis was planned.'})
    advanced=_cluster_geo_cuped_sequential_review(spec,design.get('power_plan') or {},outcome)
    return {**outcome,'analysis_status':'EXPERIMENT_ANALYSIS_COMPILED','design_review':design,'outcome':outcome,'segments':segments,'advanced_design_review':advanced,'causal_interpretation':'Outcome evidence can support a causal decision only when assignment, exposure, instrumentation, interference and concurrent-change risks are acceptable.','measurement_action':'Use design risks, cluster/geo structure, covariate plan and sequential-monitoring rules to decide whether to rerun/fix the experiment before scaling creative, offer or SKU decisions.'}
