from pathlib import Path
import subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1]
def test_v030_capability_floor_preserved():
    for rel in ['references/PHOTOGRAPHY_CMF_SPEC.md','references/DECISION_SYSTEM_SPEC.md','references/CREATIVE_SYSTEM_SPEC.md','references/SURFACE_ARCHITECTURE.md','references/PROMPT_STATE_ISOLATION.md','references/CONVERSATION_REQUIREMENT_AUDIT.md']:
        assert (ROOT/rel).exists()
    ids={x['id'] for x in yaml.safe_load((ROOT/'references/capability_ledger.yaml').read_text(encoding='utf-8'))['capabilities']}
    for k in ['RACE','STP_JTBD','DECISION_MODELS','RACE_ETHNICITY','INTERSECTIONALITY','CMF','PHOTOGRAPHY','SURFACES','TOOLKITS','POSITIVE_FIRST']:
        assert k in ids
