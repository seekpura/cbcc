from pathlib import Path

# SKILL.md
p = Path('SKILL.md')
text = p.read_text(encoding='utf-8')
text = text.replace('version: 0.6.17-host-action-mapping', 'version: 0.6.18-transport-descriptor-parity', 1)
anchor = '## v0.6.17 Host Action / MCP / Plugin Mapping\n'
section = '''## v0.6.18 Transport Descriptor Parity
- 从 v0.6.17 canonical Action Catalog 自动派生 MCP tool descriptors 与 Plugin/OpenAPI 3.1 descriptors；transport 不维护第二份 action schema。
- checked-in 生成物：`transport/mcp_tools.json`、`transport/plugin_openapi.json`、`transport/descriptor_manifest.json`，由生成器物化并由测试反向校验当前 canonical schema。
- parity 必须同时满足：action 数量一致、tool/operation 名称一致、input schema exact equality、permission scope 一致、authorization source 一致、credential-like field lint 为零。
- 每个 action 记录 canonical / MCP / Plugin schema hash；三者必须相同，schema 漂移 fail closed。
- Plugin/OpenAPI 默认使用同源相对 server `/`，descriptor 本身不绑定假远程服务地址。
- `PluginActionTransportAdapter` 是薄 operationId adapter，唯一执行依赖为 `ProviderActionDispatcher`；不持有 surface / bridge / executor。
- checked-in manifest 明确 `mcp_server_included=false`、`plugin_http_server_included=false`：当前版本生成可消费 descriptor，但不伪造网络 server 已存在。

'''
if '## v0.6.18 Transport Descriptor Parity' not in text:
    if anchor not in text:
        raise SystemExit('SKILL anchor missing')
    text = text.replace(anchor, section + anchor, 1)
p.write_text(text, encoding='utf-8')

# CHANGELOG.md
p = Path('CHANGELOG.md')
text = p.read_text(encoding='utf-8')
section = '''## 0.6.18 — Transport Descriptor Parity
- Added generated MCP tool and Plugin/OpenAPI 3.1 descriptors from the canonical host action catalog.
- Added checked-in transport artifacts with exact schema/scope parity hashes and credential-field lint.
- Added fail-closed parity checks for schema, authorization scope, operation naming and secret-field drift.
- Added a thin PluginActionTransportAdapter that delegates only to ProviderActionDispatcher.
- Explicitly records that no MCP server or Plugin HTTP server is included in this release.
- See `CHANGELOG_V0618.md`.

'''
if not text.startswith('## 0.6.18'):
    text = section + text
p.write_text(text, encoding='utf-8')

# CURRENT_HANDOFF.md
p = Path('CURRENT_HANDOFF.md')
text = p.read_text(encoding='utf-8')
text = text.replace('# CBCC v0.6.17 CURRENT HANDOFF', '# CBCC v0.6.18 CURRENT HANDOFF', 1)
text = text.replace('当前版本：`0.6.17-host-action-mapping`。', '当前版本：`0.6.18-transport-descriptor-parity`。', 1)
next_anchor = '## 下一步唯一主任务\n'
if '## v0.6.18 已完成' not in text:
    pos = text.find(next_anchor)
    if pos < 0:
        raise SystemExit('handoff next-task anchor missing')
    section = '''## v0.6.18 已完成
1. MCP tools 与 Plugin/OpenAPI descriptors 全部由 v0.6.17 canonical Action Catalog 生成，不再手写两套 schema。
2. 6 个 canonical actions 在 MCP / Plugin 两种 transport 下保持 exact input-schema parity。
3. descriptor parity 同时校验 tool/operation naming、permission scope、authorization source 与 credential-like field lint。
4. checked-in `descriptor_manifest.json` 保存 canonical/MCP/Plugin schema hashes；当前 6 个 action 三方 hash 全部一致，issues=[]。
5. checked-in `mcp_tools.json / plugin_openapi.json / descriptor_manifest.json` 与 runtime generator 输出完全一致。
6. OpenAPI 使用同源相对 `/`；没有把 credential schema、API key 字段或假 provider runtime 放进 descriptor。
7. `PluginActionTransportAdapter` 只做 operationId → canonical action → Dispatcher 转发，不持有 surface / bridge / executor。
8. descriptor manifest 明确没有 MCP server / Plugin HTTP server；网络 host 仍是下一层薄适配器责任。
9. v0.6.13–v0.6.18 provider continuity + transport parity 定向联测：40 passed。

'''
    text = text[:pos] + section + text[pos:]
start = text.find(next_anchor)
if start < 0:
    raise SystemExit('handoff next-task anchor missing after insert')
replacement = '''## 下一步唯一主任务
**在 v0.6.18 descriptors 之上实现一个真正可启动但仍然薄的 transport host：优先实现 Plugin/OpenAPI HTTP host（与当前 ChatGPT/Plugin 使用面最接近），只负责 HTTP request → operationId → `PluginActionTransportAdapter` → `ProviderActionDispatcher`，并把 `ActionAuthorization` 作为宿主注入而不是请求体 credential。补 health/schema endpoints、request size/JSON validation、authorization hook、pending/resume/status HTTP semantics 与 transport-level error mapping；禁止 transport host 直接调用 ProviderExecutionSurface / Bridge / Executor。MCP server 后续复用同一 canonical descriptors/dispatcher。**
'''
text = text[:start] + replacement
p.write_text(text, encoding='utf-8')
