# CBCC v0.6.8 — Asset Production Workspace

## 目标
把 v0.6.7 已经完成的 Strategy / Content / Visual / Listing / Prompt / Evidence 语义工作区继续下沉到**单资产生产现场**。单资产页面不再是“左侧 tab + 右侧文档”，而是围绕当前资产如何真正被生产、审阅和追溯组织信息。

## 已完成
1. `_asset_page()` 退出通用 `module-shell`，进入 `asset-production-workspace`。
2. 生产阶段由真实资产内容动态生成：决策 / Design Card、画面执行、摄影 / CMF、文案、Prompt 执行、QA / 来源；没有内容的阶段不会出现。
3. `overview + strategy` 合并成购买决策对象，避免用户在两个文档 tab 之间反复对照。
4. 中文 Prompt 与英文 / 目标模型 Prompt 合并为一个执行台，支持分别复制，并明确 Prompt 必须继承前序决策。
5. `production` 备注收进 Prompt 执行区；Parameter Trace、合同、源文件和未知 legacy 视图收进 QA / 来源区。
6. 移动端生产阶段变为横向可滚动决策轨；打印时自动展开所有资产阶段。
7. 新增 `tests/test_v068_asset_production_workspace.py`；v0.6.7 IA + v0.6.8 资产工作区定向联测 10 passed。
8. 使用真实 `tests/fixtures/kiyuu_my_tiktok` 编译验证：3 个资产均进入独立生产台，生成的离线 HTML 约 4.98 MB，单资产页不再出现 `module-shell`。

## 全量测试事实
当前恢复基线 + v0.6.8 新测试实测为 **98 passed / 13 baseline failures**。13 个失败来自既有历史兼容性 / 旧期望债务，本轮单资产工作区没有新增失败。此前交接文档记录的 `93 passed / 12 failures` 已由本轮同源对照复测纠正，不继续沿用错误数字。

## 下一阶段
继续移除 Product / Market / Risk 的通用 `module-shell`，但只在真实用户任务需要时拆分，不为了“页面都不同”而机械制造新模板。随后用真实 SKU 做策划参数 → Design Card → Canonical Prompt → 单资产生产台的一致性审计。
