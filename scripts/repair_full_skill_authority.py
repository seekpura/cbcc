#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'SKILL.md'
MARKER='## FULL vs TASK_SCOPED Delivery Authority — current precedence'
BLOCK='''## FULL vs TASK_SCOPED Delivery Authority — current precedence
- **FULL Commerce Project / FULL Strategy / End-to-End 商品项目**：当用户明确要求完整商品策略、完整跨境电商项目、端到端交付，或请求同时覆盖 Product Truth + Strategy + Listing/Content + Visual/Asset/Prompt 等完整链路时，执行本 Skill 的 FULL 硬合同。FULL 必须物化 9 个决策域：信息完整度/假设日志、产品事实与 A/B/C 证据、平台×区域×人群×族裔文化洞察、营销核心策略、视觉/摄影/CMF、分平台内容矩阵、RACE 执行表、族裔文化适配检查表、合规/风险/评估/P0-P1-P2。RACE=Research → Action → Communication → Evaluation 作为传播流程骨架；STP+JTBD 定策略，AIDA/FABE 定内容结构，4P/Funnel 定转化。C 级证据不得形成硬宣称。
- **TASK_SCOPED 局部任务**：当用户只要求 Listing、单个资产、Prompt、视觉审查、局部研究、某个 Surface 或其他窄范围时，继续使用 v0.6.21–0.6.29 的动态 Scope / Decision Authority；不为了“系统会这些能力”强塞 9 个域、RACE、固定框架、固定资产数或未来工作。
- **两者不是冲突**：FULL 的 9 个域是“决策覆盖与交付完整度”合同，不是固定页面模板、固定章节篇幅、固定图片数、固定方向数或流水线 UI。HTML/工作区仍按真实业务对象设计；资产数量、页面组织、摄影字段和创意方向仍由当前商品、平台、市场、人群、证据和购买决策动态产生。
- FULL 与 TASK_SCOPED 都必须保持 Product Truth、Claim/Compliance、证据、Photography/CMF、Product Fidelity、Prompt、Review/Revision/Hash lineage；动态化不得通过删除既有能力换取简洁。
- 完整任务的完成态必须包含真实人类交付 Artifact（自包含 `index.html` + 可编辑源 + 逐资产包 + `DELIVERY_MANIFEST.json` + ZIP）；源码存在或聊天正文不构成 FULL 完成。

'''


def main()->int:
    text=PATH.read_text(encoding='utf-8')
    if MARKER in text:
        print('SKILL authority already reconciled')
        return 0
    anchor='## v0.6.29 Final Stabilization — 当前主权威\n'
    if anchor not in text:
        raise SystemExit('SKILL anchor not found')
    text=text.replace(anchor,BLOCK+anchor,1)
    PATH.write_text(text,encoding='utf-8')
    print('SKILL FULL vs TASK_SCOPED authority reconciled')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
