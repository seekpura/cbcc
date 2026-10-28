#!/usr/bin/env python3
"""Backward-compatible CLI over the canonical runtime economics engine.

This file intentionally contains no independent unit-economics formula. The runtime engine is
`cbcc.tools.economics`; this wrapper only maps the historical CLI flags into its cost contract.
"""
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.tools.economics import unit_economics

p=argparse.ArgumentParser()
p.add_argument('--price',type=float,required=True); p.add_argument('--cost',type=float,required=True)
for k in ['platform_fee_pct','payment_fee_pct','return_pct','tax_pct','ad_pct']:
    p.add_argument('--'+k.replace('_','-'),dest=k,type=float,default=0)
p.add_argument('--fixed-fee',type=float,default=0); p.add_argument('--logistics',type=float,default=0)
a=p.parse_args()
costs={
    'landed_cost':a.cost,
    'platform_fee':{'type':'rate','value':(a.platform_fee_pct+a.payment_fee_pct)/100},
    'fulfillment':a.fixed_fee+a.logistics,
    'affiliate_commission':0,
    'ad_cost':{'type':'rate','value':a.ad_pct/100},
    'tax':{'type':'rate','value':a.tax_pct/100},
    'refund_allowance':{'type':'rate','value':a.return_pct/100},
}
r=unit_economics(a.price,costs,0)
out={'contribution':r.get('contribution'),'net_margin':r.get('contribution_margin'),'pre_ad_contribution':r.get('contribution_before_ads'),'break_even_roas':r.get('break_even_roas'),'runtime_authority':'cbcc.tools.economics.unit_economics'}
print(json.dumps(out,indent=2))
