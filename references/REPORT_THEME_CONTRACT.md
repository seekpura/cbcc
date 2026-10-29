# CBCC Human Workspace Theme Contract v0.6.42

## 定义
`index.html` 是面向项目运营、Listing、创意、投放与生产使用者的完整离线 SaaS Workspace。它不是长篇 Editorial Report、Markdown 聚合器、文件浏览器，也不是把所有内容纵向铺在一页的“单页叙事”。

## 稳定交互底座 + 动态内容结构
FULL / 高密度项目保留 v0.6.36 的可用交互底座：
- 一级工作对象用路由切换，正常状态一次只显示一个工作面；
- 一级对象只从当前项目真实存在的内容生成，不固定页数，不制造空页；
- 模块内部用局部导航 / Tabs / Lenses 切换当前主题；
- 资产库与资产详情分离；每个资产有独立详情路由；
- 搜索、Copy action、对象返回、PC/移动端响应式、打印/PDF 投影持续可用。

“动态/作者化”指的是对象的存在、命名、顺序、分组、模块内部结构、视觉主题、信息密度和具体交互由项目决定；**它不等于删除路由、把所有内容放一页、把资产详情缩成摘要，也不等于每次发明一个全新的全局壳。**

## 主工作对象
系统不强制固定菜单数量，但 FULL 商品项目常见的真实对象包括 Product Truth、Market/Audience/Culture、Listing、Strategy、Content、Visual/Photography、Assets、Prompts、Risk/Evidence，以及在当前项目有真实数据时出现的 `运营执行`。不存在的对象不显示；复杂对象可按需要拆成多个局部视图。

运营执行是新增工作面，不是首页巨型注入，也不是完整项目替代品。它聚合发布动作、生产动作、Paid Test、Review Revision、Economics Control 等运营任务，同时保留跳回完整 Listing / Strategy / Visual / Asset 对象的能力。

## 资产 Portfolio 与详情
资产中心首先展示完整 Asset Universe / Portfolio，而不是只展示平台当前可上线槽位。

平台最多 9 图 / 7 图 / 1 视频等只限制 Live Activation Set。候选资产可以包含多 Hero、多卖点、多广告、多 PDP/A+、Detail、Store/Banner、Social/Creator/UGC、Video、Test Pool、Rotation Pool。不得把平台容量当成资产总量目标或上限。

资产库只用于浏览/筛选/比较资产；进入单个资产后，相关的 Human Design Card、视觉执行、摄影/CMF、Visible Copy、Model Prompt CN/EN、Production/Assembly Notes、QA/来源在同一资产工作区按视图切换。Human Design Card / 商业任务应是默认高优先级人类视图，原始 YAML/JSON 只属于追溯层。

## 中文与运营可读
默认交付语言 `zh-CN`。目标市场消费者可见文案保留原文，并在同一对象显示中文释义 / 用途。Listing 字段中文在前；平台原始 key、Asset ID、Provider、hash 等技术标识是次级层。

运营主界面优先回答：现在做什么、使用哪个最终对象、为什么、什么不动、做到什么算完成、看什么数据决定下一步。Runtime/Consumer/Trace 是 Inspector，不是主要内容。

## 视觉系统
视觉主题优先从当前项目 CMF / HEX / 品牌 / 市场派生，不能所有项目强制同一绿色后台或同一组件语言。但“每个项目视觉不同”不能以牺牲交互稳定性为代价。

PC 保持高密度工作区；移动端把主导航/子导航适配成可用的横向或折叠交互，内容单列。核心阅读离线可用，不依赖外部 CDN。

## 失败判定
以下任一情况属于 P0 交付回归：
- FULL 项目主要内容全部出现在一个纵向长页面；
- 删除/绕过已有路由，导致 v0.6.36 已有的页面切换、子视图、搜索、复制、资产详情失效；
- 平台 `max_images=9` 被解释为 Asset Universe 只能 9 个；
- 多 Hero / Paid Ads / PDP-A+ / Social / Video / Test / Rotation 变体被平台槽位截断；
- 运营执行台替代而不是补充 Listing / Strategy / Visual / Assets；
- 资产详情只给 role/status/render route，完整 Design Card/Prompt/Production 藏在文件夹；
- 为填 UI 编造价格、预算、ROAS、CVR、费率或其他数字；
- 通过换壳/删交互声称“升级”。

出现上述情况必须回归责任层修复，不能继续在错误壳上叠组件。