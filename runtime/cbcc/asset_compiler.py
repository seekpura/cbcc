from __future__ import annotations
from pathlib import Path
from typing import Any
import json, yaml
from .providers import route_production
from .asset_architecture import _visual_production_signature, _editable_layer_contract
from .category_strategy import classify_decision_intent
from .prompt_compiler import compile_asset_prompt, _cn_phrase


def _write(path:Path,text:str):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding='utf-8')

def _jdump(x): return json.dumps(x,ensure_ascii=False,indent=2)


def _asset_strategy_markdown(asset:dict[str,Any], strategy:dict[str,Any], strategy_authority:dict[str,Any]|None=None)->str:
    core=(strategy_authority or {}).get('sections',{}).get('04_marketing_core_strategy',{})
    pos=core.get('positioning',{}) if isinstance(core,dict) else {}
    primary=pos.get('primary_conversion_proposition')
    lines=[
        '# 资产策划与决策', '',
        f"- 资产：**{asset.get('asset_name') or asset.get('asset_id')}**",
        f"- Surface / Family：{asset.get('surface')} / {asset.get('family')}",
        f"- 优先级：{asset.get('priority')}",
        f"- 消费者问题：**{asset.get('consumer_question')}**",
        f"- Decision Intent：{asset.get('decision_intent')}",
        f"- 合并的同义/同意图问题：{asset.get('merged_consumer_questions') or []}",
        f"- 战略任务：{asset.get('strategic_job')}",
        f"- Surface Need：{asset.get('surface_need')}",
        f"- Business Hypothesis：{asset.get('business_hypothesis')}",
        f"- 为什么必须存在：{asset.get('reason_to_exist')}",
        f"- 相比其他资产新增的信息：{asset.get('incremental_information')}",
    ]
    if primary: lines.append(f"- 上游核心主张：{primary}")
    if asset.get('purchase_barrier'): lines.append(f"- 购买阻力：{asset.get('purchase_barrier')}")
    if asset.get('belief_target'): lines.append(f"- 目标信念：{asset.get('belief_target')}")
    if asset.get('entry_state') or asset.get('exit_state'):
        lines += [f"- 进入状态：{asset.get('entry_state')}",f"- 期望离开状态：{asset.get('exit_state')}"]
    lines += [
        f"- RACE / Journey：{asset.get('race_stage')} / {asset.get('journey_stage')}",
        f"- 成功指标：{asset.get('success_metric') or '按该Surface实际任务选择CTR/CVR/互动/理解等指标'}",
        f"- 下一跳 / Handoff：{asset.get('handoff')}",
        '', '## 策略合同（机器可读）', '```json', _jdump(strategy), '```',
    ]
    return '\n'.join(lines)+'\n'

def _human_asset_design_card_markdown(asset:dict[str,Any], prompt_bundle:dict[str,Any], language_contract:dict[str,Any])->str:
    card=prompt_bundle.get('design_card') or {}
    task=card.get('commerce_task') or {}
    cam=card.get('composition_camera') or {}
    lm=card.get('lighting_material_cmf') or {}
    info=card.get('information_design') or {}
    identity=card.get('product_identity') or {}
    editability=card.get('editable_layer_contract') or {}
    copy=asset.get('visible_copy') or {}
    if not isinstance(copy,dict): copy={'target_copy':copy}
    zh_copy=copy.get('delivery_translation') or copy.get('zh') or copy.get('zh-CN') or copy.get('chinese')
    target_copy=copy.get('target_copy') or copy.get('copy') or copy.get('text') or copy.get('headline') or copy
    lines=[
        '# 资产人类设计卡（中文）','',
        '> 本文件是该资产的人类首读层。机器合同、ID、JSON/YAML 与完整追踪文件仍保留，但不要求用户先读。','',
        '## 1. 这张资产为什么存在','',
        f"- **消费者要确认的问题**：{task.get('consumer_question') or asset.get('consumer_question') or '—'}",
        f"- **为什么必须有**：{task.get('reason_to_exist') or asset.get('reason_to_exist') or '—'}",
        f"- **购买阻力**：{task.get('purchase_barrier') or asset.get('purchase_barrier') or '—'}",
        f"- **进入状态**：{task.get('entry_state') or asset.get('entry_state') or '—'}",
        f"- **目标信念**：{task.get('belief_target') or asset.get('belief_target') or '—'}",
        f"- **期望离开状态**：{task.get('exit_state') or asset.get('exit_state') or '—'}",
        f"- **相比其他资产新增的信息**：{task.get('incremental_information') or asset.get('incremental_information') or '—'}",
        '', '## 2. 画面与摄影执行','',
        f"- **视觉任务**：{card.get('visual_objective') or asset.get('strategic_job') or '—'}",
        f"- **完整逐资产 Art Direction**：{asset.get('asset_art_direction') or '—'}",
        f"- **视觉载体**：{(asset.get('asset_art_direction') or {}).get('visual_carrier') or '—'}",
        f"- **Product Presence / Role**：{(asset.get('asset_art_direction') or {}).get('product_presence') or card.get('product_presence') or '—'}",
        f"- **Decisive Moment**：{(asset.get('asset_art_direction') or {}).get('decisive_moment') or '—'}",
        f"- **Subject / Action / Environment / Props**：{ {k:(asset.get('asset_art_direction') or {}).get(k) for k in ('subject','action','environment','props') if (asset.get('asset_art_direction') or {}).get(k)} or '—'}",
        f"- **构图语法**：{_cn_phrase(cam.get('composition_grammar')) or (asset.get('asset_art_direction') or {}).get('composition_grammar') or '—'}",
        f"- **空间节奏 / 几何**：{(asset.get('asset_art_direction') or {}).get('spatial_rhythm') or '—'} / {(asset.get('asset_art_direction') or {}).get('layout_geometry') or (asset.get('asset_art_direction') or {}).get('relative_placement') or '—'}",
        f"- **尺度 / 纵深 / 占画**：{(asset.get('asset_art_direction') or {}).get('scale_depth') or '—'} / {(asset.get('asset_art_direction') or {}).get('product_occupancy') or '—'}",
        f"- **焦点路径 / 留白**：{(asset.get('asset_art_direction') or {}).get('focal_path') or '—'} / {(asset.get('asset_art_direction') or {}).get('negative_space') or '—'}",
        f"- **证据层级**：{(asset.get('asset_art_direction') or {}).get('evidence_hierarchy') or (asset.get('asset_art_direction') or {}).get('evidence_plane') or '—'}",
        f"- **机位 / 视角**：{_cn_phrase(cam.get('camera_or_view')) or '—'}",
        f"- **焦段**：{cam.get('focal_length_mm') or '—'}",
        f"- **光圈 / 景深**：{cam.get('aperture_dof_intent') or '—'}",
        f"- **快门 / ISO**：{cam.get('shutter_speed') or '—'} / {cam.get('iso') or '—'}",
        f"- **色温**：{lm.get('cct') or '—'}",
        f"- **光比 / Prelight**：{_cn_phrase(lm.get('exposure_ratio_plan')) or '—'}",
        f"- **CMF / 材质响应**：{_cn_phrase(lm.get('cmf') or lm.get('material_response_to_show')) or '—'}",
        f"- **商品保真模式**：{identity.get('product_fidelity') or asset.get('product_fidelity') or '—'}",
        f"- **允许进入画面的视觉元素**：{card.get('approved_visual_elements') or '—'}",
        f"- **精确执行边界**：{card.get('precision_boundaries') or '—'}",
        f"- **可编辑层**：{editability.get('editable_layers') or '—'}",
        f"- **冻结层**：{editability.get('frozen_layers') or '—'}",
        f"- **局部修订规则**：{editability.get('revision_rule') or '—'}",
        '', '## 3. 文案与语言','',
        f"- **人类交付语言**：{language_contract.get('delivery_locale') or 'zh-CN'}",
        f"- **目标市场可见语言**：{language_contract.get('primary_locale') or '按目标市场策划'}",
        f"- **目标市场原文**：{target_copy if target_copy not in ({},None,'') else '当前资产无锁定可见文案 / 待补'}",
        f"- **中文释义 / 用途**：{zh_copy or ('当前资产无外语可见文案' if target_copy in ({},None,'') else '待补中文释义；不得把未解释的外语作为人类主交付层')}",
        '', '## 4. 模型生成提示词（Model-facing）','',
        '### Model Prompt CN｜中文生成提示词','',
        '> 这是直接给图像/视频生成模型的视觉执行语言，不承载 Runtime/装配合同。','',
        '```text', prompt_bundle.get('model_prompt_cn') or prompt_bundle.get('prompt_cn') or '', '```','',
        '### Model Prompt EN｜英文生成提示词','',
        '> 英文执行说明必须保持英文；目标市场原文可作为准确可见 copy 保留，中文释义放在 Visible Copy Block。','',
        '```text', prompt_bundle.get('model_prompt_en') or prompt_bundle.get('prompt_en') or '', '```','',
        '### Visible Copy Block｜准确文案与中文释义','',
        '```json', _jdump(prompt_bundle.get('visible_copy_block') or {}), '```','',
        '### Production / Assembly Notes｜生产与装配说明','',
        '> 锁图、产品参考角色、文字渲染路线、可编辑/冻结层、Provider 与后期装配规则在此管理，不污染 Model Prompt。','',
        '```json', _jdump(prompt_bundle.get('production_assembly_notes') or {}), '```','',
        f"- **Model Prompt Readiness**：{prompt_bundle.get('model_prompt_status') or (prompt_bundle.get('prompt_consumption_audit') or {}).get('status') or '—'}",
        '', '## 5. 成功与承接','',
        f"- **成功指标**：{task.get('success_metric') or asset.get('success_metric') or '按当前展示位置的真实任务选择指标'}",
        f"- **下一资产 / 下一动作承接**：{task.get('handoff') or asset.get('handoff') or '—'}",
    ]
    return '\n'.join(str(x) for x in lines)+'\n'


def _visual_spec_markdown(asset:dict[str,Any], visual:dict[str,Any], strategy_authority:dict[str,Any]|None=None)->str:
    master=(strategy_authority or {}).get('sections',{}).get('05_visual_photography_strategy',{})
    art=asset.get('asset_art_direction') or {}
    brief=asset.get('creative_brief') or {}
    presence=art.get('product_presence') or asset.get('product_presence') or {}

    def fmt(value:Any)->str:
        if value in (None,'',[],{}): return '—'
        if isinstance(value,dict):
            for key in ('cn','zh','zh-CN','CN'):
                if value.get(key) not in (None,'',[],{}): return str(value.get(key))
            return _jdump(value)
        if isinstance(value,list): return '；'.join(str(x) for x in value)
        return str(value)

    rows=[
        ('商业任务',asset.get('strategic_job')),
        ('消费者问题',asset.get('consumer_question')),
        ('视觉载体',art.get('visual_carrier') or asset.get('information_assetization',{}).get('representation')),
        ('创意核心',art.get('creative_thesis') or art.get('thesis')),
        ('视觉语言',art.get('visual_language') or art.get('image_language') or art.get('style')),
        ('关键瞬间',art.get('decisive_moment')),
        ('产品出现 / 角色',presence),
        ('主体',art.get('subject')),
        ('动作',art.get('action') or art.get('decisive_action')),
        ('环境',art.get('environment')),
        ('道具',art.get('props') or art.get('scene_props')),
        ('人物 / Casting',art.get('human_context') or art.get('people') or art.get('casting')),
        ('构图语法',art.get('composition_grammar') or art.get('composition') or art.get('spatial_grammar') or brief.get('composition') or master.get('composition')),
        ('空间节奏',art.get('spatial_rhythm') or art.get('space_rhythm')),
        ('相对位置 / 几何',art.get('layout_geometry') or art.get('relative_placement') or art.get('placement_relationships')),
        ('尺度 / 纵深',art.get('scale_depth') or art.get('scale_relationships') or art.get('depth_program')),
        ('产品占画',art.get('product_occupancy') or art.get('product_frame_ratio') or art.get('product_scale_percent')),
        ('焦点路径',art.get('focal_path')),
        ('负空间',art.get('negative_space') or art.get('copy_negative_space')),
        ('证据层级',art.get('evidence_hierarchy') or art.get('proof_mechanism') or art.get('evidence_plane')),
        ('文字安全区',art.get('copy_zone') or art.get('text_zone') or art.get('safe_zone')),
        ('字体 / 信息层级',art.get('typography')),
        ('输出规格',art.get('output_spec') or art.get('canvas') or art.get('format_spec')),
        ('完成质感 / Post Look',art.get('post_look') or art.get('grade') or art.get('finishing_look')),
        ('商品 Fidelity',asset.get('product_fidelity')),
        ('生产方式',asset.get('production_mode')),
    ]
    lines=['# 视觉 / Art Direction 执行合同','', '## 资产级完整视觉决策','']
    for label,value in rows:
        if value not in (None,'',[],{}): lines.append(f'- **{label}**：{fmt(value)}')

    photo_rows=[
        ('机位 / 视角',art.get('camera_or_view') or art.get('preferred_view') or art.get('view')),
        ('焦段 / 镜头',art.get('focal_length_mm') or art.get('lens')),
        ('镜头家族',art.get('lens_family')),
        ('透视 / 投影',art.get('perspective') or art.get('projection')),
        ('机位参数',art.get('camera_position')),
        ('对焦 / 景深',art.get('focus_dof')),
        ('灯光',art.get('lighting') or art.get('lighting_program') or brief.get('lighting') or master.get('lighting_framework')),
        ('Prelight',art.get('prelight') or art.get('prelight_plan')),
        ('CMF',art.get('cmf') or art.get('material_program') or brief.get('color') or master.get('cmf')),
        ('材质响应',art.get('material_response') or art.get('surface_behavior')),
        ('Palette / HEX',art.get('palette_hex') or art.get('palette') or art.get('color_world') or master.get('palette_hex')),
        ('色彩管理',art.get('color_management') or master.get('color_management')),
    ]
    if any(v not in (None,'',[],{}) for _,v in photo_rows):
        lines += ['', '## 摄影 / 灯光 / CMF（仅当前路线相关时）','']
        for label,value in photo_rows:
            if value not in (None,'',[],{}): lines.append(f'- **{label}**：{fmt(value)}')

    video_rows=[
        ('时长 / 节奏',art.get('motion_timing') or art.get('timing') or art.get('duration') or art.get('shot_timing')),
        ('镜头顺序',art.get('shot_sequence') or art.get('shot_plan') or art.get('storyboard')),
        ('镜头运动',art.get('camera_motion') or art.get('motion_program')),
        ('转场 / 音频',art.get('transition_audio') or art.get('transitions') or art.get('audio_direction')),
    ]
    if str(asset.get('asset_type') or '').upper()=='VIDEO' or any(v not in (None,'',[],{}) for _,v in video_rows):
        lines += ['', '## 动态执行（Video 相关时）','']
        for label,value in video_rows:
            if value not in (None,'',[],{}): lines.append(f'- **{label}**：{fmt(value)}')

    why_rows=[
        ('视觉载体 WHY',art.get('visual_carrier_why')),
        ('构图 WHY',art.get('composition_why')),
        ('产品出现 WHY',art.get('product_presence_why') or (presence.get('presence_why') if isinstance(presence,dict) else None)),
        ('摄影 / 媒介 WHY',art.get('media_route_why') or art.get('photography_why')),
    ]
    if any(v not in (None,'',[],{}) for _,v in why_rows):
        lines += ['', '## 为什么这样设计','']
        for label,value in why_rows:
            if value not in (None,'',[],{}): lines.append(f'- **{label}**：{fmt(value)}')

    lines += [
        '', '## 文化、事实与执行边界','',
        f"- **文化 / 人物执行**：{fmt(visual.get('culture_implications'))}",
        f"- **允许进入画面的视觉元素**：{fmt(visual.get('approved_visual_elements'))}",
        f"- **精确边界**：{fmt(visual.get('precision_boundaries'))}",
        '', '## 为什么这张资产必须存在','',
        f"这张资产用于回答：**{asset.get('consumer_question') or '当前购买决策问题'}**。产品是否出现、信息关系、构图、人物/道具/场景与可见文案都应服务这个购买判断，而不是为了补图位或复用模板。",
        '', '## 完整 Agent Art Direction 原始对象（可编辑源）','```json',_jdump(art),'```',
    ]
    return '\n'.join(str(x) for x in lines)+'\n'

def compile_asset_packages(root:Path,assets:list[dict[str,Any]],product:dict[str,Any],target:dict[str,Any],culture:dict[str,Any],language_contract:dict[str,Any],locale_profiles:dict[str,Any],photography:dict[str,Any]|None=None,provider_preferences:dict[str,Any]|None=None,strategy_authority:dict[str,Any]|None=None,source_product_assets:list[dict[str,Any]]|None=None)->dict[str,Any]:
    base=Path(root); index=[]
    for raw_asset in assets:
        # Asset packages may be compiled from the full architecture or from a direct/legacy asset row.
        # v0.6.0 guarantees that the production contract still receives a decision-specific visual
        # grammar and a semantic editable/frozen layer contract instead of silently falling back to
        # a generic provider envelope.
        asset=dict(raw_asset)
        if not asset.get('decision_intent'):
            asset['decision_intent']=classify_decision_intent(asset.get('consumer_question') or asset.get('strategic_job') or '')
        if not asset.get('decision_topic'):
            asset['decision_topic']=asset.get('consumer_question') or asset.get('strategic_job') or asset.get('decision_intent')
        if not asset.get('visual_production_signature'):
            asset['visual_production_signature']=_visual_production_signature(asset.get('decision_intent'),asset.get('decision_topic'),asset.get('surface'),asset.get('production_mode'))
        if not asset.get('editable_layer_contract'):
            asset['editable_layer_contract']=_editable_layer_contract(asset.get('production_mode'),asset.get('product_fidelity'))
        d=base/asset['asset_id']; d.mkdir(parents=True,exist_ok=True)
        manifest={k:asset.get(k) for k in ['asset_id','asset_name','asset_type','status','surface','family','consumer_question','decision_intent','decision_topic','merged_consumer_questions','strategic_job','surface_need','business_hypothesis','reason_to_exist','incremental_information','production_mode','product_fidelity','priority','dependencies','source_ids','claim_ids','listing_reference','success_metric','race_stage','information_assetization','product_presence','asset_art_direction','surface_copy_budget','surface_native_contract','creative_direction','visual_expression_variant','product_visual_intelligence','creative_anchor_plan','visual_production_signature','editable_layer_contract']}
        manifest.update({'platform':target.get('platform_family'),'site':target.get('site'),'market':target.get('market'),'languages':language_contract.get('visible_copy_locales',[]),'source_product_assets':list(source_product_assets or [])})
        _write(d/'00_asset_manifest.yaml',yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False))
        strategy_content_rows=[r for r in ((((strategy_authority or {}).get('sections',{}) or {}).get('06_platform_content_matrix',[])) or []) if r.get('asset_id')==asset.get('asset_id')]
        surface_production_contracts=[r.get('surface_production_contract') for r in strategy_content_rows if r.get('surface_production_contract')]
        strategy={k:asset.get(k) for k in ['consumer_question','decision_intent','merged_consumer_questions','purchase_barrier','belief_target','strategic_job','surface_need','business_hypothesis','journey_stage','entry_state','exit_state','race_stage','reason_to_exist','incremental_information','handoff','success_metric']}
        _write(d/'01_strategy.md',_asset_strategy_markdown(asset,strategy,strategy_authority))
        asset_photo_reasoning=next((r for r in (((strategy_authority or {}).get('sections',{}).get('05_visual_photography_strategy',{}) or {}).get('asset_parameter_reasoning',[]) or []) if r.get('asset_id')==asset.get('asset_id')),None)
        visual={'asset_art_direction':asset.get('asset_art_direction',{}),'creative_brief':asset.get('creative_brief',{}),'approved_visual_elements':asset.get('approved_visual_elements',[]),'precision_boundaries':asset.get('precision_boundaries',[]),'culture_implications':culture.get('visual_implications',[]),'locale_profiles':locale_profiles.get('profiles',[]),'asset_photography_reasoning':asset_photo_reasoning,'visual_production_signature':asset.get('visual_production_signature',{}),'editable_layer_contract':asset.get('editable_layer_contract',{}),'source_product_assets':list(source_product_assets or [])}
        _write(d/'02_visual_spec.md',_visual_spec_markdown(asset,visual,strategy_authority))
        if asset.get('asset_type')=='IMAGE' and photography:
            photography_contract={**photography,'asset_reasoning':asset_photo_reasoning}
        elif asset.get('asset_type')=='IMAGE' and asset_photo_reasoning:
            photography_contract={'status':'STRATEGY_DERIVED_PHOTOGRAPHY_PLAN','authority':'ADVISORY_UNLESS_REAL_CAPTURE_EXPLICITLY_SELECTED','prelight_required':False,'project_completion_blocking':False,'asset_type':'IMAGE','asset_reasoning':asset_photo_reasoning,'reason':'This is an optional execution recommendation. It becomes capture-critical only when real-photo production is explicitly selected; stylized/illustrated/3D/generated directions do not need to imitate real photography.'}
        else:
            photography_contract={'status':'NOT_APPLICABLE_OR_NOT_SUPPLIED','asset_type':asset.get('asset_type'),'reason':'03_photography_contract.json is retained for package continuity; populate with executable photography parameters when this asset requires photography.'}
        _write(d/'03_photography_contract.json',_jdump(photography_contract))
        _write(d/'04_layout_contract.json',_jdump({'surface':asset.get('surface'),'visible_copy':asset.get('visible_copy',{}),'language_contract':language_contract,'surface_production_contracts':surface_production_contracts,'surface_native_contract':asset.get('surface_native_contract',{}),'surface_copy_budget':asset.get('surface_copy_budget',{}),'product_presence':asset.get('product_presence',{}),'information_assetization':asset.get('information_assetization',{}),'visual_expression_variant':asset.get('visual_expression_variant',{}),'visual_production_signature':asset.get('visual_production_signature',{}),'editable_layer_contract':asset.get('editable_layer_contract',{}),'copy_visual_alignment':{'decision_answer':asset.get('incremental_information') or asset.get('belief_target') or asset.get('strategic_job'),'rule':'Visible copy must point to, label or explain the actual decision-critical evidence shown in the frame; decorative copy detached from visual evidence is not an acceptable substitute.'}}))
        try:
            prompt_bundle=compile_asset_prompt(asset,product,target,culture,language_contract,locale_profiles,photography_contract,strategy_authority,source_product_assets)
        except Exception as exc:
            prompt_bundle={
                'status':'OPTIONAL_PROMPT_NOT_READY',
                'design_card':{
                    'commerce_task':{k:asset.get(k) for k in ['consumer_question','reason_to_exist','purchase_barrier','entry_state','belief_target','exit_state','incremental_information','success_metric','handoff']},
                    'visual_objective':asset.get('strategic_job'),
                    'composition_camera':{},'lighting_material_cmf':{},
                    'information_design':{'locked_visible_copy':asset.get('visible_copy') or {}},
                    'product_identity':{'product_fidelity':asset.get('product_fidelity') or 'REFERENCE_GUIDED','rule':'Source files are design references by default; visual re-rendering/stylization is allowed unless a locked-source mode was explicitly selected.'},
                    'editable_layer_contract':asset.get('editable_layer_contract') or {},
                },
                'prompt_cn':'','prompt_en':'','deterministic_copy_overlay':asset.get('visible_copy') or {},
                'parameter_trace':[],
                'prompt_consumption_audit':{'status':'NOT_READY','project_completion_blocking':False,'missing_decisions':['PROMPT_COMPILE_ERROR'],'error':str(exc)},
                'machine_visual_contract':{},'renderer_recipe':{},'qa_target_contract':{},
            }
        _write(d/'00_HUMAN_DESIGN_CARD_CN.md',_human_asset_design_card_markdown(asset,prompt_bundle,language_contract))
        _write(d/'05_prompt_CN.txt',prompt_bundle['prompt_cn'])
        _write(d/'06_prompt_EN.txt',prompt_bundle['prompt_en'])
        _write(d/'12_design_card.json',_jdump(prompt_bundle['design_card']))
        _write(d/'14_visible_copy_block.json',_jdump(prompt_bundle.get('visible_copy_block') or {'raw':asset.get('visible_copy') or {}}))
        _write(d/'15_production_assembly_notes.json',_jdump(prompt_bundle.get('production_assembly_notes') or {}))
        _write(d/'13_prompt_contract.json',_jdump({'status':prompt_bundle.get('status'),'model_prompt_status':prompt_bundle.get('model_prompt_status'),'project_completion_blocking':False,'design_card':prompt_bundle.get('design_card') or {},'model_prompt_cn':prompt_bundle.get('model_prompt_cn') or prompt_bundle.get('prompt_cn') or '','model_prompt_en':prompt_bundle.get('model_prompt_en') or prompt_bundle.get('prompt_en') or '','canonical_prompt_cn':prompt_bundle.get('prompt_cn') or '','canonical_prompt_en':prompt_bundle.get('prompt_en') or '','visible_copy_block':prompt_bundle.get('visible_copy_block') or {},'production_assembly_notes':prompt_bundle.get('production_assembly_notes') or {},'legacy_copy_overlay':prompt_bundle.get('deterministic_copy_overlay') or {},'parameter_trace':prompt_bundle.get('parameter_trace') or [],'prompt_consumption_audit':prompt_bundle.get('prompt_consumption_audit') or {},'machine_visual_contract':prompt_bundle.get('machine_visual_contract') or {},'renderer_recipe':prompt_bundle.get('renderer_recipe') or {},'qa_target_contract':prompt_bundle.get('qa_target_contract') or {}}))
        signature=asset.get('visual_production_signature') or {}
        edit_contract=asset.get('editable_layer_contract') or {}
        fidelity_line=('Explicit locked-source mode: use the supplied master as an immutable product layer.' if str(asset.get('product_fidelity') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} else 'Reference-guided mode: source files guide the design; redraw/rerender/restyle/recompose is allowed. Keep verified facts/claims honest; pixel matching and photorealism are not required.')
        _write(d/'07_generation_guidance.txt','目标结果：\n- '+asset.get('strategic_job','Resolve the consumer question')+'\n- 视觉信息语法：'+str(signature.get('composition_grammar') or 'decision-led composition')+'\n- 决策关键证据平面：'+str(signature.get('evidence_plane') or asset.get('consumer_question'))+'\n- 差异化轴：'+str(signature.get('differentiation_axis') or 'decision-specific evidence relationship')+'\n\n产品 Fidelity 执行：\n- '+fidelity_line+'\n\n允许的语义元素：\n- '+('\n- '.join(map(str,asset.get('approved_visual_elements',[]))) or 'Use only elements required by the approved creative brief.')+'\n\n精确边界：\n- '+('\n- '.join(map(str,asset.get('precision_boundaries',[]))) or 'Preserve product truth, locked copy and approved product identity.')+'\n\n可局部修改层：\n- '+('\n- '.join(map(str,edit_contract.get('editable_layers',[]))) or 'No local editable layers declared; request an explicit scoped revision.')+'\n\n冻结层：\n- '+('\n- '.join(map(str,edit_contract.get('frozen_layers',[]))) or 'Product truth and locked copy remain frozen.')+'\n')
        _write(d/'08_copy.md','# 锁定的可见文案\n\n> 目标市场可见文案按策划使用目标语言；人类交付 HTML 必须同时显示中文释义 / 用途。\n\n```json\n'+_jdump(asset.get('visible_copy',{}))+'\n```\n')
        route=route_production({**asset,'source_product_assets':list(source_product_assets or [])},provider_preferences)
        production_quality_targets={'product_fidelity':asset.get('product_fidelity'),'source_product_assets':list(source_product_assets or []),'visual_production_signature':asset.get('visual_production_signature',{}),'editable_layer_contract':asset.get('editable_layer_contract',{}),'copy_visual_alignment':{'locked_visible_copy':asset.get('visible_copy',{}),'decision_answer':asset.get('incremental_information') or asset.get('belief_target') or asset.get('strategic_job')},'provider_observation_targets':['product_identity_preserved','decision_answer_visible','surface_contract_met','copy_visual_alignment','photography_cmf_alignment','visual_differentiation_preserved'],'canonical_prompt_contract':prompt_bundle.get('machine_visual_contract') or {},'parameter_trace':prompt_bundle.get('parameter_trace') or [],'deterministic_copy_overlay':prompt_bundle.get('deterministic_copy_overlay') or {},'renderer_recipe':prompt_bundle.get('renderer_recipe') or {},'qa_target_contract':prompt_bundle.get('qa_target_contract') or {},'prompt_generation_readiness':(prompt_bundle.get('prompt_consumption_audit') or {}).get('status'),'prompt_generation_readiness_blocks_asset_delivery':False}
        _write(d/'09_production_notes.md','# 生产说明\n\n## 执行路由\n```json\n'+_jdump(route)+'\n```\n\n## 展示位置生产合同（Surface）\n```json\n'+_jdump(surface_production_contracts)+'\n```\n\n## 生产质量目标\n```json\n'+_jdump(production_quality_targets)+'\n```\n\n- 产品保真：'+str(asset.get('product_fidelity'))+'\n- 展示位置（Surface）：'+str(asset.get('surface'))+'\n')
        _write(d/'10_source_trace.md','# 来源追踪\n\n```json\n'+_jdump({'source_ids':asset.get('source_ids',[]),'claim_ids':asset.get('claim_ids',[]),'listing_reference':asset.get('listing_reference',[])})+'\n```\n')
        # Additive only: preserve the alpha6 asset package and attach upstream strategy WHY/context.
        if strategy_authority:
            sections=strategy_authority.get('sections',{})
            marketing=sections.get('04_marketing_core_strategy',{}) or {}
            pos=marketing.get('positioning',{}) or {}
            listing=marketing.get('listing_strategy',{}) or {}
            visual_master=sections.get('05_visual_photography_strategy',{}) or {}
            market=(sections.get('03_platform_region_audience_culture_insight',{}) or {}).get('market',{}) or {}
            content_rows=[r for r in sections.get('06_platform_content_matrix',[]) if r.get('asset_id')==asset.get('asset_id') or r.get('topic')==asset.get('consumer_question')]
            shot_rows=[r for r in visual_master.get('shot_list',[]) if r.get('asset_id')==asset.get('asset_id')]
            culture_rows=[r for r in sections.get('08_culture_adaptation_checklist',[]) if r.get('result') in {'APPLY','REVIEW','BASELINE'}]
            decision_index=[]
            for drow in strategy_authority.get('decision_index',[]) or []:
                if drow.get('domain') in {'POSITIONING','MESSAGE_HIERARCHY','VISUAL','MARKET'}:
                    decision_index.append(drow)
                elif drow.get('domain')=='ASSET' and (drow.get('what') in {asset.get('asset_id'),asset.get('asset_name')} or asset.get('asset_id') in str(drow.get('what'))):
                    decision_index.append(drow)
            trace={
                'strategy_status':strategy_authority.get('status'),
                'decision_contract':strategy_authority.get('strategy_decision_contract'),
                'asset_id':asset.get('asset_id'),
                'consumer_question':asset.get('consumer_question'),
                'reason_to_exist':asset.get('reason_to_exist'),
                'positioning':{
                    'target_user':pos.get('target_user'),
                    'primary_conversion_proposition':pos.get('primary_conversion_proposition'),
                    'message_hierarchy':pos.get('message_hierarchy',[]),
                    'objection_reducers':pos.get('objection_reducers',[]),
                },
                'listing_relevance':{
                    'title_job':listing.get('title_job'),
                    'hero_job':listing.get('hero_job'),
                    'pdp_sequence':[r for r in listing.get('pdp_sequence',[]) if r.get('question')==asset.get('consumer_question') or r.get('job') in {asset.get('strategic_job'),asset.get('belief_target')}],
                },
                'market_decisions':market.get('strategic_insights',[])[:4],
                'visual_execution':{
                    'style':visual_master.get('style'),'style_why':visual_master.get('style_why'),
                    'palette_hex':visual_master.get('palette_hex'),'cmf':visual_master.get('cmf'),
                    'shot_rows':shot_rows,
                },
                'platform_content_rows':content_rows,
                'culture_adaptation':culture_rows,
                'relevant_strategy_decisions':decision_index,
                'trace_scope':'FOCUSED_TO_THIS_ASSET; upstream full strategy remains in project strategy package.',
            }
            _write(d/'11_strategy_authority_trace.json',_jdump(trace))
        else:
            _write(d/'11_strategy_authority_trace.json',_jdump({'strategy_status':'NOT_SUPPLIED','asset_id':asset.get('asset_id'),'consumer_question':asset.get('consumer_question'),'reason_to_exist':asset.get('reason_to_exist'),'surface_need':asset.get('surface_need'),'business_hypothesis':asset.get('business_hypothesis'),'trace_scope':'PRESERVED_PACKAGE_SLOT; compile with Strategy Authority to populate upstream decision trace.'}))
        index.append({'asset_id':asset['asset_id'],'path':str(d),'status':asset.get('status'),'production_mode':asset.get('production_mode'),'provider':route.get('provider'),'legacy_package_preserved':True})
    _write(base/'ASSET_PACKAGE_INDEX.json',_jdump({'assets':index,'count':len(index),'legacy_alpha6_package_preserved':True,'legacy_package_preserved':True,'required_legacy_files':REQUIRED_ASSET_FILES,'additive_capability_files':['00_HUMAN_DESIGN_CARD_CN.md','12_design_card.json','13_prompt_contract.json','14_visible_copy_block.json','15_production_assembly_notes.json']}))
    return {'status':'COMPILED','asset_count':len(index),'index':index}


REQUIRED_ASSET_FILES=[
    '00_asset_manifest.yaml','00_HUMAN_DESIGN_CARD_CN.md','01_strategy.md','02_visual_spec.md','03_photography_contract.json','04_layout_contract.json',
    '08_copy.md','09_production_notes.md','10_source_trace.md','11_strategy_authority_trace.json','12_design_card.json','14_visible_copy_block.json','15_production_assembly_notes.json'
]
OPTIONAL_PRODUCTION_FILES=['05_prompt_CN.txt','06_prompt_EN.txt','07_generation_guidance.txt','13_prompt_contract.json']
_INTERNAL_PROMPT_TOKENS=['authority_hash','READY_REVIEW','INVALIDATED','claim_ids','source_ids','project_state','revision']

def validate_asset_packages(root:Path)->dict[str,Any]:
    base=Path(root); errors=[]; assets=[]
    idx=base/'ASSET_PACKAGE_INDEX.json'
    if not idx.exists(): return {'pass':False,'errors':['missing ASSET_PACKAGE_INDEX.json'],'assets':[]}
    data=json.loads(idx.read_text(encoding='utf-8'))
    for row in data.get('assets',[]):
        d=base/row['asset_id']; missing=[f for f in REQUIRED_ASSET_FILES if not (d/f).exists()]
        if missing: errors.append(f"{row['asset_id']}: missing {missing}")
        for fn in ['05_prompt_CN.txt','06_prompt_EN.txt']:
            fp=d/fn
            if fp.exists():
                text=fp.read_text(encoding='utf-8')
                leaked=[x for x in _INTERNAL_PROMPT_TOKENS if x in text]
                if leaked: errors.append(f"{row['asset_id']} {fn}: internal-state leakage {leaked}")
        optional_missing=[f for f in OPTIONAL_PRODUCTION_FILES if not (d/f).exists()]
        assets.append({'asset_id':row['asset_id'],'missing':missing,'optional_production_missing':optional_missing})
    return {'pass':not errors,'errors':errors,'assets':assets,'count':len(assets),'optional_production_files':OPTIONAL_PRODUCTION_FILES,'prompt_generation_files_block_asset_delivery':False}
