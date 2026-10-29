# Final Output Contract — 人类交付权威

## 1. HTML 是完整正式交付，而且必须正常交互
`index.html` 必须是自包含、可直接使用的离线人类工作区。它不是长篇 Markdown 报告、不是把所有模块按顺序摊在同一页、也不是只有摘要卡/状态徽章的 dashboard。

**FULL / 高密度项目的交互底座不得低于 v0.6.36：**
- 当前项目真实存在的一级业务对象进入可切换路由；没有内容的对象不占页面；页数不固定；
- 正常浏览时一次只显示一个一级工作面，不把 Product Truth / Market / Listing / Strategy / Content / Visual / Assets / Prompt / Risk / Sources 全部纵向摊开；
- 模块内部可以有局部子视图 / Tabs / Lenses，一次聚焦当前主题；
- 资产库负责选择资产，每个资产进入独立详情路由，再查看 Design Card、画面/版式、摄影/CMF、文案、Prompt、Production、QA 等相关视图；
- 保留搜索、复制、对象切换、响应式导航和打印/PDF 投影；
- 用户不需要跳出 HTML 或打开 MD/JSON/TXT 才能理解、复制或执行核心工作。

“项目作者化”只决定**哪些真实对象存在、如何命名/排序/分组、模块内部如何组织、视觉主题和信息密度**；它不允许删除上述交互底座，也不允许把 FULL 项目重新压成一条长单页。稳定工作区骨架不是固定内容模板。

## 2. FULL 深度只能增加，不能因 UI 重构被压缩
FULL 项目的九域决策深度仍是完整度合同，不是九个固定页面。Product Truth、研究、平台×区域×人群×文化、策略、Listing、内容、Visual/Photography、Video、Asset Universe、逐资产生产对象、Economics/Offer、Ads、Review、Evidence/Risk 等按当前项目相关性完整保留。

运营执行台是**增量工作面**：可集中展示“现在做什么、直接使用什么对象、完成标准、看什么指标决定下一步”，但不能替代 Listing 最终文案、策略正文、视觉策展、逐资产详情、经济性或证据对象。

摘要可以做入口，不能做正文替代。若信息对执行有价值，必须在 HTML 中可直接查看/展开/复制/进入完整对象。

## 3. Asset Universe 与平台上线槽位严格分离
平台 `max_images=9`、`max_images=7`、`max_videos=1` 等只约束**一次同时上线的 Live / Activation Set**，绝不约束候选 Asset Universe 总量。

资产总量由购买决策、Surface、创意假设、测试与运营需求决定。允许并应在有独立价值时保留：
- 多 Hero：H01 / H02 / H03…；
- 同一卖点的不同视觉/证据假设：B01 / B02 / B03…；
- Paid Ads 多 Hook / 构图 / 人群 / Offer 版本；
- PDP / A+ / Detail / Longform；
- Store / Banner；
- Social / Creator / UGC；
- Short Video / Live；
- Test Pool / Rotation Pool / Campaign / Seasonal。

平台槽位只决定哪些候选进入当前 Live Set。**“最多 9 图”绝不能被解释为“只策划/只生产 9 个资产”。** 20、30、50 个候选都可以，只要每个有独立商业/创意假设与增量信息。

人类 HTML 应区分 `Asset Universe / Live Candidates / Test Pool / Rotation Pool / Paid Media / PDP-A+ Content / Archive` 等状态，让运营能看懂“现在上线什么”和“还有什么可测试/轮换”。

## 4. 逐资产必须是完整商业生产对象
每个激活资产必须能进入完整对象。按相关性直接可见：购买问题、Strategic Job、Creative Thesis、Product Presence / Role、Decisive Moment、subject/action/environment/props/evidence、composition/spatial geometry、scale/depth/occupancy/focal path/negative space、Visible Copy 与中文释义、CMF/material/color、相关 Camera/Lighting/Human 参数、Surface/Output、Model Prompt CN、Model Prompt EN、Production / Assembly Notes、Reference/Truth/Claim 边界、实际输出 QA、最小修复路径、与相邻资产的 Portfolio Delta。

Graphic / Illustration / Native Text / 3D 不强塞无关摄影字段；Photography / Video 必须保留真正改变结果的执行参数。

真实商品需要出现时，真实商品图默认作为强 Reference Input 进入完整最终成图，保留商品身份；`EXACT_PIXEL_COMPOSITE` 仅在明确要求源图原像素层不可改变时使用。

## 5. 全局中文释义合同
人类交付默认中文。**凡运营人员在正式人类交付中需要读懂的外文内容，都必须保留原文，并在同一对象提供中文释义 / 用途。** 中文释义是完成对象的一部分，不是可选元数据。

覆盖范围包括但不限于：
- Listing / 上架：类目 / 分类 / 类目路径、标题、卖点、描述、属性、变体名称和值、包装内含物、使用说明、搜索词 / 后台关键词、FAQ、平台字段值；
- Visual / Assets：目标市场 Visible Copy、标题、证据文案、CTA、Caption；
- Video / Creator：Hook、首帧文字、屏显、字幕、对话、VO / Script、封面文字、CTA；
- Ads：Hook、Headline、Primary Text / Body、Caption、Creator Script、Offer Copy、CTA、Landing Message；
- Review / CS / Return：在工作区展示的外文评论、客服原话、投诉、退货原因、消费者原话；
- Research / Strategy：在主工作区直接展示的消费者原话、竞品文案、品类 / Segment 标签、Positioning / Value Proposition 或证据摘录。

Listing 人类字段标题必须中文在前；`description / category / attributes` 等平台原始 key 只能作为次级技术标识。搜索词的中文 companion 可以解释**搜索意图 / 用途**，无需机械逐词直译。外文评论/竞品原文必须保留，中文负责解释其语义与决策信号。

SKU、GTIN/EAN/UPC、URL/URI、HEX、INCI、型号 / 部件号、HS Code、品牌专名等技术标识或官方专名可保留原值，不要求硬翻译；但字段名称、作用和操作说明仍应中文优先。

`Model Prompt EN` 可以保留英文执行语言，但必须与 `Model Prompt CN` 成对，并明确它属于模型执行输入而不是唯一的人类说明。

**`待补中文释义`、空白中文 companion、外文-only 人类内容都不是 FULL 完成态。** Agent 必须在最终交付前补齐；Runtime 负责审计并 BLOCK 缺失项，不能为了过 Gate 自动编造机器翻译。

## 6. 商业能力连续性
七大能力始终是一等能力：Market Research；Product Strategy（SKU + Pricing + Economics + Offer）；Listing Creative；Product Image；Product Video；Advertising Optimization；Review Analysis。按项目相关性激活，不是固定七步流水线，也不能因视觉/HTML升级被挤掉。

Pricing/Economics 只使用显式输入。缺少成本、平台费、履约、佣金、税、退款预留、CVR 等保持 `MISSING_INPUT`；不得为填 UI 虚构价格、预算、ROAS、CVR、费率、销量、认证或排名。

## 7. 视觉与交互质量
主题、CMF、密度和局部组件可由当前商品/品牌/市场派生；不要所有项目同一绿色、同一卡片风格、同一布局。但交互创新不能牺牲可用性：FULL 项目不能因为“作者化”失去路由、对象详情、搜索、复制或正常阅读层级。

桌面/移动端按真实使用目标响应；固定几何目标保持真实几何。打印/PDF 是工作区投影，不反过来主导网页结构。

## 8. 交付前强制回归检查
交付前至少确认：
- 正常浏览时是否一次聚焦一个一级工作面，而不是全部内容一页纵向摊开；
- Listing/策略/视觉/资产/运营等真实对象是否都能直接进入；
- 资产库是否能进入独立资产详情与完整 Design Card / Prompt / Production；
- 搜索、复制、子视图、响应式交互是否仍可用；
- Asset Universe 是否独立于平台 Live Slot 容量，多 Hero / Paid / PDP / Social / Video 变体是否被错误截断；
- 运营执行是否只是增量入口，而没有替代完整内容；
- 上架类目、描述、属性、搜索词、FAQ 等所有可见外文是否同对象有中文释义；
- 资产 Visible Copy、视频、广告、评论原话、研究摘录中的可见外文是否同对象有中文释义 / 用途；
- 是否仍出现 `待补中文释义` 却被标为 READY / 完成；
- 是否出现虚构数字或把 MISSING_INPUT 当 0；
- 是否要求用户去文件夹找真正正文。

任一 P0 回归出现，都不能把交付标记为完成。