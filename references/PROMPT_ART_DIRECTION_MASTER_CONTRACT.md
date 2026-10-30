# CBCC PROMPT + ART DIRECTION MASTER CONTRACT

## 0. 核心定义

**Prompt ≠ 摄影参数集合。**

CBCC 的生产 Prompt 不是“镜头 + 灯光 + 背景”的参数串，也不是几句风格词。它是一个已经完成商业策展和逐资产 Art Direction 的**完整商业画面 / 动态作品的无损编译结果**。

Prompt 上游必须先决定：
`Product Truth → Consumer Decision → Commercial Objective → Portfolio Curation → Visual Carrier → Per-asset Art Direction → Surface Adaptation → Production Parameter Closure`。

Prompt 只负责把这些已完成的决策转换为当前模型可以直接执行的自然语言。Prompt Compiler 不得在上游缺失时自行用 packshot、居中产品、左右分栏、暖白背景、soft light、premium editorial 等模板补洞。

**只含摄影参数、只含风格词、只含产品+背景、只含几句商业任务，必须判为不合格。**

---

# 1. 商业决策层：Prompt 必须知道为什么存在

每个资产先锁定：
- **商业决策**：这个资产推动哪个购买决定；
- consumer question / shopper question；
- **购买障碍**；
- entry state；
- target belief / **信念转变**；
- Strategic Job；
- **增量信息**：用户从这一资产新学到什么；
- handoff：看完后应进入哪个下一步；
- **商业假设**；
- **成功指标**；
- Surface need：为什么这个平台/版位需要独立资产；
- WHY：为什么这个市场、人群、文化语境下如此表达。

这些是 Art Direction 的因，不是要原样堆进画面。Prompt 必须让其改变视觉结果，但不得把 RACE/KPI/内部状态/工程字段直接塞进模型提示词。

---

# 2. 人物 / 主体层

## 2.1 人物 / 主体
主体可为人、动物、植物、商品、身体局部、手、物体、环境、文字/信息结构或多个主体组合。人物不是强制；人物出现必须有商业角色。

人物相关至少按资产相关性决定：
- **人物角色**：用户、达人、专家语境、家庭成员、操作主体、陪衬等；
- **年龄**；
- **肤色**与曝光/暗部保护；
- **发型 / 发质**；
- **妆容**与皮肤修饰边界；
- **服装 / 配饰**；
- 体型；
- 残障呈现；
- 宗教/文化相关服饰与身体呈现；
- **姿态**；
- **表情**；
- **视线**；
- **手部动作**；
- 握持/按压/涂抹/拆封/倒取等物理动作；
- **人物与产品交互**；
- 人物与道具/环境的关系；
- 人物在画面中的角色强度：hero / supporting / contextual / detail / absent。

人物不应只是“lifestyle model”装饰。

## 2.2 非人物主体
对动物/植物/物件/环境等主体也必须明确：
- 主体身份；
- 状态；
- 动作/变化；
- 与商品的物理/语义关系；
- 可见细节；
- 尺度；
- 空间位置；
- 是否承担证据功能。

---

# 3. 动作与 decisive moment

每个需要叙事的资产必须有具体**动作**、**行为**或**时间瞬间**，而不是静态物品清单。

至少按相关性决定：
- action；
- gesture；
- handling；
- use moment；
- transformation moment；
- before/after 仅在有合法证据时；
- interaction mechanics；
- **decisive moment**；
- 动作方向；
- 力量/速度/节奏；
- 手/身体/产品接触点；
- 液体、织物、凝胶、粉末、包装等的真实物理行为。

---

# 4. 元素、场景、环境、道具

## 4.1 场景世界
Prompt 必须根据策展决定具体：
- **场景**；
- **环境**；
- 室内/室外/棚拍/生活空间/零售空间/抽象信息场等；
- 时间、季节、天气（需要时）；
- 地域/文化环境线索（有依据时）；
- 地面/台面/墙面/背景材质；
- **前景**；
- **中景**；
- **背景**；
- 空气感、空间深度与环境光。

## 4.2 元素和道具
逐项决定：
- **元素**；
- **道具**；
- **表面 / 承托**；
- 容器、织物、镜面、水体、植物、家具、器具、包装附件、来源文档等；
- 每个元素的战略作用；
- 元素数量与信息预算；
- 与产品/人物的关系；
- 真实尺寸与尺度；
- 前后遮挡；
- 哪些必须真实、哪些可以抽象化；
- 哪些元素禁止出现以避免错误联想/医疗化/实验室化/廉价模板感。

道具不是装饰库存；没有商业作用的道具应被删除。

---

# 5. 视觉载体、视觉钩子与情绪节奏

每资产要选择**视觉载体**，例如：
- product portrait；
- use moment；
- tactile macro；
- material study；
- diagrammatic evidence；
- comparison；
- scale demonstration；
- lifestyle vignette；
- source/document view；
- editorial information field；
- packaging trust board；
- unboxing / contents；
- creator-native frame；
- dynamic motion sequence；
- 其他项目特定载体。

同时决定：
- **视觉钩子**：第一眼抓住什么；
- first-scan answer；
- Hero Moment；
- **情绪节奏**；
- **信息密度**；
- Cognitive Budget；
- 视觉叙事顺序；
- 视觉张力与呼吸；
- 品牌识别与当前资产差异的平衡。

---

# 6. 商品角色、出现节奏与真实性

每个资产明确：
- **商品角色**；
- Product Presence：HERO_REQUIRED / REQUIRED / SUPPORTING / OPTIONAL→PRESENT|ABSENT / DETAIL_ONLY / FORBIDDEN；
- **商品出现节奏**：在整套 portfolio 中何时 hero、何时 supporting、何时 detail、何时 absent；
- **产品占画**；
- product envelope；
- scale relationship；
- **身份锚点**：Logo、品牌、标签、包装形态、部件、颜色、材质、印刷等哪些必须可辨认；
- source reference role：SUBJECT_REFERENCE / TRUTH_REFERENCE_ONLY / LOCKED_SOURCE_LAYER / NOT_NEEDED；
- fidelity 路由；
- 遮挡允许范围；
- 真实产品与环境的接触、阴影、反射、透视关系。

Product Fidelity 不能被误解为 Product Presence。真实参考存在不代表每张图必须展示产品。

---

# 7. 构图与空间系统

Prompt/Art Direction 必须按当前资产决定：
- **构图语法**；
- **空间关系**；
- **尺度层级**；
- **深度关系**；
- product/subject relative placement；
- asymmetry / balance；
- crop；
- orientation；
- foreground / midground / background relationship；
- **焦点路径**；
- **负空间**；
- visual flow；
- evidence zone；
- copy zone；
- **safe zone**；
- mobile crop / thumbnail crop；
- foreground occlusion；
- frame-edge behavior。

不得把“左文右图 / 右文左图 / 居中产品 / podium / card grid / split screen”当默认电商语法。

---

# 8. 证据与信息层级

每资产明确：
- **证据层级**；
- **主证据**；
- **次级证据**；
- proof / support；
- **Proof Hierarchy**；
- 信息是文字、图形、实物关系、来源文档、材质细节、尺寸关系、使用动作还是其他可视证据；
- 证据与 Product Truth 的对应关系；
- 哪些事实允许视觉化；
- 哪些不能夸张、不能制造临床/认证/实验室错觉；
- A/B/C 证据如何影响表达强度。

证据不等于“加一个 badge”。

---

# 9. 文案、字体与信息设计

当资产有可见文字时，必须决定：
- **文案** exact string；
- headline / support / proof / CTA；
- 文案预算；
- 是否 MODEL_RENDER / HYBRID / POST_COMPOSITE / NO_VISIBLE_COPY；
- **字体**角色；
- type character；
- **字重**；
- **字号层级**；
- **行数**；
- line length；
- **对齐**；
- **排版关系**；
- 字间/行间的视觉密度；
- 与产品/证据/人物的关系；
- contrast/background；
- **safe zone**；
- mobile legibility；
- 文案是否需要与场景透视/表面结合；
- 禁止模型额外生成未批准营销文字。

字体不是“clean sans-serif”一句话就算完成；要说明它在当前层级中的角色与视觉关系。

---

# 10. 目标市场语言与本地化排版

按当前平台/市场决定：
- **目标市场语言**；
- exact publishable copy；
- English semantic baseline（非英语市场）；
- 中文释义/用途；
- native review / back-translation；
- **本地化排版**；
- 长词/短词造成的版式变化；
- **RTL**；
- **CJK**；
- Thai/Arabic/Latin 等脚本行为（相关时）；
- 单位、货币、日期；
- transcreation；
- 文化语义；
- 不同语言对字号、行数、信息密度、对齐、阅读顺序造成的变化。

不能把英文版排版机械换字后当本地化。

---

# 11. 文化、人群与包容性进入画面

当与当前资产有关时，Prompt/Art Direction 必须消费：
- **文化语境**；
- 语言；
- 宗教；
- 节日；
- **禁忌**；
- 家庭结构；
- 日常行为；
- **包容性表征**；
- 肤色、发质、体型、年龄、残障；
- wardrobe/grooming；
- 人物关系；
- AI bias review；
- stereotype guard。

文化适配改变的可以是：购买问题优先级、证据、顺序、人物、场景、道具、色彩、构图、文案、排版、CTA，而不是加一个“本地元素”装饰。

---

# 12. CMF、材质、颜色与真实物理响应

按资产相关性决定：
- **CMF**；
- **材质**；
- **微表面**；
- matte / satin / gloss；
- **透明 / 半透明**；
- **反射**；
- 折射；
- **高光**；
- subsurface；
- microtexture；
- seam / edge；
- fabric drape；
- liquid/gel/foam viscosity cues（只有真源支持时）；
- deformation；
- contact behavior；
- **颜色系统**；
- **HEX**；
- 主/辅/背景/文字色；
- contrast；
- verified pack color；
- saturation；
- neutrality；
- final grade；
- color management。

材质必须真实响应灯光，不是用“premium texture”代替。

---

# 13. 摄影、光学与灯光只是其中一层

相关资产再进入：
- lens / focal length；
- working distance；
- camera height；
- yaw / pitch / roll；
- shot size；
- perspective；
- focus plane；
- aperture / DOF；
- shutter / ISO（相关时）；
- key / fill / negative fill / rim；
- modifier size/distance/angle；
- CCT / WB；
- light ratio；
- exposure；
- shadow/highlight policy；
- reflection/polarization；
- Prelight；
- skin-tone exposure；
- color management；
- finishing。

这些参数必须服务前面的商业画面设计。**摄影参数完整但人物/动作/场景/空间/证据/文案/材质/文化/平台逻辑为空，仍是不合格 Prompt。**

---

# 14. 平台、站点、Surface、设备与输出

每资产按真实使用面决定：
- **平台**；
- **站点**；
- **Surface**；
- **设备**；
- **画幅**；
- **尺寸**；
- **色彩空间**；
- resolution；
- thumbnail behavior / **缩略图可读性**；
- crop behavior；
- safe areas；
- mobile first hierarchy；
- platform-native behavior；
- cover/first frame；
- submission constraints（已验证或待查证）。

不能把同一张图简单 resize 成所有 Surface。

---

# 15. 动态、视频、Creator、LIVE

当资产为动态媒体时，除上述静态世界外，还必须决定：
- **动态**机制；
- duration；
- **镜头序列**；
- **beat**；
- hook timing；
- **主体运动**；
- **相机运动**；
- framing changes；
- frame rate / stabilization（相关时）；
- **转场**；
- **字幕**；
- **VO**；
- **音频**；
- music / rights；
- product handling；
- creator performance；
- CTA hold；
- first frame / cover；
- platform-native rhythm；
- live objection/demo/offer loop（LIVE 时）；
- landing/attribution handoff。

Video / Creator / LIVE 不继承静态 PDP 的固定版式，也不固定五段式。

---

# 16. 差异化签名与 Portfolio Rhythm

每个资产必须说明：
- 为什么不能由上一张替代；
- 新增了什么购买信息；
- 新的 visual carrier / scene / scale / subject / evidence / spatial relation 是什么；
- **差异化签名**；
- **与相邻资产的 rhythm delta**；
- 哪些 continuity tokens 保持同一品牌世界；
- 哪些必须变化以避免模板化。

禁止整组资产只是：暖白背景 + 左文右产品 + 柔光 + 小道具的换文案版本。

---

# 17. QA、修复与真实输出闭环

Prompt 只是生产前对象。生成后必须做真实结果 QA：
- **QA** 产品身份；
- Logo / 标签文字 / 包装几何 / 部件；
- 人物/手/动作；
- 场景/元素/道具；
- 证据真实性；
- copy spelling / exactness / hierarchy；
- typography legibility；
- CMF/material；
- color fidelity；
- occupancy/safe zone；
- mobile legibility；
- 多语言溢出；
- artifact；
- platform readiness；
- 与相邻资产是否重复；
- 商业决策是否第一眼成立。

失败时走**最小责任层修复**：
- prompt refinement；
- reference change；
- local edit/mask；
- typography-only repair；
- crop/surface adaptation；
- product/reference regeneration；
- provider/model change；
- post-composite（只有此时成为最佳路线时）。

保留 Provider → Result → Review → **Local Revision** → package/hash lineage。

修复不能把商业决策、证据、文化、本地化、差异化或参数密度一起删掉。

---

# 18. 四生产对象中的职责边界

## Model Prompt CN
完整中文 model-native 视觉/动态执行语义；目标市场 exact copy 可保留原语言。

## Model Prompt EN
完整英文 provider-readable 视觉/动态执行语义；允许 exact quoted target-market render strings；不能混中文说明；不能因为“英文纯度”而删减任何已选像素/时序/排版/材质/人物/场景决策。

## Visible Copy Block
exact target-market copy + hierarchy + locale + render route + English baseline（非英语市场）+ 中文翻译/用途 + copy budget。

## Production / Assembly Notes
source/reference/fidelity + editable/frozen layers + assembly + provider route + output + QA + revision boundary。不得把应进入 Model Prompt 的画面世界全移到 Notes，导致模型实际拿到的 Prompt 变薄。

---

# 19. Prompt READY 的真实标准

一个资产的 Prompt READY 必须同时满足：
1. 商业决策已闭合；
2. 逐资产 Art Direction 已闭合；
3. 人物/主体/动作/元素/场景/道具等相关内容已具体化；
4. 商品角色/出现策略/参考行为已闭合；
5. 构图/空间/证据/文案/字体/语言/文化已闭合；
6. CMF/材质/颜色/摄影/灯光等相关执行已闭合；
7. 平台/Surface/设备/输出已闭合；
8. 动态媒体的镜头/运动/音频/时序已闭合；
9. Production Parameter Closure 中所有已选结果改变型值已被正确对象消费；
10. 与相邻资产的差异化机制明确；
11. QA 合同和最小修复路由明确。

任何只靠“字段存在”“prompt 字数够长”“摄影参数很多”来判 READY 的方式均无效。
