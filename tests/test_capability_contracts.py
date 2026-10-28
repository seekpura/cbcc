from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def test_capability_ledger_has_behavioral_evidence():
    d=yaml.safe_load((ROOT/'references/capability_ledger.yaml').read_text(encoding='utf-8'))
    assert d['version']>=3
    for c in d['capabilities']:
        if not c.get('required'): continue
        assert c['trigger_examples'] and c['runtime_consumers'] and c['behavior_test'] and c['e2e_evidence']
        for rel in c['runtime_consumers']+c['implementation_paths']:
            assert (ROOT/rel).exists(), (c['id'],rel)
        assert c['maturity'] in {'RUNTIME_VERIFIED','CONTRACT_VERIFIED'}
