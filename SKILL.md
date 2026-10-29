---
name: cross-border-commerce-creative
description: Autonomous cross-border commerce agent for product truth, decision-driven research, market/SKU/economics, strategy, listing, content, visual/photography, dynamic assets, production, review and learning.
version: 0.6.33-reference-guided-native-asset-universe
---

# Cross-Border Commerce Creative — Hard Contract Strategy → Creative → Production Build

## Reference-Guided Native Product + Dynamic Asset Universe Authority — highest current precedence
- **“锁真实商品”默认不是后期合成。** 真实商品图作为生成模型的强参考输入，最终商品必须在完整最终画面中原生生成并真实可见；同时锁定包装几何/比例、泵头/滴管/瓶盖结构、Logo、品牌文字、标签版式与可辨识印刷、主色和材质身份。模型可以为匹配已作者化的机位/透视/灯光/景深/场景做原生重建，但不得把商品改成另一个包装版本。
- 默认保真模式为 `REFERENCE_GUIDED_NATIVE_LOCK`。旧输入中的 `pixel_lock=true / LOCKED_PIXEL / LOCKED_SOURCE_COMPOSITE` 在没有“必须保留原始像素层”这一明确意图时，迁移为 native reference identity lock；只有 `exact_pixel_layer=true / exact_pixel_composite=true / EXACT_PIXEL_COMPOSITE` 才允许使用不可变像素层合成。
- **Reference input 必须进入 Provider handoff。** 真实商品源图不能只留在 Truth/QA；当 Product Presence=PRESENT 时，Provider Job 必须绑定真实商品 reference input，生成结果必须确认 `product_reference_input_used + native_product_rendered_in_final_output + product_identity_preserved`。
- **资产宇宙没有总数上限。** 平台“最多9图/7图”等仅约束一次同时上线的 activation set；不约束 Hero 变体、卖点变体、测试图、轮换图、广告图、A+/PDP 详情模块、长图、Banner、Social/Creator/Video 或其他资产总量。20、30、50 个候选都允许，只要每个有独立创意/商业假设。
- **同一角色允许多方案。** Hero H01/H02/H03、同一卖点 B01/B02/B03、同一广告角度的多个 Hook/构图/人群版本不得因为 `consumer_question + surface + family` 相同被 Runtime 合并。显式 `variant_id / creative_hypothesis_id / test_hypothesis` 是一等身份。
- 资产交付分为 `Asset Universe`、`Live/Activation Candidates`、`Test Pool`、`Rotation Pool`、`Paid Media`、`PDP/A+ Content`、`Archive` 等运营状态；“现在没放进平台9个槽位”不等于“不生产/不存在”。
- Surface 范围至少允许 Listing/Gallery/Search、Hero、Benefit/Proof、Usage/How-to、Trust/Packaging、Paid Ads、A+/PDP/Longform、Store/Banner、Social/Creator/UGC、Short Video/Live、Campaign/Seasonal 等。实际项目由 Agent 动态增删，不形成固定20张或固定类型配额。


## Purpose
Create a professional cross-border ecommerce plan **before** governance machinery becomes visible. The user-facing mainline is positive commercial design: understand the product, market and shopper; decide positioning and message architecture; design platform-native content, visual and photography; compile dynamic assets; then use evidence/platform/compliance/review as background guardrails.


## Production Parameter Closure + Creative Depth Authority — highest current precedence
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


## Agent Creative Authority — highest current precedence
- **本节高于下方所有会把 Runtime heuristics、Surface、intent、reference 或方向级默认值解释成创意权威的历史说明。** Product Truth、用户明确锁定、平台/法规硬约束、Claim 证据和目标输出技术边界继续是硬约束；商业策略、资产策展和视觉设计由宿主 Agent 主导。
- 对 FULL 商品项目以及任何要求视觉策展 / 资产规划 / 商品图 / 视频 / Prompt / Production 的任务，宿主 Agent 是 **Portfolio Curator + Creative Director + Per-Asset Art Director**。Agent 决定资产是否存在、是否合并/省略、信息载体、产品是否出现及其角色、主体/动作/环境/道具、空间语法/尺度/焦点路径/留白、证据层级，以及相关时的摄影/灯光/CMF/人物/生产路线。
- Python / Runtime 的创意职责严格降为 **validate → serialize → compile → trace → execute → package → test**。Runtime 可以保存和校验 Agent 已做出的设计决策，但在 Agent authority 激活时不得原创 Product Presence、Subject、Composition、Camera、Lighting、CMF、Layout 或“为了完整”添加资产。
- **缺设计决策必须回到 Agent。** 逐资产 Art Direction 或 Product Presence 未解决时，使用 `AUTHOR_PER_ASSET_ART_DIRECTION` / `AGENT_ART_DIRECTION_REQUIRED` / `UNRESOLVED_AGENT_DECISION` 等显式状态；不得用 centered hero、left-text/right-product、card grid、podium、generic lifestyle、packshot 或 intent→layout fallback 自动补洞。
- **Product Presence 与 Product Fidelity 分离。** 商品源文件可以是 `TRUTH_REFERENCE_ONLY` 而画面完全没有商品。每张视觉资产由 Agent 显式决定 `HERO_REQUIRED / REQUIRED / SUPPORTING / DETAIL_ONLY / OPTIONAL→PRESENT|ABSENT / FORBIDDEN / NOT_APPLICABLE`（只使用当前任务需要的状态）。`FORBIDDEN` 时下游不得出现 packshot、corner product、ghost silhouette、podium product 或 product layer。
- **Surface 不是创意权威。** Surface architecture 可以给 representation / copy / product-usefulness 的兼容建议，但 `authoritative_for_generation=false`；逐资产 Agent Art Direction 才能确定真实 product presence、visual carrier 和空间设计。
- **Direction 是共享系统，不是页面模板。** Direction 只提供可共享的 thesis / continuity tokens / color-type-material principles 等；不得覆盖单资产已作者化的 Art Direction。相邻资产可以共享系统，但 composition、product role、subject、evidence plane、scale、density、camera/view 和媒介表达应按各自购买问题动态设计。
- Creative Opportunity 和 Direction 数量没有默认配额。Agent 可以形成一个明显正确的方向，也可以在不确定性或机会空间需要时扩展；停止条件是新增探索不再可能改变重要商业/创意决策，而不是 6–12 / 3–5 / 固定多方向数量。
- **摄影是工具，不是母模板。** Camera / lens / light / Prelight / CMF 只有在当前 carrier 和 production route 真正需要时才由 Agent 策划并贯穿执行；Graphic / Source Evidence / Native Text / Illustration / 3D 等资产不得为了“专业感”被强制塞摄影参数。
- Prompt Compiler 是 compiler，不是 designer。唯一允许的链路是 `Product Truth + Commerce Strategy → Agent Portfolio Curation → Creative Direction → Per-Asset Art Direction → Canonical Prompt → Renderer/Provider → Agent Review/Revision`。Prompt 只能压缩和投影已经选定、会改变生产结果的参数，不能反向发明设计。
- 人类交付仍默认中文优先；目标市场可见文案可使用当地语言，但在人类工作区/资产说明中必须有合适的中文释义与用途说明。九域是 FULL 的决策深度合同，不是固定页面、固定资产、固定 UI 或固定视觉模板。


## Model-Native Prompt + Human Depth Authority — highest current precedence
- **模型 Prompt、可见文案、生产装配说明是三个不同责任层。** 逐资产生产对象必须至少区分：`Model Prompt CN`、`Model Prompt EN`、`Visible Copy Block`、`Production / Assembly Notes`。`prompt_cn / prompt_en` 只能作为 Model Prompt 的兼容别名，不得再承载 renderer layer、machine contract、deterministic typography、provider transport、audit log 等工程合同。
- **英文生成提示词必须是英文执行语言。** 马来文/阿语等目标市场原文可作为准确可见 copy 出现在引号内；中文释义、中文消费者问题、中文 Art Direction 说明不得混入 EN Model Prompt。若上游只有中文创意语义，Agent 应补写英文 render semantics；Runtime 标记 `BILINGUAL_RENDER_SEMANTICS_REQUIRED`，不得把混合语言文本伪装成英文 Prompt。
- **文字是否由生成模型直接渲染不是 Runtime 全局默认。** 当资产有可见文案时，由 Agent/生产路线根据模型能力与资产目标显式选择 `MODEL_RENDER / POST_COMPOSITE / HYBRID`；无可见文案使用 `NO_VISIBLE_COPY`。缺少该决定时标记 `COPY_RENDER_MODE_REQUIRED`。禁止把所有资产统一写成“deterministic post-layout text”。
- **生图 Prompt 必须像真实模型 Prompt，而不是把 Design Card/JSON 改写成英文段落。** Still 顺序优先为 `输出规格 → 视觉目标/风格 → 场景/载体 → 主体/动作/产品角色 → 构图/相对位置/尺度/焦点路径/留白 → 证据层级 → 摄影机(相关时) → 灯光/材质/CMF/色彩(相关时) → 人物(相关时) → 文案行为 → finishing look → truth/negative constraints`；Video 另消费 duration/beat/shot/motion/transition/audio/CTA hold。
- **参数连续性必须核对具体值，不核对字段名。** Prompt Consumption Audit 要从每个 selected decision 的实际值追到 `MODEL_PROMPT / VISIBLE_COPY_BLOCK / PRODUCTION_NOTES`。`surface size / composition / palette / camera` 这种字段名在 Selected/Projected 两边重复不构成 PASS。
- **FULL 人类交付禁止“上游缩水、下游 Prompt 膨胀”。** Semantic Compression 只能去重复，不能删除会改变商业/创意/生产结果的独立决策。Visual Master、CMF、平台规格、内容矩阵、每张资产完整 Art Direction 与参数 WHY 必须保留真实深度；Prompt Lab 只展示执行对象，不得用重复的全局 boilerplate 占据主要信息预算。
- 每张视觉/视频资产的人类设计卡应可见：visual carrier、product presence/role、decisive moment、subject/action/environment/props、composition/spatial rhythm/layout geometry、scale/depth、product occupancy、focal path、negative space、evidence hierarchy、copy zone/hierarchy、palette/CMF/material、camera/lens/focus（相关时）、lighting/CCT/ratio/reflection/prelight（相关时）、human/casting（相关时）、output spec/post look，以及 Video 的 timing/shot/motion（相关时）。不相关字段标 N/A，而不是删除整个设计层。

## FULL vs TASK_SCOPED Delivery Authority — current precedence
- **FULL Commerce Project / FULL Strategy / End-to-End 商品项目**：当用户明确要求完整商品策略、完整跨境电商项目、端到端交付，或请求同时覆盖 Product Truth + Strategy + Listing/Content + Visual/Asset/Prompt 等完整链路时，执行本 Skill 的 FULL 硬合同。FULL 必须物化 9 个决策域：信息完整度/假设日志、产品事实与 A/B/C 证据、平台×区域×人群×族裔文化洞察、营销核心策略、视觉/摄影/CMF、分平台内容矩阵、RACE 执行表、族裔文化适配检查表、合规/风险/评估/P0-P1-P2。RACE=Research → Action → Communication → Evaluation 作为传播流程骨架；STP+JTBD 定策略，AIDA/FABE 定内容结构，4P/Funnel 定转化。C 级证据不得形成硬宣称。
- **TASK_SCOPED 局部任务**：当用户只要求 Listing、单个资产、Prompt、视觉审查、局部研究、某个 Surface 或其他窄范围时，继续使用 v0.6.21–0.6.29 的动态 Scope / Decision Authority；不为了“系统会这些能力”强塞 9 个域、RACE、固定框架、固定资产数或未来工作。
- **两者不是冲突**：FULL 的 9 个域是“决策覆盖与交付完整度”合同，不是固定页面模板、固定章节篇幅、固定图片数、固定方向数或流水线 UI。HTML/工作区仍按真实业务对象设计；资产数量、页面组织、摄影字段和创意方向仍由当前商品、平台、市场、人群、证据和购买决策动态产生。
- FULL 与 TASK_SCOPED 都必须保留 Product Truth、Claim/Compliance、证据、Visual/Photography/CMF、Product Reference/Fidelity、Prompt/Production、Review/Revision/Hash 等能力；**保留能力不等于每个任务都强制执行或阻断**。摄影、Prompt、生图方案、Provider 生产只有在当前任务/生产路线需要时才成为局部执行要求。
- 完整任务的完成态必须包含真实人类交付 Artifact（自包含 `index.html` + 可编辑源 + 逐资产包 + `DELIVERY_MANIFEST.json` + ZIP）；源码存在或聊天正文不构成 FULL 完成。

### FULL Decision-Depth + Prompt Execution Continuity — highest current precedence
- **本节高于下面所有历史版本说明。** 任何 v0.6.21–v0.6.29 关于“框架可选 / scope 动态”的历史段落，只适用于 TASK_SCOPED；不得覆盖 FULL 的九域深度合同。
- FULL 九域不是标题检查：每个域必须包含会改变商业/创意/生产决策的内容。产品层必须清楚区分 Fact / 真实卖点 / 可感知利益 / 情绪价值 / Claim Boundary / A-B-C 证据；区域与用户层必须回答平台×区域×人群×族裔文化 WHY、交叉性、语言/宗教/节庆/支付/物流/法规与禁忌/刻板印象；视觉层必须给可执行构图、HEX/对比、CMF/材质与平台规格；摄影、灯光、镜头、人物等只在当前视觉载体/生产路线相关时策划，并把已选参数贯穿到逐资产执行；内容层必须给平台执行字段、RACE、文化校验、CTA、指标、落地/归因；风险层必须给合规、A/B、P0/P1/P2、取舍、下一步与输出自检。
- **深度不等于字数。** 允许删除重复解释、内部 ID、RACE/KPI 元数据和与当前资产无关的摄影 toolbox；禁止删除已有证据边界、区域/用户洞察、策略 WHY/取舍、生产参数或人类可执行动作。
- Canonical Prompt 使用 **Semantic Compression, never Capability Compression**：当当前任务需要 Prompt / 生图 / Provider 执行时，已选且会改变该生产结果的参数应投影到 Model Prompt、Visible Copy Block 或 Production / Assembly Notes，并记录 `prompt_consumption_audit`。**Prompt Consumption Audit 是生产质量诊断，不是项目或资产完整度的全局阻断 Gate**；`missing_decisions` 可以形成 `NEEDS_PROMPT_WORK`，但不能阻止策略、Listing、内容、视觉策展、资产设计卡或完整人类交付完成。
- 人物/手部/身体关系资产必须执行包容性表征与 AI 偏见控制；**真实摄影路线**再把肤色测光、深肤色暗部保护、Prelight、reflector/bounce、diffusion 等转成拍摄参数。插画、3D、风格化生成等非真实摄影路线使用与该媒介匹配的表征控制，不强行套摄影参数。
- FULL 最终导出必须重新运行当前 `delivery_contract.validate_strategy_delivery()`，并把 `FULL_DELIVERY_DEPTH_AUDIT.json`、`PROMPT_CONSUMPTION_AUDIT.json` 写入交付包。后者是可见的生产准备度审计但 `project_completion_blocking=false`。`index.html` 必须直接可见九域核心对象；宿主自写的一套更短报告不能替代它。

### Product Reference / Fidelity — current authority
- 用户提供的商品图片、包装图、源文件默认是**产品/设计参考**，不是像素级不可修改层。默认 `REFERENCE_GUIDED`：可根据创意方向重绘、重渲染、3D、插画化、风格化、重新构图或合成；不默认要求摄影写实，也不默认要求像素匹配。
- Product Truth 约束的是**事实与 Claim 诚实**：规格、成分、功能、认证、包装上真实可读事实等不能被创意伪造成另一种事实。视觉参考可以被创作性解释，只要不把创作性变化冒充成真实产品事实。
- 只有用户/任务明确要求原图锁定、原始包装像素不可重绘、真实产品合成或等价语义时，才启用 `LOCKED_SOURCE_COMPOSITE / LOCKED_PIXEL`；该硬约束只作用于对应生产子任务。
- 摄影、灯光、CMF、镜头、Prelight 等是专业能力池：真实拍摄/摄影式生成路线按需消费；插画、3D、图形设计、风格化生成等路线不因为系统会摄影就被强制写实化。
- 七大第一类工具（市场研究、产品策略、Listing 创意、商品图片、商品视频、广告优化、评论分析）与其他已集成参考能力必须保持可调用并能被项目消费；是否激活由当前任务证据与目标决定，不制造固定七步流水线。

## v0.6.29 Final Stabilization — 当前主权威
- 本版不新增架构，专门清理 baseline 中确认存在的真实业务断链；Commerce Agent 自主权、动态 Scope、Completion 与 blocking/advisory frontier 保持不变。
- Final Copy 数字等价审计现在把“字段显式绑定的已批准 Claim 数字”视为字段级 numeric authority；未绑定数字继续阻断。Claim 的真实证据等级与发布资格仍由 Claim Authority 单独决定，不能用 `APPROVED` 标签绕过证据边界。
- Compliance issue 统一稳定 shape：`scope / asset_id / code / claim_ids / severity`；asset-routing issue 与 claim-ledger issue 分流，调用方可以可靠定位哪个资产引用了未批准 Claim。
- Canonical Prompt 在 Render Objective 显式保留 `Consumer Decision Question + Product Truth binding`，同时继续禁止 Product Name、Asset ID、RACE/KPI 等内部元数据泄漏到生成模型 Prompt。
- v0.6.29 的发布门槛不是“再加能力”，而是 baseline 实际修复：`FIXED_FAILURE_COUNT > 0` 且 `NEW_FAILURE_COUNT = 0`。
- 这一版之后停止版本号驱动的连续扩张；只有真实电商任务/案例暴露新的业务缺口时，才从当前 `main` 派生下一次修改。
- 详细变更见 `CHANGELOG_V0629.md`。

## v0.6.28 Blocking vs Advisory Agent Frontier — 当前主权威
- **还有可研究 ≠ 当前任务必须继续循环。** Agent frontier 现在显式拆成 `blocking_frontier` 与 `advisory_frontier`；只有前者阻止 `STOP_CURRENT_SCOPE_SATISFIED`。
- 未解决 Research 保留原 action identity `RESEARCH_OR_EVIDENCE_RESOLUTION`，通过 `blocking=false + advisory_frontier` 表达“可选后续研究”；不通过重命名破坏旧宿主/调用方兼容。
- Research 是否 blocking 由当前 `gate_scope` 路由决定；只影响非阻断/非当前 scope Gate 的研究不会强迫 Agent 再跑一轮。
- Compliance / Creative / Asset Architecture / Production frontier 同样按 current-scope Gate requiredness / blockingness 分类，不再因为能力或对象存在就自动变成硬下一步。
- 显式 Agent Stop 可以在仅剩 advisory frontier 时成立；不能越过真正的 current-scope hard blocker。
- 修复生产意图语义：`production_run: {}` 表示“明确请求生产、使用默认配置”，不再因空映射 `bool({}) == False` 被误判成未请求；Compiler / Gate Scope / Decision Scope / Agent Frontier 共用 presence-based intent。
- Human Project Hub 分开显示“当前范围必须先解决”与“可选后续优化 / 研究（不阻断当前完成）”。
- v0.6.28 targeted + continuity：`45 passed`；全量相对 frozen v0.6.27 main：12 vs 12，`NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。
- 详细变更见 `CHANGELOG_V0628.md`。

## v0.6.27 Current-Scope Completion Authority — 当前主权威
- **`final_ready` 不再是永远 False 的静态旗标。** 新增 `completion.py`，完成态由当前 scope 的真实闭环条件派生。
- READY 条件：当前 scope 的 blocking Gate 没有 PENDING/HOLD/MISSING/INVALIDATED 等阻断；required 非 Gate 交付项已到可审状态并完成必要 review；blocking research/action 已解决；open local revision 已闭环；不存在当前 scope 的 hard Agent frontier。
- Supporting / advisory Gate、ContentObject、Research Action 与 Agent frontier 可以继续存在，不再为了“还有可做的事”阻止当前交付完成。
- `RESEARCH_OR_EVIDENCE_RESOLUTION` 只有在对应 unresolved action 对当前 blocking scope 真正 blocking 时才阻止完成；planning-only 的 advisory research 可以保留并继续显示。
- `AUTHOR_DECISION_OR_ASSET_SCOPE / REPLAN_ASSET_ARCHITECTURE / AUTHOR_OR_SELECT_CREATIVE_DIRECTION / RESOLVE_COMPLIANCE_BOUNDARY / PRODUCE_RESUME_OR_REPAIR` 等 hard frontier 继续阻断对应当前 scope。
- Review Manifest 的 `final_ready` 直接来自 completion authority；`ProjectState.final_ready` 与 `completion` 会在 build/review/provider/revision/learning 后统一刷新并持久化。
- CLI `export` 删除旧的固定 Gate required 列表，不再要求一套静态流水线全部 LOCKED；Export 与 Review/State 共用同一 current-scope completion。
- Revision 仍会按 dependency graph INVALIDATE 受影响层，并立即重新计算 readiness；支持层变化不应无故推翻无关已完成 scope。
- v0.6.27 targeted + continuity：`40 passed`；全量相对 frozen v0.6.26 main：12 vs 12，`NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。
- 详细变更见 `CHANGELOG_V0627.md`。

## v0.6.26 Task-Scoped Content + Gate Readiness — 当前主权威
- **对象存在 ≠ 当前任务必须完成。** 新增 `content_requiredness.json`，把 active/preserved family 与 `required_for_current_scope` 明确拆开；Listing/Compliance 等可以继续作为支持权威存在，而不自动变成人类当前交付债务。
- ContentObject 不再统一写 `required=True`。显式 content scope、Asset/Video/Paid/Measurement/Compliance deliverable，以及“已有决策问题 + 明确资产生产意图”才会把对应 family 升级为当前 required deliverable。
- 新增 `gate_scope.json`：18 个 canonical gate 全部继续保留，但每个 Gate 增加 `required_for_current_scope / blocking_for_current_scope / scope_status / scope_reason`。
- ProjectState 继续保存 canonical Gate 与 dependency lineage；`NOT_IN_CURRENT_SCOPE` Gate 可以维持机器状态/工件，不再反向制造 readiness debt。
- Planning-only 的 Platform Compile 可以是当前需要的证据上下文，但不因动态规则待研究而阻断 Strategy；required 与 blocking 明确分离。
- Review Manifest 不再硬编码“除 ASSET_COMPILE / PRODUCTION 外全部 Gate required”；只让当前 scope 的 blocking Gate 进入 `required_missing`。
- Supporting ContentObject 仍可审阅、追溯、被 Strategy/Asset 消费，但默认不会进入 `review_pending` 阻断当前交付。
- Review HTML / checklist 同时显示 Runtime Status、Current Scope 与 Blocking，避免把机器流水线状态误读成用户工作流。
- canonical gates、Product Truth、Decision Authority、Strategy、Asset/Photography/Prompt、00–13 包、Provider/Review/Revision/Hash lineage 均继续保留。
- v0.6.26 targeted + continuity：`34 passed`；全量相对 frozen v0.6.25 main：12 vs 12，`NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。
- 详细变更见 `CHANGELOG_V0626.md`。

## v0.6.25 Decision Question Authority — 当前主权威
- **消费者问题允许为空。** Runtime 不再因为目标平台、PDP Surface 或“电商通常要回答这些问题”而自动制造 `What is it / Why relevant / What evidence / What after purchase` 四问。
- 新增 `decision_question_authority.json`：问题只来自用户/调用方、Agent content scope / decision trace、显式 Asset/Video job，以及当前 Listing/CX 中真实存在的异议；每条问题保留 origin / decision job / surface / family / evidence lineage。
- Decision Trace 不再按问题数组位置机械映射 `ACTION / COMMUNICATION / EVALUATION` 或 `IDENTIFY / RELATE / VERIFY / USE`；RACE stage 只有在 RACE 被显式选择且该问题本身有阶段信息时才出现。
- Decision Framework 不再有默认全家桶。`decision_frameworks` / Agent `strategy_frameworks` 是唯一选择权威；AIDA / FABE / 4P 的 persuasion compiler 也只消费显式选中的框架。
- Content family 继续 task-scoped：目标 Surface 单独存在只是执行约束，不会制造 Listing / Search / Offer / Visual 工作；只有真实任务信号才激活 family。
- 兼容边界：当已经存在明确 shopper question 且明确请求 `compile_assets / production_run` 时，请求 Surface 可以决定这些**已有问题**应落入 VISUAL / VIDEO / CREATOR / CX 等哪种资产 family；这是路由，不是 Surface 配额。
- 明确请求资产/生产但没有任何决策问题/Asset job 时，不再用 Runtime 默认问题补洞，而是在 `agent_next_action.json` 暴露 `AUTHOR_DECISION_OR_ASSET_SCOPE`，交还 Agent 决策。
- Product Truth、Evidence、Market/Listing、Strategy 九段机器兼容结构、动态 Asset、Photography/CMF、00–13 包、Provider / Review / Revision / Hash lineage 全部继续保留。
- v0.6.25 targeted + continuity：`46 passed`；全量相对 frozen v0.6.24 main：12 vs 12，`NEW_FAILURE_COUNT=0` / `FIXED_FAILURE_COUNT=0`。
- 详细变更见 `CHANGELOG_V0625.md`。

## v0.6.24 Task-Scoped Strategy + Asset Authority — 当前主权威
- **机器兼容结构与人类当前任务分层。** `strategy_authority.json` 继续保留九段 canonical section、证据、追溯和资产包绑定；`MASTER_STRATEGY_CN.md` 只投影当前 Commerce 目标真正相关的决策域，不再把九段目录当成人类配额。
- STP / JTBD / 4P / Funnel / AIDA / FABE / Fogg / Means-End / Signaling / FIRST / Cognitive Budget / Belief Sequence / Commerce Response Ladder / RACE 均为可选决策镜头。只有 Agent / 用户显式选择时才进入当前 Strategy Authority；默认不再全量注入。
- RACE 未显式启用时，机器 section 07 保持兼容键但内容为空；Content Matrix 不再机械写 `race_stage=COMMUNICATION`。显式选择 RACE 时完整保留。
- P0/P1/P2 与 A/B 不再为了“策略完整”自动制造未来工作。只有真实 Compliance HOLD、未解决 Research、明确 Evaluation/Experiment 信号才形成当前动作；没有实质未解决项时允许 `CURRENT_SCOPE_CAN_STOP`。
- Asset Architecture 不再在没有视觉/视频/Creator/Paid Surface 时把 shopper question 强制变成 GALLERY 图片。问题可继续留在 Strategy / Listing，直到真实资产 Surface 被激活。
- Asset 列表顺序只用于展示；没有显式 `handoff` 时不再自动生成 A→B→C 链。资产关系为 `EXPLICIT_ONLY`，显式关系继续保留。
- Foundation roles、Product Truth、Claim/Evidence、Photography/CMF、00–13 资产包、Provider / Review / Revision / Hash lineage 全部继续保留；动态化不是删能力。
- v0.6.24 targeted + continuity：`28 passed`；全量相对 frozen v0.6.23 main：12 vs 12，`NEW_FAILURE_COUNT=0`。
- baseline failing node-id 必须逐项判断真实断链还是旧语义断言；禁止用固定失败数量替代能力审计，也禁止为旧字符串测试倒退当前合同。
- 详细变更见 `CHANGELOG_V0624.md`。

## v0.6.23 Task-Scoped Human Delivery + Listing Authority — 当前主权威
- **人类工作区的主任务由当前 Commerce scope 决定，不再由系统拥有的全部能力反向规定。** Listing 数据可以长期保留，但视觉、内容、Prompt、生产等当前任务不因为价格、物流、退换货或卖家信息缺失而被整项目标记为 HOLD。
- `compile_upload_center()` 读取当前 request、Agent content scope、Content Graph 与 `agent_next_action.json`；只有 Listing / Search / Offer 或明确上架发布任务激活时，上架字段才进入当前主工作面。
- Listing readiness 改为 **task-scoped readiness**：只让当前平台明确 required 字段与真正 submission-sensitive 字段参与阻断；未供应的可选字段不再制造“待查证”权威。
- 非 Listing 当前任务使用 `NOT_IN_CURRENT_SCOPE`；已有 Listing / Product 数据继续保存在结构化真源和 `preserved_listing_fields`，动态化不以删除信息换简洁。
- Listing 激活时，字段按实际出现 / 平台 required / 当前提交需要动态形成，并按商品识别、类目搜索、购买决策、事实使用、Offer 履约等语义分组；不存在固定 25 字段展示配额。
- Listing Conversion Architecture 的 click / expectation fields 同样从当前存在或 required 字段投影，不再默认强塞 `price / variant / primary_image / faq / usage / package / attributes`。
- 项目总控台优先显示当前 Agent scope、动态 frontier、资产与真实风险；固定“四件事 / 四步正常使用路径”退出主权威。
- v0.6.23 发布验证：targeted + compatibility `23 passed`；相对 frozen v0.6.22 main 的全量失败 node-id `NEW_FAILURE_COUNT=0`（两侧各 12 个既有历史失败）。
- 详细变更见 `CHANGELOG_V0623.md`。

## v0.6.22 Dynamic Workspace + Relevant Prompt Projection — 当前主权威
- **Workspace 也是 Agent 决策面的投影，不是固定功能目录。** 一级路由和首页动作只显示当前项目实际存在或当前 frontier 需要的业务对象；Archive 等机器追踪入口保持次级，不用固定菜单数制造“完整感”。
- 单资产页使用动态工作视图，不存在强制的“决策→画面→摄影→文案→Prompt→QA”执行顺序。缺失/不相关视图不占位；Agent 显式顺序优先，默认顺序只有展示意义。
- Design Card / Product Truth / source / trace 仍完整保留。动态化不得以删信息换简洁；未知 legacy 资产内容必须可在 QA / 来源中回收。
- Prompt Projection 只携带**实际影响当前资产**的视觉、构图、摄影、灯光、CMF、人物、Surface、编辑性与商品保真参数。不得把空 schema、全局摄影 toolbox 或“专业字段”机械倾倒给生成模型。
- 一旦 Agent/策略已经为当前资产选定摄影/构图/灯光/CMF参数，它们必须继续贯穿执行链，不能因 relevance filtering 被误删。相关性裁剪的对象是无关默认值，不是已经做出的生产决策。
- Parameter Trace、QA checks 与 Renderer layer plan 也必须 relevance-driven；下游不得反向逼上游虚构快门、ISO、CCT、Prelight、人物摄影或其它不相关字段。
- Content/Listing/Strategy 的人类界面继续中文优先；目标市场语言与中文释义并存。固定 Hook/CTA/RACE/页面数量/模块数量均不拥有默认权威。
- v0.6.22 发布验证：targeted + compatibility 20 passed；相对 v0.6.21 frozen main 的全量失败 node-id `NEW_FAILURE_COUNT=0`。
- 详细变更见 `CHANGELOG_V0622.md`。

## v0.6.21 Commerce Agent Autonomy — 当前主权威
- **冻结事实与硬边界，Agent 自主决定完成路径。** Product Truth、用户明确锁定、平台/法规硬约束、Claim 证据、目标输出技术规格属于不可擅自改写的边界；只有显式锁定源图时，源图像素/对应身份层才成为生产硬边界。研究范围、策略路径、内容范围、资产数量、创意机制、方向数量、构图/摄影/CMF、生产路线和迭代深度属于 Agent 决策。
- 宿主 Agent 应优先自行形成 `agent_plan` / `agent_decisions`，而不是让 Runtime 的兼容 heuristics 代替智能判断。Plan 可以按当前任务只声明真正需要的 research/content/creative/framework/iteration 决策，不要求填写固定表单。
- Research 以**信息增益是否仍会改变重要商业决策**作为继续/停止条件；禁止为了固定来源数、竞品数、关键词数、页面数或“研究完整度”机械扩写。
- Content/Asset 由真实消费者问题、目标 Surface、商业任务、证据与生产需求派生；不存在默认 7 图/9 图、固定 Hero/Proof/How-to 套餐、固定内容家族配额。
- Creative exploration 不规定 6–12 mechanisms、3–5 directions 或固定差异数量。Agent 可以只形成一个明显正确的方向，也可以在不确定性较高时扩展更多 materially distinct 方向；数量必须来自任务需要，而不是系统配额。
- AIDA / FABE / 4P / STP / JTBD / Funnel / RACE 都是**可选思考工具**。只有它们能改善当前决策时才启用；不得因为框架存在就强制生成对应阶段、页面、资产或叙事。
- Asset expression 必须从该资产自身的 buyer decision / evidence plane / Surface / production mode 推导；禁止固定 intent→layout 映射和轮换式空间节奏伪装“多样性”。
- Photography / composition / lighting / CMF 参数是执行工具，不是必填专业字段。只有相关时才进入策划；一旦 Agent 决定某个参数会影响结果，该参数必须继续贯穿 Design Card → CN/EN Canonical Prompt → Parameter Trace → Machine Contract → Production，不得在执行链丢失。
- `agent_next_action.json` 是当前轮的动态 action frontier：Agent 根据真实未解决问题决定继续研究、重规划、生产/修复、复核，或停止。**不存在固定下一步流水线。**
- MCP / Plugin / HTTP / Provider Host 属于**可选宿主/生产接入基础设施**。它们服务电商能力，但不拥有研究、策略、设计或产品路线权威，也不应成为主迭代目标。
- 详细变更见 `CHANGELOG_V0621.md`。

## v0.6.20 MCP stdio Host
- 新增真正可启动的 MCP stdio transport：`runtime/cbcc/mcp_stdio.py` + `python -m cbcc.mcp_stdio_cli`；stdout 只输出 newline-delimited UTF-8 JSON-RPC MCP message。
- 开发前按当前 MCP 官方规范重核协议：现代主版本为 `2026-07-28`，采用每请求 `_meta` + `server/discover`；`initialize / notifications/initialized` 只保留给 `2025-11-25` legacy 兼容路径。
- `server/discover`、`tools/list`、`tools/call` 直接消费 v0.6.18 `mcp_tool_descriptors()` / canonical Action Catalog；不维护第二套 MCP tool schema。
- 现代 `tools/list` deterministic 且按 `ActionAuthorization` scope 过滤；现代 cacheable results 带保守 `ttlMs: 0 / cacheScope: private`。
- `tools/call` 只映射 `MCP tool → canonical action → ProviderActionDispatcher`；返回 `structuredContent` 并同步 text JSON 兼容内容，PENDING 继续暴露既有 operation/status/resume 状态，不创建 MCP 侧任务库。
- unsupported modern protocol 使用 `-32022 UnsupportedProtocolVersion`；缺失现代 clientCapabilities、未知 tool、非法 arguments 使用稳定 JSON-RPC/MCP error。
- `CBCC_MCP_AUTH_MODULE` 只保存 host module 名；默认 DENY，authorization resolver 异常 fail closed 且不回显宿主异常详情。
- transport runtime 不 import/call `ProviderExecutionSurface / ProviderExecutorBridge / ProviderExecutor`；composition root 才组装既有 Surface → Dispatcher。
- legacy initialize/list/call 与 modern discover/list/call 共用同一 tool descriptor、authorization 和 dispatcher authority。
- v0.6.13–v0.6.20 provider/action/Plugin/MCP continuity 定向联测：62 passed。
- 全量回归与 v0.6.19 main 按失败 node-id 对比：`NEW_FAILURE_COUNT=0`。

## v0.6.19 Plugin/OpenAPI HTTP Host
- 新增真正可启动的 `PluginHTTPApplication` / WSGI host；HTTP action route 全部来自 v0.6.18 generated OpenAPI descriptor，不手写第二套路由表。
- 唯一调用链保持 `HTTP request → operationId → PluginActionTransportAdapter → ProviderActionDispatcher`；`plugin_http.py` 不 import `ProviderExecutionSurface / ProviderExecutorBridge / ProviderExecutor`。
- 提供 `/health`、`/openapi.json`、`/actions.json`（含 schema aliases）；checked-in descriptor bundle 仍保持 descriptor-only，因此其 `plugin_http_server_included=false` 不等于仓库没有 host runtime。
- POST action 强制 `application/json`、`Content-Length`、JSON object 与可配置 request-size limit；transport error 使用稳定 HTTP/code 映射。
- `ActionAuthorization` 由宿主 hook 注入；`CBCC_ACTION_AUTH_MODULE` 只指定 auth module 名，不把 API key/token/credential 放进 action body 或 CLI 参数。
- 默认授权 DENY；authorization resolver 异常按 403 fail-closed 且不回显宿主异常文本。
- canonical `PENDING` 映射 HTTP 202，并返回 `Retry-After`、`X-CBCC-Operation-Id`、`X-CBCC-Operation-State`；status/resume 继续复用 v0.6.17 operation/state lineage。
- 新增 `cbcc.plugin_http_cli` composition root，可用标准库 `wsgiref.simple_server` 启动 reference host；生产宿主也可直接挂载标准 WSGI application。

## v0.6.18 Transport Descriptor Parity
- 从 v0.6.17 canonical Action Catalog 自动派生 MCP tool descriptors 与 Plugin/OpenAPI 3.1 descriptors；transport 不维护第二份 action schema。
- checked-in 生成物：`transport/mcp_tools.json`、`transport/plugin_openapi.json`、`transport/descriptor_manifest.json`，由生成器物化并由测试反向校验当前 canonical schema。
- parity 必须同时满足：action 数量一致、tool/operation 名称一致、input schema exact equality、permission scope 一致、authorization source 一致、credential-like field lint 为零。
- 每个 action 记录 canonical / MCP / Plugin schema hash；三者必须相同，schema 漂移 fail closed。
- Plugin/OpenAPI 默认使用同源相对 server `/`，descriptor 本身不绑定假远程服务地址。
- `PluginActionTransportAdapter` 是薄 operationId adapter，唯一执行依赖为 `ProviderActionDispatcher`；不持有 surface / bridge / executor。
- checked-in manifest 明确 `mcp_server_included=false`、`plugin_http_server_included=false`：当前版本生成可消费 descriptor，但不伪造网络 server 已存在。

## v0.6.17 Host Action / MCP / Plugin Mapping
- 新增 canonical host action catalog：`adapters.list / execute / status / resume / cancel / reconcile` 六个 action，schema 与 permission scope 由同一真源定义。
- `ProviderActionDispatcher` 只调用 v0.6.16 `ProviderExecutionSurface`；Action / MCP / Plugin 不复制 ProviderExecutor、Bridge、Receipt 或 ProjectState completion runtime。
- authorization 默认 DENY；read / execute / cancel / reconcile 权限显式分离，mutating action 必须持有对应 scope。
- 长任务不建立第二套 async job DB：execute 返回稳定非敏感 operation ID；status 只读现有 `bridge_state / executor_state / result / production_run`；resume 重新进入同一持久化 Provider lifecycle，因此不重复 submit。
- operation ID 与 project + materialized job scope 绑定；status/resume 改换 asset scope 会被拒绝。
- action payload 在 dispatch 前递归拒绝 credential-like 字段，包含 exact 与 namespaced 形式：`api_key / provider_api_key / oauth_token / clientSecret / password / credential / authorization / private_key` 等。
- runtime context 继续只来自 ProviderExecutionSurface resolver，不进入 action JSON。
- `action_transport_manifest()` 仅声明 MCP tool name / Plugin operationId 的薄映射，并显式声明当前仓库没有 MCP/Plugin server；未来 transport 只能包裹 canonical dispatcher。

## v0.6.16 Provider Host Execution Surface
- 新增 `ProviderExecutionSurface`，把 v0.6.15 Adapter Registry / Executor Bridge 暴露成宿主可操作入口；仍然复用唯一链路 `Provider Job → Adapter Registry → Executor Bridge → ProviderExecutor → Production Receipt → Ingest`。
- CLI 新增 `adapter-list / provider-execute / provider-cancel / provider-reconcile`；不提供 `--api-key` / token / secret 等参数，避免凭证进入 shell history、项目文件或日志。
- `CBCC_PROVIDER_HOST_MODULE` 只保存宿主 Python module 名称。真实 SDK/client/auth/callback 由 module 的 `create_runtime_context(...)` 在运行时注入，runtime context 不持久化。
- `provider-execute` 只有在 `PROVIDER_JOB_INDEX` 中所有 materialized job 都有真实 result 时才自动调用既有 ingest；局部/分批执行不能把全项目误标为 COMPLETE。
- 自动 ingest 成功后继续更新既有 ProjectState `PRODUCTION` gate 与 Review Workspace；Host Surface 不创建第二套完成权威。
- cancel / reconcile 继续复用同一 external job ID、`executor_state.json` 与 `bridge_state.json` lineage。
- 安全回归明确扫描 `bridge_state / executor_state / result / production_run / ProjectState`，宿主 secret 值不得落盘。

## v0.6.15 Provider Adapter Registry / Executor Bridge
- 新增 credential-free `ProviderAdapterRegistry`：按 provider / production mode / capabilities / operations 发现适配器，优先级选择确定性；显式指定 adapter 也必须通过 capability 匹配。
- 新增 `ProviderExecutorBridge`，只编排现有 v0.6.14 `ProviderExecutor`；唯一执行链保持 `Provider Job → Adapter Registry → Executor Bridge → ProviderExecutor → Production Receipt → Ingest`，不建立旁路完成态。
- 标准化 transient / permanent / rate-limit 错误；retry 有界，backoff 可配置，429 可使用 provider `retry_after_seconds`。未知异常默认永久失败，避免认证/参数错误无限重试。
- `bridge_state.json` 只保存 adapter ID、策略、attempt history、cancel/reconcile 状态；runtime_context / callbacks / API keys / credentials 不写入项目文件。
- 新增 cancel 与 reconcile 语义；reconcile 对比本地 executor state 与 provider 状态，不覆盖 `executor_state.json` 或 receipt lineage。
- 新增 `HostCallbackExecutor` 与 `EPV_HOST_CALLBACK_V1`：真实宿主通过 runtime callback/SDK/client 注入 Provider 能力；CBCC 不保存凭证。Reference Memory adapter 保持 opt-in，不是 production default。
- `provider_contract()` 对 EXTERNAL_ADAPTER 显式暴露 executor + bridge contract，避免 Bridge 成为未接路由的孤立模块。

## v0.6.14 Provider Executor Lifecycle
- `ProviderExecutor` 是真实 Provider 执行的可插拔边界：adapter 自己负责 credentials / network client / vendor SDK，CBCC 负责 portable job、source lineage、idempotency、resume state、output hash 与 production receipt。
- materialized `EXTERNAL_ADAPTER` job 可执行完整生命周期：校验并 upload / refresh 商品资产 → 构建 executor transmission → 幂等 submit → poll / resume → collect → resolve 实际输出字节 → 写 `result.json + production_receipt` → 交回既有 ingest。
- `executor_state.json` 在每个外部边界持久化，因此宿主中断后可继续 poll，不会因为重试再次创建同一 Provider job。
- portable `source_binding_hash` 是不可变 lineage；provider handle 重绑定使用独立 `provider_execution_source_binding_hash`，不能覆盖上游真源绑定。
- executor transmission 必须声明 v0.6.13 portable transmission 为 parent；ingest 校验 parent transmission linkage、executor request hash 与 external acknowledgement 三层绑定。
- `ReferenceMemoryExecutor` 是可执行 reference adapter，只用于证明协议闭环；真实 provider 的凭证、上传、提交、轮询、下载实现继续外置。

## v0.6.13 Provider Transport Integrity
- `PROVIDER_ASSET_HANDLE` 支持结构化 lifecycle：provider / state / expires_at / supersedes_handle / generation / content SHA256；过期、撤销、内容 hash 不一致会在 handoff HOLD。旧字符串 handle 继续兼容，但只具有 `DECLARED_ONLY` 语义。
- `EXTERNAL_ADAPTER` 现在有统一 Adapter Profile、字段映射、request hash、idempotency key、transmission ID 与 external job acknowledgement contract；统一 portable job 可以映射到真实 Provider API，而不把“已映射”误报为“已调用”。
- 外部 Provider Job ingestion 对远程输出 URI 要求 resolver 提供真实字节并重算 SHA256；没有 resolver、下载失败或 hash 不一致均进入 Review。Runtime 本身不伪装拥有网络权限。
- 新增可验证远程 artifact recovery：下载/解析后的字节必须先匹配 receipt SHA256，再写入本地恢复副本并再次校验。

## v0.6.12 可携带 Provider Package + Production Receipt
- 外部 Provider Job 必须自包含执行资源：LOCAL_FILE_PATH 商品母版在 handoff 时复制到 job `inputs/product_masters/` 并重绑为 `PACKAGE_RELATIVE_PATH`；Provider handle 保持显式 handle。
- 冻结资产包复制到 `inputs/asset_package/`，原 package hash 继续作为策略/设计合同 lineage；job.json 不再依赖 CBCC 主机绝对路径执行。
- 外部 `result.json` 必须带 `production_receipt`，绑定 job_id、asset_id、provider、package_hash、portable_manifest_hash、source_binding_hash 与输出文件 SHA256。
- LOCKED_PIXEL receipt 必须带 `layer_manifest` 证明真实商品层来自正确 source asset/hash 且保持 frozen；REAL_PHOTO / VIDEO receipt 必须带真实 `capture_metadata`，不得虚构 EXIF。

## v0.6.11 商品母版绑定 + 冻结层修订执行
- LOCKED_PIXEL 的真实商品母版必须以机器可执行 `source_product_bindings` 进入 Renderer Recipe 与 Provider Job；每个 binding 至少包含 asset_id、resolver/locator、SHA256、pixel_lock、allowed_transforms 与 identity_features。
- Provider handoff 不得只信 compile-time ingest 状态：LOCAL_FILE_PATH 在发单时重新检查文件存在与 SHA256；PROVIDER_ASSET_HANDLE 必须带已声明 SHA256。不可解析的真实商品母版使真实商品生产进入 HOLD。
- LOCKED_PIXEL Provider Result 必须回报 `source_product_asset_ids_used`、`source_product_hashes_used`、`product_layer_operation`、`product_identity_preserved`，并回显 `source_binding_hash`；ID/hash lineage 不一致进入 Review。
- Local Revision 除 `changed_fields` 外还必须回报 `changed_layers`；任何 frozen product-identity layer 被报告修改都触发 `FROZEN_LAYER_MUTATION_REPORTED`。
- Provider contract 对所有 LOCKED_PIXEL 模式（包括 GRAPHIC_DESIGN）要求 source-product binding，不再只对摄影/合成模式声明输入。

## v0.6.10 视觉执行边界 + 锁定文案隔离
- `approved_visual_elements`、`precision_boundaries`、`editable_layer_contract` 与 `product_fidelity` 是逐资产生产执行合同；不能只停留在 Design Card / JSON，必须在 Render Prompt 与人类 Visual 工作台出现正确的可执行子集。
- Render Prompt 必须明确允许视觉元素、精确边界、可编辑层、冻结层和商品 Fidelity；局部修改只能动明确可编辑层，LOCKED_PIXEL 商品身份层保持冻结。
- `information_design.locked_visible_copy` 是确定性文字合成权威。精确目标市场文案必须留在 `deterministic_copy_overlay` 与人类 Copy 工作台；Surface / Copy Budget 进入图像模型前必须移除 `locked_copy` / `visible_copy` 等精确文案字段。
- 人类单资产工作台的 Copy 阶段直接读取 `information_design.locked_visible_copy`，不再依赖旧 `copy_language` / `copy` 字段或旁路 Markdown 才能看到锁定文案。
- Parameter Trace 新增 `VISUAL EXECUTION BOUNDARIES / EDITABILITY`，用于证明视觉允许项、精确边界和编辑冻结合同真正进入执行层。

## v0.6.9 摄影执行合同连续性
- 显式 `Photography Contract` 是生产执行权威之一。`capture_mode`、完整 `composition` 字典与显式 `color_management` 必须原样进入 Design Card 的 `photography_execution`；不得只抽取旧白名单中的镜头、机位和灯光字段。
- `photography_execution` 必须继续进入 CN/EN Canonical Prompt、Parameter Trace、Machine Visual Contract 与人类单资产「摄影 / CMF」工作区。策划里用于出图的参数，最终必须能在执行层找到。
- Composition 使用开放字典语义：`product_occupancy`、`negative_space`、`subject_clearance` 或未来新增的执行字段均不得因编译器未预登记字段名而丢失。
- 显式输出色彩管理（例如 `output_space=sRGB`、真实商品颜色锁定）优先作为执行合同保留；策略派生的颜色一致性计划可以补充解释，但不能覆盖或吞掉显式合同。
- 仍然禁止把 Asset / Project / Direction ID、RACE、KPI 等内部元数据塞进 Render Prompt；摄影合同连续性只传递真正影响画面生成/拍摄/合成的参数。

## v0.6.8 单资产生产工作区
- 单资产详情页不再复用通用 `module-shell`。每张资产按当前真实内容动态形成 **决策 / Design Card → 画面执行 → 摄影 / CMF → 文案 → Prompt 执行 → QA / 来源** 的生产工作区；缺失阶段不占位，不预设固定阶段数。
- Design Card 概览与购买决策合并为同一个决策对象；Visual Execution 只回答消费者可见关系；Photography / CMF 承接镜头、机位、曝光、灯光、材质与颜色执行。
- 中文 Canonical Prompt 与英文 / 目标模型 Prompt 在同一个执行台核对与复制；Prompt 明确是前序策划参数的执行合同，不是独立创意来源。
- 合同、Parameter Trace、源文件与未知旧版资产内容进入 QA / 来源区，确保追溯完整但不污染最终 Render Prompt。
- 单资产生产阶段数量由真实资产内容动态决定；legacy 资产仍可回收进入 QA，不因新 UI 丢内容。

## v0.6.7 语义工作区 + 中文优先交付
- **默认交付语言是中文（zh-CN）**，除非用户明确要求其他语言。不要因为目标市场是英语、马来语、阿拉伯语等，就把策略、解释、风险、摄影策划或 HTML UI 变成大段外语。
- 区分 `delivery_locale` 与 `target-visible locale`：前者服务项目使用者，后者服务目标消费者。目标市场标题/描述/CTA/搜索词/资产可见文案可按策划使用本地语言，但人类交付必须在同一界面提供中文释义、用途或搜索意图说明。
- CN/EN Canonical Prompt 都要保留：中文 Prompt 是人类生产说明与审阅权威；英文/目标模型 Prompt 是渲染执行载体。任何英文 Prompt 不得成为唯一可读交付。
- `index.html` 不再使用报告式连续章节或“左侧锚点 + 长页面”。它是 **语义化 SaaS Workspace**，不同业务对象不能复用同一套页面骨架：Strategy 使用决策板，Content 使用内容泳道 / 矩阵，Visual 使用方向接触表 + Inspector，Listing 使用横向上架任务工作台，Prompt 使用资产选择器 + 中英双执行面板，Evidence 使用媒体证据墙 + 文档 / 文件账本。页面数量由真实输入动态决定，不固定方向数、内容数或资产数。
- 所有内容仍完整嵌入 HTML；“分页面”只是交互状态，不是把用户赶回 MD。MD/JSON/TXT 继续作为编辑与机器真源。
- 内部英文术语如 Product Truth / Prompt / Surface 可作为小号次级标签，中文名称必须是主要信息层。



## v0.6.5 SaaS delivery + prompt integrity rule
The product is **capability-first, not validation-first**. The runtime must finish the commercial reasoning and production language needed for the user to execute real work; automated checks are maintenance guardrails, never the main user-facing product or a substitute for strategy/creative capability.

The authoritative creative-production chain is now:
`Information Audit → Product Truth / Offer / Evidence → Research (Market / Platform / Audience / Race-Ethnicity-Culture / Competitor) → Action (STP / JTBD / Positioning / Message / 4P / Funnel / Visual / Budget) → Communication (Listing / Creator / UGC / Paid / CRM / Localization) → Evaluation (Metrics / Attribution / A-B / Feedback / Economics / Revision) → Product Visual Intelligence → Creative Opportunity Universe (6–12 mechanisms) → Direction Synthesis / Council → Creative Anchors → Dynamic Surface Architecture → Information Assetization → per-asset Visual Expression → Design Card → Canonical CN/EN Prompt Contract → Provider Job → Review / Local Revision → Learning`.

Required behavior:
- **RACE authority for this Skill is Research / Action / Communication / Evaluation.** Research covers product/market/platform/audience/race-ethnicity-culture/competitor truth; Action converts research into strategy, hierarchy, content, shoot and budget; Communication executes platform-native creator/UGC/paid/owned/localized distribution; Evaluation covers metrics, attribution, A/B, feedback and iterative revision. Do not substitute Reach/Act/Convert/Engage in this project.
- If no creative directions are supplied, first compile a **Creative Opportunity Universe** of 6–12 current-product mechanisms from Product Visual Intelligence, decision intents, Surface needs, reference whitespace/cliches, scale/use/material/risk/system evidence and remote-domain spatial logic. Only then synthesize 3–5 materially different directions. Stable route IDs are compatibility tags, not a fixed style library. Candidate directions must differ in buyer entry, creative thesis, composition grammar, product role, image language, proof mechanism, verbal thesis and/or color world; coherence must not collapse into repeated layout.
- Compile Product Visual Intelligence before downstream production: geometry, structure, materials/finish, transparency/reflectivity, label/identity faces, canonical views, source masters, visual risks and permitted reconstruction. Unknown product facts stay unknown.
- Foundation assets answer **who the product is**; Creative Anchors answer **how the chosen visual system behaves**. Anchors create continuity without forcing identical composition.
- Surface planning is dynamic. Decide whether information belongs in IMAGE / NATIVE_TEXT / HYBRID / SOURCE_VIEW / NOT_NEEDED / OFF_DOMAIN_HANDOFF before turning every useful fact into another image. Product presence is deliberate, not mandatory on every asset.
- Every activated asset receives a materially specific Visual Expression Variant and a full Design Card: shopper question, belief transition, RACE stage, decisive moment, subject/action/environment/props, composition/camera/crop, lighting/CMF/material behavior, information hierarchy, copy/language budget, Surface semantics, source masters, editable/frozen layers and measurement hypothesis.
- `05_prompt_CN.txt` and `06_prompt_EN.txt` are complete canonical production prompts, not thin summaries. They inherit the Design Card, Product Visual Intelligence, Creative Direction/Anchor, Surface contract, Copy contract, Photography/CMF, locale and Product Fidelity boundaries.
- Paid advertising is its own Campaign Architecture with objective, audience state, tension, offer, proof, landing handoff, materially different concepts and test hypotheses. It is not a resized PDP asset. Creator/Video/Live likewise use native hook/demo/proof/objection/CTA logic and rights/usage contracts.
- Exact approved visible copy should use deterministic text composition when precision matters. Image/video generation must not rewrite, translate or invent locked packaging or market copy.
- Preserve existing Market/Competitor, SKU/Economics, Listing, Platform, Culture/Localization, Evidence, Provider, Review, Local Revision and Learning capabilities. This rebase is additive and replaces thin creative/prompt handoff behavior, not those systems.


### Hard business / culture / execution contract
- Evidence grade is authoritative: **A = test report / official certification / reproducible measurement; B = supply-chain specification / formula or ingredient-mechanism support; C = subjective experience / creative hypothesis / pending validation. C must never become a hard claim.**
- Every major strategy decision answers **why this platform, this region, this audience, and—when relevant—this race/ethnicity/cultural context**. Unsupported identity-to-behavior inference is prohibited.
- Claims/compliance are P0. Efficacy, ingredient, certification, price, sales rank/volume and regulated categories (medical/beauty/food/finance and similar) require a separate evidence/compliance boundary; unknown current rules are `待查证`.
- Intersectionality evaluates relevant combinations such as ethnicity × gender × age × income × geography plus language/religion/lifestyle only when they affect representation, access, scene or purchase friction.
- Inclusive photography is P0 where people appear: skin-tone metering, deep-skin exposure/reflector/diffusion, hair texture, body/age/disability representation and AI-bias checks must be executable, not a generic diversity sentence.
- Platform execution includes dimensions/aspect, duration, cover/first-frame, subtitles, music/usage rights, traffic/discovery mechanism, CTA, landing handoff, UTM or equivalent attribution IDs. Unknown current platform mechanisms/rules are `待查证`.
- Localization includes native-language review/back-translation, holiday calendar when relevant, payment/logistics promise, religion/taboo review and local regulation. Unknowns remain `待查证`.
- Resource constraints force tradeoffs: **P0 = failure/claim/identity/compliance risk; P1 = material performance impact; P2 = enhancement.** Cut duplicate/decorative/low-information assets before P0/P1.
- Strategy rows prefer tables and contain **依据 + 取舍 + 可执行动作 + metric** rather than adjectives.
- Before delivery, self-check fabrication, WHY coverage, culture/intersectionality, compliance, metrics/attribution and explicit assumptions.
- Information lock: audit first → at most 10 clarification questions → explicit assumptions → continue under assumptions; ordinary missing information may not stop the whole strategy.
- FULL delivery is not complete unless all nine required sections, the RACE execution table, culture adaptation checklist, platform execution fields, P0/P1/P2 priorities and output self-check are materialized.
- Every delivery package includes a **self-contained offline SaaS-style `index.html` workspace** with task pages (Overview / Product Truth / Market & Audience / Listing / Strategy / Content / Visual & Photography / Asset Library / Prompt Lab / Risk & Compliance / Sources / Archive) plus independent in-HTML asset routes. The HTML contains the full human-facing delivery; Markdown/JSON/TXT remain editable/machine authorities, not required reading.

### Seven first-class commerce tool contracts
The reference seven-agent capabilities are first-class orchestrated tools rather than filename presence:
1. **Market Research** — cleaning/profile, concentration, price bands/valleys, configuration, competitor, keywords, customer voice and source-quality context.
2. **Product Strategy** — product truth/value ladder + SKU roles + pricing/economics + positioning/offer decisions and tradeoffs.
3. **Listing Creative** — keyword architecture → field authoring/decision map → Claim trace → platform/locale transcreation/back-translation → final-copy release contract.
4. **Product Image** — Product Visual Intelligence → creative opportunity/council → dynamic asset architecture → per-asset Design Card / canonical prompts / visual production contracts. Never regress to a fixed nine-image quota.
5. **Product Video** — native hook/script/storyboard/shot plan → video prompt → VO/subtitle/cover/music-rights/CTA/landing handoff with platform timing.
6. **Advertising Optimization** — funnel diagnosis + economics/break-even + creative/audience/placement analysis + P0/P1/P2 actions + attribution/UTM + incrementality boundary.
7. **Review Analysis** — eight commerce feedback classes + misunderstanding detector + defect-vs-communication + fixability + praise/issue ranking + exact reconciliation + local routing back to Listing/Image/Offer/Product.
Tools 6 and 7 feed the smallest responsible layer back into tools 2/3/4; they must not trigger indiscriminate full-plan rewrites.


### v0.6.5 production-parameter integrity
- Strategy-derived photography is executable planning, not decorative prose. When no measured shoot contract exists, provide a category/decision-specific **starting recommendation** for focal length/lens family, azimuth/elevation/roll, working-distance intent, camera height, shot size, focus plane, aperture/DOF, shutter, ISO, key/fill/negative/rim geometry, CCT/WB, light ratio, shadow/highlight policy, prelight, polarization, CMF/material and color consistency. Mark measured/final values as prelight-dependent rather than inventing them.
- Merge photography as **Master → Asset/Video Override → Shot Override**. A local override must not erase unrelated master parameters.
- Every image and video production contract exposes a `parameter_trace` showing how Strategy Authority parameters enter the render contract / prompt.
- Render prompts contain only generation-relevant production language. Asset/Video/Direction/Project IDs, RACE, KPI, audit status and internal scores stay in Design Card / Machine Contract / trace. Internal lead-ins such as `asset for <project>` or `For <project>, synthesize...` are not render instructions.
- Inclusive photography applicability is determined by the **final asset task**, not only by whether the input request explicitly supplied casting. Any person/hand/body relationship activates P0 skin-tone exposure, reflector/diffusion, hair texture, body/age/disability representation and AI-bias controls.
- Claim Authority is normalized **before** positioning/listing/compliance/asset decisions. `APPROVED`, `VERIFIED` or a declared A/B label does not create evidence; only linked A/B support may enter hard/bounded claims or Primary Value.
- Product Truth provenance is field-specific. Do not attach every project source to every fact. Unmapped user facts remain `USER_SUPPLIED_UNMAPPED`.

### Plugin execution boundary
The packaged Python seven-tool runtime is a real local Runtime/CLI capability, but the current private ChatGPT plugin is Skills-only unless a verified `mcp.json` is present. Do not claim that normal ChatGPT plugin chat is directly invoking the Python seven-agent functions. In Skills-only mode, ChatGPT follows the same contracts using host tools. Direct tool invocation requires a separately deployed MCP server.

## v0.5.14 real-production quality rule
A real-product production route is not executable merely because a Provider exists. For LOCKED_PIXEL and other real-product modes, bind exact source product masters with hash lineage first. Missing or mismatched masters remain explicit holds; never silently substitute a generated/reconstructed product.

Every asset must carry a decision-specific visual production signature and semantic editable/frozen layer contract into the Provider Job. Distinct shopper decisions must remain visually distinct through composition grammar, evidence plane, context role and surface-native execution rather than collapsing into one reusable centered-product layout.

Provider completion requires evidence-bearing quality observations for the relevant dimensions (product fidelity, decision visibility, surface usability, copy-visual alignment, Photography/CMF and visual differentiation). Boolean QA remains compatibility metadata, not sufficient production evidence. Local Revision may edit only declared semantic layers and must never alter LOCKED_PIXEL product identity. Production learning should revise the smallest implicated execution layer before escalating Product Truth, Positioning or Offer.

## v0.5.11 integration rule
A capability is **not** considered integrated merely because a file, prompt, knowledge document, calculator, toolkit or test exists. It must have a runtime consumer and materially change or constrain at least one of: Strategy Authority, Dynamic Asset Architecture, Final Copy, per-asset production contracts, Provider Jobs, or Measurement / Revision Routing. QA/lint/validator wrappers remain background guardrails and are not counted as strategy capability.

Evidence-quality reconciliation must weight current market/search/review/competitor signals by declared traceability, freshness, representativeness metadata, scope match, explicit source quality and source agreement/conflict. Market observations require explicit Product Truth fit before creating own-product asset jobs. Ads and Feedback diagnostics must route to local strategy edit/freeze layers rather than trigger whole-plan rewrites.

## v0.5.13 real-product quality rule
A strategy is not professionally deep merely because every framework, asset file or runtime capability exists. Preserve every live consumer decision question through atomic decision coverage, Listing field routing and Dynamic Asset curation. Category priors may sequence questions but may not erase product-specific decisions. Proof contracts must follow the atomic decision topic (for example clinical evidence vs formula fact vs cleaning vs compatibility).

When deterministic Strategy Authority is commercially shallow, materialize `strategy_host_authoring_request.json` and return professional reasoning under `strategy_annotations`. Host/model interpretation may deepen value, Positioning, message hierarchy, Listing/Visual WHY and execution, but must not overwrite Product Truth, claim/evidence ledger, deterministic market/economics/experiment results, exact policy authority, Final Copy release state or asset hashes. Extra numeric Final Copy is allowed only through explicit field-level approved Claim authority.

## v0.5.12 executable production-learning rule
A review-requested Local Revision must be compiled as a separate scope-limited Provider Job; never rewrite the parent `00–11` package in place. Preserve parent package hash, `allowed_fields`, revised output hash and independent re-review. Post-change metrics produce descriptive learning by default; causal credit requires explicit valid causal evidence. Apply learning only to implicated edit layers and keep declared frozen layers authoritative.

Runtime CLI lifecycle: `provider-ingest → review-apply → revision-compile → revision-ingest → review-apply → learning-apply`.

## Canonical mainline
`Information Audit → Product Truth → RACE Research → RACE Action (STP/JTBD/Positioning/4P/Funnel/Visual/Budget) → RACE Communication (Listing/Creator/Paid/Owned/Localization) → RACE Evaluation (Metrics/Attribution/A-B/Feedback/Economics) → Dynamic Asset Architecture → Asset Compiler → Production → Local Revision / Learning`

## Required final strategy deliverables
Every complete strategy project must materialize the following nine sections and explain **WHY** for major decisions:
1. Information completeness, pending confirmations, assumptions and decision log.
2. Product truth audit and value ladder: real selling point / perceived benefit / emotional value / unclaimable item / A-B-C evidence grade / publication status. C-level material is soft-only and cannot be a hard claim.
3. Platform × region × audience × race/ethnicity/culture insight, including intersectionality and stereotype/taboo review.
4. Product/SKU/Offer strategy, positioning, value proposition, message hierarchy, STP, JTBD, RACE, AIDA, FABE, 4P, Funnel, Fogg, Means–End, Signaling, FIRST, Cognitive Budget, Belief Sequence and Commerce Response Ladder.
5. Visual strategy and shoot plan: style/moodboard, composition, role-based HEX + contrast, CMF, lighting direction/CCT/key-fill/soft-hard, focal length, framing, camera position, scene, props, casting/wardrobe/hair/makeup, platform dimensions, shot list, deep-skin exposure/reflector/diffusion and AI-bias controls.
6. Platform content matrix: platform / audience / topic / hook / script structure / visual form / CTA / metric / RACE / culture adaptation + taboo check / dimensions / duration / cover / subtitles / music rights / traffic mechanism / landing handoff / UTM or equivalent attribution / WHY.
7. RACE execution table: stage / objective / action / output / platform / culture check / KPI / WHY.
8. Culture adaptation checklist: adaptation / inclusive representation / stereotype or taboo concern / result / modification / WHY.
9. Compliance/cultural risk, measurement and A/B hypotheses, P0/P1/P2 action plan and next information needed.

## Decision contract
For every major strategy decision use the structure:
`WHAT → WHY → EVIDENCE → CONSUMER LOGIC → PLATFORM LOGIC → CULTURE LOGIC → BUSINESS LOGIC → EXECUTION → MEASUREMENT`.
Frameworks are decision lenses, not forms to fill mechanically.


## Professional-depth rule
A structurally complete report is not enough. Do not stop at generic statements such as “target audience”, “use suitable CTA”, “premium visual”, or “optimize conversion”. The final strategy must convert evidence into a concrete commercial decision and explain WHY. Deterministic tools calculate; the strategy/model layer interprets those results and changes SKU/positioning/listing/content/visual/measurement accordingly.

Use the specialized prompt authorities in `prompts/registry.json` when a domain requires deeper reasoning. The nine-section final report is the synthesis layer, not a substitute for Market, SKU, Listing, Creative, Culture or Measurement reasoning.

## Positive-first policy
Describe the desired commercial and creative result first. Plants, water, laboratory cues, models, props, environments, textures, graphics and motion are selectable creative devices when they serve product truth and the shopper decision. Add precision boundaries only where they prevent factual, rights, safety, product-identity, cultural or platform errors.

## Product truth and value
Keep `Fact → Advantage → Perceived Benefit → Emotional Value → Proof` distinct. A useful strategy idea can exist before final evidence is complete, but publication-sensitive hard claims retain evidence status and cannot silently become product facts.

## Market / Product / Economics tool split
Semantic interpretation and strategy belong to the strategy/model layer. Deterministic tools handle cleaning, aggregation, CR3/CR10/HHI, price/configuration matrices, contribution waterfalls, break-even ROAS/CPA/CPC, listing lint/trace, advertising metrics, feedback aggregation and experiment statistics. Tool results feed strategy; they do not replace reasoning.

## Audience, culture, race/ethnicity and intersectionality
Identity variables may affect representation, casting, language and context when supported by evidence. They are not shortcuts to consumer behavior. Evaluate relevant intersections such as ethnicity × gender × age × income × geography × lifestyle and convert them into concrete copy, casting, styling, scene, gesture, photography and CTA implications with rationale.

## Photography / CMF
When relevant, specify executable contracts for focal length/equivalent, working distance, camera height, yaw/pitch/roll, crop/product occupancy, focus plane/DOF, key/fill/negative-fill/rim, modifier geometry/distance, CCT/WB, contrast, shadows, exposure/highlight protection, reflection/material control, skin-tone metering, output color space, product color fidelity, CMF, styling and props. The plan also explains **why** those choices fit the commercial job.

## Asset package preservation — mandatory
The Strategy Authority is upstream of asset production and must never replace or collapse the established asset package workflow.
Each activated asset retains the complete package:
- `00_asset_manifest.yaml`
- `01_strategy.md`
- `02_visual_spec.md`
- `03_photography_contract.json`
- `04_layout_contract.json`
- `05_prompt_CN.txt`
- `06_prompt_EN.txt`
- `07_generation_guidance.txt`
- `08_copy.md`
- `09_production_notes.md`
- `10_source_trace.md`
- `11_strategy_authority_trace.json`

The canonical `00–11` contract remains unchanged for backward compatibility. v0.6.0 adds production-depth companions instead of replacing it:
- `12_design_card.json`
- `13_prompt_contract.json`

`12` carries the complete per-asset commercial/decision/visual/production specification. `13` carries the canonical CN/EN prompt contract, machine visual contract, renderer recipe and QA target used by Provider Jobs.

`03` and `11` stay present even when their content is not applicable/supplied; they carry an explicit status instead of disappearing. Provider Jobs, Provider Results, Review Items, Local Revision records and Package Hash continuity remain part of the workflow.

## Research and platform rules
Missing exact platform/site/category/program rules should not stop the whole strategy. Continue all evidence-supported strategic work and hold only the submission-sensitive decision that depends on the missing rule. Family planning capability never equals exact submission readiness.

## Knowledge / Ontology / Prompt layers
- `knowledge/`: reusable commercial reasoning.
- `ontology/commerce_ontology.json`: shared entities, relations, constraints and processes.
- `prompts/registry.json`: executable strategy/prompt authority references.
- `runtime/`: deterministic and stateful project execution.
These layers prevent all expertise from being buried in one giant prompt.

## Strategy reasoning context
The runtime dynamically selects relevant `knowledge/`, ontology entities/relations/constraints and registered prompts, extracts authority content, binds it to the nine Strategy Authority sections, and materializes `artifacts/strategy_reasoning_context.json`. These layers are runtime-consumed rather than passive documentation. Deterministic tools remain the authority for calculations and Product Truth remains the authority for facts.


## v0.5.10 evidence-commerce reconciliation depth
- Treat Category Commerce Profiles as strategic priors, not unquestioned winners. The runtime reconciles them against scoped Product Truth, own shopper/feedback/behavior evidence and current market/search/review/competitor evidence.
- Evidence may reorder objection, proof, message and platform-expression priorities, but may not create product facts, claims, certifications, price economics or service scope.
- Preserve the authority order: Product Truth / verified policy & evidence → own evidence → current scoped external evidence → category prior → generic fallback.
- Proof hierarchy rows declare evidence conditions and input support rather than treating a category-typical proof format as if evidence already exists.
- Promo response, bundle affinity and repeat/replacement observations are descriptive offer evidence. They may support a test candidate but do not establish causal elasticity, incrementality or a final promotion/CRM cadence.
- Platform × category intersection changes entry logic, information density, proof rule and offer role while keeping Product Truth and evidence priority stable across surfaces.
- Reconciliation decisions must remain traceable through WHAT/WHY/EVIDENCE/CONSUMER/PLATFORM/BUSINESS/EXECUTION/MEASUREMENT.

## v0.5.3+ portfolio / competitor / localization depth
- Competitor intelligence joins source-bounded Listing message/offer/proof observations with explicitly labelled review themes before positioning decisions.
- Multi-SKU strategy evaluates overlap/cannibalization hypotheses, trade-up justification and lifecycle offer roles; no forecast percentage is invented without behavioral evidence.
- Listing transcreation materializes locale × field authoring tasks and audits supplied localized numerical facts.
- Platform Content Matrix now carries locale-specific authoring tasks, beat plans and copy contracts while preserving dynamic asset count.
- Market/review themes may create new Dynamic Asset jobs only after explicit Product Truth fit confirmation.


## v0.5.4 research / behavioral validation / Final Copy depth
- Market/competitor/customer research must preserve source IDs, dates, declared freshness windows, sampling metadata and scope boundaries. Never infer representativeness from N.
- Structural SKU overlap is a hypothesis. Use cross-shopping, switching, cohort and treatment/control evidence to validate portfolio decisions while keeping descriptive behavior separate from causal incrementality.
- `_localized_copy` is an authored draft/source layer, not automatic Final Copy. `_localized_copy_reviews` must explicitly approve native fluency, claim equivalence, platform fit and culture fit before `APPROVED_FINAL`.
- TikTok Shop, Shopee, Amazon and DTC/Shopify use distinct native commerce authoring systems. Reuse Product Truth / Positioning / Message Hierarchy / evidence, not identical copy or beat sequence.
- Preserve `artifacts/listing_final_copy.json` and per-locale Final Copy files in delivery when Listing authoring is present.


## v0.5.5 evidence / incrementality / authoring / surface depth
- Research ingestion defaults to `REPORT_ONLY`; deterministic dedup is opt-in and limited to exact same-source row fingerprints. Cross-source duplicate candidates remain separate provenance evidence.
- Source version lineage records explicit `supersedes` relationships separately from merely observed chronological versions; later is not automatically more truthful.
- Directional switch rates require explicit eligible-from denominators. Shared visitors alone are not a switch or cannibalization rate.
- Holdout calculations may report arithmetic incremental orders/contribution, but do not claim statistical significance; assignment integrity, interference, power and pre-period balance remain experiment-review concerns.
- Localized copy review is version-bound. Any revised version invalidates an older approval until the current version passes hard checks plus native fluency, claim equivalence, platform fit and culture fit review.
- Authoring work is materialized as author / revise / re-review tasks rather than pretending deterministic runtime can judge native-language quality.
- Platform-native logic is compiled at the actual commerce surface, not only at platform-family level.
- Every image asset carries an asset-level photography reasoning chain into `02_visual_spec.md` and `03_photography_contract.json`; the master photography recipe is not treated as a sufficient explanation by itself.


## v0.5.6 adapter / causal / copy / production / CMF depth
- Research adapters may normalize full snapshots or incremental batches into canonical market/keyword/review/competitor datasets. Primary-key change sets and high-watermarks are provenance signals; semantic near-duplicates are review-only and never silently deleted.
- Experiment Strategy Authority reviews assignment/randomization, pre-period balance, MDE/power planning, contamination, spillover and interference before interpreting outcome lift. Arithmetic significance or lift never substitutes for design validity.
- Host/model authoring responses create new locale × field copy versions only. The current version must pass deterministic hard checks and explicit native fluency / claim equivalence / platform fit / culture fit review; old-version approval becomes stale after revision.
- Platform-native strategy must compile a surface production contract covering decision job, first frame/line, safe-zone/copy-density logic, motion/demo/audio/caption logic, product fidelity, reuse-vs-recompose, deliverable intent and measurement. Exact submission limits come from current platform authority, not generic runtime guesses.
- Supplied CMF/material signals must affect shot-level lighting reasoning. Explain key geometry, fill/negative fill, reflection/highlight handling and color management for the actual material response. When finish behavior is unknown, require a material test frame rather than inventing one.
- These additions must flow into the nine Strategy Authority sections and active asset `00–11` packages; they are not sidecar calculators or new Gate systems.


## v0.5.9 category-commerce depth

The Runtime must not stop multi-category specificity at visual style or asset type. It must use the project category family, Product Truth and actual consumer decision questions to compile a **category commerce profile** that can change:

- Listing objection priority and PDP decision order;
- proof hierarchy and proof conditions;
- offer patterns that should be tested, without locking unsupported discounts/services/bundles;
- message sequence and category-specific script structure;
- content cadence as module rotation + refresh triggers, never an invented posting-frequency rule.

Current category families include beauty/personal care, apparel fit, fashion accessory, food/beverage, electronics, home durable, high-ticket durable and general commerce fallback. Category profiles are strategy hypotheses, not Product Truth. They must never create certifications, dietary facts, compatibility, performance evidence, warranty/service scope, delivery/installation promises, returns policy, sensory facts or pricing economics.

Category decision-intent classification must use controlled word/phrase matching. Avoid substring collisions that can manufacture false intent. The generic P0/P1/P2/P3 hierarchy may remain as a cross-category compatibility reference, but category message/proof/objection architecture must be visible in the formal Strategy Authority and Platform Content Matrix.

## v0.5.8 multi-category strategy-specificity depth
- Reuse the commerce decision architecture across categories, **not** one fixed asset sequence, surface mix, visual territory or photography recipe.
- Infer a category execution profile only from supplied product/category context. The profile guides purchase-decision priorities, visual territory and provisional photography planning; it does not create Product Truth or claims.
- Auto-curated purchase questions should be classified into decision intents such as identity, fit/wear, size/capacity, leak/seal, storage/stacking, care, compatibility, material/sensory, proof, relevance and usage. Merge repeated questions only when they solve the same decision intent on the same production surface/family.
- Explicit user-authored asset jobs are authoritative and must not be silently semantically merged.
- Platform-pack capability/surface gaps mark strategy objects as research-required; they do not delete useful strategic surfaces. Submission readiness remains separate from planning eligibility.
- When no explicit photography contract is supplied, category/decision-specific camera and lighting recommendations may be created as `STRATEGY_DERIVED_PHOTOGRAPHY_PLAN`, but must remain `prelight_required` and cannot masquerade as measured execution settings.
- CMF reasoning must respond to material behavior: textile/woven, transparent/glass, glossy, metallic and matte products should not inherit one beauty-style soft-light treatment.
- Multi-category validation is a professional-quality check, not a Gate-count target. If materially different categories produce essentially identical asset portfolios or photography WHY without evidence, treat that as a strategy-homogenization defect.

## v0.6.3 historical human-first delivery note — superseded by v0.6.6
The v0.6.3 rule that HTML must contain the complete human-readable delivery remains valid, but its **Commerce Editorial long-report presentation is superseded**. v0.6.6 authority is the object/task-based offline SaaS Workspace defined at the top of this Skill and in `references/FINAL_OUTPUT_CONTRACT.md` / `references/REPORT_THEME_CONTRACT.md`. Source files remain editable authorities; exact platform categories still require current site-tree evidence and otherwise remain `待查证`.
