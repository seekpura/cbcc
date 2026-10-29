from pathlib import Path


def test_v0631_release_version_and_depth_contract_are_active():
    root=Path(__file__).resolve().parents[1]
    assert (root/'VERSION').read_text(encoding='utf-8').strip()=='0.6.31-model-native-prompt-integrity'
    delivery=(root/'runtime/cbcc/delivery_contract.py').read_text(encoding='utf-8')
    assert 'FULL_DECISION_DEPTH_V2_CARRIER_AWARE_NO_SILENT_COMPRESSION' in delivery
    skill=(root/'SKILL.md').read_text(encoding='utf-8')
    assert 'Model-Native Prompt + Human Depth Authority' in skill
