from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p=Path(path); s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'anchor not found in {path}: {old[:180]!r}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

# --- Core Skill authority: product source is reference-guided; prompts/photography are advisory by default.
replace_once(
    'SKILL.md',
    '- FULL 与 TASK_SCOPED 都必须保持 Product Truth、Claim/Compliance、证据、Photography/CMF、Product Fidelity、Prompt、Review/Revision/Hash lineage；动态化不得通过删除既有能力换取简洁。\n',
    '- FULL 与 TASK_SCOPED 都必须保留 Product Truth、Claim/Compliance、证据、Visual/Photography/CMF、Product Reference/Fidelity、Prompt/Production、Review/Revision/Hash 等能力；**保留能力不等于每个任务都强制执行或阻断**。摄影、Prompt、生图方案、Provider 生产只有在当前任务/生产路线需要时才成为局部执行要求。\n',
)
replace_once(
    'SKILL.md',
    '- Canonical Prompt 使用 **Semantic Compression, never Capability Compression**：凡已经选定且会改变像素、摄影、合成或确定性后期的参数，必须进入 Prompt 或明确的 deterministic production instruction。每个激活资产必须输出 `prompt_consumption_audit`，`missing_decisions` 必须为空后才可完成。\n',
    '- Canonical Prompt 使用 **Semantic Compression, never Capability Compression**：当当前任务需要 Prompt / 生图 / Provider 执行时，已选且会改变该生产结果的参数应投影到 Prompt 或 deterministic production instruction，并记录 `prompt_consumption_audit`。**Prompt Consumption Audit 是生产质量诊断，不是项目或资产完整度的全局阻断 Gate**；`missing_decisions` 可以形成 `NEEDS_PROMPT_WORK`，但不能阻止策略、Listing、内容、视觉策展、资产设计卡或完整人类交付完成。\n',
)
replace_once(
    'SKILL.md',
    '- 人物/手部/身体关系一旦进入资产，包容性摄影即为 P0：肤色测光、深肤色暗部保护、按 Prelight 决定的曝光补偿、neutral/white reflector 或 bounce、large soft diffusion、真实发质、体型/年龄/残障自然呈现和 AI 偏见控制必须变成执行语言；不能只留在总策划。\n',
    '- 人物/手部/身体关系资产必须执行包容性表征与 AI 偏见控制；**真实摄影路线**再把肤色测光、深肤色暗部保护、Prelight、reflector/bounce、diffusion 等转成拍摄参数。插画、3D、风格化生成等非真实摄影路线使用与该媒介匹配的表征控制，不强行套摄影参数。\n',
)
replace_once(
    'SKILL.md',
    '- FULL 最终导出必须重新运行当前 `delivery_contract.validate_strategy_delivery()`，并把 `FULL_DELIVERY_DEPTH_AUDIT.json`、`PROMPT_CONSUMPTION_AUDIT.json` 写入交付包。`index.html` 必须直接可见九域核心对象；宿主自写的一套更短报告不能替代它。\n',
    '- FULL 最终导出必须重新运行当前 `delivery_contract.validate_strategy_delivery()`，并把 `FULL_DELIVERY_DEPTH_AUDIT.json`、`PROMPT_CONSUMPTION_AUDIT.json` 写入交付包。后者是可见的生产准备度审计但 `project_completion_blocking=false`。`index.html` 必须直接可见九域核心对象；宿主自写的一套更短报告不能替代它。\n\n### Product Reference / Fidelity — current authority\n- 用户提供的商品图片、包装图、源文件默认是**产品/设计参考**，不是像素级不可修改层。默认 `REFERENCE_GUIDED`：可根据创意方向重绘、重渲染、3D、插画化、风格化、重新构图或合成；不默认要求摄影写实，也不默认要求像素匹配。\n- Product Truth 约束的是**事实与 Claim 诚实**：规格、成分、功能、认证、包装上真实可读事实等不能被创意伪造成另一种事实。视觉参考可以被创作性解释，只要不把创作性变化冒充成真实产品事实。\n- 只有用户/任务明确要求原图锁定、原始包装像素不可重绘、真实产品合成或等价语义时，才启用 `LOCKED_SOURCE_COMPOSITE / LOCKED_PIXEL`；该硬约束只作用于对应生产子任务。\n- 摄影、灯光、CMF、镜头、Prelight 等是专业能力池：真实拍摄/摄影式生成路线按需消费；插画、3D、图形设计、风格化生成等路线不因为系统会摄影就被强制写实化。\n- 七大第一类工具（市场研究、产品策略、Listing 创意、商品图片、商品视频、广告优化、评论分析）与其他已集成参考能力必须保持可调用并能被项目消费；是否激活由当前任务证据与目标决定，不制造固定七步流水线。\n',
)

# --- Provider / production: VIDEO and reference-guided assets do not imply real-master/photography locks.
replace_once('runtime/cbcc/providers.py', "    if fidelity=='LOCKED_PIXEL' and spec.get('locked_pixel') in {'NOT_APPLICABLE','REFERENCE_ONLY'}:\n", "    locked=str(fidelity or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}\n    if locked and spec.get('locked_pixel') in {'NOT_APPLICABLE','REFERENCE_ONLY'}:\n")
replace_once('runtime/cbcc/providers.py', "    real_product_mode=mode in {'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT','VIDEO'}\n    source_binding_required=bool(real_product_mode or fidelity=='LOCKED_PIXEL')\n", "    real_product_mode=mode in {'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT'}\n    source_binding_required=bool(real_product_mode or locked)\n")
replace_once('runtime/cbcc/providers.py', "            'locked_pixel_result_evidence':['source_product_asset_ids_used','source_product_hashes_used','product_layer_operation','product_identity_preserved'] if fidelity=='LOCKED_PIXEL' else [],\n", "            'locked_pixel_result_evidence':['source_product_asset_ids_used','source_product_hashes_used','product_layer_operation','product_identity_preserved'] if locked else [],\n")
replace_once('runtime/cbcc/production.py', "_REAL_PRODUCT_MODES={'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT','VIDEO'}\n", "_REAL_PRODUCT_MODES={'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT'}\n")
replace_once('runtime/cbcc/production.py', "    fidelity=str(manifest.get('product_fidelity') or 'REFERENCE_CONSTRAINED').upper()\n", "    fidelity=str(manifest.get('product_fidelity') or 'REFERENCE_GUIDED').upper()\n")
replace_once('runtime/cbcc/production.py', "    real_product_required=(fidelity=='LOCKED_PIXEL' or mode in _REAL_PRODUCT_MODES) and mode not in {'AI_GENERATIVE','DOCUMENTATION'}\n", "    locked=fidelity in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}\n    real_product_required=(locked or mode in _REAL_PRODUCT_MODES) and mode not in {'AI_GENERATIVE','DOCUMENTATION'}\n")
replace_once('runtime/cbcc/production.py', "    if fidelity=='LOCKED_PIXEL' and source_bindings and not any(bool(x.get('pixel_lock')) for x in source_bindings):\n", "    if locked and source_bindings and not any(bool(x.get('pixel_lock')) for x in source_bindings):\n")
replace_once('runtime/cbcc/production.py', "    if fidelity=='LOCKED_PIXEL' and mode=='AI_GENERATIVE':\n", "    if locked and mode=='AI_GENERATIVE':\n")
replace_once('runtime/cbcc/production.py', "    if mode in {'REAL_PHOTO','REAL_PRODUCT_COMPOSITE','AI_ENVIRONMENT_REAL_PRODUCT','AI_HUMAN_REAL_PRODUCT','VIDEO'}:\n", "    if mode in _REAL_PRODUCT_MODES:\n")
replace_once('runtime/cbcc/production.py', "    if fidelity=='LOCKED_PIXEL':\n", "    if locked:\n",)
replace_once('runtime/cbcc/production.py', "        'locked_pixel_rule':('Use the exact supplied product master as an immutable pixel layer; preserve logo, packaging print, product color identity, geometry and proportions. Only contract-authorized placement/compositing transforms are permitted.' if fidelity=='LOCKED_PIXEL' else 'Preserve verified product identity and do not invent unsupported product detail.'),\n", "        'locked_pixel_rule':('Explicit locked-source mode: use the exact supplied master as an immutable pixel layer and permit only authorized transforms.' if locked else 'Reference-guided mode: source files guide the design/product subject; redraw/rerender/restyle/recompose is allowed. Keep verified product facts and approved claims honest.'),\n")
replace_once('runtime/cbcc/production.py', "            {'dimension':'PRODUCT_FIDELITY','question':'Does the output preserve the exact product identity/master constraints?'},\n", "            {'dimension':'PRODUCT_REFERENCE_FIDELITY','question':'Does the output follow the selected reference/fidelity policy—reference-guided by default, exact source preservation only when explicitly locked?'},\n")
replace_once('runtime/cbcc/production.py', "    if fidelity=='LOCKED_PIXEL':\n        identity_status,_identity_evidence=_quality_obs_state(obs.get('product_identity_preserved'))\n", "    if fidelity in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}:\n        identity_status,_identity_evidence=_quality_obs_state(obs.get('product_identity_preserved'))\n")

# --- Video: reference-guided by default; prompts/plans remain optional aids.
replace_once('runtime/cbcc/video_creator.py', "              {'shot':'PRODUCT_OR_ACTION_REVEAL','seconds':round(dur*0.24,2),'job':'Introduce the real product in the action/evidence relationship.','visual':source.get('visual_expression_variant') or source.get('visual_production_signature')},\n", "              {'shot':'PRODUCT_OR_ACTION_REVEAL','seconds':round(dur*0.24,2),'job':'Introduce the product/reference subject in the action/evidence relationship using the selected fidelity policy.','visual':source.get('visual_expression_variant') or source.get('visual_production_signature')},\n")
replace_once('runtime/cbcc/video_creator.py', "              'voice':'first-person natural demonstration, not corporate ad read','opening':'specific problem/use context in first seconds','product_handling':'realistic handling and scale; preserve pack identity','proof':'show, then explain; do not claim beyond approved evidence','cta':'native recommendation / shop action after proof','rights_fields':['creator_usage_rights','paid_usage_rights','whitelisting_spark_ads_authorization','usage_term','territory']\n", "              'voice':'first-person natural demonstration, not corporate ad read','opening':'specific problem/use context in first seconds','product_handling':'match the chosen creator/visual medium and product-reference policy; exact pack pixels only when explicitly locked','proof':'show, then explain; do not claim beyond approved evidence','cta':'native recommendation / shop action after proof','rights_fields':['creator_usage_rights','paid_usage_rights','whitelisting_spark_ads_authorization','usage_term','territory']\n")
replace_once('runtime/cbcc/video_creator.py', "        master={\n          'creative_thesis':render_thesis,'camera':camera,'lighting':lighting,'cmf':cmf,\n", "        locked_source=any(bool(x.get('pixel_lock')) or str(x.get('fidelity_mode') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} for x in (source_product_assets or []) if isinstance(x,dict))\n        product_reference_rule=('Explicit locked-source mode: preserve the supplied product master as an immutable source layer; do not redraw that layer.' if locked_source else 'Reference-guided mode: supplied product/source files guide design and identity cues; redraw, rerender, stylize, illustrate or recompose as the selected direction requires. Do not present creative changes as verified product facts.')\n        master={\n          'creative_thesis':render_thesis,'camera':camera,'lighting':lighting,'cmf':cmf,\n")
replace_once('runtime/cbcc/video_creator.py', "          'product_identity':{'source_product_assets':list(source_product_assets or []),'rule':'Use supplied real product masters/references as identity authority. Do not redraw packaging, logo, printed copy, geometry, proportions or product color.'}\n", "          'product_identity':{'source_product_assets':list(source_product_assets or []),'mode':'LOCKED_SOURCE_COMPOSITE' if locked_source else 'REFERENCE_GUIDED','rule':product_reference_rule}\n")
replace_once('runtime/cbcc/video_creator.py', "          '', '[PRODUCT IDENTITY]', master['product_identity']['rule'], 'Use the real product master/reference images supplied with this task as the sole visual identity authority.',\n", "          '', '[PRODUCT REFERENCE / FIDELITY]', master['product_identity']['rule'],\n")
replace_once('runtime/cbcc/video_creator.py', "'','【商品身份】',_vtxt(_vcn(master['product_identity']['rule'])),'使用本次随任务提供的真实商品母版 / 参考图作为唯一商品身份视觉依据。','','【分镜程序】'", "'','【产品参考 / 保真策略】',_vtxt(_vcn(master['product_identity']['rule'])),'','【分镜程序】'")
replace_once('runtime/cbcc/video_creator.py', "          {'parameter':'product identity masters','source':'Product Truth / source assets','target':'all product shots'},\n", "          {'parameter':'product reference / fidelity policy','source':'Product Truth / source assets','target':'all product shots'},\n")

# Seven-agent standalone tools: prompt failure is advisory; standalone video no-strategy is not HOLD.
replace_once('runtime/cbcc/tools/seven_agent.py', "    prompts=[]\n    for a in creative_arch.get('assets',[]):\n        prompts.append({'asset_id':a.get('asset_id'),'prompt_contract':compile_asset_prompt(a,product,target,culture,language_contract,photography=photography,strategy_authority=strategy_authority,source_product_assets=source_product_assets)})\n", "    prompts=[]\n    for a in creative_arch.get('assets',[]):\n        try:\n            pc=compile_asset_prompt(a,product,target,culture,language_contract,photography=photography,strategy_authority=strategy_authority,source_product_assets=source_product_assets)\n        except Exception as exc:\n            pc={'status':'OPTIONAL_PROMPT_NOT_READY','project_completion_blocking':False,'error':str(exc)}\n        prompts.append({'asset_id':a.get('asset_id'),'prompt_contract':pc})\n")
replace_once('runtime/cbcc/tools/seven_agent.py', "        plan['strategy_visual_binding']='HOLD_STRATEGY_AUTHORITY_REQUIRED_FOR_FULL_RENDER_CONTRACT'\n", "        plan['strategy_visual_binding']='ADVISORY_STRATEGY_AUTHORITY_NOT_SUPPLIED'\n")
replace_once('runtime/cbcc/tools/seven_agent.py', "        v['ai_video_prompt']='Use the shot-by-shot visual jobs, real product identity contract and locked copy. Do not let the video model redraw packaging or invent proof.'\n", "        v['ai_video_prompt']='Use the shot-by-shot visual jobs and selected product-reference/fidelity policy. Source files are design references by default; redraw/rerender/stylization is allowed unless an explicit locked-source mode is selected. Never invent product facts or proof.'\n")

# Plugin host wrapper: mirror current authority, so host-native delivery cannot regress when Runtime is not executed.
replace_once('scripts/build_plugin_dist.py', "Prompt 参数消费审计，并物化完整中文优先 index.html", "Prompt/生产参数连续性审计（生产准备度不阻断项目），并物化完整中文优先 index.html")
replace_once('scripts/build_plugin_dist.py', "每个激活资产完成前必须形成 **Prompt Consumption Audit**：`selected execution decisions → projected decisions → missing decisions`。missing 必须为 0 才能声称 Prompt 完成。人物/手/身体关系资产必须把包容性摄影 P0 变成可执行语言，不能只在总策划里出现。", "当当前任务需要 Prompt/生图/Provider 执行时，形成 **Prompt Consumption Audit**：`selected execution decisions → projected decisions → missing decisions`。它是生产准备度诊断，不是项目/资产完整度的全局阻断 Gate；missing 可以标记 `NEEDS_PROMPT_WORK`。人物/手/身体关系资产必须执行包容性表征；真实摄影路线再消费测光、Prelight、柔光等摄影参数。")
replace_once('scripts/build_plugin_dist.py', "- `asset_packages/`：逐资产独立包，保留中文 Canonical Prompt、英文/目标模型 Prompt、Design Card、Photography/CMF/Composition、Product Fidelity、Copy、Parameter Trace、QA/来源等当前资产实际需要的对象。", "- `asset_packages/`：逐资产独立对象包，至少保留中文人类设计卡、策略、视觉/版式、Copy、来源/QA 与当前实际需要的执行对象；Canonical Prompt、生图指导、摄影合同等属于可选生产附件，缺失或未就绪不得让资产本身变成不完整。")
replace_once('scripts/build_plugin_dist.py', "## 人类工作区合同\n", "## Product Reference / Production Authority\n- 用户提供的产品图/包装图/源文件默认作为**设计参考**，不是像素级锁定层；默认允许重绘、重渲染、3D、插画化、风格化、重新构图或合成，不默认强求摄影写实。\n- 只有用户/任务明确要求锁定原图/真实产品合成时才启用 `LOCKED_SOURCE_COMPOSITE / LOCKED_PIXEL`，且只约束对应生产子任务。\n- Prompt、生图方案、摄影/灯光/Prelight 是能力与生产准备度，不是项目或资产完整度的全局 Gate。\n- 七大第一类工具与其他已集成参考能力必须保持可调用、可消费、可追踪；按任务相关性激活，不变成固定七步流水线。\n\n## 人类工作区合同\n")

# Regression test for provider/video non-real default.
Path('tests/test_reference_guided_video_provider_authority.py').write_text(r'''from cbcc.providers import provider_contract
from cbcc.production import _REAL_PRODUCT_MODES
from cbcc.video_creator import build_video_creator_plan, enrich_video_plan_with_strategy
from cbcc.tools.seven_agent import product_video_tool


def _strategy():
    return {'sections':{'05_visual_photography_strategy':{'camera':{},'lighting_framework':{},'cmf':{},'material_lighting_profile':{},'asset_parameter_reasoning':[],'inclusive_photography':{}}}}


def test_generic_video_does_not_imply_real_product_master_or_photography_contract():
    c=provider_contract('VIDEO_PROVIDER','VIDEO',{'product_fidelity':'REFERENCE_GUIDED'})
    assert c['status']=='READY'
    assert c['source_binding_contract']['required'] is False
    assert 'source_product_assets' not in c['required_inputs']
    assert 'photography_contract' not in c['required_inputs']
    assert 'VIDEO' not in _REAL_PRODUCT_MODES


def test_video_render_contract_is_reference_guided_by_default():
    plan=build_video_creator_plan('P',[{'family':'VIDEO','surface':'PDP_VIDEO','curation_job':'show use'}],['How is it used?'],{'primary_locale':'en-US','visible_copy_locales':['en-US']})
    out=enrich_video_plan_with_strategy(plan,_strategy(),source_product_assets=[{'asset_id':'SRC','pixel_lock':False,'fidelity_mode':'REFERENCE_GUIDED'}])
    v=out['assets'][0]
    assert v['visual_render_contract']['product_identity']['mode']=='REFERENCE_GUIDED'
    assert 'redraw' in v['visual_render_contract']['product_identity']['rule'].lower()
    assert 'sole visual identity authority' not in v['canonical_video_prompt_en']
    assert '[PRODUCT REFERENCE / FIDELITY]' in v['canonical_video_prompt_en']


def test_standalone_video_without_strategy_is_advisory_not_hold():
    out=product_video_tool(project_id='P',content_objects=[],shopper_questions=[],language_contract={'primary_locale':'en-US'},video_jobs=[])
    assert out['result']['strategy_visual_binding']=='ADVISORY_STRATEGY_AUTHORITY_NOT_SUPPLIED'
''',encoding='utf-8')

print('final reference-guided authority patch applied')
