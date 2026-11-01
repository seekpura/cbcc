from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

MODULE = Path(__file__).parents[1] / 'runtime/cbcc/information_audit_authority.py'
spec = importlib.util.spec_from_file_location('information_audit_authority_v0676_alias', MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def test_full_project_alias_remains_full_for_information_audit_wrapper():
    def base(request, *args, **kwargs):
        return {
            'human_projection': {'mode':'FULL_PROJECT'},
            'sections': {
                '01_information_completeness_assumptions_decisions': {
                    'required_missing':['cost'],
                    'pending_confirmations':[],
                    'assumptions':[],
                    'decision_log':[],
                },
                '02_product_truth_value_ladder': {'product_facts':[]},
            },
        }
    out = mod.wrap_build_master_strategy(base)({'sources':[]})
    info = out['sections']['01_information_completeness_assumptions_decisions']
    assert info['schema'] == 'cbcc-information-audit-authority-v1'
    assert mod.information_audit_issues(out) == []


def test_task_scoped_alias_does_not_get_full_authority_enforcement():
    strategy = {
        'human_projection': {'mode':'TASK_SCOPED'},
        'sections': {'01_information_completeness_assumptions_decisions': {'required_missing':['cost']}},
    }
    assert mod.information_audit_issues(strategy) == []
