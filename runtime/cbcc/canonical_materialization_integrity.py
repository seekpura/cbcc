from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping
import hashlib, json, re

PRESENCE_STATES={
 'HERO_REQUIRED','REQUIRED','SUPPORTING','DETAIL_ONLY','OPTIONAL','FORBIDDEN','ABSENT','PRODUCT_ABSENT','NOT_NEEDED'
}
COPY_ROUTES={
 'MODEL_RENDER_INTEGRATED','MODEL_RENDER','INTEGRATED','HYBRID','POST_COMPOSITE','NO_VISIBLE_COPY',
 'EXACT_PIXEL_COMPOSITE','DETERMINISTIC_COMPOSITION_AFTER_RENDER'
}
SOURCE_ROUTE_WORDS={'GENERATIVE','SOURCE_CROP','SOURCE_MONTAGE','SOURCE','REFERENCE_GUIDED'}

_CAMERA_TOKENS=re.compile(r'\b(?:\d+(?:\.\d+)?\s*mm|f\s*/?\s*\d|iso\s*\d|1/\d+\s*s?|eye[- ]?level|top[- ]?down|low angle|high angle|working distance|camera|lens|macro|orthographic|perspective|focus|dof|景深|焦段|镜头|机位|俯角|仰角|工作距离|对焦|正交|视角)\b',re.I)
_LIGHT_TOKENS=re.compile(r'(?:\b\d{4}\s*K\b|key\s*light|fill\s*light|rim\s*light|side\s*light|window\s*light|daylight|softbox|strip\s*light|bounce|diffusion|reflector|flag|lighting|light ratio|negative fill|prelight|polariz|柔光|主光|补光|轮廓光|反光板|黑旗|光比|色温|灯光|窗光)',re.I)
_CMF_TOKENS=re.compile(r'(?:ivory|forest|sage|acrylic|plastic|satin|matte|gloss|stone|cotton|skin|clear|paper|material|材质|亚克力|塑料|石材|棉|肤色|哑光|透明|暖白|森林绿)',re.I)
_OUTPUT_TOKENS=re.compile(r'(?:\b\d{3,4}\s*[×x]\s*\d{3,4}\b|\b\d+\s*:\s*\d+\b|sRGB|Display P3|dpi|px|MP4|MOV|WEBM|≤?\s*\d+\s*MB|fps|static|video|image|方图|竖版|横版)',re.I)
_METRIC_TOKENS=re.compile(r'\b(?:CTR|CVR|CPA|ROAS|CPC|CPM|ATC|dwell|hold|completion|save|share|click|conversion|retention|swipe|FAQ|comments?|reviews?|support|tickets?|orders?|revenue|margin)\b|转化|点击|停留|完播|收藏|分享|加购|订单|评论|归因|指标',re.I)
_HYPOTHESIS_TOKENS=re.compile(r'如果|若|将|能够|能否|是否|预期|相比|降低|提高|提升|测试|假设|because|if |whether|should|could|increase|reduce|improve|test',re.I)


def _text(v:Any)->str:
    if v in (None,'',[],{}): return ''
    if isinstance(v,(dict,list)): return json.dumps(v,ensure_ascii=False,sort_keys=True,default=str)
    return str(v)

def _issue(code:str, field:str, value:Any, why:str)->dict[str,Any]:
    return {'code':code,'field':field,'value':_text(value)[:500],'why':why}

def _presence_state(card:Mapping[str,Any])->str:
    p=card.get('product_presence')
    if isinstance(p,Mapping): return str(p.get('state') or p.get('planning_state') or '').upper().strip()
    return str(p or '').upper().strip()

def audit_asset_semantics(card:Mapping[str,Any]) -> list[dict[str,Any]]:
    """Reject cross-domain field shifts before Prompt/package/HTML compilation.

    This guard deliberately does not try to auto-shift corrupted positional data. Guessing which field
    used to belong where would create a second source of truth. The Agent must re-author/re-materialize
    the asset from named canonical Art Direction fields.
    """
    issues=[]
    vc=_text(card.get('visual_carrier')).strip().upper()
    if vc in PRESENCE_STATES or vc in COPY_ROUTES or vc in SOURCE_ROUTE_WORDS:
        issues.append(_issue('ASSET_SCHEMA_SEMANTIC_MISMATCH','visual_carrier',card.get('visual_carrier'),'visual_carrier contains a presence/copy/source route enum, consistent with positional field shift'))
    route=_text(card.get('copy_render_route')).strip().upper()
    if route and route not in COPY_ROUTES:
        issues.append(_issue('ASSET_SCHEMA_SEMANTIC_MISMATCH','copy_render_route',card.get('copy_render_route'),'copy_render_route must be a recognized route enum, not visible copy text'))
    ev=_text(card.get('evidence_hierarchy')).strip().upper()
    if ev in COPY_ROUTES:
        issues.append(_issue('ASSET_SCHEMA_SEMANTIC_MISMATCH','evidence_hierarchy',card.get('evidence_hierarchy'),'evidence_hierarchy contains a copy render route'))
    camera=_text(card.get('camera_optics'))
    if camera and _LIGHT_TOKENS.search(camera) and not _CAMERA_TOKENS.search(camera):
        issues.append(_issue('ASSET_SCHEMA_SEMANTIC_MISMATCH','camera_optics',camera,'camera field contains lighting language without camera/view/lens semantics'))
    light=_text(card.get('lighting'))
    if light and _CMF_TOKENS.search(light) and not _LIGHT_TOKENS.search(light):
        issues.append(_issue('ASSET_SCHEMA_SEMANTIC_MISMATCH','lighting',light,'lighting field looks like CMF/material content'))
    cmf=_text(card.get('cmf_material_color'))
    if cmf and _OUTPUT_TOKENS.search(cmf) and not _CMF_TOKENS.search(cmf):
        issues.append(_issue('ASSET_SCHEMA_SEMANTIC_MISMATCH','cmf_material_color',cmf,'CMF field looks like output dimensions/format'))
    output=_text(card.get('output_surface'))
    if output and not _OUTPUT_TOKENS.search(output):
        if len(output)>45 or _HYPOTHESIS_TOKENS.search(output):
            issues.append(_issue('ASSET_SCHEMA_SEMANTIC_MISMATCH','output_surface',output,'output field looks like business prose rather than output/surface specification'))
    hyp=_text(card.get('business_hypothesis'))
    if hyp and _METRIC_TOKENS.search(hyp) and not _HYPOTHESIS_TOKENS.search(hyp) and len(hyp)<80:
        issues.append(_issue('ASSET_SCHEMA_SEMANTIC_MISMATCH','business_hypothesis',hyp,'business_hypothesis is metric-only; likely shifted from success_metric'))
    metric=_text(card.get('success_metric'))
    if metric and not _METRIC_TOKENS.search(metric) and len(metric)>20:
        issues.append(_issue('ASSET_SCHEMA_SEMANTIC_MISMATCH','success_metric',metric,'success_metric is narrative prose without measurement semantics'))
    rhythm=_text(card.get('portfolio_rhythm_delta')).strip().upper()
    if rhythm in SOURCE_ROUTE_WORDS or rhythm in COPY_ROUTES or rhythm in PRESENCE_STATES:
        issues.append(_issue('ASSET_SCHEMA_SEMANTIC_MISMATCH','portfolio_rhythm_delta',card.get('portfolio_rhythm_delta'),'portfolio rhythm contains a production/source/presence enum'))
    state=_presence_state(card)
    if state and state not in PRESENCE_STATES:
        issues.append(_issue('ASSET_SCHEMA_SEMANTIC_MISMATCH','product_presence',state,'unrecognized Product Presence state'))
    return issues


def parse_visible_copy_markdown(text:str)->dict[str,str]:
    text=str(text or '')
    def section(name:str, next_names:list[str])->str:
        m=re.search(r'^##\s+'+re.escape(name)+r'[^\n]*\n',text,re.M|re.I)
        if not m:return ''
        end=len(text)
        for nxt in next_names:
            n=re.search(r'^##\s+'+re.escape(nxt)+r'[^\n]*\n',text[m.end():],re.M|re.I)
            if n:end=min(end,m.end()+n.start())
        return text[m.end():end].strip()
    rm=re.search(r'\*\*Render route:\*\*\s*(.*?)\s*(?=\*\*Locale:|\n##|$)',text,re.S|re.I)
    return {
      'render_route': (rm.group(1).strip() if rm else ''),
      'target': section('Bahasa Melayu',['English semantic baseline','中文释义 / 用途']),
      'en': section('English semantic baseline',['中文释义 / 用途']),
      'cn': section('中文释义 / 用途',[]),
    }

def audit_visible_copy_markdown(text:str)->list[dict[str,Any]]:
    b=parse_visible_copy_markdown(text);issues=[]
    route=b['render_route'].strip().upper()
    if route and route not in COPY_ROUTES:
        issues.append(_issue('VISIBLE_COPY_LANGUAGE_SLOT_MISMATCH','render_route',b['render_route'],'visible-copy render route contains copy text or an unknown route'))
    if b['en'] and re.search(r'[\u4e00-\u9fff]',b['en']):
        issues.append(_issue('VISIBLE_COPY_LANGUAGE_SLOT_MISMATCH','english_semantic_baseline',b['en'],'English semantic baseline contains Chinese text'))
    cn=b['cn']
    if cn and 'NO_VISIBLE_COPY' not in cn.upper() and not re.search(r'[\u4e00-\u9fff]',cn):
        issues.append(_issue('VISIBLE_COPY_LANGUAGE_SLOT_MISMATCH','chinese_meaning',cn,'Chinese meaning/use slot contains no Chinese; likely shifted camera/production text'))
    return issues


def canonical_art_direction_payload(asset:Mapping[str,Any])->dict[str,Any]:
    art=asset.get('asset_art_direction') if isinstance(asset.get('asset_art_direction'),Mapping) else {}
    return {
      'asset_id': asset.get('asset_id') or asset.get('id'),
      'visual_carrier': art.get('visual_carrier') or asset.get('visual_carrier'),
      'product_presence': art.get('product_presence') or asset.get('product_presence'),
      'subject': art.get('subject') or asset.get('subject'),
      'action': art.get('action') or art.get('decisive_moment') or asset.get('action_decisive_moment'),
      'environment': art.get('environment') or asset.get('scene_environment'),
      'props': art.get('props') or asset.get('props_supporting_elements'),
      'composition': art.get('composition') or art.get('composition_grammar') or asset.get('composition_spatial_rhythm'),
      'evidence_hierarchy': art.get('evidence_hierarchy') or asset.get('evidence_hierarchy'),
      'copy_render_route': art.get('copy_render_route') or asset.get('copy_render_route'),
      'camera': art.get('camera') or art.get('camera_optics') or asset.get('camera_optics'),
      'lighting': art.get('lighting') or asset.get('lighting'),
      'cmf': art.get('cmf') or art.get('material') or asset.get('cmf_material_color'),
      'typography': art.get('typography'),
      'output': art.get('output_spec') or asset.get('output_surface'),
      'culture_inclusion': art.get('culture_inclusion') or asset.get('culture_inclusion'),
      'truth_boundary': art.get('truth_boundary') or asset.get('truth_boundary'),
    }

def canonical_art_direction_hash(asset:Mapping[str,Any])->str:
    raw=json.dumps(canonical_art_direction_payload(asset),ensure_ascii=False,sort_keys=True,separators=(',',':'),default=str).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

def stamp_prompt_lineage(asset:Mapping[str,Any], bundle:Mapping[str,Any])->dict[str,Any]:
    out=deepcopy(dict(bundle)); h=canonical_art_direction_hash(asset)
    lineage={'schema_version':'cbcc-canonical-art-direction-v1','canonical_art_direction_sha256':h,'source':'normalized_named_asset_art_direction'}
    out['canonical_prompt_lineage']=lineage
    card=out.setdefault('design_card',{}); card['canonical_prompt_lineage']=lineage
    contract=out.setdefault('prompt_contract',{}); contract['canonical_prompt_lineage']=lineage
    return out

def audit_prompt_lineage(asset:Mapping[str,Any], bundle:Mapping[str,Any])->list[dict[str,Any]]:
    line=bundle.get('canonical_prompt_lineage') if isinstance(bundle,Mapping) else None
    if not isinstance(line,Mapping): return [_issue('PROMPT_CANONICAL_LINEAGE_MISSING','canonical_prompt_lineage','', 'CN and EN prompts must be projections of one canonical Art Direction')]
    expected=canonical_art_direction_hash(asset); got=str(line.get('canonical_art_direction_sha256') or '')
    if got!=expected:return [_issue('PROMPT_CANONICAL_LINEAGE_MISMATCH','canonical_prompt_lineage',got,'prompt lineage hash differs from current canonical Art Direction')]
    return []


def audit_asset_directory(asset_dir:Path)->list[dict[str,Any]]:
    issues=[];card={}
    for name in ('12_design_card.json','11_design_card.json'):
        p=asset_dir/name
        if p.exists():
            try: card=json.loads(p.read_text(encoding='utf-8'))
            except Exception: card={}
            break
    if card:
        for x in audit_asset_semantics(card): issues.append({'asset_id':asset_dir.name,**x})
    for name in ('07_visible_copy.md','08_copy.md'):
        p=asset_dir/name
        if p.exists():
            for x in audit_visible_copy_markdown(p.read_text(encoding='utf-8',errors='ignore')): issues.append({'asset_id':asset_dir.name,**x})
            break
    return issues
