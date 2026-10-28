#!/usr/bin/env python3
"""Backward-compatible CSV CLI over the canonical market engine."""
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.tools.market import analyze_market

p=argparse.ArgumentParser(); p.add_argument('csv'); p.add_argument('--sales-col',default='sales'); p.add_argument('--revenue-col',default='revenue'); p.add_argument('--entity-col',default='seller')
a=p.parse_args(); rows=list(csv.DictReader(open(a.csv,encoding='utf-8-sig')))
r=analyze_market(rows,field_map={'units':a.sales_col,'revenue':a.revenue_col,'seller':a.entity_col})
c=r.get('concentration') or {}; cap=r.get('market_capacity') or {}
out={'rows':r.get('row_count'),'sales_total':cap.get('units'),'revenue_total':cap.get('revenue'),'cr3':None if c.get('cr3') is None else c.get('cr3')/100,'cr10':None if c.get('cr10') is None else c.get('cr10')/100,'hhi':c.get('hhi'),'runtime_authority':'cbcc.tools.market.analyze_market'}
print(json.dumps(out,indent=2))
