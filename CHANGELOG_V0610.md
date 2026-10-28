# CBCC v0.6.10 — Visual Execution + Locked Copy Continuity

## 本轮真实断链
1. `approved_visual_elements`、`precision_boundaries`、`editable_layer_contract` 已在 Design Card / Machine Contract 中存在，但 Render Prompt 不消费；人类 Visual 工作台也未直接显示。
2. 人类资产页的 Copy 结构化读取仍指向旧 `copy_language` / `copy`，没有读取当前权威字段 `information_design.locked_visible_copy`。
3. 英文 Render Prompt 通过 `surface_contract` / `copy_budget` 整包 JSON 把 `locked_copy` 精确营销文案重新泄漏给图像模型，与 deterministic text composition 规则冲突。

## 修复
- CN/EN Prompt 新增 Visual Execution Boundaries / Editability，传递：允许视觉元素、精确执行边界、可编辑层、冻结层、商品 Fidelity 与安全的局部修改规则。
- Parameter Trace 新增同名执行位置。
- 人类 Visual 工作台直接显示 Fidelity、允许视觉元素、精确边界、可编辑/冻结层与局部修改规则。
- Copy 工作台直接读取 `information_design.locked_visible_copy`，并同步显示确定性排版规则、文案预算和字体方向。
- Render Prompt 在序列化 Surface / Copy Budget 前递归移除精确文案字段；精确文案仍完整保留在 `deterministic_copy_overlay` 与人类交付。
- `00_HUMAN_DESIGN_CARD_CN.md` 同步加入视觉边界与编辑冻结合同。

## 回归
- 新增 `tests/test_v0610_visual_execution_copy_continuity.py`。
- v0.6.7 / v0.6.8 / v0.6.9 / v0.6.10 定向联测：14 passed。
- 全量：103 passed / 12 个剩余失败；v0.6.9 已通过项无回退，并有 1 个既有 Provider Quality Preflight 失败因执行追踪增强转为通过。
