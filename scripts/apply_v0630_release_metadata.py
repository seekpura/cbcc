from __future__ import annotations

import json
import re
from pathlib import Path

SOURCE_VERSION='0.6.30-agent-art-direction-authority'
SEMVER='0.6.30'


def replace_once(path: Path, old: str, new: str, *, required: bool=True) -> None:
    text=path.read_text(encoding='utf-8')
    if new in text and old not in text:
        return
    if old not in text:
        if required:
            raise SystemExit(f'{path}: expected text not found: {old[:120]!r}')
        return
    text=text.replace(old,new,1)
    path.write_text(text,encoding='utf-8')


def update_version() -> None:
    Path('VERSION').write_text(SOURCE_VERSION+'\n',encoding='utf-8')


def update_skill() -> None:
    path=Path('SKILL.md')
    text=path.read_text(encoding='utf-8')
    text=re.sub(r'(?m)^version:\s*0\.6\.29-final-stabilization\s*$',f'version: {SOURCE_VERSION}',text,count=1)
    old='视觉层必须给可执行构图、HEX/对比、摄影、灯光、CMF、镜头、人物、平台规格与逐资产参数；'
    new='视觉层必须给可执行构图、HEX/对比、CMF/材质与平台规格；摄影、灯光、镜头、人物等只在当前视觉载体/生产路线相关时策划，并把已选参数贯穿到逐资产执行；'
    if old in text:
        text=text.replace(old,new,1)
    path.write_text(text,encoding='utf-8')


def update_runtime_version() -> None:
    replace_once(
        Path('runtime/cbcc/compiler.py'),
        "st.data['runtime_version']='0.6.29-final-stabilization'",
        f"st.data['runtime_version']='{SOURCE_VERSION}'",
    )


def update_prompt_registry() -> None:
    path=Path('prompts/registry.json')
    data=json.loads(path.read_text(encoding='utf-8'))
    data['version']=SOURCE_VERSION
    purposes={
        'PROMPT-VISUAL-PHOTO':'Agent-authored visual/art direction; photography, lighting and CMF are consumed only when relevant to the selected carrier/production route.',
        'PROMPT-ASSET-CURATION':'Host-Agent dynamic portfolio curation: asset existence/omission, visual carrier, product-presence rhythm and per-asset handoff.',
        'PROMPT-CREATIVE-SURFACE-CANONICAL':'Consume Agent-authored direction and per-asset Art Direction into surface-native executable CN/EN prompts without inventing product/layout fallbacks.',
    }
    for row in data.get('prompts') or []:
        if row.get('id') in purposes:
            row['purpose']=purposes[row['id']]
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def update_plugin_builder() -> None:
    path=Path('scripts/build_plugin_dist.py')
    text=path.read_text(encoding='utf-8')
    old='只做当前 SKU 的目标市场/平台视觉资产策展和逐资产生产提示词，本轮不生成图片；先建立商品真源、购买决策、创意机会和动态 Surface，并确保摄影/CMF/构图参数进入最终 Prompt。'
    new='只做当前 SKU 的目标市场/平台视觉资产策展和逐资产生产提示词，本轮不生成图片；先建立商品真源、购买决策、创意机会和动态 Surface，由 Agent 逐资产决定视觉载体、产品是否出现、构图与相关执行参数；只把当前资产已选且会改变结果的构图/摄影/灯光/CMF等参数贯穿到最终 Prompt，不相关摄影字段不强制生成。'
    if old in text:
        text=text.replace(old,new,1)

    old2='5. **视觉总策略与拍摄执行**：风格/情绪板、构图、主辅背景文字色HEX及对比、CMF、灯光方向/CCT/光比/柔硬、镜头焦段、景别/机位、场景/道具、模特服化道、平台尺寸、镜头表；人物适用时执行肤色测光、深肤色暗部保护、反光板/柔光、发质/体型/年龄/残障与AI偏见控制。'
    new2='5. **视觉总策略与按需媒介/拍摄执行**：先由 Agent 确定视觉载体、产品 presence/role、构图、空间节奏、证据层级、主辅背景文字色HEX及对比、CMF/材质与平台尺寸；只有真实摄影/摄影式生成路线才继续策划灯光方向/CCT/光比/柔硬、镜头焦段、景别/机位、Prelight与镜头表；人物适用时执行肤色测光、深肤色暗部保护、反光板/柔光、发质/体型/年龄/残障与AI偏见控制。'
    if old2 in text:
        text=text.replace(old2,new2,1)

    anchor="# Cross-Border Commerce Creative v{version}\n\n完整 Agent/Skill 权威位于 `resources/SKILL.md`。"
    insert="# Cross-Border Commerce Creative v{version}\n\n## Agent Creative Authority\n商业策略、资产策展与视觉设计由宿主 Agent 主导；Runtime 只负责 validate / serialize / compile / trace / execute / package / test。逐资产必须由 Agent 决定视觉载体、产品是否出现及其角色、主体/动作/环境/道具、空间语法与相关时的摄影/灯光/CMF。缺失 Art Direction 时返回 Agent 补决策，不得自动补 packshot、centered hero、left-text/right-product 或其他模板。Product Reference/Fidelity 不等于 Product Presence。\n\n完整 Agent/Skill 权威位于 `resources/SKILL.md`。"
    if '## Agent Creative Authority\n商业策略、资产策展与视觉设计由宿主 Agent 主导' not in text:
        if anchor not in text:
            raise SystemExit('build_plugin_dist.py: skill wrapper anchor not found')
        text=text.replace(anchor,insert,1)
    path.write_text(text,encoding='utf-8')


def retire_old_release_autotrigger() -> None:
    path=Path('.github/workflows/release-v0629.yml')
    text=path.read_text(encoding='utf-8')
    marker='name: CBCC human-delivery release acceptance'
    if marker in text:
        text=text.replace(marker,'name: CBCC v0.6.29 historical release acceptance (manual)',1)
    # Preserve the historical acceptance job exactly, but stop it from auto-running against v0.6.30 main.
    text2=re.sub(
        r'(?ms)^on:\n  push:\n.*?^  workflow_dispatch:\n',
        'on:\n  workflow_dispatch:\n',
        text,
        count=1,
    )
    if text2==text and 'on:\n  workflow_dispatch:\n' not in text:
        raise SystemExit('release-v0629.yml: could not retire push trigger')
    path.write_text(text2,encoding='utf-8')


def main() -> None:
    update_version()
    update_skill()
    update_runtime_version()
    update_prompt_registry()
    update_plugin_builder()
    retire_old_release_autotrigger()
    print('Applied v0.6.30 release metadata and retired v0.6.29 automatic release trigger.')


if __name__=='__main__':
    main()
