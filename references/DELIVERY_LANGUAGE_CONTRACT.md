# Delivery Language Contract — v0.6.6

1. 默认人类交付语言：`zh-CN`。
2. 用户明确指定其他交付语言时覆盖默认值。
3. 目标市场可见语言与交付语言是两个不同维度。
4. 当目标文案不是交付语言：
   - Listing / CTA / Asset visible copy：显示原文 + 中文释义。
   - Search terms：显示原词 + 中文搜索意图 / 用途，不强制逐词翻译。
   - Canonical Prompt：中文生产 Prompt + 英文/目标模型 Render Prompt 同时保留。
5. 交付界面、策略 WHY、摄影/CMF、风险、合规、假设、决策日志默认中文。
6. 品牌、SKU、产品型号、标准字段、专有名词可保留原文，不要求伪造中文名。
