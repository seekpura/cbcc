from __future__ import annotations
from pathlib import Path
from typing import Any
import base64, html, json, mimetypes, re

from .workspace_autonomy import build_workspace_route_plan, relevant_asset_view_keys


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''


def _read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {} if default is None else default


def _slug(text: str) -> str:
    return (re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]+', '-', str(text)).strip('-')[:80] or 'section').lower()


def _has_cjk(text: Any) -> bool:
    return bool(re.search(r'[\u4e00-\u9fff]', str(text or '')))


def _zh_heading(text: Any) -> str:
    raw=str(text or '').strip()
    table={
        'overview':'总览','product truth':'产品事实','market & audience':'市场与人群','market and audience':'市场与人群',
        'listing':'上架资料','strategy':'营销策略','visual & photography':'视觉与摄影','visual and photography':'视觉与摄影',
        'asset library':'资产中心','prompt lab':'提示词工作台','risk & compliance':'风险与合规','risk and compliance':'风险与合规',
        'sources':'来源与真源','archive':'完整归档','complete archive':'完整归档','matched sku':'匹配商品','current holds':'当前待补 / HOLD',
        'claim ledger':'宣称与证据台账','real source gallery':'真实来源图库','primary audience':'核心人群','secondary':'次级人群',
        'culture / casting':'文化与模特呈现','message hierarchy':'信息层级','jtbd barriers':'JTBD 障碍','cmf':'CMF 色彩 / 材质 / 表面',
        'photography master':'摄影主方案','territories explored':'已探索创意方向','content matrix':'内容矩阵','p0':'P0 必须项','p1':'P1 重要项','p2':'P2 加分项',
        'bm description':'马来语商品描述','en description':'英文商品描述','search architecture':'搜索架构','platform category':'平台类目',
        'complete content':'完整内容','full content':'完整内容','summary':'概览','strategy authority':'策略权威','upload ready':'上架就绪',
        # Common machine keys are rendered as Chinese human labels. The raw key remains in JSON/archive only.
        'stage':'阶段','objective':'目标','key_actions':'关键动作','output':'输出物','platform':'平台','culture_check':'文化校验','kpi':'指标','why':'为什么',
        'claim':'宣称 / 事实','fact':'事实','grade':'证据等级','status':'状态','basis':'依据','source':'来源','source_ids':'来源 ID','evidence':'证据',
        'adaptation_point':'文化适配点','evidence_or_implication':'依据 / 影响','inclusive_representation':'包容性表征','stereotype_taboo_risk':'刻板印象 / 禁忌风险','result':'校验结果','modification':'修改动作',
        'audience':'人群','topic':'选题','hook':'钩子','script':'脚本结构','visual':'视觉形式','cta':'CTA / 行动引导','race_stage':'RACE 阶段','culture_validation':'文化 / 禁忌校验',
        'dimension':'维度','decision':'决策','rationale':'依据','tradeoff':'取舍','action':'执行动作','metric':'指标','priority':'优先级','assumption':'假设','fact_or_assumption':'事实 / 假设',
        'product_name':'商品名称','title':'标题','description':'商品描述','highlights':'核心卖点','bullets':'卖点','usage':'使用方法','ingredients':'成分','warnings':'警示','attributes':'属性','category':'类目','category_id':'类目 ID','category_path':'类目路径',
        'locale':'语言 / Locale','field':'字段','value':'内容','release_status':'发布状态','delivery_translation':'中文释义','delivery_note':'中文说明',
        'asset_id':'资产 ID','surface':'展示位置（Surface）','role':'资产角色','consumer_question':'消费者问题','strategic_job':'战略任务','product_presence':'产品出现方式','decision_intent':'决策意图',
        '01_information_completeness_assumptions_decisions':'信息完整度 / 假设 / 决策日志','02_product_truth_value_ladder':'产品事实 / 价值分级','03_platform_region_audience_culture_insight':'平台 / 区域 / 人群 / 文化洞察','04_marketing_core_strategy':'营销核心策略','05_visual_photography_strategy':'视觉 / 摄影策略','06_platform_content_matrix':'平台内容矩阵','07_race_execution_table':'RACE 传播执行','08_culture_adaptation_checklist':'文化适配检查','09_risk_measurement_priority_next_steps':'风险 / 指标 / 优先级 / 下一步',
        '中文 canonical prompt':'中文规范生产提示词','中文生产提示词（canonical prompt）':'中文规范生产提示词','英文 / 生成模型 prompt':'英文 / 生成模型执行提示词',
        'camera':'镜头 / 相机','lighting':'灯光','composition':'构图','cmf':'CMF','material_response':'材质响应','copy':'文案','copy_hierarchy':'文案层级','language':'语言','metric_hypothesis':'指标假设',
    }
    low=raw.casefold()
    if low in table:return table[low]
    prefix_rules=[
        (r'^executive summary', '决策摘要'),
        (r'^4\.1\s+product\s*/\s*sku\s*/\s*offer strategy', '4.1 产品 / SKU / Offer 策略'),
        (r'^4\.2\s+positioning\s*/\s*value proposition\s*/\s*message architecture', '4.2 定位 / 价值主张 / 信息架构'),
        (r'^shot list$', '镜头表'),
        (r'^asset visual production signatures$', '资产视觉生产签名'),
        (r'^asset-level photography causal why$', '单资产摄影因果 WHY'),
        (r'^dynamic asset curation$', '动态资产策展'),
        (r'^9\.1\s+ads\s*/\s*economics\s*/\s*incrementality', '9.1 广告 / 经济性 / 增量'),
        (r'^9\.2\s+review\s*/\s*cs\s*/\s*return', '9.2 评论 / 客服 / 退货 → 局部修订'),
        (r'^asset strategy$', '资产策划与决策'),
        (r'^strategy contract$', '策略合同'),
        (r'^visual execution contract$', '视觉执行合同'),
        (r'^why this visual exists$', '为什么这张资产必须存在'),
        (r'^machine-readable contract$', '机器可读合同'),
        (r'^locked visible copy$', '锁定的可见文案'),
        (r'^production notes$', '生产说明'),
        (r'^provider / route$', '执行路由'),
        (r'^surface production contract$', '展示位置生产合同（Surface）'),
        (r'^production quality targets$', '生产质量目标'),
        (r'^source trace$', '来源追踪'),
    ]
    for pat,zh in prefix_rules:
        if re.search(pat,low):return zh
    return raw


def _human_cn_internal(text: Any) -> str:
    """Translate CBCC-owned machine prose/labels for the Chinese human layer.

    Target-market copy is not generically translated here; only known internal terminology,
    statuses and deterministic fallback sentences are localized.
    """
    s=str(text or '')
    exact={
      'SUFFICIENT_FOR_STRATEGY_WITH_GAPS':'信息足以继续策略，但仍有缺口',
      'MARKET_DATA_NOT_SUPPLIED':'市场数据未提供',
      'CATEGORY_EVIDENCE_RECONCILED':'品类先验与当前证据已协调',
      'CATEGORY_OFFER_HYPOTHESES_REQUIRE_ECONOMICS_AND_PRODUCT_FIT':'品类 Offer 候选需通过商品适配与单位经济验证',
      'CATEGORY_OFFER_EVIDENCE_VALIDATION':'品类 Offer 证据校验',
      'LISTING_STRATEGY_COMPILED':'上架策略已编译',
      'SUPPLIED_FOR_REVIEW':'已提供，待专业复核',
      'NUMERIC_EQUIVALENCE_REVIEW':'数值等价性待复核',
      'EVIDENCE_PRIORITY_NOT_AUTOMATIC_CLAIM':'证据优先级，不自动构成宣称',
      'ACTIVE_CATEGORY_DECISION_RISK':'当前项目已激活的品类决策风险',
      'CATEGORY_CHECK_NOT_YET_ACTIVATED':'品类检查项，当前尚未激活',
      'PROJECT_FOCAL / HERO_CANDIDATE':'当前项目主推 / Hero 候选',
      'IDENTITY + PRIMARY VALUE':'产品识别 + 第一购买理由',
      'TRUST / RISK REDUCTION':'信任 / 风险降低',
      'SEARCH_RELEVANCE':'搜索相关性',
      'TITLE_OR_PRIMARY':'标题 / 主字段',
      'BULLET_OR_DETAIL':'卖点 / 详情字段',
      'APPROVED_FINAL':'已批准最终版',
      'BLOCKED_HARD_CONSTRAINT':'硬约束阻断',
      'DRAFT_REVIEW_REQUIRED':'草稿，需专业复核',
      'READY':'就绪','PARTIAL':'部分信息','MISSING':'缺失','ASSUMPTION':'假设',
      'RESEARCH':'研究','ACTION':'行动','COMMUNICATION':'传播执行','EVALUATION':'评估',
      'IDENTIFY':'识别产品','RELATE':'建立相关性','BELIEVE':'建立可信度','REDUCE RISK':'降低风险','NEXT_ACTION':'下一步行动',
      'CORE':'核心搜索','FEATURE':'特征 / 配方搜索','PROOF':'证据','USAGE':'使用方式','RELEVANCE':'相关性',
    }
    if s in exact:return exact[s]
    phrases=[
      ('Product Truth','产品真源'),('approved claims','已批准宣称'),('Claim Evidence','宣称证据'),('Claim / Evidence','宣称 / 证据'),
      ('Primary Conversion Proposition','第一转化主张'),('Value Proposition','价值主张'),('Message Architecture','信息架构'),
      ('Category Message Architecture','品类信息架构'),('Category Proof Hierarchy','品类证据层级'),('Category Objection Priorities','品类异议优先级'),
      ('Generic Message Hierarchy Reference','通用信息层级参考'),('Belief Sequence','信念推进序列'),('Commerce Response Ladder','商业响应阶梯'),
      ('Search Intent Architecture','搜索意图架构'),('Locale × Field Transcreation Tasks','语言 × 字段本土化改写任务'),('Localized Copy Audit','本土化文案审计'),
      ('Local-language Final Copy Workflow','本地语言最终文案流程'),('Platform Native Profile','平台原生表达画像'),('Release Rule','发布规则'),('Generation Contract','生成合同'),('Release Counts','发布状态统计'),
      ('Field Content / Strategy','字段内容 / 策略'),('Attributes','属性'),('Highlights/Bullets','核心卖点 / 卖点'),('Description','商品描述'),('FAQ','常见问题'),
      ('Market Evidence → Product Truth Fit Contract','市场证据 → 产品真源适配合同'),('Offer Strategy','Offer 策略'),('Hero Candidate','主推候选'),('Cannibalization','内部蚕食'),
      ('Surface Need','展示位置需求'),('Incremental Information','新增信息价值'),('Business Hypothesis','商业假设'),('Surface','展示位置'),
      ('Dynamic Asset Curation','动态资产策展'),('Asset Visual Production Signatures','资产视觉生产签名'),('Shot List','镜头表'),
      ('Human Use Decisive Moment','真实使用关键瞬间'),('Information Hierarchy as Visual Form','信息层级视觉化'),('Canonical Prompt','规范生产提示词'),
      ('Provider / Route（执行路由）','执行路由'),('Surface 生产合同','展示位置生产合同'),('Claim / 卖点价值分级','宣称 / 卖点价值分级'),
      ('9.1 Ads / Economics / Incrementality','9.1 广告 / 经济性 / 增量'),('9.2 Review / CS / Return → Local Revision','9.2 评论 / 客服 / 退货 → 局部修订'),
    ]
    for a,b in phrases:s=s.replace(a,b)
    sentence_map={
      'Current market/search/review evidence may change priority and sequence only after quality weighting; it never creates own-product facts or proves that competitor/customer observations apply to the product.':'当前市场、搜索、评论证据只有在完成质量加权后才能调整优先级和顺序；它不能创造本产品事实，也不能证明竞品或消费者观察天然适用于本产品。',
      'Category norms shape which offer structures are worth testing, but they do not override contribution economics, platform rules or actual product configuration.':'品类惯例只决定哪些 Offer 结构值得测试，不能覆盖贡献经济、平台规则或真实商品配置。',
      'The category changes the order of beliefs that usually block purchase; exact copy still comes from Product Truth and approved claims.':'品类会改变阻碍购买的信念顺序；最终文案仍必须来自产品真源与已批准宣称。',
      'Higher-ranked proof should answer a more fundamental purchase uncertainty for this category; availability still depends on Product Truth/evidence.':'优先级更高的证据应先回答该品类更基础的购买不确定性；是否可用仍取决于产品真源与真实证据。',
      'Category-level risk priority; activate as an own-product objection only when Product Truth, shopper questions, market/review evidence or feedback supports it.':'这是品类层风险优先级；只有当产品真源、购买问题、市场 / 评论证据或反馈支持时，才可升级为本产品异议。',
      'What Product Truth or approved evidence supports the primary benefit?':'什么产品真源或已批准证据能够支持核心利益？',
      'How should it be used and what should not be over-promised?':'应该如何使用？哪些内容不能过度承诺？',
      'Is this appropriate for the stated routine/skin or hair context?':'它是否适合当前声明的日常流程、肤质或发质语境？',
      'Numbers often encode size, concentration, duration or quantity. Extra numbers are allowed only when this exact field already carries an explicit approved Claim reference containing that number; all other drift remains blocked.':'数字通常代表规格、浓度、时长或数量。只有该字段已有明确且获批的宣称来源时才能增加对应数字；其他数值漂移均应阻断。',
      'Product identity/spec must remain factually equivalent':'产品身份 / 规格必须保持事实等价',
      'Claim strength/evidence boundary must not increase':'宣称强度 / 证据边界不得被放大',
      'Numbers/pack contents/usage constraints must remain equivalent':'数字、包装内容物与使用限制必须保持等价',
      'Rewrite syntax and information order for the locale; do not translate word-by-word':'按目标语言重新组织句法和信息顺序，不做逐字翻译',
      'Use locally natural product/category wording when supported by search/market evidence':'在搜索 / 市场证据支持时使用当地自然的商品 / 品类表达',
      'Preserve search intent without keyword stuffing':'保留搜索意图，不堆砌关键词',
      'No localized string becomes APPROVED_FINAL merely because it exists. It must pass deterministic hard checks and explicit professional language/claim/platform/culture review of the current version.':'任何本土化文案都不会因为“已经生成”就自动成为最终批准版；当前版本必须通过确定性硬检查，以及语言、宣称、平台和文化的专业复核。',
      'Host/model authors or revises target-locale drafts from Strategy Authority + Transcreation Tasks; runtime audits hard invariants, version binding and review/release state.':'宿主模型依据策略权威与本土化改写任务撰写 / 修订目标语言草稿；Runtime 负责审计硬约束、版本绑定以及复核 / 发布状态。',
      'The live PDP sequence is compiled from current atomic buyer questions and evidence priority. Category message architecture remains a prior/reference, not a substitute for product-specific unresolved decisions.':'当前 PDP 顺序由本项目的原子购买问题与证据优先级编译；品类信息架构只是先验 / 参考，不能替代本产品尚未解决的具体购买决策。',
    }
    for a,b in sentence_map.items():s=s.replace(a,b)
    return s


def _inline(text: Any) -> str:
    s=html.escape(_human_cn_internal(text), quote=False)
    s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
    s=re.sub(r'\*([^*]+)\*',r'<em>\1</em>',s)
    return s


def markdown_to_html(text: str) -> str:
    lines=text.splitlines(); out=[]; i=0; in_code=False; code=[]; in_ul=False; in_ol=False
    def close_lists():
        nonlocal in_ul,in_ol
        if in_ul: out.append('</ul>'); in_ul=False
        if in_ol: out.append('</ol>'); in_ol=False
    while i<len(lines):
        line=lines[i]
        if line.strip().startswith('```'):
            if not in_code: close_lists(); in_code=True; code=[]
            else: out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>'); in_code=False
            i+=1; continue
        if in_code: code.append(line); i+=1; continue
        if line.startswith('|') and i+1<len(lines) and re.match(r'^\|?[\s:|-]+\|',lines[i+1]):
            close_lists(); headers=[c.strip() for c in line.strip('|').split('|')]; i+=2; rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip('|').split('|')]); i+=1
            out.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+_inline(_zh_heading(x))+'</th>' for x in headers)+'</tr></thead><tbody>')
            for r in rows: out.append('<tr>'+''.join('<td>'+_inline(r[j] if j<len(r) else '')+'</td>' for j in range(len(headers)))+'</tr>')
            out.append('</tbody></table></div>'); continue
        m=re.match(r'^(#{1,6})\s+(.*)$',line)
        if m:
            close_lists(); lvl=len(m.group(1)); title=m.group(2).strip(); zh=_zh_heading(title)
            secondary='' if zh==title or _has_cjk(title) else f'<span class="heading-en">{html.escape(title)}</span>'
            out.append(f'<h{lvl} id="{_slug(title)}">{_inline(zh)}{secondary}</h{lvl}>'); i+=1; continue
        if line.startswith('- '):
            if in_ol: out.append('</ol>'); in_ol=False
            if not in_ul: out.append('<ul>'); in_ul=True
            out.append('<li>'+_inline(line[2:])+'</li>'); i+=1; continue
        om=re.match(r'^\d+\.\s+(.*)$',line)
        if om:
            if in_ul: out.append('</ul>'); in_ul=False
            if not in_ol: out.append('<ol>'); in_ol=True
            out.append('<li>'+_inline(om.group(1))+'</li>'); i+=1; continue
        close_lists()
        if line.startswith('> '): out.append('<blockquote>'+_inline(line[2:])+'</blockquote>')
        elif line.strip()=='---': out.append('<hr>')
        elif line.strip(): out.append('<p>'+_inline(line.strip())+'</p>')
        i+=1
    close_lists()
    if in_code: out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>')
    return '\n'.join(out)


def _first_heading(text:str,fallback:str)->str:
    for line in text.splitlines():
        if line.startswith('# '): return line[2:].strip()
    return fallback


def _split_h2(text:str)->tuple[str,list[tuple[str,str]]]:
    title=_first_heading(text,''); body=re.sub(r'^# .*$','',text,count=1,flags=re.M).strip(); matches=list(re.finditer(r'^##\s+(.+)$',body,flags=re.M))
    if not matches:return title,[('完整内容',body)] if body else []
    chunks=[]; pre=body[:matches[0].start()].strip()
    if pre:chunks.append(('概览',pre))
    for idx,m in enumerate(matches):
        start=m.end(); end=matches[idx+1].start() if idx+1<len(matches) else len(body); chunks.append((m.group(1).strip(),body[start:end].strip()))
    return title,chunks


def _hex_luminance(value:str)->float:
    value=value.lstrip('#')
    if len(value)!=6:return .5
    try:rgb=[int(value[i:i+2],16)/255 for i in (0,2,4)]
    except Exception:return .5
    def lin(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
    r,g,b=map(lin,rgb);return .2126*r+.7152*g+.0722*b


def _theme_from_project(package_dir:Path)->dict[str,str]:
    texts=[]
    for p in list(package_dir.rglob('*.md'))[:100]:
        if any(k in p.name.upper() for k in ['VISUAL','STRATEGY','CMF','BRAND','PRODUCT']):texts.append(_read(p))
    hexes=[]
    for t in texts:
        for h in re.findall(r'#[0-9A-Fa-f]{6}\b',t):
            h=h.upper()
            if h not in hexes:hexes.append(h)
    dark=[h for h in hexes if _hex_luminance(h)<.32];mid=[h for h in hexes if .18<=_hex_luminance(h)<=.68];light=[h for h in hexes if _hex_luminance(h)>.78]
    return {'accent':(dark or mid or ['#23483D'])[0],'accent2':(mid or dark[1:] or ['#718F85'])[0],'paper':(light or ['#F5F4F0'])[0],'ink':'#18211D','muted':'#6A746F','line':'#DEE3DF'}


def _data_uri(path:Path,budget:list[int],max_total:int|None=None)->str|None:
    try:
        size=path.stat().st_size
        if max_total is not None and budget[0]+size>max_total:return None
        raw=path.read_bytes();budget[0]+=size;mime=mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        return f'data:{mime};base64,'+base64.b64encode(raw).decode('ascii')
    except Exception:return None


def _fallback_center(package_dir:Path)->dict[str,Any]:
    manifest=_read_json(package_dir/'asset_manifest.json',{});copy=[]
    listing=next(iter(sorted(package_dir.glob('*LISTING*.md'))),None)
    if listing:
        _,chunks=_split_h2(_read(listing))
        for label,value in chunks:
            if value:copy.append({'label':_zh_heading(label),'field':_slug(label),'value':value,'status':'READY','copyable':True})
    if not any(x.get('field')=='platform_category' for x in copy):copy.insert(0,{'label':'平台对应类目','field':'platform_category','value':None,'status':'待查证','copyable':False})
    assets=[]
    for a in manifest.get('assets') or []:assets.append({'asset_id':a.get('asset_id') or a.get('id'),'title':a.get('title'),'surface':a.get('surface'),'role':a.get('role') or a.get('title'),'status':a.get('status') or 'PLANNED'})
    return {'version':'legacy','delivery_language':{'locale':'zh-CN'},'target':{'market':manifest.get('market'),'platform':manifest.get('platform'),'delivery_locale':'zh-CN'},'product':{'product_name':manifest.get('project')},'copy_center':copy,'localized_copy':[],'media_slots':assets,'risks_and_holds':[]}


def _center(package_dir:Path)->dict[str,Any]:
    for p in [package_dir/'HUMAN_DELIVERY.json',package_dir/'supporting_analysis/HUMAN_DELIVERY.json',package_dir/'LISTING_UPLOAD_CENTER.json']:
        if p.exists():return _read_json(p,{})
    return _fallback_center(package_dir)


def _classify_doc(path:Path)->str:
    n=path.name.upper();rel=str(path).upper()
    if 'PRODUCT_TRUTH' in n or 'PRODUCT FACT' in n:return 'product'
    if any(k in n for k in ['MARKET','PLATFORM_STRATEGY','AUDIENCE','CULTURE']):return 'market'
    if 'LISTING' in n or 'UPLOAD_READY' in n:return 'listing'
    if any(k in n for k in ['VISUAL','PHOTOGRAPHY','CMF','CURATION']):return 'visual'
    if 'MASTER_STRATEGY_CN' in n:return 'master'
    if any(k in n for k in ['CONTENT_SYSTEM','CONTENT_MATRIX','CONTENT_PLAN','CREATOR_CONTENT','SOCIAL_CONTENT']):return 'content'
    if any(k in n for k in ['STRATEGY_MASTER','MARKETING']):return 'strategy'
    if any(k in n for k in ['RISK','COMPLIANCE','AUDIT','HOLD']):return 'risk'
    if 'SOURCE' in n or 'EVIDENCE' in n:return 'sources'
    if '/ASSETS/' in rel or '/ASSET_PACKAGES/' in rel:return 'asset'
    return 'archive'


def _split_h3_body(body:str)->list[tuple[str,str]]:
    matches=list(re.finditer(r'^###\s+(.+)$',body,flags=re.M))
    if not matches:return []
    out=[];pre=body[:matches[0].start()].strip()
    if pre:out.append(('概览',pre))
    for i,m in enumerate(matches):
        start=m.end();end=matches[i+1].start() if i+1<len(matches) else len(body)
        out.append((m.group(1).strip(),body[start:end].strip()))
    return [(a,b) for a,b in out if b.strip()]


def _master_strategy_views(path:Path,package_dir:Path)->dict[str,list[dict[str,str]]]:
    out={'overview':[],'product':[],'market':[],'strategy':[],'content':[],'visual':[],'risk':[]}
    if not path or not path.exists():return out
    _,chunks=_split_h2(_read(path))
    for i,(name,body) in enumerate(chunks):
        n=str(name).strip()
        # FULL human headings deliberately have no numeric workflow prefix. Route by semantic domain so
        # the SaaS workspace stays object-based while the nine-domain completion contract remains visible.
        if re.match(r'^1[.、\s]',n) or '信息完整度' in n:bucket='overview'
        elif re.match(r'^2[.、\s]',n) or '产品真实事实审计' in n or '产品真相与价值' in n:bucket='product'
        elif re.match(r'^3[.、\s]',n) or re.match(r'^8[.、\s]',n) or '平台 × 区域 × 人群 × 族裔文化' in n or '族裔文化适配检查表' in n:bucket='market'
        elif re.match(r'^5[.、\s]',n) or '视觉总策略与拍摄执行清单' in n:bucket='visual'
        elif re.match(r'^[67][.、\s]',n) or '分平台内容矩阵表' in n or 'RACE传播框架执行表' in n:bucket='content'
        elif re.match(r'^9[.、\s]',n) or '合规、文化敏感与风险清单' in n:bucket='risk'
        else:bucket='strategy'
        domain_label=_zh_heading(n)
        sub=_split_h3_body(body)
        # Long chapters become task cards, but the parent decision domain is never discarded.
        if len(sub)>=2:
            for j,(subname,subbody) in enumerate(sub):
                subtitle=_zh_heading(subname)
                key=f'master-{i}-{j}-{_slug(subname)}'
                banner=f'<div class="strategy-domain-label"><span>完整交付域</span><b>{html.escape(domain_label)}</b></div>'
                title=domain_label if j==0 else subtitle
                secondary=subtitle if j==0 else domain_label
                out[bucket].append({'key':key,'title':title,'secondary':secondary,'html':banner+markdown_to_html(subbody),'source':str(path.relative_to(package_dir)).replace('\\','/')})
        else:
            key=f'master-{i}-{_slug(n)}'
            out[bucket].append({'key':key,'title':domain_label,'secondary':'','html':markdown_to_html(body),'source':str(path.relative_to(package_dir)).replace('\\','/')})
    return out


def _doc_views(paths:list[Path],package_dir:Path,module_id:str)->list[dict[str,str]]:
    views=[]
    for p in paths:
        text=_read(p);doc_title=_first_heading(text,p.stem);_,chunks=_split_h2(text)
        if not chunks:chunks=[('完整内容',text)]
        for j,(section,body) in enumerate(chunks):
            if not body.strip():continue
            title=_zh_heading(section if len(chunks)>1 else doc_title)
            secondary=''
            original=section if len(chunks)>1 else doc_title
            if title==original and not _has_cjk(original):secondary=original
            key=f'{module_id}-{_slug(p.stem)}-{j}'
            views.append({'key':key,'title':title,'secondary':secondary,'html':markdown_to_html(body),'source':str(p.relative_to(package_dir)).replace('\\','/')})
    return views


def _module_workspace(views:list[dict[str,str]],module_id:str,empty='暂无内容')->str:
    if not views:return f'<div class="empty">{html.escape(empty)}</div>'
    tabs=[];panes=[]
    for i,v in enumerate(views):
        tabs.append(f'''<button class="subnav-btn {'active' if i==0 else ''}" data-module="{module_id}" data-view="{html.escape(v['key'])}"><span>{html.escape(v['title'])}</span>{f'<small>{html.escape(v["secondary"])}</small>' if v.get('secondary') else ''}</button>''')
        panes.append(f'''<article class="subview {'active' if i==0 else ''} searchable" data-module="{module_id}" data-view="{html.escape(v['key'])}">{v['html']}</article>''')
    return f'''<div class="module-shell"><aside class="module-nav">{''.join(tabs)}</aside><div class="module-stage">{''.join(panes)}</div></div>'''


def _view_source(v:dict[str,str])->str:
    src=str(v.get('source') or '').strip()
    return f'<small>{html.escape(src)}</small>' if src else ''


def _strategy_workspace(views:list[dict[str,str]])->str:
    if not views:return '<div class="empty">本项目没有策略内容。</div>'
    cards=[]
    for i,v in enumerate(views,1):
        cards.append(f'''<details class="strategy-decision searchable" {'open' if i==1 else ''}>
          <summary><span class="strategy-index">{i:02d}</span><div><b>{html.escape(v['title'])}</b>{f'<small>{html.escape(v["secondary"])}</small>' if v.get('secondary') else ''}</div><span class="strategy-open">展开决策</span></summary>
          <div class="strategy-body">{v['html']}<div class="ia-source">{_view_source(v)}</div></div>
        </details>''')
    return f'<div class="strategy-board" data-workspace-kind="strategy"><div class="strategy-map-head"><b>决策地图</b><span>{len(views)} 个动态策略主题 · 按决策阅读，不按报告顺序阅读</span></div>{"".join(cards)}</div>'


def _content_workspace(views:list[dict[str,str]])->str:
    if not views:return '<div class="empty">本项目没有独立内容策划内容。</div>'
    lanes=[]
    for i,v in enumerate(views,1):
        lanes.append(f'''<article class="content-lane searchable" data-content-view="{html.escape(v['key'])}">
          <header><span>{i:02d}</span><div><h3>{html.escape(v['title'])}</h3>{f'<small>{html.escape(v["secondary"])}</small>' if v.get('secondary') else ''}</div></header>
          <div class="content-lane-body">{v['html']}</div><footer>{_view_source(v)}</footer>
        </article>''')
    return f'''<div class="content-board" data-workspace-kind="content"><div class="content-board-head"><div><b>内容系统</b><span>内容主题由当前策略与平台需要动态产生，不预设固定资产数量。</span></div><strong>{len(views)}</strong></div><div class="content-lanes">{"".join(lanes)}</div></div>'''


def _visual_workspace(views:list[dict[str,str]])->str:
    if not views:return '<div class="empty">本项目没有视觉 / 摄影内容。</div>'
    group='visual-studio';selectors=[];panels=[]
    for i,v in enumerate(views):
        selectors.append(f'''<button class="visual-thumb workspace-switch {'active' if i==0 else ''}" data-switch-group="{group}" data-view="{html.escape(v['key'])}"><span>{i+1:02d}</span><b>{html.escape(v['title'])}</b>{f'<small>{html.escape(v["secondary"])}</small>' if v.get('secondary') else ''}</button>''')
        panels.append(f'''<article class="visual-inspector searchable workspace-panel {'active' if i==0 else ''}" data-switch-group="{group}" data-view="{html.escape(v['key'])}"><div class="visual-inspector-bar"><span>视觉方向 / 执行检查器</span>{_view_source(v)}</div>{v['html']}</article>''')
    return f'''<div class="visual-studio" data-workspace-kind="visual"><div class="visual-contact-sheet">{"".join(selectors)}</div><div class="visual-stage">{"".join(panels)}</div></div>'''


def _evidence_workspace(media:list[str], doc_views:list[dict[str,str]], source_files:list[str])->str:
    if not media and not doc_views and not source_files:return '<div class="empty">暂无来源内容。</div>'
    parts=['<div class="evidence-center" data-workspace-kind="evidence">']
    if media:
        parts.append(f'<section class="evidence-zone evidence-media"><header><div><span>01</span><h2>产品 / 来源媒体</h2></div><strong>{len(media)}</strong></header><div class="media-grid">{"".join(media)}</div></section>')
    if doc_views:
        docs=[]
        for i,v in enumerate(doc_views,1):
            docs.append(f'<details class="evidence-doc searchable" {"open" if i==1 else ""}><summary><span>{i:02d}</span><b>{html.escape(v["title"])}</b>{_view_source(v)}</summary><div class="evidence-doc-body">{v["html"]}</div></details>')
        parts.append(f'<section class="evidence-zone evidence-docs"><header><div><span>02</span><h2>证据文档</h2></div><strong>{len(doc_views)}</strong></header>{"".join(docs)}</section>')
    if source_files:
        parts.append(f'<section class="evidence-zone evidence-files"><header><div><span>03</span><h2>来源文件账本</h2></div><strong>{len(source_files)}</strong></header><ul class="source-files">{"".join(source_files)}</ul></section>')
    parts.append('</div>')
    return ''.join(parts)


def _intent_zh(value:Any)->str:
    v=str(value or '').upper()
    mapping={'IDENTIFY':'产品识别','IDENTITY':'产品识别','PROOF':'证据与可信度','USAGE':'使用方式','RELEVANCE':'人群相关性','FIT':'适配 / 合适度','SCALE':'尺寸与尺度','MATERIAL':'材质表现','CONTENTS':'包装与包含物','COMPATIBILITY':'兼容关系','CARE':'护理 / 维护','OBJECTION':'异议消除','RISK':'风险降低','BENEFIT':'核心利益','HERO':'主视觉','PRIMARY':'主视觉'}
    for k,z in mapping.items():
        if k in v:return z
    return '决策资产'


def _intent_question_zh(intent:Any, fallback:Any='')->str:
    table={
      'IDENTIFY':'这是什么产品？我实际会收到什么？','RELEVANCE':'它与我的真实需求 / 日常场景有什么关系？',
      'PROOF':'有哪些可验证事实支持这个选择？','USAGE':'应该如何正确使用？如何进入日常流程？',
      'FIT_WEAR':'它是否适合我的使用 / 穿着 / 搭配场景？','SIZE_FIT':'尺寸 / 比例 / 适配关系是什么？',
      'MATERIAL_SENSORY':'材质、质地或触感应该如何理解？','INGREDIENT_COMPOSITION':'配方 / 成分事实是什么？',
      'PERFORMANCE_PROOF':'有哪些可验证的性能证据？','EXPECTATION_BOUNDARY':'购买前必须明确哪些边界，避免错误预期？',
      'CONTENTS':'包装里到底包含什么？','COMPATIBILITY':'兼容 / 适配边界是什么？','CARE':'如何护理、储存或维护？',
      'DECISION_SUPPORT':'这张资产要帮助消费者完成什么具体购买判断？'
    }
    return table.get(str(intent or '').upper(), str(fallback or '') if _has_cjk(fallback) else '这张资产要帮助消费者完成什么具体购买判断？')


def _humanize_asset_text(value:Any)->Any:
    if value in (None,'',[],{}): return value
    if isinstance(value,list): return [_humanize_asset_text(v) for v in value]
    if isinstance(value,dict): return { _zh_heading(k):_humanize_asset_text(v) for k,v in value.items() }
    raw=str(value)
    if _has_cjk(raw): return raw
    exact={
      'Use the supplied real-product master as the product subject':'以用户提供的真实商品母版作为商品主体',
      'Resolve the named shopper decision with one clearly visible information relationship.':'用一个清晰可见的信息关系解决当前购买问题。',
      'Make product identity and the primary proposition recoverable at first scan.':'让消费者第一眼识别商品身份与第一购买理由。',
      'Only mechanism-relevant scale/use/evidence/context objects; no decorative prop kit.':'只使用与机理、尺度、使用、证据或语境直接相关的道具；不放装饰性道具套件。',
      'minimal category cue':'最小化品类语境，只保留识别所需线索',
      'specific use context':'具体真实使用语境',
      'product-dominant identity field':'产品主导的身份识别画面',
      'context-led relevance frame':'语境主导的相关性画面',
      'evidence-led proof frame':'证据主导的证明画面',
      'front/3Q label-readable view':'正面 / 三分之四视角，保证标签可读',
      'human/object/environment relationship':'人物 / 商品 / 环境关系视角',
      'NATIVE_ACTION_CENTERED_OBJECT_STUDY':'原生动作中心的商品研究式构图',
      'LEFT_WEIGHTED':'左侧重心构图',
      'RIGHT_WEIGHTED':'右侧重心构图',
      'CENTERED':'中心构图',
      'REQUIRED':'必须', 'OPTIONAL':'可选', 'FORBIDDEN':'禁止', 'PRESENT':'出现', 'RESOLVE_PER_BLUEPRINT':'按蓝图决定',
      'IMAGE':'图片','VIDEO':'视频','HYBRID':'混合表达','MEDIUM':'中等','LOW_TO_MEDIUM':'低到中等','HIGH':'高',
    }
    if raw in exact:return exact[raw]
    # Keep compact technical tokens intact. Long prose must not silently become the Chinese primary layer.
    if len(raw)<=42 or re.search(r'\b(?:mm|ISO|f/|K\b|EV\b|CTR\b|CVR\b|PDP\b|RACE\b|CMF\b|RGB\b|HEX\b)',raw,re.I): return raw
    return '原始生产参数（英文）：“'+raw+'”'


def _human_kv(rows:list[tuple[str,Any]], *, cls:str='design-grid')->str:
    cards=[]
    for label,value in rows:
        if value in (None,'',[],{}): continue
        value=_humanize_asset_text(value)
        if isinstance(value,(dict,list)): value=json.dumps(value,ensure_ascii=False,indent=2)
        cards.append(f'<div class="human-kv"><span>{html.escape(label)}</span><div>{html.escape(str(value))}</div></div>')
    return f'<div class="{cls}">'+''.join(cards)+'</div>' if cards else '<div class="empty">暂无已确认内容。</div>'


def _formal_asset_dir(path:Path,package_dir:Path)->dict[str,Any]:
    aid=path.name;manifest={};yamlp=path/'00_asset_manifest.yaml';design=_read_json(path/'12_design_card.json',{});prompt_contract=_read_json(path/'13_prompt_contract.json',{});visible_copy_block=_read_json(path/'14_visible_copy_block.json',{});production_notes=_read_json(path/'15_production_assembly_notes.json',{});closure=prompt_contract.get('production_parameter_closure') or {};art=design.get('agent_art_direction') or {}
    if yamlp.exists():
        raw=_read(yamlp)
        for key in ['asset_name','surface','decision_intent','consumer_question','asset_type','production_mode','variant_id','variant_cluster','deployment_state','test_hypothesis','activation_set_id']:
            m=re.search(rf'^{key}:\s*(.+)$',raw,flags=re.M)
            if m:manifest[key]=m.group(1).strip().strip('"\'')
    # Prefer structured Design Card fields over parsing YAML when available.
    original_title=design.get('asset_name') or manifest.get('asset_name') or aid
    intent=design.get('commerce_task',{}).get('decision_intent') or manifest.get('decision_intent')
    surface=design.get('surface') or manifest.get('surface')
    asset_type=design.get('asset_type') or manifest.get('asset_type')
    display_title=original_title if _has_cjk(original_title) else _intent_zh(intent)
    prompt_cn='';prompt_en='';src=[]
    for f in sorted(path.iterdir()):
        if not f.is_file(): continue
        src.append(str(f.relative_to(package_dir)).replace('\\','/'))
        if f.name=='05_prompt_CN.txt': prompt_cn=_read(f).strip()
        elif f.name=='06_prompt_EN.txt': prompt_en=_read(f).strip()

    views=[]
    if design:
        commerce=design.get('commerce_task') or {}; narrative=design.get('visual_narrative') or {}; subject=design.get('subject_action_environment_props') or {}; comp=design.get('composition_camera') or {}; light=design.get('lighting_material_cmf') or {}; info=design.get('information_design') or {}; copyc=design.get('copy_language') or design.get('copy') or info.get('locked_visible_copy') or {}; product_role=design.get('product_presence') or design.get('product_role') or {}; surfacec=design.get('surface_contract') or design.get('surface_native_contract') or {}; identity=design.get('product_identity') or {}; editability=design.get('editable_layer_contract') or {}
        qzh=_intent_question_zh(intent,commerce.get('consumer_question'))
        overview='<div class="design-card-hero"><div class="design-question"><span>消费者要确认的问题</span><h2>'+html.escape(qzh)+'</h2>'+(f'<small>原始目标问题：{html.escape(str(commerce.get("consumer_question")))}</small>' if commerce.get('consumer_question') and not _has_cjk(commerce.get('consumer_question')) else '')+'</div>'+_human_kv([
          ('为什么必须有这张资产',commerce.get('reason_to_exist')),('购买障碍',commerce.get('purchase_barrier')),('进入状态',commerce.get('entry_state')),('目标信念',commerce.get('target_belief')),('退出状态',commerce.get('exit_state')),('新增信息',commerce.get('incremental_information')),('画面必须传达',narrative.get('what_must_be_visible') or design.get('visual_objective')),('成功指标',commerce.get('success_metric')),('后续承接',commerce.get('handoff'))
        ])+'</div>'
        views.append({'key':'overview','title':'资产概览','html':overview})
        strategy=_human_kv([
          ('消费者问题',qzh),('决策意图',_intent_zh(intent)),('购买障碍',commerce.get('purchase_barrier')),('信念转变',narrative.get('belief_transition')),('战略任务',commerce.get('strategic_job') if _has_cjk(commerce.get('strategic_job')) else commerce.get('reason_to_exist')),('为什么存在',commerce.get('reason_to_exist')),('新增信息价值',commerce.get('incremental_information')),('成功指标',commerce.get('success_metric'))
        ])
        views.append({'key':'strategy','title':'策划与决策','html':strategy})
        visual=_human_kv([
          ('视觉载体',art.get('visual_carrier') or design.get('visual_carrier')),('创意核心',art.get('creative_thesis') or art.get('thesis')),('视觉语言',art.get('visual_language') or art.get('image_language') or art.get('style')),('决策关键瞬间',art.get('decisive_moment') or design.get('decisive_moment') or narrative.get('decisive_moment')),('画面必须可见',narrative.get('what_must_be_visible')),('主体',art.get('subject') or subject.get('subject')),('动作',art.get('action') or art.get('decisive_action') or subject.get('action')),('环境',art.get('environment') or subject.get('environment')),('道具',art.get('props') or art.get('scene_props') or subject.get('props')),('人物 / Casting',art.get('human_context') or art.get('people') or art.get('casting') or subject.get('human_context')),('构图语法',art.get('composition_grammar') or art.get('composition') or comp.get('composition_grammar')),('空间节奏',art.get('spatial_rhythm') or comp.get('spatial_rhythm')),('相对位置 / 几何',art.get('layout_geometry') or art.get('relative_placement') or art.get('placement_relationships')),('尺度 / 纵深',art.get('scale_depth') or art.get('scale_relationships') or art.get('depth_program')),('产品占画',art.get('product_occupancy') or art.get('product_frame_ratio') or art.get('product_scale_percent')),('焦点路径',art.get('focal_path')),('负空间',art.get('negative_space') or art.get('copy_negative_space')),('证据层级',art.get('evidence_hierarchy') or art.get('proof_mechanism') or art.get('evidence_plane')),('文字安全区',art.get('copy_zone') or art.get('text_zone') or art.get('safe_zone')),('字体 / 信息层级',art.get('typography')),('视角 / 机位',art.get('camera_or_view') or comp.get('camera_or_view')),('产品出现方式',art.get('product_presence') or ((product_role.get('production_resolution') or product_role.get('planning_state')) if isinstance(product_role,dict) else product_role)),('商品保真模式',identity.get('product_fidelity')),('输出规格',art.get('output_spec') or art.get('canvas') or art.get('format_spec')),('完成质感 / Post Look',art.get('post_look') or art.get('grade') or art.get('finishing_look')),('相邻资产差异 / Deliberate Delta',art.get('deliberate_difference') or art.get('adjacent_asset_delta') or art.get('differentiation_axis') or art.get('why_different_from_adjacent')),('设计 WHY',art.get('why') or art.get('design_why') or art.get('art_direction_why')),('允许进入画面的视觉元素',design.get('approved_visual_elements')),('精确执行边界',design.get('precision_boundaries')),('可编辑层',editability.get('editable_layers')),('冻结层',editability.get('frozen_layers')),('局部修订规则',editability.get('revision_rule')),('展示位置（Surface）',surface),('信息表达方式',(surfacec.get('representation') if isinstance(surfacec,dict) else None)),('文案密度',(surfacec.get('copy_budget') or {}).get('density_class') if isinstance(surfacec,dict) else None),('移动端扫描原则','第一眼只承载一个主要购买答案；次级解释移到相邻原生内容位。' if isinstance(surfacec,dict) and surfacec else None)
        ])
        views.append({'key':'visual','title':'画面与版式','html':visual})
        photo_exec=design.get('photography_execution') or {}
        photo_rows=[
          ('拍摄 / 合成模式',photo_exec.get('capture_mode') or art.get('production_route')),('构图执行合同',photo_exec.get('composition')),('输出色彩管理',art.get('color_management') or photo_exec.get('color_management') or (closure.get('selected_parameters') or {}).get('color_management')),
          ('焦段',art.get('focal_length_mm') or art.get('focal_length') or art.get('lens') or comp.get('focal_length_mm') or (closure.get('selected_parameters') or {}).get('focal_length')),('镜头家族',art.get('lens_family') or comp.get('lens_family') or (closure.get('selected_parameters') or {}).get('lens_family')),('工作距离',art.get('working_distance') or art.get('working_distance_intent') or (closure.get('selected_parameters') or {}).get('working_distance')),('透视 / 投影',art.get('perspective') or art.get('projection')),('机位高度',art.get('camera_height') or comp.get('camera_height') or (closure.get('selected_parameters') or {}).get('camera_height')),('Yaw / Pitch / Roll',art.get('yaw_pitch_roll') or art.get('orientation') or (closure.get('selected_parameters') or {}).get('yaw_pitch_roll')),('景别 / 裁切',art.get('shot_size') or art.get('framing') or (closure.get('selected_parameters') or {}).get('shot_size')),('机位参数',art.get('camera_position')),('方位角',comp.get('azimuth')),('俯仰 / 高度',comp.get('elevation')),
          ('对焦平面',art.get('focus_plane') or comp.get('focus_plane') or (closure.get('selected_parameters') or {}).get('focus_plane')),('光圈 / 景深',art.get('aperture') or art.get('focus_dof') or comp.get('aperture_dof_intent') or (closure.get('selected_parameters') or {}).get('aperture_dof')),('快门起点',art.get('shutter') or art.get('shutter_speed') or comp.get('shutter_speed') or (closure.get('selected_parameters') or {}).get('shutter')),('ISO 起点',art.get('iso') or comp.get('iso') or (closure.get('selected_parameters') or {}).get('iso')),
          ('灯光方案',art.get('lighting') or art.get('lighting_program')),('主光',art.get('key_light') or light.get('key') or (closure.get('selected_parameters') or {}).get('key_light')),('补光',art.get('fill_light') or light.get('fill') or (closure.get('selected_parameters') or {}).get('fill_light')),('负补光',art.get('negative_fill') or light.get('negative_fill') or (closure.get('selected_parameters') or {}).get('negative_fill')),('轮廓光',art.get('rim_light') or light.get('rim') or (closure.get('selected_parameters') or {}).get('rim_light')),('控光附件 / Modifier',art.get('modifier_geometry') or (closure.get('selected_parameters') or {}).get('modifier_geometry')),('灯距',art.get('light_distance') or (closure.get('selected_parameters') or {}).get('light_distance')),('色温',art.get('cct') or light.get('cct') or (closure.get('selected_parameters') or {}).get('cct')),('白平衡',art.get('white_balance') or light.get('white_balance') or (closure.get('selected_parameters') or {}).get('white_balance')),('光比 / 曝光关系',art.get('light_ratio') or ((art.get('lighting') or {}).get('exposure_ratio_plan') if isinstance(art.get('lighting'),dict) else None) or (closure.get('selected_parameters') or {}).get('light_ratio')),('曝光 / 测光策略',art.get('exposure_policy') or (closure.get('selected_parameters') or {}).get('exposure_policy')),('阴影策略',art.get('shadow_policy') or light.get('shadow') or (closure.get('selected_parameters') or {}).get('shadow_policy')),('高光策略',art.get('highlight_policy') or light.get('highlight_policy') or (closure.get('selected_parameters') or {}).get('highlight_policy')),('反射控制',art.get('reflection_control') or (closure.get('selected_parameters') or {}).get('reflection_control')),('偏振',art.get('polarization') or light.get('polarization_plan') or (closure.get('selected_parameters') or {}).get('polarization')),('Prelight',art.get('prelight') or art.get('prelight_plan') or light.get('prelight_plan') or (closure.get('selected_parameters') or {}).get('prelight')),
          ('CMF',art.get('cmf') or art.get('material_program') or light.get('cmf') or (closure.get('selected_parameters') or {}).get('cmf')),('材质响应',art.get('material_response') or art.get('surface_behavior') or light.get('material_response_to_show') or (closure.get('selected_parameters') or {}).get('material_response')),('Palette / HEX',art.get('palette_hex') or art.get('palette') or art.get('color_world') or (closure.get('selected_parameters') or {}).get('palette_hex')),('肤色曝光 / 包容性',art.get('skin_tone_exposure') or (closure.get('selected_parameters') or {}).get('skin_tone_exposure')),('服装 / 发型 / 妆发',art.get('wardrobe_hair_makeup') or (closure.get('selected_parameters') or {}).get('wardrobe_hair_makeup')),('色彩一致性',light.get('color_consistency_plan'))
        ]
        if any(v not in (None,'',[],{}) for _,v in photo_rows):
            views.append({'key':'photo','title':'摄影 / CMF','html':_human_kv(photo_rows)})
        effective_copy=visible_copy_block or copyc
        if effective_copy:
            views.append({'key':'copy','title':'可见文案','html':_human_kv([('目标市场可见文案',effective_copy.get('target_market_copy') if isinstance(effective_copy,dict) else effective_copy),('次级文案',effective_copy.get('secondary_copy') if isinstance(effective_copy,dict) else None),('中文释义 / 用途',effective_copy.get('delivery_translation_zh') if isinstance(effective_copy,dict) else None),('文字渲染 / 装配路线',production_notes.get('copy_render_mode')),('文案预算',(effective_copy.get('copy_budget') if isinstance(effective_copy,dict) else None) or info.get('copy_budget')),('字体方向',(effective_copy.get('typography_direction') if isinstance(effective_copy,dict) else None) or info.get('typography'))])})
        if production_notes or closure:
            views.append({'key':'production','title':'生产 / 装配说明','html':_human_kv([('文字渲染路线',production_notes.get('copy_render_mode')),('产品 Fidelity',production_notes.get('product_fidelity')),('商品参考生成方式',production_notes.get('product_reference_generation_mode')),('真实商品 Reference Input',production_notes.get('reference_input_required')),('最终商品必须原生生成',production_notes.get('final_output_must_contain_generated_product')),('产品出现方式',production_notes.get('product_presence')),('产品参考规则',production_notes.get('product_reference_rule')),('可编辑层',production_notes.get('editable_layers')),('冻结层',production_notes.get('frozen_layers')),('局部修订规则',production_notes.get('revision_rule')),('Provider / Route',production_notes.get('provider_route')),('装配原则',production_notes.get('assembly_principle')),('参数闭环状态',closure.get('status')),('生产路线判定',closure.get('route')),('已选择且必须消费的执行参数',closure.get('selected_parameters')),('缺失执行参数',closure.get('missing_required_parameters')),('英文执行语义缺口',closure.get('english_render_semantics_missing_for')),('锁图复合底片闭环',closure.get('locked_source_final_composite_instruction'))])})
    # Human-facing Markdown files remain useful, but machine YAML/JSON is never the default asset view.
    group_files={'strategy':[],'visual':[],'photo':[],'copy':[],'production':[],'trace':[]}
    for f in sorted(path.iterdir()):
        if not f.is_file() or f.name in {'05_prompt_CN.txt','06_prompt_EN.txt','14_visible_copy_block.json','15_production_assembly_notes.json'}: continue
        raw=_read(f);name=f.name.lower();ext=f.suffix.lower()
        if f.name in {'00_asset_manifest.yaml','12_design_card.json','13_prompt_contract.json'} or 'trace' in name or 'contract' in name or ext in {'.json','.yaml','.yml'}:
            grp='trace'
        elif name.startswith('01_') or 'strategy' in name: grp='strategy'
        elif name.startswith('02_') or 'visual' in name or 'layout' in name: grp='visual'
        elif name.startswith('03_') or 'photo' in name or 'cmf' in name: grp='photo'
        elif name.startswith('08_') or 'copy' in name: grp='copy'
        else: grp='production'
        if ext=='.md': body=markdown_to_html(raw)
        elif ext in {'.json','.yaml','.yml','.txt'}: body=f'<pre><code>{html.escape(raw)}</code></pre>'
        else: continue
        # Structured human Design Card owns strategy/visual/photo first. Keep duplicate raw files in trace.
        if design and grp in {'strategy','visual','photo'} and ext!='.md': grp='trace'
        group_files[grp].append(f'<div class="asset-file"><div class="file-label">{html.escape(f.name)}</div>{body}</div>')
    existing={v['key'] for v in views}
    labels={'strategy':'策划与决策','visual':'画面与版式','photo':'摄影 / CMF','copy':'文案','production':'生成与生产','trace':'合同 / QA / 来源'}
    for k in ['strategy','visual','photo','copy','production','trace']:
        if not group_files[k]: continue
        if k in existing:
            # Human summary stays first; optional source detail is collapsed inside the same task page.
            target=next(v for v in views if v['key']==k)
            target['html'] += '<details class="source-detail"><summary>查看该页底层文件</summary>'+''.join(group_files[k])+'</details>'
        else:
            views.append({'key':k,'title':labels[k],'html':''.join(group_files[k])})
    summary=' · '.join(str(x) for x in [surface,_intent_zh(intent),qzh if design else manifest.get('consumer_question')] if x)
    return {'id':aid,'title':display_title,'original_title':original_title,'summary':summary,'prompt_cn':prompt_cn,'prompt_en':prompt_en,'model_prompt_status':prompt_contract.get('model_prompt_status'),'views':views,'source_files':src,'surface':surface,'intent':intent,'asset_type':asset_type,'variant_id':design.get('variant_id') or manifest.get('variant_id'),'variant_cluster':design.get('variant_cluster') or manifest.get('variant_cluster'),'deployment_state':design.get('deployment_state') or manifest.get('deployment_state'),'test_hypothesis':design.get('test_hypothesis') or manifest.get('test_hypothesis'),'activation_set_id':design.get('activation_set_id') or manifest.get('activation_set_id'),'agent_view_order':design.get('workspace_view_order') or design.get('agent_view_order') or []}


def _legacy_asset(path:Path,package_dir:Path)->dict[str,Any]:
    text=_read(path);title,chunks=_split_h2(text);title=title or path.stem
    aid_match=re.match(r'^([A-Z]\d{2,4}|ASSET[-_A-Z0-9]+)',path.stem.upper());aid=aid_match.group(1) if aid_match else path.stem
    cn='';en='';views=[]
    for i,(name,body) in enumerate(chunks):
        low=name.lower()
        if ('prompt' in low and ('中文' in name or 'cn' in low)) or '中文 canonical prompt' in low:cn=body;continue
        if ('prompt' in low and ('english' in low or '英文' in name or ' en' in low)) or 'english canonical prompt' in low:en=body;continue
        views.append({'key':f'v{i}','title':_zh_heading(name),'html':markdown_to_html(body)})
    display=title if _has_cjk(title) else f'资产 {aid}'
    return {'id':aid,'title':display,'original_title':title,'summary':chunks[0][1][:420] if chunks else '', 'prompt_cn':cn,'prompt_en':en,'views':views,'source_files':[str(path.relative_to(package_dir)).replace('\\','/')], 'surface':None,'intent':None,'asset_type':None}


def _assets(package_dir:Path)->list[dict[str,Any]]:
    out=[];formal=package_dir/'asset_packages'
    if formal.exists():
        for d in sorted(formal.iterdir()):
            if d.is_dir():out.append(_formal_asset_dir(d,package_dir))
    legacy=package_dir/'assets'
    if legacy.exists():
        known={x['id'] for x in out}
        for p in sorted(legacy.glob('*.md')):
            a=_legacy_asset(p,package_dir)
            if a['id'] not in known:out.append(a)
    for d in sorted(package_dir.glob('artifacts/asset_packages/*')):
        if d.is_dir() and d.name not in {x['id'] for x in out}:out.append(_formal_asset_dir(d,package_dir))
    return out


def _copy_group(field:str)->str:
    f=str(field or '').casefold()
    if f in {'title','product_name','brand','category','category_id','category_path','sku','variant'}:return 'basic'
    if f in {'attributes','ingredients','materials','package','size','specification','specifications'}:return 'spec'
    if f in {'highlights','bullets','description','usage','warnings','faq'}:return 'copy'
    if 'keyword' in f or 'term' in f or f in {'backend_terms','search_terms'}:return 'search'
    if f in {'price','offer','shipping','returns','seller_info'}:return 'commerce'
    return 'other'




def _is_empty(v:Any)->bool:
    return v is None or v=='' or v==[] or v=={}
def _value_html(v:Any)->str:
    if isinstance(v,(dict,list)):return html.escape(json.dumps(v,ensure_ascii=False,indent=2))
    return html.escape('' if v is None else str(v))


def _copy_card(x:dict[str,Any],idx:int)->str:
    v=x.get('value');status=str(x.get('status') or '');loc=str(x.get('locale') or '');delivery=str(x.get('delivery_locale') or 'zh-CN')
    translation=x.get('delivery_translation');note=x.get('delivery_note');foreign=bool(loc and loc.casefold()!=delivery.casefold())
    companion=''
    if foreign and not _is_empty(v):
        if translation not in (None,''):
            companion=f'<div class="cn-companion"><span>中文释义</span><div>{_value_html(translation)}</div>{f"<small>{html.escape(str(note))}</small>" if note else ""}</div>'
        else:
            companion='<div class="cn-companion missing"><span>中文释义</span><div>待补中文释义 / 用途说明</div></div>'
    pid=f'copy-{idx}'
    return f'''<article class="copy-card searchable"><div class="copy-head"><div><small>{html.escape(str(x.get('group') or '上架字段'))}{(' · '+html.escape(loc)) if loc else ''}</small><h3>{html.escape(str(x.get('label') or x.get('field') or ''))}</h3></div><span class="badge {'ready' if status=='READY' else 'hold'}">{html.escape(status)}</span></div><div class="target-copy" id="{pid}">{_value_html(v) if not _is_empty(v) else '<em>—</em>'}</div>{companion}{'<button class="copy-btn" data-copy="'+pid+'">复制目标文案</button>' if not _is_empty(v) else ''}</article>'''


def _listing_workspace(center:dict[str,Any])->str:
    rows=center.get('copy_center') or [];localized=center.get('localized_copy') or [];groups={'basic':[],'spec':[],'copy':[],'search':[],'commerce':[],'other':[]}
    for i,x in enumerate(rows):groups[_copy_group(x.get('field'))].append(_copy_card(x,i))
    labels={'basic':'基础信息','spec':'类目 / 属性 / 规格','copy':'标题与详情文案','search':'搜索与关键词','commerce':'价格 / 履约 / 售后','other':'其他平台字段'}
    views=[]
    for k in ['basic','spec','copy','search','commerce','other']:
        if groups[k]:views.append({'key':f'listing-{k}','title':labels[k],'secondary':'','html':'<div class="copy-grid">'+''.join(groups[k])+'</div>','source':'HUMAN_DELIVERY.json'})
    # Localized view is intentionally separate so target-language copy never replaces Chinese human explanation.
    locale_groups={}
    for r in localized:
        locale_groups.setdefault(str(r.get('locale') or 'unknown'),[]).append(r)
    locale_html=[]
    for loc,lrows in locale_groups.items():
        locale_html.append(f'<div class="locale-block"><h3>{html.escape(loc)} <span class="heading-en">目标市场文案</span></h3>')
        for j,r in enumerate(lrows):
            val=r.get('value');trans=r.get('delivery_translation');comp=''
            if str(loc).casefold()!=str(r.get('delivery_locale') or center.get('delivery_language',{}).get('locale') or 'zh-CN').casefold():
                comp=f'<div class="cn-companion {"" if trans else "missing"}"><span>中文释义 / 用途</span><div>{_value_html(trans) if trans else "待补中文释义；搜索词应解释意图而非机械翻译。"}</div></div>'
            locale_html.append(f'<article class="locale-row"><div class="locale-field"><strong>{html.escape(str(r.get("field") or ""))}</strong><span>{html.escape(str(r.get("status") or ""))}</span></div><div class="target-copy">{_value_html(val)}</div>{comp}</article>')
        locale_html.append('</div>')
    if locale_html:views.append({'key':'listing-locales','title':'多语言 / 中文对照','secondary':'本地化','html':''.join(locale_html),'source':'listing_final_copy.json'})
    if not views:return '<div class="empty">暂无上架字段。</div>'
    tabs=[];panels=[];group='listing-studio'
    for i,v in enumerate(views):
        tabs.append(f'<button class="listing-task workspace-switch {"active" if i==0 else ""}" data-switch-group="{group}" data-view="{html.escape(v["key"])}"><span>{i+1:02d}</span><b>{html.escape(v["title"])}</b></button>')
        panels.append(f'<section class="listing-panel workspace-panel {"active" if i==0 else ""}" data-switch-group="{group}" data-view="{html.escape(v["key"])}"><div class="listing-panel-head"><b>{html.escape(v["title"])}</b><small>{html.escape(v.get("source") or "")}</small></div>{v["html"]}</section>')
    return f'<div class="listing-studio" data-workspace-kind="listing"><div class="listing-tasks">{"".join(tabs)}</div><div class="listing-stage">{"".join(panels)}</div></div>'


def _asset_card(a:dict[str,Any])->str:
    orig=a.get('original_title') or ''
    sec=f'<small>{html.escape(orig)}</small>' if orig and orig!=a.get('title') else ''
    chips=''.join(f'<span>{html.escape(str(_humanize_asset_text(x)))}</span>' for x in [a.get('asset_type'),a.get('surface'),a.get('variant_cluster'),a.get('variant_id'),a.get('deployment_state'),a.get('intent')] if x)
    hypothesis=f'<p><strong>测试 / 创意假设：</strong>{html.escape(str(a.get("test_hypothesis")))}</p>' if a.get('test_hypothesis') else ''
    return f'''<a class="asset-card searchable route-link" href="#asset/{html.escape(a['id'])}" data-route="asset/{html.escape(a['id'])}"><div class="asset-top"><b>{html.escape(a['id'])}</b><div class="asset-chips">{chips}</div></div><h3>{html.escape(a['title'])}</h3>{sec}<p>{html.escape(a.get('summary') or '打开查看完整资产工作区')}</p>{hypothesis}<span class="asset-open">进入资产工作区 →</span></a>'''


def _asset_universe_cards(assets:list[dict[str,Any]])->str:
    if not assets:
        return '<div class="empty">暂无资产。</div>'
    groups=[
      ('LIVE_CANDIDATE','当前上线候选','可进入当前平台 activation set；平台槽位只限制这里同时上线数量。'),
      ('TEST_POOL','测试池','用于 A/B、Hero 方向、卖点、构图、人群与文案假设测试；不受当前平台槽位总数限制。'),
      ('ROTATION_POOL','轮换池','已生产、可按周期或数据表现替换上线的资产。'),
      ('PAID_MEDIA','广告资产','Paid Ads / Retargeting / Hook 等广告创意资产。'),
      ('PDP_CONTENT','PDP / A+ / 详情','A+、详情模块、长图、说明/证据/FAQ 等丰富内容。'),
      ('ARCHIVE','归档','暂不激活但保留用于复盘、复用或历史对照的资产。'),
      ('OTHER','其他资产','Store、Banner、Social、Creator、Video 等按实际 Surface 使用的资产。'),
    ]
    buckets={k:[] for k,_,_ in groups}
    for a in assets:
        state=str(a.get('deployment_state') or '').upper()
        if state not in buckets:
            surface=str(a.get('surface') or '').upper()
            if surface=='PAID_AD': state='PAID_MEDIA'
            elif surface in {'A_PLUS','LONGFORM'}: state='PDP_CONTENT'
            elif surface in {'STORE_BANNER','SOCIAL_CONTENT','CREATOR','SHORT_VIDEO','PDP_VIDEO','LIVE'}: state='OTHER'
            else: state='LIVE_CANDIDATE'
        buckets[state].append(a)
    out=[]
    for key,title,desc in groups:
        rows=buckets[key]
        if not rows: continue
        out.append(f'<section class="panel asset-universe-group"><div class="page-head"><div><span class="kicker">ASSET UNIVERSE · {html.escape(key)}</span><h2>{html.escape(title)} · {len(rows)}</h2><p>{html.escape(desc)}</p></div></div><div class="asset-grid">'+''.join(_asset_card(a) for a in rows)+'</div></section>')
    return ''.join(out)

def _prompt_workspace(assets:list[dict[str,Any]])->str:
    if not assets:return '<div class="empty">暂无可执行提示词。</div>'
    selectors=[];panels=[];group='prompt-lab'
    for i,a in enumerate(assets):
        key=f'prompt-{_slug(a["id"])}'
        selectors.append(f'<button class="prompt-asset-switch workspace-switch {"active" if i==0 else ""}" data-switch-group="{group}" data-view="{key}"><span>{html.escape(a["id"])}</span><b>{html.escape(a["title"])}</b></button>')
        cn=a.get('prompt_cn') or '中文规范生产提示词 待补。英文生成提示词不能作为唯一的人类交付。';en=a.get('prompt_en') or '英文生成提示词待补。'
        cid=f'{key}-cn';eid=f'{key}-en'
        body=f'''<div class="prompt-workbench"><section class="prompt-primary"><div class="prompt-head"><div><span>直接给生成模型</span><h3>Model Prompt CN｜中文模型提示词</h3></div><button class="copy-btn mini" data-copy="{cid}">复制中文 Prompt</button></div><pre id="{cid}"><code>{html.escape(cn)}</code></pre></section><section class="prompt-secondary"><div class="prompt-head"><div><span>Direct model input</span><h3>Model Prompt EN｜英文模型提示词</h3></div><button class="copy-btn mini" data-copy="{eid}">复制英文 Prompt</button></div><pre id="{eid}"><code>{html.escape(en)}</code></pre></section></div><div class="language-note">这里只展示模型输入。目标市场可见文案与中文释义在“可见文案”对象中管理；锁图、文字装配、可编辑层、Provider 与后期规则在“生产 / 装配说明”中管理，不混入 Model Prompt。</div>'''
        panels.append(f'<article class="prompt-asset-panel searchable workspace-panel {"active" if i==0 else ""}" data-switch-group="{group}" data-view="{key}"><div class="prompt-asset-meta"><b>{html.escape(a["title"])}</b><span>{html.escape(a["id"])}</span></div>{body}</article>')
    return f'<div class="prompt-lab" data-workspace-kind="prompt"><div class="prompt-selector">{"".join(selectors)}</div><div class="prompt-stage">{"".join(panels)}</div></div>'


def _asset_page(a:dict[str,Any])->str:
    raw_views=list(a.get('views') or [])
    by_key={str(v.get('key') or ''):v for v in raw_views if isinstance(v,dict)}
    raw_order=relevant_asset_view_keys(a)
    group=f'asset-workspace-{_slug(a["id"])}'
    lenses={}

    def add(key:str,title:str,eyebrow:str,description:str,body:str):
        if body and body.strip() and '暂无已确认内容' not in body:
            lenses[key]={'key':key,'title':title,'eyebrow':eyebrow,'description':description,'body':body}

    # Decision lens groups the Design Card overview and strategy because they answer one work object,
    # but it is not a first step and carries no execution-order authority.
    decision_parts=[]
    for key,label in [('overview','Design Card 概览'),('strategy','购买决策')]:
        view=by_key.get(key)
        if view and (view.get('html') or '').strip():
            decision_parts.append(f'<section class="asset-decision-block"><div class="asset-section-label">{label}</div>{view.get("html") or ""}</section>')
    if decision_parts:
        add('decision','决策 / Design Card','WHY · DECISION','查看这张资产为什么存在、要解决什么购买判断以及依据。',''.join(decision_parts))

    direct={
        'visual':('画面执行','VISUAL','查看当前资产实际采用的主体、关系、构图与信息层级。'),
        'photo':('摄影 / CMF','PHOTO · CMF','仅显示本资产真正需要的摄影、灯光、材质、CMF 或色彩执行参数。'),
        'copy':('文案','COPY','查看本资产实际承担的目标市场可见文案与中文说明。'),
        'production':('生产 / 装配说明','PRODUCTION','查看锁图、文字装配、图层、Provider 与本资产执行方式直接相关的生产备注。'),
    }
    for key,(title,eyebrow,desc) in direct.items():
        view=by_key.get(key)
        if view:
            add(key,title,eyebrow,desc,view.get('html') or '')

    if a.get('prompt_cn') or a.get('prompt_en'):
        parts=[];aid=_slug(a['id'])
        if a.get('prompt_cn'):
            cid=f'asset-{aid}-prompt-cn'
            parts.append(f'''<section class="prompt-primary"><div class="prompt-head"><div><span>直接给生成模型</span><h3>Model Prompt CN｜中文模型提示词</h3></div><button class="copy-btn mini" data-copy="{cid}">复制中文 Prompt</button></div><pre id="{cid}"><code>{html.escape(a['prompt_cn'])}</code></pre></section>''')
        if a.get('prompt_en'):
            eid=f'asset-{aid}-prompt-en'
            parts.append(f'''<section class="prompt-secondary"><div class="prompt-head"><div><span>Direct model input</span><h3>Model Prompt EN｜英文模型提示词</h3></div><button class="copy-btn mini" data-copy="{eid}">复制英文 Prompt</button></div><pre id="{eid}"><code>{html.escape(a['prompt_en'])}</code></pre></section>''')
        body='<div class="asset-prompt-console"><div class="prompt-workbench">'+''.join(parts)+'</div><div class="language-note">Model Prompt 只承载当前资产真正需要进入生成模型的视觉、空间、摄影 / CMF、动态与文字行为。产品锁定、图层、文字装配、Provider、QA 与修订规则请到“生产 / 装配说明”查看；这些工程合同不进入模型提示词。</div></div>'
        add('prompt','Model Prompt','MODEL INPUT','查看当前资产真正发送给图像 / 视频生成模型的 CN / EN 提示词。',body)

    # QA/trace is one recoverability lens: machine trace, source files and unknown legacy views all remain accessible.
    qa_parts=[]
    trace=by_key.get('trace')
    if trace and (trace.get('html') or '').strip():
        qa_parts.append('<section class="asset-qa-source"><div class="asset-section-label">合同 / 参数追踪</div>'+str(trace.get('html') or '')+'</section>')
    known={'overview','strategy','visual','photo','copy','production','trace'}
    for view in raw_views:
        if not isinstance(view,dict): continue
        key=str(view.get('key') or '')
        if key in known: continue
        body=str(view.get('html') or '').strip()
        if not body: continue
        title=str(view.get('title') or '补充资料')
        qa_parts.append(f'<section class="asset-qa-source"><div class="asset-section-label">{html.escape(title)}</div>{body}</section>')
    source_files=a.get('source_files') or []
    if source_files:
        qa_parts.append('<section class="asset-source-ledger"><div class="asset-section-label">源文件账本</div><ul>'+''.join(f'<li>{html.escape(str(x))}</li>' for x in source_files)+'</ul></section>')
    if qa_parts:
        add('qa','QA / 来源','TRACE · QA','核对事实、参数、机器合同、源文件与兼容性资料；这些追踪信息不进入生成 Prompt。',''.join(qa_parts))

    # Agent-authored order wins. Otherwise use a stable UI reading order only for presentation;
    # absent lenses are never manufactured and this order has no planning/execution authority.
    alias={'overview':'decision','strategy':'decision','trace':'qa','qa':'qa','prompt':'prompt'}
    explicit=list(a.get('agent_view_order') or a.get('workspace_view_order') or [])
    order=[]
    for key in explicit:
        mapped=alias.get(str(key),str(key))
        if mapped in lenses and mapped not in order: order.append(mapped)
    for raw in raw_order:
        mapped=alias.get(str(raw),str(raw))
        if mapped not in lenses and str(raw) not in known and 'qa' in lenses: mapped='qa'
        if mapped in lenses and mapped not in order: order.append(mapped)
    for key in ['decision','visual','photo','copy','production','prompt','qa']:
        if key in lenses and key not in order: order.append(key)

    panels=[lenses[k] for k in order]
    if not panels:
        panels=[{'key':'empty','title':'资产概览','eyebrow':'ASSET','description':'当前资产还没有可执行的人类工作视图。','body':'<div class="empty">暂无资产内容。</div>'}]

    rail=[];stage=[]
    for i,s in enumerate(panels):
        view=f'asset-view-{_slug(a["id"])}-{s["key"]}'
        active='active' if i==0 else ''
        rail.append(f'''<button class="asset-phase workspace-switch {active}" data-switch-group="{group}" data-view="{view}"><span class="asset-phase-copy"><small>{html.escape(s['eyebrow'])}</small><b>{html.escape(s['title'])}</b></span></button>''')
        stage.append(f'''<section class="asset-stage asset-stage-{_slug(s['key'])} workspace-panel searchable {active}" data-switch-group="{group}" data-view="{view}"><header class="asset-stage-head"><div><span>{html.escape(s['eyebrow'])}</span><h2>{html.escape(s['title'])}</h2><p>{html.escape(s['description'])}</p></div></header><div class="asset-stage-body">{s['body']}</div></section>''')

    sec=f'<div class="asset-original">{html.escape(str(a.get("original_title") or ""))}</div>' if a.get('original_title') and a.get('original_title')!=a.get('title') else ''
    chips=''.join(f'<span>{html.escape(str(_humanize_asset_text(x)))}</span>' for x in [a.get('asset_type'),a.get('surface'),a.get('variant_cluster'),a.get('variant_id'),a.get('deployment_state'),a.get('intent')] if x)
    readiness=[]
    if a.get('model_prompt_status'):
        readiness.append('Model Prompt：'+str(a.get('model_prompt_status')))
    else:
        if a.get('prompt_cn'): readiness.append('中文 Model Prompt 已生成')
        if a.get('prompt_en'): readiness.append('英文 Model Prompt 已生成')
    if source_files: readiness.append(f'{len(source_files)} 个源文件可追溯')
    ready_html=''.join(f'<span>{html.escape(x)}</span>' for x in readiness) or '<span>等待当前资产所需合同补齐</span>'
    passport=f'''<div class="asset-passport"><div><span class="asset-passport-id">{html.escape(a['id'])}</span><div class="asset-passport-chips">{chips}</div></div><div class="asset-readiness">{ready_html}</div></div>'''
    return f'''<section class="page asset-page" data-route="asset/{html.escape(a['id'])}"><div class="page-head"><div><a class="back route-link" href="#assets" data-route="assets">← 返回资产中心</a><div class="kicker">资产工作台 <span class="heading-en">{html.escape(a['id'])}</span></div><h1>{html.escape(a['title'])}</h1>{sec}<p>{html.escape(a.get('summary') or '')}</p></div></div>{passport}<div class="asset-production-workspace" data-workspace-kind="asset-production"><aside class="asset-production-rail"><div class="asset-rail-head"><b>当前工作视图</b><span>{len(panels)} 个相关视图 · 无固定先后顺序</span></div>{''.join(rail)}</aside><div class="asset-production-stage">{''.join(stage)}</div></div></section>'''

def _json_panel(path:Path,package_dir:Path)->str:
    rel=str(path.relative_to(package_dir)).replace('\\','/');raw=_read(path)
    try:pretty=json.dumps(json.loads(raw),ensure_ascii=False,indent=2)
    except Exception:pretty=raw
    return f'<details class="machine searchable"><summary>{html.escape(rel)}</summary><pre><code>{html.escape(pretty)}</code></pre></details>'


def _delivery_product_name(center:dict[str,Any], fallback:str)->tuple[str,str|None]:
    product=center.get('product') or {}; delivery=str((center.get('delivery_language') or {}).get('locale') or (center.get('target') or {}).get('delivery_locale') or 'zh-CN')
    original=str(product.get('product_name') or '').strip(); brand=str(product.get('brand') or '').strip()
    if brand and original.casefold().startswith(brand.casefold()): original_full=original
    else: original_full=' '.join(x for x in [brand,original] if x).strip()
    companion=None
    for row in center.get('localized_copy') or []:
        if str(row.get('field') or '').casefold() in {'product_name','title'} and row.get('delivery_translation'):
            companion=str(row.get('delivery_translation')).strip(); break
    for row in center.get('copy_center') or []:
        if not companion and str(row.get('field') or '').casefold() in {'product_name','title'} and row.get('delivery_translation'):
            companion=str(row.get('delivery_translation')).strip(); break
    if delivery.casefold().startswith('zh') and companion:
        return companion, (original_full if original_full and original_full!=companion else None)
    return original_full or fallback, None


def _human_target_label(value:Any, kind:str='market')->str:
    raw=str(value or '').strip()
    if not raw:return '待查证'
    if kind=='platform':
        m={'tiktok_shop':'TikTok Shop','tiktok shop':'TikTok Shop','amazon':'Amazon','shopee':'Shopee','lazada':'Lazada','noon':'Noon','shopify':'Shopify','walmart':'Walmart','temu':'Temu','etsy':'Etsy','ebay':'eBay'}
        return m.get(raw.casefold(),raw)
    m={'malaysia':'马来西亚','my':'马来西亚','singapore':'新加坡','sg':'新加坡','thailand':'泰国','th':'泰国','vietnam':'越南','vn':'越南','indonesia':'印度尼西亚','id':'印度尼西亚','philippines':'菲律宾','ph':'菲律宾','united states':'美国','usa':'美国','us':'美国','united kingdom':'英国','uk':'英国','gb':'英国','united arab emirates':'阿联酋','uae':'阿联酋','ae':'阿联酋','saudi arabia':'沙特阿拉伯','sa':'沙特阿拉伯','japan':'日本','jp':'日本','south korea':'韩国','korea':'韩国','kr':'韩国','australia':'澳大利亚','au':'澳大利亚','canada':'加拿大','ca':'加拿大','brazil':'巴西','br':'巴西','mexico':'墨西哥','mx':'墨西哥','germany':'德国','de':'德国','france':'法国','fr':'法国'}
    return m.get(raw.casefold(),raw)


def build_delivery_html(package_dir:Path,output:Path|None=None,title:str='CBCC Delivery')->Path:
    package_dir=Path(package_dir);output=Path(output) if output else package_dir/'index.html';center=_center(package_dir);theme=_theme_from_project(package_dir)
    target=center.get('target') or {};product=center.get('product') or {};readiness=center.get('readiness') or {};delivery_locale=(center.get('delivery_language') or {}).get('locale') or target.get('delivery_locale') or 'zh-CN'
    product_name,product_name_secondary=_delivery_product_name(center,str(product.get('product_name') or title))
    platform=_human_target_label(target.get('platform') or target.get('site'),'platform');market=_human_target_label(target.get('market') or target.get('country'),'market');target_locale=target.get('locale') or '待查证'
    copy_rows=center.get('copy_center') or [];ready=sum(1 for x in copy_rows if x.get('status')=='READY');pending=len(copy_rows)-ready
    companion_missing=sum(1 for x in copy_rows if not _is_empty(x.get('value')) and str(x.get('locale') or '').casefold()!=str(x.get('delivery_locale') or delivery_locale).casefold() and str(x.get('field') or '').casefold() not in {'brand','sku','category_id'} and not x.get('delivery_translation'))
    assets=_assets(package_dir);risks=center.get('risks_and_holds') or []

    docs={'product':[],'market':[],'listing':[],'strategy':[],'content':[],'visual':[],'risk':[],'sources':[],'master':[],'archive':[]};asset_source_paths={s for a in assets for s in a.get('source_files',[])}
    for p in sorted(package_dir.rglob('*.md')):
        rel=str(p.relative_to(package_dir)).replace('\\','/')
        if rel in asset_source_paths:continue
        if p.name.startswith(('CHANGELOG','BASELINE_AUDIT','INTEGRATION_','REAL_PRODUCT_','REAL_PRODUCTION_','MULTICATEGORY_','PRODUCTION_LEARNING_')):continue
        docs.setdefault(_classify_doc(p),[]).append(p)

    master_path=docs.get('master',[None])[0] if docs.get('master') else None
    master_views=_master_strategy_views(master_path,package_dir) if master_path else {'overview':[],'product':[],'market':[],'strategy':[],'content':[],'visual':[],'risk':[]}
    product_views=master_views['product']+_doc_views(docs['product'],package_dir,'product')
    market_views=master_views['market']+_doc_views(docs['market'],package_dir,'market')
    strategy_views=master_views['strategy']+_doc_views(docs['strategy'],package_dir,'strategy')
    content_views=master_views['content']+_doc_views(docs['content'],package_dir,'content')
    visual_views=master_views['visual']+_doc_views(docs['visual'],package_dir,'visual')
    risk_views=master_views['risk']+_doc_views(docs['risk'],package_dir,'risk')
    product_ws=_module_workspace(product_views,'product','本项目没有产品事实内容。')
    market_ws=_module_workspace(market_views,'market','本项目没有市场/人群内容。')
    strategy_ws=_strategy_workspace(strategy_views)
    content_ws=_content_workspace(content_views)
    visual_ws=_visual_workspace(visual_views)
    risk_ws=_module_workspace(risk_views,'risk','本项目没有风险内容。')
    overview_ws=_module_workspace(master_views['overview'],'overview-decision','本项目没有信息完整度 / 假设 / 决策日志。')
    listing_ws=_listing_workspace(center)
    asset_cards=_asset_universe_cards(assets)
    prompt_ws=_prompt_workspace(assets)

    budget=[0];media=[];source_files=[]
    for p in sorted(package_dir.rglob('*')):
        if not p.is_file() or p==output:continue
        rel=str(p.relative_to(package_dir)).replace('\\','/');ext=p.suffix.lower()
        if ext in {'.png','.jpg','.jpeg','.webp','.gif','.svg'}:
            uri=_data_uri(p,budget)
            if uri:media.append(f'<figure class="media-card searchable"><img loading="lazy" src="{uri}" alt="{html.escape(p.name)}"><figcaption>{html.escape(rel)}</figcaption></figure>')
        elif ext in {'.mp4','.webm','.mov','.m4v'}:
            uri=_data_uri(p,budget)
            if uri:media.append(f'<figure class="media-card searchable"><video controls preload="metadata" src="{uri}"></video><figcaption>{html.escape(rel)}</figcaption></figure>')
        elif ext in {'.mp3','.wav','.m4a','.ogg'}:
            uri=_data_uri(p,budget)
            if uri:media.append(f'<figure class="media-card searchable"><audio controls preload="metadata" src="{uri}"></audio><figcaption>{html.escape(rel)}</figcaption></figure>')
        elif '/sources/' in '/'+rel.lower() or rel.lower().startswith('sources/'):
            source_files.append(f'<li><strong>{html.escape(p.name)}</strong><span>{html.escape(rel)} · {p.stat().st_size:,} bytes</span></li>')

    risk_cards=''.join(f'<article class="risk"><span>{html.escape(str(x.get("status") or "OPEN"))}</span><div><strong>{html.escape(str(x.get("source") or x.get("type") or "风险"))}</strong><p>{html.escape(str(x.get("item") or x.get("reason") or x))}</p></div></article>' for x in risks) or '<div class="empty">当前没有结构化风险项。</div>'
    machine=[]
    for p in sorted(package_dir.rglob('*')):
        if not p.is_file():continue
        rel=str(p.relative_to(package_dir)).replace('\\','/')
        if rel in asset_source_paths or p.suffix.lower() not in {'.json','.yaml','.yml','.txt'}:continue
        if _read(p):machine.append(_json_panel(p,package_dir))
    machine_html=''.join(machine) or '<div class="empty">暂无结构化归档。</div>'

    css=f'''
:root{{--bg:{theme['paper']};--panel:#fff;--ink:{theme['ink']};--muted:{theme['muted']};--line:{theme['line']};--accent:{theme['accent']};--accent2:{theme['accent2']};--soft:#F1F4F2;--ok:#176642;--okbg:#EAF7EF;--warn:#915E12;--warnbg:#FFF4E2;--danger:#9A3D3D;--shadow:0 16px 42px rgba(21,36,29,.08);--r:16px}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.65 Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif}}a{{color:inherit}}button,input{{font:inherit}}button{{cursor:pointer}}
.app{{display:grid;grid-template-columns:224px minmax(0,1fr);min-height:100vh}}.sidebar{{position:sticky;top:0;height:100vh;background:#10231C;color:#EDF5F1;padding:18px 12px;overflow:auto;z-index:30}}.brand{{padding:7px 9px 18px}}.brand b{{font-size:16px;display:block}}.brand span{{font-size:11px;color:#9FB5AB;display:block;margin-top:4px}}.nav-label{{font-size:10px;color:#789286;text-transform:uppercase;letter-spacing:.13em;margin:13px 9px 5px}}.nav a{{display:flex;gap:9px;align-items:center;text-decoration:none;color:#D9E6E0;padding:9px 10px;border-radius:10px;margin:2px 0}}.nav a:hover,.nav a.active{{background:rgba(255,255,255,.10);color:#fff}}.nav .ico{{width:18px;text-align:center}}.sidebar-foot{{margin-top:18px;border-top:1px solid rgba(255,255,255,.12);padding:12px 9px;color:#94A99F;font-size:10px}}
.workspace{{min-width:0}}.topbar{{position:sticky;top:0;height:64px;z-index:25;background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(14px);border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;gap:14px;padding:9px 22px}}.context b{{display:block;font-size:13px}}.context span{{font-size:10px;color:var(--muted)}}.search{{width:min(420px,46vw);padding:9px 12px;border:1px solid var(--line);border-radius:10px;background:#fff;outline:none}}
.page{{display:none;padding:24px 24px 60px;max-width:1560px;margin:auto}}.page.active{{display:block}}.page-head{{display:flex;align-items:flex-start;justify-content:space-between;gap:18px;margin-bottom:18px}}.kicker{{font-size:10px;font-weight:850;letter-spacing:.13em;text-transform:uppercase;color:var(--accent)}}.page-head h1{{font-size:30px;line-height:1.15;margin:4px 0 6px}}.page-head p{{color:var(--muted);margin:0;max-width:900px}}.heading-en{{display:block;font-weight:500;font-size:10px;color:var(--muted);margin-top:2px}}.back{{font-weight:750;text-decoration:none;color:var(--accent);font-size:12px}}
.command-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}.command-card{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:17px;text-decoration:none;box-shadow:0 6px 20px rgba(20,35,28,.035);transition:.17s}}.command-card:hover{{transform:translateY(-2px);box-shadow:var(--shadow)}}.command-card b{{display:block;font-size:14px}}.command-card span{{color:var(--muted);font-size:11px}}.stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:14px 0 18px}}.stat{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px}}.stat strong{{display:block;font-size:24px}}.stat span{{font-size:10px;color:var(--muted)}}.panel{{background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:18px;margin-bottom:14px;box-shadow:0 5px 20px rgba(20,35,28,.03)}}.panel h2{{font-size:18px;margin:0 0 10px}}
.module-shell{{display:grid;grid-template-columns:220px minmax(0,1fr);gap:14px;align-items:start}}.module-nav{{position:sticky;top:82px;background:#fff;border:1px solid var(--line);border-radius:14px;padding:7px;max-height:calc(100vh - 104px);overflow:auto}}.subnav-btn{{display:block;width:100%;text-align:left;border:0;background:transparent;padding:10px 10px;border-radius:9px;color:var(--ink);margin:1px 0}}.subnav-btn:hover{{background:var(--soft)}}.subnav-btn.active{{background:color-mix(in srgb,var(--accent) 10%,#fff);color:var(--accent);font-weight:750}}.subnav-btn span{{display:block}}.subnav-btn small{{display:block;color:var(--muted);font-size:9px;font-weight:500;margin-top:2px}}.module-stage{{min-width:0}}.subview{{display:none;background:#fff;border:1px solid var(--line);border-radius:16px;padding:22px;box-shadow:0 6px 22px rgba(20,35,28,.035);min-height:360px}}.subview.active{{display:block}}.source-note{{font-size:9px;color:var(--muted);border-bottom:1px solid var(--line);padding-bottom:8px;margin-bottom:12px}}
.workspace-panel{{display:none}}.workspace-panel.active{{display:block}}
.asset-passport{{display:flex;justify-content:space-between;align-items:center;gap:14px;background:#10231C;color:#EDF5F1;border-radius:16px;padding:13px 16px;margin-bottom:12px}}.asset-passport-id{{font:850 11px ui-monospace,monospace;color:#AFC1B8}}.asset-passport-chips{{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}}.asset-passport-chips span{{font-size:9px;border:1px solid rgba(255,255,255,.18);border-radius:999px;padding:3px 7px}}.asset-readiness{{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}}.asset-readiness span{{font-size:9px;background:rgba(255,255,255,.09);border-radius:999px;padding:4px 8px}}
.asset-production-workspace{{display:grid;grid-template-columns:230px minmax(0,1fr);gap:12px;align-items:start}}.asset-production-rail{{position:sticky;top:82px;background:#fff;border:1px solid var(--line);border-radius:16px;padding:8px;display:grid;gap:5px}}.asset-rail-head{{display:flex;justify-content:space-between;gap:8px;align-items:end;padding:7px 8px 10px;border-bottom:1px solid var(--line);margin-bottom:2px}}.asset-rail-head b{{font-size:12px}}.asset-rail-head span{{font-size:8px;color:var(--muted)}}.asset-phase{{border:0;background:transparent;text-align:left;border-radius:11px;padding:10px;display:grid;grid-template-columns:30px 1fr;gap:8px;align-items:start;color:var(--ink)}}.asset-phase:hover{{background:var(--soft)}}.asset-phase.active{{background:var(--accent);color:#fff}}.asset-phase-index{{font:800 10px ui-monospace,monospace;color:var(--accent)}}.asset-phase.active .asset-phase-index{{color:#CFE0D8}}.asset-phase-copy small{{display:block;font-size:7px;letter-spacing:.08em;color:var(--muted)}}.asset-phase.active .asset-phase-copy small{{color:#CFE0D8}}.asset-phase-copy b{{display:block;font-size:11px;margin-top:1px}}
.asset-production-stage{{min-width:0}}.asset-stage{{background:#fff;border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:0 8px 28px rgba(20,35,28,.04)}}.asset-stage-head{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;padding:18px 20px;border-bottom:1px solid var(--line);background:linear-gradient(135deg,#fff,var(--soft))}}.asset-stage-head span{{font-size:8px;font-weight:850;letter-spacing:.12em;color:var(--accent)}}.asset-stage-head h2{{font-size:20px;line-height:1.2;margin:4px 0}}.asset-stage-head p{{margin:0;color:var(--muted);font-size:10px;max-width:760px}}.asset-stage-head>strong{{font:850 28px ui-monospace,monospace;color:#D7E0DB}}.asset-stage-body{{padding:18px 20px}}.asset-section-label{{font-size:9px;font-weight:850;letter-spacing:.08em;color:var(--accent);margin:0 0 8px}}.asset-decision-block+.asset-decision-block{{margin-top:16px;padding-top:16px;border-top:1px solid var(--line)}}.asset-command-note,.photo-console-head{{display:flex;justify-content:space-between;gap:18px;align-items:start;padding:12px 14px;border-radius:12px;background:#10231C;color:#EDF5F1;margin-bottom:12px}}.asset-command-note b,.photo-console-head b{{font-size:11px}}.asset-command-note span,.photo-console-head span{{font-size:9px;color:#AFC1B8;max-width:700px}}.asset-stage-visual .design-grid{{grid-template-columns:repeat(auto-fit,minmax(210px,1fr))}}.asset-stage-photo .design-grid{{grid-template-columns:repeat(auto-fit,minmax(190px,1fr))}}.asset-copy-console .human-kv{{border-left:3px solid var(--accent)}}.asset-prompt-console .prompt-workbench{{margin-bottom:12px}}.asset-production-notes{{margin-top:12px;border:1px solid var(--line);border-radius:12px;padding:10px 12px}}.asset-production-notes>summary{{cursor:pointer;font-weight:750}}.asset-stage-qa .asset-stage-body{{display:grid;gap:12px}}.asset-qa-source,.asset-source-ledger{{border:1px solid var(--line);border-radius:13px;padding:14px}}.asset-source-ledger ul{{margin:8px 0 0;padding-left:18px;color:var(--muted);font:10px/1.55 ui-monospace,monospace;overflow-wrap:anywhere}}
.ia-source{{margin-top:16px;padding-top:9px;border-top:1px solid var(--line);color:var(--muted);font-size:9px}}
.strategy-board{{max-width:1180px}}.strategy-map-head{{display:flex;justify-content:space-between;align-items:end;gap:16px;padding:2px 3px 12px;border-bottom:2px solid var(--ink);margin-bottom:8px}}.strategy-map-head b{{font-size:16px}}.strategy-map-head span{{color:var(--muted);font-size:10px}}.strategy-decision{{background:#fff;border-bottom:1px solid var(--line)}}.strategy-decision:first-of-type{{border-radius:14px 14px 0 0}}.strategy-decision:last-child{{border-radius:0 0 14px 14px}}.strategy-decision summary{{list-style:none;display:grid;grid-template-columns:52px minmax(0,1fr) auto;gap:12px;align-items:center;padding:16px;cursor:pointer}}.strategy-decision summary::-webkit-details-marker{{display:none}}.strategy-index{{font:800 18px/1 ui-monospace,monospace;color:var(--accent)}}.strategy-decision summary b{{font-size:14px}}.strategy-decision summary small{{display:block;color:var(--muted);font-size:9px}}.strategy-open{{font-size:9px;color:var(--muted)}}.strategy-decision[open] .strategy-open{{color:var(--accent)}}.strategy-body{{padding:2px 22px 22px 80px;border-top:1px solid #EEF1EE}}
.content-board{{display:grid;gap:14px}}.content-board-head{{display:flex;justify-content:space-between;align-items:center;background:#10231C;color:#EDF5F1;border-radius:16px;padding:18px 20px}}.content-board-head b{{display:block;font-size:17px}}.content-board-head span{{display:block;font-size:10px;color:#AFC1B8;margin-top:3px}}.content-board-head strong{{font-size:32px}}.content-lanes{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px;align-items:start}}.content-lane{{background:#fff;border:1px solid var(--line);border-radius:16px;overflow:hidden}}.content-lane>header{{display:grid;grid-template-columns:34px 1fr;gap:9px;padding:13px 14px;background:var(--soft);border-bottom:1px solid var(--line)}}.content-lane>header>span{{font:800 12px ui-monospace,monospace;color:var(--accent)}}.content-lane h3{{font-size:13px;margin:0}}.content-lane header small{{font-size:9px;color:var(--muted)}}.content-lane-body{{padding:14px;max-height:620px;overflow:auto}}.content-lane footer{{padding:8px 14px;border-top:1px solid var(--line);font-size:9px;color:var(--muted)}}
.visual-studio{{display:grid;gap:12px}}.visual-contact-sheet{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}}.visual-thumb{{border:1px solid var(--line);background:#fff;border-radius:13px;padding:12px;text-align:left;min-height:88px}}.visual-thumb:hover,.visual-thumb.active{{border-color:var(--accent);box-shadow:0 7px 20px rgba(20,35,28,.06)}}.visual-thumb>span{{display:block;font:800 10px ui-monospace,monospace;color:var(--accent)}}.visual-thumb b{{display:block;font-size:12px;margin:7px 0 2px}}.visual-thumb small{{display:block;font-size:8px;color:var(--muted)}}.visual-stage{{background:#fff;border:1px solid var(--line);border-radius:16px;min-height:420px}}.visual-inspector{{padding:20px}}.visual-inspector-bar{{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid var(--line);padding-bottom:9px;margin-bottom:12px;color:var(--muted);font-size:9px}}
.listing-studio{{display:grid;gap:10px}}.listing-tasks{{display:flex;gap:7px;overflow:auto;padding-bottom:2px}}.listing-task{{min-width:150px;border:1px solid var(--line);background:#fff;border-radius:12px;padding:10px 12px;text-align:left}}.listing-task span{{display:block;font:800 9px ui-monospace,monospace;color:var(--accent)}}.listing-task b{{font-size:11px}}.listing-task.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}.listing-task.active span{{color:#CFE0D8}}.listing-panel{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px}}.listing-panel-head{{display:flex;justify-content:space-between;gap:12px;margin-bottom:12px;padding-bottom:9px;border-bottom:1px solid var(--line)}}.listing-panel-head small{{color:var(--muted);font-size:9px}}
.prompt-lab{{display:grid;grid-template-columns:minmax(180px,260px) minmax(0,1fr);gap:12px;align-items:start}}.prompt-selector{{display:grid;gap:6px;position:sticky;top:82px;max-height:calc(100vh - 105px);overflow:auto}}.prompt-asset-switch{{border:1px solid var(--line);background:#fff;border-radius:12px;padding:11px;text-align:left}}.prompt-asset-switch span{{display:block;font:800 9px ui-monospace,monospace;color:var(--accent)}}.prompt-asset-switch b{{display:block;font-size:11px;margin-top:4px}}.prompt-asset-switch.active{{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 7%,#fff)}}.prompt-stage{{min-width:0}}.prompt-asset-panel{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px}}.prompt-asset-meta{{display:flex;justify-content:space-between;gap:12px;padding-bottom:9px;margin-bottom:11px;border-bottom:1px solid var(--line)}}.prompt-asset-meta span{{font:800 9px ui-monospace,monospace;color:var(--accent)}}
.evidence-center{{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(300px,.65fr);gap:12px;align-items:start}}.evidence-zone{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:15px}}.evidence-zone>header{{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:12px}}.evidence-zone>header>div{{display:flex;align-items:center;gap:8px}}.evidence-zone>header span{{font:800 10px ui-monospace,monospace;color:var(--accent)}}.evidence-zone h2{{font-size:14px;margin:0}}.evidence-zone>header strong{{font-size:20px;color:var(--muted)}}.evidence-media{{grid-row:span 2}}.evidence-doc{{border-top:1px solid var(--line)}}.evidence-doc summary{{display:grid;grid-template-columns:30px minmax(0,1fr);gap:8px;cursor:pointer;padding:10px 0;list-style:none}}.evidence-doc summary::-webkit-details-marker{{display:none}}.evidence-doc summary span{{font:800 9px ui-monospace,monospace;color:var(--accent)}}.evidence-doc summary small{{grid-column:2;color:var(--muted);font-size:8px}}.evidence-doc-body{{padding:0 0 12px 38px}}
.copy-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px}}.copy-card{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px}}.copy-head{{display:flex;justify-content:space-between;gap:10px}}.copy-head small{{font-size:9px;color:var(--muted)}}.copy-head h3{{font-size:13px;margin:2px 0 9px}}.target-copy{{white-space:pre-wrap;word-break:break-word;background:#F8F9F7;border:1px solid #ECEFEC;border-radius:9px;padding:10px;min-height:42px}}.cn-companion{{margin-top:8px;padding:9px 10px;border-radius:9px;background:#EEF5F1;border-left:3px solid var(--accent)}}.cn-companion span{{font-size:9px;color:var(--accent);font-weight:850}}.cn-companion div{{margin-top:2px}}.cn-companion small{{color:var(--muted)}}.cn-companion.missing{{background:var(--warnbg);border-left-color:var(--warn)}}.badge{{font-size:9px;padding:3px 7px;border-radius:999px;height:max-content}}.badge.ready{{background:var(--okbg);color:var(--ok)}}.badge.hold{{background:var(--warnbg);color:var(--warn)}}.copy-btn{{border:0;background:var(--accent);color:#fff;border-radius:8px;padding:7px 9px;margin-top:8px;font-size:11px}}.copy-btn.mini{{margin:0}}
.locale-block{{margin-bottom:18px}}.locale-block h3{{font-size:16px}}.locale-row{{border:1px solid var(--line);border-radius:12px;padding:12px;margin:8px 0}}.locale-field{{display:flex;justify-content:space-between;gap:12px;margin-bottom:7px}}.locale-field span{{font-size:10px;color:var(--muted)}}
.asset-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}.asset-card{{display:block;text-decoration:none;background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px;box-shadow:0 5px 20px rgba(20,35,28,.03);transition:.17s}}.asset-card:hover{{transform:translateY(-2px);box-shadow:var(--shadow)}}.asset-top{{display:flex;justify-content:space-between;gap:8px;align-items:center}}.asset-top>b{{font-size:10px;color:var(--accent)}}.asset-chips{{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:4px}}.asset-chips span{{font-size:8px;background:var(--soft);padding:3px 5px;border-radius:999px}}.asset-card h3{{font-size:15px;margin:8px 0 2px}}.asset-card small{{color:var(--muted);font-size:9px;display:block}}.asset-card p{{font-size:11px;color:var(--muted);min-height:44px}}.asset-open{{font-size:11px;color:var(--accent);font-weight:750}}.asset-original{{font-size:10px;color:var(--muted);margin-top:-2px}}.asset-file{{margin-bottom:18px}}.file-label{{font-size:9px;color:var(--muted);font-weight:750;padding-bottom:5px;border-bottom:1px solid var(--line);margin-bottom:8px}}
.prompt-workbench{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.prompt-primary,.prompt-secondary{{min-width:0}}.prompt-head{{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:7px}}.prompt-head span{{font-size:9px;color:var(--muted)}}.prompt-head h3{{font-size:14px;margin:1px 0}}pre{{background:#0E211A;color:#E7F0EB;border-radius:11px;padding:14px;overflow:auto;white-space:pre-wrap;word-break:break-word;font-size:11px;line-height:1.58}}pre code{{background:none;padding:0}}.language-note{{margin-top:10px;background:#EEF5F1;border:1px solid #DCE8E1;border-radius:10px;padding:9px 11px;font-size:10px;color:#405047}}
.risk{{display:grid;grid-template-columns:72px 1fr;gap:10px;padding:11px 0;border-bottom:1px solid var(--line)}}.risk>span{{font-size:9px;font-weight:850;color:var(--warn)}}.risk strong{{font-size:11px}}.risk p{{margin:2px 0;color:#3C4842}}.media-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px}}.media-card{{margin:0;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden}}.media-card img,.media-card video{{width:100%;aspect-ratio:1/1;object-fit:contain;background:#F5F6F4;display:block}}.media-card audio{{width:100%;padding:12px}}.media-card figcaption{{font-size:9px;color:var(--muted);padding:7px;word-break:break-all}}
.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:10px;margin:11px 0}}table{{border-collapse:collapse;width:100%;min-width:720px}}th,td{{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}}th{{font-size:10px;background:#F1F4F2;color:#29483D}}blockquote{{padding:9px 12px;margin:11px 0;border-left:3px solid var(--accent);background:var(--soft);border-radius:0 9px 9px 0}}code{{background:var(--soft);padding:2px 5px;border-radius:5px}}h1,h2,h3,h4{{line-height:1.28}}.subview h2{{font-size:19px;margin-top:22px}}.subview h3{{font-size:15px;margin-top:18px}}.machine{{background:#fff;border:1px solid var(--line);border-radius:10px;margin:7px 0}}.machine summary{{cursor:pointer;padding:10px 12px;font-size:10px;font-weight:750}}.machine pre{{margin:0;border-radius:0 0 10px 10px;max-height:460px}}.source-files{{list-style:none;padding:0}}.source-files li{{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px solid var(--line)}}.source-files span{{font-size:9px;color:var(--muted)}}.empty{{padding:14px;border:1px dashed var(--line);border-radius:10px;color:var(--muted);background:#fff}}.design-card-hero{{display:grid;gap:14px}}.design-question{{padding:18px;border-radius:16px;background:linear-gradient(135deg,var(--soft),#fff);border:1px solid var(--line)}}.design-question span{{font-size:10px;color:var(--muted)}}.design-question h2{{margin:6px 0;font-size:22px}}.design-question small{{display:block;color:var(--muted)}}.design-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}}.human-kv{{border:1px solid var(--line);border-radius:12px;padding:12px;background:#fff;min-width:0}}.human-kv>span{{display:block;font-size:10px;color:var(--muted);margin-bottom:5px}}.human-kv>div{{white-space:pre-wrap;word-break:break-word}}.source-detail{{margin-top:18px;border-top:1px solid var(--line);padding-top:10px}}.source-detail>summary{{cursor:pointer;color:var(--muted);font-size:11px}}.is-hidden{{display:none!important}}
@media(max-width:1180px){{.command-grid{{grid-template-columns:repeat(2,1fr)}}.stats{{grid-template-columns:repeat(3,1fr)}}.asset-grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:900px){{.asset-production-workspace{{grid-template-columns:1fr}}.asset-production-rail{{position:static;display:flex;overflow:auto;gap:6px}}.asset-rail-head{{display:none}}.asset-phase{{min-width:150px;grid-template-columns:24px 1fr}}.asset-passport{{align-items:flex-start;flex-direction:column}}.asset-readiness{{justify-content:flex-start}}.prompt-lab,.evidence-center{{grid-template-columns:1fr}}.prompt-selector{{position:static;display:flex;overflow:auto;max-height:none}}.prompt-asset-switch{{min-width:160px}}.content-lanes{{grid-template-columns:1fr}}.strategy-body{{padding-left:18px}}.app{{display:block}}.sidebar{{position:sticky;height:auto;padding:7px 8px;display:flex;gap:7px;align-items:center;overflow:auto}}.brand{{min-width:160px;padding:3px 7px}}.brand span,.nav-label,.sidebar-foot{{display:none}}.nav{{display:flex;gap:3px}}.nav a{{white-space:nowrap;background:rgba(255,255,255,.05)}}.topbar{{top:51px;height:56px;padding:7px 10px}}.page{{padding:16px 10px 44px}}.module-shell{{display:block}}.module-nav{{position:sticky;top:111px;z-index:12;display:flex;gap:5px;overflow:auto;max-height:none;padding:6px;margin-bottom:9px}}.subnav-btn{{min-width:max-content;width:auto;padding:8px 10px}}.subnav-btn small{{display:none}}.copy-grid,.prompt-workbench{{grid-template-columns:1fr}}}}
@media(max-width:580px){{.strategy-decision summary{{grid-template-columns:38px minmax(0,1fr)}}.strategy-open{{display:none}}.visual-contact-sheet{{grid-template-columns:repeat(2,minmax(0,1fr))}}.design-grid{{grid-template-columns:1fr}}.context{{display:none}}.search{{width:100%}}.command-grid,.stats,.asset-grid{{grid-template-columns:1fr}}.page-head h1{{font-size:24px}}.subview{{padding:14px;min-height:260px}}.copy-card{{padding:12px}}table{{font-size:11px;min-width:650px}}}}
@media print{{.sidebar,.topbar,.module-nav,.asset-production-rail,.copy-btn{{display:none!important}}.app{{display:block}}.page{{display:block!important;padding:0}}.subview,.asset-stage{{display:block!important;box-shadow:none;break-inside:auto;margin-bottom:14px}}.asset-page{{break-before:page}}body{{background:#fff}}}}
'''

    agent_next_action=_read_json(package_dir/'artifacts/agent_next_action.json',{})
    availability={
        'product':bool(product_views),'market':bool(market_views),'listing':bool(copy_rows or center.get('localized_copy')),
        'strategy':bool(strategy_views),'content':bool(content_views),'visual':bool(visual_views),
        'assets':bool(assets),'prompts':any(a.get('prompt_cn') or a.get('prompt_en') for a in assets),
        'risk':bool(risks or risk_views),'sources':bool(docs['sources']),'archive':bool(machine),
    }
    route_plan=build_workspace_route_plan(availability=availability,agent_next_action=agent_next_action)
    nav_html=''.join(f'<a href="#{row["route"]}" data-route="{row["route"]}" class="route-link"><span class="ico">{row["icon"]}</span>{row["label"]}</a>' for row in route_plan['primary_routes'])
    commands=''.join(f'<a class="command-card route-link" href="#{row["route"]}" data-route="{row["route"]}"><b>{html.escape(str(row["name"]))}</b><span>{html.escape(str(row["description"]))}</span></a>' for row in route_plan['commands']) or '<div class="empty">当前没有需要额外推进的工作对象；可在现有项目范围内复核或停止。</div>'
    archive_link=''.join(f'<a class="route-link secondary-route" href="#{row["route"]}" data-route="{row["route"]}">{row["label"]}</a>' for row in route_plan['secondary_routes'])

    source_doc_views=_doc_views(docs['sources'],package_dir,'sources') if docs['sources'] else []
    sources_ws=_evidence_workspace(media,source_doc_views,source_files)

    if media or source_doc_views or source_files:
        availability['sources']=True
    availability['archive']=bool(machine)
    route_plan=build_workspace_route_plan(availability=availability,agent_next_action=agent_next_action)
    nav_html=''.join(f'<a href="#{row["route"]}" data-route="{row["route"]}" class="route-link"><span class="ico">{row["icon"]}</span>{row["label"]}</a>' for row in route_plan['primary_routes'])
    commands=''.join(f'<a class="command-card route-link" href="#{row["route"]}" data-route="{row["route"]}"><b>{html.escape(str(row["name"]))}</b><span>{html.escape(str(row["description"]))}</span></a>' for row in route_plan['commands']) or '<div class="empty">当前没有需要额外推进的工作对象；可在现有项目范围内复核或停止。</div>'
    archive_link=''.join(f'<a class="route-link secondary-route" href="#{row["route"]}" data-route="{row["route"]}">{row["label"]}</a>' for row in route_plan['secondary_routes'])

    stat_rows=[]
    if availability.get('listing'):
        stat_rows += [(ready,'上架字段就绪'),(pending,'待补 / 待查证')]
        if companion_missing: stat_rows.append((companion_missing,'待补中文释义'))
    if assets: stat_rows.append((len(assets),'当前资产'))
    if risks: stat_rows.append((len(risks),'结构化风险'))
    stats_html=''.join(f'<div class="stat"><strong>{value}</strong><span>{html.escape(label)}</span></div>' for value,label in stat_rows)
    next_status=str(agent_next_action.get('recommended_next_action') or 'STOP_CURRENT_SCOPE_SATISFIED')
    next_frontier=agent_next_action.get('frontier') or []
    next_items=''.join(f'<li><b>{html.escape(str(x.get("action") or "下一步"))}</b><span>{html.escape(str(x.get("reason") or ""))}</span></li>' for x in next_frontier)
    if not next_items: next_items='<li><b>当前范围可停止</b><span>没有检测到必须继续推进的固定步骤；由 Agent / 用户决定是否扩展目标。</span></li>'

    overview_decision_html=(
        '<div class="panel full-overview-domain"><div class="kicker">FULL 决策域</div><h2>信息完整度、待确认清单、假设与决策日志</h2>'
        + overview_ws + '</div>'
    ) if master_views['overview'] else ''

    page_parts=[]
    page_parts.append(f'''<section class="page" data-route="overview"><div class="page-head"><div><div class="kicker">电商工作区</div><h1>{html.escape(product_name)}</h1>{f'<div class="heading-en project-original">{html.escape(product_name_secondary)}</div>' if product_name_secondary else ''}<p>工作台只显示当前项目真实存在的业务对象和 Agent 识别到的下一步，不按固定报告目录展开。</p></div></div>{f'<div class="stats">{stats_html}</div>' if stats_html else ''}{overview_decision_html}<div class="panel"><h2>当前可以做什么？</h2><div class="command-grid">{commands}</div></div><div class="panel agent-frontier"><h2>Agent 决策前沿</h2><p><b>建议：</b>{html.escape(next_status)}</p><ul>{next_items}</ul></div><div class="panel"><h2>项目语言</h2><p><b>交付语言：</b>{html.escape(str(delivery_locale))}（默认中文，除非用户明确要求其他语言）</p><p><b>目标市场语言：</b>{html.escape(str(target_locale))}。目标语言上架文案 / 资产文案保留原文，同时显示中文释义或用途说明。</p></div></section>''')
    if availability.get('product'): page_parts.append(f'''<section class="page" data-route="product"><div class="page-head"><div><div class="kicker">商品真源 / 证据</div><h1>产品事实与证据</h1><p>只呈现当前项目实际存在的事实、证据与缺口主题。</p></div></div>{product_ws}</section>''')
    if availability.get('market'): page_parts.append(f'''<section class="page" data-route="market"><div class="page-head"><div><div class="kicker">目标市场语境</div><h1>市场、平台、人群与文化</h1><p>研究主题来自当前决策缺口；没有固定竞品数、报告章节数或研究配额。</p></div></div>{market_ws}</section>''')
    if availability.get('listing'): page_parts.append(f'''<section class="page" data-route="listing"><div class="page-head"><div><div class="kicker">上架工作室</div><h1>上架资料中心</h1><p>只呈现当前上架任务涉及的字段；目标市场文案保留目标语言，并提供中文释义 / 用途。</p></div></div>{listing_ws}</section>''')
    if availability.get('strategy'): page_parts.append(f'''<section class="page" data-route="strategy"><div class="page-head"><div><div class="kicker">策略工作室</div><h1>营销与商业决策</h1><p>以当前商品需要解决的决策为单位阅读；框架只在 Agent / 用户选择并确实有用时出现。</p></div></div>{strategy_ws}</section>''')
    if availability.get('content'): page_parts.append(f'''<section class="page" data-route="content"><div class="page-head"><div><div class="kicker">内容系统</div><h1>平台内容与传播对象</h1><p>内容对象、叙事、Surface 与数量由当前消费者问题和商业任务动态产生；不预设 Hook / CTA / 固定传播阶段。</p></div></div>{content_ws}</section>''')
    if availability.get('visual'): page_parts.append(f'''<section class="page" data-route="visual"><div class="page-head"><div><div class="kicker">视觉工作室</div><h1>视觉、摄影与 CMF</h1><p>只显示当前项目真正采用的创意、构图、摄影、材质和颜色决策；无关参数保持缺席。</p></div></div>{visual_ws}</section>''')
    if availability.get('assets'): page_parts.append(f'''<section class="page" data-route="assets"><div class="page-head"><div><div class="kicker">资产工作室</div><h1>资产中心</h1><p>每个资产拥有自己的工作视图；视图按实际内容出现，不是一条必须依次完成的流水线。</p></div></div><div class="asset-grid">{asset_cards}</div></section>''')
    if availability.get('prompts'): page_parts.append(f'''<section class="page" data-route="prompts"><div class="page-head"><div><div class="kicker">提示词工作室</div><h1>提示词工作台</h1><p>Prompt 只投影当前资产真正需要的执行参数；中文生产说明与目标模型提示词同屏核对。</p></div></div>{prompt_ws}</section>''')
    if availability.get('risk'): page_parts.append(f'''<section class="page" data-route="risk"><div class="page-head"><div><div class="kicker">风险中心</div><h1>风险、合规与待查证</h1><p>区分真正阻断执行的硬边界与 Agent 可继续研究的 advisory gap。</p></div></div><div class="panel">{risk_cards}</div>{risk_ws}</section>''')
    if availability.get('sources'): page_parts.append(f'''<section class="page" data-route="sources"><div class="page-head"><div><div class="kicker">证据中心</div><h1>来源与产品真源</h1><p>只在当前项目存在来源媒体、证据文档或源文件时出现。</p></div></div>{sources_ws}</section>''')
    if availability.get('archive'): page_parts.append(f'''<section class="page" data-route="archive"><div class="page-head"><div><div class="kicker">机器归档</div><h1>完整结构化归档</h1><p>仅用于追溯和机器合同，不进入一级人类工作导航。</p></div></div><div class="panel">{machine_html}</div></section>''')
    page_parts.extend(_asset_page(a) for a in assets)
    pages=''.join(page_parts)


    js=r'''
const allPages=[...document.querySelectorAll('.page')];
const routeLinks=[...document.querySelectorAll('.route-link')];
function route(){return decodeURIComponent(location.hash.replace(/^#/,''))||'overview'}
function go(r,push=false){const t=allPages.find(x=>x.dataset.route===r)||allPages.find(x=>x.dataset.route==='overview');allPages.forEach(x=>x.classList.remove('active'));t.classList.add('active');routeLinks.forEach(a=>a.classList.toggle('active',a.dataset.route===r));if(push&&location.hash!=='#'+r)history.pushState(null,'','#'+r);window.scrollTo(0,0)}
window.addEventListener('hashchange',()=>go(route()));document.addEventListener('click',e=>{const a=e.target.closest('.route-link');if(!a)return;e.preventDefault();go(a.dataset.route,true)});go(route());
document.addEventListener('click',e=>{const b=e.target.closest('.subnav-btn');if(!b)return;const m=b.dataset.module,v=b.dataset.view;document.querySelectorAll(`.subnav-btn[data-module="${m}"]`).forEach(x=>x.classList.remove('active'));document.querySelectorAll(`.subview[data-module="${m}"]`).forEach(x=>x.classList.remove('active'));b.classList.add('active');document.querySelector(`.subview[data-module="${m}"][data-view="${v}"]`)?.classList.add('active');window.scrollTo({top:0,behavior:'smooth'})});
document.addEventListener('click',e=>{const b=e.target.closest('.workspace-switch');if(!b)return;const g=b.dataset.switchGroup,v=b.dataset.view;document.querySelectorAll(`.workspace-switch[data-switch-group="${g}"]`).forEach(x=>x.classList.remove('active'));document.querySelectorAll(`.workspace-panel[data-switch-group="${g}"]`).forEach(x=>x.classList.remove('active'));b.classList.add('active');document.querySelector(`.workspace-panel[data-switch-group="${g}"][data-view="${v}"]`)?.classList.add('active');});
document.addEventListener('click',async e=>{const b=e.target.closest('.copy-btn');if(!b)return;const el=document.getElementById(b.dataset.copy);if(!el)return;try{await navigator.clipboard.writeText(el.innerText);const old=b.textContent;b.textContent='已复制';setTimeout(()=>b.textContent=old,1000)}catch(err){const r=document.createRange();r.selectNodeContents(el);const s=window.getSelection();s.removeAllRanges();s.addRange(r)}});
const search=document.getElementById('global-search');search?.addEventListener('input',e=>{const q=e.target.value.trim().toLowerCase();const p=document.querySelector('.page.active');if(!p)return;p.querySelectorAll('.searchable').forEach(el=>el.classList.toggle('is-hidden',q&&!el.innerText.toLowerCase().includes(q)))})
'''
    page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>{html.escape(product_name)} · CBCC 工作台</title><style>{css}</style></head><body><div class="app"><aside class="sidebar"><div class="brand"><b>CBCC 电商工作台</b><span>策略 · 上架 · 创意 · 生产</span></div><div class="nav"><div class="nav-label">工作区</div>{nav_html}</div><div class="sidebar-foot">默认中文交付<br>目标语言文案 + 中文释义<br>HTML = 完整人类交付<br>{archive_link}</div></aside><div class="workspace"><header class="topbar"><div class="context"><b>{html.escape(product_name)}</b>{f'<small>{html.escape(product_name_secondary)}</small>' if product_name_secondary else ''}<span>{html.escape(str(platform))} · {html.escape(str(market))} · 目标语言 {html.escape(str(target_locale))} · 交付语言 {html.escape(str(delivery_locale))}</span></div><input id="global-search" class="search" placeholder="搜索当前工作页…"></header>{pages}</div></div><script>{js}</script></body></html>'''
    output.write_text(page,encoding='utf-8')
    return output
