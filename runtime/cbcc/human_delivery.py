from __future__ import annotations
from pathlib import Path
from typing import Any
import json, re


def _read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {} if default is None else default


def _first(*vals):
    for v in vals:
        if v not in (None, '', [], {}):
            return v
    return None


def _clean_text(v):
    if isinstance(v, list): return '\n'.join(str(x) for x in v)
    if isinstance(v, dict): return json.dumps(v, ensure_ascii=False, indent=2)
    return '' if v is None else str(v)


def _human_product_label(center:dict[str,Any]) -> str:
    p=center.get('product') or {}; brand=str(p.get('brand') or '').strip(); name=str(p.get('product_name') or '').strip()
    # Prefer the Chinese delivery companion when one exists.
    for row in center.get('copy_center') or []:
        if row.get('field')=='product_name' and row.get('delivery_translation') not in (None,''):
            name=str(row.get('delivery_translation')).strip(); break
    if brand and name.casefold().startswith(brand.casefold()): return name
    return ' '.join(x for x in [brand,name] if x).strip() or '商品项目'


def _target_summary(project: Path) -> dict[str, Any]:
    target=_read_json(project/'artifacts/target_context.json',{})
    pc=_read_json(project/'artifacts/platform_compile.json',{})
    t=target.get('target') if isinstance(target.get('target'),dict) else target
    market=_first(t.get('market'), t.get('country'), target.get('market'))
    platform=_first(t.get('platform'), t.get('platform_family'), pc.get('platform_family'), pc.get('platform'))
    site=_first(t.get('site'), t.get('site_id'), pc.get('site'), pc.get('site_id'))
    language=t.get('language') if isinstance(t.get('language'),dict) else (target.get('language') if isinstance(target.get('language'),dict) else (target.get('language_contract') or {}))
    locale=_first(t.get('locale'), t.get('primary_locale'), language.get('primary_locale'))
    delivery_locale=_first(t.get('delivery_locale'), language.get('delivery_locale'), 'zh-CN')
    visible_locales=language.get('visible_copy_locales') or ([locale] if locale else [])
    category=_first(t.get('category'), t.get('category_name'), t.get('category_path'), pc.get('category'), pc.get('category_name'))
    category_id=_first(t.get('category_id'), pc.get('category_id'))
    return {'market':market,'platform':platform,'site':site,'locale':locale,'delivery_locale':delivery_locale,'visible_copy_locales':visible_locales,'category':category,'category_id':category_id}


def _product_summary(project: Path) -> dict[str, Any]:
    pt=_read_json(project/'artifacts/product_truth.json',{})
    data=pt.get('product') if isinstance(pt.get('product'),dict) else pt
    facts=pt.get('facts') if isinstance(pt.get('facts'),dict) else {}
    return {
        'brand': _first(data.get('brand'), facts.get('brand')),
        'product_name': _first(data.get('product_name'), data.get('name'), facts.get('product_name'), facts.get('name')),
        'sku': _first(data.get('sku'), facts.get('sku')),
        'size': _first(data.get('size'), data.get('net_content'), facts.get('size'), facts.get('net_content')),
        'product_type': _first(data.get('product_type'), data.get('category'), facts.get('product_type')),
    }


def _latest_listing_fields(project: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    analysis=_read_json(project/'artifacts/listing_analysis.json',{})
    comp=analysis.get('compiled') if isinstance(analysis.get('compiled'),dict) else analysis
    base=dict(comp.get('fields') or {})
    workflow=_read_json(project/'artifacts/listing_final_copy.json',{})
    packages=workflow.get('packages') or []
    # Prefer approved/final authored copy, otherwise show current draft with status.
    chosen={}
    rows=[]
    for pkg in packages:
        locale=str(pkg.get('locale') or '')
        for r in pkg.get('fields') or []:
            field=str(r.get('field') or '')
            value=r.get('authored_copy') if r.get('authored_copy') not in (None,'') else r.get('source_value')
            status=r.get('release_status') or pkg.get('status')
            row={'locale':locale,'field':field,'value':value,'status':status,'version':r.get('current_version_id'),'delivery_locale':r.get('delivery_locale') or workflow.get('delivery_locale') or 'zh-CN','delivery_translation':r.get('delivery_translation'),'delivery_note':r.get('delivery_note'),'delivery_companion_status':r.get('delivery_companion_status')}
            rows.append(row)
            if value not in (None,''):
                rank=2 if status=='APPROVED_FINAL' else 1
                key=(locale,field)
                if key not in chosen or rank>chosen[key][0]: chosen[key]=(rank,value,status)
    primary_locale=''
    lc=comp.get('localization_transcreation') or {}
    primary_locale=str(lc.get('primary_locale') or '')
    if not primary_locale and packages: primary_locale=str(packages[0].get('locale') or '')
    merged=dict(base)
    for (loc,field),(rank,value,status) in chosen.items():
        if not primary_locale or loc==primary_locale:
            merged[field]=value
    return merged, rows, comp


def _category_contract(target:dict[str,Any], listing_fields:dict[str,Any], platform_compile:dict[str,Any]) -> dict[str,Any]:
    # Planning category (e.g. "beauty") is not the same thing as the exact Seller Center upload category.
    explicit_name=_first(listing_fields.get('platform_category'), listing_fields.get('category_name'), platform_compile.get('category_name'))
    cid=_first(listing_fields.get('category_id'), target.get('category_id'), platform_compile.get('category_id'))
    path=_first(listing_fields.get('category_path'), platform_compile.get('category_path'))
    planning_category=_first(target.get('category'), platform_compile.get('category'), listing_fields.get('category'))
    exact_verified=bool(cid or path or platform_compile.get('category_tree_verified') or platform_compile.get('exact_category_verified'))
    name=explicit_name if explicit_name not in (None,'') else planning_category
    status='READY' if exact_verified and (name or cid or path) else '待查证'
    return {'name':name,'id':cid,'path':path,'planning_category':planning_category,'status':status,'exact_category_verified':exact_verified,'rule':'规划品类不等于平台精确上架类目。平台对应类目必须来自当前站点 Seller Center/类目树或用户提供的已验证类目；只有泛化 category 时继续标待查证，不猜。'}


def _extract_media(project:Path) -> list[dict[str,Any]]:
    arch=_read_json(project/'artifacts/asset_architecture.json',{})
    assets=arch.get('assets') or []
    out=[]
    for a in assets:
        out.append({
            'asset_id':a.get('asset_id'),
            'surface':a.get('surface') or a.get('surface_id'),
            'role':a.get('decision_intent') or a.get('role') or a.get('consumer_question'),
            'title':a.get('title') or a.get('name'),
            'status':a.get('status') or 'PLANNED',
            'product_presence':a.get('product_presence'),
        })
    return out


def _risk_summary(project:Path) -> list[dict[str,Any]]:
    compliance=_read_json(project/'artifacts/compliance_report.json',{})
    research=_read_json(project/'artifacts/research_gate.json',{})
    out=[]
    for src,label in [(compliance,'COMPLIANCE'),(research,'RESEARCH')]:
        for key in ['issues','blockers','holds','actions','research_actions','warnings']:
            vals=src.get(key) or []
            if isinstance(vals,dict): vals=[vals]
            for x in vals:
                if isinstance(x,dict):
                    out.append({'source':label,'type':key,'item':_first(x.get('message'),x.get('reason'),x.get('task'),x.get('action'),x.get('code'),x.get('rule_id'),str(x)),'status':x.get('status') or ('HOLD' if key in {'blockers','holds'} else 'OPEN')})
                else: out.append({'source':label,'type':key,'item':str(x),'status':'OPEN'})
    return out[:100]


def compile_upload_center(project_dir:Path) -> dict[str,Any]:
    project=Path(project_dir)
    target=_target_summary(project); product=_product_summary(project)
    fields,localized_rows,comp=_latest_listing_fields(project)
    pc=_read_json(project/'artifacts/platform_compile.json',{})
    econ=_read_json(project/'artifacts/offer_economics.json',{})
    category=_category_contract(target,fields,pc)
    delivery_locale=target.get('delivery_locale') or 'zh-CN'
    localized_map={(str(r.get('locale') or ''),str(r.get('field') or '')):r for r in localized_rows}
    primary_locale=str((comp.get('localization_transcreation') or {}).get('primary_locale') or target.get('locale') or '')
    canonical=[
        ('title','产品标题'),('product_name','商品名称'),('brand','品牌'),('category','平台类目'),('category_id','类目ID'),('category_path','类目路径'),
        ('highlights','核心卖点'),('bullets','卖点'),('description','商品描述'),('attributes','属性'),('backend_terms','后台关键词'),('search_terms','搜索词'),
        ('usage','使用方法'),('ingredients','成分'),('warnings','警示'),('faq','FAQ'),('package','包装/包含物'),('sku','SKU'),('variant','变体'),('price','价格'),('offer','优惠/Offer'),
        ('shipping','物流承诺'),('returns','退换货/售后'),('seller_info','卖家/责任方信息'),
    ]
    values=dict(fields)
    values.setdefault('brand',product.get('brand')); values.setdefault('product_name',product.get('product_name')); values.setdefault('sku',product.get('sku'))
    values['category']=category.get('name'); values['category_id']=category.get('id'); values['category_path']=category.get('path')
    if econ:
        values.setdefault('price',_first(econ.get('price'),econ.get('selling_price')))
    copy_center=[]
    used=set()
    for field,label in canonical:
        value=values.get(field)
        if field in {'category','category_id','category_path'}:
            status=category.get('status') if field=='category' else ('READY' if value not in (None,'',[],{}) and category.get('exact_category_verified') else '待查证')
        elif value in (None,'',[],{}):
            status='待查证' if field in {'price','shipping','returns','seller_info'} else '待补'
        else: status='READY'
        companion=(localized_map.get((primary_locale,field)) or {}) if primary_locale else {}
        delivery_translation=companion.get('delivery_translation'); delivery_note=companion.get('delivery_note')
        if field=='brand' and value not in (None,'',[],{}) and not delivery_translation:
            delivery_translation='品牌专名，无需翻译'; delivery_note='保留品牌官方写法。'
        if field=='sku' and value not in (None,'',[],{}) and not delivery_translation:
            delivery_translation='SKU 标识，无需翻译'; delivery_note='保留内部/平台 SKU 标识。'
        if field=='category_id' and value not in (None,'',[],{}) and not delivery_translation:
            delivery_translation='平台类目 ID，无需翻译'
        if field=='category' and not delivery_translation and str(value or '').casefold()=='beauty':
            delivery_translation='美妆（规划品类；平台精确上架类目待查证）'; delivery_note='这是规划层品类，不代表 Seller Center 的最终类目名称/ID/路径。'
        copy_center.append({'group':'上架资料','field':field,'label':label,'value':value,'status':status,'copyable':value not in (None,'',[],{}),'locale':primary_locale or None,'delivery_locale':delivery_locale,'delivery_translation':delivery_translation,'delivery_note':delivery_note,'delivery_companion_status':('NOT_REQUIRED' if not primary_locale or str(primary_locale).casefold()==str(delivery_locale).casefold() else ('READY' if delivery_translation not in (None,'') else '待补中文释义'))})
        used.add(field)
    for k,v in values.items():
        if k in used or str(k).startswith('_'): continue
        copy_center.append({'group':'其他平台字段','field':k,'label':k,'value':v,'status':'READY' if v not in (None,'',[],{}) else '待补','copyable':v not in (None,'',[],{}),'locale':primary_locale or None,'delivery_locale':delivery_locale,'delivery_translation':None,'delivery_companion_status':('NOT_APPLICABLE_EMPTY' if v in (None,'',[],{}) else ('NOT_REQUIRED' if not primary_locale or str(primary_locale).casefold()==str(delivery_locale).casefold() else '待补中文释义'))})
    hard_pending=[x for x in copy_center if x['status']=='待查证']
    return {
        'version':'0.6.6','delivery_language':{'locale':delivery_locale,'default_rule':'默认中文交付；用户明确要求其他交付语言时覆盖。','foreign_copy_rule':'目标市场可见文案保持目标语言；人类交付同时显示中文释义/用途说明。'},'target':target,'product':product,'category':category,
        'readiness':{'status':'READY_WITH_HOLDS' if hard_pending else 'READY','pending_count':len(hard_pending),'pending_fields':[x['field'] for x in hard_pending]},
        'copy_center':copy_center,'localized_copy':localized_rows,
        'field_contracts':comp.get('field_contracts') or [],'platform_profile':comp.get('platform_native_listing_profile') or {},
        'media_slots':_extract_media(project),'risks_and_holds':_risk_summary(project),
        'human_rule':'中文是默认项目交付语言。目标市场文案可以是 BM/EN/AR 等，但必须在同一界面同时显示中文释义或用途说明；用户不需要掌握目标语言才能评审和执行。'
    }


def render_upload_center_md(center:dict[str,Any]) -> str:
    t=center.get('target') or {}; p=center.get('product') or {}; r=center.get('readiness') or {}
    lines=['# 上架资料中心','',f"> 状态：**{r.get('status')}**｜待查证字段：{r.get('pending_count',0)}",'',
           '## 目标','',f"- 平台/站点：{_clean_text(_first(t.get('platform'),t.get('site'),'待查证'))}",f"- 市场：{_clean_text(t.get('market') or '待查证')}",f"- Locale：{_clean_text(t.get('locale') or '待查证')}",f"- 商品：{_human_product_label(center)}",'']
    lines += ['## 一页上架字段','', '| 字段 | 目标语言 | 目标文案 | 中文释义 / 用途 | 状态 |','|---|---|---|---|---|']
    for x in center.get('copy_center') or []:
        v=_clean_text(x.get('value')).replace('\n','<br>').replace('|','\\|') or '—'
        if x.get('value') in (None,'',[],{}): zh='—'
        else: zh=_clean_text(x.get('delivery_translation') or ('同交付语言，无需另译' if x.get('delivery_companion_status')=='NOT_REQUIRED' else '待补中文释义 / 用途')).replace('\n','<br>').replace('|','\\|')
        lines.append(f"| {x.get('label')} | {x.get('locale') or '—'} | {v} | {zh} | {x.get('status')} |")
    lines += ['','## 平台类目','',f"- 类目名称：{_clean_text((center.get('category') or {}).get('name') or '待查证')}",f"- 类目 ID：{_clean_text((center.get('category') or {}).get('id') or '待查证')}",f"- 类目路径：{_clean_text((center.get('category') or {}).get('path') or '待查证')}",f"- 规则：{(center.get('category') or {}).get('rule')}"]
    if center.get('media_slots'):
        lines += ['','## 媒体/资产槽位','', '| 资产 ID | 展示位置（Surface） | 角色 | 状态 |','|---|---|---|---|']
        for a in center['media_slots']:
            lines.append(f"| {a.get('asset_id') or '—'} | {a.get('surface') or '—'} | {_clean_text(a.get('role') or a.get('title') or '—').replace('|','\\|')} | {a.get('status') or '—'} |")
    if center.get('risks_and_holds'):
        lines += ['','## 风险 / 待补 / 待查证','']
        for x in center['risks_and_holds'][:30]: lines.append(f"- **{x.get('status')}** · {x.get('source')}/{x.get('type')}：{x.get('item')}")
    lines += ['','---','','> 单字段/逐资产文件仍保留，用于版本、修改和生产；正常上架与项目评审优先看本文件或 `index.html`。']
    return '\n'.join(lines)+'\n'


def build_project_hub_md(center:dict[str,Any], strategy_path:str='strategy/MASTER_STRATEGY_CN.md') -> str:
    t=center.get('target') or {}; p=center.get('product') or {}; r=center.get('readiness') or {}
    assets=center.get('media_slots') or []; risks=center.get('risks_and_holds') or []
    ready=sum(1 for x in center.get('copy_center') or [] if x.get('status')=='READY')
    pending=sum(1 for x in center.get('copy_center') or [] if x.get('status')!='READY')
    lines=['# 项目总控台','',
           f"**{_human_product_label(center)}**",'',
           f"平台：{_clean_text(_first(t.get('platform'),t.get('site'),'待查证'))}｜市场：{_clean_text(t.get('market') or '待查证')}｜目标Locale：{_clean_text(t.get('locale') or '待查证')}｜交付语言：{_clean_text(t.get('delivery_locale') or 'zh-CN')}",'',
           '## 先看这四件事','',
           f"- **上架状态**：{r.get('status')}；字段 READY {ready}，待补/待查证 {pending}。",
           f"- **平台类目**：{_clean_text(_first((center.get('category') or {}).get('path'),(center.get('category') or {}).get('name'),'待查证'))}",
           f"- **资产数量**：{len(assets)} 个已规划媒体资产。",
           f"- **风险/待办**：{len(risks)} 项开放事项。",'',
           '## 正常使用路径','',
           '1. **要上架** → 直接进入 HTML 的「上架资料」，所有可复制字段集中呈现。','2. **要看全局策略** → 进入 HTML 的「策略」页面，完整正文已内嵌。','3. **要做图/视频** → 进入 HTML 的「资产库」并打开对应 资产详情页；设计卡、摄影合同、中英文提示词与生产说明均在同一 HTML 内。','4. **要改东西** → 按具体字段 / 资产 ID 修改；Markdown/JSON 是可编辑与机器真源，不是理解项目的前置步骤。','',
           '## 上架关键字段速览','', '| 字段 | 目标市场内容 | 中文释义 / 用途 | 状态 |','|---|---|---|---|']
    for x in (center.get('copy_center') or [])[:14]:
        val=_clean_text(x.get('value')).replace('\n',' / ').replace('|','\\|')
        if len(val)>180: val=val[:177]+'...'
        zh=_clean_text(x.get('delivery_translation') or ('同交付语言，无需另译' if x.get('delivery_companion_status')=='NOT_REQUIRED' else ('—' if x.get('value') in (None,'',[],{}) else '待补中文释义 / 用途'))).replace('\n',' / ').replace('|','\\|')
        if len(zh)>180: zh=zh[:177]+'...'
        lines.append(f"| {x.get('label')} | {val or '—'} | {zh or '—'} | {x.get('status')} |")
    lines += ['','## 资产速览','', '| 资产 ID | 展示位置（Surface） | 角色 | 状态 |','|---|---|---|---|']
    for a in assets[:30]: lines.append(f"| {a.get('asset_id') or '—'} | {a.get('surface') or '—'} | {_clean_text(a.get('role') or a.get('title') or '—').replace('|','\\|')} | {a.get('status') or '—'} |")
    if risks:
        lines += ['','## 当前风险 / 待查证','']
        for x in risks[:12]: lines.append(f"- **{x.get('status')}** {x.get('item')}")
    lines += ['','## 深度文件','',f"- 完整策略：`{strategy_path}`",'- 上架资料：`01_LISTING_UPLOAD_READY.md`','- 逐资产：`asset_packages/` 或 `assets/`','- 支撑分析：`supporting_analysis/`','','> 交付原则：**一个入口看全局，一个上架中心直接复制，单文件只用于下钻。**']
    return '\n'.join(lines)+'\n'
