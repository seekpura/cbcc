from __future__ import annotations
from typing import Any
import json,re


def _extract_const_data(html:str):
    marker='const DATA='
    i=html.find(marker)
    if i<0:return {},html
    start=i+len(marker)
    while start<len(html) and html[start].isspace():start+=1
    if start>=len(html) or html[start]!='{':return {},html
    depth=0;instr=False;esc=False;end=None
    for j in range(start,len(html)):
        c=html[j]
        if instr:
            if esc:esc=False
            elif c=='\\':esc=True
            elif c=='"':instr=False
            continue
        if c=='"': instr=True;continue
        if c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:
                end=j+1;break
    if end is None:return {},html
    try:data=json.loads(html[start:end])
    except Exception:return {},html[end:]
    return data,html[end:]


def _missing_renderer_tokens(renderer:str,tokens:list[str])->list[str]:
    return [t for t in tokens if t not in renderer]


def _has_real_copy_binding(renderer:str)->bool:
    # Direct per-control binding used by lightweight project-authored workspaces.
    direct=bool(re.search(r'onclick=["\'][^"\']*copyText\s*\(',renderer,re.I))
    # Mature routed workspace uses delegated .copy-btn / data-copy controls.
    delegated=(
        ('navigator.clipboard.writeText' in renderer or "document.execCommand('copy')" in renderer or 'document.execCommand("copy")' in renderer)
        and ('.copy-btn' in renderer or 'data-copy' in renderer)
        and bool(re.search(r'addEventListener\s*\(\s*["\']click["\']',renderer,re.I))
    )
    # Generic delegated implementation is acceptable only when a real clickable control selector is present.
    generic=(
        ('navigator.clipboard.writeText' in renderer or 'clipboard.writeText' in renderer)
        and bool(re.search(r'addEventListener\s*\(\s*["\']click["\']',renderer,re.I))
        and bool(re.search(r'(?:closest|matches|querySelector)\s*\([^)]*(?:copy|clipboard)',renderer,re.I))
    )
    return direct or delegated or generic


def audit_human_projection_html(html:str)->list[dict[str,Any]]:
    """Audit visible Human Workspace projection, not mere presence inside embedded DATA.

    The DATA object is intentionally excluded from renderer-token checks. Otherwise a field can sit in
    embedded JSON, never be rendered, and still produce a false PASS. Routes/layout remain project-authored;
    this checks semantic coverage rather than imposing a fixed page taxonomy.
    """
    data,renderer=_extract_const_data(html); issues=[]
    def add(code,missing,why):
        if missing: issues.append({'code':code,'missing':missing,'why':why})

    listing=data.get('listing') if isinstance(data,dict) else None
    if isinstance(listing,dict):
        tokens=[]
        if listing.get('description_en'): tokens.append('description_en')
        for k in ('key_points','attributes','package_contents','faq'):
            if listing.get(k) not in (None,'',[],{}):tokens.append(k)
        add('HTML_LISTING_PROJECTION_INCOMPLETE',_missing_renderer_tokens(renderer,tokens),'Canonical Listing fields exist in DATA but are not consumed by visible HTML renderer.')

    strategy=((data.get('strategy') or {}).get('strategy') if isinstance(data.get('strategy'),dict) else None)
    if isinstance(strategy,dict):
        tokens=[k for k in ('value_proposition','message_hierarchy','priority_tradeoff') if strategy.get(k) not in (None,'',[],{})]
        add('HTML_STRATEGY_PROJECTION_INCOMPLETE',_missing_renderer_tokens(renderer,tokens),'Core strategy objects exist but are silently omitted from Human Workspace.')

    market=data.get('market') if isinstance(data,dict) else None
    if isinstance(market,dict):
        missing=[]
        if market.get('platform_rules') not in (None,'',[],{}) and not any(t in renderer for t in ('m.platform_rules','DATA.market.platform_rules','platform_rules.map','platform_rules,[')): missing.append('platform_rules')
        if market.get('why') not in (None,'',[],{}) and not any(t in renderer for t in ('m.why','DATA.market.why','market.why')): missing.append('why')
        add('HTML_MARKET_PROJECTION_INCOMPLETE',missing,'Platform rules and platform×region×audience×culture WHY must be human-visible when authored.')

    visual=data.get('visual') if isinstance(data,dict) else None
    if isinstance(visual,dict):
        tokens=[k for k in ('palette','contrast','typography','platform','inclusive','shot_list') if visual.get(k) not in (None,'',[],{})]
        add('HTML_VISUAL_PROJECTION_INCOMPLETE',_missing_renderer_tokens(renderer,tokens),'Visual execution details exist but are not consumed by Human Workspace.')

    content=data.get('content') if isinstance(data,dict) else None
    rows=(content or {}).get('rows') if isinstance(content,dict) else None
    if isinstance(rows,list) and rows:
        keys=('cover','subtitle','music','traffic','landing')
        tokens=[k for k in keys if any(isinstance(r,dict) and r.get(k) not in (None,'',[],{}) for r in rows)]
        add('HTML_CONTENT_MATRIX_PROJECTION_INCOMPLETE',_missing_renderer_tokens(renderer,tokens),'Platform execution columns exist but are not rendered.')

    race=data.get('race') if isinstance(data,dict) else None
    rrows=(race or {}).get('rows') if isinstance(race,dict) else None
    if isinstance(rrows,list) and rrows:
        missing=[str(i) for i,r in enumerate(rrows) if isinstance(r,dict) and r.get('platform') in (None,'',[],{})]
        add('RACE_PLATFORM_FIELD_MISSING',missing,'RACE execution rows must name the platform/surface scope.')
        if not missing:
            add('HTML_RACE_PROJECTION_INCOMPLETE',_missing_renderer_tokens(renderer,['platform']),'RACE platform field exists but is not rendered.')

    culture=data.get('culture') if isinstance(data,dict) else None
    crows=(culture or {}).get('rows') if isinstance(culture,dict) else None
    required=('script_check','casting_check','wardrobe_grooming_check','color_check','cta_check','validation_result','modification_action')
    if isinstance(crows,list) and crows:
        missing=sorted({k for r in crows if isinstance(r,dict) for k in required if r.get(k) in (None,'',[],{})})
        add('CULTURE_EXECUTION_COLUMNS_MISSING',missing,'Culture adaptation must independently check script, casting, wardrobe/grooming, color, CTA, result and modification.')
        if not missing:
            add('HTML_CULTURE_PROJECTION_INCOMPLETE',_missing_renderer_tokens(renderer,list(required)),'Culture execution columns exist but are not rendered.')

    comp=data.get('compliance') if isinstance(data,dict) else None
    if isinstance(comp,dict):
        if comp.get('other_risks') not in (None,'',[],{}):add('HTML_COMPLIANCE_PROJECTION_INCOMPLETE',_missing_renderer_tokens(renderer,['other_risks']),'Risk list exists but is omitted from Human Workspace.')
        checks=comp.get('self_check') or []
        if isinstance(checks,list):
            blob=' '.join(str((x or {}).get('item','')) for x in checks if isinstance(x,dict)).lower()
            themes={'fabrication':('编造','fabricat'),'why':('why','为什么'),'culture':('文化','族裔','culture'),'compliance':('合规','法规','claim'),'metrics':('指标','metric'),'assumptions':('假设','assumption')}
            missing_themes=[k for k,words in themes.items() if not any(w.lower() in blob for w in words)]
            add('OUTPUT_SELF_CHECK_DIMENSIONS_MISSING',missing_themes,'Pre-output self-check must explicitly cover fabrication, WHY, culture, compliance, metrics and assumptions.')

    ads=data.get('ads') if isinstance(data,dict) else None
    if isinstance(ads,dict):
        tokens=[k for k in ('objective','economics_boundary','landing','attribution','failure_diagnosis') if ads.get(k) not in (None,'',[],{})]
        add('HTML_ADS_PROJECTION_INCOMPLETE',_missing_renderer_tokens(renderer,tokens),'Ads execution/economics/attribution objects exist but are not rendered.')

    reviews=data.get('reviews') if isinstance(data,dict) else None
    if isinstance(reviews,dict) and reviews.get('status') not in (None,'',[],{}):
        if not any(t in renderer for t in ('DATA.reviews.status','reviews.status','.reviews.status')):
            add('HTML_REVIEW_PROJECTION_INCOMPLETE',['status'],'Review evidence status must be visible, not only taxonomy.')

    sources=data.get('sources') if isinstance(data,dict) else None
    srows=(sources or {}).get('sources') if isinstance(sources,dict) else None
    if isinstance(srows,list) and any(isinstance(r,dict) and r.get('url') for r in srows):
        if not any(t in renderer for t in ("['url'",'.url','[\"url\"')):
            add('HTML_SOURCE_PROJECTION_INCOMPLETE',['url'],'Source URLs exist but are not exposed in evidence view.')

    assets=data.get('assets') if isinstance(data,dict) else None
    if isinstance(assets,list) and assets:
        cards=[a.get('card') for a in assets if isinstance(a,dict) and isinstance(a.get('card'),dict)]
        tokens=[]
        for k in ('visual_carrier','output_surface','culture_inclusion','truth_boundary'):
            if any(c.get(k) not in (None,'',[],{}) for c in cards):tokens.append(k)
        if any(isinstance(c.get('product_presence'),dict) and (c['product_presence'].get('role') or c['product_presence'].get('why')) for c in cards):
            tokens += ['product_presence.role','product_presence.why']
        add('HTML_ASSET_ART_DIRECTION_PROJECTION_INCOMPLETE',_missing_renderer_tokens(renderer,tokens),'Asset detail must expose all purchase-relevant Art Direction decisions, not only a summary subset.')

    if not _has_real_copy_binding(renderer):
        issues.append({'code':'WORKSPACE_COPY_BINDING_MISSING','why':'Copy capability is not considered implemented until a visible control is behaviorally bound to clipboard/copy execution.'})

    search_handlers=re.findall(r'addEventListener\s*\(\s*["\']input["\'][\s\S]{0,1800}',renderer,re.I)
    search_blob='\n'.join(search_handlers)
    if 'DATA.assets.filter' in search_blob and not any(t in search_blob for t in ('DATA.listing','DATA.strategy','DATA.compliance','DATA.sources','workspaceSearchIndex','WORKSPACE_SEARCH_INDEX')):
        issues.append({'code':'WORKSPACE_SEARCH_SCOPE_INCOMPLETE','why':'Search is asset-only while the workspace contains Listing, strategy, risks, sources and prompts.'})
    return issues
