#!/usr/bin/env python3
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1])); import _bootstrap
from cbcc.tools.experiment import evaluate_binary_experiment
p=argparse.ArgumentParser(); p.add_argument('input_json'); a=p.parse_args(); d=json.loads(Path(a.input_json).read_text(encoding='utf-8'))
print(json.dumps(evaluate_binary_experiment(d['control_success'],d['control_total'],d['test_success'],d['test_total'],d.get('alpha',0.05),d.get('min_relative_lift')),ensure_ascii=False,indent=2))
