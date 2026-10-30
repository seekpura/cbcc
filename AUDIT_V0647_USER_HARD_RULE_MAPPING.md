# v0.6.47 用户硬性规则 → 实现/验收映射

| 用户要求 | v0.6.47 实现/验收 |
|---|---|
| 产品事实：真实卖点/可感知利益/情绪价值/不可宣称项，A/B/C证据，C不得硬宣称 | `strategy_depth_projection_v3.py` 物化 value ladder；`full_delivery_depth_v3.py` 检查字段与 C 级 hard-claim；`claim_grade_safety_v0647.py` 加固 |
| 为什么平台/区域/人群/族裔文化 | 20维 `dimension_status` + Decision Log/Framework Relationship/WHY 深度检查 |
| 合规/宣称P0，不编造 | Product Truth/Claim authority保留；当地法规/平台规则未知为 `TO_VERIFY`；P0 self-check |
| 族裔×性别×年龄×收入×地域交叉性 | `intersectionality_table` 必填 dimensions/implication/evidence_or_assumption/stereotype_guard/execution |
| 人物出现时包容性摄影P0 | 条件式检查 skin-tone exposure、deep-skin shadow、bounce/diffusion、hair、body、disability、age、AI bias；无人物不强塞 |
| 平台尺寸/时长/封面/字幕/音乐版权/流量/CTA/落地/UTM归因 | `06_platform_content_matrix` V3 必检字段 |
| 语言回译/节日/支付物流/宗教禁忌/法规 | Localization Operating Table 六维显式状态、动作、WHY、依据/假设 |
| 预算周期不足时P0/P1/P2取舍 | `resource_tradeoff_plan`: constraints/keep/cut/why；P0/P1/P2保留 |
| 每条策略依据+取舍+可执行 | Decision Log: what/why/evidence/tradeoff/execution/measurement；重要策略 authority要求WHAT→WHY→EVIDENCE→TRADEOFF→... |
| 输出前自检 | fabrication/why/culture/compliance/metric/assumption/language/asset-universe/prompt-depth self-check |
| RACE=Research→Action→Communication→Evaluation | V3固定四阶段、逐行 objective/action/output/platform/culture/KPI/WHY |
| STP/JTBD、AIDA/FABE、4P/Funnel角色关系 | `framework_relationships` 要求 role + why，不机械套表 |
| 族裔文化适配检查表 | Section 08 V3 深度检查，含 inclusive representation、stereotype/taboo、result、modification、WHY、evidence/assumption |
| 信息审计→最多10问→假设→继续 | 保留 v0.6.6 contract；V3要求 assumptions + decision log |
| 视觉执行：风格、构图、HEX、灯光、焦段、场景、道具、主体、尺寸、镜头表 | V3 Visual Execution dimension groups + mature Production Parameter Closure |
| 假设与决策日志 | Section 01 必检 |
| 九项输出结构 | Host/Runtime Canonical FULL authority + V3 strategy sections；不是标题存在即PASS |
| 商业交付文件不能丢 | `CORE_HOST_FULL_FILES` + `FULL_DELIVERY_OBJECT_MANIFEST.json` + Host package audit |
| 中文释义 | Listing/Assets/Video等外文 companion audit；EN Prompt purity audit |
| 9图不能裁资产宇宙 | `ASSET_UNIVERSE.json` + all non-archive candidate materialization audit |
