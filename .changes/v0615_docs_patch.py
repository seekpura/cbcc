from pathlib import Path

# SKILL.md
p = Path('SKILL.md')
text = p.read_text(encoding='utf-8')
text = text.replace('version: 0.6.14-provider-executor-lifecycle', 'version: 0.6.15-provider-executor-bridge', 1)
anchor = '## v0.6.14 Provider Executor Lifecycle\n'
section = '''## v0.6.15 Provider Adapter Registry / Executor Bridge
- 新增 credential-free `ProviderAdapterRegistry`：按 provider / production mode / capabilities / operations 发现适配器，优先级选择确定性；显式指定 adapter 也必须通过 capability 匹配。
- 新增 `ProviderExecutorBridge`，只编排现有 v0.6.14 `ProviderExecutor`；唯一执行链保持 `Provider Job → Adapter Registry → Executor Bridge → ProviderExecutor → Production Receipt → Ingest`，不建立旁路完成态。
- 标准化 transient / permanent / rate-limit 错误；retry 有界，backoff 可配置，429 可使用 provider `retry_after_seconds`。未知异常默认永久失败，避免认证/参数错误无限重试。
- `bridge_state.json` 只保存 adapter ID、策略、attempt history、cancel/reconcile 状态；runtime_context / callbacks / API keys / credentials 不写入项目文件。
- 新增 cancel 与 reconcile 语义；reconcile 对比本地 executor state 与 provider 状态，不覆盖 `executor_state.json` 或 receipt lineage。
- 新增 `HostCallbackExecutor` 与 `EPV_HOST_CALLBACK_V1`：真实宿主通过 runtime callback/SDK/client 注入 Provider 能力；CBCC 不保存凭证。Reference Memory adapter 保持 opt-in，不是 production default。
- `provider_contract()` 对 EXTERNAL_ADAPTER 显式暴露 executor + bridge contract，避免 Bridge 成为未接路由的孤立模块。

'''
if '## v0.6.15 Provider Adapter Registry / Executor Bridge' not in text:
    if anchor not in text:
        raise SystemExit('SKILL anchor missing')
    text = text.replace(anchor, section + anchor, 1)
p.write_text(text, encoding='utf-8')

# CHANGELOG.md
p = Path('CHANGELOG.md')
text = p.read_text(encoding='utf-8')
section = '''## 0.6.15 — Provider Adapter Registry / Executor Bridge
- Added credential-free provider adapter discovery and deterministic capability-based selection.
- Added host executor bridge with bounded retry/backoff, provider retry-after, cancel and reconcile semantics.
- Added host callback provider profile so real SDK/network/auth stay external to CBCC runtime state.
- Kept one execution chain through existing ProviderExecutor → Production Receipt → Ingest authority.
- Bound bridge capability contract into external provider routing.
- See `CHANGELOG_V0615.md`.

'''
if not text.startswith('## 0.6.15'):
    text = section + text
p.write_text(text, encoding='utf-8')

# CURRENT_HANDOFF.md
p = Path('CURRENT_HANDOFF.md')
text = p.read_text(encoding='utf-8')
text = text.replace('# CBCC v0.6.14 CURRENT HANDOFF', '# CBCC v0.6.15 CURRENT HANDOFF', 1)
text = text.replace('当前版本：`0.6.14-provider-executor-lifecycle`。', '当前版本：`0.6.15-provider-executor-bridge`。', 1)
next_anchor = '## 下一步唯一主任务\n'
if '## v0.6.15 已完成' not in text:
    pos = text.find(next_anchor)
    if pos < 0:
        raise SystemExit('handoff next-task anchor missing')
    section = '''## v0.6.15 已完成
1. 新增 credential-free Adapter Registry：按 provider / mode / capability / operation discovery；确定性选择，不在 registry 保存认证信息。
2. 新增 Executor Bridge：在 v0.6.14 executor 之上统一 retry / exponential backoff / provider retry-after / cancel / reconcile。
3. `bridge_state.json` 与 `executor_state.json` 分工明确：前者保存宿主编排策略与尝试历史，后者继续保存 Provider job lifecycle；两者都不持久化 runtime credentials。
4. 标准错误分类：只有显式 transient / rate-limit 才重试；未知错误按 permanent 处理。
5. `HostCallbackExecutor` + `EPV_HOST_CALLBACK_V1` 已打通真实宿主注入面，SDK / HTTP client / auth callback 由宿主提供。
6. Reference Memory adapter 仅 opt-in 测试使用，不进入 production default discovery。
7. cancel / reconcile 与既有 external job ID / executor state 共用同一 lineage；没有第二套完成路径。
8. `provider_contract()` 已显式暴露 executor + bridge contract。
9. v0.6.13–v0.6.15 provider continuity 定向联测：16 passed。

'''
    text = text[:pos] + section + text[pos:]
start = text.find(next_anchor)
if start < 0:
    raise SystemExit('handoff next-task anchor missing after insert')
replacement = '''## 下一步唯一主任务
**把 v0.6.15 Bridge 暴露成宿主可操作的 Execution Surface：增加 `adapter-list / provider-execute / provider-cancel / provider-reconcile` 等程序化/CLI 入口，以及不把密钥写进参数、项目文件或命令历史的 runtime-context 注入接口；这些入口必须复用 Adapter Registry → Executor Bridge → ProviderExecutor → Production Receipt → Ingest 单一链。随后再据宿主能力决定 MCP / Plugin action 映射，不先造第二套执行 runtime。**
'''
text = text[:start] + replacement
p.write_text(text, encoding='utf-8')
