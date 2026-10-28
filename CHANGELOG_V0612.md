# CBCC v0.6.12 — Portable Provider Package + Production Receipt Lineage

## 本轮真实断链
v0.6.11 已能在 CBCC 主机 handoff 时验证 LOCAL_FILE_PATH 与 SHA256，但 `materialize_provider_jobs()` 仍把主机绝对 `package_dir` 和本地 source locator 写入 Provider Job。Job 离开当前文件系统后，合同看起来 READY，外部 Provider 却可能拿不到商品母版。另一方面，`layer_manifest` / `capture_metadata` 只是 optional result 字段，没有统一绑定 job/package/source/output 的生产回执。

## 修复
- Provider Job 物化为自包含目录：冻结资产包进入 `inputs/asset_package/`。
- LOCAL_FILE_PATH 商品母版再次校验 SHA256 后复制到 `inputs/product_masters/`，执行 locator 重绑为 `PACKAGE_RELATIVE_PATH`。
- Provider Asset Handle 保留为显式外部 handle，不伪装成本地资源。
- 新增 `PORTABLE_JOB_MANIFEST.json`，记录冻结包文件 hash、upstream/portable source binding 与 portable manifest hash。
- 外部 `result.json` 必须带 `production_receipt`，绑定 job_id、asset_id、provider、package_hash、portable_manifest_hash、source_binding_hash 与输出 artifact SHA256。
- LOCKED_PIXEL receipt 必须携带 source-bound frozen `layer_manifest`。
- REAL_PHOTO / VIDEO receipt 必须携带真实 `capture_metadata`；系统不要求或制造不存在的 EXIF。
- FILE_HANDOFF 返回的 job-relative 输出会在 ingestion 时重新计算 SHA256。

## 边界
本轮解决“job 可携带 + 回执可追溯”，不假装已经实现具体云 Provider API。下一轮再审计 Provider Asset Handle 生命周期、远程输出 URI hash 回收与具体 adapter 映射。