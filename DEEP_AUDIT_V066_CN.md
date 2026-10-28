# CBCC v0.6.6 全链路深度审计

## 结论

v0.6.6 的主升级不是“再做一个 HTML 模板”，而是把人类交付、语言权威、资产工作流和 Render Prompt 生产链重新对齐。默认人类交付语言为中文；目标市场可见文案按目标语言保留原文，并在同一工作区提供中文释义/用途说明。HTML 由长报告/锚点目录改为对象化 SaaS Workspace：主工作区 → 任务子页 → 单资产工作区。

## P0 / P1 问题与处理

### 1. HTML 仍然是长报告 / 流水席
- 原问题：左侧导航只是锚点，Overview → Product Truth → Market → Listing → Strategy → Visual → Assets 仍在同一连续页面阅读。
- v0.6.6：改为路由式单页工作区。主模块一次只显示一个页面；策略/产品/市场/视觉模块继续按 H3 任务拆成子页；资产先选资产卡，再进入该资产的策划 / 画面 / 摄影 / 文案 / Prompt / QA 子页。
- 所有内容仍完整内嵌一个离线 HTML；不要求打开 MD。

### 2. 默认人类交付出现大量英文
- 原问题：目标市场语言、Runtime 英文键、英文术语和人类交付语言混在一起。
- v0.6.6：建立三层语言权威：
  1. Human Delivery：默认 zh-CN，除非用户明确要求其他语言；
  2. Target-visible Copy：按市场/平台策划使用 ms-MY / en-MY / ar / 其他语言；
  3. Renderer Prompt：可按模型需要使用英文，但必须同时交付中文生产 Prompt。
- 内部状态、规则句、机器标签在主工作区使用中文显示；原始机器键仅在归档保留。
- 目标语言文案不被“为了中文”自动篡改；同字段提供中文释义/用途。

### 3. 中文 Prompt 是“中文标题 + 英文正文”的假中文
- 原问题：`05_prompt_CN.txt` 中 Creative Thesis、Image Language、摄影/CMF说明仍夹大量 CBCC 自己生成的英文句子。
- v0.6.6：CN/EN Prompt 真正分开编译。中文 Prompt 使用中文生产语言；英文 Prompt 保留为生成模型执行载体。
- 品牌名、目标市场原文、ISO / CCT / CMF / mm 等必要技术符号可保留。

### 4. 视频 Prompt 参数重复 dump
- 原问题：每个 Shot 重复整套 Camera / Lighting / CMF / Inclusive Photography，单条中文 Prompt 可接近 2 万字，英文 3–4 万字。
- v0.6.6：Master 摄影/灯光/CMF/材质/包容性合同只写一次；Shot 只写任务、画面动作和必要局部变化。
- fresh build：3 条视频中文 Prompt 约 2.3–2.7k 字符；英文约 5.3–6.1k 字符。
- 完整 Machine Contract 仍在 JSON 中，未牺牲追踪性。

### 5. 摄影 / CMF / 构图“策划了但没真正进入 Prompt”
- v0.6.5 已建立 Parameter Trace；v0.6.6 保持并继续用于图片/视频。
- Master → Asset / Video → Shot 深合并，不允许局部 override 把未覆盖的焦段/ISO/快门/CCT/光比等参数整块抹掉。
- 图片 Prompt fresh build 均包含焦段、ISO、快门、CCT、光比等关键摄影参数，并带 parameter_trace。

### 6. 摄影参数输入不够符合真实摄影工作方式
- 原问题：`70–85mm` 等人类常用范围格式会触发数值解析错误。
- v0.6.6：支持单值、数字类型、`70–85mm`、`85mm equivalent` 等格式；策略判断使用规范化数值，Prompt 保留原始人类可读文本。

### 7. 包容性摄影适用条件过窄
- 原问题：只看用户是否显式提供 casting/human photography，某些最终 Human Use / Relevance 资产可能被判 NOT_APPLICABLE。
- 修复：由最终资产任务判断。只要出现人物、手部或身体关系，深肤色测光、发质、体型/年龄/残障和 AI bias QA 进入 P0 执行合同。

### 8. Intersectionality / race_ethnicity 输入健壮性
- 原问题：list / scalar / dict 的真实用户输入形式不一致时可能 `.get()` 崩溃。
- v0.6.6：统一正规化 list/scalar/dict 输入。

### 9. 平台规划品类被误当成精确上架类目
- 原问题：`target.category = beauty` 可能被 Human Delivery 显示成 READY。
- v0.6.6：规划品类与当前 Seller Center 精确类目分离。没有当前类目树中的 name / ID / path 证据就显示 `待查证`，不得猜。

### 10. 资产详情仍从机器 YAML/JSON 开始
- 原问题：进入资产后第一屏是 manifest/contract，用户仍承担工程拼图成本。
- v0.6.6：每个资产新增中文 Human Design Card，第一屏回答“为什么存在 / 解决什么购买问题 / 画面怎么做 / 摄影怎么拍 / 文案是什么 / 成功标准 / 下一资产如何承接”。机器合同移到最后的「合同 / QA / 来源」。

### 11. 机器文件路径 / 英文工程标签泄漏到主工作区
- v0.6.6：主工作页不再显示 `来源：strategy/xxx.md`；路径、hash、内部 route、机器键统一留在来源/归档。
- `Provider / Route`、`Surface Production Contract`、`Canonical Prompt` 等主显示标签改为中文主层。

### 12. 策略大章节仍然太长
- v0.6.6：H2 只是业务域；内部 H3 自动拆成独立任务子页。例如营销策略中的定位、价值主张、Listing/Search、框架、内容矩阵、RACE；视觉中的摄影 WHY、镜头表、资产视觉签名、单资产摄影因果、动态资产策展分别切换。

### 13. RACE / Claim / 固定模板回归扫描
- RACE Authority 仍为 `Research → Action → Communication → Evaluation`。
- `delivery_contract.py` 明确阻断 Reach / Act / Convert / Engage 作为本项目 RACE 阶段。
- `APPROVED` 不再等于证据；C 级不得硬批准。
- 未发现固定九图/固定 9 assets Runtime 配额；相关文本只存在于“不得固定九图”的反约束中。
- Render Prompt 未发现 `asset for ...` / Asset ID / RACE / KPI 等旧污染模式。

## 人类交付结构

### 主工作区
- 工作台
- 产品事实
- 市场 / 人群
- 上架中心
- 策略中心
- 视觉 / 摄影
- 资产中心
- 提示词工作台
- 风险 / 合规
- 来源 / 真源
- 归档

### 资产工作区
- 资产概览
- 策划与决策
- 画面与版式
- 摄影 / CMF
- 文案
- 生成与生产
- 合同 / QA / 来源

### 语言规则
- 中文 = 默认项目使用者语言。
- 非中文市场文案 = 原文 + 中文释义/用途。
- 中文 Prompt = 人类生产/审核权威。
- 英文/模型 Prompt = 执行载体，不是唯一交付。
- 搜索词不要求机械逐词翻译，应显示中文搜索意图/用途。

## 仍然存在的边界 / 债务

### P0 外部数据边界
- 当前平台精确类目树、规则、算法、费率、政策需要实时官方 Web/API/平台数据；离线 Runtime 不得冒充最新事实。

### 架构边界
- 当前 ChatGPT 插件仍是 Skills-only；本地七大 Python Runtime 真执行，但未通过 `mcp.json` / MCP Server 暴露为 ChatGPT 可直接调用的七大工具。

### P1 可维护性
- `strategy_depth.py / strategy_authority.py` 仍包含历史 overlay / wrapper 层。当前 active path 已统一，但后续应做 Authority Consolidation，前提是逐层保留现有成熟能力，不能为了“代码干净”砍功能。

### 本地化边界
- 中文释义用于人类理解和审核，不等于目标市场 native sign-off。正式发布仍需目标语言专业复核、回译、平台/文化/合规审查。

## 最终判定

v0.6.6 可以作为新的正式基线用于真实 SKU 测试。后续真实输出出现问题时，按最小责任层修复，不再重新发起泛化“验证工程”。

## 封包前补充发现

### 14. v0.6.3 旧 Theme Authority 会把系统拉回长报告
- `references/REPORT_THEME_CONTRACT.md` 仍写 `Commerce Editorial Report / premium long-form editorial reading`，与 v0.6.6 对象化 SaaS Workspace 冲突。
- 已升级为 v0.6.6 Human Workspace Theme Contract，并在 `SKILL.md` 明确 v0.6.3 的长报告表现形式已被废止，仅保留“HTML 必须包含完整内容”的原则。

### 15. 视频 Prompt 去重过程中可能漏掉局部摄影参数
- 定向回归发现，压缩器最初只取 `ratio` / `color` 等固定键，可能漏掉资产级 `exposure_ratio_plan=2:1`、`primary=#163C31`，以及字符串型 `polarization_plan=cross-polarize...`。
- 已改为保留常见主色/背景色、`exposure_ratio_plan` / `prelight_plan`，并兼容 dict / list / string 型材质摄影合同。
- 最终定向回归：`85mm / 5000K / 2:1 / cross-polarize / +0.3 EV / #163C31` 均能进入视频执行 Prompt，同时不重新膨胀到旧的重复体量。
