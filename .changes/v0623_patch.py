from pathlib import Path
import re

ROOT=Path('.')

# --- human_delivery.py ---
p=ROOT/'runtime/cbcc/human_delivery.py'
s=p.read_text(encoding='utf-8')

helper=r'''

def _string_list(value):
    if value is None: return []
    if not isinstance(value,(list,tuple,set,frozenset)): value=[value]
    return [str(x).strip() for x in value if str(x or '').strip()]


def _delivery_task_scope(project:Path) -> dict[str,Any]:
    request=_read_json(project/'meta/request.json',{})
    plan=_read_json(project/'artifacts/agent_autonomy_plan.json',{})
    next_action=_read_json(project/'artifacts/agent_next_action.json',{})
    graph=_read_json(project/'artifacts/content_graph.json',{})
    scope=(plan.get('content_scope') or {}) if isinstance(plan.get('content_scope'),dict) else {}
    families=[]
    for source in [request.get('content_families'),scope.get('families'),scope.get('content_families')]:
        for x in _string_list(source):
            if x not in families: families.append(x)
    if not families:
        for obj in graph.get('objects') or []:
            fam=str((obj or {}).get('family') or '').strip()
            if fam and fam not in families: families.append(fam)
    objective=' '.join(_string_list([request.get('goal'),request.get('task'),request.get('objective'),request.get('intent')])).casefold()
    listing_terms=('listing','seller center','upload listing','publish listing','上架','发布商品','商品发布','上架资料')
    submission_terms=('seller center','upload listing','publish listing','上架','发布商品','商品发布')
    listing_active=bool(request.get('listing_input')) or any(x in {'LISTING','SEARCH','OFFER_PROMOTION'} for x in families) or any(t in objective for t in listing_terms)
    submission_sensitive=bool(request.get('listing_submission') or request.get('publish_listing') or request.get('submission_ready')) or any(t in objective for t in submission_terms)
    frontier=list(next_action.get('frontier') or [])
    return {
        'listing_active':listing_active,
        'listing_submission_sensitive':submission_sensitive,
        'families':families,
        'frontier':frontier,
        'recommended_next_action':next_action.get('recommended_next_action'),
        'scope_status':next_action.get('status'),
        'principle':'Human delivery follows the current commerce task. Preserved data does not become a blocking workspace merely because the system knows how to render it.',
    }


_FIELD_LABELS={
    'title':'产品标题','product_name':'商品名称','brand':'品牌','category':'平台类目','category_id':'类目ID','category_path':'类目路径',
    'highlights':'核心卖点','bullets':'卖点','description':'商品描述','attributes':'属性','backend_terms':'后台关键词','search_terms':'搜索词',
    'usage':'使用方法','ingredients':'成分','warnings':'警示','faq':'FAQ','package':'包装/包含物','sku':'SKU','variant':'变体','price':'价格','offer':'优惠/Offer',
    'shipping':'物流承诺','returns':'退换货/售后','seller_info':'卖家/责任方信息',
}
_FIELD_GROUPS={
    'title':'商品识别','product_name':'商品识别','brand':'商品识别','sku':'商品识别','variant':'商品识别',
    'category':'类目 / 搜索','category_id':'类目 / 搜索','category_path':'类目 / 搜索','backend_terms':'类目 / 搜索','search_terms':'类目 / 搜索',
    'highlights':'购买决策','bullets':'购买决策','description':'购买决策','faq':'购买决策',
    'attributes':'事实 / 使用','usage':'事实 / 使用','ingredients':'事实 / 使用','warnings':'事实 / 使用','package':'事实 / 使用',
    'price':'Offer / 履约','offer':'Offer / 履约','shipping':'Offer / 履约','returns':'Offer / 履约','seller_info':'Offer / 履约',
}
'''

if '_delivery_task_scope' not in s:
    s=s.replace('\ndef compile_upload_center(project_dir:Path) -> dict[str,Any]:', helper+'\ndef compile_upload_center(project_dir:Path) -> dict[str,Any]:')

new_compile=r'''def compile_upload_center(project_dir:Path) -> dict[str,Any]:
    project=Path(project_dir)
    target=_target_summary(project); product=_product_summary(project)
    fields,localized_rows,comp=_latest_listing_fields(project)
    pc=_read_json(project/'artifacts/platform_compile.json',{})
    econ=_read_json(project/'artifacts/offer_economics.json',{})
    category=_category_contract(target,fields,pc)
    task_scope=_delivery_task_scope(project)
    delivery_locale=target.get('delivery_locale') or 'zh-CN'
    localized_map={(str(r.get('locale') or ''),str(r.get('field') or '')):r for r in localized_rows}
    primary_locale=str((comp.get('localization_transcreation') or {}).get('primary_locale') or target.get('locale') or '')
    values=dict(fields)
    for key,val in [('brand',product.get('brand')),('product_name',product.get('product_name')),('sku',product.get('sku'))]:
        if val not in (None,'',[],{}): values.setdefault(key,val)
    if category.get('name') not in (None,'',[],{}): values.setdefault('category',category.get('name'))
    if category.get('id') not in (None,'',[],{}): values.setdefault('category_id',category.get('id'))
    if category.get('path') not in (None,'',[],{}): values.setdefault('category_path',category.get('path'))
    if econ:
        price=_first(econ.get('price'),econ.get('selling_price'))
        if price not in (None,'',[],{}): values.setdefault('price',price)

    contracts={str(x.get('field')):x for x in (comp.get('field_contracts') or []) if isinstance(x,dict) and x.get('field')}
    required={k for k,v in contracts.items() if bool(v.get('required'))}
    submission_sensitive=bool(task_scope.get('listing_submission_sensitive'))
    submission_fields={'category','category_id','category_path'} if submission_sensitive else set()
    listing_active=bool(task_scope.get('listing_active'))

    # Preserve known data even when Listing is outside the current scope, but do not promote it into a blocking workspace.
    preserved=[{'field':k,'label':_FIELD_LABELS.get(k,k),'value':v} for k,v in values.items() if not str(k).startswith('_') and v not in (None,'',[],{})]
    if not listing_active:
        return {
            'version':'0.6.23','delivery_language':{'locale':delivery_locale,'default_rule':'默认中文交付；用户明确要求其他交付语言时覆盖。','foreign_copy_rule':'目标市场可见文案保持目标语言；人类交付同时显示中文释义/用途说明。'},
            'target':target,'product':product,'category':category,'task_scope':task_scope,
            'readiness':{'status':'NOT_IN_CURRENT_SCOPE','pending_count':0,'pending_fields':[],'optional_gap_count':0,'scope':'NON_LISTING_CURRENT_TASK'},
            'copy_center':[],'field_groups':[],'preserved_listing_fields':preserved,'localized_copy':localized_rows,
            'field_contracts':comp.get('field_contracts') or [],'platform_profile':comp.get('platform_native_listing_profile') or {},
            'media_slots':_extract_media(project),'risks_and_holds':_risk_summary(project),
            'human_rule':'当前任务不需要 Listing 时，上架字段不会占据主工作区或制造全项目 HOLD；已有 Listing 数据仍保留在结构化真源中。'
        }

    # Listing workspace is driven by supplied values + current platform-required fields + explicitly submission-sensitive fields.
    relevant=[]
    for field,value in values.items():
        if str(field).startswith('_'): continue
        if value not in (None,'',[],{}) and field not in relevant: relevant.append(field)
    for field in list(contracts):
        if field in required and field not in relevant: relevant.append(field)
    for field in submission_fields:
        if field not in relevant: relevant.append(field)

    preferred=['title','product_name','brand','sku','variant','category','category_id','category_path','highlights','bullets','description','attributes','backend_terms','search_terms','usage','ingredients','warnings','faq','package','price','offer','shipping','returns','seller_info']
    order=[x for x in preferred if x in relevant]+[x for x in relevant if x not in preferred]
    copy_center=[]
    for field in order:
        value=values.get(field)
        is_required=field in required or field in submission_fields
        if field in {'category','category_id','category_path'} and value not in (None,'',[],{}) and not category.get('exact_category_verified'):
            status='待查证' if is_required else '规划参考'
        elif value in (None,'',[],{}):
            status='待补' if is_required else '可选待补'
        else:
            status='READY'
        companion=(localized_map.get((primary_locale,field)) or {}) if primary_locale else {}
        delivery_translation=companion.get('delivery_translation'); delivery_note=companion.get('delivery_note')
        if field=='brand' and value not in (None,'',[],{}) and not delivery_translation:
            delivery_translation='品牌专名，无需翻译'; delivery_note='保留品牌官方写法。'
        if field=='sku' and value not in (None,'',[],{}) and not delivery_translation:
            delivery_translation='SKU 标识，无需翻译'; delivery_note='保留内部/平台 SKU 标识。'
        if field=='category_id' and value not in (None,'',[],{}) and not delivery_translation:
            delivery_translation='平台类目 ID，无需翻译'
        copy_center.append({
            'group':_FIELD_GROUPS.get(field,'其他平台字段'),'field':field,'label':_FIELD_LABELS.get(field,field),'value':value,'status':status,
            'required_for_current_scope':is_required,'copyable':value not in (None,'',[],{}),'locale':primary_locale or None,'delivery_locale':delivery_locale,
            'delivery_translation':delivery_translation,'delivery_note':delivery_note,
            'delivery_companion_status':('NOT_REQUIRED' if not primary_locale or str(primary_locale).casefold()==str(delivery_locale).casefold() else ('READY' if delivery_translation not in (None,'') else ('NOT_APPLICABLE_EMPTY' if value in (None,'',[],{}) else '待补中文释义')),
        })
    blocking=[x for x in copy_center if x.get('required_for_current_scope') and x.get('status') in {'待补','待查证'}]
    optional=[x for x in copy_center if not x.get('required_for_current_scope') and x.get('status') in {'可选待补','规划参考'}]
    groups=[]
    for name in ['商品识别','类目 / 搜索','购买决策','事实 / 使用','Offer / 履约','其他平台字段']:
        rows=[x for x in copy_center if x.get('group')==name]
        if rows: groups.append({'group':name,'fields':[x.get('field') for x in rows],'ready':sum(1 for x in rows if x.get('status')=='READY'),'pending':sum(1 for x in rows if x.get('status') in {'待补','待查证'})})
    return {
        'version':'0.6.23','delivery_language':{'locale':delivery_locale,'default_rule':'默认中文交付；用户明确要求其他交付语言时覆盖。','foreign_copy_rule':'目标市场可见文案保持目标语言；人类交付同时显示中文释义/用途说明。'},
        'target':target,'product':product,'category':category,'task_scope':task_scope,
        'readiness':{'status':'READY_WITH_HOLDS' if blocking else 'READY_FOR_CURRENT_SCOPE','pending_count':len(blocking),'pending_fields':[x['field'] for x in blocking],'optional_gap_count':len(optional),'optional_fields':[x['field'] for x in optional],'scope':'LISTING_CURRENT_TASK'},
        'copy_center':copy_center,'field_groups':groups,'preserved_listing_fields':preserved,'localized_copy':localized_rows,
        'field_contracts':comp.get('field_contracts') or [],'platform_profile':comp.get('platform_native_listing_profile') or {},
        'media_slots':_extract_media(project),'risks_and_holds':_risk_summary(project),
        'human_rule':'只让当前 Listing 任务真正要求的字段参与 readiness。已有但非当前任务必需的字段保留；未供应的可选字段不制造 HOLD。'
    }
'''
s=re.sub(r'def compile_upload_center\(project_dir:Path\) -> dict\[str,Any\]:.*?\n\ndef render_upload_center_md',new_compile+'\n\ndef render_upload_center_md',s,flags=re.S)

new_render=r'''def render_upload_center_md(center:dict[str,Any]) -> str:
    t=center.get('target') or {}; r=center.get('readiness') or {}; scope=center.get('task_scope') or {}
    lines=['# 上架资料中心','',f"> 当前范围：**{r.get('scope')}**｜状态：**{r.get('status')}**",'',
           '## 目标','',f"- 平台/站点：{_clean_text(_first(t.get('platform'),t.get('site'),'待查证'))}",f"- 市场：{_clean_text(t.get('market') or '待查证')}",f"- Locale：{_clean_text(t.get('locale') or '待查证')}",f"- 商品：{_human_product_label(center)}",'']
    if not scope.get('listing_active'):
        lines += ['## 当前任务不需要上架字段','', 'Listing 数据仍保留在项目真源中，但当前视觉 / 内容 / 生产任务不会因为价格、物流、退换货或卖家信息缺失而被标记为 HOLD。']
        kept=center.get('preserved_listing_fields') or []
        if kept:
            lines += ['','### 已保留的数据','']
            for x in kept[:20]: lines.append(f"- **{x.get('label')}**：{_clean_text(x.get('value'))}")
        return '\n'.join(lines)+'\n'
    lines += ['## 当前 Listing 工作字段','',f"真正阻断当前范围：{r.get('pending_count',0)} 项；可选/规划缺口：{r.get('optional_gap_count',0)} 项。",'']
    for group in center.get('field_groups') or []:
        rows=[x for x in center.get('copy_center') or [] if x.get('group')==group.get('group')]
        lines += [f"### {group.get('group')}",'','| 字段 | 目标市场内容 | 中文释义 / 用途 | 当前任务要求 | 状态 |','|---|---|---|---|---|']
        for x in rows:
            v=_clean_text(x.get('value')).replace('\n','<br>').replace('|','\\|') or '—'
            zh=_clean_text(x.get('delivery_translation') or ('同交付语言，无需另译' if x.get('delivery_companion_status')=='NOT_REQUIRED' else ('—' if x.get('value') in (None,'',[],{}) else '待补中文释义 / 用途'))).replace('\n','<br>').replace('|','\\|')
            lines.append(f"| {x.get('label')} | {v} | {zh} | {'是' if x.get('required_for_current_scope') else '否'} | {x.get('status')} |")
        lines.append('')
    if center.get('risks_and_holds'):
        lines += ['## 风险 / 待查证','']
        for x in center['risks_and_holds'][:30]: lines.append(f"- **{x.get('status')}** · {x.get('source')}/{x.get('type')}：{x.get('item')}")
    return '\n'.join(lines)+'\n'
'''
s=re.sub(r'def render_upload_center_md\(center:dict\[str,Any\]\) -> str:.*?\n\ndef build_project_hub_md',new_render+'\n\ndef build_project_hub_md',s,flags=re.S)

new_hub=r'''def build_project_hub_md(center:dict[str,Any], strategy_path:str='strategy/MASTER_STRATEGY_CN.md') -> str:
    t=center.get('target') or {}; r=center.get('readiness') or {}; scope=center.get('task_scope') or {}
    assets=center.get('media_slots') or []; risks=center.get('risks_and_holds') or []
    lines=['# 项目总控台','',f"**{_human_product_label(center)}**",'',
           f"平台：{_clean_text(_first(t.get('platform'),t.get('site'),'待查证'))}｜市场：{_clean_text(t.get('market') or '待查证')}｜目标Locale：{_clean_text(t.get('locale') or '待查证')}｜交付语言：{_clean_text(t.get('delivery_locale') or 'zh-CN')}",'',
           '## 当前任务','',f"- 内容/能力范围：{', '.join(scope.get('families') or []) or '由当前项目对象动态决定'}",f"- Agent 下一动作：{scope.get('recommended_next_action') or '当前范围可停止或由 Agent 自主选择'}",f"- 已规划资产：{len(assets)}",f"- 开放风险/待查证：{len(risks)}",'']
    if scope.get('listing_active'):
        ready=sum(1 for x in center.get('copy_center') or [] if x.get('status')=='READY')
        lines += ['## Listing 当前范围','',f"- 状态：{r.get('status')}；当前要求字段中阻断 {r.get('pending_count',0)} 项；已就绪 {ready} 项；可选/规划缺口 {r.get('optional_gap_count',0)} 项。",'']
    else:
        lines += ['## Listing 当前范围','', '- 当前任务未激活 Listing；Listing 字段不参与项目 readiness。已有数据保留，但不会抢占视觉 / 内容 / 生产主任务。','']
    frontier=scope.get('frontier') or []
    if frontier:
        lines += ['## Agent 识别的高价值下一动作','']
        for item in frontier:
            lines.append(f"- **{item.get('action') or 'NEXT'}**：{item.get('reason') or '继续处理当前未解决条件。'}")
        lines.append('')
    if assets:
        lines += ['## 资产速览','', '| 资产 ID | 展示位置（Surface） | 角色 | 状态 |','|---|---|---|---|']
        for a in assets[:30]: lines.append(f"| {a.get('asset_id') or '—'} | {a.get('surface') or '—'} | {_clean_text(a.get('role') or a.get('title') or '—').replace('|','\\|')} | {a.get('status') or '—'} |")
        lines.append('')
    if risks:
        lines += ['## 当前风险 / 待查证','']
        for x in risks[:12]: lines.append(f"- **{x.get('status')}** {x.get('item')}")
        lines.append('')
    lines += ['## 深度文件','',f"- 完整策略：`{strategy_path}`",'- 上架资料（仅当前范围需要时使用）：`01_LISTING_UPLOAD_READY.md`','- 逐资产：`asset_packages/` 或 `assets/`','- 支撑分析：`supporting_analysis/`','','> 交付原则：**当前商业任务决定主工作面；结构化真源负责保存，不反过来规定用户必须先看什么。**']
    return '\n'.join(lines)+'\n'
'''
s=re.sub(r'def build_project_hub_md\(center:dict\[str,Any\], strategy_path:str=.*',new_hub,s,flags=re.S)
p.write_text(s,encoding='utf-8')

# --- tools/listing.py ---
p=ROOT/'runtime/cbcc/tools/listing.py'
s=p.read_text(encoding='utf-8')
new_arch=r'''def listing_conversion_architecture(fields:dict[str,Any], keywords:dict[str,Any], objections:list[dict[str,Any]]|None=None, rules:dict[str,Any]|None=None)->dict[str,Any]:
    objections=objections or []; rules=rules or {}
    names=[str(k) for k,v in fields.items() if not str(k).startswith('_') and v not in (None,'',[],{})]
    for k,v in rules.items():
        if isinstance(v,dict) and v.get('required') and str(k) not in names: names.append(str(k))
    decision_map=field_decision_map(fields,rules)
    click_candidates=['title','brand','product_name','price','variant']
    click_fields=[x for x in click_candidates if x in names]
    if not click_fields:
        click_fields=[row.get('field') for row in decision_map if 'IDENTIFY' in str(row.get('decision_job') or '')][:3]
    post_candidates=['faq','usage','package','attributes','warnings','shipping','returns']
    post_fields=[x for x in post_candidates if x in names]
    return {
        'search_layer':{
            'job':'Match high-priority search intent while preserving readable product identity.',
            'keyword_priority':keyword_priority_plan(keywords),
            'why':'Search fields establish relevance before persuasive depth; keyword coverage without clarity can reduce click quality.'
        },
        'click_layer':{
            'job':'Make the exact product and first reason-to-click immediately legible.',
            'fields':click_fields,
            'dynamic_from_current_fields':True,
            'why':'Click surfaces only expose fields that actually exist or are required for this Listing contract; no price/variant/image slot is manufactured for completeness.'
        },
        'decision_layer':{
            'job':'Sequence relevance, benefit, proof, fit and objection resolution.',
            'field_decision_map':decision_map,
            'objections':objection_resolution_plan(objections),
            'why':'PDP/listing content should answer the next buyer question rather than repeat the same selling point across fields.'
        },
        'post_purchase_prevention':{
            'job':'Clarify package contents, usage, compatibility, size and expectations before purchase when relevant.',
            'fields':post_fields,
            'dynamic_from_current_fields':True,
            'why':'Expectation fields appear only when supplied/required/relevant; the runtime does not invent a universal after-sales checklist.'
        },
        'active_fields':names,
        'fixed_field_quota':None,
    }
'''
s=re.sub(r'def listing_conversion_architecture\(fields:dict\[str,Any\], keywords:dict\[str,Any\], objections:list\[dict\[str,Any\]\]\|None=None, rules:dict\[str,Any\]\|None=None\)->dict\[str,Any\]:.*?\n\ndef keyword_coverage',new_arch+'\n\ndef keyword_coverage',s,flags=re.S)
p.write_text(s,encoding='utf-8')

# --- compiler version marker ---
p=ROOT/'runtime/cbcc/compiler.py'
s=p.read_text(encoding='utf-8')
s=s.replace("st.data['runtime_version']='0.6.21-commerce-agent-autonomy'","st.data['runtime_version']='0.6.23-task-scoped-delivery'")
p.write_text(s,encoding='utf-8')

# --- targeted tests ---
t=ROOT/'tests/test_v0623_task_scoped_delivery.py'
t.write_text(r'''from pathlib import Path
import json

from cbcc.human_delivery import compile_upload_center, build_project_hub_md
from cbcc.tools.listing import listing_conversion_architecture


def _write(path:Path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')


def _base_project(tmp_path:Path):
    _write(tmp_path/'artifacts/product_truth.json',{'product':{'brand':'KIYUU','product_name':'K01 Gel','sku':'K01'}})
    _write(tmp_path/'artifacts/target_context.json',{'market':'MY','platform_family':'TikTok Shop','site':'MY','language':{'primary_locale':'en-MY','delivery_locale':'zh-CN'}})
    _write(tmp_path/'artifacts/platform_compile.json',{})
    return tmp_path


def test_visual_only_scope_does_not_manufacture_listing_holds(tmp_path):
    p=_base_project(tmp_path)
    _write(p/'meta/request.json',{'project_id':'V','content_families':['VISUAL'],'compile_assets':True,'goal':'制作商品视觉资产'})
    _write(p/'artifacts/agent_autonomy_plan.json',{'content_scope':{'families':['VISUAL']}})
    _write(p/'artifacts/agent_next_action.json',{'status':'ACTION_FRONTIER_OPEN','recommended_next_action':'REPLAN_ASSET_ARCHITECTURE','frontier':[{'action':'REPLAN_ASSET_ARCHITECTURE','reason':'资产需要继续规划'}]})
    center=compile_upload_center(p)
    assert center['task_scope']['listing_active'] is False
    assert center['readiness']['status']=='NOT_IN_CURRENT_SCOPE'
    assert center['copy_center']==[]
    preserved={x['field'] for x in center['preserved_listing_fields']}
    assert {'brand','product_name','sku'} <= preserved
    for field in ['price','shipping','returns','seller_info']:
        assert field not in preserved
    hub=build_project_hub_md(center)
    assert 'Listing 字段不参与项目 readiness' in hub
    assert 'REPLAN_ASSET_ARCHITECTURE' in hub


def test_listing_scope_only_blocks_current_required_fields(tmp_path):
    p=_base_project(tmp_path)
    _write(p/'meta/request.json',{'project_id':'L','content_families':['LISTING'],'listing_input':{'fields':{'title':'KIYUU K01 Gel'}}})
    _write(p/'artifacts/agent_autonomy_plan.json',{'content_scope':{'families':['LISTING']}})
    _write(p/'artifacts/listing_analysis.json',{'compiled':{'fields':{'title':'KIYUU K01 Gel'},'field_contracts':[{'field':'title','required':True},{'field':'shipping','required':True}],'localization_transcreation':{'primary_locale':'en-MY'}}})
    center=compile_upload_center(p)
    rows={x['field']:x for x in center['copy_center']}
    assert center['task_scope']['listing_active'] is True
    assert center['readiness']['status']=='READY_WITH_HOLDS'
    assert center['readiness']['pending_fields']==['shipping']
    assert rows['shipping']['required_for_current_scope'] is True
    for optional in ['price','returns','seller_info']:
        assert optional not in rows


def test_listing_scope_without_platform_requirement_does_not_invent_offer_ops(tmp_path):
    p=_base_project(tmp_path)
    _write(p/'meta/request.json',{'project_id':'L2','content_families':['LISTING'],'listing_input':{'fields':{'title':'KIYUU K01 Gel','description':'Daily gel'}}})
    _write(p/'artifacts/agent_autonomy_plan.json',{'content_scope':{'families':['LISTING']}})
    _write(p/'artifacts/listing_analysis.json',{'compiled':{'fields':{'title':'KIYUU K01 Gel','description':'Daily gel'},'field_contracts':[{'field':'title','required':True}],'localization_transcreation':{'primary_locale':'en-MY'}}})
    center=compile_upload_center(p)
    assert center['readiness']['status']=='READY_FOR_CURRENT_SCOPE'
    fields={x['field'] for x in center['copy_center']}
    assert 'title' in fields and 'description' in fields
    assert not ({'price','shipping','returns','seller_info'} & fields)


def test_listing_conversion_architecture_projects_only_active_fields():
    arch=listing_conversion_architecture({'title':'A','description':'B'}, {}, [], {})
    assert arch['click_layer']['fields']==['title']
    assert arch['post_purchase_prevention']['fields']==[]
    assert arch['fixed_field_quota'] is None
    arch2=listing_conversion_architecture({'title':'A','faq':'Q'}, {}, [], {'shipping':{'required':True}})
    assert arch2['post_purchase_prevention']['fields']==['faq','shipping']
    assert 'price' not in arch2['click_layer']['fields']
''',encoding='utf-8')

print('v0.6.23 patch materialized')
