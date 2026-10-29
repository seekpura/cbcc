from __future__ import annotations
from typing import Any
from .models import stable_hash
from .tools.video import timing
from .prompt_compiler import _cn_phrase


def _asset_for_video(assets:list[dict[str,Any]]|None, family:str, surface:str, index:int):
    rows=[a for a in (assets or []) if str(a.get('family')).upper()==str(family).upper() or str(a.get('surface')).upper()==str(surface).upper()]
    return rows[index % len(rows)] if rows else None



def _decision_derived_fallback_shots(j:dict[str,Any], source:dict[str,Any], q:str, proof:Any, dur:float, family:str)->tuple[list[dict[str,Any]],str]:
    """Graceful fallback only. Prefer explicit Agent-authored video_jobs/shots.

    Unlike the legacy universal five-beat template, this fallback selects a narrative carrier from
    the actual decision job and source asset. It is deliberately simple and records its source.
    """
    carrier=str(j.get('narrative_carrier') or source.get('visual_carrier') or (source.get('asset_art_direction') or {}).get('visual_carrier') or '').upper()
    blob=' '.join(str(x or '') for x in [q,proof,source.get('decision_intent'),source.get('strategic_job'),source.get('reason_to_exist')]).lower()
    if family=='CREATOR_AFFILIATE' or 'CREATOR' in carrier or 'POV' in carrier:
        weights=[.25,.38,.25,.12]; narrative='CREATOR_CONTEXT_DEMO'
        specs=[
          ('CREATOR_CONTEXT','Open inside the real use/problem context; the creator is already doing something, not presenting a title card.'),
          ('CREATOR_DEMO','Show the product/action relationship in first person and make the relevant mechanism/use visible.'),
          ('CREATOR_PROOF_OR_OBJECTION',f'Answer the decisive question with supported evidence: {proof}'),
          ('NATIVE_HANDOFF','Close naturally into the relevant shop/next action without resetting into a corporate packshot.')
        ]
    elif any(k in blob for k in ['size','fit','compatib','dimension','capacity','scale']):
        weights=[.18,.42,.25,.15]; narrative='FIT_SCALE_PROOF'
        specs=[
          ('DECISION_QUESTION',f'Make the fit/scale question immediately visible: {q}'),
          ('MEASURED_PROOF',f'Show the truthful size/fit/compatibility relationship: {proof}'),
          ('USE_CONTEXT','Show the product in the relevant real context so the proof can be judged.'),
          ('DECISION_CLOSE','Hold the resolved fit/scale answer and hand off to the correct commerce action.')
        ]
    elif any(k in blob for k in ['package','contents','receive','included','unbox','trust']):
        weights=[.2,.36,.29,.15]; narrative='PACKAGE_TRUST'
        specs=[
          ('ARRIVAL_CONTEXT','Open on what the shopper actually receives.'),
          ('CONTENTS_REVEAL','Reveal verified package contents/packaging clearly and without invented accessories.'),
          ('DETAIL_TRUST',f'Hold the decisive packaging/detail proof: {proof}'),
          ('EXPECTATION_CLOSE','Close on the accurate purchase expectation and next action.')
        ]
    elif any(k in blob for k in ['texture','material','feel','fabric','gel','liquid','finish']):
        weights=[.2,.4,.27,.13]; narrative='TACTILE_MATERIAL'
        specs=[
          ('TACTILE_OPEN','Open on the material/texture behavior itself, using motion and light that make it judgeable.'),
          ('MATERIAL_PROOF',f'Make the supported material/use property visible: {proof}'),
          ('PRODUCT_CONTEXT','Connect the tactile evidence back to the product and real use context.'),
          ('BELIEF_HOLD','Hold the resolved material belief long enough to understand, then hand off.')
        ]
    else:
        weights=[.23,.37,.27,.13]; narrative='DECISION_SPECIFIC'
        specs=[
          ('DECISION_OPEN',f'Open on the concrete shopper tension/question: {q}'),
          ('VISIBLE_ANSWER',f'Make the supported decision answer visible through the most relevant action/evidence: {proof}'),
          ('PRODUCT_OR_USE_CONTEXT','Connect the evidence to the product/use context; product presence follows the authored asset role rather than a mandatory packshot.'),
          ('DECISION_HANDOFF','Hold the resolved belief and move into the relevant commerce action.')
        ]
    shots=[]
    used=0.0
    for idx,(shot,job) in enumerate(specs):
        seconds=round(dur*weights[idx],2) if idx<len(specs)-1 else round(dur-used,2)
        used+=seconds
        shots.append({'shot':shot,'seconds':seconds,'job':job,'visual':'Author scene/action/camera/copy/audio from this decision job; do not substitute generic B-roll.'})
    return shots,narrative

def build_video_creator_plan(project_id:str, content_objects:list[dict[str,Any]], shopper_questions:list[str], language_contract:dict[str,Any], video_jobs:list[dict[str,Any]]|None=None, *, assets:list[dict[str,Any]]|None=None, creative_council:dict[str,Any]|None=None)->dict[str,Any]:
    jobs=list(video_jobs or [])
    if not jobs:
        for o in content_objects:
            if o.get('family') not in {'VIDEO','CREATOR_AFFILIATE','LIVE'}: continue
            related=_asset_for_video(assets,o.get('family'),o.get('surface'),len(jobs))
            q=(related or {}).get('consumer_question') or (shopper_questions[min(len(jobs),len(shopper_questions)-1)] if shopper_questions else 'What should the shopper understand?')
            jobs.append({'family':o.get('family'),'surface':o.get('surface'),'objective':o.get('curation_job'),'shopper_question':q,'duration_seconds':15 if o.get('family')!='LIVE' else 30,'source_asset':related})
    selected=(creative_council or {}).get('selected_direction') or {}
    rows=[]
    for i,j in enumerate(jobs):
        source=j.get('source_asset') or _asset_for_video(assets,j.get('family'),j.get('surface'),i) or {}
        vid='VID-'+stable_hash([project_id,j.get('family'),j.get('surface'),j.get('shopper_question'),i])[:10].upper(); dur=float(j.get('duration_seconds',15))
        q=j.get('shopper_question') or source.get('consumer_question') or 'What should the shopper understand?'
        decision=source.get('decision_intent') or j.get('decision_intent') or 'DECISION_SUPPORT'
        proof=source.get('incremental_information') or source.get('belief_target') or j.get('proof') or 'approved product-specific evidence'
        family=j.get('family','VIDEO')
        if j.get('shots'):
            shots=j['shots']; narrative_source='EXPLICIT_AGENT_VIDEO_JOB'; narrative_carrier=j.get('narrative_carrier') or 'AGENT_AUTHORED'
        else:
            shots,narrative_carrier=_decision_derived_fallback_shots(j,source,q,proof,dur,family); narrative_source='DECISION_DERIVED_RUNTIME_FALLBACK'
        creator_contract=None
        if family=='CREATOR_AFFILIATE':
            creator_contract={
              'voice':'first-person natural demonstration, not corporate ad read','opening':'specific problem/use context in first seconds','product_handling':'match the chosen creator/visual medium and product-reference policy; exact pack pixels only when explicitly locked','proof':'show, then explain; do not claim beyond approved evidence','cta':'native recommendation / shop action after proof','rights_fields':['creator_usage_rights','paid_usage_rights','whitelisting_spark_ads_authorization','usage_term','territory']
            }
        live_contract=None
        if family=='LIVE':
            live_contract={'loop':['HOOK_OR_QUERY','DEMO_OR_PROOF','OBJECTION_RESPONSE','OFFER_OR_CHOICE','CTA','RESET'],'host_support':['truth sheet','claim boundaries','FAQ','offer state','inventory/variant state'],'principle':'Live is an interactive decision loop, not a linear 15-second ad stretched longer.'}
        rows.append({
            'video_id':vid,'family':family,'surface':j.get('surface','PDP_VIDEO'),'objective':j.get('objective'),'shopper_question':q,'decision_intent':decision,
            'creative_direction_id':source.get('creative_direction',{}).get('direction_id') or selected.get('direction_id'),'creative_thesis':source.get('creative_direction',{}).get('creative_thesis') or selected.get('creative_thesis'),
            'hook':j.get('hook') or q,'duration_seconds':dur,'timing':timing(shots,dur),'shots':shots,'narrative_carrier':narrative_carrier,'narrative_source':narrative_source,'fixed_five_beat_template':False,
            'voice_locale':j.get('voice_locale') or language_contract.get('primary_locale'),'subtitle_locales':j.get('subtitle_locales') or language_contract.get('script_subtitle_locales',[]) or language_contract.get('visible_copy_locales',[]),
            'voiceover_style':j.get('voiceover_style') or ('creator-native conversational' if family=='CREATOR_AFFILIATE' else 'product-decision concise'),
            'on_screen_text_rule':'Use only locked approved copy; subtitles/labels must not cover decision-critical product/action evidence.','cta':j.get('cta'),'claim_ids':j.get('claim_ids',[]) or source.get('claim_ids',[]),'source_ids':j.get('source_ids',[]) or source.get('source_ids',[]),
            'creator_contract':creator_contract,'live_contract':live_contract,'source_asset_id':source.get('asset_id')
        })
    return {'status':'COMPILED' if rows else 'NOT_REQUIRED','dynamic_count':len(rows),'fixed_duration_authority':False,'assets':rows,'principle':'Video/creator/live plans are built from the shopper decision and native interaction pattern, not from a generic hook-proof-CTA template.'}


def _vmerge(base:dict[str,Any]|None, override:dict[str,Any]|None)->dict[str,Any]:
    out=dict(base or {})
    for k,v in (override or {}).items():
        if isinstance(v,dict) and isinstance(out.get(k),dict):
            out[k]=_vmerge(out[k],v)
        elif v not in (None,'',[],{}):
            out[k]=v
    return out


def _vtxt(v:Any)->str:
    if v in (None,'',[],{}): return ''
    import json
    return json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else str(v)


def _prompt_camera(camera:dict[str,Any]|None)->dict[str,Any]:
    c=camera or {}
    keys=('focal_length_mm','lens_family','shot_size','angle','camera_height','focus_plane','aperture','iso','shutter')
    return {k:c.get(k) for k in keys if c.get(k) not in (None,'',[],{})}


def _prompt_lighting(lighting:dict[str,Any]|None)->dict[str,Any]:
    l=lighting or {}
    keys=('key','fill','rim','background','cct','ratio','exposure_ratio_plan','prelight_plan','highlight_policy','white_balance')
    return {k:l.get(k) for k in keys if l.get(k) not in (None,'',[],{})}


def _prompt_cmf(cmf:dict[str,Any]|None)->dict[str,Any]:
    c=cmf or {}
    keys=('color','primary','secondary','accent','background','text','palette','material','finish','surface_behavior','capture_implications','post_implications')
    return {k:c.get(k) for k in keys if c.get(k) not in (None,'',[],{})}


def _prompt_material(material:dict[str,Any]|None)->dict[str,Any]:
    m=material or {}
    out={k:m.get(k) for k in ('material','finish','surface_behavior') if m.get(k) not in (None,'',[],{})}
    pre=m.get('prelight_plan') or {}; pol=m.get('polarization_plan') or {}; col=m.get('color_consistency_plan') or {}; exp=m.get('exposure_ratio_plan') or {}
    if isinstance(pre,dict):
        val=pre.get('objective') or pre.get('instruction')
        if val: out['prelight']=val
    elif pre not in (None,'',[],{}): out['prelight']=pre
    if isinstance(exp,dict):
        val=exp.get('declared_ratio') or exp.get('target_start') or exp.get('measurement')
        if val: out['exposure_ratio']=val
    elif exp not in (None,'',[],{}): out['exposure_ratio']=exp
    if isinstance(pol,dict):
        val=pol.get('capture_rule') or pol.get('test') or pol.get('applicable')
        if val: out['polarization']=val
    elif pol not in (None,'',[],{}): out['polarization']=pol
    if isinstance(col,dict):
        val=col.get('capture_rule') or col.get('reference') or col.get('output_rule')
        if val: out['color_consistency']=val
    elif col not in (None,'',[],{}): out['color_consistency']=col
    return out


def _prompt_inclusive(inclusive:dict[str,Any]|None)->dict[str,Any]:
    i=inclusive or {}
    keys=('skin_tone_metering','skin_tone_exposure','hair_texture','hair_and_styling','body_age_disability','casting_boundary','representation_principle','ai_bias_controls')
    return {k:i.get(k) for k in keys if i.get(k) not in (None,'',[],{})}


def _vcn(value:Any)->Any:
    """Chinese human/render companion for CBCC-owned video production prose."""
    if value in (None,'',[],{}): return value
    if isinstance(value,list): return [_vcn(v) for v in value]
    if isinstance(value,dict):
        key_map={
          'spatial_rhythm':'空间节奏','composition_grammar':'构图语法','viewpoint':'视角','scene_role':'场景角色',
          'direction_route':'创意路线','anti_layout_repeat':'反重复版式约束','camera_continuity':'摄影机连续性',
          'lighting_continuity':'灯光连续性','cmf_continuity':'CMF 连续性','material_continuity':'材质连续性',
          'inclusive_human_execution':'包容性人物执行','continuity_rule':'连续性规则','shot_job':'镜头任务',
          'visual_action':'画面动作','material':'材质','finish':'表面处理','surface_behavior':'表面响应',
          'prelight_plan':'Prelight 预演','lighting_diagram':'灯光图','exposure_ratio_plan':'曝光 / 光比方案',
          'polarization_plan':'偏振方案','color_consistency_plan':'颜色一致性方案','focal_length_mm':'焦段',
          'shot_size':'景别','angle':'机位 / 角度','aperture':'光圈','iso':'ISO','shutter':'快门',
          'cct':'色温（CCT）','ratio':'光比','key':'主光','fill':'补光','rim':'轮廓光',
          'background':'背景','white_balance':'白平衡','body_age_disability':'体型 / 年龄 / 残障',
          'ai_bias_controls':'AI 偏见控制','skin_tone_metering':'肤色测光','hair_texture':'发质呈现',
          'wardrobe_makeup':'服装 / 妆发','status':'状态','camera_height':'机位高度','focus_plane':'对焦平面',
          'lens_family':'镜头族','direction':'方向','modifier':'控光附件','highlight_policy':'高光策略',
          'color':'颜色','missing':'待补项','capture_implications':'拍摄影响','post_implications':'后期影响',
          'objective':'目标','frames':'参考帧','acceptance':'验收条件','boundary':'边界','camera_axis':'相机参考轴',
          'negative_fill':'负补光','background_light':'背景光','instruction':'执行说明','declared_ratio':'声明光比',
          'measurement':'测量方法','why':'为什么','applicable':'适用性','test':'测试方法','reference':'参考基准',
          'capture_rule':'拍摄规则','output_rule':'输出规则','activation_basis':'触发依据','intent':'资产意图',
          'route':'创意路线','context_role':'语境角色','intersectionality_context':'交叉性语境',
          'intersectionality_notes':'交叉性维度','skin_tone_exposure':'肤色曝光','metering_priority':'测光优先级',
          'highlight_protection':'高光保护','hair_and_styling':'发质 / 造型','hair':'发质','wardrobe':'服装',
          'makeup':'妆容','rule':'规则','casting_boundary':'选角边界','representation_principle':'表征原则',
          'review_required':'需要人工复核','p0_rule':'P0 规则','preferred_view':'优先视角','direction_thesis':'方向母命题',
          'same_layout_guard':'避免同版式约束'
        }
        return {key_map.get(str(k),_cn_phrase(str(k))):_vcn(v) for k,v in value.items() if v not in (None,'',[],{})}
    raw=str(value)
    # First reuse shared photography/CMF translations.
    shared=_cn_phrase(raw)
    if shared != raw:return shared
    exact={
      'approved product-specific evidence':'已批准的商品特定证据',
      'Show the decision situation before explanatory copy; no generic title card.':'先让购买决策情境本身可见，再补解释性文字；不要用通用标题卡开场。',
      'Introduce the real product in the action/evidence relationship.':'把真实商品放进动作 / 证据关系中自然揭示，不做脱离语境的硬切 Packshot。',
      'Use mechanism, scale, fit, use or proof appropriate to the decision intent; do not substitute generic B-roll.':'根据当前决策意图选择机理、尺度、适配、使用或证据画面；不得用无关通用 B-roll 代替。',
      'Hold the evidence long enough to understand; locked copy labels what is visible.':'证据画面停留足够时间让人理解；锁定文案只标注真实可见内容。',
      'CTA is subordinate to product truth and the resolved decision.':'行动引导服从商品真源和已经解决的购买问题，不抢占证据。',
      'Use supplied real product masters/references as identity authority. Do not redraw packaging, logo, printed copy, geometry, proportions or product color.':'仅在显式锁定源图时，以已提供的商品母版作为不可修改的源图层；普通参考设计模式不适用此约束。',
      'Reference-guided mode: supplied product/source files guide design and identity cues; redraw, rerender, stylize, illustrate or recompose as the selected direction requires. Do not present creative changes as verified product facts.':'参考设计模式：产品/源文件用于指导设计与必要的身份线索；可按方向重绘、重渲染、风格化、插画化或重新构图。不得把创作性变化当成已验证商品事实。',
      'Explicit locked-source mode: preserve the supplied product master as an immutable source layer; do not redraw that layer.':'显式锁定源图模式：保留已提供的产品母图为不可修改的源图层，不得重绘该图层。',
      'Vary framing/motion only as required by this shot job; preserve product identity, material response, white balance/brand color and selected creative system across the sequence.':'只根据当前镜头任务改变景别与运动；整段视频保持商品身份、材质响应、白平衡 / 品牌色和已选创意系统的一致性。',
      'Represent the approved audience context without using identity dimensions as automatic behavior predictions.':'呈现已批准的人群语境，但不得把身份维度直接推断成购买行为。',
      'If people/hands/body relation appear in any asset, inclusive photography and AI-bias QA are P0 production requirements.':'只要画面出现人物、手部或身体关系，包容性摄影与 AI 偏见检查即为 P0 生产要求。',
      'PARTIAL':'部分信息待补','APPLICABLE_P0':'适用，P0 执行','true':'是','false':'否',
      'capture baseline without polarization':'先拍无偏振基准帧',
      'Use polarization only when it removes obstructive glare without erasing truthful gloss, transparency, print or material cues.':'仅当偏振能去除遮挡信息的眩光、且不抹掉真实光泽、透明度、印刷或材质线索时使用。',
      'Use supplied neutral/product color reference or capture one during prelight.':'使用已提供的中性 / 商品颜色参考；若没有，则在 Prelight 阶段拍摄参考帧。',
      'Lock WB/exposure reference for a shot family; recapture reference after material/source/background changes.':'同一镜头家族锁定白平衡 / 曝光参考；材质、光源或背景变化后重新拍参考帧。',
      'Compare hero/detail/variant frames against the same product-color reference before surface exports.':'导出不同展示位置前，用同一商品颜色参考检查主视觉、细节和变体镜头。',
      'Cross-asset color drift changes perceived shade/material and can create expectation/return risk.':'跨资产颜色漂移会改变消费者对色泽 / 材质的判断，并可能造成预期与退货风险。',
      'Lock material truth, label readability and repeatable highlight geometry before hero capture.':'主镜头拍摄前先锁定材质真实性、标签可读性和可重复的高光几何。',
      'neutral reference / product color frame':'中性参考 / 商品颜色参考帧',
      'front-label readability frame':'正面标签可读性参考帧',
      'edge/material-response frame':'边缘 / 材质响应参考帧',
      'required copy remains legible':'必要文字保持可读',
      'material still reads as the supplied CMF':'材质表现仍与已提供 CMF 一致',
      'critical highlight is below clipping':'关键高光不过曝',
      'background/product edge separation is repeatable':'背景 / 商品边缘分离可重复',
      'Prelight validates the real object. If supplied CMF text conflicts with the real pack, the real pack wins and Strategy Authority should be revised.':'Prelight 用于验证真实物体；若 CMF 文本与真实包装冲突，以真实包装为准，并回修策略权威。',
      '0° reference / exact physical angle comes from supplied camera contract':'0° 参考轴；实际物理角度以摄影合同为准',
      'Record actual source positions/distances/power after the accepted prelight; do not infer missing geometry from this conceptual diagram.':'Prelight 通过后记录真实灯位、距离与功率；不得从概念图臆测缺失的物理几何。',
      'medium / medium-close interaction frame':'中景 / 中近景交互画面',
      'tight proof/detail with enough context to understand the evidence':'紧凑证据 / 细节景别，同时保留足够语境理解证据',
      '50–85mm contextual product/human lens family':'50–85mm 商品 / 人物语境镜头族',
      'interaction/decision plane; preserve natural body/hand/product proportions':'交互 / 决策平面；保持身体、手部与商品的自然比例',
      'represent a range of Malaysian skin tones and hair textures without tokenism':'呈现马来西亚真实多样的肤色与发质，避免符号化或刻板化代表。',
      'preserve natural skin texture':'保留真实自然的肌肤纹理，不做磨皮式美化。',
      'HUMAN_CONTEXT_ACTION':'真实人物 / 使用语境动作',
      'EVIDENCE_MECHANISM':'证据关系 / 因果证明',
      'PRODUCT_TRUTH_EDITORIAL':'商品真源 / 编辑式呈现',
      'MATERIAL_SENSORY_OBJECT':'材质 / 感官对象',
      'NATIVE_HOOK':'原生开场',
      'PRODUCT_OR_ACTION_REVEAL':'商品 / 动作揭示',
      'PROOF_DEMO':'证据演示',
      'BELIEF_CLOSE':'信念收束',
      'CTA_HANDOFF':'行动承接',
      'f/8–f/11 starting range':'f/8–f/11 起始范围',
      '~2:1 starting ratio':'约 2:1 起始光比',
      'creator-native conversational':'创作者原生、自然对话式',
      'product-evidence concise':'以商品证据为中心、简洁克制',
      'True':'是','False':'否','color':'颜色','material':'材质','finish':'表面处理',
      'IDENTIFY':'商品识别','RELEVANCE':'相关性','USAGE':'使用方法','PROOF':'证据','PERFORMANCE_PROOF':'性能证据',
      'ethnicity × gender × age × income × geography':'族裔 × 性别 × 年龄 × 收入 × 地域',
      'Do not inherit the previous asset composition. Preserve design-system tokens but rebuild hierarchy from this asset decision job.':'不要继承上一资产的构图；保留设计系统的一致性，但必须根据当前购买任务重新建立信息层级与版式。',
      'product optical center / interaction decision plane':'商品光学中心 / 交互决策平面',
      'current decision-relevant product / skin-tone / evidence plane':'当前决策相关的商品 / 肤色 / 证据平面',
      '45° camera-left-front, 30–45° above decision plane':'相机左前方 45°，高于决策平面 30–45°',
      'large soft source':'大型柔光源',
      'camera-right-front neutral reflector, one stop under key':'相机右前方中性反光板，比主光低约 1 档',
      'protect label, skin tone and package highlights from clipping while retaining truthful gloss':'保护标签、肤色与包装高光不过曝，同时保留真实光泽',
      'usually not required':'通常不需要',
      'minimal category context; keep only cues needed for identification':'最小化品类语境，只保留识别所需线索',
      'specific credible real-use context':'具体、可信的真实使用语境',
      'hands / body relation / real-use context':'手部 / 身体关系 / 真实使用语境',
      'top-down system relationship':'俯视系统关系构图',
      'action-led decisive use moment':'动作主导的真实使用关键瞬间',
      'choose viewpoint around real interaction/contact point':'围绕真实交互 / 接触点选择机位',
    }
    if raw in exact:return exact[raw]
    prefixes=[
      ('Open on a concrete tension/action/question: ','以具体张力 / 动作 / 问题开场：'),
      ('Make the decision answer visible: ','让当前购买答案直接可见：'),
      ('Land the target belief: ','收束到目标信念：'),
      ('Hand off to the correct commerce action/surface.','承接到正确的商业动作 / 展示位置。'),
    ]
    for a,b in prefixes:
        if raw.startswith(a):return b+raw[len(a):]
    if raw.endswith(' starting range'):
        return raw[:-len(' starting range')]+' 起始范围'
    if raw.endswith(' starting ratio'):
        return raw[:-len(' starting ratio')]+' 起始光比'
    # Direction thesis families generated by CBCC.
    if 'synthesize Human Use Decisive Moment + Information Hierarchy as Visual Form' in raw:
        return '将“真实使用关键瞬间”与“信息层级视觉化”结合：用准确的手部 / 身体 / 日常流程 / 操作瞬间解决尺度、适配、使用或相关性问题；在文字叠加前，先用空间层级表达主信息、证据和文案预算。'
    if 'synthesize Evidence Relationship / Causal Proof + Category Convention Reframing' in raw:
        return '将“证据关系 / 因果证明”与“品类惯例重构”结合：让已验证的机理、规格、配方事实、兼容关系或测试条件能够明确归属于商品，并用新的空间机制替代过度使用的品类视觉套路。'
    if 'synthesize Product Identity' in raw or 'product identity' in raw.casefold() and len(raw)>80:
        return '围绕真实商品身份和第一购买理由建立主视觉；先保证包装、比例、标签与核心价值一眼可识别，再组织其他信息。'
    return raw


def _vrender_safe(value:Any)->Any:
    """Remove runtime identifiers / project lead-ins from model-facing video instructions."""
    import re
    if isinstance(value,dict):
        out={}
        for k,v in value.items():
            lk=str(k).lower()
            if lk in {'asset_id','video_id','direction_id','source_asset_id','project_id','variant_id'} or lk.endswith('_id'):
                continue
            cleaned=_vrender_safe(v)
            if cleaned not in (None,'',[],{}): out[k]=cleaned
        return out
    if isinstance(value,list):
        rows=[_vrender_safe(v) for v in value]
        return [v for v in rows if v not in (None,'',[],{})]
    if isinstance(value,str):
        text=value
        text=re.sub(r'\b(?:AST|VID|DIR|PROJECT)-[A-Z0-9_-]+\b','',text,flags=re.I)
        text=re.sub(r'^For [^,\n]+,\s*(?=(?:synthesize|use|make|show|build|frame|compose)\b)','',text,flags=re.I)
        text=re.sub(r'\s{2,}',' ',text).strip(' ;,')
        return text
    return value


def enrich_video_plan_with_strategy(plan:dict[str,Any], strategy_authority:dict[str,Any]|None, *, source_product_assets:list[dict[str,Any]]|None=None, culture:dict[str,Any]|None=None)->dict[str,Any]:
    """Bind Strategy Authority visual/photography decisions into each video and shot.

    Business metadata (video IDs, RACE, KPI) stays outside render prompts. Camera/light/CMF,
    product identity, inclusive photography and shot actions become executable render contracts.
    """
    out={**(plan or {})}; rows=[]
    sections=(strategy_authority or {}).get('sections') or {}; visual=sections.get('05_visual_photography_strategy') or {}
    reasoning=visual.get('asset_parameter_reasoning') or []; inclusive=visual.get('inclusive_photography') or {}
    master_material=visual.get('material_lighting_profile') or {}; master_camera=visual.get('camera') or {}; master_lighting=visual.get('lighting_framework') or {}; master_cmf=visual.get('cmf') or visual.get('palette_hex') or {}
    for raw in out.get('assets') or []:
        v=dict(raw); source_id=v.get('source_asset_id'); ar=next((x for x in reasoning if x.get('asset_id')==source_id),{})
        camera=_vmerge(master_camera, ar.get('camera_choice') if isinstance(ar.get('camera_choice'),dict) else {})
        lighting=_vmerge(master_lighting, ar.get('lighting_choice') if isinstance(ar.get('lighting_choice'),dict) else {})
        material=_vmerge(master_material, ar.get('material_lighting_profile') if isinstance(ar.get('material_lighting_profile'),dict) else {})
        cmf=_vmerge(master_cmf if isinstance(master_cmf,dict) else {'palette':master_cmf}, ar.get('cmf_choice') if isinstance(ar.get('cmf_choice'),dict) else {})
        # Videos may not have an IMAGE asset_parameter_reasoning row. In that case adapt the
        # master strategy recommendation by the video's decision job rather than falling back to
        # an identity/product-still focal length for every shot.
        intent=str(v.get('decision_intent') or '').upper()
        if not ar and intent in {'USAGE','RELEVANCE','FIT_WEAR','SIZE_FIT','SENSORY_PREP'}:
            camera=_vmerge(camera,{'focal_length_mm':'65mm equivalent starting recommendation','lens_family':'50–85mm contextual product/human lens family','shot_size':'medium / medium-close interaction frame','camera_height':'interaction/decision plane; preserve natural body/hand/product proportions'})
        elif not ar and intent in {'PROOF','MATERIAL_SENSORY','INGREDIENT_COMPOSITION','PERFORMANCE_PROOF'}:
            camera=_vmerge(camera,{'focal_length_mm':'85–100mm equivalent starting recommendation','shot_size':'tight proof/detail with enough context to understand the evidence'})
        render_thesis=_vrender_safe(v.get('creative_thesis'))
        render_inclusive=_vrender_safe(inclusive)
        render_culture=_vrender_safe((culture or {}).get('visual_implications') or [])
        locked_source=any(bool(x.get('pixel_lock')) or str(x.get('fidelity_mode') or '').upper() in {'LOCKED_PIXEL','LOCKED_SOURCE_COMPOSITE','COMPOSITE'} for x in (source_product_assets or []) if isinstance(x,dict))
        product_reference_rule=('Explicit locked-source mode: preserve the supplied product master as an immutable source layer; do not redraw that layer.' if locked_source else 'Reference-guided mode: supplied product/source files guide design and identity cues; redraw, rerender, stylize, illustrate or recompose as the selected direction requires. Do not present creative changes as verified product facts.')
        master={
          'creative_thesis':render_thesis,'camera':camera,'lighting':lighting,'cmf':cmf,
          'material_response':{'material':material.get('material'),'finish':material.get('finish'),'surface_behavior':material.get('surface_behavior'),'prelight_plan':material.get('prelight_plan'),'lighting_diagram':material.get('lighting_diagram'),'exposure_ratio_plan':material.get('exposure_ratio_plan'),'polarization_plan':material.get('polarization_plan'),'color_consistency_plan':material.get('color_consistency_plan')},
          'inclusive_photography':render_inclusive,'culture_visual':render_culture,
          'product_identity':{'source_product_assets':list(source_product_assets or []),'mode':'LOCKED_SOURCE_COMPOSITE' if locked_source else 'REFERENCE_GUIDED','rule':product_reference_rule}
        }
        enriched=[]
        for shot in v.get('shots') or []:
            s=dict(shot); s['render_contract']={
              'shot_job':_vrender_safe(s.get('job')),'visual_action':_vrender_safe(s.get('visual')),'camera_continuity':camera,'lighting_continuity':lighting,'cmf_continuity':cmf,
              'material_continuity':master['material_response'],'inclusive_human_execution':render_inclusive,
              'continuity_rule':'Vary framing/motion only as required by this shot job; preserve product identity, material response, white balance/brand color and selected creative system across the sequence.'
            }; enriched.append(s)
        v['shots']=enriched; v['visual_render_contract']=master
        prompt_camera=_prompt_camera(camera); prompt_lighting=_prompt_lighting(lighting); prompt_cmf=_prompt_cmf(cmf); prompt_material=_prompt_material(master['material_response']); prompt_inclusive=_prompt_inclusive(render_inclusive)
        lines=[
          '[VIDEO RENDER OBJECTIVE]',
          f"Creative thesis: {_vtxt(render_thesis)}",
          f"Native hook / visual opening: {_vtxt(v.get('hook'))}",
          '', '[MASTER CAMERA / LIGHT / CMF]',
          f"Camera: {_vtxt(prompt_camera)}", f"Lighting: {_vtxt(prompt_lighting)}", f"CMF: {_vtxt(prompt_cmf)}", f"Material response: {_vtxt(prompt_material)}",
          f"Inclusive human photography: {_vtxt(prompt_inclusive)}", f"Cultural visual constraints: {_vtxt(master['culture_visual'])}",
          '', '[PRODUCT REFERENCE / FIDELITY]', master['product_identity']['rule'],
          '', '[SHOT PROGRAM]'
        ]
        for idx,s in enumerate(enriched,1):
            lines += [f"Shot {idx} · {s.get('shot')} · {s.get('seconds')}s",f"Action/job: {_vtxt(_vrender_safe(s.get('job')))}",f"Visual: {_vtxt(_vrender_safe(s.get('visual')))}",'Continuity: follow the master camera / light / CMF / material / inclusive-human contract above; vary only what this shot job requires.']
        lines += ['', '[TEXT / AUDIO BOUNDARY]','Do not ask the video model to invent or retype packaging/final marketing copy. Keep subtitle/label safe zones clear; exact copy and subtitles are composited from the approved copy contract. Use only licensed/original/platform-commercial-use audio.', '', '[DO NOT GENERATE]','No unsupported efficacy, ingredients, tests, certifications, before/after, body results, package text, physical effects or generic B-roll that is unrelated to the decision job.']
        v['canonical_video_prompt_en']='\n'.join(lines)+'\n'
        v['canonical_video_prompt_cn']='\n'.join([
          '【视频生成目标】',f"创意母命题：{_vtxt(_vcn(render_thesis))}",f"原生开场：{_vtxt(_vcn(v.get('hook')))}",'','【主摄影 / 灯光 / CMF】',f"摄影机：{_vtxt(_vcn(prompt_camera))}",f"灯光：{_vtxt(_vcn(prompt_lighting))}",f"CMF：{_vtxt(_vcn(prompt_cmf))}",f"材质响应：{_vtxt(_vcn(prompt_material))}",f"包容性人物摄影：{_vtxt(_vcn(prompt_inclusive))}",f"文化视觉约束：{_vtxt(_vcn(master['culture_visual']))}",'','【产品参考 / 保真策略】',_vtxt(_vcn(master['product_identity']['rule'])),'','【分镜程序】'] + [line for idx,s in enumerate(enriched,1) for line in [f"镜头 {idx} · {_vcn(s.get('shot'))} · {s.get('seconds')}s",f"动作 / 任务：{_vtxt(_vcn(_vrender_safe(s.get('job'))))}",f"画面：{_vtxt(_vcn(_vrender_safe(s.get('visual'))))}",'连续性：继承上方主摄影 / 灯光 / CMF / 材质 / 包容性人物合同；仅根据本镜头任务改变必要的景别、运动和画面动作。']] + ['','【文字 / 音频边界】','不要让视频模型重写包装文字或最终营销文案；为字幕/标签预留安全区，精确文字从已批准 Copy 后期合成。仅使用原创、已授权或平台可商用音频。','','【禁止生成】','不得编造功效、成分、检测、认证、before/after、人体结果、包装文字、物理效果或与购买任务无关的通用 B-roll。'])+'\n'
        v['parameter_trace']=[
          {'parameter':'camera','source':'Strategy §5 asset/master photography','target':'visual_render_contract + every shot render_contract'},
          {'parameter':'lighting/CCT/ratio/prelight/polarization','source':'Strategy §5 material-lighting profile','target':'visual_render_contract + every shot render_contract'},
          {'parameter':'CMF/material/color consistency','source':'Strategy §5 CMF','target':'sequence continuity'},
          {'parameter':'inclusive photography/culture','source':'Strategy §3/5/8','target':'human shots'},
          {'parameter':'product reference / fidelity policy','source':'Product Truth / source assets','target':'all product shots'},
        ]
        rows.append(v)
    out['assets']=rows; out['strategy_visual_binding']='BOUND_V065' if rows else 'NOT_REQUIRED'
    return out
