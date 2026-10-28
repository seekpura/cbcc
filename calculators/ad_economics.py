#!/usr/bin/env python3
"""Backward-compatible CLI over canonical runtime economics helpers."""
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.tools.economics import break_even_roas, allowable_cpc

p=argparse.ArgumentParser(); p.add_argument('--price',type=float,required=True); p.add_argument('--pre-ad-contribution',type=float,required=True); p.add_argument('--cvr',type=float,required=True,help='0-1')
a=p.parse_args()
# Construct a zero-fee canonical cost contract whose pre-ad contribution equals the historical input.
landed=max(0.0,a.price-a.pre_ad_contribution)
costs={'landed_cost':landed,'platform_fee':0,'fulfillment':0,'affiliate_commission':0,'ad_cost':0,'tax':0,'refund_allowance':0}
out={'break_even_roas':break_even_roas(a.price,a.pre_ad_contribution),'allowable_cpc':allowable_cpc(a.price,costs,a.cvr,0),'runtime_authority':'cbcc.tools.economics'}
print(json.dumps(out,indent=2))
