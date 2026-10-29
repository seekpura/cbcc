# Commercial Delivery Stability Authority — v0.6.45

## Highest-precedence delivery stability boundary
本节只固定“商业交付如何稳定呈现”，不改变 Agent 的策略、策展、创意作者权。

### 1. 真源媒体必须可携带、可验证
- `source_product_assets.json` 只记录路径而不把真实文件带入交付，不算完成。
- Export 在 HTML 编译前物化真实商品/包装/证据源图到交付包 `sources/`；HTML 应使用内嵌 data URI 或同包可解析资源，单独打开 `index.html` 时不能出现静默断图。
- 声明了真源但文件不可解析时，正式交付显示“真源文件缺失/未绑定”的显式状态并写审计，不得输出空白图片区假装已加载。
- 真源图的存在不等于每个创意资产都必须出现商品；Product Presence 仍由逐资产策展决定。

### 2. 平台、市场、主语言禁止历史污染和静默默认
- 当前任务没有明确平台时，`platform=UNSPECIFIED`；没有明确市场时，`market=UNSPECIFIED`。
- 禁止从历史项目、示例数据、旧 KIYUU、`platform_compile.json`、缓存输出或平台模板自动继承 TikTok、Malaysia、Shopee 或任何其他平台/市场。
- 当前请求/用户明确输入/明确标记的项目真源优先。Agent 可以提出平台建议，但“推荐”与“已选择”必须是不同状态；推荐不能直接变成正式 Listing/平台规则的当前真源。
- 未指定平台时，不加载平台专属发布规则，不生成“TikTok Shop Operator Workspace”等确定性平台标题。

### 3. 正常人类交付语言矩阵
除中国平台/中国大陆市场外，正式运营交付默认同时提供：
1. **English baseline（英文基线）**；
2. **Platform primary language（平台/市场主语言）**；
3. **Chinese interpretation（中文释义/用途）**。

规则：
- 平台主语言就是英语时去重，交付为“英文 + 中文释义”。
- 中国平台/中国大陆市场为 `CN_ONLY`，只要求中文，不为了形式再生成英文。
- 平台/市场未指定时，保留“英文基线 + 中文释义”，平台主语言明确标 `MISSING_INPUT / 待指定`；禁止猜成马来语、泰语、阿语等。
- Listing、Seller Center 字段、资产 Visible Copy、视频 Hook/屏显/字幕/VO/CTA、广告文案、Creator Script 以及其他运营可读市场文案遵循同一矩阵；技术标识符仍按既有豁免规则处理。
- Runtime 只审计与编排，不通过机器翻译伪造缺失的英文/平台主语言成稿；缺少应由 Agent 作者化的语言层时标出缺失，并在需要发布就绪的对象上阻断 READY。

### 4. CBCC Commercial Workspace Shell v1 — 冻结商业级交互底座
HTML 工作台壳版本固定为 `cbcc-commercial-v1`。CBCC 产品版本升级不等于换壳。

稳定交互底座：
- 顶部 Command Bar 固定展示当前项目关键状态：平台、市场、语言方案；未指定时明确“待指定”，不猜。
- 左/主导航继续使用成熟 routed workspace；一次只显示一个一级工作面。
- 一级对象只在真实存在时出现；模块内部允许 subview/lens/tab；Asset Portfolio 进入独立 `asset/<id>` 详情。
- 全局搜索、复制、前进/返回/hash route、响应式移动导航、打印/PDF 投影继续保留。
- `运营执行` 是可切换工作面，只做执行入口；Strategy、Listing、Assets、Video、Ads、Review、Economics、Evidence 等完整对象继续独立存在。
- Audit/Trace/Runtime/Source Inspector 属于二级检查层，不抢占商业对象主界面。
- 页面视觉使用稳定设计 token、组件与 DOM hook；后续版本可以增加对象、修复组件和提高密度，但不得因为普通版本升级重新发明 Sidebar、Dashboard、Card Wall、Overview/Theater/Compare 等全局壳。
- 只有用户明确批准新的 Shell major version，才允许从 `cbcc-commercial-v1` 升级为 v2。

### 5. 运营密度的稳定定义
商业级“密度”不是把所有信息堆在首页，也不是满屏状态徽章。每个一级工作面回答当前角色真正需要的决策：
- 当前结论 / 决策；
- 依据与真源；
- 可直接复制/发布/生产的最终对象；
- 风险与缺失输入；
- 下一执行动作与判断标准。

详情按对象逐层展开；机器合同与审计放 Inspector。任何版本不得用更短的新 Dashboard 替代完整业务深度，也不得把所有对象重新纵向摊成一页。

## Release acceptance
v0.6.45+ 交付若出现以下任一情况，不得视为稳定：
- 真源 JSON 存在但实际源图没有进入 package/HTML，导致空白或断图；
- 用户未指定平台，却显示确定的 TikTok/Malaysia 或其他历史平台/市场；
- 非中国且非英语主语言项目只有“平台主语言 + 中文”而缺英文基线；
- 中国平台被强制生成多语言冗余版本；
- 普通 CBCC patch/minor 更新更换 `cbcc-commercial-v1` 的全局交互壳；
- 运营执行页再次取代完整 Strategy/Listing/Assets 等对象。
