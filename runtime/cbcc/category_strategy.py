from __future__ import annotations
from typing import Any
import re


def _text(*parts: Any) -> str:
    return ' '.join(str(x or '') for x in parts).casefold()


def infer_category_family(request:dict[str,Any]) -> str:
    product=request.get('product') or {}; target=request.get('target') or {}
    category_text=_text(target.get('category'),product.get('category'))
    t=_text(category_text,product.get('product_type'),product.get('format'),product.get('name'))
    # Explicit category labels outrank incidental words in product names (e.g. "food container" inside home/kitchen).
    if any(x in category_text for x in ['large_appliance','large appliance','high ticket durable','furniture']): return 'HIGH_TICKET_DURABLE'
    if any(x in category_text for x in ['food_beverage','food beverage','food','beverage']): return 'FOOD_BEVERAGE'
    if any(x in category_text for x in ['electronics','electronic']): return 'ELECTRONICS'
    if any(x in category_text for x in ['beauty','skincare','cosmetic','personal_care','personal care']): return 'BEAUTY_PERSONAL_CARE'
    if any(x in category_text for x in ['apparel','clothing','footwear']): return 'APPAREL_FIT'
    if any(x in category_text for x in ['fashion_access','fashion access']): return 'FASHION_ACCESSORY'
    if any(x in category_text for x in ['home_kitchen','home kitchen','home','kitchen']): return 'HOME_DURABLE'
    # Fallback to product type/name with specific families first to avoid substring collisions.
    if any(x in t for x in ['furniture','sofa','mattress','refrigerator','fridge','washing machine','washer','dryer','dishwasher','air conditioner','air purifier','robot vacuum','vacuum cleaner','large appliance','high ticket durable']): return 'HIGH_TICKET_DURABLE'
    if any(x in t for x in ['food','beverage','tea','coffee','snack','drink','supplement','nutrition','sauce','cereal']): return 'FOOD_BEVERAGE'
    if any(x in t for x in ['electronic','electronics','device','charger','headphone','speaker','keyboard','mouse','camera','power bank','smartwatch','earbud']): return 'ELECTRONICS'
    if any(x in t for x in ['beauty','skincare','skin care','cosmetic','serum','moistur','shampoo','conditioner','acne','sunscreen','cream','gel moistur']): return 'BEAUTY_PERSONAL_CARE'
    if any(x in t for x in ['apparel','clothing','shirt','t-shirt','tee','dress','jeans','trouser','pants','skirt','jacket','coat','sweater','hoodie','shoe','footwear','sneaker']): return 'APPAREL_FIT'
    if any(x in t for x in ['fashion','accessor','shoulder bag','crossbody','backpack','wallet']) or ' bag' in t or t.endswith('bag'): return 'FASHION_ACCESSORY'
    if any(x in t for x in ['home','kitchen','container','storage','cookware','appliance','bottle','mug','glassware','tool','durable']): return 'HOME_DURABLE'
    return 'GENERAL_COMMERCE'


def _decision_term_match(q:str, term:str) -> bool:
    """Avoid accidental substring matches (rain in constraints, size in oversized, prepare in prepared)."""
    term=str(term).casefold()
    if re.fullmatch(r'[a-z0-9]+',term):
        return re.search(r'(?<![a-z0-9])'+re.escape(term)+r'(?![a-z0-9])',q) is not None
    return term in q


def classify_decision_intent(question:str, category_family:str|None=None) -> str:
    q=_text(question)
    fam=str(category_family or '').upper()
    # Identity requires identity language about the product/model itself.  Generic "what is" later in a
    # sentence (for example "what is the boundary?") must not steal a more specific decision intent.
    if re.search(r'^\s*(what exactly is this|what is this|what is the product|which product|which model|is this the exact|is this exact)', q):
        return 'IDENTIFY'
    if any(_decision_term_match(q,x) for x in ['exact model','exact sku','model number','product identity']):
        return 'IDENTIFY'
    if re.search(r'\bhow much\b.*\bfit(?:s)?\b', q) or 'fits without' in q or 'cupholder' in q or re.search(r'\bsize\b.*\bfit\b', q):
        return 'SIZE_FIT' if fam=='APPAREL_FIT' else 'SIZE_CAPACITY'
    # "What makes X different?" is a comparison/differentiation question, not a generic catch-all.
    if any(x in q for x in ['what makes', 'how is this different', 'how does this compare', 'compare with', 'versus', ' vs ']):
        return 'DIFFERENTIATION'
    rules=[
        ('PACKAGE_CONTENTS',['what exactly is included','what is included','included','in the box','what do i get','收到什么','包含','package contents','内容物']),
        ('SIZE_FIT',['size chart','which size','what size should','sizing','true to size','body measurement','garment measurement','尺码','版型','选什么码']),
        ('SITE_FIT',['site fit','fit my wall','fit my room','wall space','installation space','site constraint','clearance','doorway','utility requirement','场地','安装空间','预留尺寸']),
        ('FIT_WEAR',['sit on the body','on the body','on a real body','sit on','wear','worn','strap','adjust','body scale','肩带','佩戴','合身','穿着']),
        # Beauty/personal-care composition questions should not be labelled as food/dietary decisions.
        ('INGREDIENT_COMPOSITION',['animal-derived','animal derived','cruelty','snail-derived','snail derived','formula composition','ingredient composition']) if fam=='BEAUTY_PERSONAL_CARE' else ('INGREDIENT_DIETARY',[]),
        ('INGREDIENT_DIETARY',['ingredient list','ingredients','allergen','dietary','nutrition','sugar','calorie','halal','vegan','配料','过敏原','营养','清真','素食']),
        # Hard fulfillment/service intents must outrank generic preparation words such as "prepare".
        ('DELIVERY_INSTALLATION',['delivery','installation','assembly','install','delivery window','送装','配送','安装','组装']),
        ('WARRANTY_SERVICE',['warranty','customer support','support service','repair service','repair','保修','售后','维修']),
        ('SENSORY_PREP',['taste','flavor','flavour','aroma','brew','steep','prepare','serving','口味','风味','香气','冲泡','食用']),
        ('COMPATIBILITY',['compatibility','compatible','work with','works with','supported device','will it charge','charge my','oven','freezer','microwave','dishwasher','兼容','适配']),
        ('PERFORMANCE_PROOF',['battery','runtime','speed','latency','noise','suction','performance','benchmark','power sharing','simultaneous','insulation','cold retention','temperature retention','keeps cold','续航','性能','速度','噪音','吸力']),
        ('PORTABILITY',['weight','how heavy','portable','portability','carry weight','travel weight','重量','便携']),
        ('TOTAL_COST_OWNERSHIP',['total cost','total ownership','energy use','energy','replacement','filter replacement','filter cost','running cost','ongoing cost','maintenance cost','subscription','总成本','耗材','电费','维护成本']),
        ('SIZE_CAPACITY',['how much fits','what fits','fit inside','holds','hold my','capacity','how large','how small','dimension','多少升','容量','尺寸','规格','scale']),
        ('SEAL_LEAK',['leak','airtight','seal','soup','soups','sauce','sauces','密封','漏','防漏']),
        ('STORAGE_STACKING',['stack','nest','storage','fridge','cabinet','organize','堆叠','收纳','冰箱']),
        ('WEATHER_BOUNDARY',['rain','water-repellent','water repellent','water resistant','weather','防泼水','防水','雨']),
        ('CARE_MAINTENANCE',['care','wash','clean','maintenance','洗','清洁','保养']),
        ('MATERIAL_SENSORY',['material','fabric','nylon','glass','plastic','metal','finish','texture','transparent','材质','面料','玻璃','塑料','透明','质地']),
        ('PROOF',['proof','verified','formula','evidence','study','clinical','claim','凭什么','证据','配方','成分','参数']),
        ('RELEVANCE',['relevant','for me','适合','人群','场景','routine relevance','daily essentials','everyday essentials']),
        ('USAGE',['how to use','how do i use','use it','routine','steps','daily routine','怎么','使用','步骤','meal prep','closure']),
        ('EXPECTATION_BOUNDARY',['expect','boundary','limit','not permanent','会不会','预期','边界']),
    ]
    for intent,terms in rules:
        if terms and any(_decision_term_match(q,x) for x in terms): return intent
    return 'DECISION_SUPPORT'


def decision_profile(intent:str, question:str) -> dict[str,Any]:
    base={
      'IDENTIFY':('产品身份/类别不清，用户无法判断是否值得继续看。','我能立即识别卖的是什么，以及第一购买理由。','IDENTIFY','产品身份和价值尚不清楚','准确识别产品 + 理解第一购买理由','COMMUNICATION','承担产品识别与第一价值建立；没有这一层，后续证据缺少清晰上下文。','产品身份 + Primary Proposition，不重复后续深层证据。','CTR / first-screen comprehension'),
      'RELEVANCE':('用户理解产品，但尚不确定是否与自己的真实需求/语境相关。','这个产品与我的真实需求或日常语境相关。','RELATE','知道是什么，但相关性不足','理解适用语境/人群/场景','COMMUNICATION','把产品价值翻译成用户自己的问题，建立“这和我有关”的相关性。','目标语境/使用场景/适配信息，不重复产品身份。','engagement / PDP progression / CVR'),
      'PROOF':('用户已感兴趣，但需要事实或证据才能相信主张。','核心主张有真实、可追溯的理由支撑。','BELIEVE','相关但尚未充分相信','获得可追溯事实/证据','COMMUNICATION','用事实/参数/配方/材质/证据把兴趣转化为信任。','仅增加可验证RTB/Proof，避免再次重复主卖点。','PDP progression / CVR / claim comprehension'),
      'USAGE':('用户不确定如何使用、如何融入日常或购买后是否麻烦。','我知道如何把产品放入自己的真实使用流程。','ACT_OR_USE','价值已理解，但使用方式/场景不清','理解使用方式和日常适配','COMMUNICATION','降低使用不确定性，并提前减少误解、退货和客服问题。','使用/场景/流程信息，不新增未经证据支持的效果结果。','CVR / usage comprehension / return-theme reduction'),
      'DIFFERENTIATION':('用户知道品类，但不知道当前产品与相近替代方案的真实决策差异。','我能用可验证的规格、机制、配置或使用任务判断它是否更适合我的需求。','BELIEVE','知道是什么，但比较维度不清','形成可验证的比较维度','COMMUNICATION','比较应建立在自己的Product Truth和可比事实，而不是竞品贬损或泛化“更好”。','只比较可追溯规格/机制/配置/任务差异；价格/促销按当前渠道单独处理。','comparison comprehension / PDP progression / CVR'),
      'INGREDIENT_COMPOSITION':('用户需要确认配方/组成来源或动物来源等组成边界，而不是食品意义上的饮食适配。','我知道产品由什么构成、相关来源边界是什么，以及哪些事实仍需确认。','REDUCE_RISK','产品价值已理解但配方/来源边界不清','组成与来源边界清楚','COMMUNICATION','美妆个护中的成分/来源问题应与食品营养/过敏原逻辑分开，避免“vegan”等词把决策语义错误食品化。','只使用当前配方/标签/品牌正式来源；不从成分名称推导功效或伦理认证。','composition comprehension / objection reduction'),
      'PORTABILITY':('用户理解功能，但不确定重量、体积和携带负担是否适合真实通勤/旅行。','我能把重量和尺寸映射到自己的携带场景。','REDUCE_RISK','功能可用但物理携带成本不清','形成真实重量/体积/携带预期','COMMUNICATION','电子/耐用品的便携性是独立购买风险，不能被性能或使用说明吞掉。','真实重量、尺寸和必要尺度参照；不以“便携”形容词替代数字。','CVR / portability comprehension / expectation-gap reduction'),
      'SITE_FIT':('高客单耐用品是否适合真实场地、门洞、预留空间或安装条件不清，会导致下单后取消或无法安装。','我能判断商品与场地尺寸/安装条件是否匹配。','REDUCE_RISK','有购买意向但场地适配未知','场地/预留/安装空间适配清楚','COMMUNICATION','高客单耐用品首先要证明“放得下、装得上、接得对”，再谈生活方式价值。','产品尺寸 + 场地/门洞/预留/接口要求；未知条件明确待确认。','CVR / site-fit comprehension / cancellation reduction'),
      'SIZE_FIT':('尺码、版型和身体测量关系不清，用户容易选错码或把模特视觉误当成自己的实际合身。','我能用尺码表、服装实测和身体/版型信息选择更合适的尺码。','REDUCE_RISK','知道款式但尺码选择不确定','尺码选择有可验证依据','COMMUNICATION','服装尺码是高退货风险的硬决策信息，应优先于泛化生活方式叙事。','尺码表/服装实测/版型描述/on-body比例；不承诺“适合所有人”。','CVR / size-selection confidence / size-related return reduction'),
      'INGREDIENT_DIETARY':('配料、营养、过敏原或饮食/认证信息不清会直接阻断食品购买。','我知道自己是否能吃/喝，以及关键配料和营养事实是什么。','BELIEVE','品类已识别但食用适配/成分风险未知','关键配料/营养/过敏原边界清楚','COMMUNICATION','食品的首要Proof往往是标签事实与适配边界，而不是“好吃/健康”的营销感受。','标签/配料/营养/过敏原/认证事实；不从包装视觉推断健康功效。','CVR / dietary-fit comprehension / complaint reduction'),
      'SENSORY_PREP':('用户不知道真实风味、冲泡/食用方法或份量，容易产生体验预期差。','我知道如何准备/食用，并理解有证据支持的风味/形态预期。','RELATE','产品适配已基本理解但体验方式不清','形成真实准备/食用与感官预期','COMMUNICATION','食品感官与准备方式影响购买与复购，但只有真实资料支持时才能描述。','真实冲泡/准备步骤、份量与有证据的风味/形态，不生成虚构食物特写。','CVR / preparation comprehension / repeat / expectation-gap reduction'),
      'PERFORMANCE_PROOF':('性能参数存在但无法判断对真实任务是否有意义，或缺少可验证测试语境。','我能把关键性能证据与自己的使用任务对应起来。','BELIEVE','产品相关但性能可信度不足','性能证据与任务语境对应','COMMUNICATION','电子/耐用品需要从规格数字进入可验证使用结果，避免用无上下文“大数字”制造优越感。','规格 + 测试条件/方法/适用任务；没有来源时保持待验证。','CVR / spec comprehension / performance-return reduction'),
      'WARRANTY_SERVICE':('高考虑度商品的售后、保修和维修路径不清会显著放大购买风险。','我知道出现问题后由谁、在什么范围内提供支持。','REDUCE_RISK','产品价值已理解但售后风险未知','服务/保修范围和路径清楚','COMMUNICATION','高客单或电子商品的风险降低不能只靠促销，需要真实服务保障信息。','当前市场/渠道的保修、服务与维修事实；不可从品牌印象推断。','CVR / service-question reduction / return-or-cancel reduction'),
      'DELIVERY_INSTALLATION':('配送、安装、组装或入户条件不清，会让高客单购买在结账前后失败。','我知道商品如何到达、安装/组装，以及需要什么前置条件。','REDUCE_RISK','购买意向存在但履约摩擦未知','配送/安装/组装预期清楚','COMMUNICATION','高客单耐用品的购买决策包含物流和安装，而不是只看产品本体。','实际配送/安装/组装范围、条件和责任边界。','checkout completion / cancellation reduction / service-contact reduction'),
      'TOTAL_COST_OWNERSHIP':('初始价格不能代表长期成本，耗材、能源、维护或订阅会改变真实价值。','我能理解购买后的持续成本和价值边界。','REDUCE_RISK','初始价格可见但长期成本未知','总拥有成本关键项可判断','COMMUNICATION','高客单/电子类Offer应解释长期价值，不用一次性折扣掩盖持续成本。','已知耗材/能源/维护/订阅事实；未知项明确待确认。','CVR / AOV / cancellation / lifecycle contribution'),
      'SIZE_CAPACITY':('尺寸、容量或比例不清，用户容易买错或高估/低估实际可用空间。','我能把产品的真实尺寸/容量映射到自己的使用需求。','REDUCE_RISK','规格数字存在但缺少真实尺度感','形成可比较的尺寸/容量预期','COMMUNICATION','把抽象规格翻译成可判断的空间/尺度信息。','真实尺寸、容量、比例与必要的尺度参照。','CVR / size-related return reduction / FAQ reduction'),
      'FIT_WEAR':('用户不知道商品如何贴合身体/穿戴、调整范围或实际携带状态。','我能判断真实佩戴方式、比例与调整是否适合自己。','RELATE','商品尺寸已知但身体关系未知','理解佩戴比例、调整与使用姿态','COMMUNICATION','穿戴/佩戴类商品必须把二维规格转成身体关系，避免只靠平铺美图。','on-body scale / adjustment / silhouette / access behavior。','engagement / CVR / fit-related return reduction'),
      'MATERIAL_SENSORY':('材质、表面、透明度或触感预期不清，图片容易把真实质感拍错。','我知道实际材质看起来/反光/纹理如何，以及它与使用的关系。','BELIEVE','商品外形可见但材质预期模糊','建立真实材质/表面预期','COMMUNICATION','材质是购买证据也是摄影工程输入，必须显示真实纹理/反射而非泛化“高级感”。','材质、织纹/透明/反射/表面行为。','material comprehension / CVR / expectation-gap reduction'),
      'WEATHER_BOUNDARY':('耐候/防泼水等能力边界不清，容易把有限能力误解成完全防护。','我知道在什么条件下可用，以及能力不等于什么。','REDUCE_RISK','能力词存在但边界不清','理解能力范围和限制','COMMUNICATION','边界比夸大效果更能降低误解和退货。','已验证耐候事实 + 明确限制，不演绎未证实测试结果。','CVR / misunderstanding reduction / return-theme reduction'),
      'CARE_MAINTENANCE':('清洁、洗护或维护限制不清，会影响购买后的使用成本和寿命预期。','我知道该如何维护，以及哪些处理方式应避免。','REDUCE_RISK','购买价值已理解但维护成本未知','形成真实维护预期','COMMUNICATION','耐用品/服饰的维护限制会直接影响满意度与退货。','真实care instructions / cleaning boundary。','FAQ reduction / post-purchase satisfaction / return reduction'),
      'PACKAGE_CONTENTS':('用户不确定实际收到的部件、数量或组合。','我知道包装内具体包含什么。','REDUCE_RISK','商品身份清楚但内容物不清','内容物/数量预期清楚','COMMUNICATION','明确内容物可以直接降低误购和客服。','package contents / quantity / included components。','CVR / package-confusion return reduction'),
      'SEAL_LEAK':('用户关心密封/防漏，但静态外观无法说明闭合结构和真实边界。','我能理解闭合结构、适用场景和已验证边界。','BELIEVE','知道用途但对密封可信度不足','理解结构证据与能力边界','COMMUNICATION','功能结构应通过闭合细节/操作演示说明，不用夸张液体特效代替证据。','closure detail / operation / verified seal or leak boundary。','CVR / functional comprehension / return-theme reduction'),
      'STORAGE_STACKING':('用户不知道产品在真实空间里如何堆叠/收纳以及会占多少位置。','我能判断它是否适合我的冰箱、柜体或收纳系统。','RELATE','规格可见但空间效率未知','理解真实收纳关系','COMMUNICATION','家居耐用品的价值常在系统关系而非单体美图。','stacking / nesting / storage footprint / system relation。','CVR / space-fit comprehension'),
      'COMPATIBILITY':('兼容范围或使用环境不清会导致直接误购或安全风险。','我知道它与哪些设备/环境/温度/部件匹配。','REDUCE_RISK','用户有购买意向但适配边界未知','兼容/适配范围清楚','COMMUNICATION','兼容性属于硬决策事实，必须优先于装饰性卖点。','compatibility / environment / supported-use boundary。','CVR / incompatibility return reduction'),
      'EXPECTATION_BOUNDARY':('用户需要明确哪些体验是事实、哪些不是承诺。','我对真实到手体验与能力边界有正确预期。','REDUCE_RISK','存在模糊预期','关键限制和预期被澄清','COMMUNICATION','主动管理边界可以减少高成本的期望落差。','truthful expectation boundary。','return-theme / complaint reduction'),
    }
    vals=base.get(intent)
    if not vals:
        vals=('当前消费者问题尚未被其他资产明确解决。','获得完成下一购买判断所需的增量信息。','DECISION_SUPPORT','存在未解决问题','问题被当前Surface原生内容解决','COMMUNICATION',f'专门解决消费者问题：{question}','只增加该问题所需的新信息。','surface-native decision metric')
    keys=['purchase_barrier','belief_target','journey_stage','entry_state','exit_state','race_stage','reason_to_exist','incremental_information','success_metric']
    out={'decision_intent':intent,**dict(zip(keys,vals))}
    # RACE authority in CBCC is Research / Action / Communication / Evaluation.
    # Asset decision intent is a separate commerce-decision dimension; a shopper-facing asset is
    # an execution of Communication, not a Reach/Act/Convert/Engage funnel label.
    out['race_stage']='COMMUNICATION'
    return out


def surface_score(intent:str,obj:dict[str,Any],category_family:str='GENERAL_COMMERCE')->int:
    family=str(obj.get('family') or ''); surface=str(obj.get('surface') or '')
    pref={
      'IDENTIFY':{'GALLERY':12,'SEARCH_RESULTS':11,'PDP':8,'PAID_AD':7,'CREATOR':3},
      'DIFFERENTIATION':{'PDP':12,'GALLERY':11,'FAQ':9,'PDP_VIDEO':8,'CREATOR':7},
      'RELEVANCE':{'CREATOR':12,'PDP_VIDEO':10,'GALLERY':7,'PDP':6},
      'PROOF':{'GALLERY':12,'PDP':11,'FAQ':7,'PDP_VIDEO':6},
      'INGREDIENT_COMPOSITION':{'PDP':12,'GALLERY':11,'FAQ':10,'PDP_VIDEO':6},
      'USAGE':{'PDP_VIDEO':12,'CREATOR':11,'FAQ':9,'PDP':6,'GALLERY':5},
      'SITE_FIT':{'PDP':12,'GALLERY':11,'FAQ':10,'PDP_VIDEO':8,'CREATOR':4},
      'SIZE_FIT':{'PDP':12,'GALLERY':11,'CREATOR':10,'FAQ':10,'PDP_VIDEO':8},
      'INGREDIENT_DIETARY':{'PDP':12,'GALLERY':11,'FAQ':10,'SEARCH_RESULTS':7,'PDP_VIDEO':5},
      'SENSORY_PREP':{'PDP_VIDEO':12,'CREATOR':11,'GALLERY':9,'PDP':8,'FAQ':7},
      'PERFORMANCE_PROOF':{'PDP':12,'GALLERY':11,'PDP_VIDEO':11,'FAQ':8,'CREATOR':7},
      'PORTABILITY':{'GALLERY':12,'PDP':10,'CREATOR':9,'FAQ':8,'PDP_VIDEO':7},
      'WARRANTY_SERVICE':{'FAQ':12,'PDP':11,'GALLERY':6,'CREATOR':4},
      'DELIVERY_INSTALLATION':{'PDP':12,'FAQ':11,'PDP_VIDEO':8,'GALLERY':7},
      'TOTAL_COST_OWNERSHIP':{'PDP':12,'FAQ':11,'GALLERY':7,'PDP_VIDEO':6},
      'SIZE_CAPACITY':{'GALLERY':12,'PDP':11,'FAQ':9,'PDP_VIDEO':7,'CREATOR':5},
      'FIT_WEAR':{'CREATOR':12,'GALLERY':11,'PDP_VIDEO':10,'PDP':6},
      'MATERIAL_SENSORY':{'GALLERY':12,'PDP_VIDEO':9,'PDP':8,'CREATOR':6},
      'WEATHER_BOUNDARY':{'GALLERY':10,'PDP':10,'CREATOR':8,'PDP_VIDEO':8,'FAQ':7},
      'CARE_MAINTENANCE':{'FAQ':12,'PDP':11,'GALLERY':5,'PDP_VIDEO':5},
      'PACKAGE_CONTENTS':{'GALLERY':12,'PDP':11,'FAQ':9,'PDP_VIDEO':6},
      'SEAL_LEAK':{'PDP_VIDEO':12,'GALLERY':10,'PDP':9,'CREATOR':8,'FAQ':6},
      'STORAGE_STACKING':{'PDP_VIDEO':12,'GALLERY':11,'PDP':8,'CREATOR':7},
      'COMPATIBILITY':{'PDP':12,'FAQ':11,'GALLERY':8,'PDP_VIDEO':7},
      'EXPECTATION_BOUNDARY':{'PDP':11,'FAQ':11,'GALLERY':7,'CREATOR':6},
      'DECISION_SUPPORT':{'GALLERY':8,'PDP':7,'PDP_VIDEO':6,'CREATOR':5,'FAQ':5},
    }.get(intent,{})
    score=pref.get(surface,0)
    # When only family information is available, avoid a creator-first fallback for identity/specification jobs.
    fam_bonus={'VISUAL':2,'VIDEO':1,'CREATOR_AFFILIATE':1,'CX':1,'LISTING':1,'PAID':0}
    score += fam_bonus.get(family,0)
    if category_family=='FASHION_ACCESSORY' and intent=='FIT_WEAR' and surface=='CREATOR': score+=2
    if category_family=='APPAREL_FIT' and intent=='SIZE_FIT' and surface in {'PDP','GALLERY'}: score+=2
    if category_family=='FOOD_BEVERAGE' and intent in {'INGREDIENT_DIETARY','SENSORY_PREP'} and surface in {'PDP','PDP_VIDEO'}: score+=2
    if category_family=='ELECTRONICS' and intent in {'COMPATIBILITY','PERFORMANCE_PROOF'} and surface=='PDP': score+=2
    if category_family=='HIGH_TICKET_DURABLE' and intent in {'SITE_FIT','DELIVERY_INSTALLATION','WARRANTY_SERVICE','TOTAL_COST_OWNERSHIP'} and surface in {'PDP','FAQ'}: score+=2
    if category_family=='HOME_DURABLE' and intent in {'SEAL_LEAK','STORAGE_STACKING'} and surface=='PDP_VIDEO': score+=2
    if category_family=='BEAUTY_PERSONAL_CARE' and intent=='PROOF' and surface=='GALLERY': score+=1
    if obj.get('required'): score+=1
    return score



def category_commerce_profile(request:dict[str,Any]) -> dict[str,Any]:
    """Category-specific commerce reasoning without inventing product facts.

    The profile changes decision order, proof/objection priorities, offer hypotheses and content cadence.
    Every row remains a strategy hypothesis/check until supported by Product Truth, platform policy and economics.
    """
    fam=infer_category_family(request)
    profiles={
      'BEAUTY_PERSONAL_CARE':{
        'objection_priorities':[
          ('FIT_ROUTINE','Is this appropriate for the stated routine/skin or hair context?','RELEVANCE','highlights/faq',['routine','skin','hair','use context']),
          ('CLAIM_PROOF','What Product Truth or approved evidence supports the primary benefit?','PROOF','highlights/gallery',['formula','ingredient','claim','evidence']),
          ('USAGE_EXPECTATION','How should it be used and what should not be over-promised?','USAGE','usage/faq',['usage','frequency','boundary']),
        ],
        'proof_hierarchy':['exact product/label identity','approved formula/ingredient/spec facts','claim-specific evidence/RTB','usage/expectation boundary','social/creator context only after truth is clear'],
        'offer_patterns':['single hero SKU for trust-building','trial/entry size only when unit economics and usage support it','routine bundle only when products have distinct complementary jobs','retention offer only when repeat behavior is evidenced'],
        'offer_avoid':['deep discount before value/proof is understood','bundle that merely increases quantity without a buyer job','urgency that overpowers claim boundary'],
        'message_sequence':['IDENTITY','ROUTINE RELEVANCE','APPROVED PROOF','USAGE / EXPECTATION BOUNDARY','OFFER / ACTION'],
        'cadence_model':'Rotate education, proof, usage and objection-resolution modules; refresh when review/CS themes or claim/evidence change rather than on an arbitrary posting quota.',
      },
      'APPAREL_FIT':{
        'objection_priorities':[
          ('SIZE_SELECTION','Which size should I choose from body and garment measurements?','SIZE_FIT','attributes/size-guide/faq',['size chart','measurements','fit']),
          ('FIT_SHAPE','How does the cut/length/volume sit on a real body?','FIT_WEAR','gallery/creator',['fit','silhouette','model measurement']),
          ('MATERIAL_CARE','What fabric/construction and care limits affect comfort and ownership?','MATERIAL_SENSORY','attributes/faq',['material','fabric','care']),
          ('RETURN_RISK','What size/variant uncertainty should be resolved before purchase?','EXPECTATION_BOUNDARY','faq',['variant','size','return policy source']),
        ],
        'proof_hierarchy':['size chart + garment measurements','fit/silhouette with explicit model/garment context','fabric/construction/color truth','care and weather boundary','style inspiration after fit truth'],
        'offer_patterns':['variant availability clarity before discount','multi-buy only when fit confidence is already high','exchange/return reassurance only from current platform/store policy','seasonal offer only after size inventory and margin are checked'],
        'offer_avoid':['discount used to compensate for unresolved sizing','one model image treated as universal fit proof','bundle/multi-buy that increases size-return exposure'],
        'message_sequence':['IDENTITY','SIZE / FIT','MATERIAL / CONSTRUCTION','CARE / RISK','STYLE RELEVANCE','OFFER / ACTION'],
        'cadence_model':'Alternate fit/size education, material/detail proof and outfit/use-context; refresh with size-inventory, fit feedback and seasonal context changes.',
      },
      'FASHION_ACCESSORY':{
        'objection_priorities':[
          ('SCALE_CAPACITY','Will the item fit the intended essentials without unwanted bulk?','SIZE_CAPACITY','attributes/gallery',['capacity','dimension','scale']),
          ('WEAR_ADJUST','How does it sit/wear/adjust on the body?','FIT_WEAR','gallery/creator',['strap','wear','adjust']),
          ('MATERIAL_WEATHER','What material and weather/care boundary should I expect?','WEATHER_BOUNDARY','attributes/faq',['material','weather','care']),
        ],
        'proof_hierarchy':['dimensions/capacity','on-body scale and adjustment','material/construction detail','weather/care boundary','styling context'],
        'offer_patterns':['single hero color/shape for identity','variant/color choice with clear inventory','multi-buy only with distinct use/color job'],
        'offer_avoid':['style-only creative before scale/capacity is understood','discount without configuration clarity'],
        'message_sequence':['IDENTITY','SCALE / WEAR','MATERIAL / FUNCTION','CARE / BOUNDARY','STYLE / ACTION'],
        'cadence_model':'Rotate scale/wear demonstrations, organization/material proof and styling context; refresh when variants, inventory or care/weather evidence changes.',
      },
      'FOOD_BEVERAGE':{
        'objection_priorities':[
          ('DIETARY_FIT','Do ingredients, nutrition, allergens or certifications fit my needs?','INGREDIENT_DIETARY','attributes/gallery/faq',['ingredient','nutrition','allergen','certification']),
          ('TASTE_PREP','What does it taste/feel like and how is it prepared or served?','SENSORY_PREP','gallery/video/usage',['flavor','taste','brew','serve','prep']),
          ('PACK_VALUE','What quantity/servings/pack format am I actually buying?','PACKAGE_CONTENTS','attributes/package',['net content','serving','count','pack']),
          ('STORAGE_FRESHNESS','How should it be stored and what freshness/expiry facts are known?','EXPECTATION_BOUNDARY','faq',['storage','shelf life','expiry']),
        ],
        'proof_hierarchy':['label identity + net content','ingredients/nutrition/allergen/certification facts','real product/serving/preparation evidence','supported sensory description','storage/shelf-life/package facts'],
        'offer_patterns':['single pack for first trial','variety/sampler only when variants are real and clearly identified','multipack when repeat/household job and shelf-life support it','subscription/replenishment only after repeat behavior and expiry economics are known'],
        'offer_avoid':['health halo from color/ingredient imagery','bulk offer that hides unit price or shelf-life risk','fake sensory imagery not sourced from real product'],
        'message_sequence':['IDENTITY / PACK','DIETARY FIT','REAL PREP / SENSORY','PACK VALUE / STORAGE','OFFER / REORDER'],
        'cadence_model':'Rotate label/dietary facts, real preparation/serving, sensory education and usage occasions; refresh for formulation, certification, pack or seasonal-consumption changes.',
      },
      'ELECTRONICS':{
        'objection_priorities':[
          ('COMPATIBILITY','Will it work with my device/system/region?','COMPATIBILITY','attributes/faq',['compatibility','interface','system','region']),
          ('PERFORMANCE','Which performance claim matters for my task and under what test conditions?','PERFORMANCE_PROOF','highlights/gallery/video',['battery','speed','latency','noise','performance']),
          ('CONTROLS_SETUP','How do I set it up and operate the important functions?','USAGE','usage/video',['setup','control','pair','install']),
          ('SERVICE','What warranty/support/repair route applies in this market/channel?','WARRANTY_SERVICE','faq',['warranty','service','support']),
          ('PACKAGE','What accessories/cables/components are included?','PACKAGE_CONTENTS','package/gallery',['included','cable','adapter','accessory']),
        ],
        'proof_hierarchy':['compatibility/interface truth','core specs with test conditions','task-relevant performance evidence','setup/operation demonstration','warranty/service/package facts'],
        'offer_patterns':['base device with exact configuration','accessory bundle only when compatibility and contribution are clear','warranty/service add-on only from actual policy','upgrade/trade-up only when performance delta solves a distinct job'],
        'offer_avoid':['spec-sheet number dumping without user task','bundle with incompatible or redundant accessories','discount used to hide weak compatibility clarity'],
        'message_sequence':['IDENTITY','COMPATIBILITY','TASK PERFORMANCE','SETUP / OPERATION','SERVICE / PACKAGE','OFFER / ACTION'],
        'cadence_model':'Rotate compatibility/setup, performance proof and use-case workflows; refresh when firmware, device compatibility, configuration or warranty facts change.',
      },
      'HOME_DURABLE':{
        'objection_priorities':[
          ('SIZE_SPACE','Will it fit the intended space/capacity job?','SIZE_CAPACITY','attributes/gallery',['dimension','capacity','space']),
          ('FUNCTION_STRUCTURE','Does the structure/closure/system do the job it claims?','PROOF','gallery/video',['structure','seal','stack','function']),
          ('MATERIAL_CARE','What material, compatibility and care boundary affects ownership?','MATERIAL_SENSORY','attributes/faq',['material','care','compatibility']),
        ],
        'proof_hierarchy':['dimensions/capacity','material/structure','functional demonstration','compatibility/care','space/organization context'],
        'offer_patterns':['single configuration for exact job','set/bundle only when components form a useful system','size ladder when each size maps to a distinct use job'],
        'offer_avoid':['decorative lifestyle imagery before function/size truth','bundle that duplicates capacity without a use reason'],
        'message_sequence':['IDENTITY','SIZE / SPACE','STRUCTURE / FUNCTION','MATERIAL / CARE','SYSTEM CONTEXT','OFFER / ACTION'],
        'cadence_model':'Rotate size/space proof, functional demonstrations and care/system education; refresh when configurations or compatibility facts change.',
      },
      'HIGH_TICKET_DURABLE':{
        'objection_priorities':[
          ('SITE_FIT','Will it fit the physical site and required utilities/clearances?','SITE_FIT','attributes/pdp',['dimension','clearance','utility','space']),
          ('PERFORMANCE','What performance evidence matters for the ownership job?','PERFORMANCE_PROOF','pdp/video',['performance','capacity','efficiency','noise']),
          ('DELIVERY_INSTALL','How is it delivered, assembled or installed and what must be prepared?','DELIVERY_INSTALLATION','pdp/faq',['delivery','installation','assembly']),
          ('SERVICE_WARRANTY','What service/warranty route protects the purchase?','WARRANTY_SERVICE','faq',['warranty','service','repair']),
          ('TOTAL_COST','What ongoing energy/consumable/maintenance cost changes the real value?','TOTAL_COST_OWNERSHIP','pdp/faq',['energy','consumable','maintenance','subscription']),
        ],
        'proof_hierarchy':['site/size/utility fit','construction/material/critical interfaces','task-relevant performance with conditions','delivery/installation facts','warranty/service','total ownership cost'],
        'offer_patterns':['configuration ladder only with clear job/value delta','delivery/installation bundle only from real service capability','financing/promo only after total-cost and contribution check','service/warranty add-ons only from actual policy'],
        'offer_avoid':['coupon-first strategy for high-consideration risk','luxury lifestyle replacing site/performance proof','hidden delivery/installation cost'],
        'message_sequence':['IDENTITY','SITE FIT','PERFORMANCE / BUILD','DELIVERY / INSTALLATION','SERVICE / TOTAL COST','OFFER / CONSULT / ACTION'],
        'cadence_model':'Lower-frequency, deeper proof modules: site planning, performance, installation, service and owner education; refresh with model/configuration/service/energy-cost changes.',
      },
      'GENERAL_COMMERCE':{
        'objection_priorities':[('FIT','What must be true for this product to fit the shopper job?','RELEVANCE','pdp/faq',['product truth']),('PROOF','What proves the primary value?','PROOF','pdp/gallery',['evidence']),('USE','What use/compatibility/expectation risk should be clarified?','USAGE','usage/faq',['usage','boundary'])],
        'proof_hierarchy':['exact product identity','decision-relevant facts','approved proof','risk/usage boundary'],
        'offer_patterns':['offer only after a clear buyer job and unit-economics check'],
        'offer_avoid':['discount-first positioning','bundle without an incremental buyer job'],
        'message_sequence':['IDENTITY','RELEVANCE','PROOF','RISK','ACTION'],
        'cadence_model':'Rotate by unresolved decision state; refresh when product, market or feedback evidence changes.',
      }
    }
    raw=profiles[fam]
    objections=[]
    for rank,row in enumerate(raw['objection_priorities'],1):
        key,question,intent,field,evidence=row
        objections.append({'rank':rank,'objection_key':key,'question':question,'decision_intent':intent,'recommended_field':field,'evidence_needed':evidence,'status':'CATEGORY_DECISION_CHECK','why':'Category-level risk priority; activate as an own-product objection only when Product Truth, shopper questions, market/review evidence or feedback supports it.'})
    proof=[{'rank':i+1,'proof_type':x,'status':'EVIDENCE_PRIORITY_NOT_AUTOMATIC_CLAIM','why':'Higher-ranked proof should answer a more fundamental purchase uncertainty for this category; availability still depends on Product Truth/evidence.'} for i,x in enumerate(raw['proof_hierarchy'])]
    return {'status':'CATEGORY_COMMERCE_PROFILE','category_family':fam,'objection_priorities':objections,'proof_hierarchy':proof,'offer_architecture':{'candidate_patterns':raw['offer_patterns'],'avoid_shortcuts':raw['offer_avoid'],'status':'CATEGORY_OFFER_HYPOTHESES_REQUIRE_ECONOMICS_AND_PRODUCT_FIT','why':'Category norms shape which offer structures are worth testing, but they do not override contribution economics, platform rules or actual product configuration.'},'message_architecture':{'sequence':raw['message_sequence'],'status':'CATEGORY_DECISION_SEQUENCE','why':'The category changes the order of beliefs that usually block purchase; exact copy still comes from Product Truth and approved claims.'},'content_cadence':{'model':raw['cadence_model'],'fixed_posting_frequency':False,'refresh_triggers':['product/configuration change','new market/search/review evidence','material feedback/return theme','platform surface or policy change'],'why':'Cadence is an information-rotation and refresh logic, not an invented posts-per-week quota.'},'boundary':'Category profile changes prioritization and sequencing only. It never creates claims, return policies, certifications, compatibility, warranty, sensory facts or performance evidence.'}

def category_execution_profile(request:dict[str,Any]) -> dict[str,Any]:
    fam=infer_category_family(request); product=request.get('product') or {}
    profiles={
      'BEAUTY_PERSONAL_CARE':{
        'visual_territory':'真实配方/包装证据 × 日常使用语境的临床克制商业视觉',
        'priority_decisions':['产品身份','适用语境','配方/成分或经批准功效证据','使用方式与预期边界'],
        'proof_visuals':['包装/标签可读','只有真实资料支持时才表现真实质地','人物皮肤保持真实纹理，不用滤镜制造效果'],
        'human_rule':'人物只在适用语境、使用方法或真实体验理解需要时出现；证据图不强制加人。',
        'camera_plan':{'identity_or_proof':'70–105mm equivalent, perspective-controlled pack/product view','context_or_use':'50–85mm equivalent when body/hand/context relation is decision-relevant','macro':'Only when a real texture/detail source exists and the detail changes a purchase decision.'},
        'lighting_plan':'包装/质地/皮肤分别按真实表面响应控光；先保标签与真实肤色，再做氛围。',
      },
      'APPAREL_FIT':{
        'visual_territory':'尺码/版型/身体关系 × 面料结构 × 真实穿着状态的服装决策视觉',
        'priority_decisions':['尺码选择与服装实测','版型/松量/长度','on-body比例与活动状态','面料/结构','洗护/退换相关信息边界'],
        'proof_visuals':['尺码表/实测示意','多身型或明确模特测量信息（有真源时）','正侧背或关键版型视图','面料与缝制细节','活动/坐立等真实穿着状态'],
        'human_rule':'人物是尺码与版型证据时必须绑定模特身高/尺码/关键测量；不把单一模特视觉当成普遍合身承诺。',
        'camera_plan':{'identity_or_proof':'70–105mm equivalent for garment silhouette/measurement views','context_or_use':'50–85mm equivalent for full-body fit without wide-angle distortion','macro':'85–105mm/detail only for fabric, seam, closure or construction proof.'},
        'lighting_plan':'保留服装轮廓、面料结构和真实颜色；避免过度柔光/修身后期改变版型和材质预期。',
      },
      'FASHION_ACCESSORY':{
        'visual_territory':'轮廓/尺度/佩戴关系 × 面料真实纹理 × 功能细节的生活方式商业视觉',
        'priority_decisions':['真实尺寸与容量','on-body比例/佩戴方式','肩带或调节结构','面料纹理与耐候边界','维护限制'],
        'proof_visuals':['独立商品轮廓','on-body尺度','开口/内袋/肩带调节细节','面料近景但不夸大纹理','真实容量参照'],
        'human_rule':'穿戴关系本身是决策证据时必须出现人物/人体尺度；材质、结构、内容物资产不需要机械加模特。',
        'camera_plan':{'identity_or_proof':'70–105mm equivalent for silhouette and geometry','context_or_use':'50–70mm equivalent for on-body scale without wide-angle body/bag distortion','macro':'85–105mm or macro/detail only for weave, stitching, hardware or closure evidence.'},
        'lighting_plan':'用侧向/斜向大光源保留织纹和立体褶皱；避免正面大柔光把面料拍平，也避免过强掠射夸大缺陷。',
      },
      'HIGH_TICKET_DURABLE':{
        'visual_territory':'空间适配/结构/性能 × 配送安装 × 服务与长期价值的高考虑度耐用品商业视觉',
        'priority_decisions':['空间/尺寸与安装条件','关键性能与真实测试语境','材质/结构/接口','配送/安装/组装','保修/售后','长期耗材/能源/维护成本'],
        'proof_visuals':['精确尺寸/空间关系','结构/接口/操作细节','有来源的性能证据','安装/维护路径示意','服务/保修信息模块'],
        'human_rule':'人物/技师只在尺度、安装、操作或服务流程有决策价值时出现；不以豪华生活方式场景替代产品证据。',
        'camera_plan':{'identity_or_proof':'50–85mm equivalent for large-object geometry and spatial truth','context_or_use':'35–70mm equivalent only when room/site fit requires wider context, with distortion control','macro':'70–105mm/detail for interfaces, joints, filters, controls or material proof.'},
        'lighting_plan':'先确保大体积结构、材质和接口可读，再建立空间氛围；玻璃/金属/屏幕按各自反射行为分区控光。',
      },
      'HOME_DURABLE':{
        'visual_territory':'真实尺寸/结构/材质 × 功能操作 × 空间关系的产品工程型商业视觉',
        'priority_decisions':['容量/尺寸','内容物/部件','结构/闭合/密封','材质与透明度','堆叠/收纳/空间效率','兼容与维护边界'],
        'proof_visuals':['正面/三分之四结构视图','顶部/闭合/接口细节','尺度/容量参照','堆叠或真实空间关系','透明/反光材料边缘与内容可见性'],
        'human_rule':'手部/人物只在操作、尺度或空间关系需要时出现；不把耐用品自动拍成生活方式人物广告。',
        'camera_plan':{'identity_or_proof':'70–105mm equivalent for geometry-controlled hero/spec views','context_or_use':'50–70mm equivalent for fridge/counter/storage context','macro':'85–105mm/detail for lid, seal, hinge, texture or interface evidence.'},
        'lighting_plan':'以结构、透明边缘、盖体/接口可读性为核心；玻璃/高光塑料用反射卡与边缘分离，不用泛化柔光抹平结构。',
      },
      'FOOD_BEVERAGE':{
        'visual_territory':'包装真实信息 × 食用/冲泡语境 × 感官线索（仅限真实资料）的清晰食品商业视觉',
        'priority_decisions':['品类/规格','配料/营养/过敏原或认证','风味/形态（有真实证据时）','食用/冲泡方式','包装数量与保存'],
        'proof_visuals':['包装信息可读','真实食物/饮品形态','份量/冲泡过程','关键信息图'],
        'human_rule':'人物只在食用场景/份量/生活语境有决策价值时出现。',
        'camera_plan':{'identity_or_proof':'70–105mm equivalent for package truth','context_or_use':'50–85mm equivalent for serving/preparation context','macro':'Only for real ingredient/texture/food detail evidence.'},
        'lighting_plan':'先保证食品色和包装色真实，再控制新鲜感/质感；不靠不真实水花、蒸汽或原料堆砌暗示未经证实成分。',
      },
      'ELECTRONICS':{
        'visual_territory':'结构/接口/尺度/兼容 × 操作结果的技术产品商业视觉',
        'priority_decisions':['产品身份','尺寸/接口','兼容性','操作方式','关键性能证据','包装内容物'],
        'proof_visuals':['正交结构','接口/按钮细节','尺度关系','真实操作/屏显（有真源时）'],
        'human_rule':'人物只在人体工学/使用尺度需要时出现。',
        'camera_plan':{'identity_or_proof':'70–105mm equivalent for geometry and interface truth','context_or_use':'50–70mm equivalent for desk/hand/use context','macro':'85–105mm/detail for ports, controls, finish.'},
        'lighting_plan':'反射/金属/屏幕分别处理，接口文字与材质边界优先于氛围。',
      },
      'GENERAL_COMMERCE':{
        'visual_territory':'购买问题驱动的产品真实感商业视觉',
        'priority_decisions':['产品身份','相关性','证据','规格/风险','使用'],
        'proof_visuals':['真实产品','决策所需规格/细节/语境'],
        'human_rule':'人物只在它能回答购买问题时出现。',
        'camera_plan':{'identity_or_proof':'Perspective-controlled normal-to-short-tele product view','context_or_use':'Context lens only when spatial/human relation is decision-relevant','macro':'Only when a real detail changes the decision.'},
        'lighting_plan':'按真实材质与购买问题控光，不使用统一“高级柔光”配方。',
      }
    }
    out={'category_family':fam,**profiles[fam]}
    out['status']='CATEGORY_SPECIFIC_EXECUTION_PROFILE'
    out['basis']={'target_category':(request.get('target') or {}).get('category'),'product_category':product.get('category'),'product_type':product.get('product_type'),'product_name':product.get('name')}
    out['boundary']='This profile changes decision/visual execution logic only. It does not create product facts, claims, compatibility or performance evidence.'
    return out
