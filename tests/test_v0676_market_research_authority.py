from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

MODULE = Path(__file__).parents[1] / 'runtime/cbcc/market_research_authority.py'
spec = importlib.util.spec_from_file_location('market_research_authority', MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def sample_market():
    return {
        'status': 'CALCULATED_FROM_INPUT_ROWS',
        'row_count': 3,
        'market_capacity': {'units': 120.0, 'revenue': 3600.0, 'scope': 'SUPPLIED_SAMPLE_ONLY'},
        'price_summary': {'min': 20.0, 'median': 30.0, 'max': 40.0},
        'price_bands': [{'lower':20.0,'upper':30.0,'items':1,'units':30.0,'revenue':600.0}],
        'price_configuration_matrix': [{'cluster_id':'MID::30g','price_tier':'MID_PRICE','configuration':'30g','items':2}],
        'concentration': {'cr3': 72.0, 'cr10': 100.0, 'hhi': 2100.0, 'seller_count': 5},
        'keyword_demand': {'status':'AGGREGATED_FROM_INPUT','top_terms':[
            {'term':'oil control gel','volume':900.0,'avg_competition':0.4,'intent':'PROBLEM','source_ids':['SRC-SEARCH']}
        ]},
        'customer_voice': {'status':'AGGREGATED_FROM_SUPPLIED_LABELS','theme_summary':[
            {'theme':'sticky feel','weighted_mentions':18.0,'dominant_sentiment':'NEGATIVE','source_ids':['SRC-REV']},
            {'theme':'light texture','weighted_mentions':10.0,'dominant_sentiment':'POSITIVE','source_ids':['SRC-REV']},
        ]},
        'competitor_listing_intelligence': {'status':'AGGREGATED_FROM_SUPPLIED_LISTING_FIELDS','competitors':[
            {'competitor':'Brand A','listing_count':3,'source_ids':['SRC-COMP']}
        ], 'message_theme_summary':[{'theme':'oil control','observed_weight':3.0}]},
        'opportunity_map': [{
            'opportunity_id':'OPP-01','type':'CUSTOMER_TENSION_ALIGNMENT','signal':{'theme':'sticky feel','source_ids':['SRC-REV']},
            'interpretation':'Investigate a truthful non-sticky positioning territory.','why':'Repeated supplied review theme.',
            'data_confidence':'MEDIUM','decision_status':'HYPOTHESIS_NOT_RECOMMENDATION',
            'cross_checks_required':['product truth fit']
        }],
        'research_quality': {
            'status':'SOURCE_QUALITY_COMPILED',
            'as_of':'2026-10-30',
            'datasets':[
                {'dataset':'market_rows','row_count':3,'source_ids':['SRC-MKT'],'source_id_coverage_ratio':1.0,'resolved_source_ratio':1.0},
                {'dataset':'keyword_rows','row_count':1,'source_ids':['SRC-SEARCH'],'source_id_coverage_ratio':1.0,'resolved_source_ratio':1.0},
                {'dataset':'review_rows','row_count':2,'source_ids':['SRC-REV'],'source_id_coverage_ratio':1.0,'resolved_source_ratio':1.0},
                {'dataset':'competitor_listing_rows','row_count':1,'source_ids':['SRC-COMP'],'source_id_coverage_ratio':1.0,'resolved_source_ratio':1.0},
            ],
            'sources':[
                {'source_id':'SRC-MKT','kind':'MARKET_EXPORT','observed_at':'2026-10-25','freshness_status':'WITHIN_DECLARED_FRESHNESS_WINDOW','representativeness_status':'REPRESENTATIVENESS_DOCUMENTED_NOT_PROVEN','scope_mismatches':[],'source_quality_status':'EXPLICIT_TIER_SUPPLIED','source_quality_tier':'MEDIUM'},
                {'source_id':'SRC-SEARCH','kind':'SEARCH_EXPORT','observed_at':'2026-10-28','freshness_status':'WITHIN_DECLARED_FRESHNESS_WINDOW','representativeness_status':'REPRESENTATIVENESS_DOCUMENTED_NOT_PROVEN','scope_mismatches':[],'source_quality_status':'EXPLICIT_TIER_SUPPLIED','source_quality_tier':'MEDIUM'},
                {'source_id':'SRC-REV','kind':'REVIEW_EXPORT','observed_at':'2026-10-29','freshness_status':'WITHIN_DECLARED_FRESHNESS_WINDOW','representativeness_status':'REPRESENTATIVENESS_DOCUMENTED_NOT_PROVEN','scope_mismatches':[],'source_quality_status':'EXPLICIT_TIER_SUPPLIED','source_quality_tier':'MEDIUM'},
                {'source_id':'SRC-COMP','kind':'COMPETITOR_LISTING','observed_at':'2026-10-29','freshness_status':'WITHIN_DECLARED_FRESHNESS_WINDOW','representativeness_status':'REPRESENTATIVENESS_DOCUMENTED_NOT_PROVEN','scope_mismatches':[],'source_quality_status':'EXPLICIT_TIER_SUPPLIED','source_quality_tier':'MEDIUM'},
            ],
            'unresolved_source_ids':[], 'stale_by_declared_threshold':[], 'scope_mismatch_source_ids':[],
        },
        'data_quality': {'completeness_ratio':0.95,'representativeness':'UNKNOWN_UNLESS_SUPPLIED'},
    }


def test_all_required_research_domains_are_explicit():
    out = mod.compile_market_research_authority(sample_market())
    assert set(out['domains']) == {'DEMAND','SEARCH','COMPETITION','PRICE_BAND','REVIEWS','NEGATIVE_REVIEWS','OPPORTUNITY','RISK'}
    assert all(out['domains'][name]['status'] for name in out['domains'])


def test_evidenced_findings_have_density_and_lineage_fields():
    out = mod.compile_market_research_authority(sample_market())
    rows = [row for domain in out['domains'].values() for row in domain['findings'] if row['status'] == 'EVIDENCED']
    assert rows
    required = {'what','why','evidence','tradeoff','execution','measurement','exact_fact','interpretation','confidence','assumption_boundary','downstream_use','conflict_status'}
    assert all(required <= set(row) for row in rows)
    assert all(row['evidence']['source_ids'] for row in rows)
    assert all(row['evidence']['source_cards'] for row in rows)


def test_negative_review_opportunity_uses_explicit_negative_label_only():
    out = mod.compile_market_research_authority(sample_market())
    neg = out['domains']['NEGATIVE_REVIEWS']
    assert neg['status'] == 'EVIDENCED'
    assert any(row['exact_fact']['theme'] == 'sticky feel' for row in neg['findings'])
    assert not any(row.get('exact_fact',{}).get('theme') == 'light texture' for row in neg['findings'])


def test_missing_research_stays_to_verify_without_fabricated_numbers():
    out = mod.compile_market_research_authority({})
    assert all(domain['status'] in {'TO_VERIFY','MISSING_INPUT'} for domain in out['domains'].values())
    assert out['status'] == 'RESEARCH_INPUT_REQUIRED'
    assert all(not domain['findings'] or all(row.get('exact_fact') in (None,{}) for row in domain['findings']) for domain in out['domains'].values())
    assert all(row.get('confidence') == 'LOW' for domain in out['domains'].values() for row in domain['findings'])


def test_stale_or_scope_mismatched_sources_are_risk_and_low_confidence():
    market = sample_market()
    market['research_quality']['sources'][0]['freshness_status'] = 'OUTSIDE_DECLARED_FRESHNESS_WINDOW'
    market['research_quality']['sources'][0]['scope_mismatches'] = [{'field':'market','expected':'MY','actual':'SG'}]
    market['research_quality']['stale_by_declared_threshold'] = ['SRC-MKT']
    market['research_quality']['scope_mismatch_source_ids'] = ['SRC-MKT']
    out = mod.compile_market_research_authority(market)
    demand = out['domains']['DEMAND']['findings'][0]
    assert demand['confidence'] == 'LOW'
    risks = out['domains']['RISK']['findings']
    assert any('SRC-MKT' in row['evidence']['source_ids'] for row in risks)


def test_wrapper_attaches_authority_to_real_market_analysis_shape():
    def legacy(*args, **kwargs):
        return sample_market()
    wrapped = mod.wrap_analyze_market(legacy)
    out = wrapped([])
    assert out['research_authority']['schema'] == 'cbcc-market-research-authority-v1'
    assert out['research_authority']['domains']['SEARCH']['status'] == 'EVIDENCED'
    assert getattr(wrapped, '_cbcc_v0676_market_research_authority', False) is True
