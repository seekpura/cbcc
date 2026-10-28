from __future__ import annotations
from typing import Any
import json
from .category_strategy import category_execution_profile, category_commerce_profile, classify_decision_intent
from .evidence_reconciliation import reconcile_category_commerce, validate_category_offer_with_evidence, platform_category_intersection


def _lst(v):
    if v is None: return []
    return v if isinstance(v,list) else [v]


def _clean(v):
    return '' if v is None else str(v).strip()


def _why(what:str, why:str, *, evidence=None, consumer='', platform='', culture='', business='', execution='', measurement=''):
    return {
        'what':what,'why':why,'evidence':_lst(evidence),
        'consumer_logic':consumer,'platform_logic':platform,'culture_logic':culture,
        'business_logic':business,'execution':execution,'measurement':measurement,
    }


def _has(obj, *keys):
    cur=obj
    for k in keys:
        if not isinstance(cur,dict) or cur.get(k) in (None,'',[],{}): return False
        cur=cur[k]
    return True


def _flatten_facts(product:dict[str,Any]):
    rows=[]
    skip={'name','brand','category','primary_conversion_proposition','secondary_reasons','trust_drivers','objection_reducers','verified_selling_point'}
    for k,v in product.items():
        if str(k).startswith('_') or k in skip or v in (None,'',[],{}): continue
        if isinstance(v,dict):
            for sk,sv in v.items():
                if sv not in (None,'',[],{}): rows.append((f'{k}.{sk}',sv))
        else: rows.append((k,v))
    return rows


def _fact_type(key:str):
    k=key.casefold()
    if any(x in k for x in ['formula','ingredient','active']): return 'FORMULA_FACT'
    if any(x in k for x in ['capacity','net_content','weight','volume','size','dimension']): return 'SIZE_CAPACITY_SPEC'
    if any(x in k for x in ['strap','adjust','fit','wear']): return 'FIT_ADJUSTMENT'
    if any(x in k for x in ['water_repellent','weather','rain','water_resistant']): return 'WEATHER_BOUNDARY'
    if any(x in k for x in ['care','wash','clean','maintenance']): return 'CARE_MAINTENANCE'
    if any(x in k for x in ['airtight','seal','leak','closure','lid']): return 'CLOSURE_SEAL'
    if any(x in k for x in ['stack','nest','storage','organization','pocket']): return 'STORAGE_ORGANIZATION'
    if any(x in k for x in ['compatib','oven','freezer','microwave','dishwasher']): return 'COMPATIBILITY'
    if any(x in k for x in ['texture','finish','material','fabric','shell','lining','transparent']): return 'SENSORY_OR_MATERIAL'
    if any(x in k for x in ['product_type','format','form','shape']): return 'PRODUCT_FORMAT'
    if any(x in k for x in ['usage','direction','routine']): return 'USAGE_FACT'
    if any(x in k for x in ['package','packaging','included','contents']): return 'PACKAGE_FACT'
    if any(x in k for x in ['skin','audience','target']): return 'INTENDED_CONTEXT'
    return 'PRODUCT_FACT'


def _fact_role(ftype:str):
    return {
        'FORMULA_FACT':'证明配方构成或浓度事实；是否升级成功效利益取决于已批准Claim。',
        'SIZE_CAPACITY_SPEC':'帮助用户把尺寸/容量映射到真实使用空间、携带或份量需求，降低买错规格。',
        'FIT_ADJUSTMENT':'帮助用户判断穿戴/佩戴比例、调节范围或人体关系；需要视觉尺度证据时应进入资产任务。',
        'WEATHER_BOUNDARY':'用于说明已验证耐候/防泼水能力及其限制，避免把有限能力升级为完全防护。',
        'CARE_MAINTENANCE':'帮助用户理解清洁/洗护/维护成本和限制，减少购买后的使用落差。',
        'CLOSURE_SEAL':'帮助用户判断闭合/密封/防漏结构与边界，功能展示应依赖真实结构或经验证测试。',
        'STORAGE_ORGANIZATION':'帮助用户理解收纳、堆叠、内袋/组织与空间效率。',
        'COMPATIBILITY':'属于硬适配事实；决定能否购买/使用，应优先于装饰性卖点。',
        'SENSORY_OR_MATERIAL':'帮助用户预期真实触感/材质/外观，降低认知落差。',
        'PRODUCT_FORMAT':'让用户快速理解“它是什么”以及如何归类。',
        'USAGE_FACT':'降低使用门槛，连接购买前理解与购买后正确使用。',
        'PACKAGE_FACT':'降低“收到什么”的不确定性并减少误购/退货。',
        'INTENDED_CONTEXT':'定义适用语境，但不能自动扩展成未被证据支持的效果。',
        'PRODUCT_FACT':'作为真实产品认知的一部分，仅在能改变购买决策时进入前台传播。',
    }.get(ftype,'作为真实产品认知的一部分。')


def build_information_depth(request:dict[str,Any], research_gate:dict[str,Any]):
    product=request.get('product') or {}; target=request.get('target') or {}
    domains=[
        ('产品真源', bool(product.get('name')) and len(_flatten_facts(product))>0, '支撑所有后续定位、文案、视觉与资产，不完整时只允许做不依赖缺失事实的策略。', '补齐包装/规格/配方/使用/实拍等真实资料'),
        ('Claim证据', bool(request.get('claims')), '决定哪些利益表达可以公开使用，以及证据型资产能做到多强。', '补齐Claim、证据来源与批准状态'),
        ('市场/竞品数据', bool(request.get('market_rows') or request.get('market_file') or request.get('market_keyword_rows') or request.get('market_review_rows') or request.get('competitor_listing_rows') or request.get('market_competitor_listing_rows')), '决定市场结构、搜索需求、Customer Voice、竞品Message/Offer/Proof和差异化是否有数据支撑；不同数据类型只能支持各自范围内的结论。', '提供当前市场导出、关键词、竞品Listing/Review或可信研究'),
        ('价格/利润数据', bool(request.get('offer_economics')), '决定价格、优惠、联盟佣金、投放空间和SKU角色是否经济可行。', '提供售价、采购/履约/平台/税/退款/广告等成本'),
        ('受众/文化证据', bool(request.get('audience_culture')), '决定语言、人物、场景、服化道和文化表达能否真正本地化。', '提供目标人群、语言、文化/族裔/交叉性证据'),
        ('平台/站点目标', bool(target.get('platform_family') and target.get('site') and target.get('market')), '决定Surface、内容形式和最终提交规则。', '补齐平台、站点、市场、Program/Category/Locale'),
        ('Listing输入', bool(request.get('listing_input')), '决定搜索意图、字段规划、信息顺序和PDP/详情页转换架构。', '提供关键词、现有Listing或计划字段'),
        ('视觉/摄影输入', bool(request.get('photography_contract') or request.get('visual_strategy') or request.get('creative_directions')), '决定视觉系统是否能直接交给摄影/设计/生成团队执行。', '提供真实产品图、参考角色、CMF/摄影限制或创意方向'),
        ('经营反馈/实验', bool(request.get('ad_analysis') or request.get('feedback_rows') or request.get('experiment') or any((request.get('offer_economics') or {}).get(k) for k in ['behavior_rows','portfolio_behavior_rows','pair_behavior_rows','portfolio_pair_rows','cohort_rows','portfolio_cohort_rows','incrementality_rows','portfolio_incrementality_rows'])), '决定迭代与SKU组合判断是否基于真实用户行为，而不是上线前无限猜测。', '上线后补充广告、评论/退货/客服、SKU行为/Cohort与实验数据'),
    ]
    matrix=[]
    for name,ready,impact,action in domains:
        matrix.append({'domain':name,'status':'READY' if ready else 'NOT_SUPPLIED','impact':impact,'next_action':'无需补充' if ready else action,'strategy_can_continue':True})
    pending=[]
    for x in research_gate.get('actions',[]) or []:
        if x.get('status')=='RESOLVED': continue
        pending.append({'item':x.get('query') or x.get('reason'),'why':x.get('reason'),'blocks_scope':x.get('required_for',[]),'strategy_behavior':'继续完成不依赖该事实的正向策划；只保留对应提交/发布或硬结论为待确认。'})
    assumptions=[]
    for a in request.get('assumptions',[]) or []:
        text=a if isinstance(a,str) else a.get('assumption') or a.get('text') or str(a)
        assumptions.append({'assumption':text,'status':'ASSUMPTION','conversion_to_fact':'需要来源或用户明确确认后才能升级。'})
    return {
        'completeness_status':'SUFFICIENT_FOR_STRATEGY_WITH_GAPS' if any(x['status']!='READY' for x in matrix) else 'SUFFICIENT_FOR_CURRENT_SCOPE',
        'domain_matrix':matrix,'pending_confirmations':pending,'assumptions':assumptions,
        'decision_log':[
            _why('按证据成熟度分层推进策略，而不是等待所有资料齐全后才开始。','电商策略中的市场、平台提交、Claim和视觉执行依赖不同证据；把所有缺口当成总阻断会浪费已知信息。',evidence=[s.get('source_id') for s in request.get('sources',[]) if s.get('source_id')],consumer='先解决已知购买问题，再补真正影响决策的缺口。',platform='缺精确提交规则时只Hold提交敏感动作，不阻断定位、内容与创意。',business='缩短从资料输入到可执行方案的路径，同时保留事实边界。',execution='继续完成产品、定位、信息、视觉、内容与资产策划；把缺口挂到具体决策点。',measurement='每个待确认项在其影响的发布/预算/Claim动作前闭环。')
        ],
        'required_missing':[x['domain'] for x in matrix if x['status']!='READY'],
    }


def build_value_depth(request:dict[str,Any], truth:dict[str,Any], questions:list[str]):
    product=request.get('product') or {}; sources=request.get('sources') or []; claims=request.get('claims') or []
    source_ids=[s.get('source_id') for s in sources if s.get('source_id')]
    facts=[]
    for key,val in _flatten_facts(product):
        ftype=_fact_type(key)
        facts.append({
            'fact':key,'value':val,'fact_type':ftype,'evidence_level':'SOURCE_LINKED' if source_ids else 'USER_SUPPLIED',
            'source_ids':source_ids,'decision_role':_fact_role(ftype),
            'real_selling_point':'FACTUAL_RTB' if ftype in {'FORMULA_FACT','SIZE_CAPACITY_SPEC','FIT_ADJUSTMENT','WEATHER_BOUNDARY','CARE_MAINTENANCE','CLOSURE_SEAL','STORAGE_ORGANIZATION','COMPATIBILITY','PRODUCT_FORMAT','SENSORY_OR_MATERIAL'} else 'CONDITIONAL',
            'perceived_benefit':'需通过已批准Claim或目标购买问题翻译，不从事实直接跳成功效。',
            'emotional_value':'只有当功能/感知利益能真实支撑安心、便利、信心或身份认同时再使用。',
            'claim_boundary':'可以陈述该事实本身；更强的效果/时长/比较/安全性需独立证据。',
            'why':'这条事实是否值得前台传播，取决于它能否回答当前用户的购买问题，而不是因为它“看起来专业”。',
        })
    claim_rows=[]
    for c in claims:
        status=str(c.get('status') or 'PENDING').upper()
        grade=str(c.get('evidence_grade') or c.get('evidence_level') or '').upper()
        publication=str(c.get('publication_status') or '').upper()
        active=grade in {'A','B'} and publication not in {'BLOCKED','SOFT_ONLY_NO_HARD_CLAIM'} and status not in {'BLOCKED','PROHIBITED','REJECTED','INVALID'}
        claim_text=c.get('claim') or c.get('text') or c.get('name') or ''
        classification=c.get('type') or c.get('classification') or 'REAL_SELLING_POINT'
        claim_rows.append({
            'claim_id':c.get('claim_id'),'claim':claim_text,
            'classification':classification,
            'real_selling_point':claim_text if active and str(classification).upper() in {'REAL_SELLING_POINT','SELLING_POINT','CLAIM'} else ('可作为已批准信息使用' if active else '待证据'),
            'perceived_benefit':c.get('perceived_benefit') or c.get('consumer_value') or ('用用户语言解释该Claim与当前购买问题的关系。' if active else '仅内部假设，不作为公开利益。'),
            'emotional_value':c.get('emotional_value') or '只有当该利益能真实支撑安心、信心、便利或身份认同时再升级，不自动添加。',
            'evidence_level':c.get('evidence_level') or status,'source_ids':c.get('source_ids') or c.get('evidence_source_ids') or [],
            'publication_status':'ACTIVE' if active else 'PENDING_EVIDENCE',
            'consumer_value':c.get('consumer_value') or ('可进入核心/次级信息层级。' if active else '可作为内部策略假设，但不能写成公开确定事实。'),
            'recommended_role':c.get('recommended_role') or ('PRIMARY_OR_SECONDARY_MESSAGE' if active else 'HOLD_FOR_EVIDENCE'),
            'claim_boundary':c.get('claim_boundary') or ('按已批准原意使用；更强的结果/比较/时长需单独证据。' if active else '证据补齐前不作为公开确定事实。'),
            'why':c.get('rationale') or 'Claim强度、位置和重复频次应由证据等级和它承担的购买问题共同决定。',
        })
    active=[x for x in claim_rows if x['publication_status']=='ACTIVE']
    return {
        'product_facts':facts,'claim_value_ladder':claim_rows,
        'primary_value_candidates':[x['claim'] for x in active[:3]],
        'decision_questions':questions,
        'value_chain':'真实事实 → Advantage/RTB → 已批准可感知利益 → 情绪价值 → 证据；任何一层都不能自动跳级。',
        'unclaimable_without_more_evidence':['绝对化/保证性结果','未提供证据的时间结果','医疗/治疗性效果','未证实的临床/认证/销量/排名/用户证言'],
    }


def build_market_depth(market:dict[str,Any]|None, request:dict[str,Any]):
    if not market:
        return {
            'status':'MARKET_DATA_NOT_SUPPLIED','strategic_use':'当前定位以Product Truth、目标人群和平台任务为主；不把竞品价格/份额/趋势当成已知事实。',
            'what_can_be_decided':['产品价值层级','消费者问题','初步定位','文化/视觉策略','动态资产架构'],
            'what_requires_market_data':['竞争密度','价格机会','配置机会','竞品集群','搜索需求','市场规模/份额','数据驱动的SKU角色'],
            'next_research':['同平台同市场同类目Top商品/销量/销售额/价格/配置','关键词量级/意图/竞争','竞品Listing/视觉/评论主题','数据采集范围与代表性说明'],
            'opportunity_map':[], 'competitor_clusters':[], 'keyword_demand':{'status':'NOT_SUPPLIED'},
            'customer_voice':{'status':'NOT_SUPPLIED','theme_summary':[]},
            'why':'市场数据缺失不应把所有策略停掉，但任何竞争、价带、份额、搜索需求、Customer Voice和“市场机会”判断都不能靠想象。'
        }
    conc=market.get('concentration') or {}; comps=(market.get('competitors') or {}).get('top_competitors',[])
    top_bands=sorted(market.get('price_bands') or [],key=lambda x:(x.get('revenue') or 0,x.get('units') or 0),reverse=True)[:8]
    configs=(market.get('configuration') or [])[:10]; valleys=(market.get('price_valley_signals') or [])[:8]
    clusters=(market.get('competitor_clusters') or [])[:12]; keyword=market.get('keyword_demand') or {'status':'NOT_SUPPLIED'}
    customer_voice=market.get('customer_voice') or {'status':'NOT_SUPPLIED','theme_summary':[]}
    competitor_listing=market.get('competitor_listing_intelligence') or {'status':'NOT_SUPPLIED','competitors':[]}
    research_quality=market.get('research_quality') or {'status':'NOT_SUPPLIED','datasets':[],'sources':[]}
    research_ingestion=market.get('research_ingestion') or {'status':'NOT_SUPPLIED','datasets':[]}
    source_adapter_refresh=market.get('source_adapter_refresh') or {'status':'NO_SOURCE_ADAPTERS','adapters':[]}
    opps=market.get('opportunity_map') or []
    insights=[]
    if conc:
        insights.append(_why('用CR3 / CR10 / HHI判断“竞争结构需要怎样的差异化”，而不是把集中度当成进入/退出按钮。',f"当前输入样本 CR3={conc.get('cr3')}、CR10={conc.get('cr10')}、HHI={conc.get('hhi')}；这些只描述当前样本。",evidence=['market_analysis'],consumer='更集中的类目往往意味着用户已有成熟参照系，第一购买理由必须更清楚；更分散的类目则更需要从搜索意图/细分任务中找定位。',platform='同一市场结构在搜索型平台和推荐型平台的竞争入口不同：前者重关键词/商品卡，后者重首帧/内容分发。',business='决定是正面挑战头部、建立配置/价带差异，还是优先占据一个细分购买问题。',execution='把集中度与头部竞品、价带、配置、关键词和评论主题放在同一机会图，不单看一个数。',measurement='后续用份额、搜索位次、CTR/CVR、贡献与竞品变化验证。'))
    if top_bands:
        insights.append(_why('把成交密集价带视为“已被验证的支付区间”，把低密度价带只视为待验证假设。','价带空白可能是未满足需求，也可能只是需求弱；只有与配置、关键词、利润和购买理由同时成立才是机会。',evidence=top_bands,consumer='价格会改变用户对品质、规格和风险的预期，因此不能脱离价值理由定价。',business='避免为了“卡价差”进入没有真实需求或贡献空间不足的价格区间。',execution='候选价格必须同时通过：需求证据 × 配置适配 × 单位经济 × Positioning一致性。',measurement='价带级CVR、Contribution/order、退货/评价与相邻价带对比。'))
    if configs:
        insights.append(_why('把配置效率作为SKU/Offer结构证据，而不是只比较均价。','配置更接近用户实际购买单位（规格/套装/容量/组合），比单一价格均值更能说明Offer结构。',evidence=configs,consumer='用户购买的是具体规格与使用周期，不是抽象“均价”。',business='帮助决定单品、Bundle、Trial、Premium step或规格扩展是否值得。',execution='把units/item、revenue/item、价格、物流/成本、评论/退货联合判断。',measurement='配置级CVR、贡献、退货率、库存周转和复购。'))
    if clusters:
        insights.append(_why('用“价位层 × 配置”结构化竞品集群，寻找可解释的竞争位置。','竞品聚类必须基于当前可观测结构，而不是凭主观把品牌贴成“高端/年轻/科技”。',evidence=clusters,consumer='不同价位/配置对应不同购买预期，竞争对象应以同一决策集合为主。',business='决定真正需要对标谁、避开什么拥挤区、是否需要新的配置或价值理由。',execution='对每个候选集群补Listing主张、评论痛点、视觉语法与卖家效率，再形成差异化。',measurement='目标集群内的CTR/CVR/价格接受度/份额。'))
    if keyword.get('top_terms'):
        insights.append(_why('把搜索需求用于校正Positioning和Listing，但只保留与Product Truth真实相关的词。','高量词不等于适合本产品；追高量但低相关的词会带来低质量点击、CVR下降和误解。',evidence=keyword.get('top_terms',[])[:12],consumer='搜索词代表用户带着什么问题进入，不应被营销文案扭曲。',platform='搜索型Surface优先承接核心/规格意图；推荐型Surface则把关键词意图转成Hook和内容主题。',business='让SEO流量质量与转化/贡献同时改善，而不是只追曝光。',execution='按Search Relevance → Fit → Benefit/Proof → Risk Reduction分层映射到标题、属性、PDP与内容。',measurement='关键词级曝光/CTR/CVR/Contribution + 查询误配主题。'))
    cv_themes=[x for x in customer_voice.get('theme_summary',[]) if x.get('theme')!='UNCLASSIFIED']
    if cv_themes:
        insights.append(_why('把已标注的市场/竞品评论主题转成Customer Tension、Expectation Gap和Objection证据，而不是只把评论当“好评/差评”。','Runtime只聚合输入中明确提供的theme/category与sentiment，不从自由文本自动推断，因此每个主题都保持可追溯边界。',evidence=cv_themes[:12],consumer='重复出现的主题说明用户在实际购买/使用中反复关注什么，可帮助区分“用户真正问的问题”与品牌自说自话。',platform='评论主题可以分别回流到搜索词、Listing FAQ/PDP、推荐流Hook、达人脚本和售后教育，但不同Surface承接方式不同。',business='帮助识别竞品可攻击的Expectation Gap、Own Offer必须消除的风险，以及不值得用广告放大的错误预期。',execution='先做Product Truth fit，再把主题映射到Positioning tension、Listing objection、Content question和Dynamic Asset；未分类评论继续保留为研究缺口。',measurement='主题级CVR/退货/CS/评价变化 + 对应内容/Listing实验；不把样本频次冒充总体人群比例。'))
    if competitor_listing.get('competitors'):
        insights.append(_why('把竞品Listing主张/Offer/Proof与其Review主题联成竞争地图，再决定Own Positioning，而不是只看销量和价格。','结构数据回答“谁在卖、卖多少、什么价”；Listing与Review联合才更接近“他们怎么承诺、用户实际在意/抱怨什么”。',evidence=competitor_listing.get('competitors',[])[:10],consumer='用户会用竞品承诺形成类目预期；Own Offer应明确是满足已有预期、改变比较维度，还是降低某个真实风险。',platform='竞品标题/主图/Gallery/短视频/Offer在不同Surface承担不同入口，不能把一个Surface的语言直接当完整品牌定位。',business='帮助避免“大家都说同一句话”的同质化，也避免把竞品差评直接偷换成自己的优势。',execution='只使用已提供的观察字段/标签；对Message×Review exact overlap回看原始Listing与Review，再决定差异化、FAQ、Proof和资产任务。',measurement='竞品主题对应的CTR/CVR、搜索词、Own objection/return theme与增量实验。'))
    if research_quality.get('status')=='SOURCE_QUALITY_COMPILED':
        insights.append(_why('把研究结论绑定到来源、时间和样本范围，再决定它能支持多强的市场判断。','市场数据“有行数”不等于有代表性；来源未解析、时间窗口过期或样本框未记录时，机会判断必须降级为待验证假设。',evidence={'datasets':research_quality.get('datasets',[]),'sources':research_quality.get('sources',[])[:12]},consumer='消费者需求判断若来自偏样本，会把少数场景误当总体规律。',platform='跨平台/跨站点数据若混用，会把Surface机制差异误判成消费者偏好。',business='控制错误进入价带、错误竞品对标和错误Offer扩张的成本。',execution='每个Market/Keyword/Review/Competitor Listing dataset记录source_id coverage、source resolution、observed_at、declared freshness window、sample frame与scope mismatch。',measurement='研究刷新周期、未解析source比例、过期source比例、样本覆盖变更，以及新数据是否改变策略结论。'))
    if source_adapter_refresh.get('status')=='SOURCE_ADAPTERS_COMPILED':
        insights.append(_why('把较大规模研究输入做成可增量刷新的Source Adapter，而不是每次手工覆盖整份市场表。','Adapter明确schema map、primary key、刷新模式、high watermark、added/changed/removed change-set；语义近重复只进入review，不自动删证据。',evidence=source_adapter_refresh.get('adapters',[])[:12],consumer='稳定的数据谱系可以区分真实需求变化与采集/重复数据造成的假波动。',platform='不同平台/站点继续保留独立Adapter和scope，避免把跨平台机制差异混进同一趋势。',business='只刷新受影响数据与策略层，降低大规模市场研究的维护成本和错误重算风险。',execution='FULL_SNAPSHOT与INCREMENTAL_BATCH必须显式声明；exact key change-set与semantic near-duplicate review分开处理。',measurement='新增/变化/删除行数、high-watermark、unresolved key、near-duplicate review量，以及刷新后哪些策略结论发生变化。'))
    return {
        'status':'MARKET_STRATEGY_INTERPRETED','capacity':market.get('market_capacity'),'data_quality':market.get('data_quality'),'normalization':market.get('normalization'),
        'concentration':conc,'top_price_bands':top_bands,'price_valley_signals':valleys,'configuration_signals':configs,
        'price_configuration_matrix':(market.get('price_configuration_matrix') or [])[:20],'seller_efficiency':(market.get('seller_efficiency') or [])[:20],
        'top_competitors':comps[:15],'competitor_clusters':clusters,'keyword_demand':keyword,'customer_voice':customer_voice,'competitor_listing_intelligence':competitor_listing,'research_ingestion':research_ingestion,'source_adapter_refresh':source_adapter_refresh,'research_quality':research_quality,'opportunity_map':opps,
        'strategic_insights':insights,'why':'市场指标必须被翻译成“竞争方式、Offer结构、搜索入口和验证假设”。任何机会都必须经过产品适配、消费者需求、单位经济与平台执行四重检查；研究来源、时间与代表性边界决定这些判断能有多强。'
    }


def _category_objection_activation(request:dict[str,Any], commerce_profile:dict[str,Any]) -> list[dict[str,Any]]:
    questions=request.get('shopper_questions') or []
    family=commerce_profile.get('category_family') or 'GENERAL_COMMERCE'
    intents={classify_decision_intent(q,family) for q in questions}
    product=request.get('product') or {}
    # Keys are often more reliable than prose for explicit product facts (e.g. warranty, dimensions, ingredients).
    product_blob=' '.join([str(k) for k in product.keys()]+[str(v) for v in product.values() if not isinstance(v,(dict,list))]).casefold()
    out=[]
    for row in commerce_profile.get('objection_priorities',[]):
        r=dict(row); evidence=[str(x).casefold() for x in r.get('evidence_needed',[])]
        intent=r.get('decision_intent')
        matched_question=intent in intents
        matched_fact=any(x and x in product_blob for x in evidence)
        matched_market=bool(r.get('evidence_pressure',0))
        if matched_question or matched_fact or matched_market:
            r['status']='ACTIVE_CATEGORY_DECISION_RISK'
            r['activation_basis']={'shopper_question_intent':matched_question,'product_input_signal':matched_fact,'current_market_evidence_pressure':matched_market}
            r['why']=r.get('why','')+' Activated because current project inputs or current supplied market evidence contain a matching decision signal; resolution still requires truthful own-product field evidence.'
        else:
            r['status']='CATEGORY_CHECK_NOT_YET_ACTIVATED'
            r['activation_basis']={'shopper_question_intent':False,'product_input_signal':False,'current_market_evidence_pressure':False}
        out.append(r)
    return out


def _category_pdp_sequence(commerce_profile:dict[str,Any], positioning:dict[str,Any], questions:list[str]) -> list[dict[str,Any]]:
    family=commerce_profile.get('category_family') or 'GENERAL_COMMERCE'
    seq=((commerce_profile.get('message_architecture') or {}).get('sequence') or [])
    primary=positioning.get('primary_conversion_proposition')
    out=[]
    for i,job in enumerate(seq,1):
        j=str(job)
        content=primary if i==1 else j
        out.append({'order':i,'job':j,'question':next((q for q in questions if classify_decision_intent(q,family) in j or classify_decision_intent(q,family).replace('_',' ') in j),None),'content':content,'message_layer':f'C{i}','why':f"{commerce_profile.get('category_family')} category sequence prioritizes {j} at this point because it addresses a category-specific decision barrier before later persuasion."})
    return out


def _category_script_structure(category_family:str, intent:str, asset_type:str) -> str:
    video=asset_type=='VIDEO'
    mapping={
      ('APPAREL_FIT','SIZE_FIT'):'尺码/版型问题 → 尺码表/服装实测 → 明确模特/身体测量语境 → on-body版型证据 → 选择/FAQ；不把单一模特当普遍合身。',
      ('APPAREL_FIT','FIT_WEAR'):'真实穿着状态 → 轮廓/长度/松量 → 动作或正侧背关系 → 面料/细节 → 选择下一步。',
      ('FOOD_BEVERAGE','INGREDIENT_DIETARY'):'包装身份/净含量 → 配料/营养/过敏原或认证事实 → 适配边界 → 包装/购买下一步；不从视觉暗示健康功效。',
      ('FOOD_BEVERAGE','SENSORY_PREP'):'真实产品/冲泡或食用动作 → 准备步骤/份量 → 有证据的风味/形态 → 使用场景 → CTA/复购。',
      ('ELECTRONICS','COMPATIBILITY'):'设备/场景问题 → 接口/系统/地区兼容事实 → 关键限制 → 设置或下一步；兼容先于性能炫技。',
      ('ELECTRONICS','PERFORMANCE_PROOF'):'真实任务 → 规格/测试条件 → 可验证结果 → 限制/适用边界 → CTA；不用无上下文大数字。',
      ('HIGH_TICKET_DURABLE','SITE_FIT'):'真实场地/门洞/预留问题 → 产品尺寸/接口 → 必要clearance/前置条件 → 不适配边界 → 咨询/购买下一步。',
      ('HIGH_TICKET_DURABLE','DELIVERY_INSTALLATION'):'场地/履约问题 → 尺寸/前置条件 → 配送/安装/组装范围 → 责任边界 → 咨询/购买下一步。',
      ('HIGH_TICKET_DURABLE','WARRANTY_SERVICE'):'购买风险 → 保修/服务范围 → 服务路径 → 不覆盖项/条件 → 咨询或下单。',
      ('HIGH_TICKET_DURABLE','TOTAL_COST_OWNERSHIP'):'初始价格 → 已知持续成本项 → 使用周期/维护条件 → 价值比较 → 咨询/行动。',
      ('HIGH_TICKET_DURABLE','PERFORMANCE_PROOF'):'使用任务 → 性能指标与测试条件 → 真实结果/证据 → 空间/安装/噪音等限制 → 咨询/行动。',
    }
    if (category_family,intent) in mapping: return mapping[(category_family,intent)]
    if video: return '问题/场景钩子 → 精确产品身份 → 当前购买问题的一个新增答案 → 必要证据/边界 → 原生CTA；每个Beat只推进一个信念状态。'
    return '首屏给出当前购买问题的明确答案 → 事实/证据 → 必要风险/适配边界 → 下一资产或CTA；不复制其他Surface全文。'

def build_sku_depth(request:dict[str,Any], market_depth:dict[str,Any], economics:dict[str,Any]|None):
    skus=request.get('skus') or [{'sku':request.get('sku','SKU-1'),'name':(request.get('product') or {}).get('name'),'price':(request.get('offer_economics') or {}).get('price')}]
    economics=economics or {}; econ_roles=economics.get('dynamic_sku_roles') or []; role_by_sku={x.get('sku'):x for x in econ_roles if x.get('sku')}
    has_market=market_depth.get('status')=='MARKET_STRATEGY_INTERPRETED'; has_econ=economics.get('status') not in {None,'INSUFFICIENT_DATA'}
    rows=[]
    for i,skurow in enumerate(skus):
        sku=skurow.get('sku') or f'SKU-{i+1}'; er=role_by_sku.get(sku)
        if skurow.get('role'):
            role=skurow['role']; confidence='HIGH'; why=skurow.get('role_rationale') or '项目已明确给出商业角色。'
        elif er:
            role=er.get('role'); confidence=er.get('confidence') or 'MEDIUM'; why=er.get('why')
        elif len(skus)==1:
            role='PROJECT_FOCAL / HERO_CANDIDATE'; confidence='MEDIUM'; reasons=[]
            if has_market: reasons.append('已有市场结构/价带/配置证据可校正它的竞争位置')
            if has_econ: reasons.append('已有单位经济可约束价格/增长空间')
            why='当前项目只有一个SKU，因此天然承担主要转化任务；'+('；'.join(reasons)+'。' if reasons else '但没有足够市场/利润证据把它称为“市场Hero”或“利润款”。')+'Hero Candidate描述的是项目任务，不冒充市场地位。'
        else:
            role='ROLE_TO_BE_RESOLVED'; confidence='LOW'; why='多SKU角色需要需求、利润、生命周期、渠道任务、价格梯度与互相蚕食共同决定。'
        rows.append({'sku':sku,'name':skurow.get('name'),'role':role,'confidence':confidence,'price':skurow.get('price'),'configuration':skurow.get('configuration'),'why':why,'buyer_job':skurow.get('buyer_job'),'channel_job':skurow.get('channel_job'),'next_decision':'结合市场需求、单位贡献、价格梯度、渠道任务和Cannibalization锁定。'})
    econ_snapshot={k:economics.get(k) for k in ['currency','price','contribution','contribution_margin','total_cost','contribution_before_ads','break_even_roas','allowable_cpa_zero_contribution','allowable_cpa_target_contribution','coupon_headroom_zero_contribution','coupon_headroom_target_contribution','affiliate_rate_ceiling_zero_contribution','affiliate_rate_ceiling_target_contribution','growth_budget_pool_before_affiliate_and_ads','growth_pool_remaining_after_affiliate_and_ads','shared_growth_budget'] if economics.get(k) is not None}
    offer_decisions=[]
    if has_econ:
        contribution=economics.get('contribution'); margin=economics.get('contribution_margin'); price=economics.get('price')
        if contribution is not None:
            offer_decisions.append(_why('把Contribution设为售价、优惠、联盟佣金和广告预算的共同约束，而不是分别拍比例。',f"当前输入场景价格={price}，贡献={contribution}，贡献率={margin}。",evidence=['offer_economics'],consumer='优惠需要形成真实价值，但不能用持续补贴掩盖弱产品理由。',platform='不同平台促销/联盟/广告机制不同，但最终都消耗单位贡献。',business='Coupon、Affiliate、Paid Media共享同一利润池；任何一个增加都会挤压其他空间。',execution='先定义最低目标贡献，再按渠道/活动情景分配优惠、达人和投放预算；每个情景单独算。',measurement='Contribution/order、CPA、ROAS、refund allowance、marginal contribution。'))
        if economics.get('break_even_roas') is not None:
            offer_decisions.append(_why('把自身Break-even ROAS / CPA作为付费扩量底线。',f"当前Break-even ROAS={economics.get('break_even_roas')}；允许CPA={economics.get('allowable_cpa_target_contribution') or economics.get('allowable_cpa_zero_contribution')}。",evidence=['offer_economics'],business='低于自身经济底线的增长会放大亏损，即使GMV增长。',execution='广告诊断先过经济底线，再判断流量、点击包装或PDP问题；扩量看边际CPA而非只看平均CPA。',measurement='Actual/Marginal ROAS vs break-even；Contribution after ads。'))
    else:
        offer_decisions.append(_why('完整单位经济补齐前，不锁死售价、优惠、达人佣金和广告预算。','这些动作共享同一个利润池，缺成本瀑布时任何“可承受比例”都会是假精确。',business='先避免不可逆的亏损型Offer承诺。',execution='补售价、采购/履约、平台费、税、退款、联盟和广告成本后再定预算边界。'))
    ladder=economics.get('price_ladder',[]) or []
    ladder_strategy=[]
    for r in ladder:
        ladder_strategy.append({'sku':r.get('sku'),'scenario_id':r.get('scenario_id'),'price':r.get('price'),'price_rank':r.get('price_rank'),'gap':r.get('price_gap_from_previous'),'contribution':r.get('contribution'),'margin':r.get('contribution_margin'),'role':next((x.get('role') for x in econ_roles if x.get('sku')==r.get('sku') or x.get('scenario_id')==r.get('scenario_id')),None),'why':'价格阶梯只有在每一级都有不同的用户任务/配置/价值理由时才成立；纯粹加价不构成Premium。'})
    return {
        'sku_roles':rows,'role_decision_matrix':economics.get('role_decision_matrix',[]),'economics_status':economics.get('status'),'economics_snapshot':econ_snapshot,
        'price_ladder':ladder,'price_ladder_strategy':ladder_strategy,'economics_scenarios':economics.get('scenarios',[]),
        'portfolio_interactions':economics.get('portfolio_interactions') or {},'portfolio_behavior_validation':economics.get('portfolio_behavior_validation') or {},'interaction_behavior_validation':economics.get('interaction_behavior_validation') or {},'switch_matrix':economics.get('switch_matrix') or {},'cohort_comparability':economics.get('cohort_comparability') or {},'holdout_marginal_contribution':economics.get('holdout_marginal_contribution') or {},'trade_up_architecture':economics.get('trade_up_architecture') or [],'lifecycle_offer_map':economics.get('lifecycle_offer_map') or [],'promo_response':economics.get('promo_response') or {},'bundle_affinity':economics.get('bundle_affinity') or {},'repeat_replacement_cycle':economics.get('repeat_replacement_cycle') or {},
        'offer_decisions':offer_decisions,'shared_growth_budget':economics.get('shared_growth_budget') or {},
        'market_opportunity_links':(market_depth.get('opportunity_map') or [])[:8],
        'portfolio_logic':'Hero / Traffic / Margin / Premium / Bundle / Trial / Retention / Gift / Seasonal / Channel Exclusive 都是候选角色，不是固定模板；一个SKU也可以在不同渠道/活动承担不同角色。',
        'market_link':market_depth.get('status'),'why':'SKU角色是“为谁解决什么任务、在组合中贡献什么商业结果”，不是产品名称标签；必须同时解释需求、价格/利润、渠道、生命周期、Trade-up理由与Cannibalization。'
    }

def build_positioning_depth(request:dict[str,Any], value:dict[str,Any], market:dict[str,Any], sku:dict[str,Any], culture:dict[str,Any], questions:list[str], commerce_profile:dict[str,Any]|None=None):
    product=request.get('product') or {}; target=request.get('target') or {}; audience=request.get('audience') or request.get('audience_culture') or {}; supplied=request.get('positioning') or {}
    commerce_profile=commerce_profile or category_commerce_profile(request)
    category_objections=_category_objection_activation(request,commerce_profile)
    primary=supplied.get('primary_conversion_proposition') or product.get('primary_conversion_proposition') or product.get('verified_selling_point') or (value.get('primary_value_candidates') or [None])[0]
    if not primary: primary=f"先让用户准确理解 {product.get('name','该产品')} 是什么，再用已批准证据建立购买理由"
    target_desc=supplied.get('target') or audience.get('primary_segment') or f"{target.get('market','目标市场')} 的核心目标用户"
    frame=supplied.get('frame_of_reference') or product.get('product_type') or product.get('category') or '产品'
    tension=supplied.get('consumer_tension') or (questions[1] if len(questions)>1 else '用户需要快速判断该产品是否与自己的真实需求相关。')
    alt=supplied.get('alternative') or supplied.get('competitive_alternative') or '用户当前使用的同类方案/不购买/延后决策'
    statement=supplied.get('statement') or f"面向{target_desc}，以“{primary}”作为第一购买理由，并用真实产品事实和证据逐层回答‘是否适合我、凭什么相信、为什么现在选它、如何使用’。"
    def _unique_message_values(values, excluded=None):
        excluded_keys={' '.join(str(x or '').split()).casefold() for x in (excluded or []) if str(x or '').strip()}
        seen=set(); out=[]
        for v in values or []:
            text=' '.join(str(v or '').split()); key=text.casefold()
            if not text or key in seen or key in excluded_keys: continue
            seen.add(key); out.append(text)
        return out
    secondary_raw=supplied.get('secondary_reasons') or product.get('secondary_reasons') or [x['claim'] for x in value.get('claim_value_ladder',[]) if x.get('publication_status')=='ACTIVE']
    secondary=_unique_message_values(secondary_raw,[primary])[:4]
    trust=_unique_message_values(supplied.get('trust_drivers') or product.get('trust_drivers') or ['真实产品身份','可追溯事实/Claim','平台与语言原生表达'])
    objections=supplied.get('objection_reducers') or product.get('objection_reducers') or questions[1:5]
    active_claims=[x for x in value.get('claim_value_ladder',[]) if x.get('publication_status')=='ACTIVE']
    # Generic message hierarchy must not repeat P0/P1 verbatim as a fake "proof" layer.
    # If no distinct RTB exists, the category proof hierarchy/evidence condition remains authoritative.
    rtbs=_unique_message_values([x.get('claim') for x in active_claims],[primary,*secondary])[:5]
    cv=(market.get('customer_voice') or {}).get('theme_summary') or []
    market_tensions=[{'theme':x.get('theme'),'sentiment':x.get('dominant_sentiment'),'weighted_mentions':x.get('weighted_mentions'),'source_ids':x.get('source_ids',[]),'strategy_use':'Validate against own Product Truth before using as positioning tension, objection, hook or asset job.'} for x in cv if x.get('theme')!='UNCLASSIFIED'][:8]
    ci=market.get('competitor_listing_intelligence') or {}
    competitor_message_context={'status':ci.get('status'),'message_themes':ci.get('message_theme_summary',[])[:12],'offer_types':ci.get('offer_type_summary',[])[:12],'proof_types':ci.get('proof_type_summary',[])[:12],'message_review_overlap':ci.get('message_review_overlap',[])[:12],'boundary':'Observed competitor evidence informs the comparison set; it does not automatically become an own-product advantage.'}
    hierarchy=[{'priority':'P0','role':'IDENTITY + PRIMARY VALUE','message':primary,'consumer_state':'What is it / why care?','why':'首屏/首条内容只建立一个主要记忆点，避免多卖点平均分配注意力。'}]
    for x in secondary[:3]: hierarchy.append({'priority':'P1','role':'RELEVANCE / SECONDARY BENEFIT','message':x,'consumer_state':'Is it relevant to me?','why':'核心价值被理解后，用次级利益或适配语境增强“与我有关”。'})
    for x in rtbs[:3]: hierarchy.append({'priority':'P2','role':'REASON TO BELIEVE','message':x,'consumer_state':'Why should I believe it?','why':'证据在用户产生兴趣后出现，更能承担信任而不是抢占第一注意力。'})
    for x in trust[:2]: hierarchy.append({'priority':'P3','role':'TRUST / RISK REDUCTION','message':x,'consumer_state':'Is it safe/clear enough to act?','why':'信任/风险信息推动行动，但不应替代产品价值本身。'})
    value_prop={'target_customer':target_desc,'job_or_tension':tension,'frame_of_reference':frame,'value_promise':primary,'reasons_to_believe':rtbs,'secondary_gains':secondary,'competitive_alternative':alt,'risk_reducers':objections,'proof_boundary':'只使用Product Truth与已批准Claim；市场差异化仅在有竞品证据时表述为相对优势。'}
    belief=[
        {'step':1,'state':'IDENTIFY','question':'这是什么？','message_job':f'{frame} + 产品身份','exit_condition':'能准确归类产品'},
        {'step':2,'state':'RELATE','question':'为什么和我有关？','message_job':primary,'exit_condition':'理解第一购买理由'},
        {'step':3,'state':'BELIEVE','question':'凭什么相信？','message_job':'RTB / Product Truth / approved proof','exit_condition':'核心主张获得可信理由'},
        {'step':4,'state':'REDUCE_RISK','question':'会不会不适合/买错/难用？','message_job':'异议、规格、使用、包材、适配边界','exit_condition':'主要风险被澄清'},
        {'step':5,'state':'NEXT_ACTION','question':'现在为什么值得行动？','message_job':'Offer/CTA/availability only when economics/platform support it','exit_condition':'完成平台原生下一步'},
        {'step':6,'state':'USE_RETAIN','question':'购买后如何获得预期体验？','message_job':'使用教育/预期管理/复购触发','exit_condition':'减少误用和期望差'},
    ]
    means_end={'attributes':[x.get('fact') for x in value.get('product_facts',[])[:8]],'functional_consequences':[x for x in secondary[:4]],'psychosocial_consequences':supplied.get('emotional_values') or [],'end_values':'仅当Product Truth→利益链真实支撑时，才升级到安心/便利/自信/身份价值。'}
    signaling={'desired_signal':supplied.get('desired_signal') or '可信、清晰、与目标用户语境相关','signal_sources':['产品真实外观/规格','证据强度匹配的文案','一致的CMF/摄影','平台原生表达'],'avoid':'用“实验室/医生/奢华/天然”等符号替代真实证据，或让文化元素变成刻板标签。'}
    return {
        'target_user':target_desc,'frame_of_reference':frame,'consumer_tension':tension,'positioning_statement':statement,
        'primary_conversion_proposition':primary,'value_proposition':value_prop,'secondary_reasons_to_buy':secondary,'reasons_to_believe':rtbs,'trust_drivers':trust,'objection_reducers':objections,
        'message_hierarchy':hierarchy,'belief_sequence':belief,'means_end_chain':means_end,'signaling_strategy':signaling,
        'cognitive_budget':{'first_impression_units':1,'rule':'首屏/首帧只允许一个Primary Proposition占主导；同屏其他信息只承担身份/证据/必要风险澄清。','why':'移动端注意力稀缺，平均强调多个卖点会降低记忆与点击理解。'},
        'commerce_response_ladder':['Notice/Recognize','Understand','Relate','Believe','Reduce Risk','Act','Use/Retain'],
        'market_tension_candidates':market_tensions,'competitive_message_context':competitor_message_context,
        'category_message_architecture':commerce_profile.get('message_architecture') or {},'category_proof_hierarchy':commerce_profile.get('proof_hierarchy') or [],'category_objection_priorities':category_objections,
        'differentiation_source':'优先来自真实产品事实 × 目标购买问题 × 搜索需求 × 已观察竞品Message/Offer/Proof × Review主题 × Offer可行性；只有Own Product Truth真实匹配且比较证据充分时，才升级成相对差异化主张。',
        'decision_card':_why('锁定一个Primary Conversion Proposition，并按Belief Sequence展开。','用户并不是一次性接受所有卖点；先识别、再相关、再相信、再降风险、再行动，信息顺序比卖点数量更重要。',evidence=[x.get('claim_id') for x in active_claims if x.get('claim_id')],consumer='降低认知负荷，并把每条证据放在它最有说服力的时点。',platform=f"{target.get('platform_family')} 的不同Surface承担不同信息深度，首屏/商品卡不应复制PDP全部内容。",culture='文化适配改变表达方式、人物和语境，不创造不存在的产品价值。',business='为Listing、Hero、Creator、Paid和资产顺序提供同一个信息Authority。',execution='P0建立身份+第一理由；P1相关性；P2证据；P3信任/风险；Offer/CTA只在经济与平台条件成立时进入。',measurement='按Surface分别看CTR、首屏理解、CVR、FAQ/退货主题与Contribution，不用一个指标解释所有阶段。'),
        'sku_strategy':sku,'market_link':market.get('status')
    }

def _decision_listing_field(intent:str)->str:
    return {
      'IDENTIFY':'title/hero','DIFFERENTIATION':'highlights/gallery/description','RELEVANCE':'highlights/description',
      'PROOF':'highlights/gallery','INGREDIENT_COMPOSITION':'attributes/faq','INGREDIENT_DIETARY':'attributes/faq',
      'USAGE':'usage/faq/video','SIZE_FIT':'attributes/gallery/faq','FIT_WEAR':'gallery/creator','SIZE_CAPACITY':'attributes/gallery',
      'SITE_FIT':'attributes/faq','COMPATIBILITY':'attributes/faq','PERFORMANCE_PROOF':'highlights/gallery/video','PORTABILITY':'attributes/gallery',
      'MATERIAL_SENSORY':'attributes/gallery','WEATHER_BOUNDARY':'gallery/faq','CARE_MAINTENANCE':'faq/usage',
      'PACKAGE_CONTENTS':'package/gallery','SEAL_LEAK':'gallery/video/faq','STORAGE_STACKING':'gallery/video',
      'WARRANTY_SERVICE':'faq/policy','DELIVERY_INSTALLATION':'faq/policy','TOTAL_COST_OWNERSHIP':'description/faq','EXPECTATION_BOUNDARY':'faq/highlights'
    }.get(str(intent or '').upper(),'highlights/faq')


def _decision_specific_proof_contract(intent:str, topic:str, inherited:dict[str,Any]|None=None)->dict[str,Any]:
    """Refine category-level proof priors with the live atomic decision topic.

    Category proof hierarchy decides what kinds of proof usually matter.  The atomic shopper question
    decides what evidence contract this particular PDP job actually needs.
    """
    intent=str(intent or '').upper(); topic=str(topic or '').upper(); inherited=inherited or {}
    if topic=='CLINICAL_EVIDENCE':
        return {'proof_type':'claim-specific clinical evidence','evidence_condition':{'evidence_type':'CLAIM_SPECIFIC_SOURCE','must_include':['exact claim text/strength','study/evidence source','population/sample','method/condition','time boundary when applicable'],'do_not_infer':['clinical result beyond the supplied population/conditions','ingredient presence as proof of the studied outcome']}}
    if topic=='FORMULA_FACTS' or intent=='INGREDIENT_COMPOSITION':
        return {'proof_type':'current formula/ingredient facts','evidence_condition':{'evidence_type':'LABEL_OR_AUTHORIZED_SPEC','must_include':['current formula/label/spec','market/variant/version when relevant','source'],'do_not_infer':['benefit from ingredient presence alone','ethical/certification status without source']}}
    if intent=='CARE_MAINTENANCE':
        return {'proof_type':'care / cleaning instructions','evidence_condition':{'evidence_type':'CURRENT_CARE_INSTRUCTIONS','must_include':['current product care/cleaning instruction','part/material scope','source/version'],'do_not_infer':['dishwasher/wash compatibility from material appearance','maintenance interval without source']}}
    if intent=='SEAL_LEAK':
        return {'proof_type':'closure / leak boundary','evidence_condition':{'evidence_type':'CLOSURE_SEAL_EVIDENCE','must_include':['exact closure operation or approved leak claim','use condition/boundary','source/version'],'do_not_infer':['lifetime leak performance','all orientations/conditions beyond the supplied claim']}}
    if intent=='DIFFERENTIATION':
        return {'proof_type':'traceable comparison facts','evidence_condition':{'evidence_type':'CURRENT_COMPARISON_SOURCE_SET','must_include':['own-product fact','comparison-product observation','same dimension/metric','current source/date'],'do_not_infer':['overall superiority from one specification','competitor weakness from missing data']}}
    if intent in {'SIZE_CAPACITY','SIZE_FIT','FIT_WEAR','PORTABILITY'}:
        return {'proof_type':'dimensions / scale / fit evidence','evidence_condition':{'evidence_type':'PRODUCT_MEASUREMENTS_OR_SCALE_EVIDENCE','must_include':['exact product measurements/weight/capacity as relevant','source/version','visual scale context when used'],'do_not_infer':['universal body/space fit from one example']}}
    if intent=='COMPATIBILITY':
        return {'proof_type':'exact compatibility / interface facts','evidence_condition':{'evidence_type':'COMPATIBILITY_MATRIX_OR_EXACT_SPEC','must_include':['exact model/interface/region or declared compatibility scope','source/version'],'do_not_infer':['compatibility from connector appearance','performance at an unsupported device/load']}}
    if intent=='PERFORMANCE_PROOF':
        return {'proof_type':'conditioned performance evidence','evidence_condition':{'evidence_type':'CONDITIONED_PERFORMANCE_EVIDENCE','must_include':['metric','test/claim condition','configuration/load','source/version'],'do_not_infer':['best-case result as universal outcome']}}
    if intent=='WEATHER_BOUNDARY':
        return {'proof_type':'weather / finish boundary','evidence_condition':{'evidence_type':'CURRENT_PRODUCT_WEATHER_CARE_SOURCE','must_include':['exact weather/finish claim','explicit limitation','source/version'],'do_not_infer':['waterproofing from water-repellent wording','permanent performance when finish can degrade']}}
    if intent=='PACKAGE_CONTENTS':
        return {'proof_type':'package / included contents','evidence_condition':{'evidence_type':'CURRENT_PACKAGE_SPEC','must_include':['exact included items/count/variant','source/version'],'do_not_infer':['accessories or bundles not stated']}}
    if intent=='USAGE':
        return {'proof_type':'usage / routine instructions','evidence_condition':{'evidence_type':'CURRENT_USAGE_INSTRUCTIONS','must_include':['step/operation/order as supplied','source/version'],'do_not_infer':['frequency/result beyond instructions']}}
    return {'proof_type':inherited.get('proof_type'),'evidence_condition':inherited.get('evidence_condition')}


def _decision_led_listing_plan(asset_architecture:dict[str,Any], reconciliation:dict[str,Any], positioning:dict[str,Any])->dict[str,Any]:
    assets=list(asset_architecture.get('assets') or [])
    ranks={x.get('decision_intent'):x.get('effective_rank') for x in reconciliation.get('effective_objection_priorities',[]) if x.get('decision_intent')}
    proof_by_intent={}
    for p in reconciliation.get('effective_proof_hierarchy',[]) or []:
        for intent in p.get('supports_decision_intents') or []:
            proof_by_intent.setdefault(intent,p)
    rows=[]
    for i,a in enumerate(assets):
        intent=a.get('decision_intent') or 'DECISION_SUPPORT'
        if intent=='IDENTIFY': continue
        proof=proof_by_intent.get(intent) or {}
        specific_proof=_decision_specific_proof_contract(intent,a.get('decision_topic'),proof)
        rows.append({
          'asset_id':a.get('asset_id'),'consumer_question':a.get('consumer_question'),'decision_intent':intent,'decision_topic':a.get('decision_topic'),
          'recommended_listing_field':_decision_listing_field(intent),'surface':a.get('surface'),'incremental_information':a.get('incremental_information'),
          'proof_type':specific_proof.get('proof_type'),'proof_condition':specific_proof.get('evidence_condition'),
          'priority_key':ranks.get(intent,50+i),'why':'This row exists because the live shopper/market decision job has incremental information not safely replaceable by a generic category template.'
        })
    rows.sort(key=lambda x:(x.get('priority_key',999), next((i for i,a in enumerate(assets) if a.get('asset_id')==x.get('asset_id')),999)))
    category_sequence=((reconciliation.get('message_architecture') or {}).get('effective_sequence') or [])
    identity_job=category_sequence[0] if category_sequence else 'IDENTITY'
    seq=[{'order':1,'job':identity_job,'decision_intent':'IDENTIFY','question':next((a.get('consumer_question') for a in assets if a.get('decision_intent')=='IDENTIFY'),None),'content':positioning.get('primary_conversion_proposition'),'message_layer':'D1','source_asset_id':next((a.get('asset_id') for a in assets if a.get('decision_intent')=='IDENTIFY'),None),'recommended_listing_field':'title/hero','why':'Every PDP must establish exact product identity and the primary conversion proposition before deeper proof/risk modules; the visible job label preserves the category/evidence sequence authority.'}]
    for idx,r in enumerate(rows,2):
        seq.append({'order':idx,'job':r['decision_intent'],'decision_intent':r['decision_intent'],'question':r['consumer_question'],'content':r['incremental_information'],'message_layer':f'D{idx}','source_asset_id':r['asset_id'],'recommended_listing_field':r['recommended_listing_field'],'proof_type':r.get('proof_type'),'proof_condition':r.get('proof_condition'),'why':r['why']})
    audit=list(asset_architecture.get('decision_question_audit') or [])
    return {
      'decision_question_coverage':{'summary':asset_architecture.get('decision_coverage_summary') or {},'rows':audit},
      'decision_specific_listing_jobs':rows,
      'decision_led_pdp_sequence':seq,
      'why':'The live PDP sequence is compiled from current atomic buyer questions and evidence priority. Category message architecture remains a prior/reference, not a substitute for product-specific unresolved decisions.'
    }


def build_listing_depth(request:dict[str,Any], listing:dict[str,Any]|None, positioning:dict[str,Any], target:dict[str,Any], commerce_profile:dict[str,Any]|None=None):
    compiled=(listing or {}).get('compiled') or {}; kw=compiled.get('keyword_priority') or []; fields=compiled.get('fields') or (request.get('listing_input') or {}).get('fields',{})
    commerce_profile=commerce_profile or category_commerce_profile(request)
    category_objections=_category_objection_activation(request,commerce_profile)
    active_category_objections=[x for x in category_objections if x.get('status')=='ACTIVE_CATEGORY_DECISION_RISK']
    primary=positioning.get('primary_conversion_proposition'); questions=request.get('shopper_questions') or []
    value_prop=positioning.get('value_proposition') or {}; message=positioning.get('message_hierarchy') or []
    title_blueprint={'components':['Brand/Product Identity','Core Category/Search Intent','Critical Variant/Spec when needed','One primary value cue if platform space allows'],'priority':'Identity > exact relevance > required spec > one value cue','current':fields.get('title'),'why':'Title同时服务搜索与点击理解，但不能成为卖点仓库；搜索词必须保持自然产品身份。'}
    field_map=compiled.get('field_decision_map') or []
    if not field_map:
        field_map=[{'field':'title','decision_job':'IDENTIFY + SEARCH','why':'准确产品识别 + 核心搜索意图。'},{'field':'attributes','decision_job':'VERIFY FIT','why':'结构化规格/兼容/变体事实。'},{'field':'highlights/bullets','decision_job':'RELATE + BELIEVE','why':'次级利益 + RTB。'},{'field':'description','decision_job':'CONTEXT + PROOF','why':'承接需要解释的价值/使用逻辑。'},{'field':'faq','decision_job':'REDUCE RISK','why':'处理异议与误解。'},{'field':'usage','decision_job':'USE','why':'降低使用不确定性。'},{'field':'package','decision_job':'EXPECTATION','why':'降低内容物/规格预期差。'}]
    search_layers=[]
    for r in kw:
        search_layers.append({'term':r.get('term'),'cluster':r.get('cluster'),'priority_score':r.get('priority_score'),'field_role':r.get('role'),'decision_stage':r.get('decision_stage'),'why':r.get('why') or '关键词位置由搜索意图与购买阶段共同决定。'})
    pdp=[
        {'order':1,'job':'IDENTIFY','question':questions[0] if questions else '它是什么？','content':'产品身份 + Primary Proposition','message_layer':'P0'},
        {'order':2,'job':'RELATE','question':questions[1] if len(questions)>1 else '与我有关吗？','content':'目标场景/人群适配 + 次级利益','message_layer':'P1'},
        {'order':3,'job':'BELIEVE','question':questions[2] if len(questions)>2 else '凭什么相信？','content':'事实/参数/配方/材质/证据','message_layer':'P2'},
        {'order':4,'job':'REDUCE_RISK','question':'有什么容易误解或退货的点？','content':'规格、包装内容、兼容/使用、预期管理','message_layer':'P3'},
        {'order':5,'job':'NEXT_ACTION','question':'下一步做什么？','content':'平台原生CTA/变体/Offer；只有经济/规则支持时进入促销','message_layer':'ACTION'},
        {'order':6,'job':'USE_RETAIN','question':'买后如何正确使用并减少预期差？','content':'使用教育、注意事项、补充FAQ/复购内容','message_layer':'POST_PURCHASE'},
    ]
    category_pdp=_category_pdp_sequence(commerce_profile,positioning,questions)
    return {
        'status':'LISTING_STRATEGY_COMPILED' if listing else 'LISTING_INPUT_NOT_SUPPLIED','current_fields':fields,
        'search_intent_architecture':{'priority_terms':search_layers,'intent_summary':((compiled.get('keywords') or {}).get('intent_summary') or []),'principle':'Search relevance先准确，再 persuasion；不以堆词牺牲产品身份和点击质量。'},
        'search_intent_priority':kw,'keyword_coverage':compiled.get('keyword_coverage') or {},'repetition_audit':compiled.get('repetition_audit') or {},
        'field_contracts':compiled.get('field_contracts') or [],'field_decision_map':field_map,'claim_source_trace':compiled.get('claim_source_trace_summary') or {},
        'field_content_plan':{
            'title':fields.get('title'),'brand':fields.get('brand'),'attributes':fields.get('attributes'),'highlights':fields.get('highlights') or fields.get('bullets'),
            'description':fields.get('description'),'faq':compiled.get('faq_plan',[]),'usage':compiled.get('usage_plan',[]),'package':compiled.get('package_plan',[])
        },
        'objection_resolution_plan':(compiled.get('objection_resolution_plan') or []) + [dict(x,source='CATEGORY_COMMERCE_PROFILE') for x in active_category_objections],
        'category_objection_checks':category_objections,'category_proof_hierarchy':commerce_profile.get('proof_hierarchy') or [],'category_message_architecture':commerce_profile.get('message_architecture') or {},
        'title_strategy':title_blueprint,'title_job':{'job':f"准确产品识别 + 核心搜索意图 +（空间允许时）一个第一购买理由：{primary}",'current':fields.get('title'),'why':title_blueprint['why']},
        'hero_job':{'job':f"让用户在移动端第一眼知道卖什么，并理解核心理由：{primary}",'why':'商品卡/首图承担点击和快速识别，不复制详情页全部证据。'},
        'attributes_strategy':{'job':'把会影响是否适配/规格/兼容/变体的事实结构化，减少误购。','inputs_required':'Product Truth / platform attribute contract','why':'属性是决策与检索基础，不应用广告语言代替事实。'},
        'highlights_bullets_strategy':{'job':'按P1相关性 → P2证据展开，每条只承担一个购买问题。','message_layers':[x for x in message if x.get('priority') in {'P1','P2'}],'why':'Bullets/Highlights应增加新信息，而不是重复Title/Hero长句。'},
        'description_strategy':{'job':'解释需要上下文的产品逻辑、使用语境、材质/配方/证据与边界。','why':'描述区适合深解释，不应把所有关键信息推迟到这里。'},
        'faq_strategy':{'objection_resolution_plan':compiled.get('objection_resolution_plan') or [{'objection':x,'recommended_field':'faq','why':'优先用事实/边界解决异议。'} for x in positioning.get('objection_reducers',[])],'provided_faq':compiled.get('faq_plan',[]),'why':'FAQ用于消除真实异议/误解/退货驱动，不是新增营销Claim。'},
        'usage_strategy':{'provided_usage':compiled.get('usage_plan',[]),'job':'把购买价值翻译成清楚的使用步骤/频率/注意事项（只在有事实依据时）。','why':'正确使用和预期管理影响满意度、退货与复购。'},
        'package_strategy':{'provided_package':compiled.get('package_plan',[]),'job':'明确收到什么、数量/规格/包装差异。','why':'内容物和规格预期差是高成本但可提前预防的沟通问题。'},
        'pdp_sequence':category_pdp or pdp,'generic_belief_sequence_reference':pdp,'faq_and_return_prevention':positioning.get('objection_reducers',[]),
        'seo_geo_strategy':{'SEO':'优先核心产品/类目/规格/真实场景词，并与字段职责匹配。','GEO':'用结构化事实、FAQ、清晰实体/属性关系提高机器/生成式检索可理解性；不为“AI可见性”创造未经证据支持的事实。','why':'可检索性来自清晰实体、事实和意图匹配，不是关键词堆叠。'},
        'localization_transcreation':compiled.get('localization_transcreation') or {'principle':'目标语言先重写购买理由和信息密度，再做Exact Copy审核；不逐词直译。'},
        'platform_native_listing_profile':compiled.get('platform_native_listing_profile') or {},
        'transcreation_task_matrix':compiled.get('transcreation_task_matrix') or {},'localized_copy_audit':compiled.get('localized_copy_audit') or {},'terminology_memory':compiled.get('terminology_memory') or [],'terminology_memory_audit':compiled.get('terminology_memory_audit') or {},'final_copy_workflow':compiled.get('final_copy_workflow') or {},
        'localization':'目标语言先重写购买理由和信息密度，再处理字面翻译；数字/Claim强度/风险边界保持等价；只有经过硬约束审计和明确语言/Claim/平台/文化审校的文案才进入Final Copy。',
        'why':'Listing是Search Intent × Product Truth × Positioning/Message Hierarchy × Consumer Decision Questions × Platform Fields的共同编译结果，不是把广告文案复制到所有字段。'
    }

def _platform_profile(name:str):
    n=(name or '').casefold()
    if 'tiktok' in n: return {'attention':'前1–2秒/首屏快速识别 + 可演示/可口播理由','native_forms':['Gallery','Short Video','Creator','Live','Paid'],'cta':'进入商品页/点击商品锚点/按当前Surface原生动作','metrics':'CTR / video hold / product click / CVR / creator contribution'}
    if 'amazon' in n: return {'attention':'搜索结果识别与主图点击 → PDP证据顺序','native_forms':['Search','Primary Image','Gallery','Video','A+ / PDP'],'cta':'选择变体/购买/继续查看证据','metrics':'CTR / CVR / return themes / search term performance'}
    if 'shopee' in n: return {'attention':'移动端商品卡 + Gallery + Offer/信任','native_forms':['Search','Listing','Gallery','Video','Chat/FAQ'],'cta':'查看商品/选择规格/下单/咨询','metrics':'CTR / CVR / chat questions / return themes'}
    if 'shopify' in n: return {'attention':'流量来源落地后的PDP叙事与信任','native_forms':['Collection','PDP','UGC','Email/CRM','Paid landing'],'cta':'Add to cart / Buy / subscribe / learn more','metrics':'PDP CVR / ATC / checkout / AOV / repeat'}
    if 'instagram' in n: return {'attention':'视觉钩子 + 可保存/分享的内容价值','native_forms':['Reels','Carousel','Stories'],'cta':'查看商品/保存/分享/进入链接','metrics':'hold / saves / shares / profile or product clicks'}
    if 'meta' in n: return {'attention':'广告首帧/主图明确产品+理由','native_forms':['Feed Ad','Reels Ad','Carousel','Retargeting'],'cta':'Shop now / Learn more','metrics':'CTR / CPC / CVR / CPA / contribution'}
    return {'attention':'按该平台原生Surface的信息密度组织','native_forms':['Listing','Visual','Video'],'cta':'使用该Surface原生下一步动作','metrics':'CTR / engagement / CVR / contribution as appropriate'}




def _platform_native_authoring_system(platform:str, native_surface:str)->dict[str,Any]:
    p=(platform or '').casefold()
    if 'tiktok' in p:
        return {'system':'TIKTOK_SHOP_NATIVE_COMMERCE','entry_logic':'Discovery traffic may have low category intent; identify the exact product/category immediately before expanding the story.','hook_logic':'Visual/scene/problem/demonstration hook must still make product identity legible within the first beat.','message_sequence':['IDENTIFY','RELATE / DEMONSTRATE','PROOF / RISK REDUCTION','PRODUCT CLICK / SHOP ACTION'],'copy_density':'Short spoken-natural clauses; subtitle-safe; one major message per beat.','creator_logic':'Creator voice may change wording and scene, but Product Truth, claim strength and package/usage facts remain frozen.','offer_logic':'Offer/urgency enters only after value is understood and economics/platform rules support it.','measurement':'hold / product click / CTR / CVR / creator contribution / return-theme feedback','why':'TikTok Shop combines recommendation/content behavior with commerce; native execution must earn attention without sacrificing exact product identity.'}
    if 'shopee' in p:
        return {'system':'SHOPEE_COMPARISON_COMMERCE','entry_logic':'Users often compare adjacent products quickly from mobile search/listing cards.','hook_logic':'Exact product + decisive spec/value cue + clear variant/pack fit.','message_sequence':['SEARCH RELEVANCE','SPEC / VALUE COMPARISON','TRUST / PROOF','PACKAGE / USAGE / FAQ','ORDER / CHAT ACTION'],'copy_density':'Compact and scannable; structured facts outrank long brand narrative.','creator_logic':'Where creator/video exists, use it to demonstrate fit/usage rather than duplicate Listing copy.','offer_logic':'Price/promo helps comparison only when it does not obscure configuration and contribution economics.','measurement':'search CTR / PDP CVR / chat-question themes / variant error / return themes','why':'Shopee purchase friction is strongly comparison-driven; mobile clarity, specs and objection resolution should reduce switching uncertainty.'}
    if 'amazon' in p:
        return {'system':'AMAZON_SEARCH_PROOF_SYSTEM','entry_logic':'Search relevance and main-image identity establish the comparison set before PDP persuasion.','hook_logic':'Readable exact title + compliant main image; secondary Gallery/Bullets then answer why this offer fits.','message_sequence':['SEARCH IDENTITY','CORE BENEFIT','RTB / SPEC','OBJECTION / USAGE','DEEP PROOF / A+ WHEN AVAILABLE'],'copy_density':'Keyword-aware but readable; no keyword stuffing; each bullet/gallery slot adds incremental evidence.','creator_logic':'Video/A+ should deepen proof and use-context, not change the authoritative product/claim facts.','offer_logic':'Do not leak promotional content into fields/surfaces whose current rules prohibit it.','measurement':'search-term CTR / CVR / return reason / query mismatch / content experiment','why':'Amazon is a search-and-comparison environment where compliant discoverability and evidence sequence must work together.'}
    if 'shopify' in p or 'dtc' in p:
        return {'system':'DTC_MODULAR_PDP_LIFECYCLE','entry_logic':'Traffic may arrive from paid/social/search/CRM with different prior beliefs; landing modules should resolve the next belief state.','hook_logic':'Primary promise + exact product identity + immediate proof cue above the fold.','message_sequence':['PROMISE / IDENTITY','PROOF','FIT / USE CASE','OBJECTION','USAGE / PACKAGE','OFFER / CTA','RETENTION / CRM'],'copy_density':'Can carry more narrative depth than marketplaces, but every module must add a new decision answer.','creator_logic':'UGC supplies lived context/voice while product facts and claims remain authority-bound.','offer_logic':'Offer and subscription/bundle logic should connect to lifecycle economics, not just front-end conversion.','measurement':'PDP CVR / ATC / checkout / AOV / contribution / repeat / cohort retention','why':'DTC controls more of the page and lifecycle, so native strategy should use modular belief progression and retention economics rather than copy marketplace layouts.'}
    return {'system':'PLATFORM_NATIVE_GENERIC','entry_logic':'Start from the user state on this surface.','hook_logic':'Exact product identity + one decision reason.','message_sequence':['IDENTIFY','RELATE','BELIEVE','REDUCE RISK','NEXT_ACTION'],'copy_density':'Match the surface attention budget.','creator_logic':'Reuse Strategy Authority, not identical copy.','offer_logic':'Use offer only when economically/platform valid.','measurement':'CTR / engagement / CVR / contribution','why':'Native authoring adapts information order and density without changing Product Truth or Message Authority.'}

def _native_surface(platform:str, asset:dict[str,Any])->tuple[str,str,bool]:
    p=(platform or '').casefold(); fam=asset.get('family'); typ=asset.get('asset_type'); surface=str(asset.get('surface') or '').upper()
    if 'tiktok' in p:
        if surface=='SEARCH_RESULTS': return ('TikTok Shop Search Card','搜索卡需要产品身份、类目/规格和单一购买理由；不复刻Gallery全文。',True)
        if surface=='CREATOR' or fam=='CREATOR_AFFILIATE': return ('TikTok Creator Short Video','同一策略概念可复用，但需要Creator口播、动作、首帧和评论语境重制。',True)
        if surface=='LIVE' or fam=='LIVE': return ('TikTok LIVE Commerce','需要直播循环话术、演示节奏、异议响应和可重复CTA，不是短视频脚本拉长。',True)
        if typ=='VIDEO' or surface=='PDP_VIDEO': return ('TikTok Shop Product Video','需要移动端静音可读首帧、短Beat证明和商品卡CTA。',True)
        if surface=='PAID_AD': return ('TikTok Paid / Spark Creative','首秒注意力、原生感和广告CTA需要单独生产，同时保持Product Truth。',True)
        return ('TikTok Shop Gallery / PDP','可复用产品母资产，但按Shop移动端Gallery顺序、缩略图识别和购买问题重排。',False)
    if 'shopee' in p:
        if surface=='SEARCH_RESULTS': return ('Shopee Search Card','搜索卡优先产品/变体/规格/价值识别，信息密度低于PDP。',True)
        if surface in {'FAQ','CHAT'}: return ('Shopee Chat / FAQ','把高频异议变成短句式可回复答案，并绑定规格/使用/包裹事实。',False)
        if typ=='VIDEO' or surface=='PDP_VIDEO': return ('Shopee Product Video','用短演示降低比较和使用不确定性，避免重复静态Gallery。',True)
        return ('Shopee Listing Gallery / PDP','共享产品母资产，按移动端比较、规格和风险消解重排。',False)
    if 'amazon' in p:
        if surface=='SEARCH_RESULTS': return ('Amazon Search Result','可读关键词相关性 + 精确产品身份 + 主图规范优先。',True)
        if surface=='A_PLUS': return ('Amazon A+ Content','用模块化品牌/证据/比较信息补充PDP，而非重复Bullets。',True)
        if typ=='VIDEO' or surface=='PDP_VIDEO': return ('Amazon PDP Video','围绕使用/证据/尺寸理解做演示，避免重复Gallery静帧。',True)
        return ('Amazon Gallery / PDP Media','共享事实和母资产，按Search/PDP的增量决策问题重新编排。',False)
    if 'shopify' in p or 'dtc' in p:
        if surface in {'SEARCH_RESULTS','COLLECTION'}: return ('DTC Collection / Search','卡片级身份、差异和价值提示，进入PDP后再展开证据。',True)
        if surface=='CRM': return ('DTC CRM','按生命周期/行为触发重新组织理由、使用与复购，不复制PDP。',True)
        if fam in {'CREATOR_AFFILIATE','VIDEO'} or typ=='VIDEO': return ('DTC UGC / PDP Video','用UGC/演示承担信任或使用任务，并与PDP模块形成互补。',True)
        if surface in {'LANDING','PAID_AD'}: return ('DTC Landing / Paid','广告承诺与落地首屏必须消息连续，并按流量意图重排证据。',True)
        return ('DTC PDP Media / Modules','共享策略与母资产，按DTC信念推进、异议和生命周期组件重排。',False)
    return (asset.get('surface') or 'Platform-native surface','复用策略核心并按目标Surface重新编译。',False)


def _surface_authoring_contract(platform:str,native_surface:str,asset:dict[str,Any])->dict[str,Any]:
    ns=(native_surface or '').casefold(); q=asset.get('consumer_question'); metric=asset.get('success_metric')
    base={'surface':native_surface,'decision_job':q,'single_primary_job':True,'message_density':'One primary decision answer + only incremental proof','proof_rule':'Use only Product Truth / approved claims / explicit expectation information','metric':metric,'why':'Surface-specific authoring changes information order, density, CTA and production form while keeping the same upstream Strategy Authority.'}
    if 'search' in ns:
        base.update({'entry_state':'High scan speed / incomplete context','first_frame_or_line':'Exact product/category/variant identity before persuasion','cta_logic':'Earn qualified click','measurement':'qualified CTR + downstream CVR','avoid':'Long narrative, repeated proof, ambiguous variant identity'})
    elif 'creator' in ns or 'ugc' in ns:
        base.update({'entry_state':'Content feed / social proof context','first_frame_or_line':'Human problem/relevance or demonstration with product identity immediately recoverable','cta_logic':'Native product-card/profile action after value/proof','measurement':'2s/hold rate + product clicks + CVR + comment misunderstanding','avoid':'Ad-like feature dump or identity stereotype'})
    elif 'live' in ns:
        base.update({'entry_state':'Live, interruptible, repeated-entry audience','first_frame_or_line':'Repeatable product identity + current question/offer context','cta_logic':'Time-appropriate shop action without false urgency','measurement':'watch → product click → checkout + question resolution','avoid':'Linear one-time script that fails for mid-stream entrants'})
    elif 'chat' in ns or 'faq' in ns or 'crm' in ns:
        base.update({'entry_state':'Known objection or lifecycle trigger','first_frame_or_line':'Answer the specific question/trigger immediately','cta_logic':'Resolve uncertainty or drive next lifecycle action','measurement':'resolution / conversion / repeat / return reduction','avoid':'Top-of-funnel slogan repetition'})
    elif 'gallery' in ns or 'pdp' in ns or 'a+' in ns or 'modules' in ns:
        base.update({'entry_state':'Active product evaluation','first_frame_or_line':'Identity/relevance first; each subsequent module must add new decision information','cta_logic':'Move belief state toward purchase without hiding package/usage limits','measurement':'PDP CVR + module interaction + returns/CS themes','avoid':'Multiple assets repeating the same headline'})
    else:
        base.update({'entry_state':'Surface-specific','first_frame_or_line':'Make product identity and assigned decision question legible','cta_logic':'Use native next action','measurement':metric or 'surface KPI','avoid':'Copying another surface verbatim'})
    return base


def _surface_production_contract(platform:str,native_surface:str,asset:dict[str,Any],target:dict[str,Any]|None=None)->dict[str,Any]:
    """Compile production intent without pretending generic defaults are submission policy."""
    target=target or {}; ns=(native_surface or '').casefold(); typ=str(asset.get('asset_type') or '').upper()
    contract={
        'surface':native_surface,'asset_type':typ,'master_asset_strategy':'Reuse upstream Product Truth / message / product master where possible; recompose rather than blindly crop when entry state changes.',
        'product_fidelity':asset.get('product_fidelity'),'single_primary_job':asset.get('consumer_question'),
        'policy_authority':'Use the compiled platform pack / current platform policy for exact pixel, duration, file-size, text-overlay and submission constraints. Working intents below are creative-production guidance, not a substituted policy source.',
        'working_format_intent':'STATIC_OR_MOTION_AS_ASSIGNED','first_frame_requirement':'Product identity and the assigned decision job must remain recoverable at mobile scan speed.',
        'safe_zone_logic':'Keep product identity, locked copy, proof and CTA away from UI/crop-risk zones defined by the actual target surface.',
        'copy_density':'One primary decision answer; secondary proof only when it adds incremental information.',
        'audio_caption_logic':'If motion/spoken content is used, core meaning remains understandable with captions/on-screen proof; do not rely on audio alone.',
        'deliverable_logic':['MASTER_TRUTH_ASSET_OR_LOCKED_PRODUCT_LAYER','SURFACE_NATIVE_COMPOSITION','EDITABLE_COPY/SAFE_ZONE_LAYER','TRACE_TO_STRATEGY_AUTHORITY'],
        'measurement':asset.get('success_metric'),
    }
    if 'search' in ns:
        contract.update({'working_format_intent':'STATIC_SCAN_CARD','motion_logic':'Not required unless platform surface explicitly supports it.','first_frame_requirement':'Exact product/variant identity + one qualified-click reason; no long narrative.','production_priority':['thumbnail legibility','variant/spec clarity','clean crop resilience']})
    elif 'creator' in ns or 'ugc' in ns:
        contract.update({'working_format_intent':'VERTICAL_NATIVE_VIDEO_INTENT','motion_logic':'Human/problem/demo beat in the opening, then product identity and proof; shots should feel native without sacrificing product truth.','audio_caption_logic':'Spoken-natural local script + captions; key claim/proof must be visually recoverable.','production_priority':['opening hold','human relevance without stereotype','product recoverability','caption safe area','native CTA handoff']})
    elif 'live' in ns:
        contract.update({'working_format_intent':'LIVE_LOOP_MODULES','motion_logic':'Repeatable 20–60s commerce modules that work for mid-stream entrants; demonstration and objection-response blocks are modular.','audio_caption_logic':'Host speech is primary but product name/spec/offer/claim boundary should remain visually recoverable where the surface allows.','production_priority':['repeatable identity','demo visibility','question response','offer truth','mid-stream comprehension']})
    elif 'paid' in ns or 'spark' in ns or 'landing' in ns:
        contract.update({'working_format_intent':'PAID_NATIVE_CUTDOWN_OR_LANDING_HERO','motion_logic':'Creative must preserve message continuity from hook/ad to product card or landing first screen.','production_priority':['hook continuity','product truth','proof before CTA','variant/offer continuity']})
    elif 'video' in ns:
        contract.update({'working_format_intent':'PRODUCT_VIDEO','motion_logic':'Each beat reveals one new buying answer; include product identity early and use macro/demo only when the question requires it.','production_priority':['first-frame identity','incremental beat sequence','caption legibility','truthful demo']})
    elif 'chat' in ns or 'faq' in ns or 'crm' in ns:
        contract.update({'working_format_intent':'TEXT_OR_LIGHTWEIGHT_CONTENT_MODULE','motion_logic':'Normally unnecessary; optimize for exact answer and reusable response block.','production_priority':['question-answer immediacy','fact trace','local-language clarity']})
    elif 'gallery' in ns or 'pdp' in ns or 'a+' in ns or 'modules' in ns:
        contract.update({'working_format_intent':'MODULAR_PRODUCT_MEDIA','motion_logic':'Static by default unless assigned video; each module must add a distinct decision answer.','production_priority':['product scale consistency','cross-asset hierarchy','copy safe zone','incremental information','truthful material rendering']})
    overrides=(target.get('surface_production_overrides') or {}).get(native_surface) if isinstance(target.get('surface_production_overrides'),dict) else None
    if isinstance(overrides,dict): contract['explicit_target_overrides']=overrides
    return contract

def build_content_matrix_depth(targets:list[dict[str,Any]], culture:dict[str,Any], assets:list[dict[str,Any]], positioning:dict[str,Any], commerce_profile:dict[str,Any]|None=None):
    rows=[]; primary=positioning.get('primary_conversion_proposition'); hierarchy=positioning.get('message_hierarchy') or []; commerce_profile=commerce_profile or {'category_family':'GENERAL_COMMERCE','content_cadence':{},'message_architecture':{},'proof_hierarchy':[]}
    for t in targets:
        prof=_platform_profile(t.get('platform_family'))
        for i,a in enumerate(assets):
            q=a.get('consumer_question') or ''; stage=a.get('journey_stage') or 'DECISION_SUPPORT'
            intent=a.get('decision_intent') or classify_decision_intent(q)
            script=_category_script_structure(commerce_profile.get('category_family','GENERAL_COMMERCE'),intent,a.get('asset_type'))
            if a.get('family') in {'CREATOR_AFFILIATE','VIDEO'}: hook_type='PROBLEM / RELEVANCE / DEMONSTRATION'
            elif a.get('surface') in {'PAID_AD','SEARCH_RESULTS'}: hook_type='IDENTITY + VALUE'
            else: hook_type='DECISION ANSWER'
            hook=(a.get('visible_copy') or {}).get('headline') or (primary if i==0 else q)
            native_surface,reuse_strategy,new_prod=_native_surface(t.get('platform_family'),a)
            native_system=_platform_native_authoring_system(t.get('platform_family'),native_surface)
            surface_contract=_surface_authoring_contract(t.get('platform_family'),native_surface,a)
            production_contract=_surface_production_contract(t.get('platform_family'),native_surface,a,t)
            msg_layer='P0' if stage=='IDENTIFY' else ('P1' if stage in {'RELATE','DECISION_SUPPORT'} else ('P2' if stage=='BELIEVE' else 'P3'))
            visible_locales=t.get('visible_copy_locales') or ([t.get('primary_locale')] if t.get('primary_locale') else [])
            local_authoring_tasks=[{'locale':loc,'surface':native_surface,'message_layer':msg_layer,'source_message':hook,'task':'Rewrite natively for this locale/surface while preserving product truth, claim strength and decision job.','search_or_discovery_logic':'Use locale-specific search/creator language only when supported by current research; do not translate keywords mechanically.','culture_logic':'Apply CultureContext to wording, people, gestures, clothing and taboo checks without turning identity into stereotype.'} for loc in visible_locales]
            beat_plan=[{'beat':1,'job':'HOOK / IDENTIFY','content':hook,'why':'Earn attention while keeping product/category identity legible.'},{'beat':2,'job':'ANSWER DECISION QUESTION','content':q,'why':'Resolve the single incremental consumer question assigned to this asset.'},{'beat':3,'job':'PROOF / RISK REDUCTION','content':a.get('belief_target') or a.get('incremental_information'),'why':'Use only evidence/expectation information needed to move the user to the next state.'},{'beat':4,'job':'NATIVE NEXT ACTION','content':(a.get('visible_copy') or {}).get('cta') or prof['cta'],'why':'CTA follows value/proof and uses the platform-native action.'}]
            rows.append({
                'platform':t.get('platform_family'),'site':t.get('site'),'market':t.get('market'),'audience':t.get('audience') or positioning.get('target_user'),
                'surface':a.get('surface'),'native_surface':native_surface,'asset_id':a.get('asset_id'),'content_pillar':stage,'message_layer':msg_layer,
                'consumer_entry_state':a.get('entry_state'),'consumer_exit_state':a.get('exit_state'),'purchase_barrier':a.get('purchase_barrier'),'belief_target':a.get('belief_target'),
                'topic':q,'hook_type':hook_type,'hook':hook,'script_structure':script,'visual_form':f"{a.get('asset_type')} / {a.get('surface')}",
                'platform_native_logic':prof['attention'],'native_authoring_system':native_system,'surface_authoring_contract':surface_contract,'surface_production_contract':production_contract,'visible_copy_locales':visible_locales,'primary_locale':t.get('primary_locale'),'local_authoring_tasks':local_authoring_tasks,'beat_plan':beat_plan,'copy_contract':{'one_primary_job':q,'message_layer':msg_layer,'claim_boundary':'Product Truth + approved claims only','no_word_for_word_translation':True},'category_message_sequence':(commerce_profile.get('message_architecture') or {}).get('sequence',[]),'category_proof_hierarchy':commerce_profile.get('proof_hierarchy') or [],'content_cadence':commerce_profile.get('content_cadence') or {},'cadence_role':f"Resolve/refresh {intent} when this decision state remains a live friction; do not publish by arbitrary quota.",'reuse_strategy':reuse_strategy,'requires_platform_specific_production':new_prod,
                'cta':(a.get('visible_copy') or {}).get('cta') or prof['cta'],'metric':a.get('success_metric') or prof['metrics'],'race_stage':'COMMUNICATION',
                'culture_adaptation':culture.get('visual_implications',[])+culture.get('copy_implications',[]),'taboo_stereotype_check':'身份用于代表性/语言/语境，不自动推导消费行为；人物、动作和暴露程度按现有文化证据审核。',
                'business_hypothesis':a.get('business_hypothesis') or f"若解决“{q}”这一阻力，应改善对应Surface的下一步行为，而不是要求该资产独立承担全部转化。",
                'why':a.get('reason_to_exist') or f"这条内容只承担一个增量购买问题：{q}",
            })
    return rows


def _cmf_lighting_profile(cmf:dict[str,Any], master_lighting:dict[str,Any])->dict[str,Any]:
    material=str(cmf.get('material') or '').casefold(); finish=str(cmf.get('finish') or '').casefold(); behavior=cmf.get('surface_behavior') or {}
    text=' '.join([material,finish,str(behavior).casefold()])
    risks=[]; geometry=[]; reflection=[]
    if any(x in text for x in ['glass','透明','translucent','clear']):
        risks += ['edge/refraction can disappear on similar-value backgrounds','uncontrolled front reflection can obscure label/product contents']
        geometry += ['Use broad side/back gradients to describe transparent edges; preserve a readable front plane.','Control background luminance separately from product edge separation.']
        reflection += ['Flag camera/front reflections; use polarization only when it does not erase truthful material cues.']
    if any(x in text for x in ['gloss','glossy','亮','lacquer','plastic','膜']):
        risks += ['specular hotspot can clip print/color','large source may flatten cylindrical/curved form if both sides fill equally']
        geometry += ['Place a large diffusion source to create a long controlled highlight gradient rather than a point hotspot.','Use negative fill/flags to restore edge shape on curved glossy surfaces.']
        reflection += ['Rotate product/source/camera relationship before retouching reflections away.']
    if any(x in text for x in ['metal','metallic','金属','foil','chrome']):
        risks += ['mirror-like surface reflects the studio rather than revealing intrinsic color','small bright sources create hard distracting hotspots']
        geometry += ['Build intentional bright/dark reflection cards around the object; light the reflected environment, not only the object.']
        reflection += ['Treat polarization as conditional; many metallic reflections will not disappear with polarization.']
    if any(x in text for x in ['matte','哑','soft-touch','paper','纸']):
        risks += ['over-diffusion can make texture/embossing unreadable','grazing light may exaggerate defects beyond normal perception']
        geometry += ['Use controlled oblique light when texture/embossing is decision-relevant; otherwise keep broad tonal separation.']
    if any(x in text for x in ['textile','fabric','nylon','polyester','cotton','leather','woven','weave','织物','面料','尼龙','皮革']):
        risks += ['front-flat light can erase weave, seam and soft-volume cues','hard grazing light can exaggerate wrinkles or surface defects beyond normal viewing']
        geometry += ['Use broad oblique/side light to reveal weave and soft volume without turning normal wrinkles into defects.','Preserve color consistency because textile shade drift strongly changes product expectation.']
        reflection += ['For synthetic sheen, test source/camera angle before polarization; preserve enough sheen to keep the real fiber/finish readable.']
    if not risks:
        risks=['Material-specific optical behavior is under-specified; do not invent gloss/transparency/metal behavior.']
        geometry=['Use supplied master lighting as provisional; capture a material test frame before locking production geometry.']
    reflective=any(x in text for x in ['glass','透明','translucent','clear','gloss','glossy','亮','lacquer','plastic','膜','metal','metallic','金属','foil','chrome'])
    metallic=any(x in text for x in ['metal','metallic','金属','foil','chrome'])
    prelight={
        'objective':'Lock material truth, label readability and repeatable highlight geometry before hero capture.',
        'frames':['neutral reference / product color frame','front-label readability frame','edge/material-response frame'] + (['reflection-control comparison frame'] if reflective else []),
        'acceptance':['required copy remains legible','material still reads as the supplied CMF','critical highlight is below clipping','background/product edge separation is repeatable'],
        'boundary':'Prelight validates the real object. If supplied CMF text conflicts with the real pack, the real pack wins and Strategy Authority should be revised.'
    }
    lighting_diagram={
        'camera_axis':'0° reference / exact physical angle comes from supplied camera contract',
        'key':master_lighting.get('key') if isinstance(master_lighting,dict) else None,
        'fill':master_lighting.get('fill') if isinstance(master_lighting,dict) else None,
        'negative_fill':master_lighting.get('negative_fill') if isinstance(master_lighting,dict) else None,
        'rim':master_lighting.get('rim') if isinstance(master_lighting,dict) else None,
        'background_light':master_lighting.get('background') if isinstance(master_lighting,dict) else None,
        'instruction':'Record actual source positions/distances/power after the accepted prelight; do not infer missing geometry from this conceptual diagram.'
    }
    ratio=(master_lighting.get('exposure_ratio') or master_lighting.get('key_fill_ratio')) if isinstance(master_lighting,dict) else None
    exposure_plan={'declared_ratio':ratio,'status':'DECLARED' if ratio not in (None,'') else 'MEASURE_IN_PRELIGHT','measurement':'Measure key/fill or lit/shadow stop difference on the decision-relevant product plane; freeze the accepted ratio for repeat shots.','why':'Numeric ratio is useful only when tied to readable label/material contrast; the runtime does not invent a premium-looking ratio.'}
    polarization={
        'applicable':'CONDITIONAL_TEST' if reflective else 'NORMALLY_NOT_REQUIRED',
        'test':['capture baseline without polarization'] + (['rotate analyzer / cross-polarization where physically applicable and compare label/material truth'] if reflective and not metallic else []) + (['do not expect metallic reflections to disappear with polarization'] if metallic else []),
        'acceptance':'Use polarization only when it removes obstructive glare without erasing truthful gloss, transparency, print or material cues.'
    }
    color_consistency={
        'reference':'Use supplied neutral/product color reference or capture one during prelight.',
        'white_balance':master_lighting.get('white_balance') if isinstance(master_lighting,dict) else None,
        'capture_rule':'Lock WB/exposure reference for a shot family; recapture reference after material/source/background changes.',
        'output_rule':'Compare hero/detail/variant frames against the same product-color reference before surface exports.',
        'why':'Cross-asset color drift changes perceived shade/material and can create expectation/return risk.'
    }
    return {'material':cmf.get('material'),'finish':cmf.get('finish'),'surface_behavior':behavior,'optical_risks':risks,'lighting_geometry_logic':geometry,'reflection_control_logic':reflection or ['Preserve truthful material cues while preventing reflections from hiding required information.'],'master_lighting_reference':master_lighting,'prelight_plan':prelight,'test_shot_protocol':prelight,'lighting_diagram':lighting_diagram,'exposure_ratio_plan':exposure_plan,'polarization_plan':polarization,'color_consistency_plan':color_consistency,'authority_boundary':'Material response is based only on supplied CMF text/surface behavior. If the real pack differs, the real product is the final source of truth.'}

def _focal_numeric_values(value:Any)->list[float]:
    """Parse focal-length numbers from numeric or human camera-contract text.

    Supports values such as 85, "85mm equivalent", "70–85mm" and "24-70 mm".
    The original text remains the production authority; parsed numbers are used only for
    strategy classification (wide / medium / long), never to rewrite the capture contract.
    """
    if value in (None,"",[],{}): return []
    if isinstance(value,(int,float)): return [float(value)]
    import re
    vals=[]
    for token in re.findall(r'(?<![A-Za-z])\d+(?:\.\d+)?',str(value)):
        try: vals.append(float(token))
        except Exception: pass
    # Ignore obvious non-focal numbers accidentally present later in prose by keeping the first two.
    return vals[:2]


def build_visual_depth(request:dict[str,Any], creative:dict[str,Any], culture:dict[str,Any], positioning:dict[str,Any], assets:list[dict[str,Any]], photography_validation:dict[str,Any]|None):
    vs=request.get('visual_strategy') or {}; photo=request.get('photography_contract') or {}; cmf=creative.get('cmf') or {}
    category_profile=category_execution_profile(request)
    camera=photo.get('camera') or {}; comp=photo.get('composition') or {}; lighting=photo.get('lighting') or {}; color=photo.get('color_management') or {}
    material_lighting_profile=_cmf_lighting_profile(cmf,lighting)
    selected_direction=((creative.get('creative_council') or {}).get('selected_direction') or {})
    style=vs.get('style') or (' × '.join(x for x in [category_profile.get('visual_territory'), selected_direction.get('direction_name') or selected_direction.get('name')] if x)) or '购买问题驱动的产品真实感商业视觉'
    style_why=vs.get('style_why') or f"{category_profile.get('category_family')} 的视觉优先级来自其真实购买问题：{'; '.join(category_profile.get('priority_decisions') or [])}。摄影与构图先回答这些决策，再处理风格。"
    palette=vs.get('palette') or request.get('brand_palette') or []
    camera_planning=camera or {'status':'STRATEGY_RECOMMENDATION_REQUIRES_PRELIGHT','by_job':category_profile.get('camera_plan'),'why':'No executable camera contract was supplied; use category/job ranges to plan tests, then lock actual focal length, distance, height and focus plane during prelight.'}
    lighting_planning=lighting or {'status':'STRATEGY_RECOMMENDATION_REQUIRES_PRELIGHT','category_logic':category_profile.get('lighting_plan'),'why':'No executable lighting contract was supplied; derive geometry from real material response and the decision information that must remain readable.'}
    shot_list=vs.get('shot_list') or request.get('shot_list') or []
    if not shot_list:
        for a in assets:
            if a.get('asset_type')!='IMAGE': continue
            sig=a.get('visual_production_signature') or {}
            shot_list.append({'asset_id':a.get('asset_id'),'shot':a.get('asset_name'),'commercial_job':a.get('strategic_job'),'consumer_question':a.get('consumer_question'),'camera':camera,'composition':(a.get('creative_brief') or {}).get('composition') or sig.get('composition_grammar') or comp,'lighting':(a.get('creative_brief') or {}).get('lighting') or lighting,'visual_information_grammar':sig.get('composition_grammar'),'decision_evidence_plane':sig.get('evidence_plane'),'differentiation_axis':sig.get('differentiation_axis'),'why':a.get('reason_to_exist')})
    rationale=[]
    def add(element,setting,why,consumer='',business=''):
        if setting not in (None,'',{},[]): rationale.append({'element':element,'setting':setting,'why':why,'consumer_logic':consumer,'business_logic':business})
    add('Product Occupancy / Negative Space',comp,'主体占比、留白和安全区服务移动端识别、文案层级、裁切与平台复用；不是为了“填满画面”。','缩略图先识别产品，同时给必要Copy/证据留出视觉呼吸。','降低跨平台重做和裁切损失。')
    focal=(photo.get('lens') or {}).get('focal_length_mm') if isinstance(photo.get('lens'),dict) else None
    focal=focal if focal is not None else camera.get('focal_length_mm')
    if focal is not None:
        _fvals=_focal_numeric_values(focal)
        if _fvals and min(_fvals)>=70: why='较长焦段优先控制包装透视与边缘变形，让标签/几何更接近真实商品；同时压缩背景，适合身份/证据型Packshot。'
        elif _fvals and max(_fvals)<=35: why='较广焦段强化环境与空间关系，只适合场景/使用语境需要；必须避免把包装近大远小变形成不真实商品。'
        elif _fvals: why='中等或跨区间焦段在商品真实性与环境关系之间取舍；最终焦段由当前购买问题和Prelight锁定，不把范围文本强行压成单值。'
        else: why='已提供焦段/镜头文本，但无法安全解析为单一数值；保留原始摄影合同，在Prelight中按商品几何、信息可读性与场景关系锁定最终值。'
        add('Focal Length',focal,why,'真实透视帮助用户建立正确商品预期。','减少商品形态失真导致的真实性风险。')
    add('Working Distance',camera.get('working_distance'),'工作距离与焦段共同决定透视和主体占比；优先选择能保持包装几何、标签可读且便于控光/反射的距离。','避免夸张透视让用户误判尺寸/形态。','提高拍摄可复制性。')
    add('Camera Height',camera.get('camera_height'),'机位高度决定产品权威感、顶部/侧面可见量和标签可读性；围绕当前购买问题选择，而不是固定平拍。','让用户看到做决策真正需要的面。','减少“好看但信息缺失”的无效镜头。')
    add('Yaw',camera.get('yaw_deg'),'Yaw用于决定正面身份可读性与侧面结构信息的权衡；身份图更克制，结构/形态图才增加角度。')
    add('Pitch',camera.get('pitch_deg'),'Pitch控制顶部/底部可见信息与透视；只有规格、盖体、开口或使用动作需要时才引入更明显俯仰。')
    add('Roll',camera.get('roll_deg'),'Roll默认保持稳定商品几何；倾斜只在创意动势能服务平台注意力且不损害产品真实性时使用。')
    add('Focus Plane',camera.get('focus_plane') or (photo.get('focus_dof') or {}).get('focus_plane'),'对焦面优先落在当前资产承担的关键事实（通常是正面标签/材质/使用部位），确保购买信息清楚。')
    add('Aperture / DOF',camera.get('aperture_dof_intent') or (photo.get('focus_dof') or {}),'景深由信息任务决定：身份/证据图要让关键包装信息完整可读；情绪/场景图才允许更浅景深引导注意。')
    key=lighting.get('key') if isinstance(lighting,dict) else None
    add('Key Light Geometry',key,'主光方向、面积、距离先服务材质、形体和标签可读性，再服务氛围；大扩散源常用于控制高光梯度，但具体几何应匹配材质。')
    add('Fill',lighting.get('fill') if isinstance(lighting,dict) else None,'Fill控制暗部信息是否仍可读取；不是简单“提亮”，而是决定对比度与肤色/包装暗部细节。')
    add('Negative Fill',lighting.get('negative_fill') if isinstance(lighting,dict) else None,'Negative Fill用于恢复边缘层次和材质体积，避免大柔光把包装拍平。')
    add('Rim / Edge Separation',lighting.get('rim') if isinstance(lighting,dict) else None,'轮廓光只在需要从背景分离透明/深色/反光边缘时使用，不默认追求“高级光边”。')
    add('CCT',lighting.get('cct') if isinstance(lighting,dict) else None,'色温服务真实产品色、肤色和场景氛围的一致性；先保证中性参考和品牌色忠实，再做暖/冷氛围。')
    add('White Balance',color.get('white_balance') if isinstance(color,dict) else None,'白平衡锁定跨镜头颜色基准，避免不同资产中包装白、品牌绿或肤色漂移。')
    add('Shadow',lighting.get('shadow') if isinstance(lighting,dict) else None,'阴影方向/长度/软硬用于说明接触面、重量和空间，而不是随机装饰；电商图优先避免遮挡关键信息。')
    add('Highlight Policy',lighting.get('highlight_policy') if isinstance(lighting,dict) else None,'高光策略保护白包装、金属/亮膜和标签印刷，不让“高光质感”覆盖真实文字/颜色。')
    add('Reflection / Polarization',lighting.get('reflection_control') if isinstance(lighting,dict) else None,'反射控制用于让玻璃、塑料、膜材或金属既保留材质感又可读；完全消反会失去材质，失控反光会遮挡信息。')
    add('Color Management',color,'输出空间、产品色忠实和中性参考确保跨摄影/AI/设计/平台压缩后仍保持品牌与商品一致。','用户看到的产品应接近实际到手颜色。','降低退货/品牌资产漂移。')
    add('CMF',cmf,'Color / Material / Finish决定反射、高光、边缘分离、背景对比和后期方法；CMF是拍摄工程输入，不是配色形容词。')
    add('Casting / Styling',{'casting':vs.get('casting') or culture.get('casting_implications',[]),'styling':vs.get('wardrobe_hair_makeup') or photo.get('styling') or {},'inclusive':creative.get('inclusive_photography')},'人物只有在能回答“是否适合我/如何使用/什么语境”时出现；肤色曝光、发型、服饰、动作与身体暴露要在真实文化语境中自然，不把身份变成行为标签。')
    asset_parameter_reasoning=[]
    for a in assets:
        if a.get('asset_type')!='IMAGE': continue
        brief=a.get('creative_brief') or {}; q=a.get('consumer_question'); job=a.get('strategic_job'); surface=a.get('surface')
        shot_light=brief.get('lighting') or lighting
        intent=a.get('decision_intent') or 'DECISION_SUPPORT'
        if camera:
            asset_camera_choice=camera
        else:
            camera_role='context_or_use' if intent in {'RELEVANCE','USAGE','FIT_WEAR','STORAGE_STACKING','SEAL_LEAK'} else 'identity_or_proof'
            if intent=='MATERIAL_SENSORY': camera_role='macro'
            asset_camera_choice={'status':'STRATEGY_RECOMMENDATION_REQUIRES_PRELIGHT','lens_family':(category_profile.get('camera_plan') or {}).get(camera_role),'camera_height':'Choose height to expose the exact face/body relation required by this decision intent.','working_distance':'MEASURE_TO_PRESERVE_GEOMETRY_AND_REQUIRED_SCALE','focus_plane':'Decision-relevant product/body/material plane','intent':intent}
        sig=a.get('visual_production_signature') or {}
        asset_parameter_reasoning.append({'asset_id':a.get('asset_id'),'surface':surface,'consumer_question':q,'decision_intent':intent,'strategic_job':job,'decision_visibility_required':a.get('incremental_information') or a.get('belief_target'),'visual_production_signature':sig,'composition_choice':brief.get('composition') or sig.get('composition_grammar') or comp,'camera_choice':asset_camera_choice,'lighting_choice':shot_light or category_profile.get('lighting_plan'),'cmf_choice':brief.get('color') or cmf,'category_execution_profile':category_profile,'material_lighting_profile':material_lighting_profile,'shot_lighting_reasoning':{'material_response_to_show':material_lighting_profile.get('material') or material_lighting_profile.get('finish') or 'SUPPLIED_CMF_REQUIRED','key_geometry_why':(material_lighting_profile.get('lighting_geometry_logic') or [None])[0],'fill_negative_fill_why':'Use fill only to retain decision-relevant shadow information; use negative fill when broad diffusion removes form separation.','highlight_reflection_why':'; '.join(material_lighting_profile.get('reflection_control_logic') or []),'color_management_why':'Lock neutral/product-color reference before atmosphere grading so product/brand/skin color remains comparable across surfaces.','prelight_plan':material_lighting_profile.get('prelight_plan'),'lighting_diagram':material_lighting_profile.get('lighting_diagram'),'exposure_ratio_plan':material_lighting_profile.get('exposure_ratio_plan'),'polarization_plan':material_lighting_profile.get('polarization_plan'),'color_consistency_plan':material_lighting_profile.get('color_consistency_plan'),'truth_boundary':material_lighting_profile.get('authority_boundary')},'causal_chain':f"Consumer question [{q}] → make assigned evidence/identity visible → choose perspective/composition that preserves product truth → use supplied CMF to shape material-specific highlights/reflections → reduce the named purchase barrier → observe {a.get('success_metric') or 'surface KPI'}",'parameter_why':{'focal_length':'Use the master focal-length logic only if it preserves the exact product geometry/information this asset must show; override for context/macro only when the decision job requires it.','camera_height_yaw_pitch':'Expose the face/feature needed to answer this asset question; do not add angle merely for dynamism.','focus_dof':'Keep the assigned evidence plane readable; shallow DOF is acceptable only outside required decision information.','lighting_geometry':'Shape the actual supplied CMF/material/label/skin evidence needed by this asset; do not apply a generic premium-light recipe.','reflection_polarization':'Retain truthful material cues while removing only reflections that obscure required information; metallic surfaces may not respond to polarization.','color_management':'Protect product/brand/skin color consistency because this asset may be compared with other surfaces.'},'business_logic':a.get('business_hypothesis'),'measurement':a.get('success_metric')})
    return {
        'style':style,'style_why':style_why,'visual_territory':vs.get('visual_territory') or style,'category_execution_profile':category_profile,'category_photography_plan':{'status':'SUPPLIED_CONTRACT' if photo else 'STRATEGY_RECOMMENDATION_REQUIRES_PRELIGHT','camera_plan':category_profile.get('camera_plan'),'lighting_plan':category_profile.get('lighting_plan'),'proof_visuals':category_profile.get('proof_visuals'),'human_rule':category_profile.get('human_rule')},'palette_hex':palette,'cmf':cmf,'material_lighting_profile':material_lighting_profile,'photography_rationale':rationale,
        'composition':comp,'camera':camera_planning,'lens':photo.get('lens') or {'status':'STRATEGY_RECOMMENDATION_REQUIRES_PRELIGHT','focal_length_by_job':category_profile.get('camera_plan')},'focus_dof':photo.get('focus_dof') or {'status':'STRATEGY_RECOMMENDATION_REQUIRES_PRELIGHT','focus_plane':'Decision-relevant plane','aperture_dof_intent':'Keep all decision-critical evidence legible; exact aperture is locked in prelight.'},
        'lighting_framework':lighting_planning,'color_management':color,'scene':vs.get('scene') or photo.get('scene') or {},'props':vs.get('props') or photo.get('props') or [],
        'casting':vs.get('casting') or {'constraints':culture.get('casting_constraints') or culture.get('casting_implications') or []},'wardrobe_hair_makeup':vs.get('wardrobe_hair_makeup') or photo.get('styling') or {},
        'platform_dimensions':vs.get('platform_dimensions') or {},'shot_list':shot_list,'asset_parameter_reasoning':asset_parameter_reasoning,'asset_visual_production_signatures':[{'asset_id':a.get('asset_id'),'decision_intent':a.get('decision_intent'),'decision_topic':a.get('decision_topic'),'surface':a.get('surface'),'race_stage':a.get('race_stage'),'information_assetization':a.get('information_assetization') or {},'product_presence':a.get('product_presence') or {},'surface_copy_budget':a.get('surface_copy_budget') or {},'creative_direction_id':(a.get('creative_direction') or {}).get('direction_id'),'visual_expression_variant':a.get('visual_expression_variant') or {},'production_mode':a.get('production_mode'),'signature':a.get('visual_production_signature') or {},'editable_layer_contract':a.get('editable_layer_contract') or {}} for a in assets],'creative_opportunity_universe':creative.get('creative_opportunity_universe') or {},'selected_creative_opportunities':selected_direction.get('opportunity_mechanisms') or [],'surface_architecture':creative.get('surface_architecture') or {},'video_creator_plan':creative.get('video_creator_plan') or {},'paid_campaign_architecture':creative.get('paid_campaign_architecture') or {},'inclusive_photography':creative.get('inclusive_photography'),'photography_validation':photography_validation,
        'decision_card':_why('把Positioning / Message Hierarchy / Consumer Question翻译成统一的视觉、CMF和摄影因果系统。',style_why,consumer='画面层级必须让用户先看见产品身份和当前购买问题的答案。',platform='移动端Surface优先保证缩略图识别、裁切安全、字幕/Copy安全区和信息密度。',culture='人物、肤色、服化道、动作与场景服从CultureContext，不把“本地化”简化成装饰元素。',business='统一视觉系统降低多资产漂移，并让Hero、证据图、人物图、Creator和Paid各自承担不同任务。',execution='逐参数WHY、CMF、场景、道具与排版写入资产合同；产品真源层按Fidelity规则处理。',measurement='先过产品真实性/可读性/信息层级QA，再在真实Surface观察CTR/CVR/互动与误解反馈。')
    }

def build_asset_portfolio_depth(assets:list[dict[str,Any]]):
    rows=[]; seen={}; overlaps=[]; question_groups={}
    for i,a in enumerate(assets):
        q=_clean(a.get('consumer_question')).casefold(); job=_clean(a.get('strategic_job')).casefold(); surface=_clean(a.get('surface')).casefold(); key=(q,job,surface)
        question_groups.setdefault(q,[]).append(a.get('asset_id'))
        if key in seen: overlaps.append({'asset_id':a.get('asset_id'),'overlaps_with':seen[key],'reason':'相同消费者问题 + 相同战略任务 + 相同Surface，应优先复用/合并而不是增加资产数。','recommended_action':'MERGE_OR_REUSE'})
        else: seen[key]=a.get('asset_id')
        rows.append({'sequence':i+1,'asset_id':a.get('asset_id'),'asset_name':a.get('asset_name'),'decision_intent':a.get('decision_intent'),'merged_consumer_questions':a.get('merged_consumer_questions',[]),'surface':a.get('surface'),'surface_need':f"{a.get('surface')} 是否需要独立解决该购买问题，而不是机械复制其他Surface",'family':a.get('family'),'priority':a.get('priority'),'consumer_question':a.get('consumer_question'),'purchase_barrier':a.get('purchase_barrier'),'belief_target':a.get('belief_target'),'entry_state':a.get('entry_state'),'exit_state':a.get('exit_state'),'strategic_job':a.get('strategic_job'),'reason_to_exist':a.get('reason_to_exist'),'incremental_information':a.get('incremental_information'),'business_hypothesis':a.get('business_hypothesis') or f"解决“{a.get('consumer_question')}”后，应改善 {a.get('success_metric')} 对应的下一步行为。",'handoff':a.get('handoff'),'success_metric':a.get('success_metric'),'production_mode':a.get('production_mode'),'product_fidelity':a.get('product_fidelity'),'race_stage':a.get('race_stage'),'information_assetization':a.get('information_assetization') or {},'product_presence':a.get('product_presence') or {},'surface_copy_budget':a.get('surface_copy_budget') or {},'creative_direction_id':(a.get('creative_direction') or {}).get('direction_id'),'visual_expression_variant':a.get('visual_expression_variant') or {},'visual_production_signature':a.get('visual_production_signature') or {},'editable_layer_contract':a.get('editable_layer_contract') or {}})
    cross_surface=[]
    for q,ids in question_groups.items():
        if q and len(ids)>1: cross_surface.append({'consumer_question':q,'asset_ids':ids,'review_rule':'同一问题跨Surface可存在，但必须证明平台原生形态/信息深度/受众状态不同；否则复用母资产或合并。'})
    intent_groups={}
    for a in assets:
        intent=a.get('decision_intent') or 'DECISION_SUPPORT'; intent_groups.setdefault(intent,[]).append({'asset_id':a.get('asset_id'),'surface':a.get('surface'),'question':a.get('consumer_question')})
    semantic_review=[]
    for intent,group in intent_groups.items():
        if len(group)>1:
            semantic_review.append({'decision_intent':intent,'assets':group,'review_rule':'同一Decision Intent可以跨Surface存在，但必须证明每个资产提供不同尺度/证据/操作深度；同Surface且没有增量信息时应合并。'})
    return {'fixed_count_authority':False,'asset_count':len(rows),'portfolio':rows,'overlap_review':overlaps,'cross_surface_reuse_review':cross_surface,'semantic_intent_review':semantic_review,'curation_rules':['Consumer Decision Question','Decision Intent','Strategic Job','Surface Need','Incremental Information','Business Hypothesis','Success Metric'],'why':'资产数量来自尚未解决的购买问题、Decision Intent、Surface职责、增量信息和可验证商业假设；没有新的信息/任务就不应该因为“还差一张”而新增。'}

def build_culture_depth(target:dict[str,Any]|list[dict[str,Any]], culture:dict[str,Any]):
    targets=target if isinstance(target,list) else [target]
    targets=[t or {} for t in targets] or [{}]
    inter=culture.get('intersectionality') or {}; rows=[]
    if isinstance(inter,dict):
        for dim,val in inter.items():
            rows.append({'dimension':dim,'evidence':val,'commercial_relevance':'只在影响语言、代表性、场景、服化道、支付/使用语境或内容理解时进入执行。','execution':'结合该维度与其他维度交叉评估，不把单一身份变量当行为结论。','why':'交叉性用于避免“一个人口标签代表全部用户”的粗糙本地化。'})
    adaptation=[]
    for kind,key in [('语言/文案','copy_implications'),('视觉/场景','visual_implications'),('选角/人物','casting_implications')]:
        vals=culture.get(key) or []
        for v in vals: adaptation.append({'adaptation_point':kind,'evidence_or_implication':v,'inclusive_representation':'让目标用户在语言/人物/语境上感到自然且被准确代表。','stereotype_taboo_risk':'检查是否把身份特征直接等同于行为、审美偏好或购买动机。','result':'APPLY','modification':'写入对应Copy/Casting/Scene/Photography合同。','why':'本地化的目标是减少理解摩擦和陌生感，而不是增加表面“地方元素”。'})
    if not adaptation: adaptation.append({'adaptation_point':'证据驱动基线','evidence_or_implication':'当前没有更具体文化证据。','inclusive_representation':'采用中性、真实、可理解表达。','stereotype_taboo_risk':'不凭空增加族裔、宗教、节庆或审美偏好。','result':'BASELINE','modification':'只在文化差异真实影响商业决策时补研究。','why':'缺证据时克制比“看起来本地化”更专业。'})
    language_profiles=culture.get('language_profiles') or {}
    platform_rows=[]
    for t in targets:
        platform_rows.append({
            'platform':t.get('platform_family'),'site':t.get('site'),'region':t.get('market'),
            'audience':t.get('audience') or '以当前Audience/JTBD证据定义的目标人群',
            'language_locales':(language_profiles.get('profiles') if isinstance(language_profiles,dict) else language_profiles),
            'race_ethnicity':culture.get('race_ethnicity') or '未提供可靠族裔细分事实，不做推断',
            'intersectionality':inter,
            'adaptation':culture.get('copy_implications',[])+culture.get('visual_implications',[])+culture.get('casting_implications',[]),
            'stereotype_taboo_check':'检查语言、人物、动作、服饰、身体暴露、肤色/发型、宗教/节庆、色彩/幽默/CTA等真正相关项；不把身份当购买行为结论。',
            'why':'同一产品在不同市场/平台的价值核心可以一致，但语言层级、人物代表性、场景和内容密度需要与当地真实语境匹配。'
        })
    primary=targets[0]
    return {
        'platform':primary.get('platform_family'),'region':primary.get('market'),'race_ethnicity':culture.get('race_ethnicity') or '未提供可靠族裔细分事实，不做推断',
        'platform_audience_culture_rows':platform_rows,
        'intersectionality_table':rows,'language_profiles':language_profiles,'adaptation_rows':adaptation,
        'casting_constraints':culture.get('casting_constraints') or culture.get('casting_implications') or [],
        'why':'文化策略用于改变表达、代表性和执行细节；不从身份变量自动推出购买行为。'
    }



def build_race_depth(target:dict[str,Any], positioning:dict[str,Any], market:dict[str,Any], content_matrix:list[dict[str,Any]], asset_portfolio:dict[str,Any]):
    """Compile the authoritative CBCC RACE process: Research → Action → Communication → Evaluation.

    RACE is a work/process backbone, not a shopper funnel. Shopper decision intent, journey state and
    purchase barriers remain separate fields. This prevents the legacy Reach/Act/Convert/Engage
    semantics from leaking into asset prompts or content production.
    """
    platforms=[]
    for row in content_matrix:
        key=(row.get('platform'),row.get('site'),row.get('market'))
        if key not in platforms: platforms.append(key)
    if not platforms:
        platforms=[(target.get('platform_family'),target.get('site'),target.get('market'))]
    rows=[]
    for platform,site,market_name in platforms:
        platform_rows=[r for r in content_matrix if r.get('platform')==platform and (not site or r.get('site')==site)]
        label=' / '.join(str(x) for x in [platform,site,market_name] if x)
        assets=[r.get('asset_id') for r in platform_rows if r.get('asset_id')]
        topics=[r.get('topic') for r in platform_rows if r.get('topic')]
        rows.extend([
          {'stage':'RESEARCH','objective':'Establish product truth, evidence, market, platform, audience/culture, competitor and regulatory context before decisions.','key_actions':['Product Truth / Claim / Evidence','Market / competitor / customer research','Current platform / site / category / rule research','Audience / intersectionality / culture context','Regulatory and compliance research'],'assigned_assets':[],'assigned_topics':[],'output':'Research authority + evidence ledger + unresolved facts / 待查证','platform':label,'culture_check':'Identity/culture observations require evidence and cannot be converted into behavioral stereotypes.','kpi':'evidence coverage / source quality / unresolved P0 facts','why':'Strategy quality cannot exceed the quality of product truth and current target-context evidence.'},
          {'stage':'ACTION','objective':'Turn Research into positioning, offer, message hierarchy, content architecture, creative system, photography/CMF and execution priorities.','key_actions':['STP + JTBD','Positioning / value proposition / message hierarchy','4P / funnel / offer / economics','Creative directions / visual system / photography / CMF','Budget and P0/P1/P2 tradeoffs'],'assigned_assets':[],'assigned_topics':topics,'output':'Strategy Authority + content/asset/production contracts','platform':label,'culture_check':'Adapt language, representation and execution without changing product truth or inferring behavior from identity labels.','kpi':'decision coverage / execution readiness / unresolved P0-P1 constraints','why':'Action is where research becomes explicit choices, tradeoffs and executable contracts.'},
          {'stage':'COMMUNICATION','objective':'Execute platform-native Listing, PDP, creator/UGC, paid, live, social/CRM and localized content.','key_actions':['Listing / PDP / Search','Image / video / creator / live production','Paid and organic distribution','Locale-native copy / subtitles / CTA / landing handoff','Rights / music / UTM or equivalent attribution IDs'],'assigned_assets':assets,'assigned_topics':topics,'output':'Platform-native customer-facing communication and production assets','platform':label,'culture_check':'Every live script/model/wardrobe/scene/color/CTA is checked against culture/intersectionality constraints and current evidence.','kpi':'CTR / comprehension / engagement / CVR / qualified action by surface','why':'Communication is execution of the chosen strategy; shopper funnel intent is tracked separately from the RACE process stage.'},
          {'stage':'EVALUATION','objective':'Measure, attribute, test and learn, then route revision to the smallest responsible layer.','key_actions':['KPI and attribution review','A/B / causal experiment where appropriate','Ads diagnostics','Reviews / returns / customer-service feedback','Economics / contribution / incrementality review','Local revision and learning loop'],'assigned_assets':[],'assigned_topics':[],'output':'Measurement result + local revision route + learning update','platform':label,'culture_check':'Review outcomes for representation/cultural harm as well as commercial performance; do not overgeneralize from small identity subgroups.','kpi':'incremental lift / contribution / error reduction / return reduction / learning confidence','why':'Evaluation closes the loop without triggering broad redesign when only one responsible layer failed.'}
        ])
    return rows


def build_strategy_revision_routing(ads:dict[str,Any]|None, feedback:dict[str,Any]|None)->dict[str,Any]:
    """Translate performance/feedback diagnostics into local strategy revision routes.

    This does not auto-edit strategy. It identifies the smallest layer that should be reconsidered and
    explicitly freezes unrelated layers so measurement does not trigger broad redesign.
    """
    routes=[]
    route_map={
      'ELIGIBILITY_TRAFFIC':(['SEARCH_DEMAND','PLATFORM_ELIGIBILITY','MEDIA_BID_BUDGET'],['PRODUCT_TRUTH','POSITIONING','VISUAL_STYLE'],'Do not diagnose creative/PDP before qualified reach exists.'),
      'CLICK_PACKAGE':(['MESSAGE_P0','LISTING_TITLE_HERO','VISUAL_FIRST_FRAME'],['PRODUCT_TRUTH','SKU_ARCHITECTURE','UNRELATED_PDP_MODULES'],'Change one first-impression variable at a time and hold downstream proof/offer stable where possible.'),
      'PDP_CONVERSION':(['LISTING_DECISION_SEQUENCE','PROOF_HIERARCHY','OBJECTION_HANDLING','OFFER_ECONOMICS','TRAFFIC_QUALITY_REVIEW'],['PRODUCT_TRUTH','UNRELATED_VISUAL_STYLE'],'Audit message-match/fit/proof/offer/trust before redesigning every asset.'),
      'MEDIA_EFFICIENCY':(['MEDIA_BID_BUDGET','QUERY_PLACEMENT_MIX'],['PRODUCT_TRUTH','POSITIONING','LISTING_PROOF'],'Media cost symptoms do not by themselves justify changing product/message truth.'),
      'ECONOMICS_OR_MEDIA':(['OFFER_ECONOMICS','PRICE_MARGIN','MEDIA_BID_BUDGET'],['PRODUCT_CLAIMS','UNRELATED_CREATIVE'],'Fix the economic binding constraint before scaling creative volume.'),
    }
    ad_rows=[]
    if ads:
        if ads.get('status')=='PORTFOLIO_CALCULATED':
            for row in ads.get('rows') or []:
                for d in ((row.get('analysis') or {}).get('diagnosis') or []): ad_rows.append({'source_id':row.get('id'),'creative_id':row.get('creative_id'),'diagnosis':d})
        else:
            for d in ads.get('diagnosis') or []: ad_rows.append({'source_id':'AD_ANALYSIS','diagnosis':d})
    for row in ad_rows:
        d=row['diagnosis']; key=d.get('route'); edit,freeze,why=route_map.get(key,([key or 'REVIEW_REQUIRED'],['UNRELATED_LAYERS'],'Use the supplied diagnostic route; do not broaden the revision without evidence.'))
        routes.append({'source':'ADS','signal':d.get('symptom'),'source_id':row.get('source_id'),'creative_id':row.get('creative_id'),'edit_layers':edit,'freeze_layers':freeze,'next_check':d.get('next_check'),'why':why,'status':'LOCAL_REVISION_CANDIDATE_NOT_AUTO_APPLIED'})
    if feedback:
        for row in (feedback.get('revision_actions') or [])[:20]:
            routes.append({'source':'FEEDBACK','signal':row.get('category'),'source_id':None,'edit_layers':row.get('routes') or [],'freeze_layers':row.get('frozen_layers') or [],'next_check':'Verify the classified issue falls after the local change; escalate to product/quality only when evidence indicates a real product defect.','why':row.get('why'),'evidence_examples':row.get('evidence_examples') or [],'status':'LOCAL_REVISION_CANDIDATE_NOT_AUTO_APPLIED'})
    # Consolidate identical edit-layer families without discarding trace rows.
    summary={}
    for r in routes:
        key=' + '.join(r.get('edit_layers') or ['REVIEW_REQUIRED'])
        a=summary.setdefault(key,{'edit_layers':r.get('edit_layers') or [],'signals':[],'sources':set(),'freeze_layers':set()})
        a['signals'].append(r.get('signal')); a['sources'].add(r.get('source')); a['freeze_layers'].update(r.get('freeze_layers') or [])
    return {'status':'STRATEGY_REVISION_ROUTING_COMPILED' if routes else 'NO_REVISION_SIGNAL_SUPPLIED','routes':routes,'summary':[{'edit_layers':v['edit_layers'],'signals':v['signals'],'sources':sorted(v['sources']),'freeze_layers':sorted(v['freeze_layers'])} for v in summary.values()],'principle':'Performance evidence should revise the smallest causally plausible strategy layer. Unrelated Product Truth, positioning, visual style or offer layers stay frozen unless separate evidence implicates them.','auto_apply':False}


def build_performance_learning_depth(ads:dict[str,Any]|None, feedback:dict[str,Any]|None, experiment:dict[str,Any]|None):
    ad_block={'status':'NOT_SUPPLIED','decision':'上线后先建立资格/流量 → 点击 → PDP转化 → 经济性 → 增量性的Baseline。'}
    if ads:
        source=ads.get('aggregate') if ads.get('status')=='PORTFOLIO_CALCULATED' else ads; source=source or {}
        ad_block={'status':ads.get('status'),'metrics':source.get('metrics'),'economics':source.get('economics'),'diagnosis':source.get('diagnosis',[]),'diagnostic_tree':source.get('diagnostic_tree'),'budget_headroom':source.get('budget_headroom'),'budget_bid_hypotheses':source.get('budget_bid_hypotheses',[]),'incrementality':source.get('incrementality'),'scale_candidates':ads.get('scale_candidates',[]),'portfolio_learning_map':ads.get('portfolio_learning_map',[]),'row_count':len(ads.get('rows',[])) if ads.get('rows') is not None else 1,'strategy_action':'按因果顺序诊断：Eligibility/Traffic → Click Package → PDP/Traffic Quality → Economics → Incrementality。只有证据指向Click Package时才改Hero/Title/创意；经济有Headroom时也先做边际扩量验证。','why':'广告指标是症状，单位经济决定值不值得扩量，增量性决定是否真的创造了新增销售；三者必须合并解释。'}
    fb_block={'status':'NOT_SUPPLIED','decision':'上线后把评论、客服、退货按产品缺陷 vs 沟通误解持续分类，并做局部Revision Routing。'}
    if feedback:
        actions=[]
        for x in (feedback.get('revision_actions') or [])[:12]:
            y=dict(x); y['recommended_change']=x.get('recommended_change') or '只修改路由到的模块，并冻结无关定位/视觉/产品层。'; actions.append(y)
        dvc=dict(feedback.get('defect_vs_communication') or {})
        if dvc: dvc['why']='产品缺陷与沟通误解需要不同干预：沟通误解优先修Listing/Visual/Video/CX，真实产品缺陷必须回产品/质量层。'
        fb_block={'status':feedback.get('status'),'summary':feedback.get('summary'),'defect_vs_communication':dvc,'top_issues':(feedback.get('issues') or [])[:12],'revision_actions':actions,'category_by_source':feedback.get('category_by_source'),'category_by_severity':feedback.get('category_by_severity'),'strategy_action':'产品缺陷回产品/质量层；期望差、参数误解、包装/使用问题优先回Listing/Visual/CX/Video，并冻结无关模块。','why':'错误归因会导致不必要的产品重做，或反过来用文案/视觉掩盖真实缺陷。'}
    exp_block=experiment or {'status':'NOT_SUPPLIED','decision':'先建立Baseline，再设计单变量或最小变量实验。'}
    revision_routing=build_strategy_revision_routing(ads,feedback)
    return {'ads':ad_block,'feedback':fb_block,'experiment':exp_block,'strategy_revision_routing':revision_routing,'measurement_architecture':[
        {'layer':'ELIGIBILITY / QUALIFIED_TRAFFIC','signals':['impressions','indexing/eligibility','inventory','budget pacing'],'decision':'先判断是否有资格和足够流量。'},
        {'layer':'CLICK PACKAGE','signals':['CTR','thumbnail/title/hero response'],'decision':'判断第一视觉与第一主张是否赢得合格点击。'},
        {'layer':'PDP / CONTENT','signals':['CVR','progression','FAQ/questions','message match'],'decision':'判断相关性、证据、价格、信任、异议与流量质量。'},
        {'layer':'ECONOMICS','signals':['CPA','ROAS','contribution','refund allowance','marginal CPA'],'decision':'判断增长是否真实赚钱，而不是只看GMV/平台归因。'},
        {'layer':'INCREMENTALITY','signals':['holdout','baseline delta','organic displacement','new customers'],'decision':'判断广告/促销是否创造新增销售，而非只抢自然成交。'},
        {'layer':'POST-PURCHASE','signals':['returns','reviews','CS themes','repeat'],'decision':'判断产品缺陷、预期管理、使用教育与留存问题。'},
    ],'why':'评估层不是“看数据”，而是把每个指标映射回它真正能诊断的商业层，再做局部修正并冻结无关层。'}

def build_risk_priority_depth(info:dict[str,Any], request:dict[str,Any], compliance:dict[str,Any], research_gate:dict[str,Any], positioning:dict[str,Any], assets:list[dict[str,Any]], experiment:dict[str,Any]|None, market_depth:dict[str,Any]|None=None):
    risks=[]
    if compliance.get('status')=='HOLD': risks.append({'risk':'合规/Claim存在未解决阻断','severity':'P0','action':'定位具体Claim/平台规则并只修改受影响内容。','why':'不能把证据不足通过视觉包装成确定事实。'})
    if info.get('required_missing'):
        risks.append({'risk':'关键输入仍有缺口','severity':'P1','action':'按domain_matrix逐项补齐真正影响决策的信息。','why':'缺口不阻断全部策略，但会降低对应结论的确定性。'})
    pending=[x for x in research_gate.get('actions',[]) if x.get('status')!='RESOLVED']
    if pending: risks.append({'risk':'当前平台/法规/市场事实待核验','severity':'P1','action':'在影响提交、预算或Claim之前完成定向研究。','why':'把时效事实与长期策略分离，可避免过期规则污染整体策划。'})
    if not request.get('market_rows') and not request.get('market_file') and not request.get('research_source_adapters'): risks.append({'risk':'没有销量/GMV型市场结构样本','severity':'P1','action':'现有关键词/Review/竞品Listing可继续支撑对应洞察；在锁定市场容量、集中度、价带和结构型SKU机会前补同平台同市场销量/销售额样本。','why':'补充型研究能回答搜索/用户/竞品表达问题，但不能替代市场容量、集中度和成交价带数据。'})
    rq=(market_depth or {}).get('research_quality') or {}
    if rq.get('unresolved_source_ids'): risks.append({'risk':'市场研究存在未解析Source ID','severity':'P1','action':'补齐这些source record或从高强度结论中移除对应观察：'+', '.join(rq.get('unresolved_source_ids')[:8]),'why':'无法定位来源时，无法核验时间、范围和采集方法。'})
    if rq.get('stale_by_declared_threshold'): risks.append({'risk':'部分市场研究超出项目声明的freshness window','severity':'P1','action':'只刷新受影响source/dataset，不重做无关Product Truth与已稳定策略：'+', '.join(rq.get('stale_by_declared_threshold')[:8]),'why':'“过期”来自项目明确声明的时间窗口，不是Runtime任意设定；需要降低这些观察对当前决策的权重。'})
    if rq.get('scope_mismatch_source_ids'): risks.append({'risk':'研究来源与目标Market/Site/Platform/Category存在Scope mismatch','severity':'P1','action':'拆分或替换跨scope数据后再用于本地结论：'+', '.join(rq.get('scope_mismatch_source_ids')[:8]),'why':'跨站点/跨市场/跨平台机制差异可能被误判成消费者偏好。'})
    if not request.get('offer_economics'): risks.append({'risk':'没有完整单位经济数据','severity':'P1','action':'在锁定售价、优惠、联盟佣金和广告预算前补完整成本瀑布。','why':'销售额和ROAS不等于利润；Offer空间必须由Contribution约束。'})
    if any(a.get('product_fidelity')=='LOCKED_PIXEL' for a in assets): risks.append({'risk':'LOCKED_PIXEL产品身份在多Provider/AI制作中被改写','severity':'P0','action':'真实产品层保持锁定；AI只生成允许的环境/人物/背景/阴影/排版区域，并通过package hash与产品QA回查。','why':'产品包装、Logo、标签、结构或颜色变化会直接造成商品真实性问题。'})
    ed=(experiment or {}).get('design_review') or {}
    if ed.get('design_risks'):
        risks.append({'risk':'实验设计存在会削弱因果解释的风险','severity':'P1','action':'先修 assignment / pre-period balance / contamination / spillover / power-MDE，再用 outcome 做扩量决策：'+', '.join(ed.get('design_risks')[:8]),'why':'显著性或算术lift不能修复分流、污染、干扰或样本规划问题；错误因果结论会把预算和SKU/创意迭代导向错误层。'})
    adv=(experiment or {}).get('advanced_design_review') or {}
    if (adv.get('cluster') or {}).get('status')=='CLUSTER_DESIGN_REVIEW_COMPILED' and (adv.get('cluster') or {}).get('clusters_per_arm') in (None,''):
        risks.append({'risk':'Cluster experiment 未提供每臂独立cluster数量','severity':'P1','action':'补 clusters_per_arm 并使用cluster-aware inference/power；不要把individual z-test当cluster实验的最终推断。','why':'大量个体样本不能替代足够数量的独立cluster。'})
    if (adv.get('sequential') or {}).get('status')=='SEQUENTIAL_REVIEW_COMPILED' and not (adv.get('sequential') or {}).get('planned_looks'):
        risks.append({'risk':'Sequential monitoring缺少预先计划的look数量','severity':'P1','action':'在继续peek outcome前冻结planned looks / stopping rule。','why':'没有预先规则的反复查看会增加假阳性风险。'})
    cult=request.get('audience_culture') or {}
    if cult and not cult.get('statements') and not cult.get('source_ids'): risks.append({'risk':'文化适配缺少明确来源等级','severity':'P1','action':'把高影响文化判断标记为待研究；低风险执行保持中性、包容、可理解。','why':'文化策略应该减少沟通摩擦，而不是用未经证据支持的刻板偏好装饰页面。'})
    p0=[{'action':'冻结产品真源、已批准Claim和Primary Conversion Proposition后再进入大规模制作。','why':'没有共同Authority时，多平台/多资产会快速漂移。'}]
    if compliance.get('status')=='HOLD': p0.append({'action':'只修复导致HOLD的Claim/规则问题。','why':'合规问题应局部修复，不应自动触发无关视觉和定位重做。'})
    p1=[{'action':'完成Listing/平台内容矩阵与动态资产的逐项执行稿。','why':'把策略翻译成平台原生内容和生产合同，才能真正交给团队执行。'},
        {'action':'完成真实产品母资产、摄影/CMF和产品Fidelity所需输入。','why':'真实产品视觉是后续AI/合成/设计稳定性的基础。'}]
    for x in pending[:5]: p1.append({'action':x.get('query') or x.get('reason'),'why':x.get('reason') or '该事实影响对应提交/发布动作。'})
    p2=[{'action':'上线后按Asset/Surface建立Baseline，再做单变量或最小变量实验。','why':'先有真实基线，再判断创意、Listing、Offer或人群哪一层值得改。'},
        {'action':'把评论/客服/退货按产品缺陷 vs 沟通误解持续回流。','why':'沟通问题优先修内容，真实产品问题才回产品/质量层。'}]
    ab=[
        {'id':'AB-PROP-HIERARCHY','variable':'首屏信息层级','control':'当前Hero/主图','variant':f"只突出Primary Proposition：{positioning.get('primary_conversion_proposition')}",'hypothesis':'单一第一购买理由能否提高点击或首屏理解。','metric':'CTR / comprehension / PDP progression','why':'验证信息层级，不同时改价格、产品和整套视觉。'},
        {'id':'AB-PROOF-SEQUENCE','variable':'证据顺序','control':'核心主张→证据','variant':'核心主张→适配/异议→证据','hypothesis':'用户的主要阻力究竟是“不相关”还是“不相信”。','metric':'PDP progression / CVR','why':'测试Belief Sequence，而不是只测试颜色。'},
    ]
    if any(a.get('family') in {'CREATOR_AFFILIATE','VIDEO'} for a in assets): ab.append({'id':'AB-CREATOR-CONTEXT','variable':'人物/使用语境','control':'产品主导','variant':'真实目标市场日常语境','hypothesis':'人物语境是否在“适合我/如何用”问题上增加相关性。','metric':'hold / product click / CVR','why':'人物不是固定模板，应由购买问题决定。'})
    return {'risk_register':risks,'ab_test_hypotheses':ab,'priority_plan':{'P0':p0,'P1':p1,'P2':p2,'next_information_needed':info.get('required_missing',[]),'experiment_status':(experiment or {}).get('decision') or (experiment or {}).get('status'),'compliance_status':compliance.get('status')},'experiment':experiment}


def build_executive_summary_depth(info:dict[str,Any], market:dict[str,Any], sku:dict[str,Any], positioning:dict[str,Any], visual:dict[str,Any], portfolio:dict[str,Any], risk:dict[str,Any], target:dict[str,Any]):
    conclusions=[]
    conclusions.append({'priority':1,'conclusion':f"以“{positioning.get('primary_conversion_proposition')}”作为统一第一购买理由。",'why':'跨Listing、Hero、短视频和广告先统一价值核心，再按Surface调整表达形态，可减少多卖点互抢注意力。','execution':'所有P0资产先回答产品身份 + Primary Proposition；P1/P2再补适配、证据、信任和异议。','metric':'按Surface看CTR/首屏理解/CVR，而不是用一个指标解释所有内容。'})
    if market.get('status')=='MARKET_STRATEGY_INTERPRETED':
        conclusions.append({'priority':2,'conclusion':'市场数据用于决定进入方式、价带/配置研究优先级与差异化，不单独把“空白”当机会。','why':market.get('why'),'execution':'把CR3/CR10/HHI、价带、配置、竞品和评论/关键词联合解释。','metric':'后续以真实销售、CTR/CVR、利润和竞品表现验证。'})
    else:
        conclusions.append({'priority':2,'conclusion':'当前先做产品主导策略，不虚构市场白区。','why':market.get('why'),'execution':'继续完成定位/视觉/资产；在锁竞争打法、价带和市场型SKU角色前补市场数据。','metric':'补数后重算市场层，不重做无关产品真源与资产。'})
    conclusions.append({'priority':3,'conclusion':f"动态资产组合当前为 {portfolio.get('asset_count',0)} 项，数量来自购买问题而非固定图位。",'why':portfolio.get('why'),'execution':'每项资产必须有独立消费者问题、增量信息、成功指标与下一跳。','metric':'检查重复购买问题、Surface覆盖和资产级指标。'})
    if visual.get('style'):
        conclusions.append({'priority':4,'conclusion':f"视觉系统采用“{visual.get('style')}”。",'why':visual.get('style_why'),'execution':'将构图、CMF、摄影、人物/道具/场景全部绑定到购买问题与产品Fidelity。','metric':'产品识别、信息理解、点击/转化以及产品一致性QA。'})
    p0=(risk.get('priority_plan') or {}).get('P0',[])
    if p0:
        conclusions.append({'priority':5,'conclusion':'先锁定P0 Authority，再进入大规模生产。','why':'避免多平台、多资产在产品真源、Claim和核心主张上发生漂移。','execution':'；'.join(x.get('action','') for x in p0[:3]),'metric':'P0决策项有明确owner/依据/状态；无关模块不因局部问题返工。'})
    gaps=[x for x in info.get('domain_matrix',[]) if x.get('status')!='READY']
    return {
        'target':{'platform':target.get('platform_family'),'site':target.get('site'),'market':target.get('market'),'locale':target.get('primary_locale')},
        'strategic_conclusions':conclusions,
        'current_evidence_gaps':[{'domain':x.get('domain'),'impact':x.get('impact'),'next_action':x.get('next_action')} for x in gaps],
        'sku_roles':sku.get('sku_roles',[]),
        'asset_count':portfolio.get('asset_count',0),
        'first_actions':[(risk.get('priority_plan') or {}).get('P0',[]),(risk.get('priority_plan') or {}).get('P1',[])[:3]],
    }


def build_decision_index_depth(sections:dict[str,Any])->list[dict[str,Any]]:
    out=[]
    def add(domain,card,decision_id):
        if not isinstance(card,dict): return
        what=card.get('what') or card.get('conclusion') or card.get('message') or card.get('action')
        why=card.get('why')
        if not what or not why: return
        out.append({'decision_id':decision_id,'domain':domain,'what':what,'why':why,'evidence':card.get('evidence',[]),'consumer_logic':card.get('consumer_logic',''),'platform_logic':card.get('platform_logic',''),'culture_logic':card.get('culture_logic',''),'business_logic':card.get('business_logic',''),'execution':card.get('execution',''),'measurement':card.get('measurement') or card.get('metric','')})
    for i,d in enumerate(sections.get('01_information_completeness_assumptions_decisions',{}).get('decision_log',[]),1): add('INFORMATION',d,f'DEC-INFO-{i:02d}')
    market=sections.get('03_platform_region_audience_culture_insight',{}).get('market',{})
    for i,d in enumerate(market.get('strategic_insights',[]),1): add('MARKET',d,f'DEC-MKT-{i:02d}')
    pos=sections.get('04_marketing_core_strategy',{}).get('positioning',{})
    add('POSITIONING',pos.get('decision_card',{}),'DEC-POS-01')
    for i,row in enumerate(pos.get('message_hierarchy',[]),1): add('MESSAGE_HIERARCHY',{'what':row.get('message'),'why':row.get('why')},f'DEC-MSG-{i:02d}')
    visual=sections.get('05_visual_photography_strategy',{})
    if visual.get('style') and visual.get('style_why'): add('VISUAL',{'what':visual.get('style'),'why':visual.get('style_why'),'execution':'按摄影 / CMF / 资产镜头表执行。','measurement':'产品识别、理解、CTR/CVR和Fidelity QA。'},'DEC-VIS-01')
    portfolio=visual.get('asset_portfolio',{}).get('portfolio',[])
    for i,a in enumerate(portfolio,1): add('ASSET',{'what':a.get('asset_name') or a.get('asset_id'),'why':a.get('reason_to_exist'),'execution':a.get('strategic_job'),'measurement':a.get('success_metric')},f'DEC-AST-{i:02d}')
    perf=(sections.get('09_risk_measurement_priority_next_steps',{}) or {}).get('performance_learning') or {}
    for i,d in enumerate((perf.get('strategy_revision_routing') or {}).get('routes',[])[:20],1):
        add('REVISION_ROUTING',{'what':f"Revise {d.get('edit_layers')} from {d.get('source')}:{d.get('signal')}",'why':d.get('why'),'evidence':[d.get('source_id'),d.get('creative_id')],'execution':d.get('next_check'),'measurement':'Re-check the original symptom after the local revision while frozen layers remain unchanged.'},f'DEC-REV-{i:02d}')
    risk=sections.get('09_risk_measurement_priority_next_steps',{}).get('priority_plan',{})
    for level in ['P0','P1','P2']:
        for i,d in enumerate(risk.get(level,[]),1): add('PRIORITY',{'what':f'{level}: {d.get("action")}','why':d.get('why')},f'DEC-{level}-{i:02d}')
    return out


def build_master_strategy_depth(request:dict[str,Any], *, truth:dict[str,Any], research_gate:dict[str,Any], market:dict[str,Any]|None, economics:dict[str,Any]|None, culture:dict[str,Any], platform_compile:dict[str,Any], creative:dict[str,Any], photography_validation:dict[str,Any]|None, asset_architecture:dict[str,Any], compliance:dict[str,Any], experiment:dict[str,Any]|None=None, listing:dict[str,Any]|None=None, ads:dict[str,Any]|None=None, feedback:dict[str,Any]|None=None, authoring_context:dict[str,Any]|None=None):
    assets=asset_architecture.get('assets') or []
    category_profile=category_execution_profile(request); commerce_prior=category_commerce_profile(request)
    questions=request.get('shopper_questions') or [a.get('consumer_question') for a in assets if a.get('consumer_question')]
    info=build_information_depth(request,research_gate); value=build_value_depth(request,truth,questions); market_depth=build_market_depth(market,request)
    category_reconciliation=reconcile_category_commerce(request,market_depth,commerce_prior)
    commerce_profile={**commerce_prior,
        'objection_priorities':category_reconciliation.get('effective_objection_priorities') or commerce_prior.get('objection_priorities'),
        'proof_hierarchy':category_reconciliation.get('effective_proof_hierarchy') or commerce_prior.get('proof_hierarchy'),
        'message_architecture':{**(commerce_prior.get('message_architecture') or {}),'sequence':(category_reconciliation.get('message_architecture') or {}).get('effective_sequence') or (commerce_prior.get('message_architecture') or {}).get('sequence'),'category_prior_sequence':(category_reconciliation.get('message_architecture') or {}).get('category_prior_sequence'),'evidence_promoted_decision_intents':(category_reconciliation.get('message_architecture') or {}).get('evidence_promoted_decision_intents')},
        'evidence_reconciliation_status':category_reconciliation.get('status')}
    sku=build_sku_depth(request,market_depth,economics)
    econ_ready=bool(economics and economics.get('status') not in {None,'INSUFFICIENT_DATA','NOT_SUPPLIED','NO_ECONOMICS'})
    sku['category_offer_architecture']={**(commerce_profile.get('offer_architecture') or {}),'economics_validation_status':'ECONOMICS_AVAILABLE_FOR_VALIDATION' if econ_ready else 'ECONOMICS_NOT_SUPPLIED_DO_NOT_LOCK_OFFER'}
    sku['category_offer_evidence_validation']=validate_category_offer_with_evidence(commerce_profile,economics,request.get('offer_economics') or {})
    sku.setdefault('offer_decisions',[]).append(_why('让Offer结构服从品类购买任务，而不是所有品类都默认Coupon/Bundle。',commerce_profile.get('offer_architecture',{}).get('why',''),evidence=['category_commerce_profile','offer_economics' if economics else 'economics_not_supplied'],consumer='不同品类的核心风险不同：服装先解决尺码，食品先解决配料/份量，电子先解决兼容/性能，高客单先解决履约与服务。',platform='平台促销能力只能决定可执行形式，不能替代品类价值和风险顺序。',business='Offer只有在增加新买家任务、Trade-up、复购或降低真实摩擦时才有价值；否则只是利润让渡。',execution='先验证品类Offer假设与Product Truth/配置，再过Contribution、平台规则和增量实验。',measurement='Contribution/order、attach rate、switch、repeat、return/cancel themes、incremental contribution。'))
    positioning=build_positioning_depth(request,value,market_depth,sku,culture,questions,commerce_profile); listing_depth=build_listing_depth(request,listing,positioning,request.get('target') or {},commerce_profile)
    decision_listing=_decision_led_listing_plan(asset_architecture,category_reconciliation,positioning)
    listing_depth['category_pdp_sequence_reference']=listing_depth.get('pdp_sequence') or []
    listing_depth.update(decision_listing)
    listing_depth['pdp_sequence']=decision_listing.get('decision_led_pdp_sequence') or listing_depth.get('category_pdp_sequence_reference') or []
    targets=request.get('platform_content_targets') or [request.get('target') or {}]; culture_depth=build_culture_depth(targets,culture); visual=build_visual_depth(request,creative,culture,positioning,assets,photography_validation)
    content=build_content_matrix_depth(targets,culture,assets,positioning,commerce_profile)
    for row in content:
        row['platform_category_intersection']=platform_category_intersection(row.get('platform'),row.get('native_surface') or row.get('surface'),commerce_profile.get('category_family'),category_reconciliation)
    pack_binding={'pack_id':platform_compile.get('pack_id'),'applied_pack_ids':platform_compile.get('applied_pack_ids') or [],'pack_status':platform_compile.get('pack_status'),'compile_status':platform_compile.get('status'),'policy_boundary':'Exact submission constraints remain authoritative from the compiled platform pack/current platform policy; this binding records which pack informed planning.'}
    for row in content:
        row['platform_pack_binding']=pack_binding
        if isinstance(row.get('surface_production_contract'),dict): row['surface_production_contract']['platform_pack_binding']=pack_binding
    portfolio=build_asset_portfolio_depth(assets); race=build_race_depth(request.get('target') or {},positioning,market_depth,content,portfolio)
    risk=build_risk_priority_depth(info,request,compliance,research_gate,positioning,assets,experiment,market_depth); performance=build_performance_learning_depth(ads,feedback,experiment)
    performance['portfolio_behavior']=(economics or {}).get('portfolio_behavior_validation') or {'status':'BEHAVIOR_DATA_NOT_SUPPLIED'}
    performance['portfolio_interaction_validation']=(economics or {}).get('interaction_behavior_validation') or {}
    primary=positioning.get('primary_conversion_proposition'); evidence=[x.get('claim') for x in value.get('claim_value_ladder',[]) if x.get('publication_status')=='ACTIVE'][:4]
    frameworks={
        'STP':{'segmentation_basis':'优先按JTBD、触发、购买阻力、使用场景、价格/价值敏感度和生命周期分层；身份变量只在真实影响语境/代表性/语言时进入。','targeting':positioning.get('target_user'),'positioning':positioning.get('positioning_statement'),'why':'STP决定“为谁解决什么竞争问题”，避免把所有人当同一受众。'},
        'JTBD':{'shopper_questions':questions,'job':positioning.get('consumer_tension'),'desired_progress':primary,'barriers':positioning.get('objection_reducers',[]),'alternative':(positioning.get('value_proposition') or {}).get('competitive_alternative'),'why':'JTBD把产品属性转成用户真正想完成的进展，并决定内容应消除哪些切换阻力。'},
        '4P':{'product':'产品真源 + SKU 角色 + 价值主张','price':'Market evidence × contribution economics × price ladder/offer room','place':[(t.get('platform_family'),t.get('site'),t.get('market')) for t in targets],'promotion':'Primary proposition → relevance → proof → risk reduction → platform-native action','why':'4P用于校验产品/价格/渠道/传播是否互相支持，而不是四个独立文档。'},
        'Funnel':{'stages':['Discover/Reach','Identify','Relate','Believe','Reduce Risk','Act/Convert','Use/Retain'],'mapping':'由Belief Sequence与各Surface的Consumer Decision Question驱动。','why':'漏斗阶段只描述用户状态，资产数量仍由未解决问题与Surface需要决定。'},
        'AIDA':{'Attention':'产品身份 + 单一Primary Proposition','Interest':'目标需求/场景相关性','Desire':'已批准利益 + RTB/Proof','Action':'平台原生CTA/Offer（仅在经济/规则支持时）','why':'AIDA只用于单个内容块/脚本的信息节奏，不作为固定资产模板。'},
        'FABE':{'Feature':'产品真源中的事实 / 参数 / 配方 / 材质','Advantage':'事实如何形成真实差异或使用优势','Benefit':'与JTBD相关、且不超过Claim边界的可感知利益','Evidence':evidence,'why':'FABE防止从“有某成分/参数”直接跳到未经证据支持的功效结论。'},
        'Fogg':{'motivation':'Primary Proposition与真实JTBD产生足够购买动机','ability':'降低理解、选择、使用、支付、规格/兼容等行动摩擦','prompt':'仅在动机和能力已足够时使用平台原生CTA/促销提示','diagnostic_use':'CVR低时区分是价值动机不足、行动摩擦过高还是Prompt/时机问题。'},
        'Means_End':positioning.get('means_end_chain'),
        'Signaling':positioning.get('signaling_strategy'),
        'FIRST_Hero_Gate':{'gate':['Identify product','Understand primary value','Recognize fit/relevance','Know the next action'],'cognitive_rule':'首屏用最小信息成本完成这四个判断；证据和次级信息后置。','why':'FIRST是First-screen decision gate，不是固定视觉样式。'},
        'Cognitive_Budget':positioning.get('cognitive_budget'),
        'Belief_Sequence':positioning.get('belief_sequence'),
        'Commerce_Response_Ladder':positioning.get('commerce_response_ladder'),
    }
    sections={
        '01_information_completeness_assumptions_decisions':info,
        '02_product_truth_value_ladder':value,
        '03_platform_region_audience_culture_insight':{'market':market_depth,'culture':culture_depth,'market_evidence_fit_contract':request.get('_market_evidence_fit_contract') or {'status':'NOT_COMPILED'}},
        '04_marketing_core_strategy':{'category_decision_profile':category_profile,'category_commerce_profile':commerce_profile,'category_evidence_reconciliation':category_reconciliation,'product_strategy':sku,'positioning':positioning,'listing_strategy':listing_depth,'frameworks':frameworks},
        '05_visual_photography_strategy':{**visual,'asset_portfolio':portfolio},
        '06_platform_content_matrix':content,
        '07_race_execution_table':race,
        '08_culture_adaptation_checklist':culture_depth.get('adaptation_rows',[]),
        '09_risk_measurement_priority_next_steps':{'compliance':compliance,'research_pending':research_gate.get('actions',[]),'performance_learning':performance,**risk},
    }
    bindings=(authoring_context or {}).get('authority_bindings',{})
    for key,val in sections.items():
        if isinstance(val,dict) and bindings.get(key): val['reasoning_authorities']=bindings.get(key)
    executive=build_executive_summary_depth(info,market_depth,sku,positioning,visual,portfolio,risk,request.get('target') or {})
    decision_index=build_decision_index_depth(sections)
    return {'status':'STRATEGY_AUTHORITY_COMPILED','runtime_strategy_depth':'0.6.7-semantic-workspaces','positive_design_first':True,'governance_role':'BACKGROUND_GUARDRAIL','strategy_decision_contract':'WHAT → WHY → EVIDENCE → CONSUMER → PLATFORM → CULTURE → BUSINESS → EXECUTION → MEASUREMENT','asset_package_preservation':'REQUIRED','platform_compile_status':platform_compile.get('status'),'authoring_context':authoring_context or {},'reasoning_authority_bindings':bindings,'executive_summary':executive,'decision_index':decision_index,'sections':sections}

def _cn_human(v):
    if isinstance(v,dict): return {k:_cn_human(x) for k,x in v.items()}
    if isinstance(v,list): return [_cn_human(x) for x in v]
    if isinstance(v,str):
        try:
            from .delivery_html import _human_cn_internal
            return _human_cn_internal(v)
        except Exception:
            return v
    return v


def _fmt(v):
    v=_cn_human(v)
    if isinstance(v,(dict,list)): return json.dumps(v,ensure_ascii=False)
    return '' if v is None else str(v)


def _table(headers, rows):
    try:
        from .delivery_html import _zh_heading
        display_headers=[_zh_heading(h) for h in headers]
    except Exception:
        display_headers=headers
    out=['| '+' | '.join(display_headers)+' |','|'+'|'.join(['---']*len(headers))+'|']
    for row in rows:
        out.append('| '+' | '.join(_fmt(row.get(h,'')).replace('\n','<br>').replace('|','/ ') for h in headers)+' |')
    return '\n'.join(out)


def render_master_strategy_cn_depth(strategy:dict[str,Any]):
    s=strategy['sections']
    out=['# 跨境电商完整策略总案','', '> 主线是正向商业设计：产品真源 → 市场 / 用户 → SKU / Offer → 定位 / 价值主张 → 信息架构 → RACE / 4P / 漏斗 → 平台内容 → 创意 / 视觉 → 摄影 / CMF → 动态资产 → 生产 → 测量 / 学习。规则、证据与审核是后台护栏。','']
    ex=strategy.get('executive_summary') or {}
    out += ['## 决策摘要']
    for row in ex.get('strategic_conclusions',[]):
        out += [f"### {row.get('priority')}. {row.get('conclusion')}",f"- 为什么：{row.get('why')}",f"- 执行：{row.get('execution')}",f"- 衡量：{row.get('metric')}"]
    if ex.get('current_evidence_gaps'):
        out += ['','### 当前证据缺口（不等于全局阻断）',_table(['domain','impact','next_action'],ex.get('current_evidence_gaps',[]))]
    out += ['',f"- 当前动态资产数量：**{ex.get('asset_count',0)}**；数量由购买问题 / Surface Need / Incremental Information / Business Hypothesis 决定。",'']

    info=s['01_information_completeness_assumptions_decisions']
    out += ['## 1. 信息完整度、待确认清单、假设与决策日志',f"- 当前状态：**{info.get('completeness_status')}**",'### 信息完整度矩阵',_table(['domain','status','impact','next_action','strategy_can_continue'],info.get('domain_matrix',[]))]
    if info.get('pending_confirmations'): out += ['','### 待确认清单',_table(['item','why','blocks_scope','strategy_behavior'],info['pending_confirmations'])]
    if info.get('assumptions'): out += ['','### 假设登记',_table(['assumption','status','conversion_to_fact'],info['assumptions'])]
    out += ['','### 决策日志']
    for d in info.get('decision_log',[]):
        out += [f"- **WHAT**：{d.get('what')}",f"  - **WHY**：{d.get('why')}",f"  - **EVIDENCE**：{_fmt(d.get('evidence',[]))}",f"  - **CONSUMER LOGIC**：{d.get('consumer_logic','')}",f"  - **PLATFORM LOGIC**：{d.get('platform_logic','')}",f"  - **CULTURE LOGIC**：{d.get('culture_logic','')}",f"  - **BUSINESS LOGIC**：{d.get('business_logic','')}",f"  - **EXECUTION**：{d.get('execution','')}",f"  - **MEASUREMENT**：{d.get('measurement','')}"]

    val=s['02_product_truth_value_ladder']
    out += ['','## 2. 产品真实事实审计与卖点分级表','### 产品事实 → 商业角色',_table(['fact','value','fact_type','evidence_level','decision_role','real_selling_point','perceived_benefit','claim_boundary','why'],val.get('product_facts',[])),'','### 宣称 / 卖点价值分级',_table(['claim_id','claim','classification','real_selling_point','perceived_benefit','emotional_value','evidence_level','publication_status','claim_boundary','recommended_role','why'],val.get('claim_value_ladder',[])),f"\n**价值链原则：** {val.get('value_chain')}",f"\n**不可自动升级项：** {_fmt(val.get('unclaimable_without_more_evidence'))}"]
    if val.get('host_value_translation'):
        out += ['### 策略价值转译｜不改写产品真源，只深化商业含义',_table(['source_ref','fact_or_claim','advantage_or_rtb','perceived_benefit','emotional_or_end_value','boundary','why'],val.get('host_value_translation',[]))]

    third=s['03_platform_region_audience_culture_insight']; market=third['market']; cul=third['culture']
    out += ['','## 3. 平台 × 区域 × 人群 × 族裔文化洞察','### 3.1 真实市场 / 竞争 / 搜索解释层',f"- 状态：{market.get('status')}",f"- 为什么：{market.get('why')}"]
    if market.get('capacity'):
        out += [f"- 样本市场容量：{_fmt(market.get('capacity'))}",f"- 集中度：{_fmt(market.get('concentration'))}",f"- 数据质量/代表性：{_fmt(market.get('data_quality'))}",f"- 原始数据标准化：{_fmt(market.get('normalization'))}"]
    rq=market.get('research_quality') or {}
    ri=market.get('research_ingestion') or {}
    sar=market.get('source_adapter_refresh') or {}
    if ri.get('status')=='RESEARCH_INGESTION_COMPILED':
        out += ['#### Research Ingestion / Dedup / Version Lineage',f"- Dedup Mode：{ri.get('dedup_mode')}",_table(['dataset','input_rows','canonical_rows','exact_duplicates','dedup_mode','decision_boundary'],ri.get('datasets',[])),f"- Cross-source duplicate candidates：{_fmt(ri.get('cross_source_duplicate_candidates'))}",f"- Entity version/conflict review：{_fmt(ri.get('entity_version_or_conflict_review'))}",f"- Source version lineage：{_fmt(ri.get('source_version_lineage'))}",f"- Principles：{_fmt(ri.get('principles'))}"]
    if sar.get('status')=='SOURCE_ADAPTERS_COMPILED':
        out += ['#### Source Adapter / Incremental Refresh',_table(['adapter_id','dataset','refresh_mode','input_rows','analytical_rows','primary_key','updated_at_field','high_watermark','unresolved_primary_keys','change_set','semantic_near_duplicate_review','semantic_duplicate_policy'],sar.get('adapters',[])),f"- Principles：{_fmt(sar.get('principles'))}"]
    if rq.get('status')=='SOURCE_QUALITY_COMPILED':
        out += ['#### Research Source / Freshness / Representativeness Contract',f"- As of：{rq.get('as_of')}｜Scope：{_fmt(rq.get('research_scope'))}",_table(['dataset','row_count','rows_with_source_id','source_id_coverage_ratio','resolved_source_ratio','source_ids','decision_boundary'],rq.get('datasets',[])),_table(['source_id','kind','observed_at','age_days','max_age_days','freshness_status','representativeness_status','scope_mismatches','coverage_note'],rq.get('sources',[])),f"- Unresolved Source IDs：{_fmt(rq.get('unresolved_source_ids'))}",f"- Freshness Principle：{rq.get('freshness_principle')}",f"- Representativeness Principle：{rq.get('representativeness_principle')}"]
    if market.get('strategic_insights'):
        out += ['#### 市场决策卡']
        for d in market['strategic_insights']:
            out += [f"- **WHAT**：{d.get('what')}",f"  - 为什么：{d.get('why')}",f"  - EVIDENCE：{_fmt(d.get('evidence',[]))}",f"  - CONSUMER：{d.get('consumer_logic','')}",f"  - PLATFORM：{d.get('platform_logic','')}",f"  - BUSINESS：{d.get('business_logic','')}",f"  - 执行：{d.get('execution','')}",f"  - 衡量：{d.get('measurement','')}"]
    if market.get('top_competitors'): out += ['#### 竞品快照',_table(['competitor','items','units','revenue','median_price','revenue_per_item','rating','reviews','dominant_configuration'],market['top_competitors'])]
    if market.get('competitor_clusters'): out += ['#### 竞品结构集群（价位层 × 配置）',_table(['cluster','price_tier','configuration','items','sellers','units','revenue','median_price','share_of_revenue'],market['competitor_clusters'])]
    if market.get('top_price_bands'): out += ['#### 价格分布与已验证支付区间',_table(['band','price_low','price_high','items','units','revenue','revenue_per_item'],market['top_price_bands'])]
    if market.get('price_valley_signals'): out += ['#### 价格低密度区｜仅作为待验证假设',_table(['band','price_low','price_high','items','units','revenue','signal'],market['price_valley_signals'])]
    if market.get('configuration_signals'): out += ['#### 配置机会信号',_table(['configuration','items','units','revenue','median_price','units_per_item','revenue_per_item','review_signal'],market['configuration_signals'])]
    if market.get('price_configuration_matrix'): out += ['#### Price × Configuration Matrix',_table(['price_band','configuration','items','units','revenue','median_price','revenue_per_item'],market['price_configuration_matrix'])]
    if market.get('seller_efficiency'): out += ['#### Seller Efficiency｜用于选择深挖对象，不直接当因果结论',_table(['seller','items','units','revenue','units_per_item','revenue_per_item','median_price','reviews'],market['seller_efficiency'])]
    kd=market.get('keyword_demand') or {}
    if kd.get('top_terms'): out += ['#### 搜索需求 / 意图',_table(['term','intent','volume','avg_competition','avg_rank','priority_signal'],kd.get('top_terms',[]))]
    cv=market.get('customer_voice') or {}
    if cv.get('theme_summary'):
        out += ['#### Customer Voice｜市场/竞品评论主题（只聚合输入标签）',f"- 状态：{cv.get('status')}；未分类：{_fmt(cv.get('unclassified'))}",_table(['theme','records','weighted_mentions','dominant_sentiment','sentiment_mix','top_competitors','top_audiences','source_ids'],cv.get('theme_summary',[])[:20])]
        if cv.get('competitor_theme_matrix'): out += ['##### Competitor × Theme',_table(['competitor','theme','weighted_mentions'],cv.get('competitor_theme_matrix',[])[:30])]
        if cv.get('audience_theme_matrix'): out += ['##### Audience × Theme',_table(['audience','theme','weighted_mentions'],cv.get('audience_theme_matrix',[])[:30])]
        out += [f"- 解释边界：{cv.get('note')}"]
    ci=market.get('competitor_listing_intelligence') or {}
    if ci.get('competitors'):
        out += ['#### Competitor Listing × Review Intelligence｜只使用已提供观察字段',_table(['competitor','listing_count','observed_titles','observed_claims','message_themes','offer_types','proof_types','configurations','review_themes','exact_message_review_theme_overlap','source_ids'],ci.get('competitors',[])[:20])]
        if ci.get('message_review_overlap'): out += ['##### Message × Review Exact-label Overlap｜仅作为研究假设',_table(['competitor','theme','signal','decision_status','why'],ci.get('message_review_overlap',[])[:30])]
        out += [f"- 解释边界：{ci.get('note')}"]
    if market.get('opportunity_map'): out += ['#### 市场机会假设图（必须继续验证）',_table(['opportunity_id','type','signal','why','cross_checks_required','data_confidence','decision_status'],market['opportunity_map'])]
    out += ['','### 3.2 平台 × 区域 × 人群 × 族裔文化交叉表',_table(['platform','site','region','audience','language_locales','race_ethnicity','intersectionality','adaptation','stereotype_taboo_check','why'],cul.get('platform_audience_culture_rows',[])),'','### 3.3 交叉性拆解',f"- 族裔 / 文化语境：{_fmt(cul.get('race_ethnicity'))}",f"- 为什么：{cul.get('why')}"]
    if cul.get('intersectionality_table'): out += [_table(['dimension','evidence','commercial_relevance','execution','why'],cul['intersectionality_table'])]

    mfit=(third.get('market_evidence_fit_contract') or {})
    if mfit.get('status')=='MARKET_EVIDENCE_FIT_CONTRACT_COMPILED':
        out += ['#### 市场证据 → 产品真源适配合同',f"- Candidates：{len(mfit.get('candidates') or [])}｜Approved for asset routing：{len(mfit.get('approved_asset_jobs') or [])}",_table(['candidate_id','kind','label','fit_status','asset_routing_status','question'],mfit.get('candidates',[])[:30]),f"- Boundary：{mfit.get('boundary')}"]

    m=s['04_marketing_core_strategy']; pos=m['positioning']; sku=m['product_strategy']; listing=m['listing_strategy']; fw=m.get('frameworks') or {}; commerce=m.get('category_commerce_profile') or {}
    rec=m.get('category_evidence_reconciliation') or {}
    ep=rec.get('evidence_priority') or {}
    ranked=ep.get('ranked_intents') or []
    ranked_human='、'.join(str(x.get('intent')) for x in ranked[:5] if x.get('intent')) or '当前没有足够证据重排优先级'
    conflicts=rec.get('conflicts') or []
    offer_arch=sku.get('category_offer_architecture') or {}
    offer_val=sku.get('category_offer_evidence_validation') or {}
    offer_candidates=offer_val.get('candidates') or []
    offer_ready=sum(1 for x in offer_candidates if str(x.get('status') or '').upper() in {'READY','APPROVED','SUPPORTED'})
    econ=sku.get('economics_snapshot') or {}
    out += ['','## 4. 营销框架与核心策略','### 4.1 产品 / SKU / Offer 策略',
            f"- 品类商业画像：**{commerce.get('category_family') or '待确认'}**",
            f"- 证据与品类先验协调：{rec.get('status') or '待确认'}；当前证据优先关注：{ranked_human}。",
            f"- 协调边界：{rec.get('boundary') or ep.get('boundary') or '当前市场/竞品证据只能调整优先级，不能创造商品事实或功效。'}",
            f"- 冲突处理：{'发现 '+str(len(conflicts))+' 项品类先验与当前证据冲突，按证据质量加权后处理。' if conflicts else '当前没有结构化冲突需要升级处理。'}",
            f"- Offer 架构状态：{offer_arch.get('status') or '待确认'}；候选结构 {len(offer_arch.get('candidate_patterns') or offer_candidates)} 个，必须经过商品适配与单位经济验证后才能锁定。",
            f"- Offer 证据校验：{offer_val.get('status') or '待确认'}；已满足锁定条件 {offer_ready}/{len(offer_candidates)}。",
            _table(['sku','name','role','confidence','price','configuration','buyer_job','channel_job','why','next_decision'],sku.get('sku_roles',[])),f"- 角色逻辑：{sku.get('portfolio_logic')}"]
    if sku.get('role_decision_matrix'): out += ['#### SKU角色决策矩阵',_table(['sku','scenario_id','role','confidence','demand_signal','margin_signal','price_signal','configuration_signal','why'],sku.get('role_decision_matrix',[]))]
    out += [f"- 单位经济快照：币种 {econ.get('currency') or '待确认'}；若成本、费率、退货、履约、佣金或目标贡献未齐，不锁定价格/优惠结论。",f"- 共享增长预算：{'已提供结构化预算，详见单位经济/归档。' if sku.get('shared_growth_budget') else '未提供；不把广告、达人、样品或内容成本默认为零。'}"]
    if sku.get('price_ladder_strategy'): out += ['#### Price Ladder',_table(['sku','scenario_id','price','price_rank','gap','contribution','margin','role','why'],sku.get('price_ladder_strategy',[]))]
    if sku.get('economics_scenarios'): out += ['#### Economics Scenario Matrix',_table(['scenario_id','sku','price','discount_rate','affiliate_rate','ad_cost','contribution','contribution_margin','break_even_roas','allowable_cpa_target_contribution'],sku.get('economics_scenarios',[]))]
    pi=sku.get('portfolio_interactions') or {}
    if pi.get('pairs'): out += ['#### SKU Cannibalization / Overlap Hypotheses｜不是销量预测',_table(['sku_a','scenario_a','sku_b','scenario_b','overlap_signal_strength','evidence','unknown_inputs','price_gap_pct','role_a','role_b','decision_status','why'],pi.get('pairs',[]))]
    if sku.get('trade_up_architecture'): out += ['#### Trade-up Architecture',_table(['sku','scenario_id','price','position','role','upgrade_from','upgrade_reason_evidence','step_status','why'],sku.get('trade_up_architecture',[]))]
    if sku.get('lifecycle_offer_map'): out += ['#### Lifecycle / Offer Map',_table(['sku','scenario_id','role','lifecycle_stage','buyer_job','channel','offer_type','contribution','why'],sku.get('lifecycle_offer_map',[]))]
    pbv=sku.get('portfolio_behavior_validation') or {}
    if pbv.get('status')=='BEHAVIORAL_VALIDATION_COMPILED':
        out += ['#### Portfolio Behavioral / Cohort / Incrementality Validation',f"- Principle：{pbv.get('principle')}"]
        if pbv.get('sku_behavior'): out += ['##### SKU Behavior',_table(['sku','records','visitors','clicks','orders','new_customers','repeat_customers','observed_cvr','repeat_customer_share_of_reported_customers','contribution_per_order','source_ids','interpretation_boundary'],pbv.get('sku_behavior',[]))]
        if pbv.get('pair_behavior'): out += ['##### Pair Cross-shopping / Switching',_table(['sku_a','sku_b','period','shared_visitors','visitors_a','visitors_b','shared_on_a','shared_on_b','switch_a_to_b','switch_b_to_a','paired_orders','source_id','interpretation_boundary'],pbv.get('pair_behavior',[]))]
        sw=sku.get('switch_matrix') or {}
        if sw.get('status')=='SWITCH_MATRIX_COMPILED': out += ['##### Directional Switch Matrix',f"- Principle：{sw.get('principle')}",_table(['from_sku','to_sku','switch_count','eligible_from','switch_rate','period','source_id','rate_status'],sw.get('transitions',[]))]
        cc=sku.get('cohort_comparability') or {}
        if cc.get('status')=='COHORT_COMPARABILITY_COMPILED': out += ['##### Cohort Comparability Review',_table(['cohort','sku','comparability_metadata_supplied','comparability_status','why'],cc.get('cohorts',[]))]
        hm=sku.get('holdout_marginal_contribution') or {}
        if hm.get('status')=='HOLDOUT_MARGINAL_CONTRIBUTION_COMPILED': out += ['##### Holdout / Marginal Contribution',f"- Principle：{hm.get('principle')}",_table(['test_id','sku','segment','cohort','period','assignment_unit','randomized_declared','contamination_rate','treatment_n','control_n','incremental_orders','gross_incremental_contribution','intervention_cost','net_incremental_contribution','marginal_contribution_per_treatment_subject','design_readiness','interpretation_boundary'],hm.get('tests',[]))]
        if hm.get('segment_cohort_rollup'): out += ['###### Segment / Cohort Marginal Contribution Rollup',_table(['segment','cohort','tests','treatment_n','net_incremental_contribution','incremental_orders','marginal_contribution_per_treatment_subject','fully_observed','interpretation_boundary'],hm.get('segment_cohort_rollup',[]))]
        if pbv.get('cohorts'): out += ['##### Cohort',_table(['cohort','sku','lifecycle_stage','acquired_customers','repeat_customers','repeat_customer_rate','orders','revenue','contribution','contribution_per_acquired_customer','source_id','interpretation_boundary'],pbv.get('cohorts',[]))]
        if pbv.get('incrementality'): out += ['##### Incrementality Observations',_table(['test_id','sku','offer','treatment_n','control_n','treatment_conversion_rate','control_conversion_rate','absolute_conversion_lift','relative_conversion_lift','contribution_per_subject_lift','randomized_declared','causal_readiness','source_id','interpretation_boundary'],pbv.get('incrementality',[]))]
    ibv=sku.get('interaction_behavior_validation') or {}
    if ibv.get('pairs'): out += ['##### Hypothesis → Behavior Validation',_table(['sku_a','sku_b','hypothesis_strength','validation_status','observed_behavior','why'],ibv.get('pairs',[]))]
    out += ['#### Offer / 利润决策']
    for d in sku.get('offer_decisions',[]):
        out += [f"- **WHAT**：{d.get('what')}",f"  - 为什么：{d.get('why')}",f"  - BUSINESS：{d.get('business_logic','')}",f"  - 执行：{d.get('execution')}",f"  - 衡量：{d.get('measurement')}"]
    if sku.get('market_opportunity_links'): out += ['#### SKU / Offer 与市场机会的待验证连接',_table(['opportunity','signal','why','required_cross_checks','confidence','status'],sku.get('market_opportunity_links',[]))]

    vp=pos.get('value_proposition') or {}
    out += ['','### 4.2 定位 / 价值主张 / 信息架构',f"- 目标用户：{pos.get('target_user')}",f"- 品类 / 参照框架：{pos.get('frame_of_reference')}",f"- Consumer Tension：{pos.get('consumer_tension')}",f"- Positioning：**{pos.get('positioning_statement')}**",f"- 第一转化主张：**{pos.get('primary_conversion_proposition')}**",f"- Differentiation Source：{pos.get('differentiation_source')}",'#### 价值主张',_table(['target_customer','job_or_tension','frame_of_reference','value_promise','reasons_to_believe','secondary_gains','competitive_alternative','risk_reducers','proof_boundary'],[vp]),'#### 品类信息架构',f"- Sequence：{_fmt((pos.get('category_message_architecture') or {}).get('sequence'))}",f"- 为什么：{(pos.get('category_message_architecture') or {}).get('why')}",'#### 品类证据层级',_table(['rank','proof_type','status','why'],pos.get('category_proof_hierarchy',[])),'#### 品类异议优先级',_table(['rank','objection_key','question','decision_intent','recommended_field','status','activation_basis','why'],pos.get('category_objection_priorities',[])),'#### 通用信息层级参考',_table(['priority','role','message','consumer_state','why'],pos.get('message_hierarchy',[])),'#### 信念推进序列',_table(['step','state','question','message_job','exit_condition'],pos.get('belief_sequence',[])),f"- 手段—目的链：{_fmt(pos.get('means_end_chain'))}",f"- Signaling：{_fmt(pos.get('signaling_strategy'))}",f"- Cognitive Budget：{_fmt(pos.get('cognitive_budget'))}",f"- 商业响应阶梯：{_fmt(pos.get('commerce_response_ladder'))}"]
    if pos.get('host_strategy_rationale'):
        out += ['#### Host Strategic Rationale｜WHAT → WHY → EVIDENCE → EXECUTION',f"- {_fmt(pos.get('host_strategy_rationale'))}"]

    out += ['','### 4.3 上架文案 / 搜索完整策划',f"- 状态：{listing.get('status')}",f"- 为什么：{listing.get('why')}"]
    if (listing.get('search_intent_architecture') or {}).get('priority_terms'): out += ['#### 搜索意图架构',_table(['term','cluster','priority_score','field_role','decision_stage','why'],(listing.get('search_intent_architecture') or {}).get('priority_terms',[])),f"- 搜索意图摘要：{_fmt((listing.get('search_intent_architecture') or {}).get('intent_summary'))}"]
    out += [f"- Title任务：{_fmt(listing.get('title_job'))}",f"- Hero任务：{_fmt(listing.get('hero_job'))}"]
    if listing.get('field_decision_map'): out += ['#### Listing字段任务图',_table(['field','decision_job','value_supplied','incremental_information_rule','platform_constraint','why'],listing.get('field_decision_map',[]))]
    dqc=listing.get('decision_question_coverage') or {}
    if dqc.get('rows'): out += ['#### Consumer Decision Question Coverage｜问题不能静默丢失',f"- Summary：{_fmt(dqc.get('summary'))}",_table(['source_question','atomic_question','decision_intent','decision_topic','coverage_status','asset_id','surface','merge_basis'],dqc.get('rows',[]))]
    if listing.get('decision_specific_listing_jobs'): out += ['#### Decision-specific Listing Jobs',_table(['asset_id','consumer_question','decision_intent','decision_topic','recommended_listing_field','surface','incremental_information','proof_type'],listing.get('decision_specific_listing_jobs',[]))]
    fcp=listing.get('field_content_plan') or {}
    out += ['#### 字段内容 / 策略',f"- Attributes：{_fmt(fcp.get('attributes'))}｜Strategy：{_fmt(listing.get('attributes_strategy'))}",f"- Highlights/Bullets：{_fmt(fcp.get('highlights'))}｜Strategy：{_fmt(listing.get('highlights_bullets_strategy'))}",f"- Description：{_fmt(fcp.get('description'))}｜Strategy：{_fmt(listing.get('description_strategy'))}"]
    if listing.get('category_objection_checks'): out += ['#### Category Objection / Risk Map',_table(['rank','objection_key','question','decision_intent','recommended_field','evidence_needed','status','activation_basis','why'],listing.get('category_objection_checks',[]))]
    if listing.get('category_proof_hierarchy'): out += ['#### Listing Proof Priority',_table(['rank','proof_type','status','why'],listing.get('category_proof_hierarchy',[]))]
    if listing.get('objection_resolution_plan'): out += ['#### Objection Handling',_table(['objection_id','objection','objection_key','question','category','decision_intent','recommended_field','status','evidence_refs','evidence_needed','answer_contract','why'],listing.get('objection_resolution_plan',[]))]
    out += [f"- FAQ：{_fmt(fcp.get('faq'))}｜Strategy：{_fmt(listing.get('faq_strategy'))}",f"- Usage：{_fmt(fcp.get('usage'))}｜Strategy：{_fmt(listing.get('usage_strategy'))}",f"- Package：{_fmt(fcp.get('package'))}｜Strategy：{_fmt(listing.get('package_strategy'))}"]
    if listing.get('pdp_sequence'): out += ['#### PDP信息顺序',_table(['order','job','question','content'],listing.get('pdp_sequence',[]))]
    out += [f"- SEO/GEO：{_fmt(listing.get('seo_geo_strategy'))}",f"- Localization / Transcreation：{_fmt(listing.get('localization_transcreation'))}"]
    tcm=listing.get('transcreation_task_matrix') or {}
    if tcm.get('tasks'): out += ['#### 语言 × 字段本土化改写任务',_table(['locale','field','status','source_value','target_value','semantic_invariants','native_adaptation','search_intent_input','why'],tcm.get('tasks',[]))]
    lca=listing.get('localized_copy_audit') or {}
    if lca.get('issues'): out += ['#### 本土化文案审计',_table(['locale','field','issue','missing_source_numbers','extra_target_numbers','why'],lca.get('issues',[]))]
    fcw=listing.get('final_copy_workflow') or {}
    if fcw.get('status')=='FINAL_COPY_WORKFLOW_COMPILED':
        out += ['#### 本地语言最终文案流程',f"- 平台原生表达画像：{_fmt(listing.get('platform_native_listing_profile'))}",f"- 发布规则：{fcw.get('release_rule')}",f"- 生成合同：{fcw.get('generation_contract')}",f"- 发布状态统计：{_fmt(fcw.get('release_counts'))}"]
        for pkg in fcw.get('packages',[]):
            out += [f"##### {pkg.get('locale')} — {pkg.get('status')}",_table(['field','current_version_id','authored_copy','review_version_id','release_status','hard_issues','review_dimensions','why'],pkg.get('fields',[]))]
        if fcw.get('iteration_plan'):
            out += ['##### Author → Review → Revise → Re-review Loop',f"- Loop：{fcw['iteration_plan'].get('loop')}",f"- Authoring Tasks：{_fmt(fcw['iteration_plan'].get('authoring_tasks'))}",f"- Revision Tasks：{_fmt(fcw['iteration_plan'].get('revision_tasks'))}",f"- Review Tasks：{_fmt(fcw['iteration_plan'].get('review_tasks'))}"]
    out += [f"- Claim / Source Trace：{_fmt(listing.get('claim_source_trace'))}",f"- Keyword覆盖：{_fmt(listing.get('keyword_coverage'))}",f"- 重复信息审计：{_fmt(listing.get('repetition_audit'))}"]

    out += ['','### 4.4 营销框架如何参与决策（不是模板）']
    stp=fw.get('STP') or {}; jtbd=fw.get('JTBD') or {}; fourp=fw.get('4P') or {}; funnel=fw.get('Funnel') or {}
    out += [f"- **STP**：Segmentation={stp.get('segmentation_basis')}；Targeting={stp.get('targeting')}；Positioning={stp.get('positioning')}；WHY={stp.get('why')}",f"- **JTBD**：Job={jtbd.get('job')}；Desired Progress={jtbd.get('desired_progress')}；Barriers={_fmt(jtbd.get('barriers'))}；Alternative={jtbd.get('alternative')}；WHY={jtbd.get('why')}",_table(['P','strategy','why'],[
        {'P':'Product','strategy':fourp.get('product'),'why':'产品策略只放真实价值与SKU角色，不用营销语言覆盖产品事实。'},
        {'P':'Price','strategy':fourp.get('price'),'why':'价格既是消费者信号也是利润约束，需要市场与单位经济共同决定。'},
        {'P':'Place','strategy':fourp.get('place'),'why':'渠道决定Surface、信息密度、内容形态和购买路径。'},
        {'P':'Promotion','strategy':fourp.get('promotion'),'why':'传播顺序应沿购买信念推进，而不是重复同一卖点。'},
    ]),f"- **Funnel**：{_fmt(funnel)}",f"- **AIDA**：{_fmt(fw.get('AIDA'))}",f"- **FABE**：{_fmt(fw.get('FABE'))}",f"- **Fogg**：{_fmt(fw.get('Fogg'))}",f"- **Means–End**：{_fmt(fw.get('Means_End'))}",f"- **Signaling**：{_fmt(fw.get('Signaling'))}",f"- **FIRST Hero Gate**：{_fmt(fw.get('FIRST_Hero_Gate'))}",f"- **Cognitive Budget**：{_fmt(fw.get('Cognitive_Budget'))}",f"- **Belief Sequence**：{_fmt(fw.get('Belief_Sequence'))}",f"- **Commerce Response Ladder**：{_fmt(fw.get('Commerce_Response_Ladder'))}"]

    vis=s['05_visual_photography_strategy']; port=vis.get('asset_portfolio') or {}
    out += ['','## 5. 视觉总策略与拍摄执行清单',f"- Visual Territory：**{vis.get('visual_territory')}**",f"- 品类执行画像：{_fmt(vis.get('category_execution_profile'))}",f"- 视觉风格：**{vis.get('style')}**",f"- 为什么：{vis.get('style_why')}",f"- 配色 HEX：{_fmt(vis.get('palette_hex'))}",f"- CMF：{_fmt(vis.get('cmf'))}",f"- 材质 / 灯光画像：{_fmt(vis.get('material_lighting_profile'))}",f"- 构图：{_fmt(vis.get('composition'))}",f"- 摄影机：{_fmt(vis.get('camera'))}",f"- 镜头：{_fmt(vis.get('lens'))}",f"- 对焦 / 景深：{_fmt(vis.get('focus_dof'))}",f"- 灯光几何：{_fmt(vis.get('lighting_framework'))}",f"- 色彩管理：{_fmt(vis.get('color_management'))}",f"- 场景 / 道具：{_fmt(vis.get('scene'))} / {_fmt(vis.get('props'))}",f"- 模特 / 服装 / 发型 / 妆容：{_fmt(vis.get('casting'))} / {_fmt(vis.get('wardrobe_hair_makeup'))}",f"- 平台尺寸：{_fmt(vis.get('platform_dimensions'))}",'### 摄影参数 WHY',_table(['element','setting','why','consumer_logic','business_logic'],vis.get('photography_rationale',[])),'### 镜头表',_table(['asset_id','shot','commercial_job','consumer_question','visual_information_grammar','decision_evidence_plane','differentiation_axis','camera','composition','lighting','why'],vis.get('shot_list',[])),'### 资产视觉生产签名',_table(['asset_id','decision_intent','decision_topic','surface','production_mode','signature','editable_layer_contract'],vis.get('asset_visual_production_signatures',[])),'### 单资产摄影因果 WHY',_table(['asset_id','surface','consumer_question','strategic_job','decision_visibility_required','visual_production_signature','composition_choice','camera_choice','lighting_choice','cmf_choice','material_lighting_profile','shot_lighting_reasoning','causal_chain','parameter_why','business_logic','measurement'],vis.get('asset_parameter_reasoning',[])),'### 动态资产策展',f"- 资产数量：{port.get('asset_count')}（**无固定目标数**）",f"- 策展依据：{_fmt(port.get('curation_rules'))}",f"- 为什么：{port.get('why')}",_table(['sequence','asset_id','asset_name','decision_intent','merged_consumer_questions','surface','surface_need','priority','consumer_question','purchase_barrier','belief_target','strategic_job','reason_to_exist','incremental_information','business_hypothesis','success_metric','production_mode','product_fidelity','visual_production_signature','editable_layer_contract'],port.get('portfolio',[]))]
    if port.get('overlap_review'): out += ['#### 重复资产审查',_table(['asset_id','overlaps_with','reason','recommended_action'],port['overlap_review'])]
    if port.get('cross_surface_reuse_review'): out += ['#### 跨Surface复用审查',_table(['consumer_question','asset_ids','review_rule'],port['cross_surface_reuse_review'])]
    if port.get('semantic_intent_review'): out += ['#### Decision Intent 语义重复审查',_table(['decision_intent','assets','review_rule'],port['semantic_intent_review'])]

    out += ['','## 6. 分平台内容矩阵表',f"- Category Content Cadence：{_fmt(commerce.get('content_cadence'))}",_table(['platform','site','market','audience','surface','native_surface','asset_id','content_pillar','message_layer','primary_locale','visible_copy_locales','consumer_entry_state','consumer_exit_state','purchase_barrier','belief_target','topic','hook_type','hook','script_structure','category_message_sequence','category_proof_hierarchy','content_cadence','cadence_role','beat_plan','copy_contract','local_authoring_tasks','visual_form','platform_native_logic','native_authoring_system','surface_authoring_contract','surface_production_contract','platform_category_intersection','reuse_strategy','requires_platform_specific_production','cta','metric','race_stage','culture_adaptation','taboo_stereotype_check','business_hypothesis','why'],s['06_platform_content_matrix'])]
    out += ['','## 7. RACE传播框架执行表',_table(['stage','objective','key_actions','output','platform','culture_check','kpi','why'],s['07_race_execution_table'])]
    out += ['','## 8. 族裔文化适配检查表',_table(['adaptation_point','evidence_or_implication','inclusive_representation','stereotype_taboo_risk','result','modification','why'],s['08_culture_adaptation_checklist'])]

    last=s['09_risk_measurement_priority_next_steps']; pr=last.get('priority_plan') or {}; perf=last.get('performance_learning') or {}; ads=perf.get('ads') or {}; fb=perf.get('feedback') or {}
    out += ['','## 9. 合规 / 文化 / 风险 + A/B + P0/P1/P2 + 学习闭环','### 9.1 Ads / Economics / Incrementality']
    if (perf.get('portfolio_behavior') or {}).get('status')=='BEHAVIORAL_VALIDATION_COMPILED': out += [f"- Portfolio Behavior / Cohort / Incrementality：{_fmt(perf.get('portfolio_behavior'))}",f"- Portfolio Hypothesis Validation：{_fmt(perf.get('portfolio_interaction_validation'))}"]
    if ads.get('metrics'):
        out += [_table(['impressions','clicks','orders','spend','revenue','ctr','cvr','cpc','cpa','roas','acos'],[ads.get('metrics')]),f"- 单位经济阈值：{_fmt(ads.get('economics'))}",f"- 预算余量：{_fmt(ads.get('budget_headroom'))}",_table(['symptom','route','next_check'],ads.get('diagnosis',[])),f"- Diagnostic Tree：{_fmt(ads.get('diagnostic_tree'))}",f"- Budget / Bid Hypotheses：{_fmt(ads.get('budget_bid_hypotheses'))}",f"- Incrementality：{_fmt(ads.get('incrementality'))}",f"- Portfolio Learning Map：{_fmt(ads.get('portfolio_learning_map'))}",f"- Scale candidates：{_fmt(ads.get('scale_candidates'))}",f"- Strategy Action：{ads.get('strategy_action')}",f"- 为什么：{ads.get('why')}"]
    else: out += [f"- {ads.get('decision') or ads.get('strategy_action') or '暂无广告数据'}"]
    out += ['','### 9.2 Review / CS / Return → Local Revision']
    if fb.get('summary'):
        dvc=fb.get('defect_vs_communication') or {}
        out += [f"- 样本：{_fmt(fb.get('summary'))}",f"- Product defect vs Communication：{_fmt(dvc)}",_table(['category','count','share','severity_points','routes','examples'],fb.get('top_issues',[])),_table(['category','priority_score','routes','recommended_change','frozen_layers','why'],fb.get('revision_actions',[])),f"- Category × Source：{_fmt(fb.get('category_by_source'))}",f"- Category × Severity：{_fmt(fb.get('category_by_severity'))}",f"- Strategy Action：{fb.get('strategy_action')}",f"- 为什么：{fb.get('why')}"]
    else: out += [f"- {fb.get('decision') or fb.get('strategy_action') or '暂无反馈数据'}"]
    rr=perf.get('strategy_revision_routing') or {}
    if rr.get('status')=='STRATEGY_REVISION_ROUTING_COMPILED':
        out += ['','### 9.2.1 Strategy Revision Routing｜只改被证据指向的层',f"- Principle：{rr.get('principle')}",_table(['source','signal','source_id','creative_id','edit_layers','freeze_layers','next_check','why','status'],rr.get('routes',[]))]
    ledger=perf.get('learning_ledger') or []
    if ledger:
        out += ['','### 9.2.2 Post-production Learning Ledger｜改了什么、结果怎样、下一步只动哪一层',_table(['cycle_id','revision_id','edit_layers','freeze_layers','metric_comparison','causal_credit_allowed','recommendation','why','created_at'],ledger),'- 规则：before/after 变化默认只作描述性学习；只有显式有效的因果证据才允许把效果归因给本次修改。']
    expd=(perf.get('experiment') or {}).get('design_review') or {}
    out += ['','### 9.3 实验与指标→决策层映射',f"- Experiment：{_fmt(perf.get('experiment'))}"]
    if expd.get('status')=='EXPERIMENT_DESIGN_REVIEW_COMPILED': out += ['#### Experiment Design / Causal Readiness',f"- Design Readiness：{expd.get('design_readiness')}",f"- Power / MDE：{_fmt(expd.get('power_plan'))}",_table(['metric','treatment_mean','control_mean','standardized_difference','status','source_id'],expd.get('pre_period_balance',[])),f"- Contamination / Spillover / Interference：{_fmt({'contamination_rate':expd.get('contamination_rate'),'spillover_rate':expd.get('spillover_rate'),'interference_risk':expd.get('interference_risk'),'design_risks':expd.get('design_risks')})}"]
    out += [_table(['layer','signals','decision'],perf.get('measurement_architecture',[])),f"- 为什么：{perf.get('why')}",'','### 9.4 风险清单',_table(['risk','severity','action','why'],last.get('risk_register',[])),'','### 9.5 A/B测试建议',_table(['id','variable','control','variant','hypothesis','metric','why'],last.get('ab_test_hypotheses',[])),'','### P0']
    out += [f"- {x.get('action')} — WHY：{x.get('why')}" for x in pr.get('P0',[])]
    out += ['### P1']+[f"- {x.get('action')} — WHY：{x.get('why')}" for x in pr.get('P1',[])]
    out += ['### P2']+[f"- {x.get('action')} — WHY：{x.get('why')}" for x in pr.get('P2',[])]
    out += [f"### 下一步需补充信息\n{_fmt(pr.get('next_information_needed',[]))}"]

    bindings=strategy.get('reasoning_authority_bindings') or {}
    if bindings:
        out += ['','## 策略推理权威｜Runtime 实际消费的知识 / 本体 / Prompt 依据','这些权威用于指导生成与解释，不替代产品真源和项目输入。']
        for sec,b in bindings.items():
            out += [f"### {sec}",f"- {_fmt(b)}"]
    out += ['','## 资产包连续性','本总案是逐资产生产包的上游 Strategy Authority，不替代逐资产生产包。每个动态资产必须继续保留 `00_asset_manifest.yaml` 至 `11_strategy_authority_trace.json`；Provider Job → Provider Result → Review Item → Local Revision → Package Hash 链路继续保留。新增策略深度只做加法，不以压缩文件或删能力换取“简洁”。']
    return '\n'.join(out)+'\n'


# ---------------------------------------------------------------------------
# v0.6.1 Hard Delivery Contract overrides
# User-authoritative RACE = Research → Action → Communication → Evaluation.
# These overrides preserve the deep v0.6.0 strategy engine while hard-binding
# the required evidence, culture, platform execution and delivery fields.
# ---------------------------------------------------------------------------
from .delivery_contract import EVIDENCE_LEVELS, RACE_STAGES, normalize_evidence_grade, publication_rule, validate_strategy_delivery

_V061_ORIG_INFORMATION = build_information_depth
_V061_ORIG_VALUE = build_value_depth
_V061_ORIG_CONTENT = build_content_matrix_depth
_V061_ORIG_VISUAL = build_visual_depth
_V061_ORIG_CULTURE = build_culture_depth
_V061_ORIG_RISK = build_risk_priority_depth
_V061_ORIG_MASTER = build_master_strategy_depth
_V061_ORIG_RENDER = render_master_strategy_cn_depth


def _v061_contrast_ratio(a, b):
    def rgb(h):
        s=str(h or '').strip().lstrip('#')
        if len(s)!=6: return None
        try: return [int(s[i:i+2],16)/255 for i in (0,2,4)]
        except Exception: return None
    def lum(c):
        if c is None:return None
        vals=[]
        for x in c:
            vals.append(x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4)
        return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]
    la,lb=lum(rgb(a)),lum(rgb(b))
    if la is None or lb is None:return None
    hi,lo=max(la,lb),min(la,lb)
    return round((hi+.05)/(lo+.05),2)


def build_information_depth(request:dict[str,Any], research_gate:dict[str,Any]):
    base=_V061_ORIG_INFORMATION(request,research_gate)
    questions=[]
    for row in base.get('domain_matrix',[]):
        if row.get('status')!='READY':
            questions.append({'question':row.get('next_action'),'domain':row.get('domain'),'why':row.get('impact'),'status':'待确认'})
    for row in base.get('pending_confirmations',[]):
        questions.append({'question':row.get('item'),'domain':'Research / Rule','why':row.get('why'),'status':'待查证'})
    # Hard cap: no more than 10 questions. Strategy continues under explicit assumptions.
    base['clarifying_questions']=questions[:10]
    explicit=[]
    supplied=base.get('assumptions') or []
    explicit.extend(supplied)
    for row in base.get('domain_matrix',[]):
        if row.get('status')!='READY':
            explicit.append({'assumption':f"{row.get('domain')}未提供或未核实；当前继续完成不依赖该项的策略，涉及硬Claim/提交/预算锁定时标记待查证。",'status':'ASSUMPTION','why':'信息不足不能成为停止全部策略的理由，但不得把未知改写成事实。'})
    base['explicit_assumptions']=explicit[:20]
    base['execution_lock']='信息审计 → 待确认清单（最多10问） → 明确假设 → 在假设边界内继续输出；不得因普通缺口停止。'
    return base


def build_value_depth(request:dict[str,Any], truth:dict[str,Any], questions:list[str]):
    # Normalize claim evidence before strategy authoring even when this function is called outside the main compiler.
    from .claim_authority import compile_claim_authority
    req=dict(request)
    claim_authority=compile_claim_authority(request.get('claims') or [], request.get('sources') or [])
    req['claims']=claim_authority.get('claims') or []
    base=_V061_ORIG_VALUE(req,truth,questions)
    sources=request.get('sources') or []
    source_index={str(s.get('source_id')):s for s in sources if s.get('source_id')}

    # Fact provenance is field-specific. Never attach every project source to every product fact.
    product=request.get('product') or {}
    source_map={}
    for candidate in [request.get('product_source_refs'), product.get('_source_refs'), (truth or {}).get('product_source_refs'), (truth or {}).get('_source_refs')]:
        if isinstance(candidate,dict): source_map.update(candidate)
    for row in base.get('product_facts',[]):
        key=str(row.get('fact') or '')
        refs=source_map.get(key)
        if refs is None and '.' in key:
            # Allow a parent-level source map such as ingredients -> [SRC-1].
            refs=source_map.get(key.split('.',1)[0])
        if refs is None: refs=[]
        if not isinstance(refs,list): refs=[refs]
        refs=[str(x) for x in refs if str(x)]
        row['source_ids']=refs
        row['provenance_status']='SOURCE_LINKED' if refs else 'USER_SUPPLIED_UNMAPPED'
        row['source_mapping_rule']='Only sources explicitly mapped to this field are attached; project-wide sources are never sprayed across all facts.'
        # Product/formula/spec/supply-chain facts are B unless their linked source explicitly proves A.
        linked=[source_index.get(str(x),{}) for x in refs]
        st=' '.join(str(x.get(k,'')) for x in linked for k in ['source_type','evidence_type','type','title'])
        grade=normalize_evidence_grade(None,source_type=st)
        if not any(t in st.upper() for t in ['TEST','LAB','CERT','CERTIFICATION','OFFICIAL','MEASUREMENT','INSTRUMENT']): grade='B'
        row['evidence_grade']=grade; row['evidence_level']=grade; row['evidence_definition']=EVIDENCE_LEVELS[grade]
        row['publication_rule']=publication_rule(grade)
        row['classification']='真实卖点候选 / 产品事实'
    for row in base.get('claim_value_ladder',[]):
        explicit=str(row.get('evidence_level') or '').strip().upper()
        linked=[source_index.get(str(x),{}) for x in row.get('source_ids',[])]
        st=' '.join(str(x.get(k,'')) for x in linked for k in ['source_type','evidence_type','type','title'])
        grade=explicit if explicit in EVIDENCE_LEVELS else normalize_evidence_grade(None,source_type=st,subjective='体验' in str(row.get('classification','')))
        row['evidence_grade']=grade; row['evidence_level']=grade; row['evidence_definition']=EVIDENCE_LEVELS[grade]
        row['publication_rule']=publication_rule(grade)
        if grade=='C':
            row['publication_status']='SOFT_ONLY_NO_HARD_CLAIM'
            row['recommended_role']='SOFT_EXPERIENCE_OR_INTERNAL_HYPOTHESIS'
            row['claim_boundary']='C级只能作为主观体验、创意假设或待验证方向，不得作为硬宣称。'
        elif grade=='B':
            row['publication_status']='BOUNDED_SUPPORTED_CLAIM'
        else:
            row['publication_status']='HARD_CLAIM_ALLOWED_WITH_SCOPE'
    base['evidence_grade_authority']=EVIDENCE_LEVELS
    base['claim_authority_issues']=claim_authority.get('issues') or []
    base['grading_rule']='A=检测报告/官方认证/可复现实测；B=供应链或成分/机理支持；C=主观体验/待验证，C不得作硬宣称。'
    base['value_categories']=['真实卖点','可感知利益','情绪价值','不可宣称项']
    return base


def build_content_matrix_depth(targets:list[dict[str,Any]], culture:dict[str,Any], assets:list[dict[str,Any]], positioning:dict[str,Any], commerce_profile:dict[str,Any]|None=None):
    rows=_V061_ORIG_CONTENT(targets,culture,assets,positioning,commerce_profile)
    for row in rows:
        pc=row.get('surface_production_contract') or {}
        row['race_stage']='COMMUNICATION'
        row['platform_dimensions']=pc.get('dimensions') or pc.get('aspect_ratio') or '待查证：按当前Site×Surface官方规则锁定'
        row['duration']=pc.get('duration') or ('按脚本/Surface动态求解；待当前官方时长上限查证' if row.get('native_surface') in {'SHORT_VIDEO','VIDEO','LIVE'} else 'N/A')
        row['cover_first_frame']=pc.get('cover') or '首帧/封面必须先完成身份+相关性；若平台有精确封面规则则以当前官方规则为准。'
        row['subtitle_strategy']=pc.get('subtitle') or '视频/口播默认关键价值与Claim可通过字幕恢复；语言按Locale合同，本地母语审校。'
        row['music_rights']='仅使用已授权/平台商用音乐库/原创音频；版权状态不明标记待查证。'
        row['traffic_mechanism']='按当前平台Surface的发现/搜索/推荐/联盟/广告机制制定；算法细节未有当前证据时标记待查证。'
        row['landing_handoff']='CTA必须对应真实落地页/PDP/Shop/Live/表单路径，并保证信息与Offer连续。'
        row['utm_attribution']='可支持UTM/平台Campaign-AdGroup-Creative ID/Creator ID/landing ID的归因链；平台不支持UTM时保留等价追踪ID。'
        row['localization_checks']={'back_translation':'营销/关键Claim完成回译或母语审校','holiday_calendar':'相关活动前核对当地节日/宗教日历','payment_logistics':'涉及Offer/CTA时核对当地支付与物流承诺','religion_taboo':'按CultureContext与当前证据检查','local_regulation':'强监管/平台提交规则不确定时标记待查证'}
    return rows


def build_culture_depth(target:dict[str,Any]|list[dict[str,Any]], culture:dict[str,Any]):
    base=_V061_ORIG_CULTURE(target,culture)
    dims=['族裔/民族文化背景','性别','年龄','收入/价格敏感度','地域/城乡','语言/脚本','宗教/节日','肤色/发质','体型/残障','家庭结构/生活场景']
    existing={str(x.get('dimension')):x for x in base.get('intersectionality_table',[]) if isinstance(x,dict)}
    table=[]
    for d in dims:
        src=existing.get(d,{})
        table.append({'dimension':d,'evidence':src.get('evidence') or '待查证/仅在有来源且与任务相关时启用','commercial_relevance':src.get('commercial_relevance') or '仅用于语言、代表性、场景、可达性或真实购买摩擦；不得从身份直接推断消费行为。','execution':src.get('execution') or '若证据不足则保持中性、多样和可访问，不做标签化。','why':src.get('why') or '交叉性用于减少单一身份标签和AI生成偏见。'})
    base['intersectionality_table']=table
    targets=target if isinstance(target,list) else [target]
    checks=[
      ('族裔/文化背景','语言、宗教、节日、禁忌与身份呈现只在有证据时具体化','不同身份作为真实市场代表性，不绑定固定行为','单族裔标签化/异国情调化/刻板手势','待查证','按当前市场证据和母语/文化审校修改'),
      ('语言与回译','主语言/辅助语言/脚本/术语/Claim边界','本地自然表达','逐字翻译导致语义/法规偏差','待查证','关键文案母语审校+回译'),
      ('宗教/节日/禁忌','活动、服饰、饮食、身体暴露、图像符号','按真实节日/宗教语境使用','借节日符号但与产品/当地习俗无关','待查证','活动前查当地日历与文化规则'),
      ('肤色呈现','深/中/浅肤色曝光与综合色彩管理','不同肤色保留真实层次/纹理','AI自动美白、欠曝深肤色','必须校验','按深肤色曝光方案与肤色QA执行'),
      ('发质/发型','直/卷/波浪/保护性发型等按任务相关性呈现','发质与造型多样且自然','默认单一顺直发/不真实AI边缘','必须校验','Casting和Hair brief显式说明'),
      ('体型与年龄','在产品目标人群内提供现实差异','不以单一理想体型/过度年轻化代表所有用户','瘦身/抗老等暗示越界','必须校验','按品类和真实受众分层选角'),
      ('残障/可访问性','产品/场景相关时考虑行动、视觉、听觉可访问性','自然纳入而非励志化/工具化','象征性摆拍/忽视字幕和可读性','必须校验','字幕、对比度、操作演示与场景可达性检查'),
      ('家庭/关系结构','仅在产品使用场景相关时表达','多样家庭/独居/朋友关系可被真实呈现','默认单一家庭规范','待查证','用JTBD与场景证据决定'),
      ('服化道与配色','服装、妆发、色彩与产品/场景/当地语境一致','人物不是文化道具','符号化民族服装/肤色不友好的色彩分级','必须校验','在Art Direction与CMF中逐项审查'),
      ('CTA/促销语境','CTA、支付、物流、稀缺性话术与当地平台/法规一致','用户能理解下一步且承诺真实','虚假稀缺/不适当节日促销/物流承诺','待查证','按当前平台和当地规则锁定'),
    ]
    base['adaptation_rows']=[{'adaptation_point':a,'evidence_or_implication':b,'inclusive_representation':c,'stereotype_taboo_risk':d,'result':e,'modification':f,'why':'文化适配服务真实理解、代表性和购买摩擦，不从身份标签推导行为。'} for a,b,c,d,e,f in checks]
    base['localization_operating_checks']={'back_translation':'REQUIRED_FOR_KEY_COPY','holiday_calendar':'CHECK_WHEN_CAMPAIGN_RELEVANT','payment_logistics':'CHECK_WHEN_OFFER_OR_CTA_RELEVANT','religion_taboo':'CHECK_WITH_EVIDENCE','local_regulation':'P0_FOR_REGULATED_OR_SUBMISSION_SENSITIVE_CONTENT'}
    return base


def _v061_palette_roles(palette):
    vals=[]
    if isinstance(palette,dict): vals=[palette.get(k) for k in ['primary','secondary','background','text']]
    elif isinstance(palette,list): vals=palette[:4]
    elif palette: vals=[palette]
    vals=[x for x in vals if x]
    while len(vals)<4: vals.append('待设计锁定')
    primary,secondary,bg,text=vals[:4]
    ratio=_v061_contrast_ratio(text,bg)
    return {'primary':primary,'secondary':secondary,'background':bg,'text':text,'text_background_contrast_ratio':ratio if ratio is not None else '待在最终HEX锁定后计算','contrast_acceptance':'普通文字目标≥4.5:1；大字目标≥3:1；如品牌/平台/可访问性要求更严格则从严。'}



def _v065_merge(base:dict[str,Any]|None, override:dict[str,Any]|None)->dict[str,Any]:
    out=dict(base or {})
    for k,v in (override or {}).items():
        if isinstance(v,dict) and isinstance(out.get(k),dict): out[k]=_v065_merge(out[k],v)
        elif v not in (None,'',[],{}): out[k]=v
    return out

def build_visual_depth(request:dict[str,Any], creative:dict[str,Any], culture:dict[str,Any], positioning:dict[str,Any], assets:list[dict[str,Any]], photography_validation:dict[str,Any]|None):
    base=_V061_ORIG_VISUAL(request,creative,culture,positioning,assets,photography_validation)
    palette=base.get('palette_hex') or []
    base['color_roles']=_v061_palette_roles(palette)
    base['moodboard_direction']=(request.get('visual_strategy') or {}).get('moodboard_direction') or {'source_logic':'从商品PVI、Creative Opportunity Universe、已选方向、目标Surface和类目视觉空白构建；参考图只提取机制，不复制画面。','required_panels':['product truth/material','composition grammar','lighting/material response','human/context if relevant','typography/information design','negative/cliche avoidance']}
    photo_exec={
      'lighting_direction':'默认45°侧前/侧后主光按产品材质测试；透明/反光/金属按材质响应重建，不用一套灯法套所有品类。',
      'cct_white_balance':'商品/肤色混合摄影起始5000–5600K并以灰卡/产品色卡校准；氛围色温可变化但产品真色与肤色必须独立校验。',
      'key_fill_ratio':'人物/商品混合场景起始1.5:1–2:1；证据/质地图可提高塑形但不得丢失标签或深肤色层次。',
      'soft_hard':'人物皮肤优先大面积柔光+受控负补；材质证据根据Gloss/Matte/Metal/Glass决定软硬与反射卡。',
      'deep_skin_exposure':'深肤色不使用固定“提亮肤色”算法；以面部/肤色局部测光为基准，现场从中性参考做 +0.3 / +0.7 EV bracket（仅作测试起点），以高光保护、肤色层次和产品标签共同决定最终曝光。',
      'reflector_diffusion':'深肤色/高反差场景优先大柔光面；暗侧用白/中性反光板或柔和填充恢复层次，避免小型硬银板产生不自然热点；需要时用negative fill塑形。',
      'hair_texture':'卷发/保护性发型/深色发质用背/轮廓光与背景分离，避免发丝吞黑；不通过AI磨皮/重绘改变真实发质。',
      'body_age_disability':'Casting按真实目标和使用场景覆盖年龄/体型/可达性，不把残障或年龄作为戏剧化标签；动作必须真实可执行。',
      'ai_bias_controls':'禁止默认美白、瘦身、年轻化、发质同化、残障消除；人物生成/修图需检查肤色、手部/助具、发型边缘和身体比例。',
    }
    supplied=(request.get('photography_contract') or {}).get('execution') or {}
    photo_exec.update(supplied)
    base['photography_execution']=photo_exec

    # v0.6.5: a strategy recommendation must be executable. Unknown measured values remain
    # prelight-confirmed, but camera/light starting points are not left blank merely because the
    # user did not supply a studio contract.
    explicit_photo=request.get('photography_contract') or {}
    if not explicit_photo:
        family=str((base.get('category_execution_profile') or {}).get('category_family') or 'GENERAL_COMMERCE')
        master_camera={
          'status':'EXECUTION_RECOMMENDATION_REQUIRES_PRELIGHT_CONFIRMATION',
          'focal_length_mm':'85mm equivalent starting recommendation',
          'lens_family':'70–105mm equivalent perspective-controlled product lens family',
          'azimuth':'15–25° for 3Q identity/material views; 0° when front-label proof is the decision job',
          'elevation':'0–8° above product optical center unless the decision job needs top/contents evidence',
          'roll_deg':'0° unless an intentionally dynamic creator frame is selected',
          'working_distance':'Set distance to preserve geometry at the selected focal length; record after prelight',
          'camera_height':'Product optical center for pack/product proof; eye/hand relation height for human-use context',
          'focus_plane':'Decision-relevant label/material/action plane',
          'aperture_dof_intent':'f/8 starting recommendation for pack/proof; f/5.6–8 for contextual human/product relation; keep all decision evidence sharp',
          'shutter_speed':'1/125s starting recommendation for controlled studio capture; adjust for motion/strobe without changing exposure intent',
          'iso':'ISO 100 starting recommendation; raise only when motion/available-light constraints require it',
          'shot_size':'Tight product/medium-close proof by default; widen only when human, scale or environment is decision-relevant',
          'authority_boundary':'These are strategy starting settings, not claimed measured values. Prelight confirms final camera distance, exposure and exact framing.'
        }
        if family in {'APPAREL_FIT','FASHION_ACCESSORIES'}:
            master_camera.update({'focal_length_mm':'70mm equivalent starting recommendation','lens_family':'50–85mm equivalent for on-body/fit; 85–105mm for detail','camera_height':'Body/garment decision plane; keep verticals and body proportions natural','shot_size':'Full/3Q/medium according to fit question; include scale reference where needed'})
        elif family in {'FOOD_BEVERAGE'}:
            master_camera.update({'focal_length_mm':'85mm equivalent product starting recommendation','lens_family':'70–105mm product/food detail; macro only for real texture','shot_size':'Pack identity + preparation/use scale according to decision job'})
        elif family in {'HIGH_TICKET_DURABLE','HOME_LIVING'}:
            master_camera.update({'focal_length_mm':'50mm equivalent starting recommendation for spatial truth','lens_family':'35–70mm for site/scale; 70–105mm for detail without distortion','camera_height':'Human eye/installation plane appropriate to site-fit evidence','shot_size':'Wide/medium for scale and site fit; detail for controls/material only when needed'})
        elif family in {'ELECTRONICS'}:
            master_camera.update({'focal_length_mm':'70mm equivalent starting recommendation','lens_family':'50–85mm system/use; 85–105mm detail','shot_size':'Medium-close system relationship + tight interface/detail proof'})

        master_light={
          'status':'EXECUTION_RECOMMENDATION_REQUIRES_PRELIGHT_CONFIRMATION',
          'key':'Large diffused key 45° camera-left/front, approximately 30–45° above the decision plane; move angle to reveal real material curvature/texture',
          'fill':'Large neutral white bounce or soft fill from camera-right/front; tune after metering rather than flattening form',
          'negative_fill':'Black flag/negative fill opposite key when broad diffusion erases edge/form separation',
          'rim':'Subtle edge/rim only when product/hair/background separation needs it; never as a generic glow effect',
          'cct':'5200K starting recommendation with neutral card/product-color reference; final WB frozen after prelight',
          'softness':'Large soft source for skin/pack readability; introduce smaller/harder controlled accents only when real gloss/edge/material evidence needs it',
          'shadow':'Soft-edged but directional; retain enough shadow to describe form without losing label or deep-skin detail',
          'highlight_policy':'Keep critical print/skin/material highlights below clipping; preserve truthful gloss rather than retouching all specular response away',
          'exposure_ratio_plan':{'target_start':'1.5:1–2:1 for mixed product/human and label-readable commerce frames','proof_material_range':'up to ~2.5:1 when form/material proof benefits and critical detail remains readable','final':'meter and freeze after accepted prelight'},
          'authority_boundary':'Geometry/CCT/ratio are production recommendations. Exact light distance/power and final exposure are measured and locked during prelight.'
        }
        base['camera']=_v065_merge(master_camera, base.get('camera') if isinstance(base.get('camera'),dict) else {})
        # Strategy recommendation must override the old placeholder status while preserving useful legacy by_job logic.
        base['camera']['status']='EXECUTION_RECOMMENDATION_REQUIRES_PRELIGHT_CONFIRMATION'
        base['lens']=_v065_merge({'focal_length_by_job':(base.get('category_execution_profile') or {}).get('camera_plan')}, {k:v for k,v in master_camera.items() if k in {'focal_length_mm','lens_family','authority_boundary'}})
        base['focus_dof']={'status':'EXECUTION_RECOMMENDATION_REQUIRES_PRELIGHT_CONFIRMATION','focus_plane':master_camera['focus_plane'],'aperture_dof_intent':master_camera['aperture_dof_intent']}
        base['lighting_framework']=_v065_merge(master_light, base.get('lighting_framework') if isinstance(base.get('lighting_framework'),dict) else {})
        base['lighting_framework']['status']='EXECUTION_RECOMMENDATION_REQUIRES_PRELIGHT_CONFIRMATION'
        ml=base.get('material_lighting_profile') or {}
        if isinstance(ml,dict):
            diag=ml.get('lighting_diagram') if isinstance(ml.get('lighting_diagram'),dict) else {}
            diag=_v065_merge({'camera_axis':'0° reference','key':'45° camera-left/front, 30–45° elevation, large diffusion','fill':'camera-right/front neutral bounce/soft fill','negative_fill':'opposite key as needed for edge/form separation','rim':'conditional separation light only','background_light':'only when surface/background separation requires it','instruction':'Record actual positions/distances/power after accepted prelight.'},diag)
            # Replace null placeholder geometry with the executable strategy recommendation.
            for k,v in {'key':'45° camera-left/front, 30–45° elevation, large diffusion','fill':'camera-right/front neutral bounce/soft fill','negative_fill':'opposite key as needed','rim':'conditional separation only','background_light':'conditional only'}.items():
                if diag.get(k) in (None,''): diag[k]=v
            ml['lighting_diagram']=diag
            ratio=ml.get('exposure_ratio_plan') if isinstance(ml.get('exposure_ratio_plan'),dict) else {}
            if ratio.get('declared_ratio') in (None,''):
                ratio['strategy_start']='1.5:1–2:1'; ratio['status']='STRATEGY_START_MEASURE_AND_FREEZE_IN_PRELIGHT'
            ml['exposure_ratio_plan']=ratio
            color=ml.get('color_consistency_plan') if isinstance(ml.get('color_consistency_plan'),dict) else {}
            if color.get('white_balance') in (None,''): color['white_balance']='5200K starting recommendation; gray/product color reference decides final WB'
            ml['color_consistency_plan']=color
            base['material_lighting_profile']=ml

        for row in base.get('asset_parameter_reasoning') or []:
            intent=str(row.get('decision_intent') or '')
            sig=row.get('visual_production_signature') or {}
            cam=_v065_merge(master_camera, row.get('camera_choice') if isinstance(row.get('camera_choice'),dict) else {})
            if intent in {'USAGE','RELEVANCE','FIT_WEAR','SIZE_FIT'}:
                cam.update({'focal_length_mm':'65mm equivalent starting recommendation','lens_family':'50–85mm contextual product/human lens family','shot_size':'Medium/medium-close to preserve hand/body/product relation','camera_height':'At the interaction/decision plane; avoid wide-angle body/product distortion'})
            elif intent in {'MATERIAL_SENSORY','PROOF','INGREDIENT_COMPOSITION','PERFORMANCE_PROOF'}:
                cam.update({'focal_length_mm':'85–100mm equivalent starting recommendation','shot_size':'Tight proof/detail with enough context to understand what the evidence belongs to'})
            if 'front' in str(sig.get('camera_or_view') or '').lower(): cam['azimuth']='0–15° prioritizing label/identity readability'
            row['camera_choice']=cam
            light=_v065_merge(master_light, row.get('lighting_choice') if isinstance(row.get('lighting_choice'),dict) else {})
            if intent in {'MATERIAL_SENSORY','PROOF','INGREDIENT_COMPOSITION','PERFORMANCE_PROOF'}:
                light['softness']='Large soft key for readability plus controlled harder/strip accent only when needed to reveal truthful material edge/gloss/texture'
            row['lighting_choice']=light
            row['shot_size']=cam.get('shot_size')
            row['production_parameter_status']='EXECUTION_RECOMMENDATION_WITH_PRELIGHT_CONFIRMATION'
    return base


def build_race_depth(target:dict[str,Any], positioning:dict[str,Any], market:dict[str,Any], content_matrix:list[dict[str,Any]], asset_portfolio:dict[str,Any]):
    platform=target.get('platform_family')
    common='文化判断标注依据或假设；身份变量只影响真实语境/代表性/语言，不从身份推断行为。'
    return [
      {'stage':'RESEARCH','objective':'完成产品事实、市场/平台、人群、族裔文化、竞品、法规与证据研究。','key_actions':'Product Truth / Claim Evidence / Market & Competitor / Platform & Surface / Audience & Intersectionality / Culture / Regulation research','output':'研究底稿、事实审计、待确认项、假设与决策日志','platform':platform,'culture_check':common,'kpi':'source coverage / unresolved P0 / research freshness / evidence grade distribution','why':'先知道什么是真的、什么只是假设，才能避免把竞品话术、文化印象或成分机理直接变成硬宣称。'},
      {'stage':'ACTION','objective':'把研究转成定位、信息层级、内容矩阵、拍摄执行、预算与优先级。','key_actions':'STP + JTBD + Positioning + Message Hierarchy + 4P/Funnel + Asset Architecture + Photography/CMF + P0/P1/P2 tradeoff','output':'策略总案、视觉/拍摄清单、动态资产组合、预算/周期取舍','platform':platform,'culture_check':common,'kpi':'decision coverage / P0 closure / executable asset & production coverage','why':'研究只有转成明确取舍和可执行合同才有商业价值。'},
      {'stage':'COMMUNICATION','objective':'按平台原生方式传播，覆盖达人/UGC/广告/私域并完成语言本地化。','key_actions':'Listing/PDP + Creator/UGC + Paid + Live/Social/CRM + Native Localization + CTA/Landing/Tracking','output':'分平台内容矩阵、脚本/Prompt、Creator brief、Paid concepts、CTA与落地页交接','platform':platform,'culture_check':common,'kpi':'reach/CTR/engagement/CVR/creator efficiency by surface, with attribution IDs','why':'同一价值在不同平台、Surface、Locale和人群语境中需要原生表达，而不是机械搬运。'},
      {'stage':'EVALUATION','objective':'用指标、归因、A/B测试、评论/退货/客服和经济性回流到最小责任层。','key_actions':'Attribution + KPI review + A/B/experiment + Review/Return analysis + Unit economics + local revision + learning','output':'评估报告、归因链、实验结论、局部修订与学习记录','platform':platform,'culture_check':common,'kpi':'CTR/CVR/CPA/ROAS/contribution/return/review themes/experiment effect with causal boundary','why':'评估用于判断哪一层需要改，而不是因为一个结果波动就重做全部策略。'},
    ]


def build_risk_priority_depth(info:dict[str,Any], request:dict[str,Any], compliance:dict[str,Any], research_gate:dict[str,Any], positioning:dict[str,Any], assets:list[dict[str,Any]], experiment:dict[str,Any]|None, market_depth:dict[str,Any]|None=None):
    base=_V061_ORIG_RISK(info,request,compliance,research_gate,positioning,assets,experiment,market_depth)
    pr=base.get('priority_plan') or {'P0':[],'P1':[],'P2':[]}
    for k in ['P0','P1','P2']: pr.setdefault(k,[])
    if not pr['P0']: pr['P0'].append({'action':'锁定Product Truth / Claim Evidence / 强监管合规 / 产品身份与平台硬规则','why':'这些错误会造成错商品、违法/违规或不可逆生产返工。'})
    if not pr['P1']: pr['P1'].append({'action':'完成核心定位、平台原生内容、视觉差异化、Creator/Paid与关键本地化','why':'这些直接影响理解、点击、转化和内容效率。'})
    if not pr['P2']: pr['P2'].append({'action':'扩展次级创意变体、补充美术细节和非关键自动化','why':'这些提高成熟度，但不应挤占P0/P1资源。'})
    pr['budget_cycle_tradeoff']={'protect':['P0 产品真源 / 宣称 / 合规','P0 产品保真 / 包容性摄影','P1 核心价值主张 / 平台原生执行','P1 最小可用测量 / 归因设置'],'cut_first':['P2 装饰性变体','P2 低优先级额外展示位置','duplicate assets with low information gain','non-critical automation polish'],'rule':'预算/周期不足时先砍重复和装饰，不砍事实、合规、产品身份、关键文化/包容性和核心购买决策覆盖。'}
    base['priority_plan']=pr
    base['output_self_check']={
      'fabrication_check':'所有事实/数字/法规/平台规则/文化判断是否有来源或明确标“待查证/假设”；不得编造。',
      'why_check':'关键策略是否回答为什么是这个平台、区域、人群、文化语境以及为什么不是其他选择。',
      'culture_check':'是否完成交叉性、包容性表征、禁忌/刻板印象和AI偏见校验。',
      'compliance_check':'功效/成分/认证/价格/销量及强监管品类是否过P0证据与法规边界。',
      'metric_check':'每个关键动作是否有指标、归因或评估方法；无法归因时是否声明边界。',
      'assumption_check':'假设是否显式标注且与事实分离；待确认项是否≤10问并继续输出。',
    }
    base.setdefault('risk_register',[]).extend([
      {'risk':'强监管/功效/认证/医疗美妆食品金融类Claim证据不足','severity':'P0','action':'保持HOLD/软表达/待查证，不上线硬宣称','why':'Claim风险高于一般创意风险。'},
      {'risk':'平台算法/规则/音乐版权/当地法规信息不是当前证据','severity':'P0/P1','action':'标记待查证并在发布前获取当前官方规则','why':'动态规则不能由历史知识或猜测替代。'},
      {'risk':'族裔/文化标签化或AI人物偏见','severity':'P0','action':'交叉性+包容性摄影+文化检查表逐项校验','why':'错误代表性既伤害用户也会导致创意失真。'},
    ])
    return base


def build_master_strategy_depth(request:dict[str,Any], **kwargs):
    strategy=_V061_ORIG_MASTER(request,**kwargs)
    s=strategy.get('sections') or {}
    core=s.get('04_marketing_core_strategy') or {}
    fw=core.get('frameworks') or {}
    fw['RACE_Definition']={'authority':'Research → Action → Communication → Evaluation','relationship':'RACE是传播流程骨架；STP+JTBD定策略；AIDA/FABE定内容结构；4P/内容漏斗定转化；Fogg/Means-End/Signaling/FIRST/Cognitive Budget/Belief Sequence作为需要时的决策镜头。','anti_template':'不得只套框架名；每个框架必须改变一个明确决策或标记不适用。'}
    core['frameworks']=fw; s['04_marketing_core_strategy']=core
    last=s.get('09_risk_measurement_priority_next_steps') or {}
    last.setdefault('output_self_check',(_V061_ORIG_RISK({},request,kwargs.get('compliance') or {},kwargs.get('research_gate') or {},{},[],kwargs.get('experiment'),{}).get('output_self_check') if False else {}))
    # build_risk_priority_depth already adds self-check through global dispatch; keep fallback here.
    if not last.get('output_self_check'):
        last['output_self_check']={'fabrication_check':'未来源化事实不得输出为确定事实。','why_check':'关键策略需有WHY。','culture_check':'需完成交叉性/包容性校验。','compliance_check':'强监管与Claim P0。','metric_check':'关键动作需指标/归因。','assumption_check':'事实/假设分离。'}
    s['09_risk_measurement_priority_next_steps']=last
    strategy['sections']=s
    strategy['runtime_strategy_depth']='0.6.7-semantic-workspaces'
    strategy['race_authority']='Research → Action → Communication → Evaluation'
    strategy['evidence_grade_authority']=EVIDENCE_LEVELS
    strategy['delivery_contract']=validate_strategy_delivery(strategy)
    return strategy


def render_master_strategy_cn_depth(strategy:dict[str,Any]):
    md=_V061_ORIG_RENDER(strategy)
    s=strategy.get('sections') or {}; vis=s.get('05_visual_photography_strategy') or {}; rows=s.get('06_platform_content_matrix') or []; last=s.get('09_risk_measurement_priority_next_steps') or {}
    visual_extra='\n'.join([
      '### 5.x 执行锁补充｜色彩对比与包容性摄影',
      f"- 情绪板方向：{_fmt(vis.get('moodboard_direction'))}",
      f"- 主/辅/背景/文字色与对比度：{_fmt(vis.get('color_roles'))}",
      f"- 摄影执行参数：{_fmt(vis.get('photography_execution'))}",
      ''
    ])
    md=md.replace('\n## 6. 分平台内容矩阵表', '\n'+visual_extra+'\n## 6. 分平台内容矩阵表')
    exec_rows=[]
    for r in rows:
        exec_rows.append({k:r.get(k) for k in ['platform','site','asset_id','platform_dimensions','duration','cover_first_frame','subtitle_strategy','music_rights','traffic_mechanism','landing_handoff','utm_attribution','localization_checks']})
    platform_extra='\n### 6.x 平台执行 / 本地化 / 归因补充矩阵\n'+_table(['platform','site','asset_id','platform_dimensions','duration','cover_first_frame','subtitle_strategy','music_rights','traffic_mechanism','landing_handoff','utm_attribution','localization_checks'],exec_rows)+'\n'
    md=md.replace('\n## 7. RACE传播框架执行表', '\n'+platform_extra+'\n## 7. RACE传播框架执行表')
    sc=last.get('output_self_check') or {}
    selfcheck='\n### 9.x 输出前自检\n'+_table(['check','requirement'],[{'check':k,'requirement':v} for k,v in sc.items()])+'\n'
    needle='\n## 策略推理权威｜Runtime 实际消费的知识 / 本体 / Prompt 依据'
    md=md.replace(needle, '\n'+selfcheck+needle) if needle in md else md+selfcheck
    try:
        from .delivery_html import _human_cn_internal
        md='\n'.join(_human_cn_internal(line) for line in md.splitlines())+'\n'
    except Exception:
        pass
    return md
