# CBCC v0.6.11 — Source Master Binding + Frozen Revision Enforcement

## 本轮真实断链
真实 KIYUU + 真实临时商品母版的生产运行证明：商品母版虽然在 QA Contract 中有 `asset_id/path/hash/pixel_lock/allowed_transforms`，但 Provider 执行层没有独立、机器可读的 source binding；Renderer Recipe 也不携带母版 binding。结果侧要求 `source_product_asset_ids_used`，却没有对称的 SHA256 lineage。Local Revision 结果也没有强制声明 changed layers，因此 frozen product layer 仍可能只靠文字提醒保护。

## 修复
- Renderer Recipe 新增 `source_product_bindings`。
- Provider Job 顶层与 execution brief 都携带 handoff-verified binding，并使用 `source_binding_hash` 锁定本次母版合同。
- LOCAL_FILE_PATH 在 handoff 时重新检查文件存在与 SHA256；外部 Provider Handle 以声明 SHA256 绑定。
- Provider Contract 对所有 LOCKED_PIXEL 模式要求 `source_product_assets` + `source_product_bindings`。
- LOCKED_PIXEL result observations 新增 `source_product_hashes_used`；ID/hash lineage 不一致进入 Review。
- LOCKED_PIXEL result 必须确认 production contract 并回显 source binding hash。
- Local Revision result 必须声明 `changed_layers`；任何 frozen layer 修改报告直接进入 Review。

## 真实验证
- KIYUU fixture 注入真实本地商品母版并执行 production run。
- 3/3 Provider Jobs 均获得同一个 `READY_LOCAL_VERIFIED` 商品母版 binding。
- 删除编译后的母版文件后，handoff 转为 HOLD。
- 错误 source SHA、错误 binding hash、frozen-layer mutation 均被结果校验拒绝。
- v0.6.7–v0.6.11 定向回归：18 passed。
- 全量：107 passed / 12 个既有历史失败；无新增失败。
