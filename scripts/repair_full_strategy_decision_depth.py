from pathlib import Path

P=Path('runtime/cbcc/strategy_depth.py')
text=P.read_text(encoding='utf-8')

anchor="""        third['platform_audience_culture_rows']=culture_depth.get('platform_audience_culture_rows') or []
        s['03_platform_region_audience_culture_insight']=third
        if not s.get('08_culture_adaptation_checklist'):
            s['08_culture_adaptation_checklist']=culture_depth.get('adaptation_rows') or []
"""
insert="""        third['platform_audience_culture_rows']=culture_depth.get('platform_audience_culture_rows') or []
        # FULL human/runtime contract exposes the same localization content under the canonical key;
        # compatibility aliases remain additive rather than hiding the content one level down.
        third['adaptation_rows']=culture_depth.get('adaptation_rows') or third.get('culture_adaptation_rows') or []
        s['03_platform_region_audience_culture_insight']=third
        if not s.get('08_culture_adaptation_checklist'):
            s['08_culture_adaptation_checklist']=culture_depth.get('adaptation_rows') or []

        # FULL core strategy must expose message hierarchy and an explicit WHY at the final section level.
        positioning=core.get('positioning') or {}
        if positioning:
            core['message_hierarchy']=core.get('message_hierarchy') or positioning.get('message_hierarchy') or []
            if not positioning.get('why'):
                target_user=positioning.get('target_user') or '当前目标用户'
                tension=positioning.get('consumer_tension') or '当前购买问题'
                primary=positioning.get('primary_conversion_proposition') or '当前第一购买理由'
                positioning['why']=(
                    f'面向{target_user}，当前张力是“{tension}”；因此先用“{primary}”建立第一购买理由，'
                    '再按相关性→证据→风险澄清→行动展开。这样能同时降低移动端认知负荷、避免卖点平均用力，'
                    '并让Listing、内容、视觉和Prompt共享同一个购买决策主线。文化差异只改变表达/人物/场景，不创造不存在的产品价值。'
                )
            core['positioning']=positioning
        s['04_marketing_core_strategy']=core

        # FULL visual strategy cannot stop at style adjectives. Supply executable, explicitly provisional
        # starting contracts when exact brand/platform values are not source-bound yet.
        vis=s.get('05_visual_photography_strategy') or {}
        visual_request=request.get('visual_strategy') or {}
        product=request.get('product') or {}
        target=request.get('target') or {}
        supplied_palette=(visual_request.get('palette_hex') or visual_request.get('palette') or product.get('brand_colors') or product.get('colors'))
        if not vis.get('palette_hex'):
            vis['palette_hex']=supplied_palette or {
                'primary':'待从真实包装/品牌母版提取并锁定HEX',
                'secondary':'待从真实包装/品牌母版或当前创意方向提取并锁定HEX',
                'background':'#F7F6F2（FULL起始建议；与真实包装冲突时由商品真源覆盖）',
                'text':'#1F2926（FULL起始建议；最终按实际背景验证普通文字≥4.5:1）',
            }
        if not vis.get('composition'):
            vis['composition']={
                'authority':'BUYER_DECISION_DRIVEN_MOBILE_FIRST',
                'primary_image':'商品身份优先；主体比例/位置由真实包装几何与移动端识别任务锁定，保留清晰负空间，不为“高级感”牺牲产品可读性。',
                'human_context':'人物只在适配/使用/尺度/肤质等决策需要时出现；避免大头模板，优先真实关系与可读留白。',
                'evidence_graphic':'证据关系优先于装饰；数字/事实层级清晰，不用卡片堆叠替代信息设计。',
                'variation_rule':'不同购买问题必须产生不同的空间关系/证据平面；不能九张同构图只换标题。',
                'status':'FULL_STARTING_RECOMMENDATION; asset-level Design Card may override',
            }
        if not vis.get('color_management'):
            vis['color_management']={
                'output_space':'sRGB',
                'product_color':'真实包装/商品颜色为source-bound；禁止为了统一视觉而漂移品牌绿、肤色、材质色。',
                'skin_tone':'人物资产以真实肤色为测光/调色参考，避免自动美白、灰肤或过饱和。',
                'white_balance':'以灰卡/真实商品色/肤色Prelight锁定；氛围色温不能覆盖产品真色。',
                'status':'EXECUTION_STARTING_CONTRACT; final values are prelight/source dependent',
            }
        if not vis.get('platform_dimensions'):
            dims=(target.get('dimensions') or target.get('image_dimensions') or target.get('image_size') or target.get('canvas'))
            vis['platform_dimensions']=dims or {
                'planning':'按当前Platform × Site × Surface分别锁定，不用一个尺寸覆盖所有Surface。',
                'exact_submission':'待查证：发布前从当前官方规则/已验证Platform Pack确认尺寸、比例、安全区、时长和封面限制。',
            }
        # Keep aliases directly consumable by Prompt/HTML instead of burying them in photography_execution.
        photo=vis.get('photography_execution') or {}
        if not vis.get('camera') and isinstance(photo,dict): vis['camera']=photo.get('camera') or {'authority':'按asset_parameter_reasoning/类目Camera Plan逐资产选择；人物/商品/微距不共用同一焦段。'}
        if not vis.get('lens'):
            vis['lens']={'authority':'按决策任务选择正常到中长焦；人物/手部/商品几何避免广角畸变；具体焦段进入逐资产parameter reasoning。'}
        s['05_visual_photography_strategy']=vis

        # FULL always tells the operator what additional evidence would materially improve/release the work.
        last=s.get('09_risk_measurement_priority_next_steps') or {}
        info=s.get('01_information_completeness_assumptions_decisions') or {}
        if not last.get('next_information_needed') and not last.get('next_information'):
            pending=[]
            for item in (info.get('pending_confirmations') or [])[:10]:
                pending.append({'item':item,'priority':'P0/P1按影响判定','why':'补齐后可收紧当前假设、Claim或执行参数。'})
            if not pending:
                pending=[
                    {'item':'发布前核验当前平台×站点×Surface的官方尺寸/时长/封面/音乐/提交规则','priority':'P0/P1','why':'动态平台规则不能由历史知识冒充当前发布权威。'},
                    {'item':'把仍为“待查证”的Claim/法规/文化判断补成可追溯来源','priority':'P0','why':'强监管、文化敏感和硬宣称必须在发布前闭合证据。'},
                    {'item':'如进入实拍/合成，完成真实商品母版、色卡/灰卡和人物/材质Prelight','priority':'P0/P1','why':'把当前策略级摄影建议锁成可重复生产参数，并保护商品色/肤色/材质真实性。'},
                ]
            last['next_information_needed']=pending
        s['09_risk_measurement_priority_next_steps']=last
"""
if 'FULL core strategy must expose message hierarchy' not in text:
    if anchor not in text:
        raise SystemExit('v0.6.24 FULL projection anchor not found')
    text=text.replace(anchor,insert,1)

# FULL keeps the user's explicit nine-domain human contract visible. This is a content-completeness
# authority, not a fixed page/layout template; TASK_SCOPED still renders only relevant domains.
old_headings="""    heading_names={
      '1':'信息完整度 / 假设 / 决策','2':'产品真相与价值边界','3':'市场 / 平台 / 人群 / 文化洞察',
      '4':'核心商业策略','5':'视觉 / 摄影 / CMF / 资产策略','6':'平台内容与 Surface 执行',
      '7':'RACE传播框架执行表','8':'族裔文化适配检查表','9':'合规、文化敏感、风险、评估与 P0/P1/P2 下一步'}
"""
new_headings="""    heading_names={
      '1':'信息完整度、待确认清单、假设与决策日志',
      '2':'产品真实事实审计与卖点分级表',
      '3':'平台 × 区域 × 人群 × 族裔文化洞察',
      '4':'营销框架与核心策略',
      '5':'视觉总策略与拍摄执行清单',
      '6':'分平台内容矩阵表',
      '7':'RACE传播框架执行表',
      '8':'族裔文化适配检查表',
      '9':'合规、文化敏感与风险清单；评估指标与A/B测试建议；P0/P1/P2执行优先级与下一步需补充信息'}
"""
if old_headings in text:
    text=text.replace(old_headings,new_headings,1)
elif "'2':'产品真实事实审计与卖点分级表'" not in text:
    raise SystemExit('FULL heading_names anchor not found')

P.write_text(text,encoding='utf-8')
print('FULL strategy decision-depth repair applied')
