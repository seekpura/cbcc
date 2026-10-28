#!/usr/bin/env python3
"""Backward-compatible descriptive CLI over the canonical experiment helper."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from cbcc.tools.experiment import relative_change
p=argparse.ArgumentParser(); p.add_argument('--baseline',type=float,required=True); p.add_argument('--variant',type=float,required=True); a=p.parse_args()
print(json.dumps({'baseline':a.baseline,'variant':a.variant,'relative_change':relative_change(a.baseline,a.variant),'runtime_authority':'cbcc.tools.experiment.relative_change','boundary':'Descriptive change only; no significance or causality is implied.'},indent=2))
