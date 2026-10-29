from __future__ import annotations

from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text=path.read_text(encoding='utf-8')
    if new in text:
        return
    if old not in text:
        raise SystemExit(f'{path}: anchor not found: {old[:100]!r}')
    path.write_text(text.replace(old,new,1),encoding='utf-8')


def patch_skill() -> None:
    path=Path('SKILL.md')
    marker='\n## FULL vs TASK_SCOPED Delivery Authority — current precedence\n'
    section=r'''

## Model-Native Prompt + Human Depth Authority — highest current precedence
- **模型 Prompt、可见文案、生产装配说明是三个不同责任层。** 逐资产生产对象必须至少区分：`Model Prompt CN`、`Model Prompt EN`、`Visible Copy Block`、`Production / Assembly Notes`。`prompt_cn / prompt_en` 只能作为 Model Prompt 的兼容别名，不得再承载 renderer layer、machine contract、deterministic typography、provider transport、audit log 等工程合同。
- **英文生成提示词必须是英文执行语言。** 马来文/阿语等目标市场原文可作为准确可见 copy 出现在引号内；中文释义、中文消费者问题、中文 Art Direction 说明不得混入 EN Model Prompt。若上游只有中文创意语义，Agent 应补写英文 render semantics；Runtime 标记 `BILINGUAL_RENDER_SEMANTICS_REQUIRED`，不得把混合语言文本伪装成英文 Prompt。
- **文字是否由生成模型直接渲染不是 Runtime 全局默认。** 当资产有可见文案时，由 Agent/生产路线根据模型能力与资产目标显式选择 `MODEL_RENDER / POST_COMPOSITE / HYBRID`；无可见文案使用 `NO_VISIBLE_COPY`。缺少该决定时标记 `COPY_RENDER_MODE_REQUIRED`。禁止把所有资产统一写成“deterministic post-layout text”。
- **生图 Prompt 必须像真实模型 Prompt，而不是把 Design Card/JSON 改写成英文段落。** Still 顺序优先为 `输出规格 → 视觉目标/风格 → 场景/载体 → 主体/动作/产品角色 → 构图/相对位置/尺度/焦点路径/留白 → 证据层级 → 摄影机(相关时) → 灯光/材质/CMF/色彩(相关时) → 人物(相关时) → 文案行为 → finishing look → truth/negative constraints`；Video 另消费 duration/beat/shot/motion/transition/audio/CTA hold。
- **参数连续性必须核对具体值，不核对字段名。** Prompt Consumption Audit 要从每个 selected decision 的实际值追到 `MODEL_PROMPT / VISIBLE_COPY_BLOCK / PRODUCTION_NOTES`。`surface size / composition / palette / camera` 这种字段名在 Selected/Projected 两边重复不构成 PASS。
- **FULL 人类交付禁止“上游缩水、下游 Prompt 膨胀”。** Semantic Compression 只能去重复，不能删除会改变商业/创意/生产结果的独立决策。Visual Master、CMF、平台规格、内容矩阵、每张资产完整 Art Direction 与参数 WHY 必须保留真实深度；Prompt Lab 只展示执行对象，不得用重复的全局 boilerplate 占据主要信息预算。
- 每张视觉/视频资产的人类设计卡应可见：visual carrier、product presence/role、decisive moment、subject/action/environment/props、composition/spatial rhythm/layout geometry、scale/depth、product occupancy、focal path、negative space、evidence hierarchy、copy zone/hierarchy、palette/CMF/material、camera/lens/focus（相关时）、lighting/CCT/ratio/reflection/prelight（相关时）、human/casting（相关时）、output spec/post look，以及 Video 的 timing/shot/motion（相关时）。不相关字段标 N/A，而不是删除整个设计层。
'''
    text=path.read_text(encoding='utf-8')
    if '## Model-Native Prompt + Human Depth Authority — highest current precedence' not in text:
        if marker not in text:
            raise SystemExit('SKILL.md insertion marker missing')
        text=text.replace(marker,section+marker,1)
    text=text.replace('投影到 Prompt 或 deterministic production instruction','投影到 Model Prompt、Visible Copy Block 或 Production / Assembly Notes')
    path.write_text(text,encoding='utf-8')


def patch_asset_compiler() -> None:
    path=Path('runtime/cbcc/asset_compiler.py')
    text=path.read_text(encoding='utf-8')

    text=text.replace(
        "'information_assetization','product_presence','surface_copy_budget'",
        "'information_assetization','product_presence','asset_art_direction','surface_copy_budget'",
        1,
    )
    text=text.replace(
        "visual={'creative_brief':asset.get('creative_brief',{}),",
        "visual={'asset_art_direction':asset.get('asset_art_direction',{}),'creative_brief':asset.get('creative_brief',{}),",
        1,
    )

    old="""        _write(d/'05_prompt_CN.txt',prompt_bundle['prompt_cn'])
        _write(d/'06_prompt_EN.txt',prompt_bundle['prompt_en'])
        _write(d/'12_design_card.json',_jdump(prompt_bundle['design_card']))
        _write(d/'13_prompt_contract.json',_jdump({'status':prompt_bundle.get('status'),'project_completion_blocking':False,'design_card':prompt_bundle.get('design_card') or {},'canonical_prompt_cn':prompt_bundle.get('prompt_cn') or '','canonical_prompt_en':prompt_bundle.get('prompt_en') or '','deterministic_copy_overlay':prompt_bundle.get('deterministic_copy_overlay') or {},'parameter_trace':prompt_bundle.get('parameter_trace') or [],'prompt_consumption_audit':prompt_bundle.get('prompt_consumption_audit') or {},'machine_visual_contract':prompt_bundle.get('machine_visual_contract') or {},'renderer_recipe':prompt_bundle.get('renderer_recipe') or {},'qa_target_contract':prompt_bundle.get('qa_target_contract') or {}}))
"""
    new="""        _write(d/'05_prompt_CN.txt',prompt_bundle['prompt_cn'])
        _write(d/'06_prompt_EN.txt',prompt_bundle['prompt_en'])
        _write(d/'12_design_card.json',_jdump(prompt_bundle['design_card']))
        _write(d/'14_visible_copy_block.json',_jdump(prompt_bundle.get('visible_copy_block') or {'raw':asset.get('visible_copy') or {}}))
        _write(d/'15_production_assembly_notes.json',_jdump(prompt_bundle.get('production_assembly_notes') or {}))
        _write(d/'13_prompt_contract.json',_jdump({'status':prompt_bundle.get('status'),'model_prompt_status':prompt_bundle.get('model_prompt_status'),'project_completion_blocking':False,'design_card':prompt_bundle.get('design_card') or {},'model_prompt_cn':prompt_bundle.get('model_prompt_cn') or prompt_bundle.get('prompt_cn') or '','model_prompt_en':prompt_bundle.get('model_prompt_en') or prompt_bundle.get('prompt_en') or '','canonical_prompt_cn':prompt_bundle.get('prompt_cn') or '','canonical_prompt_en':prompt_bundle.get('prompt_en') or '','visible_copy_block':prompt_bundle.get('visible_copy_block') or {},'production_assembly_notes':prompt_bundle.get('production_assembly_notes') or {},'legacy_copy_overlay':prompt_bundle.get('deterministic_copy_overlay') or {},'parameter_trace':prompt_bundle.get('parameter_trace') or [],'prompt_consumption_audit':prompt_bundle.get('prompt_consumption_audit') or {},'machine_visual_contract':prompt_bundle.get('machine_visual_contract') or {},'renderer_recipe':prompt_bundle.get('renderer_recipe') or {},'qa_target_contract':prompt_bundle.get('qa_target_contract') or {}}))
"""
    if new not in text:
        if old not in text:
            raise SystemExit('asset_compiler prompt write block missing')
        text=text.replace(old,new,1)

    old_h="""        '', '## 4. 生产提示词（可选生产辅助，不阻断资产交付）','',
        '### 中文规范生产提示词','',
        '```text', prompt_bundle.get('prompt_cn') or '', '```','',
        '### 英文 / 生成模型执行提示词','',
        '> 仅用于需要英文执行语言的生成模型；中文生产说明是人类主交付。','',
        '```text', prompt_bundle.get('prompt_en') or '', '```','',
        '## 5. 成功与承接','',
"""
    new_h="""        '', '## 4. 模型生成提示词（Model-facing）','',
        '### Model Prompt CN｜中文生成提示词','',
        '> 这是直接给图像/视频生成模型的视觉执行语言，不承载 Runtime/装配合同。','',
        '```text', prompt_bundle.get('model_prompt_cn') or prompt_bundle.get('prompt_cn') or '', '```','',
        '### Model Prompt EN｜英文生成提示词','',
        '> 英文执行说明必须保持英文；目标市场原文可作为准确可见 copy 保留，中文释义放在 Visible Copy Block。','',
        '```text', prompt_bundle.get('model_prompt_en') or prompt_bundle.get('prompt_en') or '', '```','',
        '### Visible Copy Block｜准确文案与中文释义','',
        '```json', _jdump(prompt_bundle.get('visible_copy_block') or {}), '```','',
        '### Production / Assembly Notes｜生产与装配说明','',
        '> 锁图、产品参考角色、文字渲染路线、可编辑/冻结层、Provider 与后期装配规则在此管理，不污染 Model Prompt。','',
        '```json', _jdump(prompt_bundle.get('production_assembly_notes') or {}), '```','',
        f"- **Model Prompt Readiness**：{prompt_bundle.get('model_prompt_status') or (prompt_bundle.get('prompt_consumption_audit') or {}).get('status') or '—'}",
        '', '## 5. 成功与承接','',
"""
    if new_h not in text:
        if old_h not in text:
            raise SystemExit('asset_compiler human prompt block missing')
        text=text.replace(old_h,new_h,1)

    old_visual="""        f"- **视觉任务**：{card.get('visual_objective') or asset.get('strategic_job') or '—'}",
        f"- **构图语法**：{_cn_phrase(cam.get('composition_grammar')) or '—'}",
"""
    new_visual="""        f"- **视觉任务**：{card.get('visual_objective') or asset.get('strategic_job') or '—'}",
        f"- **完整逐资产 Art Direction**：{asset.get('asset_art_direction') or '—'}",
        f"- **视觉载体**：{(asset.get('asset_art_direction') or {}).get('visual_carrier') or '—'}",
        f"- **Product Presence / Role**：{(asset.get('asset_art_direction') or {}).get('product_presence') or card.get('product_presence') or '—'}",
        f"- **Decisive Moment**：{(asset.get('asset_art_direction') or {}).get('decisive_moment') or '—'}",
        f"- **Subject / Action / Environment / Props**：{ {k:(asset.get('asset_art_direction') or {}).get(k) for k in ('subject','action','environment','props') if (asset.get('asset_art_direction') or {}).get(k)} or '—'}",
        f"- **构图语法**：{_cn_phrase(cam.get('composition_grammar')) or (asset.get('asset_art_direction') or {}).get('composition_grammar') or '—'}",
        f"- **空间节奏 / 几何**：{(asset.get('asset_art_direction') or {}).get('spatial_rhythm') or '—'} / {(asset.get('asset_art_direction') or {}).get('layout_geometry') or (asset.get('asset_art_direction') or {}).get('relative_placement') or '—'}",
        f"- **尺度 / 纵深 / 占画**：{(asset.get('asset_art_direction') or {}).get('scale_depth') or '—'} / {(asset.get('asset_art_direction') or {}).get('product_occupancy') or '—'}",
        f"- **焦点路径 / 留白**：{(asset.get('asset_art_direction') or {}).get('focal_path') or '—'} / {(asset.get('asset_art_direction') or {}).get('negative_space') or '—'}",
        f"- **证据层级**：{(asset.get('asset_art_direction') or {}).get('evidence_hierarchy') or (asset.get('asset_art_direction') or {}).get('evidence_plane') or '—'}",
"""
    if new_visual not in text:
        if old_visual not in text:
            raise SystemExit('asset_compiler visual detail anchor missing')
        text=text.replace(old_visual,new_visual,1)

    text=text.replace(
        "'08_copy.md','09_production_notes.md','10_source_trace.md','11_strategy_authority_trace.json','12_design_card.json'",
        "'08_copy.md','09_production_notes.md','10_source_trace.md','11_strategy_authority_trace.json','12_design_card.json','14_visible_copy_block.json','15_production_assembly_notes.json'",
        1,
    )
    text=text.replace(
        "'additive_capability_files':['00_HUMAN_DESIGN_CARD_CN.md','12_design_card.json','13_prompt_contract.json']",
        "'additive_capability_files':['00_HUMAN_DESIGN_CARD_CN.md','12_design_card.json','13_prompt_contract.json','14_visible_copy_block.json','15_production_assembly_notes.json']",
        1,
    )
    path.write_text(text,encoding='utf-8')


def patch_plugin_builder() -> None:
    path=Path('scripts/build_plugin_dist.py')
    text=path.read_text(encoding='utf-8')
    anchor='## Agent Creative Authority\n商业策略、资产策展与视觉设计由宿主 Agent 主导；Runtime 只负责 validate / serialize / compile / trace / execute / package / test。逐资产必须由 Agent 决定视觉载体、产品是否出现及其角色、主体/动作/环境/道具、空间语法与相关时的摄影/灯光/CMF。缺失 Art Direction 时返回 Agent 补决策，不得自动补 packshot、centered hero、left-text/right-product 或其他模板。Product Reference/Fidelity 不等于 Product Presence。\n\n'
    addition='## Model-Native Prompt Contract\n逐资产生产必须分离 Model Prompt CN、Model Prompt EN、Visible Copy Block 与 Production / Assembly Notes。英文 Model Prompt 的执行说明保持英文，目标市场原文可准确保留，中文释义放在人类交付/Copy Block；不要把 deterministic typography、renderer layer、machine contract、audit/provenance 等 Runtime 工程词塞进模型 Prompt。文字由模型直接生成还是后期装配由 Agent/生产路线显式决定，不做全局默认。FULL 交付不得为缩短篇幅而压扁 Visual Master、内容矩阵或逐资产 Art Direction。\n\n'
    if addition not in text:
        if anchor not in text:
            raise SystemExit('build_plugin_dist Agent authority anchor missing')
        text=text.replace(anchor,anchor+addition,1)
    path.write_text(text,encoding='utf-8')


def main() -> None:
    patch_skill()
    patch_asset_compiler()
    patch_plugin_builder()
    print('Applied v0.6.31 prompt/delivery contract migration.')


if __name__=='__main__':
    main()
