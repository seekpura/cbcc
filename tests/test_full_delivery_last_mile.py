

def test_full_export_revalidates_depth_and_materializes_visible_audits(tmp_path:Path):
    project=tmp_path/'project'
    build_project(project,_request(),_pack(tmp_path))
    out=tmp_path/'delivery'
    manifest=export_delivery_package(project,out)

    depth=json.loads((out/'FULL_DELIVERY_DEPTH_AUDIT.json').read_text(encoding='utf-8'))
    prompt=json.loads((out/'PROMPT_CONSUMPTION_AUDIT.json').read_text(encoding='utf-8'))
    language=json.loads((out/'HUMAN_LANGUAGE_AUDIT.json').read_text(encoding='utf-8'))
    html=(out/'index.html').read_text(encoding='utf-8')

    assert depth['mode']=='FULL'
    assert depth['status']=='PASS', depth
    assert depth['depth_contract']=='FULL_DECISION_DEPTH_V2_CARRIER_AWARE_NO_SILENT_COMPRESSION'
    # Prompt/generation readiness remains visible for production work, but it is not a FULL-project gate.
    assert prompt['status']=='READY', prompt
    assert prompt['project_completion_blocking'] is False
    assert language['status']=='PASS', language
    for token in [
        '信息完整度、待确认清单、假设与决策日志',
        '产品真实事实审计与卖点分级表',
        '平台 × 区域 × 人群 × 族裔文化洞察',
        '营销框架与核心策略',
        '视觉总策略与拍摄执行清单',
    ]:
        assert token in html
    assert manifest['complete_human_delivery'] is True
