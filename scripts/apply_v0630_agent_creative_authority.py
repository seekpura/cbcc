from __future__ import annotations

from pathlib import Path


MARKER = '## Agent Creative Authority — highest current precedence'

SECTION = r'''
## Agent Creative Authority — highest current precedence
- **本节高于下方所有会把 Runtime heuristics、Surface、intent、reference 或方向级默认值解释成创意权威的历史说明。** Product Truth、用户明确锁定、平台/法规硬约束、Claim 证据和目标输出技术边界继续是硬约束；商业策略、资产策展和视觉设计由宿主 Agent 主导。
- 对 FULL 商品项目以及任何要求视觉策展 / 资产规划 / 商品图 / 视频 / Prompt / Production 的任务，宿主 Agent 是 **Portfolio Curator + Creative Director + Per-Asset Art Director**。Agent 决定资产是否存在、是否合并/省略、信息载体、产品是否出现及其角色、主体/动作/环境/道具、空间语法/尺度/焦点路径/留白、证据层级，以及相关时的摄影/灯光/CMF/人物/生产路线。
- Python / Runtime 的创意职责严格降为 **validate → serialize → compile → trace → execute → package → test**。Runtime 可以保存和校验 Agent 已做出的设计决策，但在 Agent authority 激活时不得原创 Product Presence、Subject、Composition、Camera、Lighting、CMF、Layout 或“为了完整”添加资产。
- **缺设计决策必须回到 Agent。** 逐资产 Art Direction 或 Product Presence 未解决时，使用 `AUTHOR_PER_ASSET_ART_DIRECTION` / `AGENT_ART_DIRECTION_REQUIRED` / `UNRESOLVED_AGENT_DECISION` 等显式状态；不得用 centered hero、left-text/right-product、card grid、podium、generic lifestyle、packshot 或 intent→layout fallback 自动补洞。
- **Product Presence 与 Product Fidelity 分离。** 商品源文件可以是 `TRUTH_REFERENCE_ONLY` 而画面完全没有商品。每张视觉资产由 Agent 显式决定 `HERO_REQUIRED / REQUIRED / SUPPORTING / DETAIL_ONLY / OPTIONAL→PRESENT|ABSENT / FORBIDDEN / NOT_APPLICABLE`（只使用当前任务需要的状态）。`FORBIDDEN` 时下游不得出现 packshot、corner product、ghost silhouette、podium product 或 product layer。
- **Surface 不是创意权威。** Surface architecture 可以给 representation / copy / product-usefulness 的兼容建议，但 `authoritative_for_generation=false`；逐资产 Agent Art Direction 才能确定真实 product presence、visual carrier 和空间设计。
- **Direction 是共享系统，不是页面模板。** Direction 只提供可共享的 thesis / continuity tokens / color-type-material principles 等；不得覆盖单资产已作者化的 Art Direction。相邻资产可以共享系统，但 composition、product role、subject、evidence plane、scale、density、camera/view 和媒介表达应按各自购买问题动态设计。
- Creative Opportunity 和 Direction 数量没有默认配额。Agent 可以形成一个明显正确的方向，也可以在不确定性或机会空间需要时扩展；停止条件是新增探索不再可能改变重要商业/创意决策，而不是 6–12 / 3–5 / 固定多方向数量。
- **摄影是工具，不是母模板。** Camera / lens / light / Prelight / CMF 只有在当前 carrier 和 production route 真正需要时才由 Agent 策划并贯穿执行；Graphic / Source Evidence / Native Text / Illustration / 3D 等资产不得为了“专业感”被强制塞摄影参数。
- Prompt Compiler 是 compiler，不是 designer。唯一允许的链路是 `Product Truth + Commerce Strategy → Agent Portfolio Curation → Creative Direction → Per-Asset Art Direction → Canonical Prompt → Renderer/Provider → Agent Review/Revision`。Prompt 只能压缩和投影已经选定、会改变生产结果的参数，不能反向发明设计。
- 人类交付仍默认中文优先；目标市场可见文案可使用当地语言，但在人类工作区/资产说明中必须有合适的中文释义与用途说明。九域是 FULL 的决策深度合同，不是固定页面、固定资产、固定 UI 或固定视觉模板。
'''.strip()


def main() -> None:
    path = Path('SKILL.md')
    text = path.read_text(encoding='utf-8')
    if MARKER in text:
        print('Agent Creative Authority section already present; no change.')
        return
    anchor = '## FULL vs TASK_SCOPED Delivery Authority — current precedence'
    if anchor not in text:
        raise SystemExit(f'Cannot find insertion anchor: {anchor}')
    text = text.replace(anchor, SECTION + '\n\n' + anchor, 1)
    path.write_text(text, encoding='utf-8')
    print('Inserted Agent Creative Authority highest-precedence section into SKILL.md')


if __name__ == '__main__':
    main()
