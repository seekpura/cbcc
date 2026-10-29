# v0.6.46 — Commercial Continuity & Decision Lineage Recovery

## 这版修的不是“提示词长度”，而是整条商业生产链

### 1. 恢复完整 Canonical
正式 builder 重新以 repo root `SKILL.md` 为 Canonical 真源，并让 Host Skill / `resources/SKILL.md` byte-identical。Guard 禁止再次从完整商业权威缩成 compact wrapper。

### 2. 七工具真实 payload 继续下传
新增 `Commerce Decision Context`，保留 Market / Pricing / Economics / Audience / Culture / Positioning / RACE / Listing / Ads / Review / Experiment / Measurement 的真实决策值与来源，不再用 status/count 替代。

### 3. Per-Asset Decision Lineage
每个资产按购买问题、阻力、Decision Intent、Surface、RACE 和商业任务绑定相关决策；Price/Offer、Ads、Review 等只进入相关资产。所有绑定保留 source artifact/path。

### 4. Prompt 与摄影参数同时闭环
商业决策上下文作为新增 Prompt section 叠加在既有 Production Parameter Closure 之后；不会覆盖焦段、工作距离、机位、对焦/景深、Key/Fill/Negative/Rim、CCT/WB、光比、反射/偏振、Prelight、CMF、色彩管理、finishing 等具体参数。

### 5. 商业 HTML 一等可见
在 `cbcc-commercial-v1` 内新增动态 routed `商业洞察` 工作面，显示当前项目真实存在的：市场/区域/人群、Pricing/Economics/Offer、Search/Listing/Objection、RACE/Journey、Ads、Reviews、Experiment/Measurement、Decision Lineage/Evidence。Machine Archive 继续保留但不再替代商业主交付。

### 6. Continuity Audit
新增项目级和资产级 continuity audit：有上游决策但没有进入 Design Card / Prompt / Human Delivery 时，状态为 INCOMPLETE，而不是因为文件存在就算集成完成。

### 兼容性
继续保留 v0.6.36 routed workspace、v0.6.37+ 商业/operator 深度、v0.6.42 Asset Universe activation-only、v0.6.43 中文释义、v0.6.44 default-prompt authority boundary、v0.6.45 真源媒体/显式平台/语言矩阵/`cbcc-commercial-v1`。
