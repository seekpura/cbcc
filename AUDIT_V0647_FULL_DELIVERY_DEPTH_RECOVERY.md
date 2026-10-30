# v0.6.47 FULL 商业交付深度恢复审计

## 样本
本轮以用户提供的两个真实交付 ZIP 做回归基准：
- `KIYUU_K01_TikTok_MY_CBCC.zip`：此前较完整的 TikTok MY 交付样本；
- `KIYUU_K01_CBCC_测试.zip`：v0.6.46 后测试包，暴露当前回归。

## 结论
本次事故不是“规则文件被删除”，而是 **ChatGPT Skills-only Host-native 交付旁路了正式 Runtime Export + Host 采用存在性/布尔审计替代内容深度审计**。因此 Canonical/Runtime 中仍有能力，最终 ZIP 却没有稳定物化对应商业对象。

## 已确认回归证据

### 1. 交付对象丢失
测试包只有 9 个 `LST-01…09` asset packages，没有独立 machine authority / supporting analysis 层。缺失的正式 FULL 对象包括：
- `PLATFORM_SCOPE.json`
- `DELIVERY_LANGUAGE_MATRIX_AUDIT.json`
- `HUMAN_LANGUAGE_AUDIT.json`
- `SOURCE_TRUTH_MEDIA_AUDIT.json`
- `strategy/MASTER_STRATEGY_CN.md`
- `strategy/strategy_authority.json`
- `strategy/STRATEGY_DECISION_INDEX.json`
- `strategy/COMMERCE_DECISION_CONTEXT.json`
- `strategy/COMMERCIAL_CONTINUITY_AUDIT.json`
- `supporting_analysis/product_truth.json`
- `supporting_analysis/target_context.json`
- `supporting_analysis/culture_context.json`
- `supporting_analysis/asset_architecture.json`
- `supporting_analysis/seven_agent_synthesis.json`
- 独立 `ASSET_UNIVERSE.json`
- `FULL_DELIVERY_OBJECT_MANIFEST.json`

### 2. Asset Universe 被最终物化层重新压成 Gallery 9 图
此前样本存在：
- LST-01…08 Live；
- `AD-01` Paid Media；
- `TST-01/02/03` Test/Rotation；
- `VID-01/02` Video。

当前测试包最终只物化 LST-01…09。说明“平台容量只约束 Activation Set”的代码规则没有贯穿到 Host-native 最终 ZIP。

### 3. Listing 中文释义丢失
当前 `01_LISTING_UPLOAD_READY.md` 含 English + BM 的 Title / Bullets / Description / Search Terms，但没有同对象中文释义/用途，违反 v0.6.43+ 全局中文释义与 v0.6.45 语言矩阵。

### 4. Model Prompt EN 被中文执行语言污染
当前 9/9 `06_prompt_EN.txt` 存在中文执行说明，例如 English prompt 中出现中文 Consumer Decision / Composition / Photography 文本。说明 Host 直接写文件时没有执行 Model Prompt EN language-purity contract。

### 5. 九域“文件回来了，内容仍然薄”
当前策略 01–09 文件存在，但市场/区域/人群/文化深度主要停留在少量 audience bullets + 泛化文化说明。缺少或不足：
- 平台 / 国家 / 次区域 / 人群 / 年龄 / 性别 / 收入消费力逐维度状态；
- race/ethnicity × gender × age × income × geography 的可执行交叉矩阵；
- religion / holiday / payment / logistics / local regulation 的运营表；
- language native review / back-translation；
- 当前平台行为、Search/Demand、Competition、Price Band 的来源/状态；
- 明确 Resource Tradeoff Plan（约束/保留/砍掉/WHY）；
- 人物出现时的深肤色曝光、bounce/diffusion、发质、体型、残障、年龄、AI bias P0 执行表。

### 6. 逐资产同质化
测试包 9 个资产中：
- Photography Contract 两两平均文本相似度约 96%；
- 8/9 `09_production_notes.md` 完全相同；
- 9/9 `measurement_hypothesis` 为同一句通用模板；
- CN Prompt 两两平均相似度约 75%；
- EN Prompt 两两平均相似度约 80%。

这说明逐资产 Art Direction / Scene / Subject / Evidence / Production / Measurement 在 Host-native 路径又被压成共享母版。

## 根因
1. 私有 ChatGPT Plugin 正常调用为 Skills-only 路径；Python Runtime 不是自动执行条件。
2. v0.6.43–0.6.46 的多个修复主要落在 Runtime/export/validator；Host 仍可直接手工物化另一套 ZIP。
3. Host-native 自定义交付没有被要求与 Runtime Export 文件合同完全等价。
4. 当前 `_full_html_depth_check()` 仍以九个标题字符串存在为主要检查，无法证明内容深度。
5. 旧 Host 审计把 `culture_intersectionality=true / photography_parameters=true` 之类布尔存在性当成完成证据。

## v0.6.47 修复边界
- **Host-native FULL Materialization Contract = Runtime Export Contract**。
- FULL 内容使用 V3 结构深度审计，不再接受标题/boolean/file-count 证明。
- 策略生成阶段直接物化 20 维 Market/Audience/Culture 状态、交叉性、本地化、Framework Relationship、Resource Tradeoff、条件式 Inclusive Photography。
- Runtime Export 恢复全部顶层 machine authorities 到 `supporting_analysis/`，导出独立 `ASSET_UNIVERSE.json`、Video objects、Object Manifest、Materialization Audit。
- Asset Universe 的所有非 Archive / NOT_NEEDED 候选必须物化，或有明确 HOLD/MISSING_INPUT 决策；Gallery capacity 不得删除 Paid/Test/Social/Video/PDP/A+ 候选。
- Listing / Assets / Video / Ads / Review / Research 的外文运营文本必须有同对象中文 companion；EN Model Prompt 保持 provider-facing English execution language。
- 完成前运行 Host package parity audit；任何 P0 materialization gap 不得标 READY/PASS。
