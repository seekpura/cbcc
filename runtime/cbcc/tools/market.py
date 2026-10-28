from __future__ import annotations
from collections import defaultdict, Counter
from math import floor
from statistics import median
from typing import Any, Iterable
from datetime import datetime, timezone
import re
from .evidence import compile_research_ingestion


def _f(v, default=0.0):
    if v in (None, ''):
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _share_percent(v: float) -> float:
    return v * 100.0 if 0 <= v <= 1 else v


def _first(row: dict[str, Any], *keys, default=None):
    for key in keys:
        if row.get(key) not in (None, ''):
            return row.get(key)
    return default


def normalize_market_rows(rows: list[dict[str, Any]], field_map: dict[str, str] | None = None) -> dict[str, Any]:
    """Normalize common marketplace exports without pretending semantic equivalence.

    field_map maps canonical -> source field. Alias matching is intentionally conservative.
    Unknown columns are preserved under ``_raw`` so the host/model can still interpret them.
    """
    rows = list(rows or [])
    field_map = field_map or {}
    aliases = {
        'product': ['product', 'product_name', 'title', 'item_name', 'listing_name'],
        'seller': ['seller', 'seller_name', 'shop', 'shop_name', 'merchant'],
        'brand': ['brand', 'brand_name'],
        'price': ['price', 'selling_price', 'sale_price', 'unit_price'],
        'units': ['units', 'sales_units', 'sold', 'orders', 'quantity_sold'],
        'revenue': ['revenue', 'sales', 'gmv', 'sales_value'],
        'configuration': ['configuration', 'config', 'variant', 'size', 'pack', 'bundle'],
        'rating': ['rating', 'star_rating', 'avg_rating'],
        'review_count': ['review_count', 'reviews', 'ratings_count'],
        'rank': ['rank', 'ranking', 'position'],
        'keyword': ['keyword', 'search_term', 'query'],
        'search_volume': ['search_volume', 'keyword_volume', 'volume'],
        'competition': ['competition', 'keyword_competition', 'difficulty'],
    }
    normalized = []
    provenance = []
    for idx, raw in enumerate(rows):
        low = {str(k).casefold(): k for k in raw}
        out: dict[str, Any] = {}
        used = set()
        for canonical, names in aliases.items():
            src = field_map.get(canonical)
            if src and src in raw:
                value = raw.get(src); used.add(src)
            else:
                value = None
                for name in names:
                    actual = low.get(name.casefold())
                    if actual is not None and raw.get(actual) not in (None, ''):
                        value = raw.get(actual); used.add(actual); break
            if value not in (None, ''):
                out[canonical] = value
        # Derive revenue only when price and units are explicit numeric inputs.
        if out.get('revenue') in (None, '') and out.get('price') not in (None, '') and out.get('units') not in (None, ''):
            p = _f(out.get('price'), None); u = _f(out.get('units'), None)
            if p is not None and u is not None:
                out['revenue'] = p * u
                out['_derived_revenue'] = True
        for k in ['price', 'units', 'revenue', 'rating', 'review_count', 'rank', 'search_volume', 'competition']:
            if k in out:
                val = _f(out[k], None)
                if val is not None: out[k] = val
        out['_raw'] = {k: v for k, v in raw.items() if k not in used}
        out['_row_index'] = idx
        normalized.append(out)
        provenance.append({'row_index': idx, 'canonical_fields': sorted(k for k in out if not k.startswith('_')), 'unmapped_fields': sorted(out['_raw'])})
    return {'status': 'NORMALIZED', 'rows': normalized, 'provenance': provenance, 'row_count': len(normalized)}




def _parse_dt(v: Any):
    if v in (None, ''):
        return None
    try:
        text=str(v).strip().replace('Z','+00:00')
        dt=datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt=dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def research_source_quality(datasets: dict[str, list[dict[str,Any]]], source_records:list[dict[str,Any]]|None=None, as_of:str|None=None, research_scope:dict[str,Any]|None=None) -> dict[str,Any]:
    """Compile source-level traceability/freshness/representativeness contracts without claiming representativeness.

    Freshness is thresholded only when the project or source explicitly supplies max_age_days.
    Representativeness is never inferred from row count; the runtime only records whether sample-frame metadata exists.
    """
    source_records=list(source_records or []); research_scope=research_scope or {}
    by_id={str(x.get('source_id')):x for x in source_records if x.get('source_id') not in (None,'')}
    asof=_parse_dt(as_of)
    source_cards=[]
    for sid,src in by_id.items():
        observed=_parse_dt(_first(src,'observed_at','collected_at','verified_at','published_at'))
        age_days=(asof-observed).days if asof and observed else None
        max_age=_first(src,'max_age_days',default=research_scope.get('max_age_days'))
        try: max_age=float(max_age) if max_age not in (None,'') else None
        except Exception: max_age=None
        if age_days is None: freshness='DATE_NOT_SUPPLIED'
        elif age_days < 0: freshness='OBSERVATION_AFTER_AS_OF_REVIEW'
        elif max_age is None: freshness='AGE_RECORDED_NO_THRESHOLD'
        else: freshness='WITHIN_DECLARED_FRESHNESS_WINDOW' if age_days<=max_age else 'OUTSIDE_DECLARED_FRESHNESS_WINDOW'
        rep_fields=['population_scope','sample_frame','sampling_method','inclusion_criteria']
        rep_supplied=[k for k in rep_fields if src.get(k) not in (None,'',[])]
        rep='REPRESENTATIVENESS_DOCUMENTED_NOT_PROVEN' if len(rep_supplied)>=3 else 'REPRESENTATIVENESS_UNKNOWN'
        mismatches=[]
        for sk,rk in [('market','market'),('site','site'),('platform_family','platform_family'),('category','category')]:
            expected=research_scope.get(rk) or research_scope.get('expected_'+rk)
            actual=src.get(sk)
            if expected not in (None,'') and actual not in (None,'') and str(expected).casefold()!=str(actual).casefold():
                mismatches.append({'field':rk,'expected':expected,'actual':actual})
        raw_quality=_first(src,'source_quality_score','quality_score','reliability_score','evidence_quality_score')
        try:
            explicit_quality=max(0.0,min(1.0,float(raw_quality))) if raw_quality not in (None,'') else None
        except Exception:
            explicit_quality=None
        quality_tier=str(_first(src,'source_quality_tier','quality_tier','authority_level',default='') or '').upper() or None
        source_cards.append({
            'source_id':sid,'kind':src.get('kind'),'title':src.get('title'),'url':src.get('url'),
            'observed_at':_first(src,'observed_at','collected_at','verified_at','published_at'),'age_days':age_days,
            'max_age_days':max_age,'freshness_status':freshness,'representativeness_status':rep,
            'representativeness_metadata_supplied':rep_supplied,'scope_mismatches':mismatches,
            'population_scope':src.get('population_scope'),'sample_frame':src.get('sample_frame'),'sampling_method':src.get('sampling_method'),
            'query_scope':src.get('query_scope'),'inclusion_criteria':src.get('inclusion_criteria'),'exclusion_criteria':src.get('exclusion_criteria'),
            'coverage_note':src.get('coverage_note'),'source_quality_score':explicit_quality,'source_quality_tier':quality_tier,
            'source_quality_status':'EXPLICIT_SCORE_SUPPLIED' if explicit_quality is not None else ('EXPLICIT_TIER_SUPPLIED' if quality_tier else 'NOT_DECLARED')
        })
    dataset_cards=[]
    unresolved=set(); referenced=set()
    for name,rows in datasets.items():
        rows=list(rows or []); with_sid=0; resolved=0; ids=set()
        for r in rows:
            sid=_first(r,'source_id','listing_id','review_id','id')
            if sid not in (None,''):
                with_sid+=1; sid=str(sid); ids.add(sid); referenced.add(sid)
                if sid in by_id: resolved+=1
                else: unresolved.add(sid)
        coverage_ratio=round(with_sid/len(rows),4) if rows else None
        resolved_ratio=round(resolved/with_sid,4) if with_sid else None
        lineage_score=(coverage_ratio if coverage_ratio is not None else 0.0) * (resolved_ratio if resolved_ratio is not None else 0.0)
        dataset_cards.append({
            'dataset':name,'row_count':len(rows),'rows_with_source_id':with_sid,
            'source_id_coverage_ratio':coverage_ratio,
            'resolved_source_ratio':resolved_ratio,
            'traceability_score':round(lineage_score,4) if rows else None,
            'source_ids':sorted(ids),
            'decision_boundary':'This dataset may inform strategy only within its declared market/platform/category/time/sample scope; row count alone does not establish representativeness.'
        })
    source_cards=[x for x in source_cards if x.get('source_id') in referenced]
    stale=[x['source_id'] for x in source_cards if x['freshness_status']=='OUTSIDE_DECLARED_FRESHNESS_WINDOW']
    mismatched=[x['source_id'] for x in source_cards if x.get('scope_mismatches')]
    return {
        'status':'SOURCE_QUALITY_COMPILED' if any(d['row_count'] for d in dataset_cards) else 'NO_RESEARCH_ROWS',
        'as_of':as_of,'research_scope':research_scope,'datasets':dataset_cards,'sources':source_cards,
        'unresolved_source_ids':sorted(unresolved),'referenced_source_ids':sorted(referenced),
        'stale_by_declared_threshold':stale,'scope_mismatch_source_ids':mismatched,
        'representativeness_principle':'Representativeness is a documented research property, never inferred from sample size, seller count, review count or source prestige.',
        'freshness_principle':'Freshness is evaluated only against an explicitly supplied max_age_days window; otherwise the runtime records source age without inventing a threshold.',
        'source_quality_principle':'Source quality affects strategy weight only when explicitly declared as a score/tier or when deterministic traceability/scope/freshness metadata exists. Brand/source prestige is never invented as a quality shortcut.'
    }

def concentration_from_shares(shares: Iterable[float]) -> dict[str, Any]:
    vals = sorted((_share_percent(float(x)) for x in shares if x is not None), reverse=True)
    return {
        'cr3': round(sum(vals[:3]), 4) if vals else None,
        'cr10': round(sum(vals[:10]), 4) if vals else None,
        'hhi': round(sum(x*x for x in vals), 4) if vals else None,
        'share_sum': round(sum(vals), 4) if vals else None,
        'seller_count': len(vals),
    }


def concentration_from_rows(rows: list[dict[str, Any]], seller_key='seller', revenue_key='revenue') -> dict[str, Any]:
    by_seller = defaultdict(float)
    for r in rows:
        seller = str(r.get(seller_key) or 'UNKNOWN')
        by_seller[seller] += _f(r.get(revenue_key), 0.0)
    total = sum(by_seller.values())
    if total <= 0:
        shares = [r.get('share') for r in rows if r.get('share') not in (None, '')]
        return concentration_from_shares(shares)
    shares = [v / total for v in by_seller.values()]
    out = concentration_from_shares(shares)
    out['revenue_total'] = round(total, 6)
    return out


def _auto_price_step(prices: list[float]) -> float:
    if not prices:
        return 1.0
    lo, hi = min(prices), max(prices)
    span = hi - lo
    if span <= 0:
        return max(abs(lo) * 0.1, 1.0)
    raw = span / 6.0
    mag = 10 ** floor(__import__('math').log10(raw)) if raw > 0 else 1
    x = raw / mag
    nice = 1 if x <= 1 else 2 if x <= 2 else 5 if x <= 5 else 10
    return nice * mag


def price_band_analysis(rows: list[dict[str, Any]], step: float | None = None) -> list[dict[str, Any]]:
    prices = [_f(r.get('price'), None) for r in rows if r.get('price') not in (None, '')]
    prices = [p for p in prices if p is not None]
    if not prices:
        return []
    step = float(step or _auto_price_step(prices))
    origin = floor(min(prices) / step) * step
    buckets: dict[int, dict[str, float]] = defaultdict(lambda: {'items': 0, 'units': 0.0, 'revenue': 0.0})
    for r in rows:
        if r.get('price') in (None, ''):
            continue
        price = float(r['price']); idx = int(floor((price - origin) / step + 1e-12))
        b = buckets[idx]; b['items'] += 1; b['units'] += _f(r.get('units'), 0); b['revenue'] += _f(r.get('revenue'), price * _f(r.get('units'), 0))
    out=[]
    for idx in range(min(buckets), max(buckets)+1):
        b=buckets.get(idx, {'items':0,'units':0.0,'revenue':0.0})
        lower=origin+idx*step; upper=lower+step
        eff=(b['units']/b['items']) if b['items'] else None
        rev_eff=(b['revenue']/b['items']) if b['items'] else None
        out.append({'index':idx,'lower':round(lower,6),'upper':round(upper,6),'items':int(b['items']),'units':round(b['units'],6),'revenue':round(b['revenue'],6),'units_per_item':round(eff,6) if eff is not None else None,'revenue_per_item':round(rev_eff,6) if rev_eff is not None else None})
    return out


def detect_price_valleys(bands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect low-density bands bracketed by stronger adjacent demand.

    This is a signal, never a recommendation. A valley can also mean weak demand.
    """
    vals=[]
    for i in range(1, len(bands)-1):
        a,b,c=bands[i-1],bands[i],bands[i+1]
        neighbor_units=(a['units']+c['units'])/2
        if neighbor_units <= 0:
            continue
        competition=b['items']
        if b['units'] < neighbor_units*0.7 and competition <= max(a['items'],c['items']):
            vals.append({'lower':b['lower'],'upper':b['upper'],'units':b['units'],'items':b['items'],'neighbor_units_avg':round(neighbor_units,6),'signal':'LOW_DENSITY_BETWEEN_STRONGER_NEIGHBORS','interpretation_boundary':'Validate demand, configuration fit and contribution before treating as opportunity.'})
    return vals


def configuration_analysis(rows: list[dict[str, Any]], config_key='configuration') -> list[dict[str, Any]]:
    agg=defaultdict(lambda:{'items':0,'units':0.0,'revenue':0.0,'prices':[],'reviews':0.0})
    for r in rows:
        cfg=str(r.get(config_key) or 'UNSPECIFIED'); a=agg[cfg]
        a['items'] += 1; a['units'] += _f(r.get('units'),0); a['revenue'] += _f(r.get('revenue'),0); a['reviews'] += _f(r.get('review_count'),0)
        if r.get('price') not in (None,''): a['prices'].append(float(r['price']))
    out=[]
    for cfg,a in agg.items():
        out.append({'configuration':cfg,'items':a['items'],'units':round(a['units'],6),'revenue':round(a['revenue'],6),'units_per_item':round(a['units']/a['items'],6) if a['items'] else None,'revenue_per_item':round(a['revenue']/a['items'],6) if a['items'] else None,'median_price':round(median(a['prices']),6) if a['prices'] else None,'review_signal':round(a['reviews'],6)})
    return sorted(out,key=lambda x:(x['units_per_item'] or 0,x['revenue']),reverse=True)


def seller_efficiency(rows: list[dict[str, Any]], seller_key='seller') -> list[dict[str, Any]]:
    agg=defaultdict(lambda:{'items':0,'units':0.0,'revenue':0.0,'reviews':0.0})
    for r in rows:
        s=str(r.get(seller_key) or 'UNKNOWN'); a=agg[s]
        a['items'] += 1; a['units'] += _f(r.get('units'),0); a['revenue'] += _f(r.get('revenue'),0); a['reviews'] += _f(r.get('review_count'),0)
    return sorted(({'seller':s,**a,'units_per_item':round(a['units']/a['items'],6) if a['items'] else None,'revenue_per_item':round(a['revenue']/a['items'],6) if a['items'] else None} for s,a in agg.items()), key=lambda x:x['revenue'], reverse=True)


def competitor_snapshot(rows:list[dict[str,Any]], brand_key='brand', seller_key='seller') -> dict[str,Any]:
    brands=defaultdict(lambda:{'items':0,'units':0.0,'revenue':0.0,'prices':[],'ratings':[],'reviews':0.0,'configs':Counter()})
    for r in rows:
        name=str(r.get(brand_key) or r.get(seller_key) or 'UNKNOWN')
        a=brands[name]; a['items']+=1; a['units']+=_f(r.get('units'),0); a['revenue']+=_f(r.get('revenue'),_f(r.get('price'),0)*_f(r.get('units'),0)); a['reviews']+=_f(r.get('review_count'),0)
        if r.get('price') not in (None,''): a['prices'].append(float(r['price']))
        if r.get('rating') not in (None,''): a['ratings'].append(float(r['rating']))
        a['configs'][str(r.get('configuration') or 'UNSPECIFIED')]+=1
    out=[]
    for name,a in brands.items():
        out.append({'competitor':name,'items':a['items'],'units':round(a['units'],6),'revenue':round(a['revenue'],6),'median_price':round(median(a['prices']),6) if a['prices'] else None,'revenue_per_item':round(a['revenue']/a['items'],6) if a['items'] else None,'avg_rating':round(sum(a['ratings'])/len(a['ratings']),4) if a['ratings'] else None,'review_count':round(a['reviews'],6),'dominant_configuration':a['configs'].most_common(1)[0][0] if a['configs'] else None})
    out.sort(key=lambda x:x['revenue'],reverse=True)
    return {'top_competitors':out[:20],'competitor_count':len(out)}


def price_configuration_matrix(rows:list[dict[str,Any]], config_key='configuration', price_step:float|None=None) -> list[dict[str,Any]]:
    bands=price_band_analysis(rows,price_step)
    if not bands: return []
    step=bands[0]['upper']-bands[0]['lower']; origin=bands[0]['lower']
    agg=defaultdict(lambda:{'items':0,'units':0.0,'revenue':0.0})
    for r in rows:
        if r.get('price') in (None,''): continue
        idx=int(floor((float(r['price'])-origin)/step+1e-12)); cfg=str(r.get(config_key) or 'UNSPECIFIED')
        a=agg[(idx,cfg)]; a['items']+=1; a['units']+=_f(r.get('units'),0); a['revenue']+=_f(r.get('revenue'),float(r['price'])*_f(r.get('units'),0))
    out=[]
    for (idx,cfg),a in agg.items():
        lower=origin+idx*step
        out.append({'price_lower':round(lower,6),'price_upper':round(lower+step,6),'configuration':cfg,'items':a['items'],'units':round(a['units'],6),'revenue':round(a['revenue'],6),'units_per_item':round(a['units']/a['items'],6) if a['items'] else None})
    return sorted(out,key=lambda x:(x['units_per_item'] or 0,x['revenue']),reverse=True)


def competitor_clusters(rows:list[dict[str,Any]], config_key='configuration') -> list[dict[str,Any]]:
    """Deterministic structural clusters: price tier × configuration.

    This avoids semantic claims such as 'premium brand' unless the data actually supports them.
    """
    prices=[float(r['price']) for r in rows if r.get('price') not in (None,'')]
    if not prices: return []
    med=median(prices)
    agg=defaultdict(lambda:{'items':0,'units':0.0,'revenue':0.0,'competitors':set(),'prices':[]})
    for r in rows:
        p=_f(r.get('price'),None)
        if p is None: continue
        tier='LOWER_PRICE' if p < med*0.8 else ('HIGHER_PRICE' if p > med*1.2 else 'MID_PRICE')
        cfg=str(r.get(config_key) or 'UNSPECIFIED')
        a=agg[(tier,cfg)]; a['items']+=1; a['units']+=_f(r.get('units'),0); a['revenue']+=_f(r.get('revenue'),0); a['prices'].append(p); a['competitors'].add(str(r.get('brand') or r.get('seller') or 'UNKNOWN'))
    out=[]
    for (tier,cfg),a in agg.items():
        out.append({'cluster_id':f'{tier}::{cfg}','price_tier':tier,'configuration':cfg,'items':a['items'],'competitor_count':len(a['competitors']),'units':round(a['units'],6),'revenue':round(a['revenue'],6),'units_per_item':round(a['units']/a['items'],6) if a['items'] else None,'median_price':round(median(a['prices']),6) if a['prices'] else None,'interpretation':'Structural cluster for comparing offer density/efficiency; not a psychographic or brand-positioning label.'})
    return sorted(out,key=lambda x:(x['revenue'],x['units_per_item'] or 0),reverse=True)


def keyword_demand_analysis(rows:list[dict[str,Any]]|None) -> dict[str,Any]:
    rows=list(rows or [])
    agg=defaultdict(lambda:{'volume':0.0,'competition_values':[],'rank_values':[],'records':0,'intents':Counter(),'sources':set()})
    for r in rows:
        term=str(_first(r,'term','keyword','search_term','query',default='') or '').strip()
        if not term: continue
        a=agg[term.casefold()]; a['term']=term; a['volume']+=_f(_first(r,'volume','search_volume','keyword_volume'),0); a['records']+=1
        comp=_first(r,'competition','difficulty'); rank=_first(r,'rank','ranking','position')
        if comp not in (None,''): a['competition_values'].append(_f(comp,0))
        if rank not in (None,''): a['rank_values'].append(_f(rank,0))
        intent=str(r.get('intent') or r.get('cluster') or 'UNCLASSIFIED').upper(); a['intents'][intent]+=1
        if r.get('source_id'): a['sources'].add(str(r['source_id']))
    terms=[]
    for a in agg.values():
        comp=sum(a['competition_values'])/len(a['competition_values']) if a['competition_values'] else None
        priority=(a['volume']/(1+comp)) if comp is not None and a['volume'] else a['volume']
        terms.append({'term':a['term'],'volume':round(a['volume'],6),'avg_competition':round(comp,6) if comp is not None else None,'avg_rank':round(sum(a['rank_values'])/len(a['rank_values']),6) if a['rank_values'] else None,'intent':a['intents'].most_common(1)[0][0] if a['intents'] else 'UNCLASSIFIED','priority_signal':round(priority,6),'records':a['records'],'source_ids':sorted(a['sources'])})
    terms.sort(key=lambda x:(x['priority_signal'],x['volume']),reverse=True)
    by_intent=defaultdict(lambda:{'term_count':0,'volume':0.0})
    for t in terms:
        a=by_intent[t['intent']]; a['term_count']+=1; a['volume']+=t['volume']
    return {'status':'AGGREGATED_FROM_INPUT' if rows else 'NOT_SUPPLIED','top_terms':terms[:50],'intent_summary':[{ 'intent':k, **v} for k,v in sorted(by_intent.items(),key=lambda kv:kv[1]['volume'],reverse=True)],'note':'Keyword priority is a demand signal only. Semantic relevance, product truth and platform field constraints remain separate authorities.'}



def customer_voice_analysis(rows:list[dict[str,Any]]|None) -> dict[str,Any]:
    """Aggregate supplied market/competitor review labels without semantic invention.

    The runtime intentionally does *not* infer theme or sentiment from free text.  Hosts/models may
    classify upstream, but this deterministic layer only aggregates explicit fields so Strategy
    Authority can distinguish observed labels from interpretation.
    """
    rows=list(rows or [])
    if not rows:
        return {'status':'NOT_SUPPLIED','row_count':0,'theme_summary':[],'sentiment_summary':[],
                'competitor_theme_matrix':[],'audience_theme_matrix':[],'unclassified':{'theme':0,'sentiment':0},
                'note':'Supply market_review_rows with explicit theme/category and sentiment labels; free text is never auto-classified here.'}
    themes=defaultdict(lambda:{'records':0,'count':0.0,'sentiments':Counter(),'competitors':Counter(),'audiences':Counter(),'examples':[],'source_ids':set()})
    sentiments=Counter(); competitor_theme=Counter(); audience_theme=Counter()
    missing_theme=missing_sentiment=0
    for idx,r in enumerate(rows):
        theme=str(_first(r,'theme','category','issue_type','review_theme',default='') or '').strip()
        sentiment=str(_first(r,'sentiment','polarity',default='') or '').strip().upper()
        competitor=str(_first(r,'competitor','brand','seller','shop',default='UNSPECIFIED') or 'UNSPECIFIED').strip()
        audience=str(_first(r,'audience_segment','segment','persona','customer_segment',default='UNSPECIFIED') or 'UNSPECIFIED').strip()
        weight=max(0.0,_f(_first(r,'count','weight','mentions',default=1),1.0))
        if not theme:
            missing_theme += 1
            theme='UNCLASSIFIED'
        if not sentiment:
            missing_sentiment += 1
            sentiment='UNCLASSIFIED'
        t=themes[theme]; t['records']+=1; t['count']+=weight; t['sentiments'][sentiment]+=weight; t['competitors'][competitor]+=weight; t['audiences'][audience]+=weight
        sentiments[sentiment]+=weight; competitor_theme[(competitor,theme)]+=weight; audience_theme[(audience,theme)]+=weight
        sid=_first(r,'source_id','review_id','id')
        if sid not in (None,''): t['source_ids'].add(str(sid))
        text=str(_first(r,'text','review','excerpt','comment',default='') or '').strip()
        if text and len(t['examples'])<3:
            t['examples'].append({'text':text[:500],'source_id':str(sid) if sid not in (None,'') else None,'row_index':idx})
    theme_rows=[]
    for theme,t in themes.items():
        dominant=t['sentiments'].most_common(1)[0][0] if t['sentiments'] else 'UNCLASSIFIED'
        theme_rows.append({'theme':theme,'records':t['records'],'weighted_mentions':round(t['count'],6),'dominant_sentiment':dominant,
                           'sentiment_mix':dict(t['sentiments']),'top_competitors':[{'competitor':k,'mentions':round(v,6)} for k,v in t['competitors'].most_common(5)],
                           'top_audiences':[{'audience':k,'mentions':round(v,6)} for k,v in t['audiences'].most_common(5)],
                           'examples':t['examples'],'source_ids':sorted(t['source_ids'])})
    theme_rows.sort(key=lambda x:(x['weighted_mentions'],x['records']),reverse=True)
    return {
        'status':'AGGREGATED_FROM_SUPPLIED_LABELS',
        'row_count':len(rows),
        'theme_summary':theme_rows,
        'sentiment_summary':[{'sentiment':k,'weighted_mentions':round(v,6)} for k,v in sentiments.most_common()],
        'competitor_theme_matrix':[{'competitor':c,'theme':t,'weighted_mentions':round(v,6)} for (c,t),v in competitor_theme.most_common(100)],
        'audience_theme_matrix':[{'audience':a,'theme':t,'weighted_mentions':round(v,6)} for (a,t),v in audience_theme.most_common(100)],
        'unclassified':{'theme':missing_theme,'sentiment':missing_sentiment},
        'note':'Deterministic aggregation of supplied labels only. No free-text semantic classification, representativeness claim, or causal conclusion is made.'
    }


def competitor_listing_analysis(rows:list[dict[str,Any]]|None, customer_voice:dict[str,Any]|None=None) -> dict[str,Any]:
    """Aggregate explicitly supplied competitor Listing/message labels without semantic invention."""
    rows=list(rows or [])
    if not rows:
        return {
            'status':'NOT_SUPPLIED','row_count':0,'competitors':[],'message_theme_summary':[],
            'offer_type_summary':[],'proof_type_summary':[],'message_review_overlap':[],
            'note':'Supply competitor_listing_rows with competitor plus observed title/claim/message_theme/offer_type/proof_type fields. Runtime does not invent semantic themes from copy.'
        }
    by_comp=defaultdict(lambda:{'listing_count':0,'titles':[],'claims':[],'message_themes':Counter(),'offer_types':Counter(),'proof_types':Counter(),'configurations':Counter(),'surfaces':Counter(),'locales':Counter(),'visual_patterns':Counter(),'source_ids':set()})
    theme_total=Counter(); offer_total=Counter(); proof_total=Counter(); proof_sources=defaultdict(set)
    for idx,r in enumerate(rows):
        comp=str(_first(r,'competitor','brand','seller','shop',default='UNSPECIFIED') or 'UNSPECIFIED').strip()
        a=by_comp[comp]; a['listing_count']+=1
        title=str(_first(r,'title','listing_title','product_title',default='') or '').strip()
        if title and len(a['titles'])<5: a['titles'].append({'text':title[:500],'row_index':idx,'source_id':r.get('source_id')})
        raw_claims=_first(r,'claims','claim','primary_claim','headline',default=[])
        if isinstance(raw_claims,str): raw_claims=[raw_claims]
        elif raw_claims in (None,''): raw_claims=[]
        elif not isinstance(raw_claims,list): raw_claims=[raw_claims]
        for c in raw_claims:
            text=str(c).strip()
            if text and len(a['claims'])<10: a['claims'].append({'text':text[:500],'source_id':r.get('source_id')})
        theme=str(_first(r,'message_theme','claim_theme','positioning_theme',default='') or '').strip()
        if theme:
            w=max(0.0,_f(_first(r,'count','weight','listings',default=1),1)); a['message_themes'][theme]+=w; theme_total[theme]+=w
        offer=str(_first(r,'offer_type','promotion_type','deal_type',default='') or '').strip()
        if offer: a['offer_types'][offer]+=1; offer_total[offer]+=1
        proof=str(_first(r,'proof_type','evidence_type','trust_signal',default='') or '').strip()
        if proof:
            a['proof_types'][proof]+=1; proof_total[proof]+=1
            psid=_first(r,'source_id','listing_id','id')
            if psid not in (None,''): proof_sources[proof].add(str(psid))
        cfg=str(_first(r,'configuration','pack','size','variant',default='') or '').strip()
        if cfg: a['configurations'][cfg]+=1
        surface=str(_first(r,'surface','placement',default='') or '').strip()
        if surface: a['surfaces'][surface]+=1
        locale=str(_first(r,'locale','language',default='') or '').strip()
        if locale: a['locales'][locale]+=1
        vp=str(_first(r,'visual_pattern','visual_territory','creative_pattern',default='') or '').strip()
        if vp: a['visual_patterns'][vp]+=1
        sid=_first(r,'source_id','listing_id','id')
        if sid not in (None,''): a['source_ids'].add(str(sid))
    cv=customer_voice or {}; review_by_comp=defaultdict(Counter)
    for x in cv.get('competitor_theme_matrix',[]) or []:
        theme=str(x.get('theme') or '').strip()
        if theme: review_by_comp[str(x.get('competitor') or 'UNSPECIFIED')][theme]+=float(x.get('weighted_mentions') or 0)
    competitors=[]; overlaps=[]
    for comp,a in by_comp.items():
        exact_overlap=sorted(set(a['message_themes']) & set(review_by_comp.get(comp,{})))
        row={
            'competitor':comp,'listing_count':a['listing_count'],'observed_titles':a['titles'],'observed_claims':a['claims'],
            'message_themes':[{'theme':k,'observed_weight':round(v,6)} for k,v in a['message_themes'].most_common(10)],
            'offer_types':[{'offer_type':k,'count':v} for k,v in a['offer_types'].most_common()],
            'proof_types':[{'proof_type':k,'count':v} for k,v in a['proof_types'].most_common()],
            'configurations':[{'configuration':k,'count':v} for k,v in a['configurations'].most_common()],
            'surfaces':[{'surface':k,'count':v} for k,v in a['surfaces'].most_common()],
            'locales':[{'locale':k,'count':v} for k,v in a['locales'].most_common()],
            'visual_patterns':[{'visual_pattern':k,'count':v} for k,v in a['visual_patterns'].most_common()],
            'review_themes':[{'theme':k,'weighted_mentions':round(v,6)} for k,v in review_by_comp.get(comp,Counter()).most_common(10)],
            'exact_message_review_theme_overlap':exact_overlap,'source_ids':sorted(a['source_ids']),
            'interpretation_boundary':'Observed copy and supplied labels only. Exact label overlap is a research signal, not proof that the competitor promise caused the review issue.'
        }
        competitors.append(row)
        for theme in exact_overlap:
            overlaps.append({'competitor':comp,'theme':theme,'signal':'EXACT_LABEL_OVERLAP','why':'The same supplied theme label appears in competitor messaging and review themes; inspect source listings/reviews before treating it as an expectation gap.','decision_status':'RESEARCH_HYPOTHESIS'})
    competitors.sort(key=lambda x:x['listing_count'],reverse=True)
    return {
        'status':'AGGREGATED_FROM_SUPPLIED_LISTING_FIELDS','row_count':len(rows),'competitors':competitors,
        'message_theme_summary':[{'theme':k,'observed_weight':round(v,6)} for k,v in theme_total.most_common(50)],
        'offer_type_summary':[{'offer_type':k,'count':v} for k,v in offer_total.most_common(50)],
        'proof_type_summary':[{'proof_type':k,'count':v,'source_ids':sorted(proof_sources.get(k,set()))} for k,v in proof_total.most_common(50)],
        'message_review_overlap':overlaps,
        'note':'Competitor intelligence is evidence-linked and source-bounded. Missing theme/proof/offer labels stay missing rather than being guessed from marketing prose.'
    }

def market_opportunity_hypotheses(analysis:dict[str,Any]) -> list[dict[str,Any]]:
    out=[]
    conc=analysis.get('concentration') or {}
    if conc.get('cr3') is not None:
        out.append({'hypothesis':'CONCENTRATION_POSITIONING','signal':f"CR3={conc.get('cr3')} / CR10={conc.get('cr10')} / HHI={conc.get('hhi')}",'interpretation':'Use concentration to decide whether differentiation must challenge dominant sellers or exploit fragmented search/offer demand.','why':'Concentration changes entry strategy, but is not itself a go/no-go rule.','requires':['competitor messaging/offer comparison','product-fit evidence']})
    for v in analysis.get('price_valley_signals',[])[:5]:
        out.append({'hypothesis':'PRICE_BAND_GAP','signal':v,'interpretation':'Check whether this low-density price band represents an unmet offer or simply weak demand.','why':'A valley becomes actionable only after margin, configuration and buyer-value fit are checked.','requires':['unit economics','configuration fit','keyword/consumer demand']})
    for c in analysis.get('configuration',[])[:5]:
        out.append({'hypothesis':'CONFIGURATION_EFFICIENCY','signal':c,'interpretation':'High units-per-item configurations may indicate efficient buyer fit or lower assortment crowding.','why':'Configuration efficiency can guide SKU/offer design when supported by sufficient sample coverage.','requires':['own-SKU cost/logistics','review/return themes']})
    kw=(analysis.get('keyword_demand') or {}).get('top_terms',[])
    if kw:
        out.append({'hypothesis':'SEARCH_DEMAND_ALIGNMENT','signal':kw[:10],'interpretation':'Prioritize terms where demand evidence and truthful product relevance overlap; do not chase high-volume terms that distort product identity.','why':'Search demand only creates value when the offer can satisfy the underlying intent.','requires':['listing relevance','claim/product truth']})
    cv=(analysis.get('customer_voice') or {}).get('theme_summary',[])
    classified=[x for x in cv if x.get('theme')!='UNCLASSIFIED']
    if classified:
        out.append({'hypothesis':'CUSTOMER_TENSION_ALIGNMENT','signal':classified[:10],
                    'interpretation':'Use repeated supplied review themes to identify purchase tensions, expectation gaps and competitor weaknesses that the truthful offer may address.',
                    'why':'Customer voice connects market structure to the language and risks buyers actually report, but supplied themes remain sampled evidence rather than population truth.',
                    'requires':['product truth fit','review collection scope/representativeness','listing and feedback validation']})
    ci=analysis.get('competitor_listing_intelligence') or {}
    if ci.get('competitors'):
        out.append({'hypothesis':'COMPETITOR_MESSAGE_OFFER_MAP','signal':ci.get('competitors',[])[:10],
                    'interpretation':'Compare observed competitor message themes, offer types and proof types with their review themes before selecting a differentiation territory.',
                    'why':'Structural market data shows who/where competitors are; listing+review evidence shows what they promise and where buyer expectations may remain unresolved.',
                    'requires':['own product truth fit','source-level competitor review','claim/legal boundary','current-platform freshness']})
    return out


def opportunity_map(analysis:dict[str,Any]) -> list[dict[str,Any]]:
    """Create evidence-linked candidate opportunity cards; no automatic go/no-go score."""
    out=[]
    quality=(analysis.get('data_quality') or {}).get('completeness_ratio',0)
    rq=analysis.get('research_quality') or {}; source_cards=rq.get('sources') or []
    source_limited=bool(rq.get('unresolved_source_ids') or rq.get('stale_by_declared_threshold') or rq.get('scope_mismatch_source_ids'))
    rep_unknown=bool(source_cards) and any(x.get('representativeness_status')!='REPRESENTATIVENESS_DOCUMENTED_NOT_PROVEN' for x in source_cards)
    if quality>=0.9 and not source_limited and not rep_unknown and source_cards: confidence='HIGH'
    elif quality>=0.7 and not source_limited: confidence='MEDIUM'
    else: confidence='LOW'
    for i,h in enumerate(analysis.get('opportunity_hypotheses',[]),1):
        out.append({'opportunity_id':f'OPP-{i:02d}','type':h.get('hypothesis'),'signal':h.get('signal'),'interpretation':h.get('interpretation'),'why':h.get('why'),'data_confidence':confidence,'research_quality_status':rq.get('status'),'representativeness_boundary':'Documented sampling metadata is not proof of population representativeness; validate before generalizing beyond the declared sample frame.','cross_checks_required':h.get('requires',[]),'decision_status':'HYPOTHESIS_NOT_RECOMMENDATION'})
    return out


def analyze_market(rows: list[dict[str, Any]], price_step: float | None = None, config_key='configuration', keyword_rows:list[dict[str,Any]]|None=None, field_map:dict[str,str]|None=None, review_rows:list[dict[str,Any]]|None=None, competitor_listing_rows:list[dict[str,Any]]|None=None, source_records:list[dict[str,Any]]|None=None, as_of:str|None=None, research_scope:dict[str,Any]|None=None, ingestion_config:dict[str,Any]|None=None) -> dict[str, Any]:
    raw_rows=list(rows or [])
    raw_keywords=list(keyword_rows or [])
    raw_reviews=list(review_rows or [])
    raw_competitor=list(competitor_listing_rows or [])
    ingestion=compile_research_ingestion({'market_rows':raw_rows,'keyword_rows':raw_keywords,'review_rows':raw_reviews,'competitor_listing_rows':raw_competitor},source_records,ingestion_config)
    effective=ingestion.pop('_canonical_datasets',{})
    if str(ingestion.get('dedup_mode')).upper()=='EXACT_SOURCE_ROW':
        raw_rows=list(effective.get('market_rows') or [])
        raw_keywords=list(effective.get('keyword_rows') or [])
        raw_reviews=list(effective.get('review_rows') or [])
        raw_competitor=list(effective.get('competitor_listing_rows') or [])
        rows=raw_rows; keyword_rows=raw_keywords; review_rows=raw_reviews; competitor_listing_rows=raw_competitor
    normalized=normalize_market_rows(raw_rows,field_map)
    rows=normalized['rows']
    prices=[float(r['price']) for r in rows if r.get('price') not in (None,'')]
    units=sum(_f(r.get('units'),0) for r in rows)
    revenue=sum(_f(r.get('revenue'), _f(r.get('price'),0)*_f(r.get('units'),0)) for r in rows)
    bands=price_band_analysis(rows,price_step)
    missing_fields={k:sum(1 for r in rows if r.get(k) in (None,'')) for k in ['seller','price','units','revenue',config_key]}
    keyword_input=keyword_rows or [r for r in rows if r.get('keyword')]
    customer_voice=customer_voice_analysis(review_rows)
    result={
        'status':'CALCULATED_FROM_INPUT_ROWS',
        'row_count':len(rows),
        'normalization':{'status':normalized['status'],'row_count':normalized['row_count'],'provenance':normalized['provenance'][:50]},
        'market_capacity':{'units':round(units,6),'revenue':round(revenue,6),'scope':'SUPPLIED_SAMPLE_ONLY'},
        'price_summary':{'min':min(prices) if prices else None,'median':median(prices) if prices else None,'max':max(prices) if prices else None},
        'concentration':concentration_from_rows(rows),
        'price_bands':bands,
        'price_valley_signals':detect_price_valleys(bands),
        'configuration':configuration_analysis(rows,config_key),
        'price_configuration_matrix':price_configuration_matrix(rows,config_key,price_step),
        'seller_efficiency':seller_efficiency(rows),
        'competitors':competitor_snapshot(rows),
        'competitor_clusters':competitor_clusters(rows,config_key),
        'keyword_demand':keyword_demand_analysis(keyword_input),
        'customer_voice':customer_voice,
        'competitor_listing_intelligence':competitor_listing_analysis(competitor_listing_rows,customer_voice),
        'research_ingestion':ingestion,
        'research_quality':research_source_quality({'market_rows':raw_rows,'keyword_rows':raw_keywords,'review_rows':raw_reviews,'competitor_listing_rows':raw_competitor},source_records,as_of,research_scope),
        'data_quality':{'missing_fields':missing_fields,'completeness_ratio':round(1-(sum(missing_fields.values())/(max(1,len(rows))*len(missing_fields))),4) if rows else 0,'representativeness':'UNKNOWN_UNLESS_SUPPLIED','note':'Results describe supplied rows only; representativeness and collection bias remain evidence questions.'},
    }
    result['opportunity_hypotheses']=market_opportunity_hypotheses(result)
    result['opportunity_map']=opportunity_map(result)
    return result


# Backward-compatible entry point.
def metrics(rows):
    return analyze_market(rows)
