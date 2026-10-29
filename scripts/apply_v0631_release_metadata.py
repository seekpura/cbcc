from __future__ import annotations

import json
import re
from pathlib import Path

SOURCE_VERSION='0.6.31-model-native-prompt-integrity'
SEMVER='0.6.31'


def replace_once(path:Path, old:str, new:str, *, required:bool=True)->None:
    text=path.read_text(encoding='utf-8')
    if new in text and old not in text:
        return
    if old not in text:
        if required:
            raise SystemExit(f'{path}: expected text not found: {old[:120]!r}')
        return
    path.write_text(text.replace(old,new,1),encoding='utf-8')


def update_version()->None:
    Path('VERSION').write_text(SOURCE_VERSION+'\n',encoding='utf-8')


def update_skill()->None:
    path=Path('SKILL.md')
    text=path.read_text(encoding='utf-8')
    text=re.sub(r'(?m)^version:\s*0\.6\.30-agent-art-direction-authority\s*$',f'version: {SOURCE_VERSION}',text,count=1)
    path.write_text(text,encoding='utf-8')


def update_runtime_version()->None:
    replace_once(
        Path('runtime/cbcc/compiler.py'),
        "st.data['runtime_version']='0.6.30-agent-art-direction-authority'",
        f"st.data['runtime_version']='{SOURCE_VERSION}'",
    )


def update_registry()->None:
    path=Path('prompts/registry.json')
    data=json.loads(path.read_text(encoding='utf-8'))
    data['version']=SOURCE_VERSION
    purposes={
      'PROMPT-VISUAL-PHOTO':'Agent-authored visual/art direction with carrier-aware photography, inclusive human execution and complete parameter continuity only when relevant.',
      'PROMPT-ASSET-CURATION':'Host-Agent dynamic portfolio curation: asset existence/omission, visual carrier, product-presence rhythm and per-asset Art Direction handoff.',
      'PROMPT-CREATIVE-SURFACE-CANONICAL':'Compile Agent-authored Art Direction into separate Model Prompt CN/EN, Visible Copy Block and Production / Assembly Notes; audit concrete values without inventing layout/product defaults.',
    }
    for row in data.get('prompts') or []:
        if row.get('id') in purposes:
            row['purpose']=purposes[row['id']]
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def update_plugin_builder()->None:
    path=Path('scripts/build_plugin_dist.py')
    text=path.read_text(encoding='utf-8')
    old1='基于当前对话、上传资料和必要的最新公开信息，完成当前商品的跨境电商策略、Listing、内容、视觉策展与逐资产中英文 Canonical Prompt。该请求属于 FULL 商品项目：必须执行九域决策深度合同、Prompt/生产参数连续性审计（生产准备度不阻断项目），并物化完整中文优先 index.html + 可编辑源 + 逐资产包 + ZIP。九域是完整度合同，不是固定页面模板；不得用自定义短报告替代。 人类交付以中文为基础语言；Listing 字段标题中文在前，平台原始 key 仅作次级技术标识；所有英文/马来文/阿语等目标市场外文 Listing、内容与资产可见文案必须在同一对象提供中文释义/用途；英文/目标模型 Prompt 必须与中文 Canonical Prompt 成对。'
    new1='基于当前对话、上传资料和必要的最新公开信息，完成当前商品的跨境电商策略、Listing、内容、视觉策展与逐资产生产对象。该请求属于 FULL 商品项目：必须执行九域决策深度合同、具体参数连续性审计（生产准备度不阻断项目），并物化完整中文优先 index.html + 可编辑源 + 逐资产包 + ZIP。九域是完整度合同，不是固定页面模板；不得用自定义短报告替代。人类交付以中文为基础语言；Listing 字段标题中文在前，平台原始 key 仅作次级技术标识；所有英文/马来文/阿语等目标市场外文 Listing、内容与资产可见文案必须在同一对象提供中文释义/用途。逐资产生产必须分离 Model Prompt CN、Model Prompt EN、Visible Copy Block 与 Production / Assembly Notes；英文 Model Prompt 的执行说明保持英文，目标市场原文可按实际可见 copy 保留。'
    if old1 in text: text=text.replace(old1,new1,1)
    old2='只做当前 SKU 的目标市场/平台视觉资产策展和逐资产生产提示词，本轮不生成图片；先建立商品真源、购买决策、创意机会和动态 Surface，由 Agent 逐资产决定视觉载体、产品是否出现、构图与相关执行参数；只把当前资产已选且会改变结果的构图/摄影/灯光/CMF等参数贯穿到最终 Prompt，不相关摄影字段不强制生成。'
    new2='只做当前 SKU 的目标市场/平台视觉资产策展和逐资产生产对象，本轮不生成图片；先建立商品真源、购买决策、创意机会和动态 Surface，由 Agent 逐资产决定视觉载体、产品是否出现、构图、空间关系、文字渲染路线与相关执行参数。把当前资产已选且会改变结果的具体构图/尺度/留白/摄影/灯光/CMF/人物/动态参数投影到正确对象：Model Prompt、Visible Copy Block 或 Production / Assembly Notes；不相关摄影字段不强制生成。'
    if old2 in text: text=text.replace(old2,new2,1)
    text=text.replace('逐资产中英文 Canonical Prompt、生产、Review、学习闭环与完整人类交付','逐资产 Model Prompt CN/EN、Visible Copy、Production / Assembly Notes、生产、Review、学习闭环与完整人类交付')
    text=text.replace('视觉摄影、图片/视频资产、Canonical Prompt、生产、Review 与学习闭环','视觉摄影、图片/视频资产、Model-Native Prompt、可见文案、生产装配说明、生产、Review 与学习闭环')
    path.write_text(text,encoding='utf-8')


def main()->None:
    update_version(); update_skill(); update_runtime_version(); update_registry(); update_plugin_builder()
    print('Applied v0.6.31 release metadata.')


if __name__=='__main__':
    main()
