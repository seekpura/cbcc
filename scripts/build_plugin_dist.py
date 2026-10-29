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
    '基于当前对话、上传资料和必要的最新公开信息，完成当前商品的跨境电商策略、Listing、内容、视觉策展与逐资产生产对象。该请求属于 FULL 商品项目：必须执行九域决策深度合同、具体参数连续性审计（生产准备度不阻断项目），并物化完整中文优先 index.html + 可编辑源 + 逐资产包 + ZIP。九域是完整度合同，不是固定页面模板；不得用自定义短报告替代。人类交付以中文为基础语言；Listing 字段标题中文在前，平台原始 key 仅作次级技术标识；所有英文/马来文/阿语等目标市场外文 Listing、内容与资产可见文案必须在同一对象提供中文释义/用途。逐资产生产必须分离 Model Prompt CN、Model Prompt EN、Visible Copy Block 与 Production / Assembly Notes；英文 Model Prompt 的执行说明保持英文，目标市场原文可按实际可见 copy 保留。 FULL 视觉资产必须先完成 Production Parameter Closure：所有已选且会改变生成结果的构图/相对位置/尺度/占画/焦点路径/负空间/摄影/灯光/CMF/材质/人物/视频参数都要被 Model Prompt 实际消费。真实商品需要出现在画面时，将真实商品图作为强模型 Reference Input 原生生成完整最终成图并锁定商品身份；只有明确要求原始源图像素层一丝不动时才使用 EXACT_PIXEL_COMPOSITE。',
    '只做当前 SKU 的目标市场/平台视觉资产策展和逐资产生产对象，本轮不生成图片；建立不受平台槽位总数限制的资产宇宙，Hero/卖点/广告/A+/PDP/详情/店铺/社媒/视频均可有多方案与测试轮换池；平台最多9图/7图仅约束同时上线集合。真实商品默认以参考图作为强模型输入原生生成完整成图并锁定产品身份，只有明确要求原始像素层不变时才使用 EXACT_PIXEL_COMPOSITE。先建立商品真源、购买决策、创意机会和动态 Surface，由 Agent 逐资产决定视觉载体、产品是否出现、构图、空间关系、文字渲染路线与相关执行参数。把当前资产已选且会改变结果的具体构图/相对位置/尺度/占画/焦点路径/留白/摄影机几何/对焦景深/灯光几何/CCT-WB/光比/阴影高光/反射偏振/Prelight/CMF材质/色彩管理/finishing/人物/动态参数投影到正确对象；摄影式路线恢复0.6.6可执行参数深度，缺值时不要把Prompt标READY。',
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
                    'longDescription': '跨境电商 Commerce Agent：从 Product Truth、证据与平台约束出发，动态完成研究、SKU/Offer、策略、Listing、内容、视觉摄影、图片/视频资产、Model-Native Prompt、可见文案、生产装配说明、生产、Review 与学习闭环。完整任务必须产出中文优先的人类交付 Artifact，包括自包含 HTML 工作台、逐资产包与 ZIP；不得以纯聊天文本替代最终交付。',
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
description: 用于跨境电商 Product Truth、动态研究、SKU/Offer、Listing/Search、策略、内容、视觉摄影、图片/视频资产、逐资产 Model Prompt CN/EN、Visible Copy、Production / Assembly Notes、生产、Review、学习闭环与完整人类交付；默认中文，任务范围与资产结构动态决定。
---
# Cross-Border Commerce Creative v{version}

## Agent Creative Authority
商业策略、资产策展与视觉设计由宿主 Agent 主导；Runtime 只负责 validate / serialize / compile / trace / execute / package / test。逐资产必须由 Agent 决定视觉载体、产品是否出现及其角色、主体/动作/环境/道具、空间语法与相关时的摄影/灯光/CMF。缺失 Art Direction 时返回 Agent 补决策，不得自动补 packshot、centered hero、left-text/right-product 或其他模板。Product Reference/Fidelity 不等于 Product Presence。

## Production Parameter Closure + Creative Depth
FULL 视觉/视频资产必须由 Agent 完成可执行 Art Direction 并闭环所有会改变结果的具体参数。摄影式路线恢复 v0.6.6 深度：焦段/镜头、工作距离、机位高度与角度、景别、对焦/景深、相关时快门/ISO、key/fill/negative/rim、modifier、CCT/WB、光比、阴影/高光、反射/偏振、Prelight、CMF/材质、色彩管理与 finishing；人物再加入肤色曝光与代表性执行。真实商品需要出现时，真实商品图必须作为强 Reference Input 进入生成模型，商品在完整最终画面中原生生成并保持包装几何、比例、结构、Logo、品牌文字、标签版式、可辨识印刷、主色和材质身份。EXACT_PIXEL_COMPOSITE 只用于用户明确要求源图像素层不可改变的特殊路线。平台最大图片数只限制同时上线集合，不限制 Asset Universe；若一组资产只是暖白底、左右分区、小角落商品、柔光的重复变体，返回 Agent 重新策展/设计。完整 Inspector 展示完整 Art Direction 与 Production Parameter Closure，摘要字段不得替代设计卡。

## Dynamic Asset Universe + Native Product Reference
资产总量由购买决策、Surface、创意假设、测试与运营需求决定，不受平台 Gallery 槽位总数限制。Hero、卖点、广告、A+/PDP/详情、Store/Banner、Social/Creator、Video 等均可存在多方案；同一消费者问题和同一 Surface 也允许 H01/H02/H03 等显式 Variant，不得因为 question/surface/family 相同而合并。人类工作区区分上线候选、测试池、轮换池、广告、PDP/A+详情、归档与其他资产。

当 Product Presence 要求真实商品可见时，真实商品图默认作为强模型 Reference Input，使用 `REFERENCE_GUIDED_NATIVE_LOCK` 原生生成完整最终画面中的商品，并保持真实商品身份；`EXACT_PIXEL_COMPOSITE` 仅在用户明确要求源图像素层不可改变时启用。

## Dynamic Asset Universe + Native Product Reference
资产总量由购买决策、Surface、创意假设、测试与运营需求决定，不受平台 Gallery 槽位总数限制。Hero、卖点、广告、A+/PDP/详情、Store/Banner、Social/Creator、Video 等均可存在多方案；同一消费者问题和同一 Surface 也允许 H01/H02/H03 等显式 Variant，不得因为 question/surface/family 相同而合并。人类工作区区分上线候选、测试池、轮换池、广告、PDP/A+详情、归档与其他资产。

当 Product Presence 要求真实商品可见时，真实商品图默认作为强模型 Reference Input，使用 `REFERENCE_GUIDED_NATIVE_LOCK` 原生生成完整最终画面中的商品，并保持真实商品身份；`EXACT_PIXEL_COMPOSITE` 仅在用户明确要求源图像素层不可改变时启用。

## Model-Native Prompt Contract
逐资产生产必须分离 Model Prompt CN、Model Prompt EN、Visible Copy Block 与 Production / Assembly Notes。英文 Model Prompt 的执行说明保持英文，目标市场原文可准确保留，中文释义放在人类交付/Copy Block；不要把 deterministic typography、renderer layer、machine contract、audit/provenance 等 Runtime 工程词塞进模型 Prompt。文字由模型直接生成还是后期装配由 Agent/生产路线显式决定，不做全局默认。FULL 交付不得为缩短篇幅而压扁 Visual Master、内容矩阵或逐资产 Art Direction。

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
5. **视觉总策略与按需媒介/拍摄执行**：先由 Agent 确定视觉载体、产品 presence/role、构图、空间节奏、证据层级、主辅背景文字色HEX及对比、CMF/材质与平台尺寸；只有真实摄影/摄影式生成路线才继续策划灯光方向/CCT/光比/柔硬、镜头焦段、景别/机位、Prelight与镜头表；人物适用时执行肤色测光、深肤色暗部保护、反光板/柔光、发质/体型/年龄/残障与AI偏见控制。
6. **分平台内容矩阵**：平台/人群/选题/钩子/脚本结构/视觉形式/CTA/指标/RACE阶段/文化与禁忌，同时包含尺寸、时长、封面首帧、字幕、音乐版权、流量机制、落地页与UTM/等价归因；未知标待查证。
7. **RACE传播框架执行表**：Research / Action / Communication / Evaluation 四阶段，包含目标、关键动作、输出物、平台、文化校验、KPI、WHY。
8. **族裔文化适配检查表**：文化适配点、包容性表征、刻板印象/禁忌、校验结果、修改动作、WHY。
9. **合规/文化敏感/风险 + 评估/A-B + P0/P1/P2 + 下一步信息**：强监管Claim单列、测试假设、预算/周期取舍、自检（编造/WHY/文化/合规/指标/假设）。

**深度不等于堆字数。** 可以压缩重复说明，但不得压缩决策能力、证据边界、区域/人群洞察或执行参数。`resources/runtime/cbcc/delivery_contract.py` 的 FULL depth validation 是最低线；宿主自己写的报告不能低于它。

### Canonical Prompt 语义压缩 / 能力不压缩
逐资产 Prompt 可以比旧版更短，但只允许删除重复话术、内部 ID/RACE/KPI、与当前资产无关的 toolbox 字段。凡是已经被上游选择且会改变最终像素、摄影、合成或后期结果的决定，必须进入 Canonical Prompt 或明确绑定的 deterministic production instruction，包括适用的构图、产品占比/留白、镜头/视角、灯光、CMF、色彩管理、人物/肤色曝光、反光板/柔光、Product Fidelity、锁定文案区域与 editable/frozen layers。

当当前任务需要 Prompt/生图/Provider 执行时，形成 **Prompt Consumption Audit**：`selected execution decisions → projected decisions → missing decisions`。它是生产准备度诊断，不是项目/资产完整度的全局阻断 Gate；missing 可以标记 `NEEDS_PROMPT_WORK`。人物/手/身体关系资产必须执行包容性表征；真实摄影路线再消费测光、Prelight、柔光等摄影参数。

完整交付至少包含：
- `index.html`：自包含、离线可打开、中文优先的 SaaS 式人类工作台；完整人类内容必须能在 HTML 中阅读。
- `00_PROJECT_HUB.md` 与 `HUMAN_DELIVERY.json`；Listing 在当前范围时包含 `01_LISTING_UPLOAD_READY.md`。
- `strategy/`：当前策略权威与可编辑源。
- `asset_packages/`：逐资产独立对象包，至少保留中文人类设计卡、策略、视觉/版式、Copy、来源/QA 与当前实际需要的执行对象；Canonical Prompt、生图指导、摄影合同等属于可选生产附件，缺失或未就绪不得让资产本身变成不完整。
- `DELIVERY_MANIFEST.json` 与最终 ZIP。

若当前宿主能执行 CBCC Runtime，使用 `delivery_export`/`cbcc export`。若 Runtime 未连接但宿主具有原生文件或 Artifact 生成能力，必须使用宿主能力生成等价交付，不得因为 Runtime 未部署就退化成聊天报告。**源码被打包在 resources 中不等于交付已经发生。**

## Product Reference / Production Authority
- 用户提供的真实商品图/包装图在 Product Presence 需要真实商品可见时，默认作为**强模型 Reference Input**：模型原生生成完整最终画面中的同一真实商品身份，可匹配作者化机位/透视/光线/景深/场景，但不得擅自改包装几何、比例、泵头/滴管/瓶盖结构、Logo、品牌文字、标签版式、可辨识印刷、主色或材质身份。
- `REFERENCE_GUIDED_NATIVE_LOCK` 是常规真实商品生成保真路线；`EXACT_PIXEL_COMPOSITE` 仅在用户明确要求“原始源图像素层不可改变/必须保留 exact pixels”时启用。Product Presence=ABSENT/FORBIDDEN 时，真实商品图只做 Truth/Identity Reference，不强行把商品放进画面。
- Prompt、生图方案、摄影/灯光/Prelight 是能力与生产准备度，不是项目或资产完整度的全局 Gate。
- 七大第一类工具与其他已集成参考能力必须保持可调用、可消费、可追踪；按任务相关性激活，不变成固定七步流水线。

## 人类工作区合同
- **中文是默认的人类交付基础语言**。策略、解释、WHY、风险、摄影策划、UI 与字段标题优先中文；用户明确要求其他交付语言时才覆盖。
- **Listing 人类字段标题必须中文在前**。平台原始英文/外文字段 key、类目 ID、SKU、GTIN 等只作为次级技术标识；未知平台字段若没有语义明确的中文标题，不得把原 key 直接当唯一标题交付。
- **任何英文/马来文/阿语等目标市场外文内容都必须在同一人类交付对象提供中文释义/用途**，覆盖 Listing 标题/描述/卖点/搜索词说明、广告/内容文案、资产 headline/subhead/CTA/badge/caption/hook/script overlay 等。搜索词可解释搜索意图而非机械逐词翻译。
- **逐资产中文解释不可缺失**：每个资产保留目标市场原文，同时在同一资产对象/中文设计卡说明中文含义、为什么使用、如何进入画面；英文/目标模型 Prompt 必须与中文 Canonical Prompt 成对存在。
- 品牌、SKU、GTIN、URL、HEX、INCI、平台官方字段 key 等专名/技术值可以保留原文，但必须有中文字段名、用途或角色说明。
- 缺中文主标题、缺外文中文 companion、缺中文资产设计卡或只有英文 Prompt 时，均不是完成态；真实 Runtime 导出必须由 `HUMAN_LANGUAGE_AUDIT.json` 阻断，宿主原生 Artifact 交付也必须执行同等检查。
- 工作区按真实业务对象组织，不按固定流水线或 01→02→03 阶段组织。
- Strategy、Content、Visual、Listing、Prompt、Evidence 使用各自适合的交互与信息架构；不能只是同一个页面模板换标题。
- 单资产是对象工作区，可自由进入“决策 / Design Card、画面执行、摄影 / CMF、文案、Prompt、QA / 来源”等实际存在的对象视图；无固定先后顺序，不制造不存在的字段。
- HTML 必须包含完整人类交付；MD/JSON/TXT 是编辑与机器真源，不应成为阅读完整交付的前置条件。

## 商业与生产连续性
- 从用户目标、Product Truth、证据、目标市场/平台与当前交付范围开始，由 Agent 动态发现信息缺口并决定研究、内容、Surface、资产与创意方向。
- **FULL 与 TASK_SCOPED 分权**：FULL 执行上面的九域深度合同与 RACE 四阶段；TASK_SCOPED 局部任务才按当前目标动态选择框架/域。两者都不规定固定图片数、方向数、页面模板或摄影字段配额。
- 不把固定 9 图/12 图、固定方向数、通用页面流水线当作创意/商业权威；但不得用“动态”作为删除 FULL 已要求能力的理由。
- 商品规格、成分、功能、认证、Claim 与其他已验证事实必须 source-bound；产品图、包装图和源文件默认是设计参考，可按已选创意方向重绘/重渲染/风格化，除非当前子任务显式锁定源图。Claim、Compliance、平台当前证据、Review 与 Completion 按 `resources/SKILL.md` 和 Runtime 合同执行。
- 摄影、灯光、CMF、构图、色彩管理、商品保真、可编辑/冻结层若已参与策划并与当前资产相关，必须一路投影到该资产的 Design Card、Parameter Trace 与 Canonical Prompt；不能只存在于策划文字里。
- Product Name、Asset ID、RACE/KPI 等内部管理元数据不得污染最终生成模型 Prompt，除非它们本身就是消费者可见内容或执行必需事实。

## 完成判定
在声称“完成”之前，检查真实交付物而不是源码文件名：
1. `index.html` 实际存在且可读；
2. HTML 为中文优先且不是报告式长页/流水线；
3. 当前范围的策略、Listing、内容、视觉与资产对象完整进入交付；
4. 若当前任务需要 Prompt / 生图 / Provider 执行，则显示 Prompt Consumption Audit 作为生产准备度；`missing decisions` 形成 `NEEDS_PROMPT_WORK`，但不得阻止资产、策略或项目人类交付完成；
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
            'prompt_consumption_blocks_project_completion': False,
            'product_source_default_reference_guided': True,
            'photorealism_default_required': False,
            'seven_agent_capability_continuity_required': True,
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
