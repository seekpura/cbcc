# CBCC v0.6.9 — Photography Execution Continuity

## 目标
修复真实 KIYUU 一致性审计发现的执行断链：摄影合同已经参与策划，但 `capture_mode`、商品占画比例、显式输出色彩空间等参数在 Design Card → Canonical Prompt → 人类生产台之间被部分吞掉。

## 已完成
1. `prompt_compiler._design_card()` 新增 `photography_execution`，完整保留显式 `capture_mode`、`composition`、`color_management`。
2. CN/EN Canonical Prompt 新增拍摄 / 合成模式、构图执行合同与色彩管理合同。
3. `Parameter Trace` 新增 `PHOTOGRAPHY EXECUTION CONTRACT`；`machine_visual_contract` 同步携带 `photography_execution`。
4. Human Asset Production Workspace 的「摄影 / CMF」阶段直接展示拍摄 / 合成模式、构图执行合同与输出色彩管理。
5. Composition 不做字段白名单截断：回归测试加入 `negative_space` 与 `subject_clearance`，确保未来扩展字段继续贯穿。
6. 真实 KIYUU fixture 三个资产均验证 `COMPOSITE`、68% 商品占画、`sRGB`、`locked real-product layer` 同时存在于 Design Card、CN/EN Prompt、Trace 与 HTML 工作区。
7. v0.6.7 + v0.6.8 + v0.6.9 定向联测：12 passed。
8. 全量测试：100 passed / 13 个既有 baseline failures；本轮没有新增失败。

## 边界
- 不把 `target_user`、RACE、KPI、Asset/Project/Direction ID 等内部策略/工程元数据机械灌入 Render Prompt。
- 精确可见文案继续走 deterministic composition，不交给图像模型重写。
- 策略派生的颜色一致性说明可以补充显式色彩合同，但不得覆盖显式 `output_space` / 商品颜色保真约束。

## 下一阶段
继续用真实 KIYUU SKU 审计视觉执行约束，重点检查 `approved_visual_elements` 与 `editable_layer_contract` 在 Design Card、Machine Contract、Prompt 和人类生产台之间是否各自出现在正确层级；只传递真正影响生成/合成的内容，不把内部控制元数据污染 Render Prompt。
