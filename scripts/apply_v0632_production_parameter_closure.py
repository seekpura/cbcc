#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VERSION='0.6.32-production-parameter-closure'
SECTION='''## Production Parameter Closure + Creative Depth Authority — highest current precedence
- **本节修正 v0.6.31 可能被误读成“Model Prompt 变短即可”的问题。** Model-Native 分层只负责把工程合同移出 Prompt，绝不允许把已经策划、会改变像素/时间/运动/合成结果的设计与摄影参数一起删掉。Prompt 长短没有目标；生产可执行性才是目标。
- FULL 视觉项目、商品图、视频、Prompt/Production 任务中，宿主 Agent 必须先完成 **Portfolio Art Direction → Per-Asset Art Direction → Production Parameter Closure**。资产不能因为有标题、Carrier、占比、构图、Camera、Lighting 六七个摘要字段就标 READY。
- **恢复并提升 v0.6.6 的摄影执行深度。** 摄影/摄影式生成/摄影式锁图复合路线按实际需要作者化焦段/镜头族、工作距离、机位高度、yaw/pitch/roll、景别/裁切、对焦平面、光圈/景深、真实拍摄或运动相关时的快门/ISO、key/fill/negative/rim、modifier 尺寸与距离、CCT/WB、光比、曝光/阴影/高光保护、反射/偏振、Prelight、CMF/材质响应、色彩管理、finishing/grade；人物相关时再加入肤色测光、深肤色暗部保护、bounce/reflector/diffusion、发质/服装/妆发等。最终值依赖实拍时标注 Prelight-dependent，不得假装已测量。
- **参数策划必须被消费。** 任何 Agent 已选且会改变当前生成结果的具体值，必须进入 Model Prompt CN/EN；只属于锁图/图层/装配/Provider 的规则进入 Production / Assembly Notes。不能把 `85mm / 5200K / 2:1 / 68% / x-y位置 / 阴影密度 / 高光策略 / 材质响应 / post look` 留在策划卡里却给模型一句“warm ivory background, soft light”。
- **LOCKED_SOURCE_COMPOSITE 不是空背景生成。** 不重画商品只锁定商品身份层；环境底片仍必须围绕最终商品 envelope/occupancy、相对位置、纵深、透视、接触面、接触阴影、反射接收、环境光向/光比、CCT/WB、grade-match、前景遮挡与 copy/evidence safe zone 来生成。Prompt 必须描述最终合成空间/光线系统，同时明确不生成锁定商品本体。
- 手写 `model_prompt_cn/en` 不能绕过闭环。Compiler/Audit 仍要逐项比对所有 selected generation-relevant values；丢参数则 `ART_DIRECTION_EXECUTION_DEPTH_REQUIRED` / `MODEL_PROMPT_NEEDS_AGENT_DECISIONS`，该 Prompt 不得标 READY。
- **完整人类 Design Card 必须可见。** Inspector/HTML 至少能查看 decisive moment、subject/action/environment/props、visual carrier、product presence/role、composition/spatial grammar/layout geometry、scale/depth/occupancy、focal path、negative space、evidence hierarchy、copy zone/hierarchy、palette/CMF/material response、camera/focus/exposure、lighting/CCT/WB/ratio/reflection/prelight、human/casting、post look，以及视频 timing/shot/motion/transition/audio；不相关项说明 N/A/原因。摘要卡只能做入口。
- **平台容量不是资产配额。** “最多9图/7图”等只表示上限，不得因为有槽位就全部激活。资产数量由增量购买决策/证据/情绪/原生 Surface 价值决定；重复、装饰性、低信息资产优先删除或合并。
- **设计同质化必须回 Agent 重做。** 交付前审查相邻资产的 carrier、product role、subject/evidence plane、composition grammar、相对位置、scale/depth、focal path、negative-space shape、information density、camera/view、lighting/material、palette role 和 decisive moment。若只是重复 `暖白/象牙白 + 左文右品/右文左品 + 小角落商品 + 柔光 + 编辑感`，不能用“统一视觉系统”解释，必须重新策展/设计。
- Agent 应检索并转化当前任务相关的已集成案例/Techniques/设计/摄影/信息可视化/动效机制，用于改变真实的构图、载体、空间、材质、光线或叙事；“premium / editorial / clean / minimal / modern”这类形容词不能单独构成 Creative Direction。
'''


def write(path:Path,text:str):
    path.write_text(text,encoding='utf-8')


def replace_once(text:str,old:str,new:str,label:str)->str:
    if old not in text:
        raise SystemExit(f'missing patch anchor: {label}')
    return text.replace(old,new,1)

# VERSION
write(ROOT/'VERSION',VERSION+'\n')

# Root SKILL highest-precedence authority.
skill_path=ROOT/'SKILL.md'
skill=skill_path.read_text(encoding='utf-8')
skill=re.sub(r'(?m)^version:\s*[^\n]+$',f'version: {VERSION}',skill,count=1)
if '## Production Parameter Closure + Creative Depth Authority — highest current precedence' not in skill:
    anchor='## Agent Creative Authority — highest current precedence'
    skill=replace_once(skill,anchor,SECTION+'\n\n'+anchor,'root skill authority')
write(skill_path,skill)

# Runtime metadata.
compiler_path=ROOT/'runtime/cbcc/compiler.py'
compiler=compiler_path.read_text(encoding='utf-8')
compiler=compiler.replace("0.6.31-model-native-prompt-integrity",VERSION)
write(compiler_path,compiler)

# Prompt registry version.
registry_path=ROOT/'prompts/registry.json'
registry=json.loads(registry_path.read_text(encoding='utf-8'))
registry['version']=VERSION
for row in registry.get('prompts') or []:
    if row.get('id')=='PROMPT-VISUAL-PHOTO':
        row['purpose']='Agent-authored portfolio/per-asset visual, photography and CMF strategy with v0.6.6 execution-depth parameters, locked-source composite scene integration and anti-homogenization review.'
    if row.get('id')=='PROMPT-CREATIVE-SURFACE-CANONICAL':
        row['purpose']='Compile Agent Art Direction into lossless Model Prompt CN/EN + Visible Copy + Production Notes with concrete production-parameter closure; missing useful execution values are not READY.'
registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Plugin build defaults and wrapper authority.
build_path=ROOT/'scripts/build_plugin_dist.py'
build=build_path.read_text(encoding='utf-8')
old="逐资产生产必须分离 Model Prompt CN、Model Prompt EN、Visible Copy Block 与 Production / Assembly Notes；英文 Model Prompt 的执行说明保持英文，目标市场原文可按实际可见 copy 保留。"
new=old+" FULL 视觉资产必须先完成 Production Parameter Closure：所有已选且会改变生成结果的构图/相对位置/尺度/占画/焦点路径/负空间/摄影/灯光/CMF/材质/人物/视频参数都要被 Model Prompt 实际消费；LOCKED_SOURCE_COMPOSITE 仍须按最终商品 envelope、透视、接触阴影、反射与环境光生成可合成底片。"
build=replace_once(build,old,new,'default full prompt')
old2="把当前资产已选且会改变结果的具体构图/尺度/留白/摄影/灯光/CMF/人物/动态参数投影到正确对象：Model Prompt、Visible Copy Block 或 Production / Assembly Notes；不相关摄影字段不强制生成。"
new2="把当前资产已选且会改变结果的具体构图/相对位置/尺度/占画/焦点路径/留白/摄影机几何/对焦景深/灯光几何/CCT-WB/光比/阴影高光/反射偏振/Prelight/CMF材质/色彩管理/finishing/人物/动态参数投影到正确对象；摄影式路线恢复0.6.6可执行参数深度，缺值时不要把Prompt标READY。"
build=replace_once(build,old2,new2,'default visual prompt')
wrapper_anchor='## Agent Creative Authority\n商业策略、资产策展与视觉设计由宿主 Agent 主导；Runtime 只负责 validate / serialize / compile / trace / execute / package / test。逐资产必须由 Agent 决定视觉载体、产品是否出现及其角色、主体/动作/环境/道具、空间语法与相关时的摄影/灯光/CMF。缺失 Art Direction 时返回 Agent 补决策，不得自动补 packshot、centered hero、left-text/right-product 或其他模板。Product Reference/Fidelity 不等于 Product Presence。\n'
wrapper_add=wrapper_anchor+'''\n## Production Parameter Closure + Creative Depth\nFULL 视觉/视频资产必须由 Agent 完成可执行 Art Direction 并闭环所有会改变结果的具体参数。摄影式路线恢复 v0.6.6 深度：焦段/镜头、工作距离、机位高度与角度、景别、对焦/景深、相关时快门/ISO、key/fill/negative/rim、modifier、CCT/WB、光比、阴影/高光、反射/偏振、Prelight、CMF/材质、色彩管理与 finishing；人物再加入肤色曝光与代表性执行。LOCKED_SOURCE_COMPOSITE 仍必须围绕最终商品占画/位置/纵深/透视/接触阴影/反射/环境光生成可合成底片。平台最大图片数只是上限，不得自动填满。若一组资产只是暖白底、左右分区、小角落商品、柔光的重复变体，返回 Agent 重新策展/设计。完整 Inspector 展示完整 Art Direction 与 Production Parameter Closure，摘要字段不得替代设计卡。\n'''
if '## Production Parameter Closure + Creative Depth\n' not in build:
    build=replace_once(build,wrapper_anchor,wrapper_add,'plugin wrapper authority')
write(build_path,build)

print('applied',VERSION)
