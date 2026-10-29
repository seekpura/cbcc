from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'scripts/build_plugin_dist.py'
text=p.read_text(encoding='utf-8')

repls=[
(
" FULL 视觉资产必须先完成 Production Parameter Closure：所有已选且会改变生成结果的构图/相对位置/尺度/占画/焦点路径/负空间/摄影/灯光/CMF/材质/人物/视频参数都要被 Model Prompt 实际消费；LOCKED_SOURCE_COMPOSITE 仍须按最终商品 envelope、透视、接触阴影、反射与环境光生成可合成底片。",
" FULL 视觉资产必须先完成 Production Parameter Closure：所有已选且会改变生成结果的构图/相对位置/尺度/占画/焦点路径/负空间/摄影/灯光/CMF/材质/人物/视频参数都要被 Model Prompt 实际消费。真实商品需要出现在画面时，将真实商品图作为强模型 Reference Input 原生生成完整最终成图并锁定商品身份；只有明确要求原始源图像素层一丝不动时才使用 EXACT_PIXEL_COMPOSITE。"
),
(
"FULL 视觉/视频资产必须由 Agent 完成可执行 Art Direction 并闭环所有会改变结果的具体参数。摄影式路线恢复 v0.6.6 深度：焦段/镜头、工作距离、机位高度与角度、景别、对焦/景深、相关时快门/ISO、key/fill/negative/rim、modifier、CCT/WB、光比、阴影/高光、反射/偏振、Prelight、CMF/材质、色彩管理与 finishing；人物再加入肤色曝光与代表性执行。LOCKED_SOURCE_COMPOSITE 仍必须围绕最终商品占画/位置/纵深/透视/接触阴影/反射/环境光生成可合成底片。平台最大图片数只是上限，不得自动填满。若一组资产只是暖白底、左右分区、小角落商品、柔光的重复变体，返回 Agent 重新策展/设计。完整 Inspector 展示完整 Art Direction 与 Production Parameter Closure，摘要字段不得替代设计卡。",
"FULL 视觉/视频资产必须由 Agent 完成可执行 Art Direction 并闭环所有会改变结果的具体参数。摄影式路线恢复 v0.6.6 深度：焦段/镜头、工作距离、机位高度与角度、景别、对焦/景深、相关时快门/ISO、key/fill/negative/rim、modifier、CCT/WB、光比、阴影/高光、反射/偏振、Prelight、CMF/材质、色彩管理与 finishing；人物再加入肤色曝光与代表性执行。真实商品需要出现时，真实商品图必须作为强 Reference Input 进入生成模型，商品在完整最终画面中原生生成并保持包装几何、比例、结构、Logo、品牌文字、标签版式、可辨识印刷、主色和材质身份。EXACT_PIXEL_COMPOSITE 只用于用户明确要求源图像素层不可改变的特殊路线。平台最大图片数只限制同时上线集合，不限制 Asset Universe；若一组资产只是暖白底、左右分区、小角落商品、柔光的重复变体，返回 Agent 重新策展/设计。完整 Inspector 展示完整 Art Direction 与 Production Parameter Closure，摘要字段不得替代设计卡。"
),
(
"## Model-Native Prompt Contract\n",
"## Dynamic Asset Universe + Native Product Reference\n资产总量由购买决策、Surface、创意假设、测试与运营需求决定，不受平台 Gallery 槽位总数限制。Hero、卖点、广告、A+/PDP/详情、Store/Banner、Social/Creator、Video 等均可存在多方案；同一消费者问题和同一 Surface 也允许 H01/H02/H03 等显式 Variant，不得因为 question/surface/family 相同而合并。人类工作区区分上线候选、测试池、轮换池、广告、PDP/A+详情、归档与其他资产。\n\n当 Product Presence 要求真实商品可见时，真实商品图默认作为强模型 Reference Input，使用 `REFERENCE_GUIDED_NATIVE_LOCK` 原生生成完整最终画面中的商品，并保持真实商品身份；`EXACT_PIXEL_COMPOSITE` 仅在用户明确要求源图像素层不可改变时启用。\n\n## Model-Native Prompt Contract\n"
),
(
"- 用户提供的产品图/包装图/源文件默认作为**设计参考**，不是像素级锁定层；默认允许重绘、重渲染、3D、插画化、风格化、重新构图或合成，不默认强求摄影写实。\n- 只有用户/任务明确要求锁定原图/真实产品合成时才启用 `LOCKED_SOURCE_COMPOSITE / LOCKED_PIXEL`，且只约束对应生产子任务。",
"- 用户提供的真实商品图/包装图在 Product Presence 需要真实商品可见时，默认作为**强模型 Reference Input**：模型原生生成完整最终画面中的同一真实商品身份，可匹配作者化机位/透视/光线/景深/场景，但不得擅自改包装几何、比例、泵头/滴管/瓶盖结构、Logo、品牌文字、标签版式、可辨识印刷、主色或材质身份。\n- `REFERENCE_GUIDED_NATIVE_LOCK` 是常规真实商品生成保真路线；`EXACT_PIXEL_COMPOSITE` 仅在用户明确要求“原始源图像素层不可改变/必须保留 exact pixels”时启用。Product Presence=ABSENT/FORBIDDEN 时，真实商品图只做 Truth/Identity Reference，不强行把商品放进画面。"
),
]
for old,new in repls:
    if old in text:
        text=text.replace(old,new)
    elif new not in text:
        raise SystemExit('missing wrapper patch anchor: '+old[:100])
p.write_text(text,encoding='utf-8')
print('v0.6.33 plugin wrapper authority patched')
