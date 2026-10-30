# FULL Final ZIP Hard-Rule Completion Lock — v0.6.48

## Highest current precedence for FULL completion

本规则只管 **FULL / end-to-end 商业项目的最终完成态**。它不把九域变成固定页面模板，也不限制 Agent 的创意与资产数量；它只解决一个事故：上游 Skill/Runtime 明明有能力，Host-native 最终 ZIP 却可以绕开消费者与验证器，自写一份较薄的 `index.html` / audit 后仍被当成“已经实现”。

**最终真实交付包（final materialized package）是完成证据。上游代码、Prompt、Authority、布尔字段、标题、文件数量、旧 audit、自述“已完成”都不能替代对最终包的检查。**

## 1. FULL 最终包必须直接物化 9 个用户硬合同对象

除既有 Product Truth / Listing / Asset Universe / per-asset packages 等对象外，FULL 最终包必须有可机器读取的下列对象；名称固定是为了让 Host-native 与 Runtime 能被同一终检器验证，不代表人类 UI 必须按固定九页组织：

1. `supporting_analysis/INFORMATION_COMPLETENESS_ASSUMPTION_DECISION.json`
2. `supporting_analysis/PRODUCT_FACT_AUDIT.json`
3. `supporting_analysis/PLATFORM_REGION_AUDIENCE_CULTURE.json`
4. `supporting_analysis/MARKETING_FRAMEWORK_CORE_STRATEGY.json`
5. `supporting_analysis/VISUAL_EXECUTION_LOCK.json`
6. `supporting_analysis/PLATFORM_CONTENT_MATRIX.json`
7. `supporting_analysis/RACE_FRAMEWORK.json`
8. `supporting_analysis/CULTURAL_ADAPTATION.json`
9. `supporting_analysis/COMPLIANCE_RISK_EVALUATION_PRIORITY.json`
10. `supporting_analysis/CLAIM_EVIDENCE_MATRIX.json`（P0 claim/evidence authority）

`index.html` 必须让人类直接看到九域核心对象；Listing、Asset、Video、Paid、Creator 等业务对象继续按项目作者化，不得被九域覆盖或缩掉。

## 2. 真实内容合同，不接受占位/标题式 PASS

- Domain 01：信息审计 → 最多10个待确认 → 明确假设 → 决策日志 → 继续执行。
- Domain 02：必须同时出现真实卖点 / 可感知利益 / 情绪价值 / 不可宣称项，并显式定义完整证据等级 A/B/C：A=检测报告/官方认证/可复现实测；B=供应链/配方/成分机理等有边界支持；C=主观体验/创意假设/待验证。任何 C 级 `hard_claim_allowed` 必须为 false；不能因为当前项目没有 A 级材料就删掉 A 级定义。
- Domain 03：平台 / 区域 / 人群 / 族裔文化 WHY 必须可见；交叉性至少覆盖 `族裔 × 性别 × 年龄 × 收入 × 地域`；本地化至少覆盖语言回译、节日、支付、物流、宗教/禁忌、法规。FULL 中 `race_ethnicity=NOT_RELEVANT` 不能作为逃避文化校验的默认值；没有细分证据应写 `TO_VERIFY / ASSUMPTION / REQUIRED_CULTURAL_VALIDATION` 并保持非标签化。
- Domain 04：每条重大策略必须有 `decision + basis + tradeoff + why_platform_region_audience_culture + execution + metric`；明确 RACE / STP+JTBD / AIDA/FABE / 4P/Funnel 的角色；资源取舍显式 P0/P1/P2。
- Domain 05：风格、情绪板、构图、HEX/对比、灯光、焦段/景别/机位、场景、道具、模特/服化道、平台规格、Shot List 必须实际物化。人物相关时 Inclusive Photography 为 P0：深肤色曝光/暗部保护、neutral bounce/reflector/diffusion、发质、体型、残障、年龄、AI bias。具体曝光值若给出，必须标明是 Prelight 起始值/条件，而不是把肤色变成固定曝光公式。
- Domain 06：实际 Surface 行必须有平台、人群、选题、Hook、脚本结构、视觉、CTA、Metric、RACE、文化/禁忌、尺寸/时长、封面/首帧、字幕、音乐版权、流量机制、Landing、UTM/归因；当前平台算法/规则/法规未知写 `TO_VERIFY`。
- Domain 07：RACE 顺序固定 `Research → Action → Communication → Evaluation`；每阶段包含目标、关键动作、输出物、平台、文化校验、指标、WHY。
- Domain 08：文化检查表至少有适配点、包容性表征、刻板印象/禁忌、校验结果、修改动作、依据/假设。
- Domain 09：合规/文化风险、A/B、指标、自检、P0/P1/P2、下一步输入齐全；P0 Claim Matrix 显式覆盖功效、成分、认证、价格、销量等风险类别。

## 3. 完成态必须经过“最终真实包”终检

Runtime 路径与 Host-native/Skills-only 路径都必须在 **所有最终文件写完之后** 对实际 package directory 运行同一检查语义。仓库参考实现：

`scripts/check_v0648_user_hard_rule_final_zip.py <package_dir>`

检查结果写入：

`qa/USER_HARD_RULE_VALIDATION.json`

并满足：

- `status = PASS`
- `issues = []`
- `project_completion_blocking = true`

然后重新打 ZIP；对 **重新解压后的 ZIP** 再运行一次同一终检。只有 re-extracted package 也 PASS，才允许说“FULL 用户硬合同已完成”。

Host 没有 Python Runtime 时，也必须对最终 package 做等价内容检查并写同结构 audit；但**不得读取旧 `FULL_MATERIALIZATION_AUDIT.json` 的 PASS 字段来替代检查**。旧 audit 只能是被检查对象之一。

## 4. Hard-rule completeness 与 Launch readiness 分离

用户硬合同是否物化完整，和外部发布条件是否已满足，是两个不同状态：

- 例如：NPRA Notification 未提供时，九域/文化/RACE/视觉/内容矩阵可以完整，`USER_HARD_RULE_VALIDATION` 可以 PASS；
- 但 `launch_readiness` 必须保持 BLOCKED / MISSING_INPUT，不能宣称法规上架就绪。

这样既不会因为外部缺件让 Agent 停工，也不会把缺失的法规/认证/经济数据编造出来。

## 5. Completion wording lock

任一条件发生时不得说“修复完成 / FULL COMPLETE / READY”：

- 终检脚本/等价终检未运行；
- 最终 ZIP 未重新解压复核；
- `USER_HARD_RULE_VALIDATION.status != PASS`；
- `index.html` 没直接消费九域核心对象；
- C 级形成硬宣称；
- `race_ethnicity=NOT_RELEVANT` 被用来跳过 FULL 文化校验；
- RACE/文化表/内容矩阵/视觉包容性只存在于规则文件，不在最终交付包。

本锁的目标不是增加运营门禁，而是让 **Agent 已经拥有的策略能力真正消费到最后一个可交付文件**。