# CBCC MODEL PROMPT SEMANTIC MEMBRANE CONTRACT — v0.6.56

## Core rule
**Only model-visible, pixel-changing instructions belong in Model Prompt.**

Model Prompt is the instruction sent to the image/video generation model. It is not the place for project governance, evidence-source hierarchy, file-management language, runtime orchestration, QA checklists, compliance-audit labels, provider-routing metadata or repair workflow.

The generation model should receive the visual world it must create, not the project-management system that produced that world.

## 1. Three semantic planes

### A. Model Prompt — generation plane
Allowed when relevant because the instruction can change pixels/frames/audio:
- deliverable type, canvas/aspect/platform behavior;
- visual objective and visual carrier;
- subject, product role, action, decisive moment;
- scene, environment, props, foreground/midground/background;
- composition, crop, scale, depth, focal path, safe zones;
- exact visible copy only when the selected route is MODEL_RENDER/HYBRID;
- evidence representation that must actually appear;
- camera/perspective/focus/motion when relevant;
- lighting/reflection/material/CMF/color/finish;
- human appearance/action/wardrobe/hair/makeup/representation when relevant;
- direct visual exclusions that prevent generation failure, e.g. `render no extra marketing text`, `no unrelated logos`, `hands anatomically natural`;
- product-reference instructions only when the provider job actually binds/attaches those references.

Good provider-bound wording:
- `Use the attached product reference images to preserve the real package geometry, transparent pump structure and verified packaging identity.`
- `Render only the exact approved Malay copy shown below; render no extra marketing text or invented numbers.`
- `Keep both hands anatomically natural, with correct finger count and believable contact with the applicator.`

### B. Production / Assembly Notes — orchestration plane
Belongs here, not in Model Prompt:
- source file names and paths;
- source-of-truth hierarchy;
- `Excel is the highest authority` / `以 Excel 为最高权威`;
- product fact provenance and evidence grade;
- provider asset handles and source binding metadata;
- Product Fidelity enum names and machine routes;
- editable/frozen layer inventory;
- post-composite assembly order;
- typography composition workflow;
- operator instructions and source reconciliation;
- compliance owner / responsibility layer;
- revision routing.

The production system may use Excel, source files and evidence tables to determine the exact visual facts and copy. It must **compile those facts into explicit model-facing instructions** rather than telling the model to consult an Excel file it cannot see.

Bad:
- `Excel is the highest authority; all numbers must come from Excel.`

Good when text is model-rendered:
- `Render exactly “0.57% Salicylic Acid · 1% Niacinamide · 2% Panthenol” and no other percentages.`

Good when text is post-composited:
- do not send the numeric copy to the image model; keep it in Visible Copy Block / Production Notes.

### C. Review / QA — validation and repair plane
Belongs here, not in Model Prompt:
- `QA:` labels or acceptance checklists;
- source-truth verification after generation;
- spelling verification against canonical copy;
- product-geometry comparison to references;
- safe-zone pass/fail checks;
- thumbnail legibility scoring;
- compliance review status;
- output defect classification;
- `minimum repair` / `最小修复` route;
- responsibility-layer routing such as `文字层 → 局部包装几何 → 透明泵头反射 → 整图重生成`.

A QA criterion may be transformed into a direct forward-generation constraint only when that constraint changes the actual rendered output.

Examples:
- QA `hands/fingers natural` → Model Prompt `hands anatomically natural; correct finger count and believable grip`.
- QA `no invented text` → Model Prompt `render no extra marketing text` when MODEL_RENDER/HYBRID.
- QA `safe zone pass` → Model Prompt `keep headline and product identity inside the defined mobile-safe area`.
- QA `repair text layer first` → stays entirely outside Model Prompt.

## 2. Opaque project nouns are not model instructions
Do not assume a generation model knows internal names such as `K01`, `Asset 07`, `Excel真源`, `产品事实最高权威`, `H03`, local filenames, repository paths or business-object IDs.

Internal names may remain only when they are themselves visible brand/product copy or when they disambiguate a provider-bound reference already attached to the generation job. Otherwise translate them into the actual visual fact.

Bad:
- `Use KIYUU K01 full-view package file as identity truth.`

Good:
- `Use the attached front/side/back product reference images to preserve the real tube proportions, transparent pump applicator and packaging identity.`

## 3. Reference-image binding rule
A Model Prompt may say `attached / supplied product reference images` only if the Provider Job actually binds those images.

If the image model does not receive the references, do not mention them as if it can inspect them. The production layer must either:
1. attach/bind the actual references; or
2. compile the needed verified visual facts into explicit prompt instructions; or
3. mark the generation job not ready when required identity cannot be expressed safely without references.

## 4. Compliance translation rule
Compliance is not dumped as policy prose. Convert only generation-relevant compliance boundaries into visual/content constraints.

Bad:
- `No medical-treatment implication; comply with product claims policy.`

Better when relevant:
- `Do not add medical crosses, clinical-treatment symbols, before/after skin outcomes, cure/treatment wording or invented efficacy numbers.`

If exact visible copy is already locked and no risky visual symbolism is possible, the compliance audit stays outside Model Prompt.

## 5. Model Prompt rejection conditions
A Model Prompt fails the semantic membrane if it contains project-orchestration language such as:
- `Excel 为最高权威`, `Excel is the highest authority`, `source of truth`;
- local filenames / `.xlsx` / repository paths / source-table names;
- `QA:` / `质量验收:` / `acceptance checklist`;
- `最小修复` / `minimum repair` / repair-order chains;
- `provider route`, `authority hash`, `machine contract`, `audit status`;
- `editable layers` / `frozen layers` as workflow metadata rather than direct visible constraints;
- opaque internal asset IDs that do not correspond to visible copy or bound references.

## 6. Required production separation
Each production-ready asset retains four distinct human-operable objects plus Review:
1. Model Prompt CN;
2. Model Prompt EN;
3. Visible Copy Block;
4. Production / Assembly Notes;
5. Review / QA / Local Revision contract.

Rich Art Direction is preserved across the system, but **not every Art Direction / production / review field is copied into the Model Prompt**. The compiler projects each decision to the plane that can actually act on it.
