# CBCC HUMAN WORKSPACE + PROMPT CONTINUITY LOCK — v0.6.54

## 0. 事故边界
本锁解决真实回归：资产包中的 `05_prompt_CN.txt` / `06_prompt_EN.txt` 仍存在，但 Human `index.html` 在一次“硬规则修复”中被重新手写，导致 Prompt 从人类交付消失，同时成熟 routed workspace 被固定九域 section 报告替代。

因此：**文件存在不等于人类交付存在；内容修复不允许顺手重造 Workspace。**

本锁优先级高于普通 HTML 重构、语言修复、合规修复、九域补齐、媒体修复和摘要优化。

## 1. Mature Workspace 是稳定底座
FULL / 高密度商品项目默认保留经过验证的 v0.6.36 routed interaction floor，并由 `cbcc-commercial-v1` 商业工作台壳承载。

除非用户明确要求 redesign / 新 Shell major version，否则不得改变以下交互底座：
- 一次只显示一个一级工作面；
- 当前项目真实业务对象动态形成 route，不以九域固定菜单替代；
- module subview / lens；
- 独立 `asset/<id>` 资产详情；
- Prompt 工作面；
- 逐资产 Prompt lens；
- search / copy / back / hash route；
- responsive navigation；
- print / PDF projection；
- 目标市场 exact copy、中文释义与可生产对象直接在人类工作台可用；
- standalone-safe media。

**九域不是九个页面，也不是九个固定 section。** 九域只定义完整度；信息架构继续由当前项目真实对象作者化。

## 2. Runtime-first materialization
当 packaged runtime 可以执行时，FULL 交付和已有项目修复必须 **runtime-first**，优先使用成熟消费者：
- `resources/runtime/cbcc/delivery_export.py`；
- `resources/runtime/cbcc/delivery_workspace.py`；
- `resources/runtime/cbcc/delivery_html.py`；
- `resources/runtime/cbcc/commercial_workspace_shell.py`。

它们已经承担：routed workspace、资产详情、Prompt 投影、商业 shell、语言/媒体投影和最终 package 生成。

Host 不得因为需要补中文、补九域、补合规、补媒体、补业务密度，就绕过这些消费者重新手写另一套 `index.html`。

## 3. Existing package repair
修复已有 FULL package 时：
1. 先定位责任对象/数据层；
2. 修 Product Truth / Strategy / Listing / Culture / Visual / Asset / Prompt 等真实对象；
3. 如果 runtime 可用，用同一成熟 renderer 重新物化；
4. 如果 runtime 真不可用，只允许对现有 HTML/data 做局部、结构保持式 patch；
5. **不得重写 index.html** 或另造固定 Dashboard / Card Wall / 九域报告壳；
6. 修复前后必须做 Surface Continuity 对比。

“内容更完整”不能成为版式/交互退化的理由。

## 4. Prompt human-projection continuity
只要某个资产包存在 `05_prompt_CN.txt` 或 `06_prompt_EN.txt`，Human HTML 必须真实消费，而不是要求用户去文件夹寻找。

生产资产的 HTML 至少保留：
- `Model Prompt CN` / 中文模型提示词；
- `Model Prompt EN` / 英文模型提示词；
- copy action；
- 与当前 asset 的绑定；
- 逐资产 `asset/<id>` 详情中的 Prompt lens。

成熟 runtime 还应保留独立 Prompt 工作面，让多个资产可切换查看 Prompt。

以下均 FAIL：
- Prompt 文件在 ZIP 中，但 `index.html` 没有 CN/EN Prompt；
- 只有全局 Prompt 摘要，没有逐资产 Prompt；
- 只有逐资产文件路径，没有可读 Prompt；
- Prompt 被 raw JSON Inspector 取代；
- Prompt 因中文/合规/UI 修复被删出 Human HTML。

## 5. Repair cannot redesign IA
语言、九域、Product Truth、合规、媒体、商业密度等修复只能改变对应业务对象和必要的局部呈现；不得默认改变 top-level IA、全局导航、路由模型、资产详情结构或 Prompt 访问方式。

只有用户明确提出“重做界面 / redesign / 换交互体系”时才允许改变全局壳；即使如此也必须保留完整业务对象与 Prompt 可达性。

## 6. Exact-heading validation cannot drive layout
机器检查可验证九域语义对象，但不得要求 Human HTML 使用固定标题、固定页数、固定编号或固定 DOM section。

尤其禁止为了满足“九域标题存在”而：
- 创建 `01...09` 固定导航；
- 把全部内容平铺为长页面；
- 用固定九域 section 覆盖 Product / Market / Strategy / Listing / Visual / Assets / Prompts 等成熟业务 route；
- 改掉 `asset/<id>` 详情。

验收应检查内容语义和可达性，不检查固定版式。

## 7. Surface Continuity acceptance
最终 package 在打 ZIP 前以及重新解压后都必须验证：
- `cbcc-commercial-v1` 或明确兼容的成熟 routed floor 存在；
- 一级正常浏览一次只激活一个 primary work surface；
- `asset/<id>` 资产详情对所有生产资产可达；
- 有 Prompt 文件的资产，其 CN/EN Prompt 在 Human HTML 可达；
- Prompt 工作面 / per-asset Prompt lens 至少满足当前成熟 runtime 能力；
- search/copy/back/hash、responsive、print/PDF 没有因修复消失；
- 未出现固定九域 replacement shell。

参考终检：`scripts/check_v0654_workspace_prompt_continuity.py`。

## 8. Completion wording
以下任一条件存在，不得声称 FULL / 修复完成：
- Prompt 文件存在但 Human HTML 不可见；
- `asset/<id>` 详情消失；
- `cbcc-commercial-v1` / mature routed workspace 被固定报告壳替代；
- 修复未经 Surface Continuity 检查；
- 九域补齐导致全局 IA 改写；
- 用户没有要求 redesign，却发生 top-level layout / navigation / route model 变化。
