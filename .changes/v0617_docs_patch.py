from pathlib import Path

# SKILL.md
p = Path('SKILL.md')
text = p.read_text(encoding='utf-8')
text = text.replace('version: 0.6.16-provider-host-execution-surface', 'version: 0.6.17-host-action-mapping', 1)
anchor = '## v0.6.16 Provider Host Execution Surface\n'
section = '''## v0.6.17 Host Action / MCP / Plugin Mapping
- 新增 canonical host action catalog：`adapters.list / execute / status / resume / cancel / reconcile` 六个 action，schema 与 permission scope 由同一真源定义。
- `ProviderActionDispatcher` 只调用 v0.6.16 `ProviderExecutionSurface`；Action / MCP / Plugin 不复制 ProviderExecutor、Bridge、Receipt 或 ProjectState completion runtime。
- authorization 默认 DENY；read / execute / cancel / reconcile 权限显式分离，mutating action 必须持有对应 scope。
- 长任务不建立第二套 async job DB：execute 返回稳定非敏感 operation ID；status 只读现有 `bridge_state / executor_state / result / production_run`；resume 重新进入同一持久化 Provider lifecycle，因此不重复 submit。
- operation ID 与 project + materialized job scope 绑定；status/resume 改换 asset scope 会被拒绝。
- action payload 在 dispatch 前递归拒绝 credential-like 字段，包含 exact 与 namespaced 形式：`api_key / provider_api_key / oauth_token / clientSecret / password / credential / authorization / private_key` 等。
- runtime context 继续只来自 ProviderExecutionSurface resolver，不进入 action JSON。
- `action_transport_manifest()` 仅声明 MCP tool name / Plugin operationId 的薄映射，并显式声明当前仓库没有 MCP/Plugin server；未来 transport 只能包裹 canonical dispatcher。

'''
if '## v0.6.17 Host Action / MCP / Plugin Mapping' not in text:
    if anchor not in text:
        raise SystemExit('SKILL anchor missing')
    text = text.replace(anchor, section + anchor, 1)
p.write_text(text, encoding='utf-8')

# CHANGELOG.md
p = Path('CHANGELOG.md')
text = p.read_text(encoding='utf-8')
section = '''## 0.6.17 — Host Action / MCP / Plugin Mapping
- Added canonical provider action schemas and a host-neutral dispatcher over ProviderExecutionSurface.
- Added explicit default-deny authorization scopes for read, execute, cancel, reconcile and status operations.
- Added status/resume semantics over existing persisted provider state without a second async job database.
- Added stable operation scope binding and recursive rejection of exact/namespaced credential-bearing action fields.
- Added declarative MCP tool / Plugin operation mappings without claiming a transport server exists.
- See `CHANGELOG_V0617.md`.

'''
if not text.startswith('## 0.6.17'):
    text = section + text
p.write_text(text, encoding='utf-8')

# CURRENT_HANDOFF.md
p = Path('CURRENT_HANDOFF.md')
text = p.read_text(encoding='utf-8')
text = text.replace('# CBCC v0.6.16 CURRENT HANDOFF', '# CBCC v0.6.17 CURRENT HANDOFF', 1)
text = text.replace('当前版本：`0.6.16-provider-host-execution-surface`。', '当前版本：`0.6.17-host-action-mapping`。', 1)
next_anchor = '## 下一步唯一主任务\n'
if '## v0.6.17 已完成' not in text:
    pos = text.find(next_anchor)
    if pos < 0:
        raise SystemExit('handoff next-task anchor missing')
    section = '''## v0.6.17 已完成
1. 仓库审计确认当前没有 MCP server / Plugin action runtime，因此没有伪造“已接 MCP”；先建立 host-neutral canonical Action Contract + Dispatcher。
2. 六个 canonical actions：adapter list、execute、status、resume、cancel、reconcile；每个 action 有明确 input schema / output status / permission scope。
3. authorization 默认 DENY；`PROVIDER_ADAPTER_READ / PROVIDER_STATUS_READ / PROVIDER_EXECUTE / PROVIDER_CANCEL / PROVIDER_RECONCILE` 权限独立。
4. Action Dispatcher 只调用现有 `ProviderExecutionSurface`，不直接 instantiate executor，不复制 Provider runtime。
5. execute → PENDING → status(read-only) → resume 已跑通；resume 复用同一 external job，Reference Executor submit count 保持 1。
6. operation ID 绑定 project + materialized job scope；scope 被改动时 status/resume 拒绝继续。
7. 不建立第二套 async job DB；状态继续来自 `bridge_state.json / executor_state.json / result.json / production_run.json`。
8. action payload 禁止 credential-like 字段，包含 namespaced key；runtime context 继续只由 v0.6.16 Host Surface resolver 注入。
9. 提供 MCP tool name / Plugin operationId 的 declarative thin mapping，但 manifest 明确 `claims_mcp_server_exists=false / claims_plugin_server_exists=false`。
10. v0.6.13–v0.6.17 provider continuity + host-action 定向联测：33 passed。

'''
    text = text[:pos] + section + text[pos:]
start = text.find(next_anchor)
if start < 0:
    raise SystemExit('handoff next-task anchor missing after insert')
replacement = '''## 下一步唯一主任务
**基于 v0.6.17 canonical Action Catalog 生成真正可消费的 Transport Descriptors：MCP tool descriptor 与 Plugin/OpenAPI action descriptor 必须从同一 action schema 自动派生、通过 schema parity / authorization / secret-field lint；随后实现一个薄 transport adapter（优先选择与当前宿主最匹配者），其 handler 只能调用 ProviderActionDispatcher。禁止手写两套 schema、禁止 transport 自己执行 Provider lifecycle。**
'''
text = text[:start] + replacement
p.write_text(text, encoding='utf-8')
