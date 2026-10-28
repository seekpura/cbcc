from pathlib import Path

# SKILL.md
p = Path('SKILL.md')
text = p.read_text(encoding='utf-8')
text = text.replace('version: 0.6.13-provider-transport-integrity', 'version: 0.6.14-provider-executor-lifecycle', 1)
anchor = '## v0.6.13 Provider Transport Integrity\n'
section = '''## v0.6.14 Provider Executor Lifecycle
- `ProviderExecutor` 是真实 Provider 执行的可插拔边界：adapter 自己负责 credentials / network client / vendor SDK，CBCC 负责 portable job、source lineage、idempotency、resume state、output hash 与 production receipt。
- materialized `EXTERNAL_ADAPTER` job 可执行完整生命周期：校验并 upload / refresh 商品资产 → 构建 executor transmission → 幂等 submit → poll / resume → collect → resolve 实际输出字节 → 写 `result.json + production_receipt` → 交回既有 ingest。
- `executor_state.json` 在每个外部边界持久化，因此宿主中断后可继续 poll，不会因为重试再次创建同一 Provider job。
- portable `source_binding_hash` 是不可变 lineage；provider handle 重绑定使用独立 `provider_execution_source_binding_hash`，不能覆盖上游真源绑定。
- executor transmission 必须声明 v0.6.13 portable transmission 为 parent；ingest 校验 parent transmission linkage、executor request hash 与 external acknowledgement 三层绑定。
- `ReferenceMemoryExecutor` 是可执行 reference adapter，只用于证明协议闭环；真实 provider 的凭证、上传、提交、轮询、下载实现继续外置。

'''
if '## v0.6.14 Provider Executor Lifecycle' not in text:
    if anchor not in text:
        raise SystemExit('SKILL anchor missing')
    text = text.replace(anchor, section + anchor, 1)
p.write_text(text, encoding='utf-8')

# CHANGELOG.md
p = Path('CHANGELOG.md')
text = p.read_text(encoding='utf-8')
section = '''## 0.6.14 — Provider Executor Lifecycle
- Added pluggable `ProviderExecutor` execution boundary with credential/network ownership kept in provider adapters.
- Added persisted executor state for upload/refresh → idempotent submit → poll/resume → collect → byte resolution → production receipt.
- Preserved immutable portable source-binding lineage while tracking provider-side handle rebinding separately.
- Added child execution-transmission lineage bound to the v0.6.13 portable parent transmission and validated by existing ingest.
- Added `ReferenceMemoryExecutor` plus end-to-end tests proving resume without duplicate submit and existing-ingest compatibility.
- See `CHANGELOG_V0614.md`.

'''
if not text.startswith('## 0.6.14'):
    text = section + text
p.write_text(text, encoding='utf-8')

# CURRENT_HANDOFF.md
p = Path('CURRENT_HANDOFF.md')
text = p.read_text(encoding='utf-8')
text = text.replace('# CBCC v0.6.13 CURRENT HANDOFF', '# CBCC v0.6.14 CURRENT HANDOFF', 1)
text = text.replace('当前版本：`0.6.13-provider-transport-integrity`。', '当前版本：`0.6.14-provider-executor-lifecycle`。', 1)
next_anchor = '## 下一步唯一主任务\n'
if '## v0.6.14 已完成' not in text:
    pos = text.find(next_anchor)
    if pos < 0:
        raise SystemExit('handoff next-task anchor missing')
    section = '''## v0.6.14 已完成
1. 新增可插拔 `ProviderExecutor` protocol；credentials / network client / vendor SDK 由 adapter 外置，CBCC 只拥有执行状态与完整性合同。
2. materialized Provider Job 进入真实生命周期：prepare / upload-or-refresh → idempotent submit → poll/resume → collect → resolve/download → `result.json + production_receipt`。
3. `executor_state.json` 持久化外部 job ID、resume token、poll count 与 transmission，宿主恢复后不重复 submit。
4. 本地商品母版上传前再次 SHA256；过期 Provider Handle refresh 必须 rotate handle，并保留 supersedes + generation + content SHA256 lineage。
5. portable `source_binding_hash` 保持不可变；Provider 侧 locator/handle 重绑定使用 `provider_execution_source_binding_hash`。
6. executor transmission 成为 v0.6.13 portable transmission 的 child；ingest 同时校验 parent binding、execution request hash、external acknowledgement。
7. `ReferenceMemoryExecutor` 已跑通 upload / refresh / submit / resume / output bytes / receipt / existing ingest 闭环。
8. v0.6.13 + v0.6.14 定向联测：9 passed。

'''
    text = text[:pos] + section + text[pos:]
start = text.find(next_anchor)
if start < 0:
    raise SystemExit('handoff next-task anchor missing after insert')
replacement = '''## 下一步唯一主任务
**把 ProviderExecutor 从 reference protocol 推进到宿主可调用的 Adapter Registry / Executor Bridge：定义 provider adapter discovery、capability declaration、retry/backoff/rate-limit/cancel/reconcile 语义，并接一个真实 Provider profile 时保持凭证外置。与此同时继续以现有 `Provider Job → Executor → Production Receipt → Ingest` 为唯一执行链，不建立旁路。**
'''
text = text[:start] + replacement
p.write_text(text, encoding='utf-8')
