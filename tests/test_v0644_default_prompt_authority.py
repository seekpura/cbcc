from scripts import build_plugin_dist_v0644 as v0644


def test_manifest_omits_default_prompt_when_no_invocation_prompt_is_needed():
    manifest = v0644.plugin_manifest('0.6.44')
    interface = manifest['extensions']['com.openai']['interface']
    assert 'defaultPrompt' not in interface


def test_v0644_moves_all_business_authority_into_skill():
    assert v0644.DEFAULT_PROMPTS == []
    text = v0644.AUTHORITY_BOUNDARY
    assert 'Default Prompt Is Not Authority' in text
    assert 'Host Skill / Canonical Skill' in text
    assert '业务规则' in text
    assert 'defaultPrompt' in text


def test_v0644_keeps_current_business_contracts_in_skill_authority():
    text = v0644.AUTHORITY_BOUNDARY + '\n' + v0644.CHINESE_INTERPRETATION_AUTHORITY
    assert '中文释义' in text
    assert 'Host Skill / Canonical Skill' in text
    assert '升级只能做加法' in text
