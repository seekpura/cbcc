from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import json, re

MARKER='CBCC_CANONICAL_HUMAN_PROJECTION_V0670'


def _extract_embedded_data(text:str)->dict[str,Any]:
    m=re.search(r'\bconst\s+DATA\s*=\s*',text)
    if not m:return {}
    dec=json.JSONDecoder()
    try:
        obj,_=dec.raw_decode(text[m.end():])
        return obj if isinstance(obj,dict) else {}
    except Exception:return {}


def _json(value:Any)->str:
    return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')


def apply_canonical_human_projection_to_existing_html(html_path:Path|str, data:Mapping[str,Any]|None=None)->dict[str,Any]:
    """Mount a lossless Human projection onto the existing project-authored cbcc-commercial-v1 world.

    This intentionally does not replace the project's navigation/world. It overrides only business-object
    renderers and workspace tools that were lossy in the legacy export. No facts are invented: the script
    can render only values already present in the supplied/embedded canonical DATA object.
    """
    path=Path(html_path)
    if not path.exists():return {'status':'NOT_FOUND','path':str(path)}
    text=path.read_text(encoding='utf-8',errors='ignore')
    if MARKER in text:return {'status':'PASS','already_applied':True,'path':str(path)}
    payload=dict(data or {}) or _extract_embedded_data(text)
    if not payload:return {'status':'INCOMPLETE','issues':['CANONICAL_HUMAN_DATA_MISSING'],'path':str(path)}

    script=r'''
<script id="cbcc-canonical-human-projection-v0670">
/* CBCC_CANONICAL_HUMAN_PROJECTION_V0670 */
const CBCC_CANONICAL_HUMAN=__PAYLOAD__;
(function(){
  const D=CBCC_CANONICAL_HUMAN;
  const e=(v)=>typeof esc==='function'?esc(v):String(v??'');
  const sec=(t,d='')=>typeof section==='function'?section(t,d):`<h2>${e(t)}</h2><p>${e(d)}</p>`;
  const tbl=(rows,cols)=>typeof table==='function'?table(rows||[],cols):'';
  const arr=(v)=>Array.isArray(v)?v:[];
  const obj=(v)=>v&&typeof v==='object'&&!Array.isArray(v)?v:{};
  const pairs=(v)=>Object.entries(obj(v)).map(([key,value])=>({key,value:typeof value==='object'?JSON.stringify(value,null,2):String(value??'')}));
  const join=(v)=>Array.isArray(v)?v.join('；'):String(v??'');
  const pretty=(v)=>typeof v==='string'?v:JSON.stringify(v??{},null,2);
  function cbccCopy(btn){const raw=decodeURIComponent(btn.dataset.copyPayload||'');navigator.clipboard.writeText(raw);const old=btn.textContent;btn.textContent='已复制';setTimeout(()=>btn.textContent=old,900)}
  window.cbccCopy=cbccCopy;
  function copyPane(text){return `<div class="pre" style="position:relative"><button class="copybtn" data-copy-payload="${encodeURIComponent(String(text??''))}" onclick="cbccCopy(this)">复制</button>${e(text)}</div>`}

  if(typeof launch==='function') launch=function(){
    const info=obj(D.info); const audit=obj(info.information_audit); const p=arr(info.pending_confirmations); const a=arr(info.assumptions_and_decisions);
    let out=typeof hero==='function'?hero():'';
    out+=sec('信息完整度 / 待确认','最多10项待确认；其余工作在明确假设下继续。')+tbl(p,[['priority','优先级'],['item','缺失输入'],['impact','影响']]);
    out+=sec('假设与决策日志')+tbl(a,[['status','状态'],['decision','事实/假设/决策'],['why','依据 / WHY'],['verify','验证']]);
    if(Object.keys(audit).length){
      out+=sec('产品事实原始审计')+tbl(pairs(audit),[['key','字段'],['value','权威值']]);
    }
    const comp=obj(D.compliance); out+=sec('P0 宣称 / 法规矩阵')+tbl(comp.claim_rows||[],[['area','领域'],['status','状态'],['allowed','可用边界'],['blocked','禁止/缺失'],['evidence','证据']]);
    return out;
  };

  if(typeof whybuy==='function') whybuy=function(){
    const truth=obj(D.truth), S=obj(obj(D.strategy).strategy), econ=obj(obj(D.strategy).economics);
    let out=sec('购买理由','Product Truth → Value → Strategy；C级不得形成硬宣称。');
    if(S.positioning)out+=`<div class="quote">${e(S.positioning)}</div>`;
    out+=sec('产品事实与价值分级')+tbl(truth.truth_value_table||truth.product_truth_audit_table||[],[['type','类型'],['statement','内容'],['grade','证据等级'],['basis','依据'],['publication','发布规则']]);
    if(S.value_proposition)out+=sec('价值主张')+`<div class="quote">${e(S.value_proposition)}</div>`;
    if(arr(S.message_hierarchy).length)out+=sec('信息层级')+tbl(arr(S.message_hierarchy).map((x,i)=>({n:i+1,message:x})),[['n','#'],['message','信息']]);
    out+=sec('框架如何改变决策')+tbl(S.frameworks||[],[['framework','框架'],['role','作用'],['basis','依据'],['tradeoff','取舍'],['execution','执行'],['metric','指标']]);
    out+=sec('P0 / P1 / P2 资源取舍')+tbl(S.priority_tradeoff||[],[['level','等级'],['keep','保什么'],['defer','砍/延后什么'],['why','为什么'],['restore','何时恢复']]);
    if(Object.keys(econ).length)out+=sec('Economics / Offer 边界')+tbl(pairs(econ),[['key','对象'],['value','内容']]);
    return out;
  };

  if(typeof malaysia==='function') malaysia=function(){
    const l=obj(D.listing), m=obj(D.market), c=obj(D.culture); let out=sec('Malaysia 上架信息','BM主层；EN语义基线；中文运营释义。');
    const title=obj(l.title);
    out+=`<div class="grid"><div class="card span12"><h3>标题 / Title</h3><p><b>BM：</b>${e(title.bm)}</p><p><b>EN：</b>${e(title.en)}</p><p><b>中文：</b>${e(title.cn)}</p></div>`+
      `<div class="card span4"><h3>Description / BM</h3><p>${e(l.description_bm)}</p></div><div class="card span4"><h3>Description / EN</h3><p>${e(l.description_en)}</p></div><div class="card span4"><h3>中文释义</h3><p>${e(l.description_cn)}</p></div></div>`;
    out+=sec('Key Points / 卖点')+tbl(l.key_points||[],[['bm','BM'],['en','EN'],['cn','中文']]);
    out+=sec('上架属性')+tbl(pairs(l.attributes),[['key','属性'],['value','值']]);
    const pc=obj(l.package_contents); if(Object.keys(pc).length)out+=sec('实收内容 / Package Contents')+tbl([{bm:pc.bm,en:pc.en,cn:pc.cn}],[['bm','BM'],['en','EN'],['cn','中文']]);
    out+=sec('FAQ')+tbl(l.faq||[],[['q_bm','问题 BM'],['a_bm','回答 BM'],['cn','中文释义']]);
    out+=sec('平台规则')+tbl(m.platform_rules||[],[['rule','规则'],['status','状态'],['effect','执行影响'],['source','依据']]);
    out+=sec('平台 × 区域 × 人群 × 族裔文化 WHY')+tbl(pairs(m.why),[['key','维度'],['value','WHY']]);
    out+=sec('族裔文化适配检查表')+tbl(c.rows||[],[['dimension','维度'],['status','状态'],['basis','依据/假设'],['inclusive','包容性表征'],['risk','刻板印象/禁忌'],['script_check','脚本校验'],['casting_check','模特校验'],['wardrobe_grooming_check','服化道校验'],['color_check','配色校验'],['cta_check','CTA校验'],['verification_result','校验结果'],['modification_action','修改动作'],['action','执行动作']]);
    if(arr(m.market_reference).length)out+=sec('市场参考带')+tbl(m.market_reference,[['brand','品牌'],['product','产品'],['observed_sale_rm','促销价'],['observed_list_rm','标价'],['role','用途']]);
    return out;
  };

  if(typeof campaign==='function') campaign=function(){
    const content=obj(D.content), race=obj(D.race), ads=obj(D.ads); let out=sec('分平台内容矩阵','平台原生执行 + RACE + 文化校验 + 归因。');
    out+=tbl(content.rows||[],[['surface','平台/Surface'],['audience','人群'],['topic','选题'],['hook','Hook'],['structure','脚本结构'],['script_structure','脚本结构'],['visual','视觉形式'],['visual_format','视觉形式'],['cta','CTA'],['CTA','CTA'],['metric','指标'],['race','RACE阶段'],['race_stage','RACE阶段'],['culture','文化/禁忌'],['culture_taboo_check','文化/禁忌'],['dimension','尺寸'],['duration','时长'],['cover','封面'],['subtitle','字幕'],['music','音乐版权'],['music_rights','音乐版权'],['traffic','流量机制'],['traffic_mechanism','流量机制'],['landing','落地页'],['landing_page','落地页'],['attribution','归因/UTM'],['attribution_utm','归因/UTM'],['why','WHY']]);
    out+=sec('RACE 传播执行表')+tbl(arr(race.rows).map(x=>({...x,actions:join(x.actions),outputs:join(x.outputs)})),[['stage','阶段'],['objective','目标'],['actions','关键动作'],['outputs','输出物'],['platform','平台'],['culture','文化校验'],['metric','指标'],['why','WHY']]);
    if(ads.objective)out+=sec('广告目标')+`<div class="quote">${e(ads.objective)}</div>`;
    out+=sec('Paid A/B')+tbl(ads.tests||[],[['test','测试'],['variable','唯一变量'],['a','A'],['b','B'],['primary_metric','主指标'],['secondary','次指标'],['decision','决策规则']]);
    if(ads.economics_boundary||ads.landing||ads.attribution||arr(ads.failure_diagnosis).length){out+=sec('广告经济 / 落地 / 归因 / 诊断')+tbl([
      {k:'economics_boundary',v:ads.economics_boundary},{k:'landing',v:ads.landing},{k:'attribution',v:ads.attribution},{k:'failure_diagnosis',v:join(ads.failure_diagnosis)}
    ],[['k','对象'],['v','内容']]);}
    return out;
  };

  if(typeof universe==='function') universe=function(){
    const u=obj(D.universe),v=obj(D.visual); let out=sec('视觉母系统','完整项目级视觉/摄影执行，不静默丢参数。');
    const visualRows=[
      ['thesis','视觉命题'],['moodboard','情绪板方向'],['composition','构图规则'],['palette','HEX 配色'],['contrast','对比度'],['typography','字体/排版'],['camera','镜头/机位'],['lighting','灯光'],['cmf','CMF/材质'],['platform','平台输出'],['inclusive','包容性摄影'],['shot_list','镜头表']
    ].map(([k,label])=>({label,value:pretty(v[k])}));
    out+=tbl(visualRows,[['label','视觉对象'],['value','执行内容']]);
    if(u.total_asset_candidates!=null)out+=sec('资产宇宙')+`<div class="kpi">${e(u.total_asset_candidates)}</div><p>候选总数；平台槽位只约束 Activation Set。</p>`;
    out+=sec('资产家族机会扫描')+tbl(arr(u.family_sweep).map(x=>({...x,candidates:join(x.candidates)})),[['family','Family'],['status','状态'],['candidates','候选'],['why','WHY']]);
    out+=sec('额外候选 / Backlog')+tbl(u.additional_candidates||[],[['id','ID'],['family','Family'],['state','状态'],['why','WHY']]);
    return out;
  };

  if(typeof evidence==='function') evidence=function(){
    const comp=obj(D.compliance),ads=obj(D.ads),sources=obj(D.sources),reviews=obj(D.reviews); let out=sec('证据 / 风险 / 复盘');
    out+=sec('P0 合规')+tbl(comp.claim_rows||[],[['area','领域'],['status','状态'],['allowed','可用'],['blocked','禁止'],['evidence','证据']]);
    out+=sec('其他风险')+tbl(comp.other_risks||[],[['risk','风险'],['severity','等级'],['action','动作']]);
    out+=sec('来源与消费')+tbl(sources.sources||[],[['id','ID'],['type','类型'],['title','来源'],['url','URL'],['use','用途'],['recency','时效']]);
    out+=sec('Review Analysis')+tbl(arr(reviews.taxonomy).map(x=>({...x,signals:join(x.signals)})),[['bucket','问题类'],['signals','信号'],['responsibility','责任层'],['repair','最小修复']]);
    if(reviews.learning_loop)out+=`<div class="notice okbox"><b>学习闭环：</b>${e(reviews.learning_loop)}</div>`;
    out+=sec('输出前自检')+tbl(comp.self_check||[],[['item','检查'],['status','状态'],['basis','依据'],['action','动作']]);
    return out;
  };

  if(typeof assetDetail==='function') assetDetail=function(id){
    const a=arr(D.assets).find(x=>x.id===id||x.asset_id===id); if(!a)return typeof production==='function'?production():''; const c=obj(a.card);
    const pp=obj(c.product_presence); const tabs=[['direction','Art Direction'],['promptcn','Prompt CN'],['prompten','Prompt EN'],['copy','Visible Copy'],['prod','Production'],['review','Review']];
    const card=(title,body,span='span6')=>`<div class="card ${span}"><h3>${e(title)}</h3>${body}</div>`;
    let direction=sec('逐资产完整 Art Direction')+`<div class="grid">`+
      card('消费者决策',`<p><b>Question：</b>${e(c.consumer_question)}</p><p><b>Barrier：</b>${e(c.purchase_barrier)}</p><p><b>Belief：</b>${e(c.target_belief)}</p><p><b>Strategic Job：</b>${e(c.strategic_job)}</p><p><b>Increment：</b>${e(c.incremental_information)}</p>`)+
      card('视觉载体 / Product Presence',`<p><b>Carrier：</b>${e(c.visual_carrier)}</p><p><b>State：</b>${e(pp.state||pp.planning_state)}</p><p><b>Role：</b>${e(pp.role)}</p><p><b>WHY：</b>${e(pp.why||pp.presence_why)}</p>`)+
      card('主体 / 动作 / 场景 / 道具',`<p><b>Subject：</b>${e(c.subject)}</p><p><b>Action：</b>${e(c.action_decisive_moment)}</p><p><b>Scene：</b>${e(c.scene_environment)}</p><p><b>Props：</b>${e(c.props_supporting_elements)}</p>`)+
      card('构图 / 证据 / Copy Route',`<p>${e(c.composition_spatial_rhythm)}</p><p><b>Evidence：</b>${e(c.evidence_hierarchy)}</p><p><b>Copy Route：</b>${e(c.copy_render_route)}</p>`)+
      card('摄影 / 灯光 / CMF',`<p><b>Camera：</b>${e(c.camera_optics)}</p><p><b>Light：</b>${e(c.lighting)}</p><p><b>CMF：</b>${e(c.cmf_material_color)}</p>`)+
      card('Output / Culture / Truth',`<p><b>Output：</b>${e(c.output_surface)}</p><p><b>Culture：</b>${e(c.culture_inclusion)}</p><p><b>Truth Boundary：</b>${e(c.truth_boundary)}</p>`)+
      card('商业假设 / 指标 / 节奏差',`<p><b>Hypothesis：</b>${e(c.business_hypothesis)}</p><p><b>Metric：</b>${e(c.success_metric)}</p><p><b>Rhythm delta：</b>${e(c.portfolio_rhythm_delta)}</p>`,'span12')+`</div>`;
    const pane=(id,text)=>`<div id="${id}" class="tabpane">${copyPane(text)}</div>`;
    return `<div class="asset-detail"><div class="head"><div><div class="eyebrow">${e(a.id||a.asset_id)} · ${e(c.family)} · ${e(c.surface)}</div><h1>${e(c.title_cn||c.asset_name||a.id)}</h1></div><button class="back" onclick="history.back()">← 返回</button></div><div class="tabs">${tabs.map((t,i)=>`<button class="${i===0?'active':''}" data-tab="${t[0]}" onclick="tab('${t[0]}',this)">${t[1]}</button>`).join('')}</div><div id="direction" class="tabpane active">${direction}</div>${pane('promptcn',a.prompt_cn)}${pane('prompten',a.prompt_en)}${pane('copy',a.visible_copy)}${pane('prod',a.production_notes)}${pane('review',pretty(a.review))}</div>`;
  };

  // True project-wide search. Clone the input to remove the legacy anonymous asset-only listener.
  const old=document.getElementById('search'); const box=document.getElementById('searchResults');
  const CBCC_GLOBAL_SEARCH_INDEX=[];
  function indexValue(v,path){if(v==null)return;if(Array.isArray(v)){v.forEach((x,i)=>indexValue(x,`${path}[${i}]`));return}if(typeof v==='object'){Object.entries(v).forEach(([k,x])=>indexValue(x,path?`${path}.${k}`:k));return}const text=String(v);if(text.trim())CBCC_GLOBAL_SEARCH_INDEX.push({path,text});}
  indexValue(D,'DATA'); window.CBCC_GLOBAL_SEARCH_INDEX=CBCC_GLOBAL_SEARCH_INDEX;
  if(old&&box){const input=old.cloneNode(true);old.parentNode.replaceChild(input,old);input.addEventListener('input',ev=>{const q=ev.target.value.trim().toLowerCase();if(!q){box.classList.remove('show');return}const found=CBCC_GLOBAL_SEARCH_INDEX.filter(x=>(x.path+' '+x.text).toLowerCase().includes(q)).slice(0,20);box.innerHTML=found.map(x=>`<button><b>${e(x.path)}</b><br><small>${e(x.text).slice(0,240)}</small></button>`).join('')||'<button>没有匹配内容</button>';box.classList.add('show')});}
  if(typeof render==='function')render();
})();
</script>
'''.replace('__PAYLOAD__',_json(payload))
    if '</body>' in text:text=text.replace('</body>',script+'</body>',1)
    else:text+=script
    path.write_text(text,encoding='utf-8')
    return {'status':'PASS','path':str(path),'bytes':path.stat().st_size,'marker':MARKER}
