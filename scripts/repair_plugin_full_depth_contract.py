from pathlib import Path

P=Path('scripts/build_plugin_dist.py')
text=P.read_text(encoding='utf-8')

old="""DEFAULT_PROMPTS = [
    '基于当前对话、上传资料和必要的最新公开信息，完成当前商品的跨境电商策略、Listing、内容、视觉策展与逐资产中英文 Canonical Prompt。人类交付默认中文，不要套固定模板。',
"""
new="""DEFAULT_PROMPTS = [
    '基于当前对话、上传资料和必要的最新公开信息，完成当前商品的跨境电商策略、Listing、内容、视觉策展与逐资产中英文 Canonical Prompt。该请求属于 FULL 商品项目：必须执行九域决策深度合同、Prompt 参数消费审计，并物化完整中文优先 index.html + 可编辑源 + 逐资产包 + ZIP。九域是完整度合同，不是固定页面模板；不得用自定义短报告替代。',
"""
if old in text:
    text=text.replace(old,new,1)
elif '该请求属于 FULL 商品项目' not in text:
    raise SystemExit('DEFAULT_PROMPTS anchor not found')

anchor="""## 最终交付硬合同
当用户要求完整跨境电商策划、Listing、内容、视觉策展、逐资产 Prompt、资产包或“完成当前商品项目”时，**纯聊天正文不是完成态**。必须物化可下载的人类交付 Artifact。

"""
insert=anchor+"""### FULL 项目深度合同（宿主不可改写成简版报告）
当请求同时覆盖 Product Truth / Strategy / Listing 或 Content / Visual / Asset / Prompt 等完整链路时，模式必须判定为 **FULL**。FULL 的九个决策域必须作为可见的人类交付对象进入 `index.html`；可以用适合 SaaS 的对象式导航/页面组织，但不能换成一套更短的自定义报告后声称等价。

九域必须具备真实决策深度，而不是标题存在：
1. **信息完整度、待确认清单、假设与决策日志**：信息域矩阵、最多10个关键问题、事实/假设边界、每个重大决定的依据/取舍/执行/指标。
2. **产品真实事实审计与卖点分级**：Fact → 真实卖点 → 可感知利益 → 情绪价值 → 不可宣称/Claim Boundary → A/B/C证据等级 → 来源/发布边界。C不得成为硬宣称。
3. **平台×区域×人群×族裔文化洞察**：回答为什么这个平台、区域、人群与文化语境；包含交叉性、语言/宗教/节庆/支付/物流/法规、包容性表征、禁忌/刻板印象与依据/假设。
4. **营销框架与核心策略**：定位、价值主张、信息层级、STP+JTBD、4P/内容漏斗；FULL 中 RACE=Research→Action→Communication→Evaluation。每条重要策略给依据+取舍+执行+指标，不堆概念。
5. **视觉总策略与拍摄执行**：风格/情绪板、构图、主辅背景文字色HEX及对比、CMF、灯光方向/CCT/光比/柔硬、镜头焦段、景别/机位、场景/道具、模特服化道、平台尺寸、镜头表；人物适用时执行肤色测光、深肤色暗部保护、反光板/柔光、发质/体型/年龄/残障与AI偏见控制。
6. **分平台内容矩阵**：平台/人群/选题/钩子/脚本结构/视觉形式/CTA/指标/RACE阶段/文化与禁忌，同时包含尺寸、时长、封面首帧、字幕、音乐版权、流量机制、落地页与UTM/等价归因；未知标待查证。
7. **RACE传播框架执行表**：Research / Action / Communication / Evaluation 四阶段，包含目标、关键动作、输出物、平台、文化校验、KPI、WHY。
8. **族裔文化适配检查表**：文化适配点、包容性表征、刻板印象/禁忌、校验结果、修改动作、WHY。
9. **合规/文化敏感/风险 + 评估/A-B + P0/P1/P2 + 下一步信息**：强监管Claim单列、测试假设、预算/周期取舍、自检（编造/WHY/文化/合规/指标/假设）。

**深度不等于堆字数。** 可以压缩重复说明，但不得压缩决策能力、证据边界、区域/人群洞察或执行参数。`resources/runtime/cbcc/delivery_contract.py` 的 FULL depth validation 是最低线；宿主自己写的报告不能低于它。

### Canonical Prompt 语义压缩 / 能力不压缩
逐资产 Prompt 可以比旧版更短，但只允许删除重复话术、内部 ID/RACE/KPI、与当前资产无关的 toolbox 字段。凡是已经被上游选择且会改变最终像素、摄影、合成或后期结果的决定，必须进入 Canonical Prompt 或明确绑定的 deterministic production instruction，包括适用的构图、产品占比/留白、镜头/视角、灯光、CMF、色彩管理、人物/肤色曝光、反光板/柔光、Product Fidelity、锁定文案区域与 editable/frozen layers。

每个激活资产完成前必须形成 **Prompt Consumption Audit**：`selected execution decisions → projected decisions → missing decisions`。missing 必须为 0 才能声称 Prompt 完成。人物/手/身体关系资产必须把包容性摄影 P0 变成可执行语言，不能只在总策划里出现。

"""
if '### FULL 项目深度合同（宿主不可改写成简版报告）' not in text:
    if anchor not in text: raise SystemExit('skill wrapper hard contract anchor not found')
    text=text.replace(anchor,insert,1)

old="""- 从用户目标、Product Truth、证据、目标市场/平台与当前交付范围开始，由 Agent 动态发现信息缺口并决定研究、策略、框架、内容、Surface、资产与创意方向。
- 不把固定研究清单、固定 RACE/AIDA/4P、固定 9 图/12 图、固定方向数、摄影字段配额或通用页面流水线作为创意/商业权威。
"""
new="""- 从用户目标、Product Truth、证据、目标市场/平台与当前交付范围开始，由 Agent 动态发现信息缺口并决定研究、内容、Surface、资产与创意方向。
- **FULL 与 TASK_SCOPED 分权**：FULL 执行上面的九域深度合同与 RACE 四阶段；TASK_SCOPED 局部任务才按当前目标动态选择框架/域。两者都不规定固定图片数、方向数、页面模板或摄影字段配额。
- 不把固定 9 图/12 图、固定方向数、通用页面流水线当作创意/商业权威；但不得用“动态”作为删除 FULL 已要求能力的理由。
"""
if old in text:
    text=text.replace(old,new,1)
elif '**FULL 与 TASK_SCOPED 分权**' not in text:
    raise SystemExit('commercial continuity anchor not found')

old="""4. 每个资产的中英文 Prompt 与其实际策划参数连续；
5. ZIP 中包含 HTML、Manifest、可编辑源和逐资产包。
"""
new="""4. 每个资产的中英文 Prompt 与其实际策划参数连续，Prompt Consumption Audit 的 `missing decisions = 0`；
5. FULL HTML 可见包含九域决策对象，卖点/区域/人群/文化/视觉摄影/内容矩阵/RACE/风险等达到 decision-depth，不是几句摘要；
6. ZIP 中包含 HTML、Manifest、可编辑源和逐资产包。
"""
if old in text:
    text=text.replace(old,new,1)
elif 'Prompt Consumption Audit' not in text:
    raise SystemExit('completion anchor not found')

old_yaml="""  default_prompt: 基于当前商品资料、真实商品真源和目标市场/平台，由 Agent 动态发现信息缺口并完成当前范围真正需要的研究、策略、Listing、内容、视觉策展与逐资产中英文 Canonical Prompt；人类交付默认中文。完整任务必须生成可下载的 HTML 人类工作台与资产包，不得只返回聊天报告。
"""
new_yaml="""  default_prompt: 基于当前商品资料、真实商品真源和目标市场/平台完成跨境电商工作。若用户要求策略+Listing/内容+视觉/资产+逐资产Prompt的完整链路，必须判定 FULL，执行九域决策深度合同和 Prompt Consumption Audit，并生成中文优先 index.html + 可编辑源 + 逐资产包 + ZIP；不得用自定义简版报告替代。局部任务才使用 TASK_SCOPED 动态裁剪。
"""
if old_yaml in text:
    text=text.replace(old_yaml,new_yaml,1)
elif '必须判定 FULL' not in text:
    raise SystemExit('openai yaml anchor not found')

old_manifest="""            'chat_only_completion_forbidden': True,
        },
"""
new_manifest="""            'chat_only_completion_forbidden': True,
            'full_nine_domain_decision_depth_required': True,
            'prompt_consumption_audit_required': True,
            'host_custom_short_report_cannot_substitute_full_delivery': True,
        },
"""
if old_manifest in text:
    text=text.replace(old_manifest,new_manifest,1)
elif 'full_nine_domain_decision_depth_required' not in text:
    raise SystemExit('release manifest anchor not found')

P.write_text(text,encoding='utf-8')
print('plugin FULL depth contract repair applied')
