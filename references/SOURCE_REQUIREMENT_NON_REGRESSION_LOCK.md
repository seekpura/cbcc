# CBCC SOURCE REQUIREMENT NON-REGRESSION LOCK

## Purpose
This is the release-construction lock for Cross-Border Commerce Creative. It exists because additive upgrades can still regress mature behavior when a local fix is implemented without re-reading the original source requirements that define the full system.

**The mandatory authorities below must be read before every release change that touches strategy, asset curation, Art Direction, Prompt compilation, production, Human Workspace, language, compliance or runtime behavior.** A release is not valid merely because the new local bug is fixed.

Mandatory original authorities:
- `references/MASTER_CONSTRUCTION_CONTRACT.md`
- `references/PROMPT_ART_DIRECTION_MASTER_CONTRACT.md`
- `references/BUSINESS_OBJECT_DENSITY_MASTER_CONTRACT.md`
- `references/HUMAN_WORKSPACE_PROMPT_CONTINUITY_LOCK.md`
- `references/ASSET_UNIVERSE_OPEN_WORLD_CONTRACT.md`
- `references/AUTHORITY_SOURCE_PARITY_LOCK.md`
- current canonical loading map and current Skill authority

`AUTHORITY_SOURCE_PARITY_LOCK.md` is mandatory because an additive release is still invalid when the current top-level Skill advances but packaged `resources/SKILL.md` remains on an older authority. The actually installed plugin must be re-read after update; source/package intent alone is not proof.

## Additive release invariant
Every change must preserve the complete existing capability set unless the user explicitly replaces a requirement. A fix is a regression if it improves one local dimension by deleting, compressing, hiding or bypassing another established dimension.

For commercial visual assets, the following authored dimensions are independently protected and must survive from planning → asset object → Design Card → Model Prompt / Production Notes / Review according to their proper semantic plane:
- 商业决策、消费者问题、购买障碍、目标信念、WHY；
- 人物 / 主体：角色、年龄、肤色、发型发质、妆容、服装、体型、残障、姿态、表情、视线、手部动作、人物与商品交互；
- 动作与 decisive moment；
- 场景、环境、前景 / 中景 / 背景、道具、承托面、空间深度；
- Visual Carrier、视觉钩子、Hero Moment、情绪节奏、信息密度；
- Product Presence、Product Role、Product Fidelity、真实包装身份与参考图绑定；
- 构图、空间关系、相对位置、尺度、纵深、焦点路径、负空间、裁切、安全区；
- 证据层级与可视证据关系；
- 文案、字体角色、字号层级、字重、行数、对齐、本地化排版、目标市场语言；
- 文化、人群、交叉性、包容性表征；
- CMF、材质、微表面、透明 / 半透明、反射、折射、高光、真实物理响应、颜色系统；
- 摄影 / 光学：焦段、镜头、工作距离、机位高度、yaw / pitch / roll、景别、透视、对焦面、景深 / 光圈、快门 / ISO；
- 灯光：key / fill / negative / rim、modifier 尺寸 / 距离 / 角度、CCT / WB、光比、阴影 / 高光政策、反射 / 偏振、Prelight；
- finishing / retouch / final grade；
- Surface / 平台 / 尺寸 / 移动端 / 缩略图行为；
- 视频 / Creator / LIVE 的时长、beat、shot sequence、主体运动、camera motion、转场、音频、字幕、CTA；
- Business Hypothesis、Success Metric、Test / Rotation / A-B 变量；
- QA、Review、最小修复作为独立后验对象继续保留。

## Semantic-plane rule
“完整 Art Direction”不等于“所有字段都塞进 Model Prompt”。正确分流是：
- **Model Prompt**：真正会改变像素 / 帧 / 音频的已选视觉执行信息；
- **Visible Copy Block**：消费者可见 exact copy 与中文释义 / 用途；
- **Production / Assembly Notes**：真源、文件、Provider 绑定、可编辑 / 冻结层、装配与责任层；
- **Review / QA / Revision**：验收、合规复核、缺陷分类、最小修复顺序。

语义隔离只能移除不属于 Model Prompt 的治理 / 生产 / Review 信息；**不得删除同一段中已经选定的人物、场景、道具、构图、摄影、灯光、CMF、材质、文案、文化或动态执行内容。**

## Required release proof
Any release that changes Prompt or visual production must prove all of the following on a representative high-density asset:
1. upstream Art Direction actually contains the relevant human / scene / composition / evidence / copy / culture / CMF / photography / lighting / finishing decisions;
2. compatibility projection preserves those concrete values;
3. final Model Prompt still contains every selected pixel-changing value relevant to the chosen route;
4. Excel/source-authority/QA labels/minimum-repair/provider-internal prose do not leak into Model Prompt;
5. Production Notes and Review still contain the orchestration / QA information that was intentionally separated;
6. final public compiler/provider path is tested, not only an intermediate helper;
7. previous Asset Universe, business-object density, Chinese Human Workspace and routed interaction contracts remain intact;
8. top-level packaged Skill, packaged `resources/SKILL.md`, `resources/VERSION`, plugin manifests and latest builder identify the same current release family;
9. the actually installed plugin is re-read and passes the same authority-parity check.

A heading check, field-name check or self-authored PASS flag is insufficient. Use concrete-value regression fixtures and inspect the final object actually sent downstream.
