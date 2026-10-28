# CBCC v0.6.29 安装与验证

本文只描述 `main` / `v0.6.29` 的当前安装方式。源码权威始终是 GitHub `seekpura/cbcc` 的 `main`；Release ZIP 与 ChatGPT Plugin/Skill 是派生发行物。

## A. ChatGPT 私人 Plugin

推荐安装 `cross-border-commerce-creative-plugin-v0.6.29.zip`。它包含 Agent Plugins 1.0 `plugin.json`、OpenAI interface metadata、主 Skill 与当前 GitHub 源码 resources 快照。

如果账号里已经安装旧版 `Cross-Border Commerce Creative`，应升级原插件，不要另外创建同名副本，以保留原插件身份、历史与入口。

安装后检查：

- 插件名称：`Cross-Border Commerce Creative`
- 版本：`0.6.29`
- Skill：`cross-border-commerce-creative`
- Skill 内部源码版本：`0.6.29-final-stabilization`
- 当前主权威：`resources/SKILL.md`

### Runtime 边界

私人 Plugin 中的 Skill 可以消费打包 resources，但云端 ChatGPT 不会自动执行其中的本地 Python 文件。需要 Provider 执行、Plugin HTTP Action 或 MCP tool 时，应连接一个实际运行的宿主；不要把“源码已打包”误报为“远程 Runtime 已连接”。

## B. Standalone Skill

需要只安装 Skill 时，使用 `cross-border-commerce-creative-skill-v0.6.29.zip`。它与 Plugin 包使用同一 Skill wrapper 和同一 GitHub resources 快照，但没有 Plugin manifest。

## C. 本地完整 Runtime

使用 GitHub Release 的 `cross-border-commerce-creative-runtime-v0.6.29.zip`，或直接检出 `v0.6.29` / `main`。

建议 Python 3.11+。Runtime 当前以仓库目录为完整运行单元，因此不要只复制 `runtime/cbcc/`；`platform_packs/`、`references/`、`prompts/`、`schemas/`、`builders/` 等都属于运行/审计上下文。

### 基础检查

```bash
python --version
python bin/cbcc.py --help
bash tests/run_smoke.sh
```

Windows 若没有 Bash，可逐项运行 smoke 中的 validator：

```powershell
python validators/validate_sources.py tests/fixtures/minimal_valid
python validators/validate_claims.py tests/fixtures/minimal_valid
python validators/validate_asset_map.py tests/fixtures/minimal_valid
python validators/validate_cross_module.py tests/fixtures/minimal_valid
```

### 运行审计

```bash
python -m pip install pytest
python bin/cbcc.py audit --root .
```

### CLI 项目入口

```bash
python bin/cbcc.py init --project-dir ./work/demo --project-id demo
python bin/cbcc.py build --project-dir ./work/demo --request ./request.json
python bin/cbcc.py state --project-dir ./work/demo
python bin/cbcc.py review-build --project-dir ./work/demo
```

CBCC 的 build/resume/review/provider/revision/learning/export 都通过同一 ProjectState 与 current-scope completion 权威闭环，避免出现第二套“完成状态”。

## D. Plugin/OpenAPI HTTP Host

```bash
PYTHONPATH=runtime python -m cbcc.plugin_http_cli --bind 127.0.0.1 --port 8787
```

默认端口 `8787`。Host 提供 `/health`、`/openapi.json`、`/actions.json` 以及由 canonical action catalog 派生的 action routes。

授权与 Provider runtime context 通过宿主模块/环境注入；不要把 API key、token 或 secret 放入 action payload、descriptor、ProjectState 或 CLI 参数。

## E. MCP stdio Host

```bash
PYTHONPATH=runtime python -m cbcc.mcp_stdio_cli
```

MCP host 使用 stdio JSON-RPC，并复用 canonical action descriptors / ProviderActionDispatcher；它不是另一套 Provider Runtime。

## F. Provider Host

Provider adapter、SDK/client、credentials 和 auth callback 由宿主注入。CLI 可以检查和执行已注册 adapter：

```bash
python bin/cbcc.py adapter-list
python bin/cbcc.py provider-execute --project-dir ./work/demo
python bin/cbcc.py provider-reconcile --project-dir ./work/demo --asset-id <ASSET_ID>
```

没有真实宿主 adapter/credentials 时，系统应明确保持不可执行/待接入状态，而不是伪造生产成功。

## G. 发行校验

GitHub `v0.6.29` Release 由仓库 workflow 从 `main` 构建，流程包括：

1. Smoke validators。
2. v0.6.29 real-defect regression。
3. v0.6.27–v0.6.29 current-scope / frontier continuity。
4. 构建 Plugin / Skill / Runtime ZIP。
5. 生成 `SHA256SUMS.txt`。
6. 将同一批产物附加到 GitHub `v0.6.29` Release。

历史 v0.6.29 stabilization workflow 已单独完成 full-regression node-id diff，并要求 `NEW_FAILURE_COUNT=0`、`FIXED_FAILURE_COUNT>0`；发行打包 workflow 不用“重新接受一个固定失败数量”替代该发布门。

## H. 本地自行构建

```bash
python scripts/build_plugin_dist.py --output-dir dist
python scripts/build_dist.py dist/cross-border-commerce-creative-runtime-v0.6.29.zip
```

然后自行计算 SHA256，或使用 Release 提供的 `SHA256SUMS.txt` 对照。
