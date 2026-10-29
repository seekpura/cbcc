#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = 'cross-border-commerce-creative'
DISPLAY_NAME = 'Cross-Border Commerce Creative'

EXCLUDE_PARTS = {'.git', '.github', '.pytest_cache', '__pycache__', 'dist', 'evidence'}
EXCLUDE_SUFFIXES = {'.pyc', '.pyo'}

DEFAULT_PROMPTS = [
    '基于当前对话、上传资料和必要的最新公开信息，完成当前商品的跨境电商策略、Listing、内容、视觉策展与逐资产中英文 Canonical Prompt。该请求属于 FULL 商品项目：必须执行九域决策深度合同、Prompt 参数消费审计，并物化完整中文优先 index.html + 可编辑源 + 逐资产包 + ZIP。九域是完整度合同，不是固定页面模板；不得用自定义短报告替代。',
    '只做当前 SKU 的目标市场/平台视觉资产策展和逐资产生产提示词，本轮不生成图片；先建立商品真源、购买决策、创意机会和动态 Surface，并确保摄影/CMF/构图参数进入最终 Prompt。',
    '审查当前营销策划或提示词，定位写了但未被生产链消费、同风格同布局、产品失真、平台不原生或文案与画面脱节的责任层，只修对应层。',
]


def semver() -> str:
    raw = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)', raw)
    if not match:
        raise SystemExit(f'VERSION does not start with strict semver: {raw}')
    return '.'.join(match.groups())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def should_copy(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if not path.is_file():
        return False
    if any(part in EXCLUDE_PARTS for part in rel.parts):
        return False
    if path.suffix in EXCLUDE_SUFFIXES:
        return False
    return True


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def plugin_manifest(version: str) -> dict:
    return {
        '$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
        'name': PLUGIN_NAME,
        'version': version,
        'description': 'Cross-border ecommerce Commerce Agent for product truth, dynamic research, strategy, listing, content, visual/photography, canonical prompts, production, review and complete human artifact delivery.',
        'author': {'name': 'CBCC'},
        'keywords': [
            'ecommerce', 'cross-border', 'commerce-agent', 'marketing', 'listing',
            'creative', 'visual', 'prompt', 'photography', 'production', 'html-delivery',
        ],
        'extensions': {
            'com.openai': {
                'interface': {
                    'displayName': DISPLAY_NAME,
                    'shortDescription': '跨境电商策略、内容、创意与完整交付',
                    'longDescription': '跨境电商 Commerce Agent：从 Product Truth、证据与平台约束出发，动态完成研究、SKU/Offer、策略、Listing、内容、视觉摄影、图片/视频资产、Canonical Prompt、生产、Review 与学习闭环。完整任务必须产出中文优先的人类交付 Artifact，包括自包含 HTML 工作台、逐资产包与 ZIP；不得以纯聊天文本替代最终交付。',
                    'developerName': 'CBCC',
                    'category': 'Productivity',
                    'capabilities': ['Interactive'],
                    'defaultPrompt': DEFAULT_PROMPTS,
                }
            }
        },
    }


def compatibility_manifest(manifest: dict) -> dict:
    return {
        'interface': manifest['extensions']['com.openai']['interface'],
        'name': manifest['name'],
        'version': manifest['version'],
        'description': manifest['description'],
        'author': manifest['author'],
        'keywords': manifest['keywords'],
        'skills': './skills',
    }


def skill_wrapper(version: str) -> str:
    return f'''---
name: cross-border-commerce-creative
description: 用于跨境电商 Product Truth、动态研究、SKU/Offer、Listing/Search、策略、内容、视觉摄影、图片/视频资产、逐资产中英文 Canonical Prompt、生产、Review、学习闭环与完整人类交付；默认中文，任务范围与资产结构动态决定。
---
# Cross-Border Commerce Creative v{version}

完整 Agent/Skill 权威位于 `resources/SKILL.md`。复杂任务开始前读取它；当前交付执行代码位于 `resources/runtime/cbcc/delivery_export.py` 与 `resources/runtime/cbcc/delivery_workspace.py`。

## 最终交付硬合同
当用户要求完整跨境电商策划、Listing、内容、视觉策展、逐资产 Prompt、资产包或“完成当前商品项目”时，**纯聊天正文不是完成态**。必须物化可下载的人类交付 Artifact。

### FULL 项目深度合同（宿主不可改写成简版报告）
当请求同时覆盖 Product Truth / Strategy / Listing 或 Content / Visual / Asset / Prompt 等完整链路时，模式必须判定为 **FULL**。FULL 的九个决策域必须作为可见的人类交付对象进入 `index.html`；可以用适合 SaaS 的对象式导航/页面组织，但不能换成一套更短的自定义报告后声称等价。

九域必须具备真实决策深度，而不是标题存在：
1. **信息完整度、待确认清单、假设与决策日志**：信息域矩阵、最多10个关键问题、事实/假设边界、每个重大决定的依据/取舍/执行/指标。
2. **产品真实事实审计与卖点分级**：Fact → 真实卖点 → 可感知利益 → 情绪价值 → 不可宣称/Claim Boundary → A/B/C证据等级 → 来源/发布边界。C不得成为硬宣称。
3. **平台×区域×人群×族裔文化洞察**：回答为什么这个平台、区域、人群与文化语境；包含交叉性、语言/宗教/节庆/支付/物流/法规、包容性表征、禁忌/刻板印象与依据/假设。
4. **营销框架与核心策略**：定位、价值主张、信息层级、STP+JTBD、4P/内容漏斗；FULL 中 RACE=Research→Action→Communication→Evaluation。每条重要策略给依据+取舍+执行+指标，不堆概念。
5. **视觉总策略与拍摄执行**：风格/情绪板、构图、主辅背景文字色HEX及对比、CMF、灯光方向/CCT/光比/柔硬、镜头焦段、景别/机位、场景/道具、模特服化道、平台尺寸、镜头表；人物适用时执行肤色测光、深肤色暗部保护、反光板/柔光、发质/体型/年龄/残障与AI偏见控制。
6. **分平台内容矩阵**：平台/人群/选题/钩子/脚本结构/视觉形式/CTA/指标/RACE阶段/文化与禁忌，同时包含尺寸、时长、封面首帧、字幕、音乐版权、流量机制、落地页与UTM/等价归因；未知标待查证。
7. **RACE传播框架执行表**：Research / Action / Communication / Evaluation 四阶段，包含目标、关键动作、输出物、平台、文化校验、KPI、WHY。
8. **族裔文化适配检查表**：文化适配点、包容性表征、刻板印象/禁忌、校验结果、修改动作、WHY。
9. **合规/文化敏感/风险 + 评估/A-B + P0/P1/P2 + 下一步信息**：强监管Claim单列、测试假设、预算/周期取舍、自检（编造/WHY/文化/合规/指标/假设）。

**深度不等于堆字数。** 可以压缩重复说明，但不得压缩决策能力、证据边界、区域/人群洞察或执行参数。`resources/runtime/cbcc/delivery_contract.py` 的 FULL depth validation 是最低线；宿主自己写的报告不能低于它。

### Canonical Prompt 语义压缩 / 能力不压缩
逐资产 Prompt 可以比旧版更短，但只允许删除重复话术、内部 ID/RACE/KPI、与当前资产无关的 toolbox 字段。凡是已经被上游选择且会改变最终像素、摄影、合成或后期结果的决定，必须进入 Canonical Prompt 或明确绑定的 deterministic production instruction，包括适用的构图、产品占比/留白、镜头/视角、灯光、CMF、色彩管理、人物/肤色曝光、反光板/柔光、Product Fidelity、锁定文案区域与 editable/frozen layers。

每个激活资产完成前必须形成 **Prompt Consumption Audit**：`selected execution decisions → projected decisions → missing decisions`。missing 必须为 0 才能声称 Prompt 完成。人物/手/身体关系资产必须把包容性摄影 P0 变成可执行语言，不能只在总策划里出现。

完整交付至少包含：
- `index.html`：自包含、离线可打开、中文优先的 SaaS 式人类工作台；完整人类内容必须能在 HTML 中阅读。
- `00_PROJECT_HUB.md` 与 `HUMAN_DELIVERY.json`；Listing 在当前范围时包含 `01_LISTING_UPLOAD_READY.md`。
- `strategy/`：当前策略权威与可编辑源。
- `asset_packages/`：逐资产独立包，保留中文 Canonical Prompt、英文/目标模型 Prompt、Design Card、Photography/CMF/Composition、Product Fidelity、Copy、Parameter Trace、QA/来源等当前资产实际需要的对象。
- `DELIVERY_MANIFEST.json` 与最终 ZIP。

若当前宿主能执行 CBCC Runtime，使用 `delivery_export`/`cbcc export`。若 Runtime 未连接但宿主具有原生文件或 Artifact 生成能力，必须使用宿主能力生成等价交付，不得因为 Runtime 未部署就退化成聊天报告。**源码被打包在 resources 中不等于交付已经发生。**

## 人类工作区合同
- 默认交付语言为中文；目标市场可见文案保留目标语言，并提供中文释义/用途说明。
- 工作区按真实业务对象组织，不按固定流水线或 01→02→03 阶段组织。
- Strategy、Content、Visual、Listing、Prompt、Evidence 使用各自适合的交互与信息架构；不能只是同一个页面模板换标题。
- 单资产是对象工作区，可自由进入“决策 / Design Card、画面执行、摄影 / CMF、文案、Prompt、QA / 来源”等实际存在的对象视图；无固定先后顺序，不制造不存在的字段。
- HTML 必须包含完整人类交付；MD/JSON/TXT 是编辑与机器真源，不应成为阅读完整交付的前置条件。

## 商业与生产连续性
- 从用户目标、Product Truth、证据、目标市场/平台与当前交付范围开始，由 Agent 动态发现信息缺口并决定研究、内容、Surface、资产与创意方向。
- **FULL 与 TASK_SCOPED 分权**：FULL 执行上面的九域深度合同与 RACE 四阶段；TASK_SCOPED 局部任务才按当前目标动态选择框架/域。两者都不规定固定图片数、方向数、页面模板或摄影字段配额。
- 不把固定 9 图/12 图、固定方向数、通用页面流水线当作创意/商业权威；但不得用“动态”作为删除 FULL 已要求能力的理由。
- 商品身份、包装、材质、颜色、结构与可见事实必须 source-bound；Claim、Compliance、平台当前证据、Review 与 Completion 按 `resources/SKILL.md` 和 Runtime 合同执行。
- 摄影、灯光、CMF、构图、色彩管理、商品保真、可编辑/冻结层若已参与策划并与当前资产相关，必须一路投影到该资产的 Design Card、Parameter Trace 与 Canonical Prompt；不能只存在于策划文字里。
- Product Name、Asset ID、RACE/KPI 等内部管理元数据不得污染最终生成模型 Prompt，除非它们本身就是消费者可见内容或执行必需事实。

## 完成判定
在声称“完成”之前，检查真实交付物而不是源码文件名：
1. `index.html` 实际存在且可读；
2. HTML 为中文优先且不是报告式长页/流水线；
3. 当前范围的策略、Listing、内容、视觉与资产对象完整进入交付；
4. 每个资产的中英文 Prompt 与其实际策划参数连续，Prompt Consumption Audit 的 `missing decisions = 0`；
5. FULL HTML 可见包含九域决策对象，卖点/区域/人群/文化/视觉摄影/内容矩阵/RACE/风险等达到 decision-depth，不是几句摘要；
6. ZIP 中包含 HTML、Manifest、可编辑源和逐资产包。

需要 Provider、Plugin HTTP Action 或 MCP tool 时，必须使用实际运行且经过验证的宿主/部署；不得把打包源码伪报为远程工具连接。
'''


def openai_yaml() -> str:
    return '''interface:
  display_name: Cross-Border Commerce Creative
  short_description: 跨境电商策略、内容、创意与完整交付
  default_prompt: 基于当前商品资料、真实商品真源和目标市场/平台完成跨境电商工作。若用户要求策略+Listing/内容+视觉/资产+逐资产Prompt的完整链路，必须判定 FULL，执行九域决策深度合同和 Prompt Consumption Audit，并生成中文优先 index.html + 可编辑源 + 逐资产包 + ZIP；不得用自定义简版报告替代。局部任务才使用 TASK_SCOPED 动态裁剪。
policy:
  allow_implicit_invocation: true
'''


def usage_cn() -> str:
    return '''# 使用说明

1. 复杂任务先以 `resources/SKILL.md` 作为完整权威。
2. GitHub `main` 是唯一源码真源；Plugin/Skill 是派生发行物。
3. 完整商品任务必须生成真实 Artifact：`index.html` + 项目交付目录 + 逐资产包 + `DELIVERY_MANIFEST.json` + ZIP。
4. 人类交付默认中文，目标市场可见文案保留目标语言并配中文释义。
5. Agent 根据当前 Commerce Goal、Product Truth、证据和 Surface 动态决定研究、策略、内容、资产与创意方向。
6. Plugin 内含 Runtime 源码 resources，但源码存在不等于已经执行交付或连接远程 Provider。
'''


def cli_usage_cn() -> str:
    return '''# Runtime CLI

完整本地 Runtime 使用仓库/Runtime Release。

```bash
python bin/cbcc.py --help
bash tests/run_smoke.sh
PYTHONPATH=runtime python -m cbcc.cli export --project-dir <project> --output <delivery-dir-or-zip>
PYTHONPATH=runtime python -m cbcc.plugin_http_cli --bind 127.0.0.1 --port 8787
PYTHONPATH=runtime python -m cbcc.mcp_stdio_cli
```

`cbcc export` 会生成完整人类交付目录与 ZIP，不再只是 JSON manifest。
'''


def copy_repo_resources(dest: Path) -> None:
    for src in sorted(ROOT.rglob('*')):
        if not should_copy(src):
            continue
        rel = src.relative_to(ROOT)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)


def zip_tree(source_dir: Path, output: Path, enclosing_dir: bool) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source_dir.rglob('*')):
            if not path.is_file():
                continue
            rel = path.relative_to(source_dir)
            arcname = Path(source_dir.name) / rel if enclosing_dir else rel
            zf.write(path, arcname)


def build(output_dir: Path) -> dict:
    version = semver()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = plugin_manifest(version)

    with tempfile.TemporaryDirectory(prefix='cbcc-release-') as td:
        tmp = Path(td)
        plugin_root = tmp / PLUGIN_NAME
        skill_root = plugin_root / 'skills' / PLUGIN_NAME
        resources = skill_root / 'resources'

        write_text(plugin_root / 'plugin.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        write_text(plugin_root / '.codex-plugin' / 'plugin.json', json.dumps(compatibility_manifest(manifest), ensure_ascii=False, indent=2) + '\n')
        write_text(skill_root / 'SKILL.md', skill_wrapper(version))
        write_text(skill_root / 'agents' / 'openai.yaml', openai_yaml())
        write_text(skill_root / 'references' / 'USAGE_CN.md', usage_cn())
        write_text(skill_root / 'references' / 'CLI_USAGE_CN.md', cli_usage_cn())
        copy_repo_resources(resources)

        plugin_zip = output_dir / f'{PLUGIN_NAME}-plugin-v{version}.zip'
        zip_tree(plugin_root, plugin_zip, enclosing_dir=True)

        standalone = tmp / f'{PLUGIN_NAME}-skill'
        shutil.copytree(skill_root, standalone / PLUGIN_NAME)
        skill_zip = output_dir / f'{PLUGIN_NAME}-skill-v{version}.zip'
        zip_tree(standalone / PLUGIN_NAME, skill_zip, enclosing_dir=True)

    release = {
        'version': version,
        'source_version': (ROOT / 'VERSION').read_text(encoding='utf-8').strip(),
        'artifacts': [
            {'file': plugin_zip.name, 'sha256': sha256(plugin_zip), 'bytes': plugin_zip.stat().st_size},
            {'file': skill_zip.name, 'sha256': sha256(skill_zip), 'bytes': skill_zip.stat().st_size},
        ],
        'delivery_contract': {
            'complete_html_required': True,
            'artifact_required_for_full_task': True,
            'object_based_asset_workspace': True,
            'chat_only_completion_forbidden': True,
            'full_nine_domain_decision_depth_required': True,
            'prompt_consumption_audit_required': True,
            'host_custom_short_report_cannot_substitute_full_delivery': True,
        },
    }
    write_text(output_dir / 'release_manifest.json', json.dumps(release, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(release, ensure_ascii=False, indent=2))
    return release


def main() -> int:
    ap = argparse.ArgumentParser(description='Build CBCC Agent Plugin and standalone Skill release archives from the current GitHub source tree.')
    ap.add_argument('--output-dir', default=str(ROOT / 'dist'))
    args = ap.parse_args()
    build(Path(args.output_dir).resolve())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
