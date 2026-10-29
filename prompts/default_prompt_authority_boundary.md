# Default Prompt Is Not Authority — v0.6.44

## Highest-precedence authority-source boundary
`defaultPrompt` is not a business-policy layer and must not duplicate CBCC product rules. Fixed product behavior belongs in the Host Skill and Canonical Skill, with detailed contracts in canonical prompts/references/runtime tests.

From v0.6.44 onward, the plugin manifest MUST NOT carry business rules in `defaultPrompt`. The preferred release form omits `defaultPrompt` entirely. Selecting/invoking the plugin is sufficient to load the current Host Skill / Canonical Skill authority.

## Fixed CBCC product principles live here, not in manifest prompts
The current Skill authority permanently owns these cross-version principles:
- 人类交付中文优先；目标市场外文原文保留，并在同一人类对象提供中文释义 / 用途；
- FULL / 高密度项目保留成熟项目化交互：真实对象 route、局部 subview/lens、独立 asset detail、搜索、复制、响应式与打印/PDF；
- FULL 商业深度、九域完整度合同与七大一等 Commerce capabilities 按相关性保留；
- Asset Universe 动态生成且不受平台 Live/Activation Set 槽位总数限制；
- Agent 是 Portfolio Curator + Creative Director + Per-Asset Art Director，创意策展和逐资产设计不能被 Runtime 模板替代；
- 每个生产资产保留完整 Human Design Card、Model Prompt CN、Model Prompt EN、Visible Copy Block、Production / Assembly Notes、Truth/Reference/Claim、QA/repair 等相关对象；
- 升级只能做加法；新的版本权威可以加强或修复实现，但不能通过 manifest prompt 另建一套平行规则、覆盖 Canonical 或偷偷删能力。

## Single source of truth
Priority is:
1. current Host Skill;
2. current Canonical Skill (`resources/SKILL.md`);
3. canonical prompt/reference contracts and runtime behavior/tests;
4. task/user-specific instructions that do not conflict with higher hard truth/safety/platform constraints.

The plugin manifest is packaging/discovery metadata. It must not become a second Canonical Skill.

## Release acceptance
A current release fails this boundary if:
- `plugin.json` or `.codex-plugin/plugin.json` contains a long business `defaultPrompt` list;
- a product rule exists only in `defaultPrompt` and not in Host/Canonical authority;
- Host and Canonical disagree on current fixed principles;
- removing `defaultPrompt` changes required CBCC business behavior.
