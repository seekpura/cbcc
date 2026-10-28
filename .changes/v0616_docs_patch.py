from pathlib import Path

# SKILL.md
p = Path('SKILL.md')
text = p.read_text(encoding='utf-8')
text = text.replace('version: 0.6.15-provider-executor-bridge', 'version: 0.6.16-provider-host-execution-surface', 1)
anchor = '## v0.6.15 Provider Adapter Registry / Executor Bridge\n'
section = '''## v0.6.16 Provider Host Execution Surface
- 新增 `ProviderExecutionSurface`，把 v0.6.15 Adapter Registry / Executor Bridge 暴露成宿主可操作入口；仍然复用唯一链路 `Provider Job → Adapter Registry → Executor Bridge → ProviderExecutor → Production Receipt → Ingest`。
- CLI 新增 `adapter-list / provider-execute / provider-cancel / provider-reconcile`；不提供 `--api-key` / token / secret 等参数，避免凭证进入 shell history、项目文件或日志。
- `CBCC_PROVIDER_HOST_MODULE` 只保存宿主 Python module 名称。真实 SDK/client/auth/callback 由 module 的 `create_runtime_context(...)` 在运行时注入，runtime context 不持久化。
- `provider-execute` 只有在 `PROVIDER_JOB_INDEX` 中所有 materialized job 都有真实 result 时才自动调用既有 ingest；局部/分批执行不能把全项目误标为 COMPLETE。
- 自动 ingest 成功后继续更新既有 ProjectState `PRODUCTION` gate 与 Review Workspace；Host Surface 不创建第二套完成权威。
- cancel / reconcile 继续复用同一 external job ID、`executor_state.json` 与 `bridge_state.json` lineage。
- 安全回归明确扫描 `bridge_state / executor_state / result / production_run / ProjectState`，宿主 secret 值不得落盘。

'''
if '## v0.6.16 Provider Host Execution Surface' not in text:
    if anchor not in text:
        raise SystemExit('SKILL anchor missing')
    text = text.replace(anchor, section + anchor, 1)
p.write_text(text, encoding='utf-8')

# CHANGELOG.md
p = Path('CHANGELOG.md')
text = p.read_text(encoding='utf-8')
section = '''## 0.6.16 — Provider Host Execution Surface
- Added programmatic ProviderExecutionSurface over the existing adapter registry/executor bridge.
- Added `adapter-list`, `provider-execute`, `provider-cancel`, and `provider-reconcile` CLI operations with no secret-bearing CLI arguments.
- Added host-module runtime-context injection via module name only; credentials/SDK clients remain host-owned and non-persistent.
- Automatic ingest requires a complete materialized result set and continues to use existing ingest + ProjectState production authority.
- Added host execution, state update, cancel/reconcile and secret non-persistence regression coverage.
- See `CHANGELOG_V0616.md`.

'''
if not text.startswith('## 0.6.16'):
    text = section + text
p.write_text(text, encoding='utf-8')

# CURRENT_HANDOFF.md
p = Path('CURRENT_HANDOFF.md')
text = p.read_text(encoding='utf-8')
text = text.replace('# CBCC v0.6.15 CURRENT HANDOFF', '# CBCC v0.6.16 CURRENT HANDOFF', 1)
text = text.replace('当前版本：`0.6.15-provider-executor-bridge`。', '当前版本：`0.6.16-provider-host-execution-surface`。', 1)
next_anchor = '## 下一步唯一主任务\n'
if '## v0.6.16 已完成' not in text:
    pos = text.find(next_anchor)
    if pos < 0:
        raise SystemExit('handoff next-task anchor missing')
    section = '''## v0.6.16 已完成
1. 新增 `ProviderExecutionSurface`：宿主通过稳定程序化入口操作 adapter discovery / execute / cancel / reconcile，而不是直接碰内部 executor。
2. CLI 新增 `adapter-list / provider-execute / provider-cancel / provider-reconcile`；没有 API key / token / secret 参数。
3. 新增 `CBCC_PROVIDER_HOST_MODULE`，其值仅为 host module 名称；宿主 module 可 `register_adapters(registry)` 并用 `create_runtime_context(...)` 返回瞬时 callbacks / SDK client / auth objects。
4. runtime context 不写入 adapter declaration、bridge state、executor state、result、production run 或 ProjectState。
5. `provider-execute` 继续复用 Registry → Bridge → Executor → Receipt → existing ingest；全部 materialized jobs 结果齐全后才自动 ingest。
6. 自动 ingest 成功继续更新 ProjectState `PRODUCTION=READY_REVIEW` 并物化 Review Workspace，没有第二套 completion authority。
7. 局部/分批执行结果不齐时 ingest 明确 DEFER，不会误把全项目 COMPLETE。
8. CLI cancel / reconcile 使用现有 external job ID / executor state / bridge state lineage。
9. v0.6.13–v0.6.16 provider continuity + host-surface 定向联测：23 passed。

'''
    text = text[:pos] + section + text[pos:]
start = text.find(next_anchor)
if start < 0:
    raise SystemExit('handoff next-task anchor missing after insert')
replacement = '''## 下一步唯一主任务
**把 v0.6.16 Host Execution Surface 映射到真实宿主 Action / MCP / Plugin 调用层：先审计当前 ChatGPT Plugin / 宿主可暴露的 action schema，再让 `adapter-list / provider-execute / provider-cancel / provider-reconcile` 直接调用现有 ProviderExecutionSurface；补 action authorization、长任务 resume/status 与 secret/runtime-context 边界。禁止复制 Provider runtime、禁止在 action schema 中出现 credential 值字段。**
'''
text = text[:start] + replacement
p.write_text(text, encoding='utf-8')
