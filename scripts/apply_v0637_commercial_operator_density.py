from __future__ import annotations

from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]


def read(rel:str)->str:
    return (ROOT/rel).read_text(encoding='utf-8')


def write(rel:str,text:str)->None:
    (ROOT/rel).write_text(text,encoding='utf-8')


def replace_if_present(text:str,old:str,new:str)->str:
    return text.replace(old,new) if old in text else text


def patch_init()->None:
    rel='runtime/cbcc/__init__.py'; text=read(rel)
    import_line='from . import commercial_operator_density_authority as _commercial_operator_density_authority\n'
    marker='from . import reference_guided_native_authority as _reference_guided_native_authority\n'
    if import_line not in text:
        if marker not in text: raise RuntimeError('reference authority import marker missing')
        text=text.replace(marker,marker+import_line,1)
    wrap='''_agent_authority_prompt_compiler.compile_asset_prompt = _commercial_operator_density_authority.wrap_compile_asset_prompt(\n    _agent_authority_prompt_compiler.compile_asset_prompt\n)\n'''
    assign='_legacy_prompt_compiler.compile_asset_prompt = _agent_authority_prompt_compiler.compile_asset_prompt\n'
    if wrap not in text:
        if assign not in text: raise RuntimeError('legacy assignment marker missing')
        text=text.replace(assign,wrap+assign,1)
    write(rel,text)


def patch_base_prompt_compiler()->None:
    rel='runtime/cbcc/prompt_compiler.py'; text=read(rel)
    text=replace_if_present(
        text,
        'Reserve deliberate copy zones in generation. Exact approved copy is composed deterministically after image generation unless selected renderer has verified exact-text capability.',
        'Use the Agent-selected copy route. Integrated model-rendered copy is allowed and preferred when it best serves the final asset; post-composite typography is explicit-only when selected for fidelity, editability, platform or provider reasons.'
    )
    text=replace_if_present(
        text,
        'Reserve deliberate layout zones for locked copy, but do not ask the image model to retype packaging or final marketing copy. Exact approved text is composed deterministically after generation.',
        'Follow the Agent-selected copy-render route. When MODEL_RENDER or HYBRID is selected, render approved market copy directly and exactly as part of the finished commercial image. Use post-composite typography only when explicitly selected.'
    )
    text=replace_if_present(
        text,
        '为锁定文案保留明确排版区，但不要让图像模型重新输入包装文字或最终营销文案；精确批准文案在生成后确定性合成。',
        '遵循 Agent 选择的文案渲染路线；当选择 MODEL_RENDER 或 HYBRID 时，把批准的市场文案作为最终商业画面的一部分直接、准确生成；只有明确选择后期合成时才保留后期文字路线。'
    )
    text=text.replace("'deterministic_text_composition': bool(locked_copy),","'deterministic_text_composition': False,")
    text=text.replace("'exact_copy_mode': 'DETERMINISTIC_COMPOSITION_AFTER_RENDER',","'exact_copy_mode': 'AGENT_PROVIDER_SELECTED',")
    write(rel,text)


def patch_model_native_contract()->None:
    rel='runtime/cbcc/model_native_prompt_contract.py'; text=read(rel)
    old="""    # Choosing whether exact copy is rendered by the model or composed later is a production decision.\n    # Runtime does not silently choose POST_COMPOSITE for every asset/provider.\n    return 'UNRESOLVED_AGENT_DECISION'\n"""
    new="""    # v0.6.37: normal production choices are resolved autonomously. Integrated native\n    # rendering is the default for visible market copy; POST_COMPOSITE remains explicit-only.\n    return 'MODEL_RENDER'\n"""
    text=replace_if_present(text,old,new)
    write(rel,text)


def patch_reference_authority()->None:
    rel='runtime/cbcc/reference_guided_native_authority.py'; text=read(rel)
    repeated="""    if visible and not exact:\n        closure['locked_source_final_composite_instruction']=False\n    if visible and not exact:\n        closure['locked_source_final_composite_instruction']=False\n    if visible and not exact:\n        closure['locked_source_final_composite_instruction']=False\n    if visible and not exact:\n        closure['locked_source_final_composite_instruction']=False\n"""
    single="""    if visible and not exact:\n        closure['locked_source_final_composite_instruction']=False\n"""
    text=replace_if_present(text,repeated,single)
    write(rel,text)


def patch_skill()->None:
    rel='SKILL.md'; text=read(rel)
    text=text.replace('version: 0.6.36-seven-tool-capability-continuity','version: 0.6.37-commercial-operator-density')
    section='''## Autonomous Integrated Render + Operator Density Authority — highest current precedence\n- **默认一体出图。** 对最终商业视觉，宿主 Agent 默认拥有完整制作权：商品、目标市场文字、排版、场景、人物、道具、证据图形、摄影/灯光/CMF、材质和 finishing 可以在同一次完整生成中共同完成。`POST_COMPOSITE / EXACT_PIXEL_COMPOSITE / NO_VISIBLE_COPY / PRODUCT_ABSENT` 都是按资产目的选择的专业路线，不是全局默认。\n- **限制是例外。** 只有用户明确锁定、Product Truth/Claim/合规/平台硬规则、明确 exact-pixel/post-composite 路线或真实 Provider 能力限制，才形成硬限制。不得因历史工作流默认写入“不要生成文字 / 不要生成商品 / 只做背景 / 必须留文字区 / 商品必须后期贴入”。\n- **正常专业选择由 Agent 自主闭环。** Product Presence、copy-render route、visual carrier、构图、Camera/Lighting/CMF、Hook、测试变体等只要已有足够上下文，就由 Agent 直接决定并执行，不得变成运营人员的技术门禁。只有会迫使事实虚构、违规发布、错误花钱或 Provider 无法执行的缺口才允许 `NEEDS_HARD_INPUT / HOLD_COMPLIANCE / STOP_ECONOMICS`。\n- **商业 Prompt 必须达到 production brief 密度。** 当相关时至少消费 commerce objective、creative thesis、product role/reference、decisive scene、composition geometry、integrated typography、evidence representation、camera/perspective、lighting、CMF/material response、color/grade、human/culture、surface behavior、truth boundary、variant hypothesis。禁止用 `premium/editorial/clean/soft light` 等空泛词替代设计。\n- **视频同样由 Agent 作者化。** 不允许把所有视频固定成 hook→reveal→proof→close→CTA 五段模板；Narrative carrier、first-frame、product timing、creator/human、shot/action、camera/motion、copy/VO/subtitle、sound、cover、landing handoff 与测试差异按真实 shopper tension 和商业假设动态决定。\n- **Provider 完成不等于视觉完成。** 最终成图/成片必须检查商品身份、文字准确与可读、第一眼商业答案、构图/裁切、材质物理、人体/手部交互、时间连续性、声音/字幕、伪影、证据/Claim真实性、品牌连续性、与相邻测试资产的差异、平台可用性；失败后走最小局部修复/重新生成/换 reference/换 provider。\n- **运营交付是主界面。** 每个一等工具必须最终给出“做什么、在哪做、用什么最终对象、为什么、什么不动、做到什么算完成、看什么数决定下一步”。Runtime/Consumer/Trace 属于二级 Inspector；不能让运营拿到的主要内容是 Gate、状态码和模块证明。\n- 权威 Prompt：`prompts/commercial_visual_generation_authority.md`、`prompts/commercial_video_generation_authority.md`、`prompts/operator_execution_density.md`。\n\n'''
    marker='## Seven First-Class Commerce Tools + Pricing/Economics Integrity — highest current precedence\n'
    if '## Autonomous Integrated Render + Operator Density Authority' not in text:
        if marker not in text: raise RuntimeError('SKILL insertion marker missing')
        text=text.replace(marker,section+marker,1)
    write(rel,text)


def patch_registry()->None:
    rel='prompts/registry.json'; data=json.loads(read(rel))
    data['version']='0.6.37-commercial-operator-density'
    prompts=data.setdefault('prompts',[])
    additions=[
        {'id':'PROMPT-COMMERCIAL-INTEGRATED-VISUAL','path':'commercial_visual_generation_authority.md','purpose':'Default integrated native commercial image authority: product/copy/layout/scene/evidence/photography/materials + output QA; restrictions are explicit exceptions.'},
        {'id':'PROMPT-COMMERCIAL-VIDEO','path':'commercial_video_generation_authority.md','purpose':'Dynamic commercial video narrative, shot/action/motion/copy/audio/cover/testing production authority without a fixed five-beat template.'},
        {'id':'PROMPT-OPERATOR-EXECUTION-DENSITY','path':'operator_execution_density.md','purpose':'Convert all first-class tool outputs into Chinese-first, directly executable operator objects and business release states.'},
    ]
    ids={x.get('id') for x in prompts}
    for item in additions:
        if item['id'] not in ids: prompts.append(item)
    write(rel,json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def patch_strategy_sources()->None:
    rel='runtime/cbcc/strategy_sources.py'; text=read(rel)
    old="wanted_prompts={'PROMPT-MASTER-STRATEGY','PROMPT-SKU-OFFER','PROMPT-POSITIONING','PROMPT-VISUAL-PHOTO','PROMPT-PLATFORM-MATRIX','PROMPT-ASSET-CURATION','PROMPT-CULTURE','PROMPT-CREATIVE-SURFACE-CANONICAL'}"
    new="wanted_prompts={'PROMPT-MASTER-STRATEGY','PROMPT-SKU-OFFER','PROMPT-POSITIONING','PROMPT-VISUAL-PHOTO','PROMPT-PLATFORM-MATRIX','PROMPT-ASSET-CURATION','PROMPT-CULTURE','PROMPT-CREATIVE-SURFACE-CANONICAL','PROMPT-COMMERCIAL-INTEGRATED-VISUAL','PROMPT-OPERATOR-EXECUTION-DENSITY'}"
    text=replace_if_present(text,old,new)
    video_selector="""    if request.get('video_jobs') or any(str(x).upper() in {'VIDEO','PDP_VIDEO','CREATOR','LIVE','SOCIAL_CONTENT'} for x in ((request.get('target') or {}).get('surfaces') or [])): wanted_prompts.add('PROMPT-COMMERCIAL-VIDEO')\n"""
    marker="    if 'measurement' in domains: wanted_prompts.add('PROMPT-MEASUREMENT')\n"
    if video_selector not in text:
        if marker not in text: raise RuntimeError('strategy prompt selector marker missing')
        text=text.replace(marker,marker+video_selector,1)
    write(rel,text)


def patch_compiler()->None:
    rel='runtime/cbcc/compiler.py'; text=read(rel)
    import_line='from .operator_execution_board import build_operator_execution_board\n'
    marker='from .seven_tool_continuity import compile_seven_tool_continuity\n'
    if import_line not in text:
        if marker not in text: raise RuntimeError('compiler import marker missing')
        text=text.replace(marker,marker+import_line,1)
    insert="""    operator_execution_board=build_operator_execution_board(\n        request=request,domain=domain,strategy=strategy,architecture=architecture,video_plan=video_plan,\n        paid_campaigns=paid_campaigns,agent_next_action=agent_next_action,compliance=compliance,\n        asset_compile=asset_compile,production_run=production_run,\n    )\n    _write(p/'artifacts/operator_execution_board.json',operator_execution_board)\n\n"""
    marker2="    _write(p/'artifacts/agent_next_action.json',agent_next_action)\n\n"
    if insert not in text:
        if marker2 not in text: raise RuntimeError('compiler operator insertion marker missing')
        text=text.replace(marker2,marker2+insert,1)
    write(rel,text)


def patch_delivery_workspace()->None:
    rel='runtime/cbcc/delivery_workspace.py'; text=read(rel)
    import_line='from .operator_delivery_html import inject_operator_execution\n'
    marker='from .delivery_html import build_delivery_html as _build_legacy_delivery_html\n'
    if import_line not in text:
        if marker not in text: raise RuntimeError('delivery import marker missing')
        text=text.replace(marker,marker+import_line,1)
    old="""    text = _transform_to_object_workspace(text)\n    text = _inject_commercial_brain(text, package_dir)\n    result.write_text(text, encoding='utf-8')\n"""
    new="""    text = _transform_to_object_workspace(text)\n    text = inject_operator_execution(text, package_dir)\n    text = _inject_commercial_brain(text, package_dir)\n    result.write_text(text, encoding='utf-8')\n"""
    text=replace_if_present(text,old,new)
    write(rel,text)


def patch_tool_contract_version()->None:
    rel='runtime/cbcc/tools/seven_agent.py'; text=read(rel)
    text=text.replace("TOOL_CONTRACT_VERSION='0.6.6'","TOOL_CONTRACT_VERSION='0.6.37'")
    write(rel,text)


def main()->None:
    patch_init()
    patch_base_prompt_compiler()
    patch_model_native_contract()
    patch_reference_authority()
    patch_skill()
    patch_registry()
    patch_strategy_sources()
    patch_compiler()
    patch_delivery_workspace()
    patch_tool_contract_version()
    print('v0.6.37 commercial operator density authority applied')


if __name__=='__main__':
    main()
