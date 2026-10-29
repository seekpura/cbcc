# Host-Native FULL Delivery Regression Recovery Authority

Host-native / Skills-only 是真实生产路径。v0.6.42 的目标不是再设计一套新壳，而是恢复 v0.6.36 已经可用的交互底座，并在其上保留/增加 v0.6.37+ 的商业、运营、视觉与生产深度。

## 1. FULL 人类交付的稳定交互底座
FULL / 高密度项目不得把全部内容摊成一个纵向长页面。最终 `index.html` 至少保持：
- 当前项目真实存在的一级对象使用可切换 route，一次只显示一个一级工作面；
- 模块内部保留相关 subview / tab / lens；
- 资产库 → 独立资产详情 route；
- 搜索、复制、返回/切换、PC/移动端响应式、打印/PDF 投影；
- 主 HTML 内可直接读到完整工作，不要求用户去文件夹找正文。

页面数量仍然动态：没有内容的对象不出现；对象的名称、顺序、分组、局部结构、视觉主题由当前项目作者化。**动态对象结构不等于动态删除交互。**

禁止再次使用 `project_authored_html` 一类全局后处理器去替换/抹掉成熟 route model。Host 可以在稳定底座内作者化页面与局部 UI，但不能把 FULL 交付变成一页报告、卡片墙或新的固定 Object Switcher 壳。

## 2. Asset Universe 不受平台槽位总数限制
TikTok/Shopee/Amazon/Noon 等 `max_images=9/7/...`、`max_videos=1` 只约束一次同时上线的 **Live / Activation Set**，永远不等于候选资产总数。

FULL 资产策展必须先建立完整 Asset Universe，再决定当前 Live Set。只要有独立购买决策、创意/商业假设或 Surface 价值，就允许并保留：
- 多 Hero：H01/H02/H03…；
- 多 Benefit/Proof；
- Paid Ads 多 Hook / 构图 / 人群 / Offer 版本；
- PDP/A+/Detail/Longform；
- Store/Banner；
- Social/Creator/UGC；
- Short Video/Live；
- Test Pool / Rotation Pool / Campaign / Seasonal。

**绝不因为平台最多 9 图，就只策划或只生产 9 个资产。** 平台容量只决定当前 activation subset。相同 question/surface/family 也不能自动合并显式 H01/H02/H03 或其他 variant/test hypothesis。

## 3. 运营升级是加法，不是替代
v0.6.37+ 的运营执行密度继续有效：运营应直接看到“现在做什么、使用哪个最终对象、为什么、什么不动、完成标准、看什么指标决定下一步”。

但运营执行台只能作为一个**新增可切换工作面 / 入口**，不能注入成整页之前的巨型 section，也不能替代完整 Strategy、Listing、Visual/Video、Assets、Economics、Ads、Review、Evidence。

七大一等能力继续存在：Market Research；Product Strategy（SKU + Pricing + Economics + Offer）；Listing Creative；Product Image；Product Video；Advertising Optimization；Review Analysis。

## 4. 逐资产商业生产深度
每个激活图片/视频资产必须能在 HTML 内进入完整对象。按相关性展示：shopper question、commercial job、creative thesis、Product Presence/Role、Decisive Moment、subject/action/environment/props/evidence、composition/spatial geometry、relative position、scale/depth/occupancy/focal path/negative space、Visible Copy + 中文释义、CMF/material/color、Camera/Lighting/Human、Surface/Output、Model Prompt CN、Model Prompt EN、Production / Assembly Notes、Reference/Truth/Claim 边界、实际输出 QA、最小修复路径、Portfolio Delta。

摘要卡只能做入口。完整 Design Card / Prompt / Production Notes 不能只藏在 `assets/<ID>/`。

## 5. 一体化商业视觉与策展
商业视觉默认作为完整最终成图问题处理。商品、目标市场文字、排版、场景、人物、道具、证据、摄影、灯光、CMF、材质和 finishing 可在同一资产中共同生成；商品/文字是否出现及路线由逐资产购买决策和策展决定。

Agent 是 Portfolio Curator + Creative Director + Per-Asset Art Director。禁止用统一暖白底、左右互换、固定产品位置、同一卡片或固定视频五段式制造伪多样性。

真实商品需要出现时，真实商品图默认作为强 Reference Input 原生生成完整最终画面并保持商品身份；`EXACT_PIXEL_COMPOSITE` 仅用于明确的原像素锁定需求。

## 6. 数字与完成态
不得为填 UI 虚构价格、预算、ROAS、CVR、费率、佣金、成本、销量、认证或排名。缺失经济输入保持 `MISSING_INPUT`。

出现以下任一情况即视为 P0 回归，不得声称完成：
- FULL 主要内容全部纵向摊在一页；
- 36 已有 route/subview/search/copy/asset detail 交互失效；
- 平台 9/7 图被当成 Asset Universe 总量；
- 多 Hero / Ads / PDP / Social / Video / Test / Rotation 被槽位截断；
- Operator 入口替代完整内容；
- 逐资产只剩 role/copy/render route 摘要；
- Host Skill 与 canonical authority 版本/关键规则不一致。