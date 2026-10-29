# v0.6.46 — Commercial Continuity & Decision Lineage Recovery

## 这版修的不是“提示词长度”，而是整条商业生产链

### 1. Authority 深度恢复与强制加载
Host 不再靠 defaultPrompt 兜底。新增 `Canonical Authority Loading Map`：FULL 项目强制消费成熟 v0.6.6 商业深度、Dynamic Asset Curation、Creative Direction / Surface Prompt Compiler、Commercial Visual/Video、Operator Density 与 Delivery Stability 等 specialist authority。能力保留以“真实消费者”为准，不以文件存在或字节数为准。

### 2. 七工具真实 payload 继续下传
新增 `Commerce Decision Context`，保留 Market / Pricing / Economics / Audience / Culture / Positioning / RACE / Listing / Ads / Review / Experiment / Measurement 的真实决策值与来源，不再用 status/count 替代。

### 3. Analysis → Curation → Asset 连续性
新增 Creative Curation commercial lineage：Market-fit、Listing objection、Review/Feedback、目标市场/文化与购买任务的 decision origin/source 进入 Creative Opportunity / Council，并继续进入逐资产 Art Direction。风格本身不能作为唯一策展依据。

### 4. Subject Presence System
主体不再等于人物。逐资产支持 `PERSON / ANIMAL / PLANT / PRODUCT_OR_OBJECT / ENVIRONMENT / MULTI_SUBJECT / NONE`；宠物用品可以动物主导，植物/园艺可以植物主导，证据/商品/环境资产可以无人物。Legacy `human_context` 仅做显式兼容迁移，永远不能成为全局默认。

### 5. Commercial Asset Universe / Portfolio Taxonomy
平台 7/9 图、1 视频等只约束 simultaneous Activation Set，不限制总资产宇宙。新增商业资产族与部署池：Hero、Benefit、Proof、Scenario、How-to、Trust、PDP、A+、Ads、Social/Seeding、Creator/UGC、Video、Banner，以及 Live/Test/Rotation/Paid/PDP/A+/Social/Archive 等状态。显式 A/B/Variant 不得因 question/surface/family 相同被合并。

### 6. Prompt 与摄影参数同时闭环
商业决策上下文与 Subject System 作为新增 Prompt section 叠加在既有 Production Parameter Closure 之后；不会覆盖焦段、工作距离、机位、对焦/景深、Key/Fill/Negative/Rim、CCT/WB、光比、反射/偏振、Prelight、CMF、色彩管理、finishing 等具体参数。Prompt readiness 继续做具体值消费审计。

### 7. Per-Asset Decision Lineage + Human Design Card
每个资产按购买问题、阻力、Decision Intent、Surface、RACE 和商业任务绑定相关决策；Price/Offer、Ads、Review 等只进入相关资产。Design Card 直接显示上游商业依据、Subject System、来源血缘、摄影/CMF 与四类生产对象。

### 8. 商业 HTML 一等可见
在 `cbcc-commercial-v1` 内新增动态 routed `商业洞察` 工作面，显示当前项目真实存在的：市场/区域/人群、Pricing/Economics/Offer、Search/Listing/Objection、RACE/Journey、Ads、Reviews、Measurement、Decision Lineage/Evidence，以及 Asset Universe 总量、Activation Capacity、资产族和部署/测试池。Machine Archive 继续保留但不替代商业主交付。

### 9. Continuity Audit / Wrapper Safety
新增项目级和资产级 continuity audit：有上游决策但没有进入 Curation / Design Card / Prompt / Human Delivery 时为 INCOMPLETE。商业 continuity bootstrap 改为幂等安装，避免多 import 路径重复 wrapper 造成二次覆盖。

### 兼容性
继续保留 v0.6.36 routed workspace、v0.6.37+ 商业/operator 深度、v0.6.42 Asset Universe activation-only、v0.6.43 中文释义、v0.6.44 default-prompt authority boundary、v0.6.45 真源媒体/显式平台/语言矩阵/`cbcc-commercial-v1`。升级只做加法。
