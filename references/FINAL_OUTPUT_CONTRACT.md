# Final Output Contract — 人类交付权威

## 1. HTML 是完整正式交付，不是报告目录
`index.html` 必须是自包含离线工作区。禁止“左侧目录 + 一条长报告”、禁止把所有 Markdown 按顺序摊开、禁止要求用户跳出 HTML 才能理解项目。

主工作区按业务任务/对象组织：
- 工作台
- 产品事实
- 市场 / 人群 / 文化
- 上架中心
- 策略中心
- 视觉 / 摄影
- 资产中心
- 提示词工作台
- 风险 / 合规
- 来源 / 真源
- 归档（次级）

每个模块还应有自己的子页；一次只显示一个主题。移动端把子页改为可横向滑动标签。

## 2. 上架中心是任务型界面
至少分为：基础信息、类目 / 属性 / 规格、标题与详情文案、搜索与关键词、价格 / 履约 / 售后、多语言 / 中文对照、媒体槽位。

每个可复制字段显示状态、目标语言、目标文案。**人类字段标题必须以中文作为主标题**；TikTok Shop / Amazon / Noon / Shopee / Lazada 等平台原始字段 key 可作为次级技术标识显示，但不能直接用英文 key 充当唯一标题。

若目标文案不是交付语言，还必须在同一字段对象显示中文释义 / 用途；搜索词可以解释搜索意图而不做机械逐词翻译。缺少中文 companion 的外文 Listing 内容不得通过人类交付验收。

## 3. 资产中心是对象型界面
资产库只负责选资产。进入某个 Asset 后，再在同一 HTML 中切换：资产概览、策划与决策、画面与版式、摄影 / CMF、文案、中文 Prompt、英文/目标模型 Prompt、生成 / 生产、合同 / QA / 来源。

资产中的目标市场可见文案可以使用英语、马来语、阿拉伯语或其他本地语言，但**每一组外文可见文案必须在同一资产对象中提供中文释义 / 用途**。例如 headline、subhead、CTA、badge、caption、hook、script overlay 等不能只给外文。逐资产 `00_HUMAN_DESIGN_CARD_CN.md` 必须存在并以中文解释该资产为什么存在、画面如何执行、目标市场原文是什么、中文释义是什么。

## 4. 语言权威
- 默认 `delivery_locale = zh-CN`，用户明确要求其他语言时覆盖。
- `target-visible locale` 按目标市场与平台策划决定。
- 策略、解释、WHY、风险、摄影策划、UI、字段标题默认使用 delivery locale；当前默认即中文。
- 非 delivery locale 的 Listing / 广告 / 内容 / 资产文案，在 HTML 与对应人类源文件中必须同时显示 delivery-locale 释义 / 用途说明。
- 中文 Canonical Prompt 必须存在；英文 / 目标模型 Prompt 可以用于生产，但不能替代中文生产说明。
- 品牌名、SKU、GTIN、类目 ID、URL、HEX、INCI、平台官方字段 key 等技术 / 专有标识可以保留原文或原值，但其**字段名称、用途或角色必须有中文说明**；原始标识只能作为次级信息层。
- 不允许出现“整页英文、字段标题英文、外文资产文案无中文 companion，但因为机器 JSON 里有 locale 就算完成”的情况。

## 5. 人类语言交付 Gate
每次真实 Artifact 导出必须运行 Human Language Delivery Audit：
1. Listing 当前范围内的人类字段标题是否中文在前；未知平台字段若没有语义明确的中文标题，判 `INCOMPLETE`。
2. Listing 目标市场外文内容是否有中文释义 / 用途；缺失则阻断导出。
3. 每个资产 `visible_copy` 中的外文 headline / CTA / caption / hook / script overlay 等是否存在对应中文 companion；缺失则阻断导出。
4. 只要存在英文 / 目标模型 Prompt，就必须存在中文 Canonical Prompt；缺失则阻断导出。
5. 逐资产中文人类设计卡必须存在。

审计结果写入 `HUMAN_LANGUAGE_AUDIT.json`，并进入 `DELIVERY_MANIFEST.json.workspace_contract`。这不是建议项，而是人类交付完成条件。

## 6. 源文件
MD / JSON / TXT / per-asset package 继续保留，用于编辑、机器读取、版本、局部修改和审计。它们不是人类理解项目的前置步骤。机器真源可以保留原始英文 key / ID，但不能反向支配人类界面的语言层级。

## 7. 视觉
HTML 视觉系统应从项目 CMF / HEX 派生主题，而不是固定绿色后台。页面应体现真正 SaaS 信息密度：模块化、层级、状态、局部导航、对象详情、Copy action、PC/移动端响应式、打印/PDF 支持。
