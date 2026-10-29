from pathlib import Path
import re


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    s = p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'anchor not found in {path}: {old[:140]!r}')
    p.write_text(s.replace(old, new, 1), encoding='utf-8')


def regex_once(path: str, pattern: str, repl: str) -> None:
    p = Path(path)
    s = p.read_text(encoding='utf-8')
    out, n = re.subn(pattern, repl, s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'regex anchor not found/ambiguous in {path}: {pattern[:140]!r}; n={n}')
    p.write_text(out, encoding='utf-8')


# 1) Product source files are design references by default; pixel lock is explicit-only.
replace_once(
    'runtime/cbcc/compiler.py',
    "        else:\n            status='MISSING_SOURCE_FILE'\n        out.append({\n",
    "        else:\n            status='MISSING_SOURCE_FILE'\n        requested_fidelity=str(r.get('fidelity_mode') or r.get('product_fidelity') or '').upper()\n        explicit_lock=bool(r.get('pixel_lock', False) or requested_fidelity in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'})\n        fidelity_mode='LOCKED_SOURCE_COMPOSITE' if explicit_lock else (requested_fidelity or 'REFERENCE_GUIDED')\n        out.append({\n",
)
replace_once(
    'runtime/cbcc/compiler.py',
    "            'pixel_lock':bool(r.get('pixel_lock', True)),\n            'allowed_transforms':r.get('allowed_transforms') or ['PROPORTIONAL_SCALE','PLACEMENT','MASK_OR_CROP','COMPOSITE'],\n            'identity_features':r.get('identity_features') or ['logo','packaging_print','color','geometry','proportions'],\n",
    "            'pixel_lock':explicit_lock,\n            'fidelity_mode':fidelity_mode,\n            'source_usage':r.get('source_usage') or ('IMMUTABLE_SOURCE_LAYER' if explicit_lock else 'DESIGN_REFERENCE'),\n            'allowed_transforms':r.get('allowed_transforms') or (['PROPORTIONAL_SCALE','PLACEMENT','MASK_OR_CROP','COMPOSITE'] if explicit_lock else ['REFERENCE','REDRAW','RERENDER','RESTYLE','RECOMPOSE','PROPORTIONAL_SCALE','PLACEMENT','MASK_OR_CROP','COMPOSITE']),\n            'identity_features':r.get('identity_features') or ['verified_product_facts','recognizable_product_cues','approved_brand_assets'],\n",
)
replace_once(
    'runtime/cbcc/compiler.py',
    "    _write(p/'artifacts/source_product_assets.json',{'status':'SOURCE_PRODUCT_ASSETS_BOUND' if source_product_assets else 'NOT_SUPPLIED','assets':source_product_assets,'count':len(source_product_assets),'principle':'LOCKED_PIXEL production requires an exact supplied product master. Missing masters remain missing and external production must not be represented as executed.'})\n",
    "    _write(p/'artifacts/source_product_assets.json',{'status':'SOURCE_PRODUCT_ASSETS_BOUND' if source_product_assets else 'NOT_SUPPLIED','assets':source_product_assets,'count':len(source_product_assets),'principle':'Source files are design/product references by default. Pixel-level preservation is explicit-only (LOCKED_SOURCE_COMPOSITE/LOCKED_PIXEL). Reference-guided work may redraw, rerender, restyle or recompose while keeping verified product facts and selected identity cues honest.'})\n",
)
replace_once(
    'runtime/cbcc/compiler.py',
    "    creative_ready=(not photography_validation or photography_validation.get('pass')) and council.get('status')=='SELECTED'\n",
    "    creative_ready=council.get('status')=='SELECTED'\n    creative['photography_validation_is_advisory']=True\n    creative['photography_validation_blocks_project_completion']=False\n",
)
replace_once(
    'runtime/cbcc/compiler.py',
    "              'positive_first':True,'photography_contract_required':any(a.get('asset_type')=='IMAGE' for a in architecture['assets']),'photography_validation':photography_validation,\n",
    "              'positive_first':True,'photography_contract_required':bool(request.get('photography_contract')),'photography_planning_is_advisory':True,'photography_validation':photography_validation,\n",
)

# 2) Asset architecture defaults to reference-guided, not pixel fidelity.
replace_once(
    'runtime/cbcc/asset_architecture.py',
    "    if fidelity=='LOCKED_PIXEL':\n        frozen=['product_master_pixels','logo','packaging_print','product_geometry','product_color_identity']\n    else:\n        frozen=['verified_product_identity','locked_copy','approved_claim_facts']\n    return {'editable_layers':list(dict.fromkeys(layers)),'frozen_layers':frozen,'revision_rule':'A local revision may change only the explicitly requested editable layers; frozen product truth/identity remains untouched unless a new source-of-truth package is compiled.'}\n",
    "    locked=fidelity in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'}\n    if locked:\n        frozen=['product_master_pixels','logo','packaging_print','product_geometry','product_color_identity']\n        rule='Explicit locked-source mode: source product pixels/identity stay immutable; only declared editable layers may change.'\n    else:\n        frozen=['verified_product_facts','approved_claim_facts','locked_copy']\n        rule='Reference-guided mode: source files guide product design/identity but are not immutable pixel layers. Visual form may be redrawn, rerendered, restyled or recomposed; do not turn creative interpretation into unsupported product facts or claims.'\n    return {'editable_layers':list(dict.fromkeys(layers)),'frozen_layers':frozen,'revision_rule':rule}\n",
)
replace_once('runtime/cbcc/asset_architecture.py', "'product_fidelity':j.get('product_fidelity','REFERENCE_CONSTRAINED')", "'product_fidelity':j.get('product_fidelity','REFERENCE_GUIDED')")
replace_once('runtime/cbcc/asset_architecture.py', "_editable_layer_contract(mode,j.get('product_fidelity','REFERENCE_CONSTRAINED'))", "_editable_layer_contract(mode,j.get('product_fidelity','REFERENCE_GUIDED'))")

# 3) Prompt compiler: reference-guided, stylization allowed; exact pixel/photorealism only explicit.
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "    product_fidelity = asset.get('product_fidelity') or 'REFERENCE_CONSTRAINED'\n",
    "    product_fidelity = asset.get('product_fidelity') or 'REFERENCE_GUIDED'\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "            'subject': brief.get('subject') or ('Use the supplied real-product master as the product subject' if presence.get('planning_state') != 'FORBIDDEN' else 'decision-critical context/evidence'),\n",
    "            'subject': brief.get('subject') or ('Use supplied product/source files as design references for the product subject; redraw/rerender is allowed unless an explicit locked-source mode is selected' if presence.get('planning_state') != 'FORBIDDEN' else 'decision-critical context/evidence'),\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "            'rule': ('Use the supplied real-product master pixels as an immutable layer; do not regenerate, redraw, retype, recolor or reshape the product.' if product_fidelity == 'LOCKED_PIXEL' else 'Preserve verified identity from supplied product references; do not invent packaging, logo, colors, geometry or printed details.')\n",
    "            'rule': ('Explicit locked-source mode: use supplied product master pixels as an immutable layer; do not regenerate, redraw, retype, recolor or reshape that layer.' if str(product_fidelity).upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} else 'Reference-guided mode: supplied files are design/product references, not immutable pixels. The product may be redrawn, rerendered, stylized, illustrated or recomposed according to the approved creative direction. Preserve verified product facts and only the identity cues the brief actually requires; photorealism and pixel matching are not default requirements.')\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "            'material_truth_rule': 'Reveal only source-bound material/finish/texture. Never invent gloss, transparency, cream texture, liquid behavior or physical effects.'\n",
    "            'material_truth_rule': 'Creative/stylized material depiction is allowed when selected by the art direction. Do not present invented material, finish, texture or physical behavior as a verified product fact.'\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "            '真实产品 / Product Truth 绑定：商品身份、包装、材质、颜色、结构与可见事实只允许来自已验证商品真源及随任务提供的真实商品母版 / 参考图。',\n",
    "            'Product Truth / 参考设计绑定：已验证商品事实与 Claim 不得被创意改写；随任务提供的源文件作为产品设计参考。除非明确选择锁定源图模式，否则允许重绘、重渲染、风格化、插画化与重新构图，不要求像素级一致或摄影写实。',\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "            '图像语言：保持真实商品身份、CMF、色彩与字体系统的一致性；但每张资产必须按自己的购买问题重新建立空间层级和构图，不套上一张版式。',\n",
    "            '图像语言：根据当前创意方向决定写实、风格化、插画、3D、合成或其他视觉语言；源文件提供设计与商品事实参考，每张资产按自己的购买问题重新建立空间层级和构图。',\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "            f\"颜色一致性：{_txt(_cn_phrase(lm.get('color_consistency_plan')))}\", '材质真实性边界：只表现商品真源/CMF 支持的材质、表面处理、透明度与光泽；不得凭空增加液体、膏体、金属、玻璃或其他物理效果。',\n",
    "            f\"颜色一致性：{_txt(_cn_phrase(lm.get('color_consistency_plan')))}\", '材质事实边界：可以按创意方向做风格化材质表达，但不得把源文件未支持的材质、表面处理或物理行为当成真实商品事实。',\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "            '局部修改规则：只允许修改明确列出的可编辑层；冻结的商品真源与身份层保持不变，除非重新编译新的商品真源包。' if editable else '',\n            '', '【真实商品身份】',\n            f\"商品保真模式：{_txt(prod.get('product_fidelity'))}\",\n            '以随任务提供的真实商品母版 / 参考图作为唯一商品身份视觉依据。不得重画、改字、改 Logo、改包装几何比例、改真实产品颜色或凭空补不存在的结构。',\n",
    "            '局部修改规则：遵守当前资产声明的冻结事实/Claim/文案边界；参考图本身只有在显式锁定源图模式下才是不可改像素层。' if editable else '',\n            '', '【产品参考 / 保真策略】',\n            f\"商品参考模式：{_txt(prod.get('product_fidelity'))}\",\n            prod.get('rule'),\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "            'Product Truth binding: product identity, packaging, material, color, geometry and visible facts must remain source-bound to verified Product Truth and the real-product references supplied with the task.',\n",
    "            'Product Truth / reference binding: verified product facts and claims must remain honest. Supplied source files are product/design references; unless locked-source mode is explicitly selected, redraw, rerender, stylization, illustration and recomposition are allowed and photorealism/pixel matching are not required.',\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "            'Local edit rule: Change only the explicitly listed editable layers; frozen product-truth and identity layers remain untouched unless a new source-of-truth package is compiled.' if editable else '',\n            '', '[REAL PRODUCT IDENTITY]',\n            f\"Product fidelity mode: {_txt(prod.get('product_fidelity'))}\",\n            prod.get('rule'), 'Use the real product master/reference images supplied with this task as the sole visual identity authority.',\n",
    "            'Local edit rule: preserve declared product facts/claims/copy boundaries; source pixels are immutable only in an explicit locked-source mode.' if editable else '',\n            '', '[PRODUCT REFERENCE / FIDELITY]',\n            f\"Product reference mode: {_txt(prod.get('product_fidelity'))}\",\n            prod.get('rule'),\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "        {'strategy_parameter':'consumer decision question / Product Truth execution binding','render_location':'RENDER OBJECTIVE / REAL PRODUCT IDENTITY','value':{'consumer_question':(card.get('commerce_task') or {}).get('consumer_question'),'product_truth_binding':'SOURCE_BOUND'}},\n",
    "        {'strategy_parameter':'consumer decision question / Product Truth execution binding','render_location':'RENDER OBJECTIVE / PRODUCT REFERENCE / FIDELITY','value':{'consumer_question':(card.get('commerce_task') or {}).get('consumer_question'),'product_truth_binding':'FACT_BOUND_REFERENCE_GUIDED'}},\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "        {'strategy_parameter':'product fidelity / real masters','render_location':'REAL PRODUCT IDENTITY','value':card.get('product_identity')},\n",
    "        {'strategy_parameter':'product reference / fidelity policy','render_location':'PRODUCT REFERENCE / FIDELITY','value':card.get('product_identity')},\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "    checks.append({'decision':'real_product_identity','required':True,'projected':'【真实商品身份】' in prompt_cn and '[REAL PRODUCT IDENTITY]' in prompt_en})\n",
    "    checks.append({'decision':'product_reference_fidelity','required':True,'projected':'【产品参考 / 保真策略】' in prompt_cn and '[PRODUCT REFERENCE / FIDELITY]' in prompt_en})\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "        'principle':'Semantic compression may remove repetition and irrelevant toolbox fields, but never an already-selected pixel/capture/composite-affecting execution decision.',\n",
    "        'principle':'Prompt readiness is a production-quality diagnostic, not a project-completion gate. When prompts are requested, preserve the selected execution decisions that actually matter to that production route.',\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "            'real_product_master_required': asset.get('product_fidelity') == 'LOCKED_PIXEL',\n            'real_product_master_substitution_allowed': False,\n            'immutable_identity_fields': ['logo', 'packaging_print', 'product_color_identity', 'geometry', 'proportions'] if asset.get('product_fidelity') == 'LOCKED_PIXEL' else ['verified_product_identity', 'approved_claim_facts'],\n",
    "            'real_product_master_required': str(asset.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'},\n            'real_product_master_substitution_allowed': str(asset.get('product_fidelity') or '').upper() not in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'},\n            'immutable_identity_fields': ['logo', 'packaging_print', 'product_color_identity', 'geometry', 'proportions'] if str(asset.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} else ['verified_product_facts', 'approved_claim_facts'],\n",
)
replace_once(
    'runtime/cbcc/prompt_compiler.py',
    "        'real_product_master_required': asset.get('product_fidelity') == 'LOCKED_PIXEL',\n",
    "        'real_product_master_required': str(asset.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'},\n",
)
replace_once('runtime/cbcc/prompt_compiler.py', "layers.append('product_master_or_verified_product')", "layers.append('product_reference_or_product_subject')")

# 4) Prompt / generation guidance are optional production aids, not project/asset completion blockers.
replace_once(
    'runtime/cbcc/delivery_export.py',
    "    return {\n        'status':'PASS' if not missing else 'INCOMPLETE',\n        'asset_count':len(rows),\n        'assets':rows,\n        'missing_assets':[r.get('asset_id') for r in missing],\n        'principle':'Semantic compression may remove repetition or irrelevant toolbox fields, never a selected execution decision that changes pixels, capture, composite or deterministic post-production.',\n    }\n",
    "    return {\n        'status':'READY' if not missing else 'NEEDS_PROMPT_WORK',\n        'project_completion_blocking':False,\n        'asset_count':len(rows),\n        'assets':rows,\n        'missing_assets':[r.get('asset_id') for r in missing],\n        'principle':'Prompt/generation-plan readiness is advisory for the project and asset delivery. It becomes locally blocking only for an explicitly requested prompt-ready or provider-execution sub-deliverable.',\n    }\n",
)
replace_once(
    'runtime/cbcc/delivery_export.py',
    "    prompt_audit=_prompt_consumption_summary(asset_root)\n    if full and asset_root.exists() and prompt_audit.get('status')!='PASS':\n        raise RuntimeError('BLOCKED FULL prompt consumption audit failed for assets: ' + ', '.join(prompt_audit.get('missing_assets') or []))\n    if asset_root.exists():\n",
    "    prompt_audit=_prompt_consumption_summary(asset_root)\n    # Prompt/generation-plan readiness is deliberately non-blocking for FULL human delivery.\n    # It is a production-quality diagnostic; only a separately requested prompt-ready/provider-execution task may treat it as a local gate.\n    if asset_root.exists():\n",
)
replace_once(
    'runtime/cbcc/delivery_export.py',
    "            'prompt_execution_continuity': prompt_audit.get('status') if asset_root.exists() else 'NO_ASSETS',\n",
    "            'prompt_generation_readiness': prompt_audit.get('status') if asset_root.exists() else 'NO_ASSETS',\n            'prompt_generation_readiness_blocks_project_completion': False,\n",
)

# 5) Asset compiler tolerates prompt compilation failure and validates business/human assets independently.
replace_once(
    'runtime/cbcc/asset_compiler.py',
    "        prompt_bundle=compile_asset_prompt(asset,product,target,culture,language_contract,locale_profiles,photography_contract,strategy_authority,source_product_assets)\n",
    "        try:\n            prompt_bundle=compile_asset_prompt(asset,product,target,culture,language_contract,locale_profiles,photography_contract,strategy_authority,source_product_assets)\n        except Exception as exc:\n            prompt_bundle={\n                'status':'OPTIONAL_PROMPT_NOT_READY',\n                'design_card':{\n                    'commerce_task':{k:asset.get(k) for k in ['consumer_question','reason_to_exist','purchase_barrier','entry_state','belief_target','exit_state','incremental_information','success_metric','handoff']},\n                    'visual_objective':asset.get('strategic_job'),\n                    'composition_camera':{},'lighting_material_cmf':{},\n                    'information_design':{'locked_visible_copy':asset.get('visible_copy') or {}},\n                    'product_identity':{'product_fidelity':asset.get('product_fidelity') or 'REFERENCE_GUIDED','rule':'Source files are design references by default; visual re-rendering/stylization is allowed unless a locked-source mode was explicitly selected.'},\n                    'editable_layer_contract':asset.get('editable_layer_contract') or {},\n                },\n                'prompt_cn':'','prompt_en':'','deterministic_copy_overlay':asset.get('visible_copy') or {},\n                'parameter_trace':[],\n                'prompt_consumption_audit':{'status':'NOT_READY','project_completion_blocking':False,'missing_decisions':['PROMPT_COMPILE_ERROR'],'error':str(exc)},\n                'machine_visual_contract':{},'renderer_recipe':{},'qa_target_contract':{},\n            }\n",
)
replace_once(
    'runtime/cbcc/asset_compiler.py',
    "        _write(d/'13_prompt_contract.json',_jdump({'status':prompt_bundle['status'],'design_card':prompt_bundle['design_card'],'canonical_prompt_cn':prompt_bundle['prompt_cn'],'canonical_prompt_en':prompt_bundle['prompt_en'],'deterministic_copy_overlay':prompt_bundle.get('deterministic_copy_overlay') or {},'parameter_trace':prompt_bundle.get('parameter_trace') or [],'prompt_consumption_audit':prompt_bundle.get('prompt_consumption_audit') or {},'machine_visual_contract':prompt_bundle['machine_visual_contract'],'renderer_recipe':prompt_bundle['renderer_recipe'],'qa_target_contract':prompt_bundle['qa_target_contract']}))\n",
    "        _write(d/'13_prompt_contract.json',_jdump({'status':prompt_bundle.get('status'),'project_completion_blocking':False,'design_card':prompt_bundle.get('design_card') or {},'canonical_prompt_cn':prompt_bundle.get('prompt_cn') or '','canonical_prompt_en':prompt_bundle.get('prompt_en') or '','deterministic_copy_overlay':prompt_bundle.get('deterministic_copy_overlay') or {},'parameter_trace':prompt_bundle.get('parameter_trace') or [],'prompt_consumption_audit':prompt_bundle.get('prompt_consumption_audit') or {},'machine_visual_contract':prompt_bundle.get('machine_visual_contract') or {},'renderer_recipe':prompt_bundle.get('renderer_recipe') or {},'qa_target_contract':prompt_bundle.get('qa_target_contract') or {}}))\n",
)
replace_once(
    'runtime/cbcc/asset_compiler.py',
    "        fidelity_line=('Use the supplied product master as the immutable product layer; preserve logo, packaging print, color, geometry and proportions exactly.' if asset.get('product_fidelity')=='LOCKED_PIXEL' else 'Preserve verified product identity and do not turn reference-only details into invented product facts.')\n",
    "        fidelity_line=('Explicit locked-source mode: use the supplied master as an immutable product layer.' if str(asset.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} else 'Reference-guided mode: source files guide the design; redraw/rerender/restyle/recompose is allowed. Keep verified facts/claims honest; pixel matching and photorealism are not required.')\n",
)
replace_once(
    'runtime/cbcc/asset_compiler.py',
    "'canonical_prompt_contract':prompt_bundle['machine_visual_contract'],'parameter_trace':prompt_bundle.get('parameter_trace') or [],'deterministic_copy_overlay':prompt_bundle.get('deterministic_copy_overlay') or {},'renderer_recipe':prompt_bundle['renderer_recipe'],'qa_target_contract':prompt_bundle['qa_target_contract']",
    "'canonical_prompt_contract':prompt_bundle.get('machine_visual_contract') or {},'parameter_trace':prompt_bundle.get('parameter_trace') or [],'deterministic_copy_overlay':prompt_bundle.get('deterministic_copy_overlay') or {},'renderer_recipe':prompt_bundle.get('renderer_recipe') or {},'qa_target_contract':prompt_bundle.get('qa_target_contract') or {},'prompt_generation_readiness':(prompt_bundle.get('prompt_consumption_audit') or {}).get('status'),'prompt_generation_readiness_blocks_asset_delivery':False",
)
replace_once(
    'runtime/cbcc/asset_compiler.py',
    "            photography_contract={'status':'STRATEGY_DERIVED_PHOTOGRAPHY_PLAN','authority':'EXECUTION_RECOMMENDATION_NOT_PRODUCT_TRUTH','prelight_required':True,'asset_type':'IMAGE','asset_reasoning':asset_photo_reasoning,'reason':'No user-supplied photography contract exists. The runtime preserves an executable category/decision-specific planning contract rather than a generic N/A slot; exact geometry/exposure is locked during prelight.'}\n",
    "            photography_contract={'status':'STRATEGY_DERIVED_PHOTOGRAPHY_PLAN','authority':'ADVISORY_UNLESS_REAL_CAPTURE_EXPLICITLY_SELECTED','prelight_required':False,'project_completion_blocking':False,'asset_type':'IMAGE','asset_reasoning':asset_photo_reasoning,'reason':'This is an optional execution recommendation. It becomes capture-critical only when real-photo production is explicitly selected; stylized/illustrated/3D/generated directions do not need to imitate real photography.'}\n",
)
replace_once(
    'runtime/cbcc/asset_compiler.py',
    "REQUIRED_ASSET_FILES=[\n    '00_asset_manifest.yaml','01_strategy.md','02_visual_spec.md','03_photography_contract.json','04_layout_contract.json',\n    '05_prompt_CN.txt','06_prompt_EN.txt','07_generation_guidance.txt','08_copy.md','09_production_notes.md','10_source_trace.md','11_strategy_authority_trace.json'\n]\n",
    "REQUIRED_ASSET_FILES=[\n    '00_asset_manifest.yaml','00_HUMAN_DESIGN_CARD_CN.md','01_strategy.md','02_visual_spec.md','03_photography_contract.json','04_layout_contract.json',\n    '08_copy.md','09_production_notes.md','10_source_trace.md','11_strategy_authority_trace.json','12_design_card.json'\n]\nOPTIONAL_PRODUCTION_FILES=['05_prompt_CN.txt','06_prompt_EN.txt','07_generation_guidance.txt','13_prompt_contract.json']\n",
)
replace_once(
    'runtime/cbcc/asset_compiler.py',
    "        assets.append({'asset_id':row['asset_id'],'missing':missing})\n    return {'pass':not errors,'errors':errors,'assets':assets,'count':len(assets)}\n",
    "        optional_missing=[f for f in OPTIONAL_PRODUCTION_FILES if not (d/f).exists()]\n        assets.append({'asset_id':row['asset_id'],'missing':missing,'optional_production_missing':optional_missing})\n    return {'pass':not errors,'errors':errors,'assets':assets,'count':len(assets),'optional_production_files':OPTIONAL_PRODUCTION_FILES,'prompt_generation_files_block_asset_delivery':False}\n",
)
replace_once(
    'runtime/cbcc/asset_compiler.py',
    "        '', '## 4. 生产提示词','',\n",
    "        '', '## 4. 生产提示词（可选生产辅助，不阻断资产交付）','',\n",
)

# 6) Materialize a first-class seven-tool synthesis using real compiler outputs rather than treating file presence as integration.
seven_path=Path('runtime/cbcc/tools/seven_agent.py')
seven=seven_path.read_text(encoding='utf-8')
anchor='\nSEVEN_TOOLS={\n'
if anchor not in seven:
    raise SystemExit('seven agent insertion anchor missing')
synthesis=r'''

def compile_seven_agent_synthesis(*, domain:dict[str,Any]|None=None, architecture:dict[str,Any]|None=None, video_plan:dict[str,Any]|None=None, paid_campaigns:dict[str,Any]|None=None, source_product_assets:list[dict[str,Any]]|None=None)->dict[str,Any]:
    """Materialize how the seven first-class commerce capabilities are actually consumed.

    The full compiler already uses the same underlying domain engines; this function does not
    re-run them or manufacture a fixed seven-step pipeline. It records project-active outputs and
    cross-domain handoffs so release acceptance can prove capability continuity beyond file presence.
    """
    domain=domain or {}; architecture=architecture or {}; video_plan=video_plan or {}; paid_campaigns=paid_campaigns or {}
    assets=architecture.get('assets') or []
    market=domain.get('market') or {}; economics=domain.get('economics') or {}; listing=domain.get('listing') or {}; ads=domain.get('ads') or {}; feedback=domain.get('feedback') or {}
    compiled_listing=listing.get('compiled') or {}
    ad_diag=(ads.get('aggregate') or ads).get('diagnosis') or [] if isinstance(ads,dict) else []
    ad_routes=sorted({str(x.get('route')) for x in ad_diag if isinstance(x,dict) and x.get('route')})
    feedback_issues=feedback.get('issues') or [] if isinstance(feedback,dict) else []
    market_fit_assets=[a for a in assets if a.get('decision_origin')=='MARKET_THEME_FIT']
    feedback_assets=[a for a in assets if a.get('decision_origin')=='FEEDBACK_SIGNAL']
    listing_objections=compiled_listing.get('objection_resolution_plan') or []
    capabilities=[
        {'id':'01_MARKET_RESEARCH','project_active':bool(market),'consumed_by':['Strategy §3 market/audience','Market Evidence Fit','Asset jobs only after explicit product-truth fit'],'evidence':{'status':market.get('status'),'market_fit_asset_count':len(market_fit_assets)}},
        {'id':'02_PRODUCT_STRATEGY','project_active':True,'consumed_by':['Strategy value/SKU/offer/positioning','economics guardrails','asset business hypothesis'],'evidence':{'economics_status':economics.get('status'),'asset_count':len(assets)}},
        {'id':'03_LISTING_CREATIVE','project_active':bool(listing),'consumed_by':['Listing/Search authority','objection-to-asset handoff','human delivery'],'evidence':{'status':listing.get('status'),'objection_count':len(listing_objections)}},
        {'id':'04_PRODUCT_IMAGE','project_active':bool(assets),'consumed_by':['Dynamic Asset Architecture','Creative Council/CMF','per-asset design cards and optional prompt contracts'],'evidence':{'asset_count':len([a for a in assets if a.get('asset_type')=='IMAGE'])}},
        {'id':'05_PRODUCT_VIDEO','project_active':bool(video_plan.get('assets')),'consumed_by':['Video Creator Plan','Strategy §5','production only when explicitly requested'],'evidence':{'video_asset_count':len(video_plan.get('assets') or [])}},
        {'id':'06_ADVERTISING_OPTIMIZATION','project_active':bool(ads or paid_campaigns.get('campaigns')),'consumed_by':['Strategy §9 diagnostics','Paid Campaign Architecture','local revision routing'],'evidence':{'status':ads.get('status'),'diagnostic_routes':ad_routes,'campaign_count':len(paid_campaigns.get('campaigns') or [])}},
        {'id':'07_REVIEW_ANALYSIS','project_active':bool(feedback),'consumed_by':['communication-fixable asset jobs','Strategy §9 local revision routing','listing/content correction'],'evidence':{'status':feedback.get('status'),'issue_count':len(feedback_issues),'feedback_asset_count':len(feedback_assets)}},
    ]
    asset_inputs={
        'market':{'status':market.get('status'),'approved_fit_asset_count':len(market_fit_assets)},
        'offer_economics':{'status':economics.get('status'),'currency':economics.get('currency')},
        'listing':{'status':listing.get('status'),'objection_count':len(listing_objections)},
        'ads':{'status':ads.get('status'),'diagnostic_routes':ad_routes},
        'reviews_feedback':{'status':feedback.get('status'),'issue_count':len(feedback_issues),'communication_asset_count':len(feedback_assets)},
        'product_sources':{'count':len(source_product_assets or []),'default_usage':'DESIGN_REFERENCE'},
    }
    return {
        'status':'SEVEN_AGENT_CAPABILITY_SYNTHESIS_COMPILED',
        'execution_model':'SHARED_RUNTIME_ENGINES; relevance-driven, not a mandatory seven-step pipeline',
        'all_seven_available':True,
        'all_seven_required_each_task':False,
        'capabilities':capabilities,
        'asset_inputs':asset_inputs,
        'active_ids':[x['id'] for x in capabilities if x.get('project_active')],
        'principle':'A reference capability counts as preserved only when its real project output is consumed by strategy, listing, asset/content decisions, paid/video architecture, review routing or delivery—not because a file exists.',
    }
'''
seven_path.write_text(seven.replace(anchor, synthesis+anchor, 1), encoding='utf-8')

replace_once(
    'runtime/cbcc/compiler.py',
    "from .tools.experiment import evaluate_binary_experiment, compile_experiment_analysis\n",
    "from .tools.experiment import evaluate_binary_experiment, compile_experiment_analysis\nfrom .tools.seven_agent import compile_seven_agent_synthesis\n",
)
replace_once(
    'runtime/cbcc/compiler.py',
    "    paid_campaigns=compile_paid_campaign_architecture(request.get('project_id','project'),tc,architecture.get('assets') or [],truth,domain.get('economics'),domain.get('ads'),request.get('paid_campaigns'),objects)\n    _write(p/'artifacts/paid_campaign_architecture.json',paid_campaigns)\n",
    "    paid_campaigns=compile_paid_campaign_architecture(request.get('project_id','project'),tc,architecture.get('assets') or [],truth,domain.get('economics'),domain.get('ads'),request.get('paid_campaigns'),objects)\n    _write(p/'artifacts/paid_campaign_architecture.json',paid_campaigns)\n    seven_agent_synthesis=compile_seven_agent_synthesis(domain=domain,architecture=architecture,video_plan=video_plan,paid_campaigns=paid_campaigns,source_product_assets=source_product_assets)\n    architecture['commerce_capability_inputs']=seven_agent_synthesis.get('asset_inputs') or {}\n    for _asset in architecture.get('assets') or []:\n        _asset['commerce_context']=seven_agent_synthesis.get('asset_inputs') or {}\n    _write(p/'artifacts/seven_agent_synthesis.json',seven_agent_synthesis)\n    _write(p/'artifacts/asset_architecture.json',architecture)\n",
)
replace_once(
    'runtime/cbcc/delivery_export.py',
    "    'artifacts/content_requiredness.json','artifacts/agent_next_action.json','artifacts/agent_autonomy_plan.json',\n",
    "    'artifacts/content_requiredness.json','artifacts/agent_next_action.json','artifacts/agent_autonomy_plan.json','artifacts/seven_agent_synthesis.json',\n",
)

# 7) Regression tests: default reference-guided; explicit lock preserved; prompt files advisory; seven-capability synthesis is real.
test = r'''from pathlib import Path
import json

from cbcc.compiler import _normalize_source_product_assets
from cbcc.asset_architecture import build_asset_architecture, _editable_layer_contract
from cbcc.asset_compiler import validate_asset_packages, REQUIRED_ASSET_FILES, OPTIONAL_PRODUCTION_FILES
from cbcc.delivery_export import _prompt_consumption_summary
from cbcc.tools.seven_agent import compile_seven_agent_synthesis, SEVEN_TOOLS


def test_source_product_assets_are_reference_guided_by_default(tmp_path):
    src=tmp_path/'p.png'; src.write_bytes(b'product-reference')
    rows=_normalize_source_product_assets([{'path':str(src)}],[tmp_path])
    assert rows[0]['pixel_lock'] is False
    assert rows[0]['fidelity_mode']=='REFERENCE_GUIDED'
    assert rows[0]['source_usage']=='DESIGN_REFERENCE'
    assert 'RERENDER' in rows[0]['allowed_transforms']


def test_explicit_locked_source_mode_is_preserved(tmp_path):
    src=tmp_path/'p.png'; src.write_bytes(b'product-reference')
    rows=_normalize_source_product_assets([{'path':str(src),'pixel_lock':True}],[tmp_path])
    assert rows[0]['pixel_lock'] is True
    assert rows[0]['fidelity_mode']=='LOCKED_SOURCE_COMPOSITE'
    assert rows[0]['source_usage']=='IMMUTABLE_SOURCE_LAYER'


def test_dynamic_asset_defaults_reference_guided_not_pixel_locked():
    target={'target_id':'T','surfaces':['GALLERY']}
    objects=[{'family':'VISUAL','surface':'GALLERY','curation_job':'Resolve identity','source_ids':[],'claim_ids':[]}]
    arch=build_asset_architecture('P',target,['What is this product?'],objects)
    assert arch['assets']
    assert arch['assets'][0]['product_fidelity']=='REFERENCE_GUIDED'
    edit=_editable_layer_contract('GRAPHIC_DESIGN','REFERENCE_GUIDED')
    assert 'product_master_pixels' not in edit['frozen_layers']
    assert 'verified_product_facts' in edit['frozen_layers']


def test_prompt_generation_files_do_not_block_asset_package_validation(tmp_path):
    root=tmp_path/'assets'; d=root/'AST-1'; d.mkdir(parents=True)
    for name in REQUIRED_ASSET_FILES:
        p=d/name; p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text('{}' if p.suffix in {'.json','.yaml'} else '# ok\n',encoding='utf-8')
    (root/'ASSET_PACKAGE_INDEX.json').write_text(json.dumps({'assets':[{'asset_id':'AST-1'}]}),encoding='utf-8')
    result=validate_asset_packages(root)
    assert result['pass'] is True
    assert result['prompt_generation_files_block_asset_delivery'] is False
    assert set(result['assets'][0]['optional_production_missing'])==set(OPTIONAL_PRODUCTION_FILES)


def test_prompt_consumption_is_advisory_for_project_completion(tmp_path):
    d=tmp_path/'AST-1'; d.mkdir()
    (d/'13_prompt_contract.json').write_text(json.dumps({'prompt_consumption_audit':{'status':'INCOMPLETE','missing_decisions':['camera']}}),encoding='utf-8')
    result=_prompt_consumption_summary(tmp_path)
    assert result['status']=='NEEDS_PROMPT_WORK'
    assert result['project_completion_blocking'] is False
    assert result['missing_assets']==['AST-1']


def test_seven_first_class_capabilities_are_synthesized_from_real_outputs():
    assert {str(i).zfill(2) for i in range(1,8)}.issubset(set(SEVEN_TOOLS))
    syn=compile_seven_agent_synthesis(
        domain={'market':{'status':'READY'},'economics':{'status':'READY','currency':'MYR'},'listing':{'status':'READY','compiled':{'objection_resolution_plan':[{'objection':'x'}]}},'ads':{'status':'READY','diagnosis':[{'route':'CLICK_PACKAGE'}]},'feedback':{'status':'READY','issues':[{'category':'MISUNDERSTANDING'}]}},
        architecture={'assets':[{'asset_id':'A','asset_type':'IMAGE','decision_origin':'FEEDBACK_SIGNAL'}]},
        video_plan={'assets':[{'asset_id':'V'}]},
        paid_campaigns={'campaigns':[{'id':'C'}]},
        source_product_assets=[{'asset_id':'P','source_usage':'DESIGN_REFERENCE'}],
    )
    assert syn['all_seven_available'] is True
    assert syn['all_seven_required_each_task'] is False
    assert len(syn['capabilities'])==7
    assert syn['asset_inputs']['product_sources']['default_usage']=='DESIGN_REFERENCE'
    assert '07_REVIEW_ANALYSIS' in syn['active_ids']
'''
Path('tests/test_reference_guided_optional_prompt_and_capability_continuity.py').write_text(test,encoding='utf-8')

print('reference-guided asset + optional prompt + seven-capability patch applied')
