# v0.6.45 — Commercial Delivery Stability

## Fixed regressions
1. **真源图可携带**：Export 在 HTML 编译前解析 `source_product_assets.json` 和常见 source/upload 目录，把真实图片复制到交付包 `sources/`。现有 HTML data-URI renderer 因此可以在单独打开 `index.html` 时显示真源图。声明但缺失的源图进入显式审计，不再静默空白。
2. **正常语言矩阵**：非中国平台默认交付 English baseline + Platform primary language + Chinese interpretation；英语主语言自动去重为 English + Chinese；中国平台/中国大陆市场 CN_ONLY；平台未知时 English + Chinese，平台主语言保持 MISSING_INPUT。
3. **取消平台/市场静默默认**：正式交付只接受当前请求或明确标记的项目目标。历史示例、旧项目、`platform_compile` 和自动推断不能把平台/市场升级成当前真源。
4. **冻结商业工作台 Shell**：引入 `cbcc-commercial-v1`。普通 CBCC 版本升级只能在该壳内做加法，不再反复更换 Sidebar/Dashboard/长页结构。

## Runtime
- `runtime/cbcc/platform_scope.py`
- `runtime/cbcc/delivery_language_matrix.py`
- `runtime/cbcc/source_truth_media.py`
- `runtime/cbcc/commercial_workspace_shell.py`
- `runtime/cbcc/delivery_export.py` 接入上述四层合同。

## Human workspace
`cbcc-commercial-v1` 保留 v0.6.36 成熟 routed workspace：一次一个一级工作面、模块 subview/lens、独立 `asset/<id>`、搜索、复制、响应式与打印/PDF；运营执行继续是增量入口，不替代 Strategy/Listing/Assets/Video/Ads/Review/Evidence。

## Compatibility
本版本继续保留 v0.6.44 defaultPrompt 权威边界、v0.6.43 全局中文释义和 v0.6.42 的交互/Asset Universe 恢复规则。